"""Tests for entity-based speaker identity handling."""

from __future__ import annotations

from types import SimpleNamespace
import unittest

from tests.common import homeassistant_stubs


class _FakeStates:
    def __init__(self, states: dict[str, object]) -> None:
        self._states = states

    def get(self, entity_id: str) -> object | None:
        return self._states.get(entity_id)


class EntityIdentityTests(unittest.IsolatedAsyncioTestCase):
    """Test optional identity entity behavior."""

    async def test_plain_helper_identity_is_included(self) -> None:
        """Simple helper entities should continue to work without accepted attrs."""
        with homeassistant_stubs():
            from custom_components.house_personality.identity.entity_identity import (
                async_get_entity_identity,
            )

            hass = SimpleNamespace(
                states=_FakeStates(
                    {
                        "input_text.current_speaker": SimpleNamespace(
                            state="Guest",
                            attributes={},
                        )
                    }
                )
            )

            result = await async_get_entity_identity(
                hass,
                "input_text.current_speaker",
                max_chars=50,
            )

        self.assertTrue(result.included)
        self.assertEqual(result.speaker, "Guest")
        self.assertEqual(result.reason, "included")

    async def test_rejected_speaker_sensor_is_not_included(self) -> None:
        """Speaker-recognition style entities must be accepted before injection."""
        with homeassistant_stubs():
            from custom_components.house_personality.identity.entity_identity import (
                async_get_entity_identity,
            )

            hass = SimpleNamespace(
                states=_FakeStates(
                    {
                        "sensor.last_recognized_speaker": SimpleNamespace(
                            state="Person A",
                            attributes={
                                "accepted": False,
                                "rejection_reason": "low_score_gap",
                                "best_match": "Person A",
                                "second_match": "Person B",
                            },
                        )
                    }
                )
            )

            result = await async_get_entity_identity(
                hass,
                "sensor.last_recognized_speaker",
                max_chars=50,
            )

        self.assertFalse(result.included)
        self.assertIsNone(result.speaker)
        self.assertEqual(result.reason, "low_score_gap")

    async def test_accepted_speaker_sensor_is_included(self) -> None:
        """Accepted speaker-recognition entities should inject their state."""
        with homeassistant_stubs():
            from custom_components.house_personality.identity.entity_identity import (
                async_get_entity_identity,
            )

            hass = SimpleNamespace(
                states=_FakeStates(
                    {
                        "sensor.last_recognized_speaker": SimpleNamespace(
                            state="Person A",
                            attributes={"accepted": True},
                        )
                    }
                )
            )

            result = await async_get_entity_identity(
                hass,
                "sensor.last_recognized_speaker",
                max_chars=50,
            )

        self.assertTrue(result.included)
        self.assertEqual(result.speaker, "Person A")


if __name__ == "__main__":
    unittest.main()
