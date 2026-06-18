"""Prompt assembly for House Personality."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptContext:
    """Structured inputs used to build a provider prompt."""

    personality_prompt: str
    user_message: str
    household_context: str | None = None
    speaker_identity: str | None = None
    location_context: str | None = None
    room_status_context: str | None = None
    house_memory_summary: str | None = None
    memory_context: str | None = None
    vision_context: str | None = None


def build_chat_messages(context: PromptContext) -> list[dict[str, str]]:
    """Build OpenAI-compatible chat messages."""
    messages = [
        {
            "role": "system",
            "content": context.personality_prompt.strip(),
        }
    ]

    if context.household_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Optional home context from the configured context entity:\n"
                    f"{context.household_context.strip()}"
                ),
            }
        )

    if context.speaker_identity:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Optional speaker identity from the configured identity entity:\n"
                    f"{context.speaker_identity.strip()}"
                ),
            }
        )

    if context.location_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Optional person or room location context from the configured location entity:\n"
                    f"{context.location_context.strip()}"
                ),
            }
        )

    if context.room_status_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Optional public-space room status from the configured room status entity:\n"
                    f"{context.room_status_context.strip()}"
                ),
            }
        )

    if context.house_memory_summary:
        messages.append(
            {
                "role": "system",
                "content": context.house_memory_summary.strip(),
            }
        )

    if context.memory_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Optional relevant memory from the configured memory entity:\n"
                    f"{context.memory_context.strip()}"
                ),
            }
        )

    if context.vision_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Optional recent vision or event summary from the configured entity:\n"
                    f"{context.vision_context.strip()}"
                ),
            }
        )

    messages.append(
        {
            "role": "user",
            "content": context.user_message.strip(),
        }
    )
    return messages


def describe_prompt_sections(context: PromptContext) -> dict[str, bool]:
    """Return non-sensitive prompt section metadata for logging."""
    return {
        "personality_prompt": bool(context.personality_prompt.strip()),
        "household_context": bool(context.household_context),
        "speaker_identity": bool(context.speaker_identity),
        "location_context": bool(context.location_context),
        "room_status_context": bool(context.room_status_context),
        "house_memory_summary": bool(context.house_memory_summary),
        "memory_context": bool(context.memory_context),
        "vision_context": bool(context.vision_context),
        "user_message": bool(context.user_message.strip()),
    }
