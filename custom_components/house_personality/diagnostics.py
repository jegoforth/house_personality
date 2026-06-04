"""Diagnostics for House Personality."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .const import CONFIG_KEYS, DOMAIN, REDACTED


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = _redact_config(dict(config_entry.data))
    options = _redact_config(dict(config_entry.options))

    return {
        "domain": DOMAIN,
        "entry": {
            "title": config_entry.title,
            "data": data,
            "options": options,
        },
    }


def _redact_config(values: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive config values."""
    redacted: dict[str, Any] = {}
    for key, value in values.items():
        if key == CONF_API_KEY:
            redacted[key] = REDACTED if value else ""
        elif key in CONFIG_KEYS:
            redacted[key] = value
        else:
            redacted[key] = REDACTED
    return redacted

