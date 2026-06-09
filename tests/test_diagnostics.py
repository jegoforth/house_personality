"""Tests for diagnostics redaction."""

from __future__ import annotations

import unittest

from tests.common import homeassistant_stubs


class DiagnosticsTests(unittest.TestCase):
    """Test diagnostics redaction behavior."""

    def test_redact_config_redacts_secrets_and_private_entity_ids(self) -> None:
        """Diagnostics should redact secrets and configured private entity IDs."""
        with homeassistant_stubs():
            from custom_components.house_personality.const import REDACTED
            from custom_components.house_personality.diagnostics import _redact_config

            redacted = _redact_config(
                {
                    "api_key": "secret",
                    "context_entity": "sensor.private_context",
                    "identity_entity": "sensor.private_identity",
                    "location_entity": "sensor.private_location",
                    "memory_entity": "sensor.private_memory",
                    "vision_entity": "sensor.private_vision",
                    "model": "gpt-4o-mini",
                    "tools_enabled": True,
                    "unknown_private_key": "private",
                }
            )

        self.assertEqual(redacted["api_key"], REDACTED)
        self.assertEqual(redacted["context_entity"], REDACTED)
        self.assertEqual(redacted["identity_entity"], REDACTED)
        self.assertEqual(redacted["location_entity"], REDACTED)
        self.assertEqual(redacted["memory_entity"], REDACTED)
        self.assertEqual(redacted["vision_entity"], REDACTED)
        self.assertEqual(redacted["unknown_private_key"], REDACTED)
        self.assertEqual(redacted["model"], "gpt-4o-mini")
        self.assertTrue(redacted["tools_enabled"])


if __name__ == "__main__":
    unittest.main()
