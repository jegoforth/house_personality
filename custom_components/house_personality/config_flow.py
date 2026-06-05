"""Config flow for House Personality."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_MODEL, CONF_TIMEOUT
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    NumberSelector,
    NumberSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_ASSISTANT_NAME,
    CONF_BASE_URL,
    CONF_CONTEXT_ENTITY,
    CONF_DEBUG_LOGGING,
    CONF_IDENTITY_ENTITY,
    CONF_MEMORY_ENTITY,
    CONF_PERSONALITY_PROMPT,
    CONF_RECALL_ENABLED,
    CONF_RECALL_INCLUDE_TURNS,
    CONF_RECALL_LIMIT,
    CONF_RECALL_SERVICE_DOMAIN,
    CONF_RECALL_SERVICE_NAME,
    CONF_TEMPERATURE,
    CONF_VISION_ENABLED,
    CONF_VISION_ENTITY,
    DEFAULT_ASSISTANT_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_PERSONALITY_PROMPT,
    DEFAULT_RECALL_LIMIT,
    DEFAULT_RECALL_SERVICE_DOMAIN,
    DEFAULT_RECALL_SERVICE_NAME,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    DOMAIN,
)


class HousePersonalityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for House Personality."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_user_input(user_input)
            if errors:
                return self.async_show_form(
                    step_id="user",
                    data_schema=_config_schema(user_input),
                    errors=errors,
                )

            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_ASSISTANT_NAME],
                data=_normalize_user_input(user_input),
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_config_schema(),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return HousePersonalityOptionsFlow(config_entry)


class HousePersonalityOptionsFlow(config_entries.OptionsFlow):
    """Handle options for House Personality."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.FlowResult:
        """Manage options."""
        if user_input is not None:
            errors = _validate_user_input(user_input)
            if errors:
                return self.async_show_form(
                    step_id="init",
                    data_schema=_config_schema(user_input),
                    errors=errors,
                )

            return self.async_create_entry(
                title=user_input[CONF_ASSISTANT_NAME],
                data=_normalize_user_input(user_input),
            )

        values = _entry_values(self._config_entry)
        return self.async_show_form(
            step_id="init",
            data_schema=_config_schema(values),
        )


def _entry_values(config_entry: config_entries.ConfigEntry) -> dict[str, Any]:
    """Return merged config entry data and options."""
    values = dict(config_entry.data)
    values.update(config_entry.options)
    return values


def _config_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build the config/options schema."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_ASSISTANT_NAME,
                default=defaults.get(CONF_ASSISTANT_NAME, DEFAULT_ASSISTANT_NAME),
            ): TextSelector(),
            vol.Required(
                CONF_BASE_URL,
                default=defaults.get(CONF_BASE_URL, DEFAULT_BASE_URL),
            ): TextSelector(),
            vol.Optional(
                CONF_API_KEY,
                default=defaults.get(CONF_API_KEY, ""),
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            vol.Required(
                CONF_MODEL,
                default=defaults.get(CONF_MODEL, DEFAULT_MODEL),
            ): TextSelector(),
            vol.Required(
                CONF_TEMPERATURE,
                default=defaults.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=0,
                    max=2,
                    step=0.1,
                )
            ),
            vol.Required(
                CONF_TIMEOUT,
                default=defaults.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=1,
                    max=300,
                    step=1,
                )
            ),
            vol.Required(
                CONF_PERSONALITY_PROMPT,
                default=defaults.get(
                    CONF_PERSONALITY_PROMPT,
                    DEFAULT_PERSONALITY_PROMPT,
                ),
            ): TextSelector(TextSelectorConfig(multiline=True)),
            _optional_entity_key(defaults, CONF_CONTEXT_ENTITY): EntitySelector(),
            _optional_entity_key(defaults, CONF_IDENTITY_ENTITY): EntitySelector(),
            _optional_entity_key(defaults, CONF_MEMORY_ENTITY): EntitySelector(),
            vol.Required(
                CONF_RECALL_ENABLED,
                default=defaults.get(CONF_RECALL_ENABLED, False),
            ): BooleanSelector(),
            vol.Required(
                CONF_RECALL_SERVICE_DOMAIN,
                default=defaults.get(
                    CONF_RECALL_SERVICE_DOMAIN,
                    DEFAULT_RECALL_SERVICE_DOMAIN,
                ),
            ): TextSelector(),
            vol.Required(
                CONF_RECALL_SERVICE_NAME,
                default=defaults.get(
                    CONF_RECALL_SERVICE_NAME,
                    DEFAULT_RECALL_SERVICE_NAME,
                ),
            ): TextSelector(),
            vol.Required(
                CONF_RECALL_LIMIT,
                default=defaults.get(CONF_RECALL_LIMIT, DEFAULT_RECALL_LIMIT),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=1,
                    max=10,
                    step=1,
                )
            ),
            vol.Required(
                CONF_RECALL_INCLUDE_TURNS,
                default=defaults.get(CONF_RECALL_INCLUDE_TURNS, False),
            ): BooleanSelector(),
            vol.Required(
                CONF_VISION_ENABLED,
                default=defaults.get(CONF_VISION_ENABLED, False),
            ): BooleanSelector(),
            _optional_entity_key(defaults, CONF_VISION_ENTITY): EntitySelector(),
            vol.Required(
                CONF_DEBUG_LOGGING,
                default=defaults.get(CONF_DEBUG_LOGGING, False),
            ): BooleanSelector(),
        }
    )


def _normalize_user_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize config flow values."""
    return {
        CONF_ASSISTANT_NAME: user_input[CONF_ASSISTANT_NAME].strip(),
        CONF_BASE_URL: user_input[CONF_BASE_URL].strip(),
        CONF_API_KEY: user_input.get(CONF_API_KEY, "").strip(),
        CONF_MODEL: user_input[CONF_MODEL].strip(),
        CONF_TEMPERATURE: float(user_input[CONF_TEMPERATURE]),
        CONF_TIMEOUT: int(user_input[CONF_TIMEOUT]),
        CONF_PERSONALITY_PROMPT: user_input[CONF_PERSONALITY_PROMPT].strip(),
        CONF_CONTEXT_ENTITY: _clean_optional_text(user_input.get(CONF_CONTEXT_ENTITY)),
        CONF_IDENTITY_ENTITY: _clean_optional_text(user_input.get(CONF_IDENTITY_ENTITY)),
        CONF_MEMORY_ENTITY: _clean_optional_text(user_input.get(CONF_MEMORY_ENTITY)),
        CONF_RECALL_ENABLED: bool(user_input[CONF_RECALL_ENABLED]),
        CONF_RECALL_SERVICE_DOMAIN: user_input[CONF_RECALL_SERVICE_DOMAIN].strip(),
        CONF_RECALL_SERVICE_NAME: user_input[CONF_RECALL_SERVICE_NAME].strip(),
        CONF_RECALL_LIMIT: int(user_input[CONF_RECALL_LIMIT]),
        CONF_RECALL_INCLUDE_TURNS: bool(user_input[CONF_RECALL_INCLUDE_TURNS]),
        CONF_VISION_ENABLED: bool(user_input[CONF_VISION_ENABLED]),
        CONF_VISION_ENTITY: _clean_optional_text(user_input.get(CONF_VISION_ENTITY)),
        CONF_DEBUG_LOGGING: bool(user_input[CONF_DEBUG_LOGGING]),
    }


def _optional_entity_key(defaults: dict[str, Any], key: str) -> vol.Optional:
    """Return a schema key for an optional entity selector."""
    value = _clean_optional_text(defaults.get(key))
    if value:
        return vol.Optional(key, default=value)
    return vol.Optional(key)


def _validate_user_input(user_input: dict[str, Any]) -> dict[str, str]:
    """Validate config flow values."""
    errors: dict[str, str] = {}
    required_text_fields = (
        CONF_ASSISTANT_NAME,
        CONF_BASE_URL,
        CONF_MODEL,
        CONF_PERSONALITY_PROMPT,
        CONF_RECALL_SERVICE_DOMAIN,
        CONF_RECALL_SERVICE_NAME,
    )
    for field in required_text_fields:
        if not str(user_input.get(field, "")).strip():
            errors[field] = "required"

    return errors


def _clean_optional_text(value: Any) -> str:
    """Normalize optional text values."""
    if value is None:
        return ""
    return str(value).strip()
