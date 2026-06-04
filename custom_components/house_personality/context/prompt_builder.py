"""Prompt assembly for House Personality."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptContext:
    """Structured inputs used to build a provider prompt."""

    personality_prompt: str
    user_message: str


def build_chat_messages(context: PromptContext) -> list[dict[str, str]]:
    """Build OpenAI-compatible chat messages."""
    return [
        {
            "role": "system",
            "content": context.personality_prompt.strip(),
        },
        {
            "role": "user",
            "content": context.user_message.strip(),
        },
    ]


def describe_prompt_sections(context: PromptContext) -> dict[str, bool]:
    """Return non-sensitive prompt section metadata for logging."""
    return {
        "personality_prompt": bool(context.personality_prompt.strip()),
        "user_message": bool(context.user_message.strip()),
    }

