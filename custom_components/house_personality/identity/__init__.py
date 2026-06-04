"""Identity adapters for House Personality."""

from .base import IdentityResult
from .entity_identity import async_get_entity_identity

__all__ = [
    "IdentityResult",
    "async_get_entity_identity",
]

