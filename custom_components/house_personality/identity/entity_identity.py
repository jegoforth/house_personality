"""Entity-based speaker identity adapter for House Personality."""

from __future__ import annotations

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant

from .base import IdentityResult


async def async_get_entity_identity(
    hass: HomeAssistant,
    entity_id: str | None,
    *,
    max_chars: int,
) -> IdentityResult:
    """Read optional speaker identity from a configured entity."""
    if not entity_id:
        return IdentityResult(None, False, "not_configured")

    state = hass.states.get(entity_id)
    if state is None:
        return IdentityResult(None, False, "missing")

    accepted = state.attributes.get("accepted")
    if accepted is not None and accepted is not True:
        return IdentityResult(
            None,
            False,
            state.attributes.get("rejection_reason") or "not_accepted",
        )

    if state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
        return IdentityResult(None, False, state.state)

    speaker = state.state.strip()
    if not speaker:
        return IdentityResult(None, False, "empty")

    return IdentityResult(_truncate(speaker, max_chars), True, "included")


def _truncate(value: str, max_chars: int) -> str:
    """Limit identity size before adding it to the prompt."""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}...[truncated]"
