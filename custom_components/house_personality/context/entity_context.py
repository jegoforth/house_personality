"""Entity-based context adapter for House Personality."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State


@dataclass(frozen=True, slots=True)
class EntityContextResult:
    """Result from reading an optional context entity."""

    content: str | None
    included: bool
    reason: str


async def async_get_entity_context(
    hass: HomeAssistant,
    entity_id: str | None,
    *,
    max_chars: int,
) -> EntityContextResult:
    """Read optional household context from a configured entity."""
    if not entity_id:
        return EntityContextResult(None, False, "not_configured")

    state = hass.states.get(entity_id)
    if state is None:
        return EntityContextResult(None, False, "missing")

    if state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
        return EntityContextResult(None, False, state.state)

    return EntityContextResult(
        _truncate(_format_state(state), max_chars),
        True,
        "included",
    )


def _format_state(state: State) -> str:
    """Format state and attributes for prompt context."""
    lines = [
        f"Entity: {state.entity_id}",
        f"State: {state.state}",
    ]
    if state.attributes:
        lines.append(f"Attributes: {_json_dump(state.attributes)}")
    return "\n".join(lines)


def _json_dump(value: dict[str, Any]) -> str:
    """Serialize entity attributes deterministically."""
    return json.dumps(value, ensure_ascii=True, sort_keys=True, default=str)


def _truncate(value: str, max_chars: int) -> str:
    """Limit context size before adding it to the prompt."""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}...[truncated]"
