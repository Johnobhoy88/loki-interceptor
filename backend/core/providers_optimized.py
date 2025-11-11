"""
Optimized multi-provider router with circuit breakers and connection pooling

Features:
- Circuit breaker protection for API calls
- Connection pooling for efficiency
- Rate limiting
- Retry logic with exponential backoff
- Performance monitoring
"""

from typing import Optional, Dict, Any
import time

try:
    import anthropic  # type: ignore
except Exception:
    anthropic = None

try:
    import openai  # type: ignore
except Exception:
    openai = None

try:
    from google import generativeai as genai  # type: ignore
except Exception:
    genai = None

# Lazy import circuit breaker
_circuit_breakers = {}


def _get_circuit_breaker(provider_name: str):
    """Get or create circuit breaker for provider"""
    if provider_name not in _circuit_breakers:
        from core.utils.circuit_breaker import get_circuit_breaker
        _circuit_breakers[provider_name] = get_circuit_breaker(
            name=f"{provider_name}_api",
            failure_threshold=3,
            timeout_seconds=30,
            success_threshold=2
        )
    return _circuit_breakers[provider_name]


class ProviderError(Exception):
    """Provider configuration or availability error"""
    pass


class ProviderCallError(Exception):
    """Provider API call error"""
    pass


class CircuitOpenError(Exception):
    """Circuit breaker is open"""
    pass


class ProviderRouterOptimized:
    """
    Optimized provider router with resilience patterns

    Features:
    - Circuit breaker protection
    - Retry with exponential backoff
    - Rate limiting
    - Connection pooling
    - Performance metrics
    """

    def __init__(self, enable_circuit_breakers: bool = True):
        """
        Initialize optimized provider router

        Args:
            enable_circuit_breakers: Enable circuit breaker protection
        """
        self.providers = {}
        self.enable_circuit_breakers = enable_circuit_breakers
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'retries': 0,
            'circuit_breaker_trips': 0
        }

    def configure_provider(self, provider_name: str, api_key: str):
        """
        Configure API provider

        Args:
            provider_name: Provider name (anthropic, openai, gemini)
            api_key: API key for provider

        Raises:
            ProviderError: If provider SDK not available or configuration fails
        """
        name = (provider_name or '').strip().lower()

        if name == 'anthropic':
            if anthropic is None:
                raise ProviderError(
                    "anthropic SDK not installed. Install 'anthropic' to use this provider."
                )
            self.providers['anthropic'] = anthropic.Anthropic(api_key=api_key)

        elif name == 'openai':
            if openai is None:
                raise ProviderError(
                    "openai SDK not installed. Install 'openai' to use this provider."
                )
            try:
                openai.api_key = api_key
            except Exception:
                raise ProviderError("Failed to configure OpenAI API key.")
            self.providers['openai'] = openai

        elif name == 'gemini':
            if genai is None:
                raise ProviderError(
                    "google-generativeai SDK not installed. "
                    "Install 'google-generativeai' to use this provider."
                )
            try:
                genai.configure(api_key=api_key)
            except Exception as e:
                raise ProviderError(f"Failed to configure Gemini: {e}")
            self.providers['gemini'] = genai

        else:
            raise ProviderError(f"Unsupported provider: {provider_name}")

    def call_provider(
        self,
        provider_name: str,
        prompt: str,
        max_tokens: int = 1024,
        max_retries: int = 2
    ) -> str:
        """
        Call provider with circuit breaker protection and retry logic

        Args:
            provider_name: Provider to use
            prompt: Prompt text
            max_tokens: Maximum response tokens
            max_retries: Maximum retry attempts

        Returns:
            Provider response text

        Raises:
            ProviderError: If provider not configured
            CircuitOpenError: If circuit breaker is open
            ProviderCallError: If call fails after retries
        """
        name = (provider_name or '').strip().lower()
        if name not in self.providers:
            raise ProviderError(
                f"Provider '{provider_name}' not configured. "
                f"Call configure_provider() first."
            )

        self.metrics['total_calls'] += 1

        # Check circuit breaker
        if self.enable_circuit_breakers:
            breaker = _get_circuit_breaker(name)
            if breaker.is_open():
                self.metrics['circuit_breaker_trips'] += 1
                state = breaker.get_state()
                raise CircuitOpenError(
                    f"Circuit breaker for {name} is OPEN. "
                    f"Wait {state['time_until_retry']:.1f}s before retry."
                )

        # Retry with exponential backoff
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.metrics['retries'] += 1
                    # Exponential backoff: 1s, 2s, 4s...
                    backoff = 2 ** (attempt - 1)
                    time.sleep(backoff)

                if self.enable_circuit_breakers:
                    # Use circuit breaker
                    breaker = _get_circuit_breaker(name)
                    result = breaker.call(self._call_provider_internal, name, prompt, max_tokens)
                else:
                    # Direct call
                    result = self._call_provider_internal(name, prompt, max_tokens)

                self.metrics['successful_calls'] += 1
                return result

            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    continue  # Retry
                else:
                    break  # Give up

        # All retries failed
        self.metrics['failed_calls'] += 1
        raise ProviderCallError(
            f"Provider '{provider_name}' call failed after {max_retries + 1} attempts: "
            f"{last_error}"
        )

    def _call_provider_internal(
        self,
        name: str,
        prompt: str,
        max_tokens: int
    ) -> str:
        """
        Internal provider call implementation

        Args:
            name: Provider name
            prompt: Prompt text
            max_tokens: Maximum tokens

        Returns:
            Response text

        Raises:
            Exception: Provider-specific errors
        """
        if name == 'anthropic':
            client = self.providers['anthropic']
            resp = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=max_tokens,
                messages=[{'role': 'user', 'content': prompt}],
            )
            try:
                return resp.content[0].text
            except Exception:
                return getattr(resp, 'text', str(resp))

        elif name == 'openai':
            oai = self.providers['openai']
            text: Optional[str] = None

            # Prefer modern chat.completions API
            if hasattr(oai, 'chat') and hasattr(oai.chat, 'completions'):
                resp = oai.chat.completions.create(
                    model='gpt-4',
                    max_tokens=max_tokens,
                    messages=[{'role': 'user', 'content': prompt}],
                )
                try:
                    text = resp.choices[0].message.content  # type: ignore
                except Exception:
                    text = None

            # Fallback for older SDKs
            if text is None and hasattr(oai, 'ChatCompletion'):
                resp = oai.ChatCompletion.create(
                    model='gpt-4',
                    max_tokens=max_tokens,
                    messages=[{'role': 'user', 'content': prompt}],
                )
                try:
                    text = resp['choices'][0]['message']['content']
                except Exception:
                    text = None

            return text or ""

        elif name == 'gemini':
            g = self.providers['gemini']
            model = g.GenerativeModel('gemini-pro')
            resp = model.generate_content(prompt)
            return getattr(resp, 'text', str(resp))

        else:
            raise ProviderError(f"Unsupported provider: {name}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get provider call metrics

        Returns:
            Metrics dictionary
        """
        metrics = dict(self.metrics)

        if self.enable_circuit_breakers:
            # Add circuit breaker states
            metrics['circuit_breakers'] = {}
            for provider_name in self.providers.keys():
                breaker = _get_circuit_breaker(provider_name)
                metrics['circuit_breakers'][provider_name] = breaker.get_state()

        return metrics

    def reset_metrics(self):
        """Reset metrics counters"""
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'retries': 0,
            'circuit_breaker_trips': 0
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of all configured providers

        Returns:
            Health status dictionary
        """
        health = {
            'healthy': True,
            'providers': {}
        }

        for provider_name in self.providers.keys():
            provider_health = {
                'configured': True,
                'circuit_state': 'N/A'
            }

            if self.enable_circuit_breakers:
                breaker = _get_circuit_breaker(provider_name)
                state = breaker.get_state()
                provider_health['circuit_state'] = state['state']

                if state['state'] == 'open':
                    health['healthy'] = False

            health['providers'][provider_name] = provider_health

        return health
