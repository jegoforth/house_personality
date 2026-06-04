"""Constants for the House Personality integration."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY, CONF_MODEL, CONF_TIMEOUT

DOMAIN = "house_personality"
NAME = "House Personality"
VERSION = "0.1.0"

CONF_ASSISTANT_NAME = "assistant_name"
CONF_BASE_URL = "base_url"
CONF_CONTEXT_ENTITY = "context_entity"
CONF_DEBUG_LOGGING = "debug_logging"
CONF_IDENTITY_ENTITY = "identity_entity"
CONF_MEMORY_ENTITY = "memory_entity"
CONF_PERSONALITY_PROMPT = "personality_prompt"
CONF_TEMPERATURE = "temperature"

DEFAULT_ASSISTANT_NAME = "House Assistant"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_CONTEXT_MAX_CHARS = 4000
DEFAULT_IDENTITY_MAX_CHARS = 500
DEFAULT_MEMORY_MAX_CHARS = 6000
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_PERSONALITY_PROMPT = "You are a helpful, concise Home Assistant voice assistant."
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 30

FRIENDLY_PROVIDER_ERROR = (
    "I could not reach the configured language model provider. "
    "Please check the House Personality provider settings."
)

REDACTED = "**REDACTED**"

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
    CONF_DEBUG_LOGGING,
)
