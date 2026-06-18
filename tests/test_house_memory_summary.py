"""Tests for House Memory Summary prompt injection."""

from __future__ import annotations

import unittest

from tests.common import homeassistant_stubs


class _FakeState:
    def __init__(self, state: str, attributes: dict):
        self.state = state
        self.attributes = attributes


class _FakeStates:
    def __init__(self, state):
        self._state = state

    def get(self, entity_id: str):
        return self._state


class _FakeHass:
    def __init__(self, state):
        self.states = _FakeStates(state)


class HouseMemorySummaryTests(unittest.TestCase):
    """Test direct House Memory Summary prompt context."""

    def test_prompt_includes_house_people_rooms_and_privacy(self) -> None:
        """Selected summary attributes should be injected under clear headings."""
        with homeassistant_stubs():
            from custom_components.house_personality.context.house_memory_summary import (
                format_house_memory_summary_attributes,
            )

            content = format_house_memory_summary_attributes(
                {
                    "house": "Family home context",
                    "people_summary": "Eric and Shelley live here.",
                    "rooms_summary": [
                        {
                            "name": "Eric's Office",
                            "privacy_class": "public",
                        },
                        {
                            "name": "Guest Room",
                            "privacy_class": "private",
                        },
                    ],
                    "privacy_rules": "Only privacy_class=private is private.",
                }
            )

        self.assertIn("House memory:\nFamily home context", content)
        self.assertIn("People:\nEric and Shelley live here.", content)
        self.assertIn("Rooms:\n", content)
        self.assertIn('"privacy_class": "public"', content)
        self.assertIn("Privacy rules:\nOnly privacy_class=private is private.", content)
        self.assertIn(
            "Use the injected House Memory Summary attributes as the source of truth",
            content,
        )

    def test_prompt_omits_memory_cleanly_when_sensor_unavailable(self) -> None:
        """Unavailable memory should add a short internal note and no entity id."""
        with homeassistant_stubs():
            from custom_components.house_personality.context.house_memory_summary import (
                get_house_memory_summary_context,
            )

            result = get_house_memory_summary_context(
                _FakeHass(_FakeState("unavailable", {})),
                "sensor.house_memory_summary",
            )

        self.assertFalse(result.included)
        self.assertEqual(result.reason, "unavailable")
        self.assertEqual(result.content, "House memory is unavailable.")
        self.assertNotIn("sensor.house_memory_summary", result.content)
        self.assertNotIn("Rooms:", result.content)

    def test_privacy_rule_instruction_is_included(self) -> None:
        """Room privacy answers should be constrained to explicit privacy fields."""
        with homeassistant_stubs():
            from custom_components.house_personality.context.house_memory_summary import (
                format_house_memory_summary_attributes,
            )

            content = format_house_memory_summary_attributes(
                {
                    "rooms_summary": [
                        {
                            "name": "Shelley's Office",
                            "room_type": "office",
                            "occupant": "Shelley",
                            "privacy_class": "public",
                        }
                    ],
                    "privacy_rules": "Use explicit privacy_class values only.",
                }
            )

        self.assertIn(
            "When answering room privacy questions, use only rooms_summary "
            "privacy fields and privacy_rules.",
            content,
        )
        self.assertIn(
            "Do not infer privacy from room name, room_type, occupant, or layout.",
            content,
        )

    def test_personality_text_remains_separate_from_memory_context(self) -> None:
        """The 255-character personality prompt remains only tone/persona text."""
        with homeassistant_stubs():
            from custom_components.house_personality.context.house_memory_summary import (
                format_house_memory_summary_attributes,
            )
            from custom_components.house_personality.context.prompt_builder import (
                PromptContext,
                build_chat_messages,
            )

            context = PromptContext(
                personality_prompt="Warm, concise tone.",
                user_message="Which rooms are private?",
                house_memory_summary=format_house_memory_summary_attributes(
                    {
                        "house": "Memory belongs here.",
                        "privacy_rules": "Use privacy_class only.",
                    }
                ),
            )

            messages = build_chat_messages(context)

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "Warm, concise tone.")
        self.assertIn("House memory:\nMemory belongs here.", messages[1]["content"])
        self.assertNotIn("Memory belongs here.", messages[0]["content"])


if __name__ == "__main__":
    unittest.main()
