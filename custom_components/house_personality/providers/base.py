"""Base provider interfaces for House Personality."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    """Normalized provider response."""

    content: str


@dataclass(frozen=True, slots=True)
class ProviderToolCall:
    """Normalized provider tool call."""

    tool_call_id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ProviderChatResponse:
    """Normalized provider chat completion response."""

    content: str | None
    tool_calls: list[ProviderToolCall]


class ProviderError(Exception):
    """Raised when a provider request fails."""


class ChatProvider(Protocol):
    """Protocol for chat completion providers."""

    async def async_generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> ProviderResponse:
        """Generate a response from provider messages."""
