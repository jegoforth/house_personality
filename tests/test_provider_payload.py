"""Tests for OpenAI-compatible provider payload helpers."""

from __future__ import annotations

import unittest

from tests.common import homeassistant_stubs


class ProviderPayloadTests(unittest.TestCase):
    """Test OpenAI-compatible payload construction."""

    def test_payload_includes_provider_options_when_set(self) -> None:
        """Configured provider options should be passed through to the payload."""
        with homeassistant_stubs():
            from custom_components.house_personality.providers.openai_compatible import (
                _build_chat_completion_payload,
            )

            payload = _build_chat_completion_payload(
                model="test-model",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.2,
                max_tokens=64,
                tools=[{"type": "function", "function": {"name": "HassTurnOn"}}],
                tool_choice="required",
                parallel_tool_calls=True,
                response_format="json_object",
            )

        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(payload["temperature"], 0.2)
        self.assertEqual(payload["max_tokens"], 64)
        self.assertEqual(payload["tool_choice"], "required")
        self.assertTrue(payload["parallel_tool_calls"])
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(payload["tools"][0]["function"]["name"], "HassTurnOn")

    def test_payload_omits_optional_provider_defaults(self) -> None:
        """Default provider options should be omitted for broad compatibility."""
        with homeassistant_stubs():
            from custom_components.house_personality.providers.openai_compatible import (
                _build_chat_completion_payload,
            )

            payload = _build_chat_completion_payload(
                model="test-model",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=0,
                tools=[],
                tool_choice="auto",
                parallel_tool_calls=False,
                response_format="default",
            )

        self.assertNotIn("max_tokens", payload)
        self.assertNotIn("response_format", payload)
        self.assertNotIn("tools", payload)
        self.assertNotIn("tool_choice", payload)
        self.assertNotIn("parallel_tool_calls", payload)


if __name__ == "__main__":
    unittest.main()
