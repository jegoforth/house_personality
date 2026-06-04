"""OpenAI-compatible chat completions provider."""

from __future__ import annotations

import logging
from typing import Any

import async_timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base import ProviderError, ProviderResponse

_LOGGER = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    """Provider for OpenAI-compatible chat completions APIs."""

    def __init__(
        self,
        hass,
        *,
        base_url: str,
        api_key: str | None,
        model: str,
        temperature: float,
        timeout: int,
        debug_logging: bool,
    ) -> None:
        """Initialize the provider."""
        self._hass = hass
        self._base_url = base_url
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._timeout = timeout
        self._debug_logging = debug_logging

    async def async_generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> ProviderResponse:
        """Generate a chat completion response."""
        url = _chat_completions_url(self._base_url)
        session = async_get_clientsession(self._hass)
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
        }

        if self._debug_logging:
            _LOGGER.debug(
                "Sending chat completion request to provider: model=%s url=%s messages=%s",
                self._model,
                url,
                len(messages),
            )

        try:
            async with async_timeout.timeout(self._timeout):
                async with session.post(url, headers=headers, json=payload) as response:
                    response_text = await response.text()
                    if response.status >= 400:
                        _LOGGER.warning(
                            "Provider returned HTTP %s: %s",
                            response.status,
                            _truncate(response_text, 300),
                        )
                        raise ProviderError(f"Provider returned HTTP {response.status}")

                    try:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                    except Exception as err:
                        raise ProviderError(
                            "Provider returned an unexpected response"
                        ) from err
        except TimeoutError as err:
            raise ProviderError("Provider request timed out") from err
        except ProviderError:
            raise
        except Exception as err:
            raise ProviderError("Provider request failed") from err

        if not isinstance(content, str) or not content.strip():
            raise ProviderError("Provider returned an empty response")

        return ProviderResponse(content=content.strip())


def _chat_completions_url(base_url: str) -> str:
    """Build a chat completions URL from a configured provider base URL."""
    normalized = base_url.strip().rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def _truncate(value: str, max_length: int) -> str:
    """Truncate provider diagnostic text."""
    if len(value) <= max_length:
        return value
    return f"{value[:max_length]}..."
