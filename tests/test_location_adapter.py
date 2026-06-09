"""Tests for generic location context adapter."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
import unittest

from tests.common import homeassistant_stubs


class _States:
    """Minimal Home Assistant state machine stub."""

    def __init__(self, state) -> None:
        self._state = state

    def get(self, entity_id: str):
        """Return a configured state by entity id."""
        if self._state is not None and self._state.entity_id == entity_id:
            return self._state
        return None


class LocationAdapterTests(unittest.IsolatedAsyncioTestCase):
    """Test location adapter behavior."""

    async def test_location_context_formats_safe_contract_fields(self) -> None:
        """Location context should include room fields and omit raw GPS fields."""
        with homeassistant_stubs():
            from custom_components.house_personality.location.entity_location import (
                async_get_entity_location,
            )

            state = SimpleNamespace(
                entity_id="sensor.person_a_location_context",
                state="Kitchen",
                attributes={
                    "person_label": "Person A",
                    "home_state": "home",
                    "room": "Kitchen",
                    "area": "Kitchen",
                    "confidence": 0.78,
                    "updated_at": datetime.now(UTC).isoformat(),
                    "stale_after_seconds": 300,
                    "latitude": 10.0,
                    "longitude": 20.0,
                    "gps_accuracy": 12,
                },
            )
            hass = SimpleNamespace(states=_States(state))

            result = await async_get_entity_location(
                hass,
                "sensor.person_a_location_context",
                max_chars=1200,
            )

        self.assertTrue(result.included)
        self.assertEqual(result.reason, "included")
        self.assertIn("Person: Person A", result.content)
        self.assertIn("Home state: home", result.content)
        self.assertIn("Room: Kitchen", result.content)
        self.assertNotIn("latitude", result.content)
        self.assertNotIn("longitude", result.content)
        self.assertNotIn("gps_accuracy", result.content)

    async def test_location_context_skips_stale_entity(self) -> None:
        """Stale location context should not be included."""
        with homeassistant_stubs():
            from custom_components.house_personality.location.entity_location import (
                async_get_entity_location,
            )

            state = SimpleNamespace(
                entity_id="sensor.person_a_location_context",
                state="Kitchen",
                attributes={
                    "updated_at": (datetime.now(UTC) - timedelta(minutes=10)).isoformat(),
                    "stale_after_seconds": 60,
                },
            )
            hass = SimpleNamespace(states=_States(state))

            result = await async_get_entity_location(
                hass,
                "sensor.person_a_location_context",
                max_chars=1200,
            )

        self.assertFalse(result.included)
        self.assertEqual(result.reason, "stale")
        self.assertIsNone(result.content)

    async def test_location_context_skips_unknown_state(self) -> None:
        """Unknown location state should not be included."""
        with homeassistant_stubs():
            from custom_components.house_personality.location.entity_location import (
                async_get_entity_location,
            )

            state = SimpleNamespace(
                entity_id="sensor.person_a_location_context",
                state="unknown",
                attributes={},
            )
            hass = SimpleNamespace(states=_States(state))

            result = await async_get_entity_location(
                hass,
                "sensor.person_a_location_context",
                max_chars=1200,
            )

        self.assertFalse(result.included)
        self.assertEqual(result.reason, "unknown")


if __name__ == "__main__":
    unittest.main()
