"""Entity-based public-space room status adapter for House Personality."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.util import dt as dt_util


@dataclass(frozen=True, slots=True)
class EntityRoomStatusResult:
    """Result from reading an optional room status entity."""

    content: str | None
    included: bool
    reason: str


async def async_get_entity_room_status(
    hass: HomeAssistant,
    entity_id: str | None,
    *,
    max_chars: int,
) -> EntityRoomStatusResult:
    """Read optional public-space room status from a configured entity."""
    if not entity_id:
        return EntityRoomStatusResult(None, False, "not_configured")

    state = hass.states.get(entity_id)
    if state is None:
        return EntityRoomStatusResult(None, False, "missing")

    if state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
        return EntityRoomStatusResult(None, False, state.state)

    if _is_private_space(state):
        return EntityRoomStatusResult(None, False, "private_space")

    if _is_stale(state):
        return EntityRoomStatusResult(None, False, "stale")

    content = _format_room_status(state)
    if not content.strip():
        return EntityRoomStatusResult(None, False, "empty")

    return EntityRoomStatusResult(_truncate(content, max_chars), True, "included")


def _format_room_status(state: State) -> str:
    """Format a room status entity using prompt-safe contract fields."""
    attributes = state.attributes or {}
    lines = [
        f"Entity: {state.entity_id}",
        f"State: {state.state}",
    ]

    field_labels = (
        ("summary", "Summary"),
        ("room", "Room"),
        ("area", "Area"),
        ("area_id", "Area ID"),
        ("occupancy", "Occupancy"),
        ("occupied", "Occupied"),
        ("people_count", "People count"),
        ("activity", "Activity"),
        ("event_type", "Event type"),
        ("confidence", "Confidence"),
        ("public_space", "Public space"),
        ("source", "Source"),
        ("observed_at", "Observed at"),
        ("updated_at", "Updated at"),
        ("expires_at", "Expires at"),
        ("stale_after_seconds", "Stale after seconds"),
    )
    for key, label in field_labels:
        value = attributes.get(key)
        if value is None or value == "":
            continue
        lines.append(f"{label}: {value}")

    return "\n".join(lines)


def _is_private_space(state: State) -> bool:
    """Return whether room status should be skipped for private spaces."""
    attributes = state.attributes or {}
    public_space = attributes.get("public_space")
    if isinstance(public_space, bool):
        return not public_space
    if isinstance(public_space, str):
        normalized = public_space.strip().lower()
        if normalized in {"false", "no", "private"}:
            return True
    return False


def _is_stale(state: State) -> bool:
    """Return whether a room status entity is stale by contract timestamps."""
    attributes = state.attributes or {}
    now = _utc_now()

    expires_at = _parse_datetime(attributes.get("expires_at"))
    if expires_at is not None and expires_at <= now:
        return True

    stale_after = _parse_positive_int(attributes.get("stale_after_seconds"))
    if stale_after is None:
        return False

    updated_at = _parse_datetime(attributes.get("updated_at"))
    observed_at = _parse_datetime(attributes.get("observed_at"))
    reference = updated_at or observed_at
    if reference is None:
        return False

    return reference + timedelta(seconds=stale_after) <= now


def _parse_datetime(value: Any) -> datetime | None:
    """Parse a Home Assistant-style datetime value."""
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = dt_util.parse_datetime(str(value))
        except (TypeError, ValueError):
            return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt_util.UTC)
    return parsed.astimezone(dt_util.UTC)


def _utc_now() -> datetime:
    """Return an aware UTC datetime."""
    now = dt_util.utcnow()
    if now.tzinfo is None:
        return now.replace(tzinfo=dt_util.UTC)
    return now.astimezone(dt_util.UTC)


def _parse_positive_int(value: Any) -> int | None:
    """Parse a positive integer."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _truncate(value: str, max_chars: int) -> str:
    """Limit room status context size before adding it to the prompt."""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}...[truncated]"
