"""
Granite Model Interceptor

Provides Claude-like interception for IBM Granite models.
Validates responses using LOKI engine + Guardian safety checks.

Similar to AnthropicInterceptor but for:
- Self-hosted Granite 3.2/4.0 models
- NVIDIA NIM microservices
- watsonx.ai hosted models
- HuggingFace Inference API

Features:
- Automatic LOKI validation
- Guardian safety checks
- Cost tracking
- On-premises or cloud deployment
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)


class GraniteInterceptor:
    """
    Intercepts Granite model calls, validates responses with LOKI.

    Examples:
        >>> interceptor = GraniteInterceptor(engine, guardian_validator)
        >>> result = interceptor.intercept(
        ...     request_data={
        ...         'model': 'granite-3.2-8b-instruct',
        ...         'messages': [{'role': 'user', 'content': 'Write financial advice'}],
        ...         'max_tokens': 1024
        ...     },
        ...     endpoint='http://localhost:8000/v1/completions',
        ...     active_modules=['fca_uk', 'gdpr_uk']
        ... )
    """

    def __init__(self, engine, guardian_validator=None):
        """
        Initialize Granite interceptor.

        Args:
            engine: LOKI compliance engine
            guardian_validator: Optional GuardianValidator instance
        """
        self.engine = engine
        self.guardian = guardian_validator

    def intercept(
        self,
        request_data: Dict[str, Any],
        endpoint: str,
        api_key: Optional[str] = None,
        active_modules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Forward request to Granite endpoint, validate response with LOKI.

        Args:
            request_data: Request payload
            endpoint: Granite API endpoint (local or cloud)
            api_key: Optional API key for hosted endpoints
            active_modules: Modules to validate against

        Returns:
            Enhanced response with LOKI and Guardian metadata

        Supports:
            - Local vLLM/TGI: http://localhost:8000/v1/completions
            - NVIDIA NIM: https://nim.nvidia.com/...
            - watsonx.ai: https://api.watsonx.ai/...
            - HuggingFace: https://api-inference.huggingface.co/...
        """
        try:
            if not isinstance(request_data, dict):
                raise ValueError('request_data must be a dict')

            # Filter to allowed parameters
            allowed_keys = {
                'model', 'messages', 'max_tokens', 'temperature',
                'top_p', 'top_k', 'stop', 'stream'
            }
            payload = {k: v for k, v in request_data.items() if k in allowed_keys}

            # Validate required fields
            if 'model' not in payload:
                payload['model'] = 'granite-3.2-8b-instruct'
            if 'messages' not in payload:
                raise ValueError('messages field is required')

            # Make request to Granite endpoint
            response = self._call_granite_endpoint(endpoint, payload, api_key)

            # Extract response text
            response_text = self._extract_text(response)

            # Validate with LOKI engine
            modules_to_check = active_modules or list(self.engine.modules.keys())
            validation = self.engine.check_document(
                text=response_text,
                document_type='ai_generated',
                active_modules=modules_to_check
            )

            # Optional: Guardian safety check
            guardian_result = None
            if self.guardian:
                guardian_result = self.guardian.validate(
                    text=response_text,
                    dimensions=['harm', 'social_bias', 'violence']
                )

            # Determine if should block
            loki_risk = validation.get('overall_risk', 'LOW')
            guardian_risk = guardian_result.overall_risk.value if guardian_result else 'LOW'

            # Block on CRITICAL from either system
            if loki_risk == 'CRITICAL' or guardian_risk == 'CRITICAL':
                return {
                    'blocked': True,
                    'error': 'LOKI_CRITICAL_ERROR',
                    'message': 'AI response contains critical compliance errors',
                    'validation': validation,
                    'guardian': self._serialize_guardian(guardian_result) if guardian_result else None,
                    'original_response': response_text
                }

            # Return enhanced response
            return {
                'blocked': False,
                'response': response,
                'loki': {
                    'risk': loki_risk,
                    'validation': validation,
                    'timestamp': datetime.utcnow().isoformat(),
                    'modules_checked': modules_to_check
                },
                'guardian': self._serialize_guardian(guardian_result) if guardian_result else None,
                'provider': 'granite',
                'model': payload.get('model')
            }

        except Exception as e:
            logger.error(f"Granite interceptor error: {e}")
            return {
                'blocked': True,
                'error': 'INTERCEPTOR_ERROR',
                'message': str(e),
                'original_response': None
            }

    def intercept_and_validate(
        self,
        request_data: Dict[str, Any],
        endpoint: str,
        api_key: Optional[str] = None,
        modules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Intercept and validate, but flag instead of blocking.

        Args:
            request_data: Request payload
            endpoint: Granite API endpoint
            api_key: Optional API key
            modules: Modules to validate

        Returns:
            Response with flagging metadata (never blocks)
        """
        try:
            result = self.intercept(request_data, endpoint, api_key, modules)

            # Convert blocking to flagging
            if result.get('blocked'):
                loki_data = result.get('loki', {})
                risk = loki_data.get('risk', 'UNKNOWN')

                return {
                    'blocked': False,  # Don't block
                    'response': result.get('response', {}),
                    'validation': result.get('validation', {}),
                    'loki': {
                        'risk': risk,
                        'flagged': True,
                        'action': 'FLAGGED',
                        'reason': result.get('message', ''),
                        'gates_checked': loki_data.get('modules_checked', [])
                    },
                    'guardian': result.get('guardian')
                }

            # Normal pass-through
            return result

        except Exception as e:
            logger.error(f"Granite validation error: {e}")
            return {
                'error': str(e),
                'blocked': False,
                'response': {},
                'validation': {},
                'loki': {'risk': 'LOW', 'flagged': False, 'action': 'ERROR'}
            }

    def _call_granite_endpoint(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        api_key: Optional[str]
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Granite endpoint.

        Supports:
            - OpenAI-compatible APIs (vLLM, TGI, NVIDIA NIM)
            - watsonx.ai
            - HuggingFace Inference API
        """
        import requests

        headers = {'Content-Type': 'application/json'}

        if api_key:
            # Detect endpoint type and set appropriate auth header
            if 'nvidia.com' in endpoint:
                headers['Authorization'] = f'Bearer {api_key}'
            elif 'watsonx' in endpoint:
                headers['Authorization'] = f'Bearer {api_key}'
            elif 'huggingface' in endpoint:
                headers['Authorization'] = f'Bearer {api_key}'
            else:
                # Default to Bearer token
                headers['Authorization'] = f'Bearer {api_key}'

        # Convert to OpenAI-compatible format if needed
        if not endpoint.endswith(('/v1/chat/completions', '/v1/completions')):
            endpoint = endpoint.rstrip('/') + '/v1/chat/completions'

        try:
            resp = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )

            if resp.status_code >= 400:
                raise RuntimeError(
                    f"Granite endpoint error {resp.status_code}: {resp.text}"
                )

            return resp.json()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Granite endpoint request failed: {e}")

    def _extract_text(self, response: Dict[str, Any]) -> str:
        """Extract text from Granite response (OpenAI-compatible format)"""
        try:
            # Try OpenAI format
            if 'choices' in response:
                message = response['choices'][0].get('message', {})
                return message.get('content', '')

            # Try direct text field
            if 'text' in response:
                return response['text']

            # Fallback to JSON dump
            return json.dumps(response)

        except Exception as e:
            logger.error(f"Error extracting Granite response text: {e}")
            return json.dumps(response)

    def _serialize_guardian(self, guardian_result) -> Optional[Dict[str, Any]]:
        """Serialize GuardianResult for JSON response"""
        if guardian_result is None:
            return None

        return {
            'overall_risk': guardian_result.overall_risk.value,
            'risk_scores': guardian_result.risk_scores,
            'flagged_dimensions': guardian_result.flagged_dimensions,
            'passed': guardian_result.passed,
            'recommendation': guardian_result.recommendation,
            'guardian_version': guardian_result.guardian_version
        }

    def get_cost_estimate(
        self,
        tokens_input: int,
        tokens_output: int,
        deployment_type: str = 'self_hosted'
    ) -> Dict[str, float]:
        """
        Estimate cost of Granite inference.

        Args:
            tokens_input: Input token count
            tokens_output: Output token count
            deployment_type: 'self_hosted', 'nvidia_nim', 'watsonx', 'huggingface'

        Returns:
            Cost breakdown
        """
        # Cost estimates per 1M tokens
        costs = {
            'self_hosted': {
                'input': 0.05,   # Compute cost estimate
                'output': 0.05
            },
            'nvidia_nim': {
                'input': 0.15,
                'output': 0.15
            },
            'watsonx': {
                'input': 0.20,
                'output': 0.20
            },
            'huggingface': {
                'input': 0.10,
                'output': 0.10
            }
        }

        pricing = costs.get(deployment_type, costs['self_hosted'])

        input_cost = (tokens_input / 1_000_000) * pricing['input']
        output_cost = (tokens_output / 1_000_000) * pricing['output']

        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': input_cost + output_cost,
            'deployment_type': deployment_type,
            'tokens_input': tokens_input,
            'tokens_output': tokens_output
        }
