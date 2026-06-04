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
    memory_context: str | None = None


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
        "memory_context": bool(context.memory_context),
        "user_message": bool(context.user_message.strip()),
    }
