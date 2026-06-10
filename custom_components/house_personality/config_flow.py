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
    SelectSelector,
    SelectSelectorConfig,
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
    CONF_LOCATION_ENTITY,
    CONF_MAX_TOKENS,
    CONF_MEMORY_ENTITY,
    CONF_PARALLEL_TOOL_CALLS,
    CONF_PERSONALITY_PROMPT,
    CONF_RECALL_ENABLED,
    CONF_RECALL_INCLUDE_TURNS,
    CONF_RECALL_LIMIT,
    CONF_RECALL_SERVICE_DOMAIN,
    CONF_RECALL_SERVICE_NAME,
    CONF_RESPONSE_FORMAT,
    CONF_ROOM_STATUS_ENTITY,
    CONF_TEMPERATURE,
    CONF_TOOL_CHOICE,
    CONF_TOOLS_ENABLED,
    CONF_VISION_ENABLED,
    CONF_VISION_ENTITY,
    DEFAULT_ASSISTANT_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_PARALLEL_TOOL_CALLS,
    DEFAULT_PERSONALITY_PROMPT,
    DEFAULT_RECALL_LIMIT,
    DEFAULT_RECALL_SERVICE_DOMAIN,
    DEFAULT_RECALL_SERVICE_NAME,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    DEFAULT_TOOL_CHOICE,
    DEFAULT_TOOLS_ENABLED,
    DOMAIN,
)

_TOOL_CHOICE_OPTIONS = ("auto", "required", "none")
_RESPONSE_FORMAT_OPTIONS = ("default", "text", "json_object")


class HousePersonalityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for House Personality."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        return await self.async_step_house_personality_setup(user_input)

    async def async_step_house_personality_setup(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.FlowResult:
        """Handle House Personality setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_user_input(user_input)
            if errors:
                return self.async_show_form(
                    step_id="house_personality_setup",
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
            step_id="house_personality_setup",
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
        return await self.async_step_house_personality_options(user_input)

    async def async_step_house_personality_options(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.FlowResult:
        """Manage House Personality options."""
        if user_input is not None:
            errors = _validate_user_input(user_input)
            if errors:
                return self.async_show_form(
                    step_id="house_personality_options",
                    data_schema=_config_schema(user_input, expose_api_key=True),
                    errors=errors,
                )

            values = _entry_values(self._config_entry)
            options, api_key = _normalize_options_input(user_input, values)
            if api_key != self._config_entry.data.get(CONF_API_KEY, ""):
                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    data={
                        **self._config_entry.data,
                        CONF_API_KEY: api_key,
                    },
                )

            return self.async_create_entry(
                title=user_input[CONF_ASSISTANT_NAME],
                data=options,
            )

        values = _entry_values(self._config_entry)
        return self.async_show_form(
            step_id="house_personality_options",
            data_schema=_config_schema(values, expose_api_key=False),
        )


def _entry_values(config_entry: config_entries.ConfigEntry) -> dict[str, Any]:
    """Return merged config entry data and options."""
    values = dict(config_entry.data)
    values.update(config_entry.options)
    return values


def _config_schema(
    defaults: dict[str, Any] | None = None,
    *,
    expose_api_key: bool = True,
) -> vol.Schema:
    """Build the config/options schema."""
    defaults = defaults or {}
    api_key_default = defaults.get(CONF_API_KEY, "") if expose_api_key else ""
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
                default=api_key_default,
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
                CONF_MAX_TOKENS,
                default=defaults.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=0,
                    max=32000,
                    step=1,
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
            vol.Required(
                CONF_TOOLS_ENABLED,
                default=defaults.get(CONF_TOOLS_ENABLED, DEFAULT_TOOLS_ENABLED),
            ): BooleanSelector(),
            vol.Required(
                CONF_TOOL_CHOICE,
                default=defaults.get(CONF_TOOL_CHOICE, DEFAULT_TOOL_CHOICE),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=list(_TOOL_CHOICE_OPTIONS),
                )
            ),
            vol.Required(
                CONF_PARALLEL_TOOL_CALLS,
                default=defaults.get(
                    CONF_PARALLEL_TOOL_CALLS,
                    DEFAULT_PARALLEL_TOOL_CALLS,
                ),
            ): BooleanSelector(),
            vol.Required(
                CONF_RESPONSE_FORMAT,
                default=defaults.get(CONF_RESPONSE_FORMAT, DEFAULT_RESPONSE_FORMAT),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=list(_RESPONSE_FORMAT_OPTIONS),
                )
            ),
            _optional_entity_key(defaults, CONF_CONTEXT_ENTITY): EntitySelector(),
            _optional_entity_key(defaults, CONF_IDENTITY_ENTITY): EntitySelector(),
            _optional_entity_key(defaults, CONF_LOCATION_ENTITY): EntitySelector(),
            _optional_entity_key(defaults, CONF_ROOM_STATUS_ENTITY): EntitySelector(),
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
        CONF_MAX_TOKENS: int(user_input[CONF_MAX_TOKENS]),
        CONF_TIMEOUT: int(user_input[CONF_TIMEOUT]),
        CONF_PERSONALITY_PROMPT: user_input[CONF_PERSONALITY_PROMPT].strip(),
        CONF_TOOLS_ENABLED: bool(user_input[CONF_TOOLS_ENABLED]),
        CONF_TOOL_CHOICE: user_input[CONF_TOOL_CHOICE],
        CONF_PARALLEL_TOOL_CALLS: bool(user_input[CONF_PARALLEL_TOOL_CALLS]),
        CONF_RESPONSE_FORMAT: user_input[CONF_RESPONSE_FORMAT],
        CONF_CONTEXT_ENTITY: _clean_optional_text(user_input.get(CONF_CONTEXT_ENTITY)),
        CONF_IDENTITY_ENTITY: _clean_optional_text(user_input.get(CONF_IDENTITY_ENTITY)),
        CONF_LOCATION_ENTITY: _clean_optional_text(user_input.get(CONF_LOCATION_ENTITY)),
        CONF_ROOM_STATUS_ENTITY: _clean_optional_text(
            user_input.get(CONF_ROOM_STATUS_ENTITY)
        ),
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


def _normalize_options_input(
    user_input: dict[str, Any],
    existing_values: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    """Normalize options while preserving the existing API key when blank."""
    values = _normalize_user_input(user_input)
    if not values[CONF_API_KEY]:
        values[CONF_API_KEY] = _clean_optional_text(existing_values.get(CONF_API_KEY))
    api_key = values.pop(CONF_API_KEY)
    return values, api_key


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

    if user_input.get(CONF_TOOL_CHOICE) not in _TOOL_CHOICE_OPTIONS:
        errors[CONF_TOOL_CHOICE] = "invalid_option"
    if user_input.get(CONF_RESPONSE_FORMAT) not in _RESPONSE_FORMAT_OPTIONS:
        errors[CONF_RESPONSE_FORMAT] = "invalid_option"

    return errors


def _clean_optional_text(value: Any) -> str:
    """Normalize optional text values."""
    if value is None:
        return ""
    return str(value).strip()
