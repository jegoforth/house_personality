# House Personality Architecture

## Current Implementation Status

The integration currently implements Phases 0 through 6, current Home Assistant conversation entity compatibility for Assist tool calls, partial Phase 7 provider tuning, partial Phase 8 validation hardening, and Phase 9 public-release documentation readiness.

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
- Optional read-only Voice Assist Recall-compatible service adapter.
- Memory proposal services with explicit approve/reject workflow.
- Optional read-only vision/event summary entity.
- Single-profile provider tuning for max tokens, tool behavior, and response format.
- Lightweight unit tests for prompt assembly, provider payload construction, diagnostics redaction, and no-tools policy.
- GitHub Actions validation workflow.
- GitHub issue and pull request templates.
- Public release support docs, examples, security notes, release checklist, and community post draft.
- Generic context contracts for optional identity, location, room status, house context, memory, recall, and vision/event summary sources.
- Diagnostics with secret redaction.

Still not implemented:

- Speaker recognition.
- Native person/room location integration.
- Native public-space room status integration.
- Direct memory writing.
- Direct writes to `house_memory.json`.
- LLM Vision native integration.
- Camera analysis.
- Provider fallback chains.
- Multiple provider profiles.
- Streaming support.
- Private assistant or household-specific behavior.

## Project Summary

`house_personality` is a Home Assistant custom integration that provides a configurable personality, identity, memory, location/context, room-status context, and Home Assistant Assist conversation layer.

The long-term goal is to create a community-friendly, HACS-installable integration that allows Home Assistant users to build a more personal and context-aware voice assistant without hardcoding any specific household, person, voice, provider, memory system, recognition engine, vision system, camera system, or location system.

This project should be designed as a reusable framework.

The maintainer's personal assistant configuration is only one private example use case. The public integration must not hardcode any private household names, user names, entity IDs, prompts, memory files, location devices, camera devices, floor plans, or assumptions.

## Design Philosophy

House Personality should act as an orchestration layer.

It should not try to own every AI-related capability directly. Instead, it should coordinate context from optional sources and present that context cleanly to a configured LLM provider.

The integration should support this general flow:

```text
Home Assistant Assist
  -> House Personality conversation agent
      -> Load configured personality
      -> Load optional household/context data
      -> Resolve optional speaker identity
      -> Retrieve optional person/room location context
      -> Retrieve optional public-space room status context
      -> Retrieve optional conversation memory
      -> Retrieve optional vision/event context
      -> Build final prompt
      -> Call configured LLM provider
      -> Return response to Assist
      -> Optionally store memory proposals
```

The integration should be modular, provider-agnostic, and HACS-friendly from the start.

`CONTEXT_CONTRACTS.md` defines the preferred generic entity and service shapes for optional companion integrations. That document is the public compatibility target for future integrations that want to provide context to House Personality without becoming hard dependencies.

## Public Project Goals

The public project should provide:

- A Home Assistant conversation agent.
- A configurable assistant/personality prompt.
- Support for OpenAI-compatible LLM providers.
- Support for Home Assistant's built-in Assist LLM tools when the configured provider supports OpenAI-compatible tool calls.
- Optional context injection from Home Assistant entities.
- Optional speaker identity context.
- Optional person/room location context from Home Assistant entities.
- Optional public-space room status context from Home Assistant entities.
- Optional read-only conversation recall integration.
- Optional read-only vision/event summary context.
- Safe fallbacks when optional components are missing.
- Clear debug logging and diagnostics.
- HACS-compatible repository structure.
- Documentation that allows non-developers to install and configure it.

## Non-Goals

The project should not:

- Hardcode any specific household or assistant persona.
- Require the maintainer's speaker recognition integration.
- Require the maintainer's Voice Assist Recall project.
- Require Bermuda, ESPresense, room-assistant, or any specific person-location integration.
- Require LLM Vision, Frigate, or any specific camera/vision integration.
- Directly modify `house_memory.json` in the first release.
- Attempt to replace all Home Assistant LLM integrations.
- Implement custom Home Assistant service-call parsing when the built-in Assist LLM tools can be used.
- Implement native Bluetooth trilateration, BLE scanning, face recognition, camera analysis, video recording, continuous camera streaming, or voice embedding models.
- Analyze raw images during normal conversation turns.
- Encourage cameras in private spaces such as bedrooms or bathrooms.
- Depend on one specific LLM provider.
- Become a monolithic "everything AI" integration.

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
      diagnostics.py
      services.py
      services.yaml
      strings.json
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
      location/
        __init__.py
        base.py
        entity_location.py
      room_status/
        __init__.py
        base.py
        entity_room_status.py
      memory/
        __init__.py
        base.py
        entity_memory.py
        proposals.py
        recall_adapter.py
      vision/
        __init__.py
        base.py
        entity_vision.py
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

The current implementation uses a plain text system prompt.

Future versions may support reusable prompt templates.

### 2. General Context

Context is information about the home, household, preferences, devices, rooms, routines, policies, people, or current state.

Initial context sources should be simple and flexible:

- A configured sensor state.
- A configured sensor's attributes.
- A configured text helper.
- A configured template sensor.
- Multiple context entities in a future phase.

The integration should not assume a specific memory file or profile format.

### 3. Identity

Identity is the likely person speaking.

Identity support should use a generic entity-based adapter.

For example, a user may configure an entity such as:

```text
sensor.last_recognized_speaker
input_text.current_speaker
sensor.assist_speaker_identity
```

The integration should read that entity and include it in the prompt as optional speaker context.

The integration should not directly depend on any specific speaker recognition integration.

### 4. Person and Room Location

Person and room location describe where a person, device, or current Assist interaction is likely taking place.

This is a high-value context source for natural requests such as:

```text
Turn on the lights in here.
Make it warmer where I am.
Is anyone still downstairs?
Where is Person A?
Did I leave my phone in the office?
```

House Personality should not perform Bluetooth trilateration, BLE scanning, GPS tracking, face tracking, or room-presence calculations itself.

Instead, House Personality should consume optional location context from Home Assistant entities or services produced by integrations such as:

- Bermuda.
- ESPresense.
- room-assistant.
- Home Assistant `person` entities.
- Home Assistant `device_tracker` entities.
- Template sensors.
- Manual helpers.
- Future local presence or room context integrations.

The initial person/room location design should be entity-based and adapter-based.

Example location entities:

```text
sensor.person_a_current_area
sensor.person_b_current_room
sensor.last_detected_person_area
device_tracker.person_a_phone
person.person_a
input_text.current_room
```

House Personality should consume values such as:

```yaml
state: Kitchen
attributes:
  person: Person A
  confidence: medium
  source: bermuda
  device: Person A phone
  area_id: kitchen
  updated_at: "2026-06-09T12:00:00-04:00"
```

House Personality should use location as grounding context, not as an authoritative identity or control source.

When both identity and location are available, the prompt builder may include context such as:

```text
Likely speaker: Person A.
Likely speaker location: Kitchen.
Assist device area: Kitchen.
Location source: Bermuda/device_tracker.
Confidence: medium.
```

Location context should remain optional and should fail gracefully when stale, unavailable, unknown, or disabled.

### 5. Public-Space Room Status

Room status describes what is currently or recently happening in a shared/public area of the home.

Room status may be generated from cameras, motion sensors, occupancy sensors, Bluetooth presence, door sensors, Frigate events, LLM Vision summaries, template sensors, manual helpers, or other Home Assistant entities.

House Personality should consume room status as short text summaries or structured entity attributes. It should not continuously watch camera streams or analyze raw camera images during normal conversation turns.

Examples of useful room status summaries:

```text
Kitchen appears occupied. Someone is near the counter. Summary age: 45 seconds.
Living room appears empty. TV is on. Summary age: 2 minutes.
Foyer motion was detected near the front door. Summary age: 20 seconds.
Dining room is occupied. People appear seated at the table. Summary age: 1 minute.
```

Good public-space camera use cases:

- Kitchen activity/status.
- Living room occupancy/status.
- Foyer/entry status.
- Dining/common-area status.
- Package/object/context summaries in shared spaces.

Poor or out-of-scope camera use cases:

- Bedrooms.
- Bathrooms.
- Private changing/sleeping areas.
- Always-on raw image prompt injection.
- Long-term image retention by House Personality.
- Face recognition inside House Personality.
- Continuous surveillance by the conversation agent.

House Personality should consume values such as:

```yaml
state: occupied
attributes:
  room: Kitchen
  area_id: kitchen
  summary: "A person appears to be near the counter. The room lights are on."
  source: llm_vision
  camera: camera.kitchen
  confidence: medium
  observed_at: "2026-06-09T12:00:00-04:00"
  summary_age_seconds: 45
```

Room status context should remain optional and should fail gracefully when stale, unavailable, unknown, private, or disabled.

House Personality should treat room status as conversational grounding, not proof. For example, it may say "It looks like the kitchen is occupied" rather than making absolute claims.

### 6. Memory

Memory is prior conversation or preference context that may be relevant to the current request.

The current implementation supports memory as optional read-only context from an entity and optional read-only recall context from a configured service.

Voice Assist Recall-style integration is service-based and optional. House Personality does not require any specific recall integration to be installed.

Memory retrieval should be modular and replaceable.

### 7. Vision/Event Context

Vision/event context may come from LLM Vision, Frigate, camera event summaries, or other entity-based sources.

The current implementation supports optional read-only text summary context from a configured entity.

Native LLM Vision integration remains future work.

House Personality should consume vision summaries; it should not perform camera analysis itself unless explicitly added in a future setup/admin workflow.

### 8. Provider

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

Provider code must be isolated from prompt/context/memory/location/room-status code.

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
    location_context=Optional[str],
    room_status_context=Optional[str],
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
  Optional person/room location context.

System:
  Optional public-space room status context.

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
- Do not log full household profiles by default.
- Do not log detailed person-location history by default.
- Do not log detailed room-status history by default.
- Do not send raw camera images to the LLM during normal conversation turns.
- Do not encourage cameras in bedrooms, bathrooms, or private spaces.
- Prefer triggered snapshots and short text summaries over continuous camera analysis.
- Provide debug logging that can be enabled intentionally.
- Provide diagnostics that redact secrets and sensitive values.
- Do not write memory automatically.
- Do not assume all users want persistent memory.
- Make memory, identity, location, room status, and vision features optional.
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

Current config flow and options fields:

```text
Assistant display name
Provider base URL
API key
Model
Temperature
Maximum response tokens
Timeout
Personality prompt
Use Home Assistant tools
Tool choice
Parallel tool calls
Response format
Context entity
Identity entity
Memory entity
Use Voice Assist Recall
Recall service domain
Recall service name
Recall result limit
Include supporting recall turns
Use vision/event summary context
Vision/event summary entity
Debug logging
```

Provider behavior is currently single-profile and OpenAI-compatible. There is no provider type selector yet.

Recommended provider type:

```text
OpenAI-compatible
```

Recommended future optional person/room location fields:

```text
use_location_context
location_entity
person_location_entity
assist_area_entity
location_max_age_seconds
```

Recommended future optional room-status fields:

```text
use_room_status_context
room_status_entity
room_status_entities
room_status_max_age_seconds
public_space_only
include_camera_source_name
```

Recommended optional context fields:

```text
context_entity
identity_entity
location_entity
room_status_entity
memory_entity
vision_entity
```

Fields should be optional unless required for the configured mode.

## Runtime Flow

The conversation request lifecycle should be:

```text
1. Home Assistant Assist sends text to House Personality.
2. House Personality receives the conversation input.
3. Load config entry options.
4. Read optional identity entity.
5. Read optional person/room location entity.
6. Read optional public-space room status entity/entities.
7. Read optional context entity.
8. Read optional memory entity or memory adapter.
9. Read optional vision/event summary entity.
10. Build final prompt.
11. If a current ChatLog is available, request Home Assistant's built-in Assist LLM API data.
12. Convert Home Assistant tools into OpenAI-compatible tool definitions.
13. Send chat log messages and tools to the configured provider.
14. If the provider returns tool calls, execute them through `chat_log.async_add_assistant_content(...)`.
15. Send resulting tool responses back to the provider.
16. Return the final provider response to Home Assistant Assist.
17. Log timing and included context sections.
18. Store memory proposals only when explicitly created through the proposal workflow.
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

If the location entity is unavailable, stale, unknown, or disabled:

```text
Continue without location context.
Log that location was skipped.
```

If room-status context is unavailable, stale, private, unknown, or disabled:

```text
Continue without room-status context.
Log that room status was skipped.
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
4. Person/room location context
5. Most relevant memory
6. Household context
7. Current public-space room status
8. Vision/event context
```

## Development Phases

### Phase 0: Repository Foundation

Status: Implemented.

Goal: Create a clean, public, HACS-compatible repository skeleton.

Acceptance Criteria:

- Repository structure matches HACS expectations.
- Home Assistant can discover the custom integration.
- Integration can be added manually to `custom_components`.
- No private household data is present.
- No assistant name is hardcoded.

### Phase 1: Conversation Agent MVP

Status: Implemented.

Goal: Register House Personality as a Home Assistant conversation agent and return responses from an OpenAI-compatible provider.

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

Goal: Add optional entity-based context and speaker identity.

Acceptance Criteria:

- User can select a context entity.
- User can select an identity entity.
- If entities are available, their state or attributes are included in the prompt.
- If entities are unavailable, the request still works.
- No dependency on a specific speaker recognition integration exists.

### Phase 3: Memory Adapter Foundation

Status: Implemented as read-only entity memory.

Goal: Add a generic memory adapter system.

Acceptance Criteria:

- Memory is optional.
- Memory can be sourced from a configured entity or service.
- Memory snippets are included only when available.
- Memory failures do not block conversation.
- Prompt size controls prevent runaway context.

### Phase 4: Voice Assist Recall-Compatible Adapter

Status: Implemented as an optional read-only service adapter.

Goal: Integrate with recall services without making any specific recall project a hard dependency.

Acceptance Criteria:

- House Personality works without Voice Assist Recall.
- If a compatible recall service is installed and configured, relevant recall snippets are included.
- Speaker identity can be passed to recall lookup.
- Recall errors do not break the conversation.

### Phase 5: Memory Update Proposal Workflow

Status: Implemented as local proposal storage and explicit services. Approved proposals are not written anywhere by House Personality.

Goal: Allow the assistant to propose memory updates without automatically changing persistent memory.

Acceptance Criteria:

- Assistant can identify possible memory updates.
- Updates are stored as proposals, not directly written to permanent memory.
- User can approve or reject a proposal.
- Approved proposals are marked approved and can be consumed by external automation.
- No automatic modification of household memory happens without explicit configuration.

### Phase 6: Vision/Event Context Adapter

Status: Implemented as optional read-only entity-based event summary context. Native LLM Vision integration is still future work.

Goal: Add optional support for recent visual or event context from external integrations.

Acceptance Criteria:

- Vision context is optional.
- House Personality works without LLM Vision.
- Recent event summaries can be included when configured.
- Camera analysis is not performed directly by House Personality in this phase.
- Vision context has strict size limits.

### Conversation Control Compatibility

Status: Implemented after Phase 6.

Goal: Make the House Personality conversation entity compatible with the current Home Assistant conversation entity and LLM tool APIs so Assist can query and control exposed entities through compatible providers.

Acceptance Criteria:

- Home Assistant can load the integration.
- The configured agent is selectable in Assist.
- The "cannot control your home" warning is not shown for the agent.
- State queries work for entities exposed to Assist.
- Control requests work when the provider/model emits compatible tool calls.
- Provider or tool failures return a friendly response instead of crashing.

### Phase 7: Advanced Provider Support

Status: Partially implemented as single-profile provider configuration. Multiple provider profiles, provider fallback chains, and streaming are still future work.

Goal: Improve provider flexibility and resilience.

Implemented:

- Maximum response token setting.
- Tool enable/disable switch.
- Tool-choice setting.
- Parallel tool-call setting.
- Response-format setting.

Future work:

- Multiple provider profiles.
- Optional local/cloud fallback provider.
- Provider test service.
- Streaming support if feasible.

### Phase 8: Diagnostics, Testing, and Hardening

Status: Partially implemented.

Goal: Prepare the integration for broader public use.

Implemented:

- Diagnostics support with redaction.
- Unit tests for prompt assembly.
- Unit tests for provider payload construction.
- Unit tests for diagnostics redaction.
- Unit tests for no-tools conversation policy.
- GitHub issue templates.
- GitHub pull request template.
- GitHub validation workflow for JSON validation, unit tests, Python compilation, and private-data scanning.

Future work:

- More context adapter tests.
- Missing optional entity tests.
- Provider error tests.
- Hassfest validation if applicable.
- GitHub release workflow.

### Phase 9: Public Release Readiness

Status: In progress.

Goal: Prepare for initial public release.

Implemented:

- Example configurations.
- Privacy documentation.
- Security reporting guidance.
- Roadmap.
- Known limitations.
- HACS custom repository install instructions.
- Release checklist.
- Community forum post draft.

Future work:

- Tagged release.
- Screenshots if useful.
- Final README review.
- Public feedback.

### Phase 10: Person and Room Location Context

Status: Planned.

Goal: Add optional person/room location context from Home Assistant entities or services without making House Personality responsible for calculating location.

Examples of compatible providers:

- Bermuda.
- ESPresense.
- room-assistant.
- Home Assistant `person` entities.
- Home Assistant `device_tracker` entities.
- Template sensors.
- Manual helpers.

Deliverables:

- Location provider interface.
- Entity-based location adapter.
- Optional person-location entity configuration.
- Optional Assist-area/current-room entity configuration.
- Staleness/max-age handling.
- Prompt builder support for person/room location context.
- Debug logs showing location included/skipped.
- Documentation examples for Bermuda and generic entities.

Acceptance Criteria:

- Location context is optional.
- House Personality works without Bermuda or any location integration.
- User can configure a generic entity that represents current person, room, area, or device location.
- Unavailable, unknown, or stale location data does not break conversation.
- Location context can help ground ambiguous requests like "in here" or "where I am".
- No Bluetooth scanning, trilateration, face recognition, or room detection is performed by House Personality.

### Phase 11: Public-Space Room Status Context

Status: Planned.

Goal: Add optional public-space room status context from Home Assistant entities or services without making House Personality responsible for camera analysis, surveillance, or image processing.

Examples of compatible providers:

- LLM Vision-generated summary sensors.
- Frigate events or summary sensors.
- Home Assistant camera snapshot automations.
- Motion or occupancy sensors.
- Bluetooth/person-location integrations.
- Door/contact sensors.
- Template sensors that summarize multiple signals.
- Manual helpers.

Deliverables:

- Room status provider interface.
- Entity-based room status adapter.
- Optional room-status entity configuration.
- Optional support for multiple public-space room status entities.
- Staleness/max-age handling.
- Privacy guardrails and documentation for public-space-only camera-derived context.
- Prompt builder support for room status context.
- Debug logs showing room status included/skipped.
- Documentation examples for triggered snapshot summaries and generic room-status entities.

Acceptance Criteria:

- Room status context is optional.
- House Personality works without LLM Vision, Frigate, or any camera integration.
- User can configure one or more generic entities that represent public-space room status.
- Unavailable, unknown, stale, or private room-status data does not break conversation.
- Room status context can help answer requests like "what is going on downstairs?" or ground ambiguous requests such as "turn on the lights where people are."
- House Personality does not continuously watch camera feeds.
- House Personality does not send raw images to the provider during normal conversation turns.
- House Personality does not perform face recognition, object detection, or camera analysis itself.
- Documentation discourages cameras in bedrooms, bathrooms, or private spaces.

## Services

Implemented services:

```yaml
house_personality.create_memory_proposal
house_personality.list_memory_proposals
house_personality.approve_memory_proposal
house_personality.reject_memory_proposal
```

Future services may include:

```yaml
house_personality.test_provider
house_personality.render_prompt_preview
house_personality.reload_context
house_personality.clear_session
```

## Logging

Logging should include:

- Provider selected.
- Model selected.
- Request start and end time.
- LLM latency.
- Context included or skipped.
- Identity included or skipped.
- Location included or skipped.
- Room status included or skipped.
- Memory included or skipped.
- Approximate prompt size.
- Friendly provider error summaries.

Logging should not include by default:

- API keys.
- Full prompts.
- Full memory.
- Full household profiles.
- Full person-location history.
- Full room-status history.
- Full camera summaries beyond compact current context.
- Full responses.

Verbose prompt logging may be added later behind an explicit debug setting.

## Prompt Size Management

Prompt size must be controlled.

The integration should eventually support configurable limits, such as:

```text
Maximum context characters
Maximum location characters
Maximum room-status characters
Maximum memory snippets
Maximum vision/event snippets
Maximum total prompt characters
```

Recommended priority when trimming:

```text
1. Keep personality prompt.
2. Keep current user message.
3. Keep speaker identity.
4. Keep current person/room location.
5. Keep most relevant memory.
6. Keep directly relevant current room status.
7. Trim household context.
8. Trim broader vision/event context.
```

## Privacy Documentation Requirements

The README should clearly explain:

- What data may be sent to the LLM provider.
- How context entities are used.
- How identity entities are used.
- How person/room location entities are used.
- How public-space room-status entities are used.
- Whether camera-derived summaries are sent to the provider.
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
Location: none
Room status: none
Memory: none
```

### Context-Aware House Assistant

A user configures:

```text
Assistant name: Family Assistant
Context entity: sensor.home_context_summary
Identity: none
Location: none
Room status: none
Memory: none
```

### Speaker-Aware Assistant

A user configures:

```text
Assistant name: Home Assistant
Context entity: sensor.home_context_summary
Identity entity: sensor.last_recognized_speaker
Location: none
Room status: none
Memory: none
```

### Room-Aware Assistant

A user configures:

```text
Assistant name: Home Assistant
Context entity: sensor.home_context_summary
Identity entity: sensor.last_recognized_speaker
Location entity: sensor.eric_current_area
Location source: Bermuda or equivalent entity
Room status: none
Memory: none
```

### Public-Space Room Status Assistant

A user configures:

```text
Assistant name: Home Assistant
Context entity: sensor.home_context_summary
Identity entity: sensor.last_recognized_speaker
Location entity: sensor.current_person_area
Room status entity: sensor.kitchen_room_status
Room status source: LLM Vision, Frigate, occupancy sensor, or template entity
Memory: none
```

### Advanced Personal Assistant

A user configures:

```text
Assistant name: Personal Assistant
Context entity: sensor.home_context_summary
Identity entity: sensor.speaker_recognition_last_user
Location entity: sensor.current_person_area
Room status entities:
  - sensor.kitchen_room_status
  - sensor.living_room_status
  - sensor.foyer_room_status
Memory provider: Voice Assist Recall-compatible service
Vision provider: event summary entity
```

This advanced example should be documented as optional and not required.

## Coding Guidelines

- Keep provider logic separate from Home Assistant conversation logic.
- Keep prompt building separate from provider calls.
- Keep identity, location, room status, memory, context, and vision as adapters.
- Avoid hard dependencies on optional integrations.
- Use Home Assistant async patterns.
- Keep config entries and options clean.
- Avoid blocking I/O in the event loop.
- Redact secrets.
- Fail gracefully.
- Prefer small, testable modules.

## Initial Codex Implementation Target

The initial Codex implementation target was Phase 0 and Phase 1 only.

That target is complete. Memory, recall, proposal, and event-summary work has since been added as optional adapters. Speaker recognition, native person-location calculation, native room-status generation, native LLM Vision, camera analysis, provider fallback chains, multiple provider profiles, streaming, and direct memory writing remain out of scope until explicitly requested.

The initial implementation proved:

```text
Installable custom integration
Configurable provider
Configurable personality prompt
Registered conversation agent
Prompt sent to OpenAI-compatible endpoint
Response returned to Assist
```

Future implementation should continue to preserve the same boundaries: optional adapters, no private household assumptions, no automatic memory writes, no native recognition/location/camera engines, no raw image analysis during normal conversation turns, and no custom home-control parser when Home Assistant's Assist LLM tools are available.

## Long-Term Vision

House Personality should become a community-friendly foundation for personalized Home Assistant voice assistants.

The integration should allow users to bring their own:

- Assistant name.
- Personality.
- LLM provider.
- Home context.
- Speaker identity source.
- Person/room location source.
- Public-space room status source.
- Memory system.
- Vision/event source.

The maintainer's private setup should serve as an advanced test case, not the default behavior.

The final goal is a flexible Home Assistant Assist conversation agent that feels aware of the home, aware of the speaker, aware of relevant room/location context, aware of recent public-space room status when explicitly configured, and able to use memory responsibly while remaining installable, understandable, privacy-conscious, and safe for community use.
