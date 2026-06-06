"""Tests for conversation tool policy helpers."""

from __future__ import annotations

import unittest

from tests.common import homeassistant_stubs


class ConversationPolicyTests(unittest.TestCase):
    """Test no-tools conversation policy."""

    def test_provider_tools_enabled_respects_switch_and_tool_choice(self) -> None:
        """Tools should be disabled by either the switch or tool_choice=none."""
        with homeassistant_stubs():
            from custom_components.house_personality.conversation import (
                _provider_tools_enabled,
            )

            self.assertTrue(
                _provider_tools_enabled(
                    {"tools_enabled": True, "tool_choice": "auto"}
                )
            )
            self.assertFalse(
                _provider_tools_enabled(
                    {"tools_enabled": False, "tool_choice": "auto"}
                )
            )
            self.assertFalse(
                _provider_tools_enabled(
                    {"tools_enabled": True, "tool_choice": "none"}
                )
            )

    def test_disabled_tool_prompt_disallows_home_control_claims(self) -> None:
        """The disabled-tools prompt should tell the model not to fake actions."""
        with homeassistant_stubs():
            from custom_components.house_personality.context.prompt_builder import (
                PromptContext,
            )
            from custom_components.house_personality.conversation import (
                _system_prompt_from_prompt_context,
            )

            prompt = _system_prompt_from_prompt_context(
                PromptContext(
                    personality_prompt="Be concise.",
                    user_message="Turn off the light.",
                ),
                include_tool_instructions=False,
            )

        self.assertIn("Home Assistant tools are disabled", prompt)
        self.assertIn("cannot inspect live Home Assistant entity states", prompt)
        self.assertIn("Do not say", prompt)
        self.assertNotIn("call the\n  available Home Assistant tools", prompt)


if __name__ == "__main__":
    unittest.main()
