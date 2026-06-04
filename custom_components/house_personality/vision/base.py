"""Base vision/event context models for House Personality."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VisionContextResult:
    """Result from reading optional vision or event context."""

    content: str | None
    included: bool
    reason: str

