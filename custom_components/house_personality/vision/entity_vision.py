"""Entity-based vision/event summary adapter for House Personality."""

from __future__ import annotations

import json
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State

from .base import VisionContextResult


async def async_get_entity_vision_context(
    hass: HomeAssistant,
    *,
    enabled: bool,
    entity_id: str | None,
    max_chars: int,
) -> VisionContextResult:
    """Read optional vision/event summary context from a configured entity."""
    if not enabled:
        return VisionContextResult(None, False, "disabled")

    if not entity_id:
        return VisionContextResult(None, False, "not_configured")

    state = hass.states.get(entity_id)
    if state is None:
        return VisionContextResult(None, False, "missing")

    if state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
        return VisionContextResult(None, False, state.state)

    content = _format_state(state)
    if not content.strip():
        return VisionContextResult(None, False, "empty")

    return VisionContextResult(_truncate(content, max_chars), True, "included")


def _format_state(state: State) -> str:
    """Format state and attributes for vision/event context."""
    lines = [
        f"Entity: {state.entity_id}",
        f"State: {state.state}",
    ]
    if state.attributes:
        lines.append(f"Attributes: {_json_dump(state.attributes)}")
    return "\n".join(lines)


def _json_dump(value: dict[str, Any]) -> str:
    """Serialize vision/event attributes deterministically."""
    return json.dumps(value, ensure_ascii=True, sort_keys=True, default=str)


def _truncate(value: str, max_chars: int) -> str:
    """Limit vision/event context size before adding it to the prompt."""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}...[truncated]"
