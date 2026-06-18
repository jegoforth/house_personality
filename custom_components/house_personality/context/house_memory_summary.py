"""House Memory Summary prompt context for House Personality."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

STATE_UNAVAILABLE = "unavailable"
STATE_UNKNOWN = "unknown"

ATTR_HOUSE = "house"
ATTR_PEOPLE_SUMMARY = "people_summary"
ATTR_ROOMS_SUMMARY = "rooms_summary"
ATTR_PRIVACY_RULES = "privacy_rules"
ATTR_CONTEXT_SOURCES = "context_sources"
ATTR_ASSISTANT_PROFILE = "assistant_profile"

_ATTRIBUTE_HEADINGS = (
    (ATTR_HOUSE, "House memory"),
    (ATTR_PEOPLE_SUMMARY, "People"),
    (ATTR_ROOMS_SUMMARY, "Rooms"),
    (ATTR_PRIVACY_RULES, "Privacy rules"),
    (ATTR_CONTEXT_SOURCES, "Context sources"),
    (ATTR_ASSISTANT_PROFILE, "Assistant profile"),
)

_SOURCE_OF_TRUTH_INSTRUCTION = (
    "Use the injected House Memory Summary attributes as the source of truth "
    "for house memory. Do not rely on live entity lookup for "
    "sensor.house_memory_summary."
)
_ROOM_PRIVACY_INSTRUCTION = (
    "When answering room privacy questions, use only rooms_summary privacy "
    "fields and privacy_rules. Do not infer privacy from room name, room_type, "
    "occupant, or layout."
)
_UNAVAILABLE_NOTE = "House memory is unavailable."


@dataclass(frozen=True, slots=True)
class HouseMemorySummaryResult:
    """Prompt context extracted from the House Memory Summary sensor."""

    content: str
    included: bool
    reason: str


def get_house_memory_summary_context(
    hass: Any,
    entity_id: str,
) -> HouseMemorySummaryResult:
    """Read prompt-safe House Memory Summary attributes directly from states."""
    state = hass.states.get(entity_id)
    if state is None:
        return HouseMemorySummaryResult(_UNAVAILABLE_NOTE, False, "missing")

    if state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
        return HouseMemorySummaryResult(_UNAVAILABLE_NOTE, False, state.state)

    content = format_house_memory_summary_attributes(state.attributes)
    if not content:
        return HouseMemorySummaryResult(_UNAVAILABLE_NOTE, False, "empty")

    return HouseMemorySummaryResult(content, True, "included")


def format_house_memory_summary_attributes(attributes: dict[str, Any]) -> str:
    """Format selected House Memory Summary attributes for prompt injection."""
    sections = [
        _SOURCE_OF_TRUTH_INSTRUCTION,
        _ROOM_PRIVACY_INSTRUCTION,
    ]

    for attribute, heading in _ATTRIBUTE_HEADINGS:
        value = attributes.get(attribute)
        if value in (None, ""):
            continue
        sections.append(f"{heading}:\n{_format_value(value)}")

    if len(sections) == 2:
        return ""

    return "\n\n".join(sections)


def _format_value(value: Any) -> str:
    """Return a deterministic prompt representation for an attribute value."""
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, default=str)
