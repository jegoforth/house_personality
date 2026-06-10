"""Tests for generic public-space room status adapter."""

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


class RoomStatusAdapterTests(unittest.IsolatedAsyncioTestCase):
    """Test room status adapter behavior."""

    async def test_room_status_formats_prompt_safe_fields(self) -> None:
        """Room status should include summaries and omit raw camera details."""
        with homeassistant_stubs():
            from custom_components.house_personality.room_status.entity_room_status import (
                async_get_entity_room_status,
            )

            state = SimpleNamespace(
                entity_id="sensor.kitchen_room_status",
                state="Kitchen appears occupied.",
                attributes={
                    "summary": "Kitchen appears occupied.",
                    "room": "Kitchen",
                    "occupancy": "occupied",
                    "confidence": 0.81,
                    "public_space": True,
                    "updated_at": datetime.now(UTC).isoformat(),
                    "stale_after_seconds": 300,
                    "camera_entity": "camera.private",
                    "image_url": "https://example.invalid/snapshot.jpg",
                },
            )
            hass = SimpleNamespace(states=_States(state))

            result = await async_get_entity_room_status(
                hass,
                "sensor.kitchen_room_status",
                max_chars=1600,
            )

        self.assertTrue(result.included)
        self.assertEqual(result.reason, "included")
        self.assertIn("Summary: Kitchen appears occupied.", result.content)
        self.assertIn("Room: Kitchen", result.content)
        self.assertIn("Occupancy: occupied", result.content)
        self.assertNotIn("camera.private", result.content)
        self.assertNotIn("snapshot.jpg", result.content)

    async def test_room_status_skips_private_space(self) -> None:
        """Private-space room status should not be included."""
        with homeassistant_stubs():
            from custom_components.house_personality.room_status.entity_room_status import (
                async_get_entity_room_status,
            )

            state = SimpleNamespace(
                entity_id="sensor.private_room_status",
                state="Private room status available.",
                attributes={
                    "summary": "Private room status available.",
                    "public_space": False,
                },
            )
            hass = SimpleNamespace(states=_States(state))

            result = await async_get_entity_room_status(
                hass,
                "sensor.private_room_status",
                max_chars=1600,
            )

        self.assertFalse(result.included)
        self.assertEqual(result.reason, "private_space")

    async def test_room_status_skips_stale_entity(self) -> None:
        """Stale room status should not be included."""
        with homeassistant_stubs():
            from custom_components.house_personality.room_status.entity_room_status import (
                async_get_entity_room_status,
            )

            state = SimpleNamespace(
                entity_id="sensor.kitchen_room_status",
                state="Kitchen appears occupied.",
                attributes={
                    "updated_at": (datetime.now(UTC) - timedelta(minutes=10)).isoformat(),
                    "stale_after_seconds": 60,
                },
            )
            hass = SimpleNamespace(states=_States(state))

            result = await async_get_entity_room_status(
                hass,
                "sensor.kitchen_room_status",
                max_chars=1600,
            )

        self.assertFalse(result.included)
        self.assertEqual(result.reason, "stale")


if __name__ == "__main__":
    unittest.main()
