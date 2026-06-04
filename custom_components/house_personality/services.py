"""Services for House Personality."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
import homeassistant.helpers.config_validation as cv

from .const import (
    ATTR_CONTENT,
    ATTR_METADATA,
    ATTR_PROPOSAL,
    ATTR_PROPOSAL_ID,
    ATTR_PROPOSALS,
    ATTR_REASON,
    ATTR_SOURCE,
    ATTR_TITLE,
    DOMAIN,
    EVENT_MEMORY_PROPOSAL_CREATED,
    EVENT_MEMORY_PROPOSAL_UPDATED,
    SERVICE_APPROVE_MEMORY_PROPOSAL,
    SERVICE_CREATE_MEMORY_PROPOSAL,
    SERVICE_LIST_MEMORY_PROPOSALS,
    SERVICE_REJECT_MEMORY_PROPOSAL,
)
from .memory.proposals import MemoryProposalStore

ATTR_INCLUDE_RESOLVED = "include_resolved"

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


def async_unload_services(hass: HomeAssistant) -> None:
    """Unregister House Personality services."""
    hass.services.async_remove(DOMAIN, SERVICE_CREATE_MEMORY_PROPOSAL)
    hass.services.async_remove(DOMAIN, SERVICE_LIST_MEMORY_PROPOSALS)
    hass.services.async_remove(DOMAIN, SERVICE_APPROVE_MEMORY_PROPOSAL)
    hass.services.async_remove(DOMAIN, SERVICE_REJECT_MEMORY_PROPOSAL)
