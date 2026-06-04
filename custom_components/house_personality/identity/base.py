"""Base identity models for House Personality."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IdentityResult:
    """Result from resolving optional speaker identity."""

    speaker: str | None
    included: bool
    reason: str
