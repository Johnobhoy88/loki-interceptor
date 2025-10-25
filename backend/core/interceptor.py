import os
import requests
import json as _json
from datetime import datetime


class AnthropicInterceptor:
    def __init__(self, engine):
        self.engine = engine

    def intercept(self, request_data, api_key, active_modules=None):
        """
        Forward request to Anthropic, validate response, return with LOKI metadata
        """
        try:
            if not isinstance(request_data, dict):
                raise ValueError('request_data must be a dict')
            if not api_key:
                raise ValueError('Missing API key')

            # Direct HTTP; no SDK client

            # Filter to allowed Anthropic parameters only
            allowed_keys = {
                'model', 'messages', 'max_tokens', 'system',
                'temperature', 'top_p', 'top_k', 'stop_sequences', 'metadata'
            }
            if not isinstance(request_data, dict):
                raise ValueError('Request must be a JSON object')
            unknown_keys = set(request_data.keys()) - allowed_keys
            # Never pass unknown keys (e.g., 'proxies') to SDK
            payload = {k: v for k, v in request_data.items() if k in allowed_keys}

            # Basic validation
            missing = [k for k in ('model', 'messages', 'max_tokens') if k not in payload]
            if missing:
                raise ValueError(f"Missing required fields: {', '.join(missing)}")

            url = 'https://api.anthropic.com/v1/messages'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            }
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                if resp.status_code >= 400:
                    raise RuntimeError(f"Anthropic HTTP {resp.status_code}: {resp.text}")
                response = resp.json()
            except Exception as api_err:
                raise RuntimeError(f"Anthropic HTTP error: {api_err}")

            # Extract response text
            response_text = ''
            try:
                for block in (response.get('content') or []):
                    if (block or {}).get('type') == 'text':
                        response_text += (block.get('text') or '')
            except Exception:
                response_text = _json.dumps(response)

            # Validate with LOKI
            modules_to_check = active_modules or list(self.engine.modules.keys())
            validation = self.engine.check_document(
                text=response_text,
                document_type='ai_generated',
                active_modules=modules_to_check
            )

            # Check if should block
            if isinstance(validation, dict) and validation.get('overall_risk') == 'CRITICAL':
                return {
                    'blocked': True,
                    'error': 'LOKI_CRITICAL_ERROR',
                    'message': 'AI response contains critical compliance errors',
                    'validation': validation,
                    'original_response': response_text
                }

            # Return enhanced response
            return {
                'blocked': False,
                'response': response,
                'loki': {
                    'risk': validation.get('overall_risk') if isinstance(validation, dict) else None,
                    'validation': validation,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            return {
                'blocked': True,
                'error': 'INTERCEPTOR_ERROR',
                'message': str(e),
                'original_response': f"[Anthropic API Error: {str(e)}]"
            }

    def intercept_and_validate(self, request_data, api_key, modules=None):
        """
        Intercept API call, validate response, block if critical
        """
        try:
            if not isinstance(request_data, dict):
                raise ValueError('request_data must be a dict')
            if not api_key:
                raise ValueError('Missing API key')

            # Filter to only allowed Anthropic parameters
            allowed_keys = ['model', 'messages', 'max_tokens', 'system', 'temperature', 'top_p', 'stop_sequences']
            filtered_request = {k: v for k, v in request_data.items() if k in allowed_keys}

            # Ensure required fields
            if 'model' not in filtered_request:
                filtered_request['model'] = 'claude-sonnet-4-20250514'
            if 'max_tokens' not in filtered_request:
                filtered_request['max_tokens'] = 1024

            # Direct HTTP call
            url = 'https://api.anthropic.com/v1/messages'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            }
            try:
                resp = requests.post(url, headers=headers, json=filtered_request, timeout=60)
                if resp.status_code >= 400:
                    raise RuntimeError(f"Anthropic HTTP {resp.status_code}: {resp.text}")
                response = resp.json()
            except Exception as e:
                return {
                    'error': f'Anthropic HTTP error: {e}',
                    'blocked': False,
                    'response': {},
                    'validation': {},
                    'loki': {'risk': 'LOW', 'flagged': False, 'action': 'ERROR'}
                }

            # Extract text from response
            response_text = ""
            try:
                for block in (response.get('content') or []):
                    if (block or {}).get('type') == 'text':
                        response_text += (block.get('text') or '')
            except Exception:
                response_text = _json.dumps(response)

            # Validate using existing engine and all loaded modules by default
            modules_to_check = modules or list(self.engine.modules.keys())
            validation = self.engine.check_document(
                text=response_text,
                document_type='ai_generated',
                active_modules=modules_to_check
            )

            overall_risk = validation.get('overall_risk', 'LOW') if isinstance(validation, dict) else 'LOW'

            # Always return response; flag instead of blocking
            return {
                'blocked': False,
                'response': response,
                'validation': validation,
                'loki': {
                    'risk': overall_risk,
                    'flagged': overall_risk != 'LOW',
                    'action': 'FLAGGED' if overall_risk != 'LOW' else 'ALLOWED',
                    'gates_checked': list((validation.get('modules') or {}).keys()) if isinstance(validation, dict) else []
                }
            }
        except Exception as e:
            return {
                'error': str(e),
                'blocked': True,
                'reason': f'Validation error: {str(e)}'
            }


class OpenAIInterceptor:
    def __init__(self, engine):
        self.engine = engine

    def intercept(self, request_data, api_key, active_modules=None):
        import json
        import urllib.request
        import urllib.error

        try:
            if not isinstance(request_data, dict):
                raise ValueError('request_data must be a dict')
            if not api_key:
                raise ValueError('Missing OpenAI API key')

            url = 'https://api.openai.com/v1/chat/completions'
            allowed = {'model', 'messages', 'max_tokens', 'temperature', 'top_p', 'stop'}
            payload = {k: v for k, v in request_data.items() if k in allowed}
            if 'model' not in payload or 'messages' not in payload:
                raise ValueError('Missing required fields: model, messages')

            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {api_key}')
            project_id = request_data.get('project') or os.getenv('OPENAI_PROJECT')
            if project_id:
                req.add_header('OpenAI-Project', project_id)
            try:
                with urllib.request.urlopen(req) as resp:
                    resp_bytes = resp.read()
                    resp_json = json.loads(resp_bytes.decode('utf-8'))
            except urllib.error.HTTPError as e:
                detail = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
                return {'blocked': True, 'error': 'OPENAI_ERROR', 'message': detail, 'original_response': f"[OpenAI API Error: {detail}]"}

            # Extract text
            text = ''
            try:
                text = resp_json['choices'][0]['message']['content']
            except Exception:
                text = json.dumps(resp_json)

            modules_to_check = active_modules or list(self.engine.modules.keys())
            validation = self.engine.check_document(text=text, document_type='ai_generated', active_modules=modules_to_check)
            if isinstance(validation, dict) and validation.get('overall_risk') == 'CRITICAL':
                return {
                    'blocked': True,
                    'error': 'LOKI_CRITICAL_ERROR',
                    'message': 'AI response contains critical compliance errors',
                    'validation': validation,
                    'original_response': text
                }

            resp_json['loki_validation'] = validation
            return resp_json
        except Exception as e:
            return {'blocked': True, 'error': 'INTERCEPTOR_ERROR', 'message': str(e), 'original_response': f"[OpenAI Interceptor Error: {str(e)}]"}


class GeminiInterceptor:
    def __init__(self, engine):
        self.engine = engine

    def intercept(self, request_data, api_key, active_modules=None):
        import json
        import urllib.request
        import urllib.parse
        import urllib.error

        try:
            if not isinstance(request_data, dict):
                raise ValueError('request_data must be a dict')
            if not api_key:
                raise ValueError('Missing Gemini API key')

            model = request_data.get('model', 'gemini-2.5-flash')
            prompt = request_data.get('prompt') or ''
            api_version = 'v1beta' if model.startswith('gemini-1.') else 'v1'
            url = f'https://generativelanguage.googleapis.com/{api_version}/models/{model}:generateContent?key={urllib.parse.quote(api_key)}'

            body = {
                'contents': [
                    {
                        'parts': [{'text': prompt}]
                    }
                ]
            }
            data = json.dumps(body).encode('utf-8')
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            try:
                with urllib.request.urlopen(req) as resp:
                    resp_bytes = resp.read()
                    resp_json = json.loads(resp_bytes.decode('utf-8'))
            except urllib.error.HTTPError as e:
                detail = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
                return {'blocked': True, 'error': 'GEMINI_ERROR', 'message': detail, 'original_response': f"[Gemini API Error: {detail}]"}

            # Extract text
            text = ''
            try:
                candidates = resp_json.get('candidates') or []
                parts = (candidates[0].get('content') or {}).get('parts') or []
                if parts and isinstance(parts[0], dict):
                    text = parts[0].get('text') or ''
            except Exception:
                text = json.dumps(resp_json)

            modules_to_check = active_modules or list(self.engine.modules.keys())
            validation = self.engine.check_document(text=text, document_type='ai_generated', active_modules=modules_to_check)
            if isinstance(validation, dict) and validation.get('overall_risk') == 'CRITICAL':
                return {
                    'blocked': True,
                    'error': 'LOKI_CRITICAL_ERROR',
                    'message': 'AI response contains critical compliance errors',
                    'validation': validation,
                    'original_response': text
                }

            resp_json['loki_validation'] = validation
            return resp_json
        except Exception as e:
            return {'blocked': True, 'error': 'INTERCEPTOR_ERROR', 'message': str(e), 'original_response': f"[Gemini Interceptor Error: {str(e)}]"}
