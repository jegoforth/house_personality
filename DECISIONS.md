# Project Decisions

This file captures current project decisions for `house_personality` so development remains focused, community-friendly, and testable.

## Current Objective

Build a reusable, HACS-friendly Home Assistant custom integration that provides a configurable personality, context, memory, event-summary, and Home Assistant Assist conversation layer.

The implementation has moved beyond the initial Phase 0/1 MVP. Phases 0 through 6 are implemented as small optional adapters, the conversation agent advertises Home Assistant control support, Phase 7 provider tuning is partially implemented, Phase 8 validation hardening is partially implemented, Phase 9 public-release documentation is in progress, and Phase 10 generic location entity context is partially implemented.

The next work should focus on context-source compatibility, public-release review, remaining validation gaps, and any release packaging needed before broader public feedback.

## Confirmed Decisions

- Repository name: `house_personality`.
- Integration domain: `house_personality`.
- Public integration name: `House Personality`.
- The project should be community-friendly and eventually public.
- The repository may remain private during early development and testing.
- The integration must be designed for HACS installation from the start.
- The integration should register as a Home Assistant conversation agent.
- The provider target remains OpenAI-compatible chat completions.
- The integration should support local or cloud OpenAI-compatible endpoints through configuration.
- Home control should use Home Assistant's current `ConversationEntity`, `ChatLog`, and LLM tool APIs.
- The built-in Assist LLM API should be used for exposed-entity state and control, not custom service-call parsing.
- Provider tool-calling should stay inside the OpenAI-compatible provider adapter and normalized provider interfaces.
- The assistant display name must be configurable.
- The personality prompt must be configurable.
- No assistant name should be hardcoded.
- No private household data should be hardcoded.
- Private assistant configurations are test cases, not the product identity.
- The maintainer's household setup should act as an advanced test case, not the default behavior.
- `CONTEXT_CONTRACTS.md` is the preferred public compatibility target for optional context sources.
- Companion integrations should expose generic Home Assistant entities or services rather than requiring House Personality to know their internals.
- House Personality should consume context; it should not calculate speaker identity, person location, room status, camera analysis, or durable memory itself.

## Implemented Scope

### Phase 0: Repository Foundation

Implemented.

- HACS-compatible repository structure.
- Home Assistant custom integration skeleton.
- `manifest.json`.
- `hacs.json`.
- Basic constants.
- Config flow.
- Translations.
- Diagnostics.
- README foundation.

### Phase 1: Conversation Agent MVP

Implemented.

- Conversation agent registration.
- OpenAI-compatible provider adapter.
- Prompt builder.
- UI configuration for provider and personality settings.
- Provider calls through async Home Assistant patterns.
- Provider responses returned to Assist.
- Safe error handling.
- Debug logging without API keys or full prompt logs.

### Phase 2: Entity-Based Context and Identity

Implemented.

- Optional context entity.
- Optional identity entity.
- Prompt builder support for context and identity.
- Options flow fields for changing context and identity entities.
- Graceful fallback when configured entities are missing, unknown, or unavailable.

### Phase 3: Memory Adapter Foundation

Implemented as read-only entity memory.

- Generic memory adapter module structure.
- Optional memory entity.
- Prompt builder support for memory context.
- Character limits for memory inclusion.
- No direct writes to persistent memory.

### Phase 4: Voice Assist Recall Adapter

Implemented as an optional, read-only service adapter.

- Recall can be enabled or disabled in options.
- Recall service domain and service name are configurable.
- Speaker identity and conversation ID can be passed to recall lookup.
- Recall errors do not block conversation.
- The integration does not require Voice Assist Recall to be installed.

### Phase 5: Memory Update Proposal Workflow

Implemented as local proposal storage and explicit services.

- Create, list, approve, and reject proposal services.
- Proposal events are fired.
- Approving a proposal marks it approved only.
- No approved proposal is written to an external memory system or memory file by this integration.

### Phase 6: Vision/Event Context Adapter

Implemented as optional read-only event-summary entity context.

- Vision/event summary entity can be enabled and configured.
- Text summary state/attributes can be included in the prompt.
- Camera analysis is not performed by House Personality.
- LLM Vision native integration is not implemented.

### Conversation Control Compatibility

Implemented after Phase 6.

- The conversation entity uses `_async_handle_message(self, user_input, chat_log)`.
- `supported_languages` returns `"*"`.
- The entity advertises `ConversationEntityFeature.CONTROL`.
- The agent calls `chat_log.async_provide_llm_data(...)` with Home Assistant's built-in Assist LLM API.
- OpenAI-compatible tools are passed to the configured provider when a current `ChatLog` is available.
- Provider tool calls are executed through `chat_log.async_add_assistant_content(...)`.
- Provider responses are returned through Assist after tool execution.

### Phase 7: Provider Configuration

Partially implemented as single-profile provider tuning.

- Configurable maximum response tokens.
- Configurable tool enable/disable switch.
- Configurable OpenAI-compatible tool choice.
- Configurable parallel tool-call behavior.
- Configurable OpenAI-compatible response format.
- Provider fallback chains, multiple provider profiles, and streaming remain out of scope until explicitly requested.

### Phase 8: Diagnostics, Testing, and Hardening

Partially implemented.

- Added lightweight unit tests that can run without a full Home Assistant runtime.
- Prompt assembly tests cover optional prompt sections and section metadata.
- Provider tests cover OpenAI-compatible payload construction for provider options.
- Diagnostics tests cover secret and configured entity redaction.
- Conversation policy tests cover tools-disabled and `tool_choice=none` behavior.
- GitHub Actions validates JSON files, lightweight unit tests, Python compilation, and private-data scanning.
- GitHub issue and pull request templates are present for eventual public feedback.

### Phase 9: Public Release Readiness

In progress.

- Public-facing examples are documented separately from private user configuration.
- Generic context contracts are documented for optional companion integrations.
- Security and sensitive-data reporting guidance is documented.
- Release checklist is documented.
- Known limitations are documented in the README.
- Community post draft is available for eventual public feedback.

### Phase 10: Person and Room Location Context

Partially implemented as single generic location entity context.

- Location context should be optional.
- House Personality should consume generic entity/service context for person, room, area, or current-speaker location.
- House Personality should not require Bermuda, ESPresense, room-assistant, `person`, `device_tracker`, or any specific location integration.
- Location context should include staleness and confidence guidance.
- Location context should be treated as sensitive private context.
- House Personality should not perform Bluetooth scanning, trilateration, or location calculation itself.
- The current implementation reads one optional `location_entity`, includes safe contract fields, ignores raw GPS fields, and skips stale context.

### Phase 11: Public-Space Room Status Context

Planned.

- Room status context should be optional.
- House Personality should consume generic public-space room status summaries from entities or services.
- House Personality should not require LLM Vision, Frigate, cameras, or any specific vision integration.
- Room status context should include staleness, confidence, and privacy guidance.
- House Personality should not analyze images, video, faces, objects, or camera streams itself.
- Documentation should discourage private-space camera-derived context.

## Out of Scope Until Explicitly Requested

Do not implement these next unless requested:

- Speaker recognition.
- Person location calculation.
- Raw GPS-to-room mapping.
- Room status calculation.
- Memory writing.
- Direct writes to `house_memory.json`.
- LLM Vision native integration.
- Camera analysis.
- Provider fallback chains.
- Multiple provider profiles.
- Streaming support.
- Private assistant-specific behavior.
- Private household-specific configuration.

## Architecture Principles

- Keep provider logic separate from conversation logic.
- Keep prompt assembly separate from provider calls.
- Keep context, identity, memory, and vision/event context as adapters.
- Keep location and room-status context as generic optional adapters.
- Optional features must fail gracefully.
- Avoid hard dependencies on optional integrations.
- Use Home Assistant async patterns.
- Avoid blocking I/O in the event loop.
- Do not log API keys or secrets.
- Do not log full prompts by default.
- Do not log full household memory by default.
- Redact sensitive diagnostics.
- Prefer small, testable modules.

## Current Success Criteria

The current working version should prove:

- Home Assistant can load the integration without import errors.
- The integration can be configured through the UI.
- The configured agent appears as a selectable Assist conversation agent.
- A user can configure an OpenAI-compatible endpoint.
- A user can configure a model and personality prompt.
- A simple Assist text request is sent to the provider.
- The provider response is returned to Assist.
- Optional context, identity, memory, recall, and event-summary sources can be configured.
- Optional context source contracts are documented for companion integrations.
- Missing optional sources do not break conversation.
- If the configured provider supports OpenAI-compatible tool calls, exposed Home Assistant entities can be queried and controlled through Assist.
- Provider failures return a friendly error instead of crashing.
- No private names, household details, or entity IDs are committed.

## Notes for Future Work

Future work may add:

- Provider test service.
- Prompt preview service.
- Better automated tests around provider tool-call handling.
- Additional diagnostics and test hardening.
- HACS/release validation.
- Public release review.
- Generic entity/service adapters for person and room location context.
- Generic entity/service adapters for public-space room status context.
- LLM Vision native adapter.
- Multiple provider profiles.
- Provider fallback behavior.
- Streaming support.
- External memory writer adapters.

These should remain optional and adapter-based.
