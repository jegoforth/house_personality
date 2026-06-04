"""Memory proposal storage for House Personality."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from typing import Any
from uuid import uuid4

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from ..const import (
    ATTR_CONTENT,
    ATTR_CREATED_AT,
    ATTR_METADATA,
    ATTR_PROPOSAL_ID,
    ATTR_REASON,
    ATTR_SOURCE,
    ATTR_STATUS,
    ATTR_TITLE,
    ATTR_UPDATED_AT,
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
    STORAGE_KEY_MEMORY_PROPOSALS,
    STORAGE_VERSION_MEMORY_PROPOSALS,
)


@dataclass(frozen=True, slots=True)
class MemoryProposal:
    """A proposed memory update awaiting explicit user review."""

    proposal_id: str
    content: str
    title: str | None
    source: str | None
    metadata: dict[str, Any]
    status: str
    created_at: str
    updated_at: str
    reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the proposal."""
        return {
            ATTR_PROPOSAL_ID: self.proposal_id,
            ATTR_CONTENT: self.content,
            ATTR_TITLE: self.title,
            ATTR_SOURCE: self.source,
            ATTR_METADATA: self.metadata,
            ATTR_STATUS: self.status,
            ATTR_CREATED_AT: self.created_at,
            ATTR_UPDATED_AT: self.updated_at,
            ATTR_REASON: self.reason,
        }


class MemoryProposalStore:
    """Persistent storage for memory proposals."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the proposal store."""
        self._store = Store(
            hass,
            STORAGE_VERSION_MEMORY_PROPOSALS,
            STORAGE_KEY_MEMORY_PROPOSALS,
        )
        self._proposals: dict[str, MemoryProposal] = {}
        self._loaded = False

    async def async_load(self) -> None:
        """Load proposals from storage."""
        if self._loaded:
            return

        data = await self._store.async_load() or {}
        raw_proposals = data.get("proposals", [])
        self._proposals = {}
        for raw_proposal in raw_proposals:
            proposal = _proposal_from_dict(raw_proposal)
            if proposal is not None:
                self._proposals[proposal.proposal_id] = proposal
        self._loaded = True

    async def async_create(
        self,
        *,
        content: str,
        title: str | None,
        source: str | None,
        metadata: dict[str, Any] | None,
    ) -> MemoryProposal:
        """Create a pending memory proposal."""
        await self.async_load()
        now = _now()
        proposal = MemoryProposal(
            proposal_id=uuid4().hex,
            content=content.strip(),
            title=_clean_optional(title),
            source=_clean_optional(source),
            metadata=_clean_metadata(metadata),
            status=STATUS_PENDING,
            created_at=now,
            updated_at=now,
        )
        self._proposals[proposal.proposal_id] = proposal
        await self._async_save()
        return proposal

    async def async_list(
        self,
        *,
        include_resolved: bool,
    ) -> list[MemoryProposal]:
        """List memory proposals."""
        await self.async_load()
        proposals = list(self._proposals.values())
        if not include_resolved:
            proposals = [
                proposal for proposal in proposals if proposal.status == STATUS_PENDING
            ]
        return sorted(proposals, key=lambda proposal: proposal.created_at)

    async def async_approve(
        self,
        proposal_id: str,
        *,
        reason: str | None,
    ) -> MemoryProposal | None:
        """Mark a proposal as approved without writing it anywhere else."""
        return await self._async_update_status(
            proposal_id,
            status=STATUS_APPROVED,
            reason=reason,
        )

    async def async_reject(
        self,
        proposal_id: str,
        *,
        reason: str | None,
    ) -> MemoryProposal | None:
        """Mark a proposal as rejected."""
        return await self._async_update_status(
            proposal_id,
            status=STATUS_REJECTED,
            reason=reason,
        )

    async def _async_update_status(
        self,
        proposal_id: str,
        *,
        status: str,
        reason: str | None,
    ) -> MemoryProposal | None:
        """Update a proposal status."""
        await self.async_load()
        existing = self._proposals.get(proposal_id)
        if existing is None:
            return None

        updated = MemoryProposal(
            proposal_id=existing.proposal_id,
            content=existing.content,
            title=existing.title,
            source=existing.source,
            metadata=existing.metadata,
            status=status,
            created_at=existing.created_at,
            updated_at=_now(),
            reason=_clean_optional(reason),
        )
        self._proposals[proposal_id] = updated
        await self._async_save()
        return updated

    async def _async_save(self) -> None:
        """Persist proposals."""
        await self._store.async_save(
            {"proposals": [proposal.as_dict() for proposal in self._proposals.values()]}
        )


def _proposal_from_dict(value: Any) -> MemoryProposal | None:
    """Parse a stored proposal."""
    if not isinstance(value, dict):
        return None

    proposal_id = value.get(ATTR_PROPOSAL_ID)
    content = value.get(ATTR_CONTENT)
    status = value.get(ATTR_STATUS, STATUS_PENDING)
    created_at = value.get(ATTR_CREATED_AT)
    updated_at = value.get(ATTR_UPDATED_AT)
    if not all(isinstance(item, str) and item for item in (proposal_id, content)):
        return None
    if status not in {STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED}:
        return None

    metadata = value.get(ATTR_METADATA)
    if not isinstance(metadata, dict):
        metadata = {}

    return MemoryProposal(
        proposal_id=proposal_id,
        content=content,
        title=_clean_optional(value.get(ATTR_TITLE)),
        source=_clean_optional(value.get(ATTR_SOURCE)),
        metadata=_clean_metadata(metadata),
        status=status,
        created_at=created_at if isinstance(created_at, str) else _now(),
        updated_at=updated_at if isinstance(updated_at, str) else _now(),
        reason=_clean_optional(value.get(ATTR_REASON)),
    )


def _clean_optional(value: Any) -> str | None:
    """Normalize optional string values."""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _clean_metadata(value: Any) -> dict[str, Any]:
    """Normalize metadata to JSON-safe object data."""
    if not isinstance(value, dict):
        return {}
    return json.loads(json.dumps(value, ensure_ascii=True, default=str))


def _now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(UTC).isoformat()
