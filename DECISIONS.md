# Project Decisions

This file captures the current project decisions for `house_personality` so development remains focused and community-friendly.

## Current Objective

Build a reusable, HACS-friendly Home Assistant custom integration that provides a configurable personality and context layer for Home Assistant Assist conversation agents.

The first implementation target is Phase 0 and Phase 1 from `ARCHITECTURE.md` only.

## Confirmed Decisions

- Repository name: `house_personality`
- Integration domain: `house_personality`
- Public integration name: `House Personality`
- The project should be community-friendly and eventually public.
- The repository may remain private during early development and testing.
- The integration must be designed for HACS installation from the start.
- The integration should register as a Home Assistant conversation agent.
- The initial provider target is OpenAI-compatible chat completions.
- The integration should support local or cloud OpenAI-compatible endpoints through configuration.
- The assistant display name must be configurable.
- The personality prompt must be configurable.
- No assistant name should be hardcoded.
- No private household data should be hardcoded.
- Elspeth is an example/private configuration, not the product identity.
- The maintainer’s household setup should act as an advanced test case, not the default behavior.

## Phase Scope

### Implement Now

Phase 0: Repository Foundation

- HACS-compatible repository structure.
- Home Assistant custom integration skeleton.
- `manifest.json`.
- `hacs.json`.
- Basic constants.
- Config flow skeleton.
- Translations.
- Diagnostics placeholder.
- README foundation.

Phase 1: Conversation Agent MVP

- Register a conversation agent.
- Add an OpenAI-compatible provider adapter.
- Add a prompt builder.
- Add UI configuration for provider and personality settings.
- Send prompt to configured provider.
- Return provider response to Assist.
- Add safe error handling.
- Add useful debug logging.

### Do Not Implement Yet

Do not implement these in the first coding pass:

- Speaker recognition.
- Voice Assist Recall native integration.
- Memory writing.
- Memory update proposals.
- LLM Vision integration.
- Camera analysis.
- Provider fallback chains.
- Multiple provider profiles.
- Streaming support.
- Elspeth-specific behavior.
- Goforth-specific configuration.
- Direct writes to `house_memory.json`.

## Architecture Principles

- Keep provider logic separate from conversation logic.
- Keep prompt assembly separate from provider calls.
- Keep context, identity, memory, and vision as adapters.
- Optional features must fail gracefully.
- Avoid hard dependencies on optional integrations.
- Use Home Assistant async patterns.
- Avoid blocking I/O in the event loop.
- Do not log API keys or secrets.
- Do not log full prompts by default.
- Do not log full household memory by default.
- Redact sensitive diagnostics.
- Prefer small, testable modules.

## Initial Success Criteria

The first working version should prove:

- Home Assistant can load the integration without import errors.
- The integration can be configured through the UI.
- The configured agent appears as a selectable Assist conversation agent.
- A user can configure an OpenAI-compatible endpoint.
- A user can configure a model and personality prompt.
- A simple Assist text request is sent to the provider.
- The provider response is returned to Assist.
- Provider failures return a friendly error instead of crashing.
- No private names, household details, or entity IDs are committed.

## Notes for Future Phases

Future phases may add:

- Entity-based context injection.
- Entity-based speaker identity.
- Generic memory adapter.
- Voice Assist Recall adapter.
- Memory update proposal workflow.
- LLM Vision or event-summary adapter.
- Multiple provider profiles.
- Provider fallback behavior.
- Prompt preview service.
- Diagnostics and test hardening.

These should be added only after Phase 0 and Phase 1 are stable.
