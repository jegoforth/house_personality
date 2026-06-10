"""Tests for House Personality services."""

from __future__ import annotations

from types import SimpleNamespace
import unittest

from tests.common import homeassistant_stubs


class ServicesTests(unittest.TestCase):
    """Test service helper behavior."""

    def test_test_provider_messages_are_minimal_text_only(self) -> None:
        """Provider test service should build a small text-only prompt."""
        with homeassistant_stubs():
            from custom_components.house_personality.services import (
                _test_provider_messages,
            )

            messages = _test_provider_messages("Say ok")

        self.assertEqual([message["role"] for message in messages], ["system", "user"])
        self.assertEqual(messages[1]["content"], "Say ok")
        self.assertNotIn("tools", messages[0])

    def test_test_provider_result_includes_no_secret_values(self) -> None:
        """Provider test responses should include useful non-secret metadata."""
        with homeassistant_stubs():
            from custom_components.house_personality.services import (
                _test_provider_result,
            )

            result = _test_provider_result(
                {
                    "base_url": "https://example.invalid/v1",
                    "api_key": "secret",
                    "model": "test-model",
                },
                success=True,
                latency_ms=42,
                response="ok",
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["base_url"], "https://example.invalid/v1")
        self.assertEqual(result["model"], "test-model")
        self.assertEqual(result["latency_ms"], 42)
        self.assertEqual(result["response"], "ok")
        self.assertNotIn("api_key", result)

    def test_find_config_entry_returns_domain_entry(self) -> None:
        """Service helpers should find the stored config entry."""
        with homeassistant_stubs():
            from homeassistant.config_entries import ConfigEntry

            from custom_components.house_personality.const import DOMAIN
            from custom_components.house_personality.services import _find_config_entry

            entry = ConfigEntry()
            entry.data = {}
            entry.options = {}
            hass = SimpleNamespace(
                data={
                    DOMAIN: {
                        "proposal_store": object(),
                        "entry": entry,
                    }
                }
            )

            found = _find_config_entry(hass)

        self.assertIs(found, entry)


if __name__ == "__main__":
    unittest.main()
