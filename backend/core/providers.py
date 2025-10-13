"""
Unified multi-provider router for Anthropic, OpenAI, and Gemini.
This module keeps imports tolerant: if a provider SDK is missing,
configure_provider will raise a descriptive error for that provider.
"""

from typing import Optional

try:
    import anthropic  # type: ignore
except Exception:  # pragma: no cover
    anthropic = None  # graceful handling if not installed

try:
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None

try:
    from google import generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None


class ProviderError(Exception):
    pass


class ProviderCallError(Exception):
    pass


class ProviderRouter:
    def __init__(self):
        self.providers = {}

    def configure_provider(self, provider_name: str, api_key: str):
        name = (provider_name or '').strip().lower()
        if name == 'anthropic':
            if anthropic is None:
                raise ProviderError("anthropic SDK not installed. Install 'anthropic' to use this provider.")
            self.providers['anthropic'] = anthropic.Anthropic(api_key=api_key)
        elif name == 'openai':
            if openai is None:
                raise ProviderError("openai SDK not installed. Install 'openai' to use this provider.")
            try:
                # Modern SDK
                openai.api_key = api_key  # legacy style still respected by many versions
            except Exception:
                raise ProviderError("Failed to configure OpenAI API key.")
            self.providers['openai'] = openai
        elif name == 'gemini':
            if genai is None:
                raise ProviderError("google-generativeai SDK not installed. Install 'google-generativeai' to use this provider.")
            try:
                genai.configure(api_key=api_key)
            except Exception as e:  # pragma: no cover
                raise ProviderError(f"Failed to configure Gemini: {e}")
            self.providers['gemini'] = genai
        else:
            raise ProviderError(f"Unsupported provider: {provider_name}")

    def call_provider(self, provider_name: str, prompt: str, max_tokens: int = 1024) -> str:
        name = (provider_name or '').strip().lower()
        if name not in self.providers:
            raise ProviderError(f"Provider '{provider_name}' not configured. Call configure_provider() first.")

        try:
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
                    # Fallback to string
                    return getattr(resp, 'text', str(resp))

            elif name == 'openai':
                oai = self.providers['openai']
                text: Optional[str] = None
                # Prefer modern chat.completions API if present
                if hasattr(oai, 'chat') and hasattr(oai.chat, 'completions'):
                    resp = oai.chat.completions.create(
                        model='gpt-4',
                        max_tokens=max_tokens,
                        messages=[{'role': 'user', 'content': prompt}],
                    )
                    try:
                        text = resp.choices[0].message.content  # type: ignore[attr-defined]
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
                raise ProviderError(f"Unsupported provider: {provider_name}")

        except Exception as e:
            raise ProviderCallError(f"Provider '{provider_name}' call failed: {e}")

