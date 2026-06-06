"""OpenAI-compatible chat completions provider."""

from __future__ import annotations

import json
import logging
from typing import Any

import async_timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base import (
    ProviderChatResponse,
    ProviderError,
    ProviderResponse,
    ProviderToolCall,
)

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
        max_tokens: int,
        timeout: int,
        tool_choice: str,
        parallel_tool_calls: bool,
        response_format: str,
        debug_logging: bool,
    ) -> None:
        """Initialize the provider."""
        self._hass = hass
        self._base_url = base_url
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout
        self._tool_choice = tool_choice
        self._parallel_tool_calls = parallel_tool_calls
        self._response_format = response_format
        self._debug_logging = debug_logging

    async def async_generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> ProviderResponse:
        """Generate a chat completion response."""
        response = await self.async_generate_chat_completion(messages)
        if response.tool_calls:
            raise ProviderError("Provider returned tool calls for a text-only request")
        if not response.content:
            raise ProviderError("Provider returned an empty response")
        return ProviderResponse(content=response.content.strip())

    async def async_generate_chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ProviderChatResponse:
        """Generate a chat completion response with optional tools."""
        url = _chat_completions_url(self._base_url)
        session = async_get_clientsession(self._hass)
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = _build_chat_completion_payload(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            tools=tools,
            tool_choice=self._tool_choice,
            parallel_tool_calls=self._parallel_tool_calls,
            response_format=self._response_format,
        )

        if self._debug_logging:
            _LOGGER.debug(
                "Sending chat completion request to provider: "
                "model=%s url=%s messages=%s tools=%s max_tokens=%s "
                "tool_choice=%s parallel_tool_calls=%s response_format=%s",
                self._model,
                url,
                len(messages),
                len(tools or []),
                self._max_tokens or "provider_default",
                self._tool_choice if tools else "not_sent",
                self._parallel_tool_calls if tools else "not_sent",
                self._response_format,
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
                        message = data["choices"][0]["message"]
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

        content = message.get("content")
        if content is not None and not isinstance(content, str):
            raise ProviderError("Provider returned invalid response content")

        tool_calls = _parse_tool_calls(message.get("tool_calls"))
        if (not content or not content.strip()) and not tool_calls:
            raise ProviderError("Provider returned an empty response")

        return ProviderChatResponse(
            content=content.strip() if isinstance(content, str) else None,
            tool_calls=tool_calls,
        )


def _chat_completions_url(base_url: str) -> str:
    """Build a chat completions URL from a configured provider base URL."""
    normalized = base_url.strip().rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def _build_chat_completion_payload(
    *,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float,
    max_tokens: int,
    tools: list[dict[str, Any]] | None,
    tool_choice: str,
    parallel_tool_calls: bool,
    response_format: str,
) -> dict[str, Any]:
    """Build an OpenAI-compatible chat completions payload."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens > 0:
        payload["max_tokens"] = max_tokens
    if response_format != "default":
        payload["response_format"] = {"type": response_format}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice
        payload["parallel_tool_calls"] = parallel_tool_calls
    return payload


def _truncate(value: str, max_length: int) -> str:
    """Truncate provider diagnostic text."""
    if len(value) <= max_length:
        return value
    return f"{value[:max_length]}..."


def _parse_tool_calls(value: Any) -> list[ProviderToolCall]:
    """Parse OpenAI-compatible tool calls."""
    if not value:
        return []
    if not isinstance(value, list):
        raise ProviderError("Provider returned invalid tool calls")

    tool_calls: list[ProviderToolCall] = []
    for item in value:
        if not isinstance(item, dict):
            raise ProviderError("Provider returned invalid tool call")

        function = item.get("function")
        if not isinstance(function, dict):
            raise ProviderError("Provider returned invalid function call")

        name = function.get("name")
        arguments = function.get("arguments", "{}")
        if not isinstance(name, str) or not name:
            raise ProviderError("Provider returned unnamed function call")
        if not isinstance(arguments, str):
            raise ProviderError("Provider returned invalid function arguments")

        try:
            parsed_arguments = json.loads(arguments or "{}")
        except json.JSONDecodeError as err:
            raise ProviderError("Provider returned malformed function arguments") from err

        if not isinstance(parsed_arguments, dict):
            raise ProviderError("Provider returned non-object function arguments")

        tool_calls.append(
            ProviderToolCall(
                tool_call_id=str(item.get("id") or name),
                name=name,
                arguments=parsed_arguments,
            )
        )

    return tool_calls
