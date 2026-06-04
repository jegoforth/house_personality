"""Voice Assist Recall adapter for House Personality."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .base import MemoryResult

ATTR_CONTEXT = "context"
ATTR_CONVERSATION_ID = "conversation_id"
ATTR_INCLUDE_TURNS = "include_turns"
ATTR_LIMIT = "limit"
ATTR_MAX_LENGTH = "max_length"
ATTR_QUERY = "query"
ATTR_RELEVANT = "relevant"
ATTR_SPEAKER_ID = "speaker_id"


async def async_get_recall_memory(
    hass: HomeAssistant,
    *,
    enabled: bool,
    service_domain: str,
    service_name: str,
    query: str,
    speaker_id: str | None,
    conversation_id: str | None,
    limit: int,
    include_turns: bool,
    max_chars: int,
) -> MemoryResult:
    """Read optional prompt-safe memory from Voice Assist Recall."""
    if not enabled:
        return MemoryResult(None, False, "disabled")

    if not service_domain or not service_name:
        return MemoryResult(None, False, "service_not_configured")

    if not hass.services.has_service(service_domain, service_name):
        return MemoryResult(None, False, "service_missing")

    service_data: dict[str, Any] = {
        ATTR_QUERY: query,
        ATTR_LIMIT: limit,
        ATTR_MAX_LENGTH: max_chars,
        ATTR_INCLUDE_TURNS: include_turns,
    }
    if speaker_id:
        service_data[ATTR_SPEAKER_ID] = speaker_id
    if conversation_id:
        service_data[ATTR_CONVERSATION_ID] = conversation_id

    try:
        response = await hass.services.async_call(
            service_domain,
            service_name,
            service_data,
            blocking=True,
            return_response=True,
        )
    except Exception:
        return MemoryResult(None, False, "service_failed")

    if not isinstance(response, dict):
        return MemoryResult(None, False, "invalid_response")

    if not response.get(ATTR_RELEVANT, False):
        return MemoryResult(None, False, "not_relevant")

    context = response.get(ATTR_CONTEXT)
    if not isinstance(context, str) or not context.strip():
        return MemoryResult(None, False, "empty")

    return MemoryResult(_truncate(context.strip(), max_chars), True, "included")


def _truncate(value: str, max_chars: int) -> str:
    """Limit recall size before adding it to the prompt."""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}...[truncated]"
