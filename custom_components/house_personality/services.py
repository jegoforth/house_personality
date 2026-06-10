"""Services for House Personality."""

from __future__ import annotations

import time
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_MODEL, CONF_TIMEOUT
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
import homeassistant.helpers.config_validation as cv

from .const import (
    ATTR_CONTENT,
    ATTR_ERROR,
    ATTR_LATENCY_MS,
    ATTR_MESSAGE,
    ATTR_METADATA,
    ATTR_PROPOSAL,
    ATTR_PROPOSAL_ID,
    ATTR_PROPOSALS,
    ATTR_REASON,
    ATTR_RESPONSE,
    ATTR_SOURCE,
    ATTR_SUCCESS,
    ATTR_TITLE,
    CONF_BASE_URL,
    CONF_MAX_TOKENS,
    CONF_PARALLEL_TOOL_CALLS,
    CONF_RESPONSE_FORMAT,
    CONF_TEMPERATURE,
    CONF_TOOL_CHOICE,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_PARALLEL_TOOL_CALLS,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    DEFAULT_TOOL_CHOICE,
    DOMAIN,
    EVENT_MEMORY_PROPOSAL_CREATED,
    EVENT_MEMORY_PROPOSAL_UPDATED,
    SERVICE_APPROVE_MEMORY_PROPOSAL,
    SERVICE_CREATE_MEMORY_PROPOSAL,
    SERVICE_LIST_MEMORY_PROPOSALS,
    SERVICE_REJECT_MEMORY_PROPOSAL,
    SERVICE_TEST_PROVIDER,
)
from .memory.proposals import MemoryProposalStore
from .providers import OpenAICompatibleProvider, ProviderError

ATTR_INCLUDE_RESOLVED = "include_resolved"
DEFAULT_TEST_PROVIDER_MESSAGE = "Reply with exactly: ok"

CREATE_MEMORY_PROPOSAL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONTENT): vol.All(cv.string, str.strip, vol.Length(min=1)),
        vol.Optional(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_SOURCE): cv.string,
        vol.Optional(ATTR_METADATA, default={}): dict,
    }
)

LIST_MEMORY_PROPOSALS_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_INCLUDE_RESOLVED, default=False): cv.boolean,
    }
)

REVIEW_MEMORY_PROPOSAL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PROPOSAL_ID): cv.string,
        vol.Optional(ATTR_REASON): cv.string,
    }
)

TEST_PROVIDER_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_MESSAGE, default=DEFAULT_TEST_PROVIDER_MESSAGE): vol.All(
            cv.string,
            str.strip,
            vol.Length(min=1),
        ),
    }
)


async def async_setup_services(
    hass: HomeAssistant,
    proposal_store: MemoryProposalStore,
) -> None:
    """Register House Personality services."""

    async def async_create_memory_proposal(call: ServiceCall) -> dict[str, Any]:
        proposal = await proposal_store.async_create(
            content=call.data[ATTR_CONTENT],
            title=call.data.get(ATTR_TITLE),
            source=call.data.get(ATTR_SOURCE),
            metadata=call.data.get(ATTR_METADATA),
        )
        payload = {ATTR_PROPOSAL: proposal.as_dict()}
        hass.bus.async_fire(EVENT_MEMORY_PROPOSAL_CREATED, payload)
        return payload

    async def async_list_memory_proposals(call: ServiceCall) -> dict[str, Any]:
        proposals = await proposal_store.async_list(
            include_resolved=call.data[ATTR_INCLUDE_RESOLVED],
        )
        return {ATTR_PROPOSALS: [proposal.as_dict() for proposal in proposals]}

    async def async_approve_memory_proposal(call: ServiceCall) -> dict[str, Any]:
        proposal = await proposal_store.async_approve(
            call.data[ATTR_PROPOSAL_ID],
            reason=call.data.get(ATTR_REASON),
        )
        if proposal is None:
            return {ATTR_PROPOSAL: None}

        payload = {ATTR_PROPOSAL: proposal.as_dict()}
        hass.bus.async_fire(EVENT_MEMORY_PROPOSAL_UPDATED, payload)
        return payload

    async def async_reject_memory_proposal(call: ServiceCall) -> dict[str, Any]:
        proposal = await proposal_store.async_reject(
            call.data[ATTR_PROPOSAL_ID],
            reason=call.data.get(ATTR_REASON),
        )
        if proposal is None:
            return {ATTR_PROPOSAL: None}

        payload = {ATTR_PROPOSAL: proposal.as_dict()}
        hass.bus.async_fire(EVENT_MEMORY_PROPOSAL_UPDATED, payload)
        return payload

    async def async_test_provider(call: ServiceCall) -> dict[str, Any]:
        entry = _find_config_entry(hass)
        if entry is None:
            return {
                ATTR_SUCCESS: False,
                ATTR_ERROR: "House Personality is not configured.",
            }

        values = _entry_values(entry)
        provider = _provider_from_values(hass, values)
        started = time.monotonic()
        try:
            response = await provider.async_generate_response(
                _test_provider_messages(call.data[ATTR_MESSAGE])
            )
        except ProviderError as err:
            return _test_provider_result(
                values,
                success=False,
                latency_ms=_elapsed_ms(started),
                error=str(err),
            )
        except Exception:
            return _test_provider_result(
                values,
                success=False,
                latency_ms=_elapsed_ms(started),
                error="Unexpected provider test failure.",
            )

        return _test_provider_result(
            values,
            success=True,
            latency_ms=_elapsed_ms(started),
            response=response.content,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_MEMORY_PROPOSAL,
        async_create_memory_proposal,
        schema=CREATE_MEMORY_PROPOSAL_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LIST_MEMORY_PROPOSALS,
        async_list_memory_proposals,
        schema=LIST_MEMORY_PROPOSALS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_APPROVE_MEMORY_PROPOSAL,
        async_approve_memory_proposal,
        schema=REVIEW_MEMORY_PROPOSAL_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REJECT_MEMORY_PROPOSAL,
        async_reject_memory_proposal,
        schema=REVIEW_MEMORY_PROPOSAL_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_TEST_PROVIDER,
        async_test_provider,
        schema=TEST_PROVIDER_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


def async_unload_services(hass: HomeAssistant) -> None:
    """Unregister House Personality services."""
    hass.services.async_remove(DOMAIN, SERVICE_CREATE_MEMORY_PROPOSAL)
    hass.services.async_remove(DOMAIN, SERVICE_LIST_MEMORY_PROPOSALS)
    hass.services.async_remove(DOMAIN, SERVICE_APPROVE_MEMORY_PROPOSAL)
    hass.services.async_remove(DOMAIN, SERVICE_REJECT_MEMORY_PROPOSAL)
    hass.services.async_remove(DOMAIN, SERVICE_TEST_PROVIDER)


def _find_config_entry(hass: HomeAssistant) -> ConfigEntry | None:
    """Return the configured House Personality entry."""
    for value in hass.data.get(DOMAIN, {}).values():
        if isinstance(value, ConfigEntry):
            return value
    return None


def _entry_values(entry: ConfigEntry) -> dict[str, Any]:
    """Return merged config entry data and options."""
    values = dict(entry.data)
    values.update(entry.options)
    return values


def _provider_from_values(
    hass: HomeAssistant,
    values: dict[str, Any],
) -> OpenAICompatibleProvider:
    """Build a provider from config entry values."""
    return OpenAICompatibleProvider(
        hass,
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
        debug_logging=False,
    )


def _test_provider_messages(message: str) -> list[dict[str, str]]:
    """Build a minimal text-only provider test prompt."""
    return [
        {
            "role": "system",
            "content": (
                "You are testing connectivity for a Home Assistant integration. "
                "Answer only the user's test message."
            ),
        },
        {"role": "user", "content": message.strip()},
    ]


def _test_provider_result(
    values: dict[str, Any],
    *,
    success: bool,
    latency_ms: int,
    response: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Build a provider test service response."""
    result: dict[str, Any] = {
        ATTR_SUCCESS: success,
        CONF_MODEL: values.get(CONF_MODEL, DEFAULT_MODEL),
        CONF_BASE_URL: values.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        ATTR_LATENCY_MS: latency_ms,
    }
    if response is not None:
        result[ATTR_RESPONSE] = response
    if error is not None:
        result[ATTR_ERROR] = error
    return result


def _elapsed_ms(started: float) -> int:
    """Return elapsed milliseconds from a monotonic start time."""
    return round((time.monotonic() - started) * 1000)
