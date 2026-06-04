"""Base provider interfaces for House Personality."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    """Normalized provider response."""

    content: str


class ProviderError(Exception):
    """Raised when a provider request fails."""


class ChatProvider(Protocol):
    """Protocol for chat completion providers."""

    async def async_generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> ProviderResponse:
        """Generate a response from provider messages."""

