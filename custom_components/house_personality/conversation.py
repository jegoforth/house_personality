"""Conversation agent for House Personality."""

from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_BASE_URL, CONF_MODEL, CONF_TIMEOUT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import (
    CONF_ASSISTANT_NAME,
    CONF_DEBUG_LOGGING,
    CONF_PERSONALITY_PROMPT,
    CONF_TEMPERATURE,
    DEFAULT_ASSISTANT_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_PERSONALITY_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    FRIENDLY_PROVIDER_ERROR,
)
from .context.prompt_builder import (
    PromptContext,
    build_chat_messages,
    describe_prompt_sections,
)
from .providers import OpenAICompatibleProvider, ProviderError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the conversation platform."""
    async_add_entities([HousePersonalityConversationAgent(hass, entry)])


class HousePersonalityConversationAgent(conversation.ConversationEntity):
    """House Personality conversation agent."""

    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the conversation agent."""
        self._hass = hass
        self._entry = entry
        self._attr_unique_id = entry.entry_id

    @property
    def name(self) -> str:
        """Return the configured assistant display name."""
        return _entry_value(self._entry, CONF_ASSISTANT_NAME, DEFAULT_ASSISTANT_NAME)

    async def async_process(
        self,
        user_input: conversation.ConversationInput,
    ) -> conversation.ConversationResult:
        """Process a conversation request."""
        values = _entry_values(self._entry)
        debug_logging = bool(values.get(CONF_DEBUG_LOGGING, False))
        user_message = user_input.text or ""

        prompt_context = PromptContext(
            personality_prompt=values.get(
                CONF_PERSONALITY_PROMPT,
                DEFAULT_PERSONALITY_PROMPT,
            ),
            user_message=user_message,
        )
        messages = build_chat_messages(prompt_context)

        if debug_logging:
            _LOGGER.debug(
                "Built House Personality prompt sections: %s",
                describe_prompt_sections(prompt_context),
            )

        provider = OpenAICompatibleProvider(
            self._hass,
            base_url=values.get(CONF_BASE_URL, DEFAULT_BASE_URL),
            api_key=values.get(CONF_API_KEY) or None,
            model=values.get(CONF_MODEL, DEFAULT_MODEL),
            temperature=float(values.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)),
            timeout=int(values.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)),
            debug_logging=debug_logging,
        )

        started = time.monotonic()
        try:
            provider_response = await provider.async_generate_response(messages)
            speech = provider_response.content
            if debug_logging:
                _LOGGER.debug(
                    "House Personality provider completed in %.2fs",
                    time.monotonic() - started,
                )
        except ProviderError as err:
            _LOGGER.warning("House Personality provider failed: %s", err)
            speech = FRIENDLY_PROVIDER_ERROR
        except Exception:
            _LOGGER.exception("Unexpected House Personality conversation failure")
            speech = FRIENDLY_PROVIDER_ERROR

        response = intent.IntentResponse(language=user_input.language)
        response.async_set_speech(speech)
        return conversation.ConversationResult(
            response=response,
            conversation_id=user_input.conversation_id,
        )


def _entry_values(entry: ConfigEntry) -> dict[str, Any]:
    """Return merged config entry data and options."""
    values = dict(entry.data)
    values.update(entry.options)
    return values


def _entry_value(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Return a merged config value."""
    return _entry_values(entry).get(key, default)

