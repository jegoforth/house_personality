"""Test helpers for loading the integration outside Home Assistant."""

from __future__ import annotations

import contextlib
from datetime import UTC, datetime
import sys
import types
from collections.abc import Iterator


@contextlib.contextmanager
def homeassistant_stubs() -> Iterator[None]:
    """Install minimal Home Assistant stubs for import-only unit tests."""
    previous = dict(sys.modules)

    homeassistant = types.ModuleType("homeassistant")
    const = types.ModuleType("homeassistant.const")
    const.CONF_API_KEY = "api_key"
    const.CONF_MODEL = "model"
    const.CONF_TIMEOUT = "timeout"
    const.STATE_UNAVAILABLE = "unavailable"
    const.STATE_UNKNOWN = "unknown"
    const.Platform = types.SimpleNamespace(CONVERSATION="conversation")

    config_entries = types.ModuleType("homeassistant.config_entries")
    config_entries.ConfigEntry = type("ConfigEntry", (), {})

    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})
    core.State = type("State", (), {})
    core.ServiceCall = type("ServiceCall", (), {})
    core.SupportsResponse = types.SimpleNamespace(OPTIONAL="optional", ONLY="only")

    components = types.ModuleType("homeassistant.components")
    conversation = types.ModuleType("homeassistant.components.conversation")
    conversation.ConversationEntity = type("ConversationEntity", (), {})
    conversation.ConversationEntityFeature = types.SimpleNamespace(CONTROL=1)
    conversation.ConversationInput = type("ConversationInput", (), {})
    conversation.ChatLog = type("ChatLog", (), {})
    conversation.AssistantContent = type("AssistantContent", (), {})

    class ConverseError(Exception):
        """Minimal ConverseError stub."""

        def as_conversation_result(self):
            return None

    conversation.ConverseError = ConverseError
    conversation.ConversationResult = type("ConversationResult", (), {})

    helpers = types.ModuleType("homeassistant.helpers")
    intent = types.ModuleType("homeassistant.helpers.intent")

    class IntentResponse:
        """Minimal IntentResponse stub."""

        def __init__(self, language: str | None = None) -> None:
            self.language = language
            self.speech = None

        def async_set_speech(self, speech: str) -> None:
            self.speech = speech

    intent.IntentResponse = IntentResponse

    llm = types.ModuleType("homeassistant.helpers.llm")
    llm.LLM_API_ASSIST = "assist"
    llm.ToolInput = type("ToolInput", (), {})

    aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
    aiohttp_client.async_get_clientsession = lambda hass: None

    util = types.ModuleType("homeassistant.util")
    dt = types.ModuleType("homeassistant.util.dt")
    dt.UTC = UTC
    dt.utcnow = lambda: datetime.now(UTC)
    dt.parse_datetime = datetime.fromisoformat
    util.dt = dt

    config_validation = types.ModuleType("homeassistant.helpers.config_validation")
    config_validation.string = str
    config_validation.boolean = bool

    storage = types.ModuleType("homeassistant.helpers.storage")

    class Store:
        """Minimal storage Store stub."""

        def __init__(self, *args, **kwargs) -> None:
            pass

    storage.Store = Store

    async_timeout = types.ModuleType("async_timeout")

    class timeout:
        """Minimal async timeout context manager."""

        def __init__(self, seconds: int) -> None:
            self.seconds = seconds

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    async_timeout.timeout = timeout

    voluptuous_openapi = types.ModuleType("voluptuous_openapi")
    voluptuous_openapi.convert = lambda value, custom_serializer=None: value

    voluptuous = types.ModuleType("voluptuous")
    voluptuous.Schema = lambda schema: schema
    voluptuous.Required = lambda key: key
    voluptuous.Optional = lambda key, default=None: key
    voluptuous.All = lambda *validators: validators[-1] if validators else None
    voluptuous.Length = lambda *args, **kwargs: str

    sys.modules.update(
        {
            "homeassistant": homeassistant,
            "homeassistant.const": const,
            "homeassistant.config_entries": config_entries,
            "homeassistant.core": core,
            "homeassistant.components": components,
            "homeassistant.components.conversation": conversation,
            "homeassistant.helpers": helpers,
            "homeassistant.helpers.intent": intent,
            "homeassistant.helpers.llm": llm,
            "homeassistant.helpers.aiohttp_client": aiohttp_client,
            "homeassistant.util": util,
            "homeassistant.util.dt": dt,
            "homeassistant.helpers.config_validation": config_validation,
            "homeassistant.helpers.storage": storage,
            "async_timeout": async_timeout,
            "voluptuous_openapi": voluptuous_openapi,
            "voluptuous": voluptuous,
        }
    )

    try:
        yield
    finally:
        sys.modules.clear()
        sys.modules.update(previous)
