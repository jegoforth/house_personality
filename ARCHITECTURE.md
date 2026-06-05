# House Personality Architecture

## Current Implementation Status

The integration currently implements Phases 0 through 6 plus current Home Assistant conversation entity compatibility for Assist tool calls.

Implemented:

- HACS-friendly repository structure.
- UI config flow and options flow.
- Home Assistant conversation agent registration.
- Current `_async_handle_message(self, user_input, chat_log)` conversation API support.
- `supported_languages` returning `"*"`.
- `ConversationEntityFeature.CONTROL` advertisement.
- OpenAI-compatible chat completions provider.
- OpenAI-compatible tool-call parsing.
- Home Assistant built-in Assist LLM tools passed to compatible providers.
- Tool calls executed through Home Assistant `ChatLog`.
- Configurable assistant name, provider settings, personality prompt, and debug logging.
- Optional entity context.
- Optional entity identity.
- Optional read-only memory entity.
- Optional read-only Voice Assist Recall service adapter.
- Memory proposal services with explicit approve/reject workflow.
- Optional read-only vision/event summary entity.
- Diagnostics with secret redaction.

Still not implemented:

- Speaker recognition.
- Direct memory writing.
- Direct writes to `house_memory.json`.
- LLM Vision native integration.
- Camera analysis.
- Provider fallback chains.
- Multiple provider profiles.
- Streaming support.
- Private assistant or household-specific behavior.

## Project Summary

`house_personality` is a Home Assistant custom integration that provides a configurable personality, identity, memory, and context layer for Home Assistant Assist conversation agents.

The long-term goal is to create a community-friendly, HACS-installable integration that allows Home Assistant users to build a more personal and context-aware voice assistant without hardcoding any specific household, person, voice, provider, or memory system.

This project should be designed as a reusable framework.

The maintainer's personal assistant configuration is only one private example use case. The public integration must not hardcode any private household names, user names, entity IDs, prompts, memory files, or assumptions.

## Design Philosophy

House Personality should act as an orchestration layer.

It should not try to own every AI-related capability directly. Instead, it should coordinate context from optional sources and present that context cleanly to a configured LLM provider.

The integration should support this general flow:

```text
Home Assistant Assist
  → House Personality conversation agent
      → Load configured personality
      → Load optional household/context data
      → Resolve optional speaker identity
      → Retrieve optional conversation memory
      → Retrieve optional vision/event context
      → Build final prompt
      → Call configured LLM provider
      → Return response to Assist
      → Optionally store or propose memory updates
```

The integration should be modular, provider-agnostic, and HACS-friendly from the start.

## Public Project Goals

The public project should provide:

- A Home Assistant conversation agent.
- A configurable assistant/personality prompt.
- Support for OpenAI-compatible LLM providers.
- Support for Home Assistant's built-in Assist LLM tools when the configured provider supports OpenAI-compatible tool calls.
- Optional context injection from Home Assistant entities.
- Optional speaker identity context.
- Optional conversation recall integration.
- Optional future vision/event context.
- Safe fallbacks when optional components are missing.
- Clear debug logging and diagnostics.
- HACS-compatible repository structure.
- Documentation that allows non-developers to install and configure it.

## Non-Goals

The initial project should not:

- Hardcode any specific household or assistant persona.
- Require the maintainer’s speaker recognition integration.
- Require the maintainer’s Voice Assist Recall project.
- Require LLM Vision.
- Directly modify `house_memory.json` in the first release.
- Attempt to replace all Home Assistant LLM integrations.
- Implement custom Home Assistant service-call parsing when the built-in Assist LLM tools can be used.
- Depend on one specific LLM provider.
- Become a monolithic “everything AI” integration.

The project should orchestrate optional capabilities, not duplicate every external integration.

## Repository Structure

The repository should follow this structure:

```text
house_personality/
  README.md
  ARCHITECTURE.md
  hacs.json
  LICENSE
  custom_components/
    house_personality/
      __init__.py
      manifest.json
      const.py
      config_flow.py
      conversation.py
      services.yaml
      strings.json
      diagnostics.py
      translations/
        en.json
      providers/
        __init__.py
        base.py
        openai_compatible.py
      context/
        __init__.py
        entity_context.py
        prompt_builder.py
      identity/
        __init__.py
        base.py
        entity_identity.py
      memory/
        __init__.py
        base.py
        entity_memory.py
        recall_adapter.py
      vision/
        __init__.py
        base.py
        entity_vision.py
      storage/
        __init__.py
        store.py
```

There must be only one Home Assistant integration under `custom_components/`.

The Home Assistant integration domain should be:

```text
house_personality
```

## Naming

Public integration name:

```text
House Personality
```

Integration domain:

```text
house_personality
```

Repository name:

```text
house_personality
```

The integration should allow users to configure their own assistant display name, such as:

```text
House Assistant
Kitchen Assistant
Workshop Assistant
Family Assistant
Personal Assistant
```

No assistant name should be hardcoded.

## Core Concepts

### 1. Personality

The personality is the configured behavior and tone of the assistant.

Examples:

- Friendly and brief.
- Witty and sarcastic.
- Formal and concise.
- Child-friendly.
- Technical and detailed.
- Household-specific.

The personality should be configurable from the UI and stored in the config entry options.

The initial implementation can use a plain text system prompt.

Future versions may support reusable prompt templates.

### 2. Context

Context is information about the home, household, preferences, devices, rooms, routines, or current state.

Initial context sources should be simple and flexible:

- A configured sensor state.
- A configured sensor’s attributes.
- A configured text helper.
- A configured template sensor.
- Multiple context entities in a future phase.

The integration should not assume a specific memory file format in the MVP.

### 3. Identity

Identity is the likely person speaking.

Initial identity support should use a generic entity-based adapter.

For example, a user may configure an entity such as:

```text
sensor.last_recognized_speaker
input_text.current_speaker
sensor.assist_speaker_identity
```

The integration should read that entity and include it in the prompt as optional speaker context.

The integration should not directly depend on any specific speaker recognition integration in the MVP.

### 4. Memory

Memory is prior conversation or preference context that may be relevant to the current request.

The first implementation should support memory as optional context from an entity or service.

Native integration with Voice Assist Recall should be added later through an adapter.

Memory retrieval should be modular and replaceable.

### 5. Vision/Event Context

Vision context may come from LLM Vision, Frigate, camera event summaries, or other entity-based sources.

This should not be part of the MVP.

When added, it should be optional and adapter-based.

House Personality should consume vision summaries; it should not perform camera analysis itself unless explicitly added in a future phase.

### 6. Provider

The LLM provider is the backend that receives the final prompt and returns a response.

The first provider is OpenAI-compatible.

This allows support for:

- OpenAI
- LocalAI
- LM Studio
- llama.cpp server
- vLLM
- Ollama through compatible endpoints if available
- Other OpenAI-compatible gateways

Provider code must be isolated from prompt/context/memory code.

When a current Home Assistant `ChatLog` is available, House Personality should request Home Assistant's built-in Assist LLM API data and pass the resulting tool definitions to the configured provider in OpenAI-compatible format.

Providers that support tool calls can request exposed-entity state or control actions. House Personality should execute those calls through Home Assistant's `ChatLog` and send the tool results back to the provider for a final spoken response.

The integration should not invent its own Home Assistant service-call parser for home control.

## Prompt Assembly

Prompt construction should be centralized in a prompt builder module.

The prompt builder should receive structured inputs:

```python
PromptContext(
    personality_prompt=str,
    user_message=str,
    speaker_identity=Optional[str],
    household_context=Optional[str],
    memory_context=Optional[str],
    vision_context=Optional[str],
)
```

It should produce a final message list suitable for the provider.

The prompt builder should be deterministic, testable, and easy to debug.

Recommended prompt structure:

```text
System:
  Personality and behavior rules.

System:
  Optional household/context information.

System:
  Optional speaker identity.

System:
  Optional relevant memory.

System:
  Optional recent vision/event context.

User:
  Current user message.
```

The integration should log which sections were included or skipped, but it must not log sensitive full prompt content unless debug logging is explicitly enabled.

## Safety and Privacy Principles

The integration may process sensitive home and personal context.

Therefore:

- Do not log full prompts by default.
- Do not log API keys.
- Do not log full memory contents by default.
- Provide debug logging that can be enabled intentionally.
- Provide diagnostics that redact secrets and sensitive values.
- Do not write memory automatically in the MVP.
- Do not assume all users want persistent memory.
- Make memory features optional.
- Clearly document what information is sent to the configured LLM provider.

## HACS and Home Assistant Compliance

The repository must be HACS-friendly from the start.

Required public repo files:

```text
README.md
ARCHITECTURE.md
hacs.json
LICENSE
custom_components/house_personality/manifest.json
```

The manifest should include:

```json
{
  "domain": "house_personality",
  "name": "House Personality",
  "codeowners": ["@jegoforth"],
  "config_flow": true,
  "documentation": "https://github.com/jegoforth/house_personality",
  "issue_tracker": "https://github.com/jegoforth/house_personality/issues",
  "iot_class": "cloud_polling",
  "version": "0.1.0"
}
```

The `iot_class` may need to be revisited depending on provider behavior.

If the integration supports only local endpoints in a future mode, the classification may differ.

The integration must support UI configuration using `config_flow.py`.

Options that users may need to change after setup should be available through an options flow.

## Configuration Model

Initial config flow fields:

```text
Assistant display name
Provider type
Provider base URL
API key
Model
Temperature
Timeout
Personality prompt
Context entity
Identity entity
Debug logging
```

Recommended default provider type:

```text
OpenAI-compatible
```

Recommended initial optional fields:

```text
context_entity
identity_entity
memory_entity
```

Fields should be optional unless required for the configured mode.

## Runtime Flow

The conversation request lifecycle should be:

```text
1. Home Assistant Assist sends text to House Personality.
2. House Personality receives the conversation input.
3. Load config entry options.
4. Read optional identity entity.
5. Read optional context entity.
6. Read optional memory entity or memory adapter.
7. Read optional vision/event summary entity.
8. Build final prompt.
9. If a current ChatLog is available, request Home Assistant's built-in Assist LLM API data.
10. Convert Home Assistant tools into OpenAI-compatible tool definitions.
11. Send chat log messages and tools to the configured provider.
12. If the provider returns tool calls, execute them through `chat_log.async_add_assistant_content(...)`.
13. Send resulting tool responses back to the provider.
14. Return the final provider response to Home Assistant Assist.
15. Log timing and included context sections.
16. Store memory proposals only when explicitly created through the proposal workflow.
```

## Error Handling

The integration must fail gracefully.

If the context entity is unavailable:

```text
Continue without context.
Log that context was skipped.
```

If the identity entity is unavailable:

```text
Continue with unknown speaker.
Log that identity was skipped.
```

If memory is unavailable:

```text
Continue without memory.
Log that memory was skipped.
```

If the LLM provider fails:

```text
Return a friendly error response through the conversation agent.
Do not expose raw stack traces to the user.
Log technical details for troubleshooting.
```

If the prompt is too large:

```text
Truncate optional sections in priority order.
Prefer keeping:
1. Personality prompt
2. Current user message
3. Speaker identity
4. Most relevant memory
5. Household context
6. Vision/event context
```

## Development Phases

### Phase 0: Repository Foundation

Status: Implemented.

Goal:

Create a clean, public, HACS-compatible repository skeleton.

Deliverables:

- Repository structure.
- `README.md`.
- `ARCHITECTURE.md`.
- `hacs.json`.
- `LICENSE`.
- `custom_components/house_personality/manifest.json`.
- Basic constants.
- Initial translations.
- Placeholder config flow.
- Placeholder diagnostics.

Acceptance Criteria:

- Repository structure matches HACS expectations.
- Home Assistant can discover the custom integration.
- Integration can be added manually to `custom_components`.
- No private household data is present.
- No assistant name is hardcoded.

### Phase 1: Conversation Agent MVP

Status: Implemented.

Goal:

Register House Personality as a Home Assistant conversation agent and return responses from an OpenAI-compatible provider.

Deliverables:

- Conversation platform implementation.
- OpenAI-compatible provider adapter.
- Config flow for provider settings.
- Configurable assistant/personality prompt.
- Basic prompt builder.
- Friendly error handling.
- Debug logging.

Acceptance Criteria:

- User can install the integration.
- User can configure provider base URL, API key, model, temperature, and timeout.
- User can configure a personality prompt.
- The integration appears as a selectable conversation agent.
- Assist can send text to the agent.
- The provider response is returned to Assist.
- Provider failures return a friendly error.

### Phase 2: Entity-Based Context and Identity

Status: Implemented.

Goal:

Add optional entity-based context and speaker identity.

Deliverables:

- Context entity support.
- Identity entity support.
- Prompt builder support for context and identity.
- Debug logs showing included/skipped context.
- Options flow for changing context and identity entities.

Acceptance Criteria:

- User can select a context entity.
- User can select an identity entity.
- If entities are available, their state or attributes are included in the prompt.
- If entities are unavailable, the request still works.
- No dependency on a specific speaker recognition integration exists.

### Phase 3: Memory Adapter Foundation

Status: Implemented as read-only entity memory.

Goal:

Add a generic memory adapter system.

Deliverables:

- Memory provider interface.
- Entity-based memory adapter.
- Optional service-based memory adapter.
- Prompt builder support for memory snippets.
- Memory inclusion limits.

Acceptance Criteria:

- Memory is optional.
- Memory can be sourced from a configured entity or service.
- Memory snippets are included only when available.
- Memory failures do not block conversation.
- Prompt size controls prevent runaway context.

### Phase 4: Native Voice Assist Recall Adapter

Status: Implemented as an optional read-only service adapter.

Goal:

Integrate with the separate Voice Assist Recall project without making it a hard dependency.

Deliverables:

- Optional adapter for Voice Assist Recall.
- Detection of whether Voice Assist Recall is installed.
- Retrieval of relevant conversation snippets.
- Speaker-aware memory lookup when identity is available.
- Graceful fallback when unavailable.

Acceptance Criteria:

- House Personality works without Voice Assist Recall.
- If Voice Assist Recall is installed and configured, relevant recall snippets are included.
- Speaker identity can be passed to recall lookup.
- Recall errors do not break the conversation.

### Phase 5: Memory Update Proposal Workflow

Status: Implemented as local proposal storage and explicit services. Approved proposals are not written anywhere by House Personality.

Goal:

Allow the assistant to propose memory updates without automatically changing persistent memory.

Deliverables:

- Memory proposal model.
- Service for creating proposed memory updates.
- Event fired when memory update is proposed.
- Optional persistent storage for pending proposals.
- Approval/rejection services.

Acceptance Criteria:

- Assistant can identify possible memory updates.
- Updates are stored as proposals, not directly written to permanent memory.
- User can approve or reject a proposal.
- Approved proposals can be emitted to an external memory system or written by a configured adapter.
- No automatic modification of household memory happens without explicit configuration.

### Phase 6: Vision/Event Context Adapter

Status: Implemented as optional read-only entity-based event summary context. Native LLM Vision integration is still future work.

Goal:

Add optional support for recent visual or event context from external integrations.

Deliverables:

- Vision/event context provider interface.
- Entity-based event summary adapter.
- Placeholder for future LLM Vision adapter only if needed.
- Prompt builder support for recent event context.
- Configuration options for enabling/disabling vision context.

Acceptance Criteria:

- Vision context is optional.
- House Personality works without LLM Vision.
- Recent event summaries can be included when configured.
- Camera analysis is not performed directly by House Personality in this phase.
- Vision context has strict size limits.

### Conversation Control Compatibility

Status: Implemented after Phase 6.

Goal:

Make the House Personality conversation entity compatible with the current Home Assistant conversation entity and LLM tool APIs so Assist can query and control exposed entities through compatible providers.

Deliverables:

- `_async_handle_message(self, user_input, chat_log)` implementation.
- `supported_languages` returning `"*"`.
- `ConversationEntityFeature.CONTROL` support.
- Home Assistant built-in Assist LLM API data requested through `chat_log.async_provide_llm_data(...)`.
- OpenAI-compatible tool definitions passed to the configured provider.
- Provider tool calls executed through `chat_log.async_add_assistant_content(...)`.
- Final provider response returned through the conversation framework.

Acceptance Criteria:

- Home Assistant can load the integration.
- The configured agent is selectable in Assist.
- The "cannot control your home" warning is not shown for the agent.
- State queries work for entities exposed to Assist.
- Control requests work when the provider/model emits compatible tool calls.
- Provider or tool failures return a friendly response instead of crashing.

### Phase 7: Advanced Provider Support

Goal:

Improve provider flexibility and resilience.

Deliverables:

- Multiple provider profiles.
- Per-provider model settings.
- Optional local/cloud fallback provider.
- Better timeout handling.
- Provider test service.
- Streaming support if feasible.

Acceptance Criteria:

- User can configure more than one provider profile.
- User can test provider connectivity.
- Provider errors are readable and useful.
- Local and cloud providers can be swapped without changing context/memory configuration.

### Phase 8: Diagnostics, Testing, and Hardening

Goal:

Prepare the integration for broader public use.

Deliverables:

- Diagnostics support with redaction.
- Unit tests for prompt builder.
- Unit tests for provider adapter.
- Unit tests for context handling.
- Linting.
- Hassfest validation if applicable.
- GitHub issue templates.
- GitHub release workflow.
- Clear troubleshooting docs.

Acceptance Criteria:

- Sensitive values are redacted in diagnostics.
- Prompt assembly is tested.
- Provider errors are tested.
- Missing optional entities are tested.
- Installation and upgrade docs are clear.
- HACS installation path is documented.

### Phase 9: Public Release Readiness

Goal:

Prepare for initial public release.

Deliverables:

- Tagged release.
- Complete README.
- Screenshots if useful.
- Example configurations.
- Privacy documentation.
- Roadmap.
- Known limitations.
- HACS custom repository install instructions.
- Community forum post draft.

Acceptance Criteria:

- A new user can install through HACS custom repositories.
- A new user can configure a basic OpenAI-compatible provider.
- A new user can create a working personality prompt.
- Optional features are clearly marked as optional.
- The project does not expose private maintainer configuration.
- The repository is ready for public feedback.

## Suggested Services

Future services may include:

```yaml
house_personality.reload_context
house_personality.test_provider
house_personality.render_prompt_preview
house_personality.propose_memory_update
house_personality.approve_memory_update
house_personality.reject_memory_update
house_personality.clear_session
```

The MVP does not need all services.

## Logging

Logging should include:

- Provider selected.
- Model selected.
- Request start and end time.
- LLM latency.
- Context included or skipped.
- Identity included or skipped.
- Memory included or skipped.
- Approximate prompt size.
- Friendly provider error summaries.

Logging should not include by default:

- API keys.
- Full prompts.
- Full memory.
- Full household profiles.
- Full responses.

Verbose prompt logging may be added later behind an explicit debug setting.

## Prompt Size Management

Prompt size must be controlled.

The integration should eventually support configurable limits, such as:

```text
Maximum context characters
Maximum memory snippets
Maximum vision/event snippets
Maximum total prompt characters
```

Recommended priority when trimming:

```text
1. Keep personality prompt.
2. Keep current user message.
3. Keep speaker identity.
4. Keep most relevant memory.
5. Trim household context.
6. Trim vision/event context.
```

## Privacy Documentation Requirements

The README should clearly explain:

- What data may be sent to the LLM provider.
- How context entities are used.
- How identity entities are used.
- Whether memory is stored.
- Whether prompts are logged.
- How to disable optional features.
- Difference between local and cloud providers.

## Example Use Cases

### Basic Personality Agent

A user configures:

```text
Assistant name: House Assistant
Provider: OpenAI-compatible endpoint
Personality: Friendly, concise, helpful
Context: none
Identity: none
Memory: none
```

### Context-Aware House Assistant

A user configures:

```text
Assistant name: Family Assistant
Context entity: sensor.home_context_summary
Identity: none
Memory: none
```

### Speaker-Aware Assistant

A user configures:

```text
Assistant name: Home Assistant
Context entity: sensor.home_context_summary
Identity entity: sensor.last_recognized_speaker
Memory: none
```

### Advanced Personal Assistant

A user configures:

```text
Assistant name: Personal Assistant
Context entity: sensor.home_context_summary
Identity entity: sensor.speaker_recognition_last_user
Memory provider: Voice Assist Recall
Vision provider: event summary entity
```

This advanced example should be documented as optional and not required.

## Coding Guidelines

- Keep provider logic separate from Home Assistant conversation logic.
- Keep prompt building separate from provider calls.
- Keep identity, memory, context, and vision as adapters.
- Avoid hard dependencies on optional integrations.
- Use Home Assistant async patterns.
- Keep config entries and options clean.
- Avoid blocking I/O in the event loop.
- Redact secrets.
- Fail gracefully.
- Prefer small, testable modules.

## Initial Codex Implementation Target

The initial Codex implementation target was Phase 0 and Phase 1 only.

That target is complete. Memory, recall, proposal, and event-summary work has since been added as optional adapters. Speaker recognition, native LLM Vision, camera analysis, provider fallback chains, multiple provider profiles, streaming, and direct memory writing remain out of scope until explicitly requested.

The initial implementation proved:

```text
Installable custom integration
Configurable provider
Configurable personality prompt
Registered conversation agent
Prompt sent to OpenAI-compatible endpoint
Response returned to Assist
```

Future implementation should continue to preserve the same boundaries: optional adapters, no private household assumptions, no automatic memory writes, and no custom home-control parser when Home Assistant's Assist LLM tools are available.

## Long-Term Vision

House Personality should become a community-friendly foundation for personalized Home Assistant voice assistants.

The integration should allow users to bring their own:

- Assistant name.
- Personality.
- LLM provider.
- Home context.
- Speaker identity source.
- Memory system.
- Vision/event source.

The maintainer's private setup should serve as an advanced test case, not the default behavior.

The final goal is a flexible Home Assistant Assist conversation agent that feels aware of the home, aware of the speaker, and able to use memory responsibly while remaining installable, understandable, and safe for community use.
