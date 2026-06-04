"""Conversation agent for House Personality."""

from __future__ import annotations

import logging
import time
from typing import Any, Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_MODEL, CONF_TIMEOUT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import (
    CONF_ASSISTANT_NAME,
    CONF_BASE_URL,
    CONF_CONTEXT_ENTITY,
    CONF_DEBUG_LOGGING,
    CONF_IDENTITY_ENTITY,
    CONF_PERSONALITY_PROMPT,
    CONF_TEMPERATURE,
    DEFAULT_ASSISTANT_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_CONTEXT_MAX_CHARS,
    DEFAULT_IDENTITY_MAX_CHARS,
    DEFAULT_MODEL,
    DEFAULT_PERSONALITY_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    FRIENDLY_PROVIDER_ERROR,
)
from .context.entity_context import async_get_entity_context
from .context.prompt_builder import (
    PromptContext,
    build_chat_messages,
    describe_prompt_sections,
)
from .identity import async_get_entity_identity
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
    _attr_supported_languages = "*"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the conversation agent."""
        self._hass = hass
        self._entry = entry
        self._attr_unique_id = entry.entry_id

    @property
    def name(self) -> str:
        """Return the configured assistant display name."""
        return _entry_value(self._entry, CONF_ASSISTANT_NAME, DEFAULT_ASSISTANT_NAME)

    @property
    def supported_languages(self) -> Literal["*"]:
        """Return the supported conversation languages."""
        return "*"

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """Handle a conversation message with the current chat log API."""
        return await self._async_process_message(user_input, chat_log)

    async def async_process(
        self,
        user_input: conversation.ConversationInput,
    ) -> conversation.ConversationResult:
        """Process a conversation request on older Home Assistant versions."""
        return await self._async_process_message(user_input)

    async def _async_process_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog | None = None,
    ) -> conversation.ConversationResult:
        """Process a conversation request."""
        values = _entry_values(self._entry)
        debug_logging = bool(values.get(CONF_DEBUG_LOGGING, False))
        user_message = user_input.text or ""
        context_result = await async_get_entity_context(
            self._hass,
            values.get(CONF_CONTEXT_ENTITY),
            max_chars=DEFAULT_CONTEXT_MAX_CHARS,
        )
        identity_result = await async_get_entity_identity(
            self._hass,
            values.get(CONF_IDENTITY_ENTITY),
            max_chars=DEFAULT_IDENTITY_MAX_CHARS,
        )

        prompt_context = PromptContext(
            personality_prompt=values.get(
                CONF_PERSONALITY_PROMPT,
                DEFAULT_PERSONALITY_PROMPT,
            ),
            user_message=user_message,
            household_context=context_result.content,
            speaker_identity=identity_result.speaker,
        )
        messages = build_chat_messages(prompt_context)

        if debug_logging:
            _LOGGER.debug(
                "Built House Personality prompt sections: %s",
                describe_prompt_sections(prompt_context),
            )
            _LOGGER.debug(
                "House Personality context entity status: entity=%s included=%s reason=%s",
                values.get(CONF_CONTEXT_ENTITY) or None,
                context_result.included,
                context_result.reason,
            )
            _LOGGER.debug(
                "House Personality identity entity status: entity=%s included=%s reason=%s",
                values.get(CONF_IDENTITY_ENTITY) or None,
                identity_result.included,
                identity_result.reason,
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
        provider_succeeded = False
        try:
            provider_response = await provider.async_generate_response(messages)
            speech = provider_response.content
            provider_succeeded = True
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

        if provider_succeeded:
            _add_assistant_response_to_chat_log(chat_log, user_input, speech)

        response = intent.IntentResponse(language=user_input.language)
        response.async_set_speech(speech)
        return conversation.ConversationResult(
            response=response,
            conversation_id=(
                chat_log.conversation_id if chat_log else user_input.conversation_id
            ),
            continue_conversation=(
                chat_log.continue_conversation
                if chat_log
                else getattr(user_input, "continue_conversation", False)
            ),
        )


def _entry_values(entry: ConfigEntry) -> dict[str, Any]:
    """Return merged config entry data and options."""
    values = dict(entry.data)
    values.update(entry.options)
    return values


def _entry_value(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Return a merged config value."""
    return _entry_values(entry).get(key, default)


def _add_assistant_response_to_chat_log(
    chat_log: conversation.ChatLog | None,
    user_input: conversation.ConversationInput,
    speech: str,
) -> None:
    """Add assistant content to the chat log when the current API is available."""
    if chat_log is None:
        return

    add_content = getattr(chat_log, "async_add_assistant_content_without_tools", None)
    assistant_content = getattr(conversation, "AssistantContent", None)
    if add_content is None or assistant_content is None:
        return

    agent_id = getattr(user_input, "agent_id", None)
    if agent_id is None:
        return

    add_content(
        assistant_content(
            agent_id=agent_id,
            content=speech,
        )
    )
