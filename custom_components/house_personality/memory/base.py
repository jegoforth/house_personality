"""Base memory models for House Personality."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemoryResult:
    """Result from reading optional memory context."""

    content: str | None
    included: bool
    reason: str

