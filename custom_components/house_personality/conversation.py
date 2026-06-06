"""Conversation agent for House Personality."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_MODEL, CONF_TIMEOUT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent, llm
from voluptuous_openapi import convert

from .const import (
    CONF_ASSISTANT_NAME,
    CONF_BASE_URL,
    CONF_CONTEXT_ENTITY,
    CONF_DEBUG_LOGGING,
    CONF_IDENTITY_ENTITY,
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
    CONF_TEMPERATURE,
    CONF_TOOL_CHOICE,
    CONF_TOOLS_ENABLED,
    CONF_VISION_ENABLED,
    CONF_VISION_ENTITY,
    DEFAULT_ASSISTANT_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_CONTEXT_MAX_CHARS,
    DEFAULT_IDENTITY_MAX_CHARS,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MEMORY_MAX_CHARS,
    DEFAULT_MODEL,
    DEFAULT_PARALLEL_TOOL_CALLS,
    DEFAULT_PERSONALITY_PROMPT,
    DEFAULT_RECALL_LIMIT,
    DEFAULT_RECALL_MAX_CHARS,
    DEFAULT_RECALL_SERVICE_DOMAIN,
    DEFAULT_RECALL_SERVICE_NAME,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    DEFAULT_TOOL_CHOICE,
    DEFAULT_TOOLS_ENABLED,
    DEFAULT_VISION_MAX_CHARS,
    DOMAIN,
    FRIENDLY_PROVIDER_ERROR,
)
from .context.entity_context import async_get_entity_context
from .context.prompt_builder import (
    PromptContext,
    build_chat_messages,
    describe_prompt_sections,
)
from .identity import async_get_entity_identity
from .memory import async_get_entity_memory, async_get_recall_memory
from .providers import OpenAICompatibleProvider, ProviderError
from .vision import async_get_entity_vision_context

_LOGGER = logging.getLogger(__name__)

_MAX_TOOL_ITERATIONS = 10
_MUTATING_TOOL_SETTLE_DELAY = 1.0
_MUTATING_TOOL_NAMES = {
    "HassBroadcast",
    "HassCancelAllTimers",
    "HassCancelTimer",
    "HassClimateSetTemperature",
    "HassDecreaseTimer",
    "HassFanSetSpeed",
    "HassIncreaseTimer",
    "HassLightSet",
    "HassListAddItem",
    "HassListCompleteItem",
    "HassListRemoveItem",
    "HassMediaNext",
    "HassMediaPause",
    "HassMediaPlayerMute",
    "HassMediaPlayerUnmute",
    "HassMediaPrevious",
    "HassMediaSearchAndPlay",
    "HassMediaUnpause",
    "HassPauseTimer",
    "HassSetPosition",
    "HassSetVolume",
    "HassSetVolumeRelative",
    "HassShoppingListAddItem",
    "HassShoppingListCompleteItem",
    "HassStartTimer",
    "HassTimerStatus",
    "HassTurnOff",
    "HassTurnOn",
    "HassUnpauseTimer",
    "HassVacuumCleanArea",
    "HassVacuumReturnToBase",
    "HassVacuumStart",
}
_OPENAI_UNSUPPORTED_TOP_LEVEL_SCHEMA_KEYS = {
    "allOf",
    "anyOf",
    "enum",
    "not",
    "oneOf",
}
_HOME_ASSISTANT_TOOL_INSTRUCTIONS = """
Home Assistant tool use rules:
- For requests to turn on, turn off, toggle, set, change, open, close,
  lock, unlock, start, stop, or otherwise control home devices, call the
  available Home Assistant tools.
- For requests to verify, check, confirm, or report the current state of home
  devices, call the available Home Assistant tools.
- When a user asks to control a device and verify the result, call the control
  tool first, wait for its result, then call the state/check tool in a later
  step.
- Do not say a Home Assistant action was performed unless a tool call was made
  and the tool result supports that claim.
- Do not say a current state was verified unless a tool call returned current
  state information.
- If a needed tool is unavailable or fails, say that clearly instead of claiming success.
""".strip()


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
    _attr_supported_features = conversation.ConversationEntityFeature.CONTROL
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
        memory_result = await async_get_entity_memory(
            self._hass,
            values.get(CONF_MEMORY_ENTITY),
            max_chars=DEFAULT_MEMORY_MAX_CHARS,
        )
        recall_result = await async_get_recall_memory(
            self._hass,
            enabled=bool(values.get(CONF_RECALL_ENABLED, False)),
            service_domain=values.get(
                CONF_RECALL_SERVICE_DOMAIN,
                DEFAULT_RECALL_SERVICE_DOMAIN,
            ),
            service_name=values.get(
                CONF_RECALL_SERVICE_NAME,
                DEFAULT_RECALL_SERVICE_NAME,
            ),
            query=user_message,
            speaker_id=identity_result.speaker,
            conversation_id=user_input.conversation_id,
            limit=int(values.get(CONF_RECALL_LIMIT, DEFAULT_RECALL_LIMIT)),
            include_turns=bool(values.get(CONF_RECALL_INCLUDE_TURNS, False)),
            max_chars=DEFAULT_RECALL_MAX_CHARS,
        )
        memory_context = _combine_memory_contexts(
            entity_memory=memory_result.content,
            recall_memory=recall_result.content,
        )
        vision_result = await async_get_entity_vision_context(
            self._hass,
            enabled=bool(values.get(CONF_VISION_ENABLED, False)),
            entity_id=values.get(CONF_VISION_ENTITY),
            max_chars=DEFAULT_VISION_MAX_CHARS,
        )

        prompt_context = PromptContext(
            personality_prompt=values.get(
                CONF_PERSONALITY_PROMPT,
                DEFAULT_PERSONALITY_PROMPT,
            ),
            user_message=user_message,
            household_context=context_result.content,
            speaker_identity=identity_result.speaker,
            memory_context=memory_context,
            vision_context=vision_result.content,
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
            _LOGGER.debug(
                "House Personality memory entity status: entity=%s included=%s reason=%s",
                values.get(CONF_MEMORY_ENTITY) or None,
                memory_result.included,
                memory_result.reason,
            )
            _LOGGER.debug(
                "House Personality recall status: enabled=%s service=%s.%s included=%s reason=%s",
                bool(values.get(CONF_RECALL_ENABLED, False)),
                values.get(CONF_RECALL_SERVICE_DOMAIN, DEFAULT_RECALL_SERVICE_DOMAIN),
                values.get(CONF_RECALL_SERVICE_NAME, DEFAULT_RECALL_SERVICE_NAME),
                recall_result.included,
                recall_result.reason,
            )
            _LOGGER.debug(
                "House Personality vision/event entity status: enabled=%s entity=%s included=%s reason=%s",
                bool(values.get(CONF_VISION_ENABLED, False)),
                values.get(CONF_VISION_ENTITY) or None,
                vision_result.included,
                vision_result.reason,
            )

        provider = OpenAICompatibleProvider(
            self._hass,
            base_url=values.get(CONF_BASE_URL, DEFAULT_BASE_URL),
            api_key=values.get(CONF_API_KEY) or None,
            model=values.get(CONF_MODEL, DEFAULT_MODEL),
            temperature=float(values.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)),
            max_tokens=int(values.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)),
            timeout=int(values.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)),
            tool_choice=values.get(CONF_TOOL_CHOICE, DEFAULT_TOOL_CHOICE),
            parallel_tool_calls=bool(
                values.get(CONF_PARALLEL_TOOL_CALLS, DEFAULT_PARALLEL_TOOL_CALLS)
            ),
            response_format=values.get(CONF_RESPONSE_FORMAT, DEFAULT_RESPONSE_FORMAT),
            debug_logging=debug_logging,
        )

        started = time.monotonic()
        try:
            if chat_log is not None:
                speech = await self._async_generate_chat_log_response(
                    user_input=user_input,
                    chat_log=chat_log,
                    provider=provider,
                    prompt_context=prompt_context,
                    tools_enabled=bool(
                        values.get(CONF_TOOLS_ENABLED, DEFAULT_TOOLS_ENABLED)
                    ),
                    debug_logging=debug_logging,
                )
            else:
                provider_response = await provider.async_generate_response(messages)
                speech = provider_response.content
            if debug_logging:
                _LOGGER.debug(
                    "House Personality provider completed in %.2fs",
                    time.monotonic() - started,
                )
        except conversation.ConverseError as err:
            return err.as_conversation_result()
        except ProviderError as err:
            _LOGGER.warning("House Personality provider failed: %s", err)
            speech = FRIENDLY_PROVIDER_ERROR
        except Exception:
            _LOGGER.exception("Unexpected House Personality conversation failure")
            speech = FRIENDLY_PROVIDER_ERROR

        if (
            chat_log is not None
            and getattr(chat_log.content[-1], "role", None) != "assistant"
        ):
            _add_assistant_response_to_chat_log(chat_log, user_input, speech)
        elif chat_log is None and speech != FRIENDLY_PROVIDER_ERROR:
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

    async def _async_generate_chat_log_response(
        self,
        *,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
        provider: OpenAICompatibleProvider,
        prompt_context: PromptContext,
        tools_enabled: bool,
        debug_logging: bool,
    ) -> str:
        """Generate a provider response using the current ChatLog tool API."""
        try:
            await chat_log.async_provide_llm_data(
                user_input.as_llm_context(DOMAIN),
                llm.LLM_API_ASSIST,
                _system_prompt_from_prompt_context(
                    prompt_context,
                    include_tool_instructions=tools_enabled,
                ),
                user_input.extra_system_prompt,
            )
        except conversation.ConverseError:
            raise
        except Exception as err:
            raise ProviderError("Error preparing Home Assistant Assist tools") from err

        tools = _format_openai_tools(chat_log) if tools_enabled else []
        if debug_logging:
            _LOGGER.debug(
                "House Personality Assist LLM API status: enabled=%s "
                "provider_tools_enabled=%s tools=%s tool_names=%s",
                bool(chat_log.llm_api),
                tools_enabled,
                len(tools),
                _tool_names(tools),
            )

        for iteration in range(_MAX_TOOL_ITERATIONS):
            response = await provider.async_generate_chat_completion(
                _chat_log_to_openai_messages(chat_log),
                tools=tools,
            )

            if response.tool_calls:
                if debug_logging:
                    _LOGGER.debug(
                        "House Personality provider requested %s tool call(s) "
                        "on iteration %s: %s",
                        len(response.tool_calls),
                        iteration + 1,
                        [tool_call.name for tool_call in response.tool_calls],
                    )
                tool_results = 0
                async for _tool_result in chat_log.async_add_assistant_content(
                    conversation.AssistantContent(
                        agent_id=user_input.agent_id,
                        content=response.content,
                        tool_calls=[
                            llm.ToolInput(
                                id=tool_call.tool_call_id,
                                tool_name=tool_call.name,
                                tool_args=tool_call.arguments,
                            )
                            for tool_call in response.tool_calls
                        ],
                    )
                ):
                    tool_results += 1
                if debug_logging:
                    _LOGGER.debug(
                        "House Personality executed %s Home Assistant tool result(s)",
                        tool_results,
                    )
                if _has_mutating_tool_call(response.tool_calls):
                    if debug_logging:
                        _LOGGER.debug(
                            "House Personality waiting %.1fs for Home Assistant "
                            "state to settle after mutating tool call",
                            _MUTATING_TOOL_SETTLE_DELAY,
                        )
                    await asyncio.sleep(_MUTATING_TOOL_SETTLE_DELAY)
                continue

            if response.content:
                if debug_logging:
                    _LOGGER.debug(
                        "House Personality provider returned final text without "
                        "tool calls on iteration %s",
                        iteration + 1,
                    )
                _add_assistant_response_to_chat_log(
                    chat_log,
                    user_input,
                    response.content,
                )
                return response.content

            raise ProviderError("Provider returned an empty response")

        raise ProviderError("Provider did not finish tool use")


def _entry_values(entry: ConfigEntry) -> dict[str, Any]:
    """Return merged config entry data and options."""
    values = dict(entry.data)
    values.update(entry.options)
    return values


def _entry_value(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Return a merged config value."""
    return _entry_values(entry).get(key, default)


def _combine_memory_contexts(
    *,
    entity_memory: str | None,
    recall_memory: str | None,
) -> str | None:
    """Combine optional memory sources for the prompt."""
    sections: list[str] = []
    if entity_memory:
        sections.append(f"Configured memory entity:\n{entity_memory}")
    if recall_memory:
        sections.append(f"Voice Assist Recall:\n{recall_memory}")

    if not sections:
        return None
    return "\n\n".join(sections)


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


def _system_prompt_from_prompt_context(
    context: PromptContext,
    *,
    include_tool_instructions: bool,
) -> str:
    """Build the system prompt without duplicating the user message."""
    system_parts = [
        message["content"]
        for message in build_chat_messages(context)
        if message["role"] == "system"
    ]
    if include_tool_instructions:
        system_parts.append(_HOME_ASSISTANT_TOOL_INSTRUCTIONS)
    return "\n\n".join(system_parts)


def _format_openai_tools(chat_log: conversation.ChatLog) -> list[dict[str, Any]]:
    """Format Home Assistant LLM tools for OpenAI-compatible providers."""
    if not chat_log.llm_api:
        return []

    tools: list[dict[str, Any]] = []
    skipped_tools: list[str] = []

    for tool in chat_log.llm_api.tools:
        parameters = convert(
            tool.parameters,
            custom_serializer=chat_log.llm_api.custom_serializer,
        )
        if not _is_openai_tool_schema_supported(parameters):
            skipped_tools.append(tool.name)
            continue

        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": parameters,
                },
            }
        )

    if skipped_tools:
        _LOGGER.debug(
            "Skipped Home Assistant tools with OpenAI-incompatible schemas: %s",
            skipped_tools,
        )

    return tools


def _is_openai_tool_schema_supported(parameters: Any) -> bool:
    """Return whether a tool schema is accepted by OpenAI-style functions."""
    if not isinstance(parameters, dict):
        return False
    if parameters.get("type") != "object":
        return False
    return not any(
        key in parameters for key in _OPENAI_UNSUPPORTED_TOP_LEVEL_SCHEMA_KEYS
    )


def _tool_names(tools: list[dict[str, Any]]) -> list[str]:
    """Return non-sensitive OpenAI tool names for debug logging."""
    names: list[str] = []
    for tool in tools:
        function = tool.get("function")
        if isinstance(function, dict) and isinstance(function.get("name"), str):
            names.append(function["name"])
    return names


def _has_mutating_tool_call(tool_calls: list[Any]) -> bool:
    """Return whether a tool-call batch likely changed Home Assistant state."""
    return any(tool_call.name in _MUTATING_TOOL_NAMES for tool_call in tool_calls)


def _chat_log_to_openai_messages(
    chat_log: conversation.ChatLog,
) -> list[dict[str, Any]]:
    """Convert Home Assistant chat log content to chat completion messages."""
    messages: list[dict[str, Any]] = []
    for content in chat_log.content:
        role = getattr(content, "role", None)
        if role == "system":
            messages.append({"role": "system", "content": content.content})
        elif role == "user":
            messages.append({"role": "user", "content": content.content})
        elif role == "assistant":
            messages.append(_assistant_content_to_openai_message(content))
        elif role == "tool_result":
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": content.tool_call_id,
                    "content": _json_content(content.tool_result),
                }
            )
    return messages


def _assistant_content_to_openai_message(content: Any) -> dict[str, Any]:
    """Convert assistant chat log content to an OpenAI-compatible message."""
    message: dict[str, Any] = {
        "role": "assistant",
        "content": content.content,
    }

    if content.tool_calls:
        message["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.tool_name,
                    "arguments": json.dumps(tool_call.tool_args),
                },
            }
            for tool_call in content.tool_calls
        ]

    return message


def _json_content(value: Any) -> str:
    """Return a JSON string for tool result content."""
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str)
