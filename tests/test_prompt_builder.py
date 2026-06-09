"""Tests for prompt assembly."""

from __future__ import annotations

import unittest

from tests.common import homeassistant_stubs


class PromptBuilderTests(unittest.TestCase):
    """Test prompt assembly behavior."""

    def test_build_chat_messages_includes_optional_sections_in_order(self) -> None:
        """All prompt sections should be represented as ordered chat messages."""
        with homeassistant_stubs():
            from custom_components.house_personality.context.prompt_builder import (
                PromptContext,
                build_chat_messages,
                describe_prompt_sections,
            )

            context = PromptContext(
                personality_prompt="Be concise.",
                user_message="What changed?",
                household_context="Context text",
                speaker_identity="Guest",
                location_context="Person A may be in Kitchen.",
                memory_context="Memory text",
                vision_context="Event text",
            )

            messages = build_chat_messages(context)

        self.assertEqual(
            [message["role"] for message in messages],
            ["system", "system", "system", "system", "system", "system", "user"],
        )
        self.assertEqual(messages[0]["content"], "Be concise.")
        self.assertIn("configured context entity", messages[1]["content"])
        self.assertIn("configured identity entity", messages[2]["content"])
        self.assertIn("configured location entity", messages[3]["content"])
        self.assertIn("configured memory entity", messages[4]["content"])
        self.assertIn("configured entity", messages[5]["content"])
        self.assertEqual(messages[-1]["content"], "What changed?")
        self.assertEqual(
            describe_prompt_sections(context),
            {
                "personality_prompt": True,
                "household_context": True,
                "speaker_identity": True,
                "location_context": True,
                "memory_context": True,
                "vision_context": True,
                "user_message": True,
            },
        )

    def test_build_chat_messages_skips_missing_optional_sections(self) -> None:
        """Missing optional context should not create empty system messages."""
        with homeassistant_stubs():
            from custom_components.house_personality.context.prompt_builder import (
                PromptContext,
                build_chat_messages,
            )

            messages = build_chat_messages(
                PromptContext(
                    personality_prompt="Be helpful.",
                    user_message="Hello",
                )
            )

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1], {"role": "user", "content": "Hello"})


if __name__ == "__main__":
    unittest.main()
