"""Constants for the House Personality integration."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY, CONF_MODEL, CONF_TIMEOUT

DOMAIN = "house_personality"
NAME = "House Personality"
VERSION = "0.1.1"

ATTR_CONTENT = "content"
ATTR_CREATED_AT = "created_at"
ATTR_METADATA = "metadata"
ATTR_PROPOSAL = "proposal"
ATTR_PROPOSAL_ID = "proposal_id"
ATTR_PROPOSALS = "proposals"
ATTR_REASON = "reason"
ATTR_SOURCE = "source"
ATTR_STATUS = "status"
ATTR_TITLE = "title"
ATTR_UPDATED_AT = "updated_at"

CONF_ASSISTANT_NAME = "assistant_name"
CONF_BASE_URL = "base_url"
CONF_CONTEXT_ENTITY = "context_entity"
CONF_DEBUG_LOGGING = "debug_logging"
CONF_IDENTITY_ENTITY = "identity_entity"
CONF_MEMORY_ENTITY = "memory_entity"
CONF_PERSONALITY_PROMPT = "personality_prompt"
CONF_RECALL_ENABLED = "recall_enabled"
CONF_RECALL_INCLUDE_TURNS = "recall_include_turns"
CONF_RECALL_LIMIT = "recall_limit"
CONF_RECALL_SERVICE_DOMAIN = "recall_service_domain"
CONF_RECALL_SERVICE_NAME = "recall_service_name"
CONF_TEMPERATURE = "temperature"
CONF_VISION_ENABLED = "vision_enabled"
CONF_VISION_ENTITY = "vision_entity"

DEFAULT_ASSISTANT_NAME = "House Assistant"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_CONTEXT_MAX_CHARS = 4000
DEFAULT_IDENTITY_MAX_CHARS = 500
DEFAULT_MEMORY_MAX_CHARS = 6000
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_PERSONALITY_PROMPT = "You are a helpful, concise Home Assistant voice assistant."
DEFAULT_RECALL_LIMIT = 5
DEFAULT_RECALL_MAX_CHARS = 1200
DEFAULT_RECALL_SERVICE_DOMAIN = "conversation_memory"
DEFAULT_RECALL_SERVICE_NAME = "prepare_recall_context"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 30
DEFAULT_VISION_MAX_CHARS = 3000

DATA_PROPOSAL_STORE = "proposal_store"
DATA_SERVICES_REGISTERED = "services_registered"

EVENT_MEMORY_PROPOSAL_CREATED = f"{DOMAIN}_memory_proposal_created"
EVENT_MEMORY_PROPOSAL_UPDATED = f"{DOMAIN}_memory_proposal_updated"

FRIENDLY_PROVIDER_ERROR = (
    "I could not reach the configured language model provider. "
    "Please check the House Personality provider settings."
)

REDACTED = "**REDACTED**"

SERVICE_APPROVE_MEMORY_PROPOSAL = "approve_memory_proposal"
SERVICE_CREATE_MEMORY_PROPOSAL = "create_memory_proposal"
SERVICE_LIST_MEMORY_PROPOSALS = "list_memory_proposals"
SERVICE_REJECT_MEMORY_PROPOSAL = "reject_memory_proposal"

STATUS_APPROVED = "approved"
STATUS_PENDING = "pending"
STATUS_REJECTED = "rejected"

STORAGE_KEY_MEMORY_PROPOSALS = f"{DOMAIN}.memory_proposals"
STORAGE_VERSION_MEMORY_PROPOSALS = 1

CONFIG_KEYS = (
    CONF_ASSISTANT_NAME,
    CONF_BASE_URL,
    CONF_API_KEY,
    CONF_MODEL,
    CONF_TEMPERATURE,
    CONF_TIMEOUT,
    CONF_PERSONALITY_PROMPT,
    CONF_CONTEXT_ENTITY,
    CONF_IDENTITY_ENTITY,
    CONF_MEMORY_ENTITY,
    CONF_RECALL_ENABLED,
    CONF_RECALL_SERVICE_DOMAIN,
    CONF_RECALL_SERVICE_NAME,
    CONF_RECALL_LIMIT,
    CONF_RECALL_INCLUDE_TURNS,
    CONF_VISION_ENABLED,
    CONF_VISION_ENTITY,
    CONF_DEBUG_LOGGING,
)
