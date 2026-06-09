"""Entity-based location context adapter for House Personality."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.util import dt as dt_util


@dataclass(frozen=True, slots=True)
class EntityLocationResult:
    """Result from reading an optional location context entity."""

    content: str | None
    included: bool
    reason: str


async def async_get_entity_location(
    hass: HomeAssistant,
    entity_id: str | None,
    *,
    max_chars: int,
) -> EntityLocationResult:
    """Read optional location context from a configured entity."""
    if not entity_id:
        return EntityLocationResult(None, False, "not_configured")

    state = hass.states.get(entity_id)
    if state is None:
        return EntityLocationResult(None, False, "missing")

    if state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
        return EntityLocationResult(None, False, state.state)

    if _is_stale(state):
        return EntityLocationResult(None, False, "stale")

    content = _format_location(state)
    if not content.strip():
        return EntityLocationResult(None, False, "empty")

    return EntityLocationResult(_truncate(content, max_chars), True, "included")


def _format_location(state: State) -> str:
    """Format a location entity using safe contract fields."""
    attributes = state.attributes or {}
    lines = [
        f"Entity: {state.entity_id}",
        f"State: {state.state}",
    ]

    field_labels = (
        ("person_label", "Person"),
        ("home_state", "Home state"),
        ("room", "Room"),
        ("current_room", "Room"),
        ("area", "Area"),
        ("area_id", "Area ID"),
        ("zone", "Zone"),
        ("confidence", "Confidence"),
        ("source", "Source"),
        ("observed_at", "Observed at"),
        ("updated_at", "Updated at"),
        ("expires_at", "Expires at"),
        ("stale_after_seconds", "Stale after seconds"),
    )
    seen_labels: set[str] = set()
    for key, label in field_labels:
        if label in seen_labels:
            continue
        value = attributes.get(key)
        if value is None or value == "":
            continue
        lines.append(f"{label}: {value}")
        seen_labels.add(label)

    return "\n".join(lines)


def _is_stale(state: State) -> bool:
    """Return whether a location entity is stale by contract timestamps."""
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
    """Limit location context size before adding it to the prompt."""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}...[truncated]"
