# House Personality

House Personality is a Home Assistant custom integration that registers a configurable Assist conversation agent. It sends the current user request and a user-defined personality prompt to an OpenAI-compatible chat completions endpoint, then returns the provider response back to Assist.

This project is intended to be reusable and community-friendly. It does not include any private household configuration, assistant persona, entity IDs, or memory files.

## Requirements

- Home Assistant Core 2025.3.0 or newer.
- An OpenAI-compatible chat completions provider.
- A provider/model with tool-call support is required for controlling exposed Home Assistant entities through Assist.

## Current Capabilities

- Registers a Home Assistant Assist conversation agent.
- Supports UI setup through a config flow.
- Lets users configure:
  - assistant display name
  - provider base URL
  - API key
  - model
  - temperature
  - maximum response tokens
  - timeout
  - personality prompt
  - Home Assistant tool use
  - OpenAI-compatible tool choice
  - parallel tool-call behavior
  - response format
  - optional context entity
  - optional identity entity
  - optional memory entity
  - optional Voice Assist Recall service adapter
  - optional vision/event summary entity
  - debug logging
- Calls an OpenAI-compatible `/chat/completions` endpoint.
- Passes Home Assistant's built-in Assist LLM tools to compatible providers so exposed entities can be queried or controlled.
- Builds prompts from the configured personality prompt, optional entity context, optional speaker identity, optional memory/recall context, optional vision/event summary context, and current user message.
- Returns friendly fallback responses when the provider fails.
- Provides memory update proposal services for explicit review.
- Provides diagnostics with secret redaction.

## Not Implemented Yet

The first version intentionally does not implement:

- speaker recognition
- memory writing
- LLM Vision integration
- camera analysis
- provider fallback chains
- multiple provider profiles
- streaming responses
- direct writes to `house_memory.json`

## HACS Installation

House Personality can be installed as a custom HACS integration while the repository is private or in public testing.

1. Add this repository as a custom HACS repository.
2. Select the `Integration` category.
3. Install House Personality.
4. Restart Home Assistant.
5. Add the integration from **Settings > Devices & services**.

## Manual Installation

1. Copy `custom_components/house_personality` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & services**.
4. Select **Add Integration**.
5. Search for **House Personality**.

## Configuration

The UI config flow asks for:

- **Assistant display name**: The label shown for the Assist agent.
- **Provider base URL**: Base URL for the OpenAI-compatible API, such as `https://api.openai.com/v1` or a local endpoint.
- **API key**: Secret token sent as a bearer token. Some local endpoints may accept any value or no value.
- **Model**: Provider model name.
- **Temperature**: Sampling temperature.
- **Maximum response tokens**: Optional cap for provider response length. Use `0` for the provider default.
- **Timeout**: Provider request timeout in seconds.
- **Personality prompt**: System prompt that defines assistant behavior.
- **Use Home Assistant tools**: Pass Assist tools to the provider for exposed-entity state and control.
- **Tool choice**: OpenAI-compatible tool-choice mode sent when tools are enabled. Supported values are `auto`, `required`, and `none`.
- **Parallel tool calls**: Allow compatible providers to request multiple tool calls in a single response. Disabled by default for more predictable Home Assistant control.
- **Response format**: Optional OpenAI-compatible response format. Use `default` unless a provider specifically needs `text` or `json_object`.
- **Context entity**: Optional entity whose state and attributes are included as home context.
- **Identity entity**: Optional entity whose state is included as the likely speaker identity.
- **Memory entity**: Optional entity whose state and attributes are included as read-only memory context.
- **Use Voice Assist Recall**: Optional read-only recall lookup through a prompt-safe Recall service.
- **Recall service domain**: Service domain for the recall adapter. The current default is `conversation_memory`.
- **Recall service name**: Service name for the recall adapter. The current default is `prepare_recall_context`.
- **Recall result limit**: Maximum number of relevant recall items requested from the service.
- **Include supporting recall turns**: Whether the Recall service may include supporting raw turns when it prepares context.
- **Use vision/event summary context**: Enables read-only event summary inclusion from a configured entity.
- **Vision/event summary entity**: Optional entity whose state and attributes describe recent camera, event, or visual summary context.
- **Debug logging**: Adds operational debug logs without logging API keys or full prompts.

The API key is entered during setup. In the options flow, the API key field is blank by default; leave it blank to keep the existing key, or enter a new value to replace it. The stored key is not pre-filled in options.

Home Assistant may show raw option keys for some selector-based fields. The fields map as follows:

| Field key | Purpose |
| --- | --- |
| `max_tokens` | Optional response-token cap. `0` uses the provider default. |
| `tools_enabled` | Enables passing Home Assistant Assist tools to the provider. |
| `tool_choice` | Tool choice mode: `auto`, `required`, or `none`. `none` disables provider tool passing for the request. |
| `parallel_tool_calls` | Allows compatible providers to request parallel tool calls. |
| `response_format` | Optional provider response format: `default`, `text`, or `json_object`. |
| `context_entity` | Optional helper or sensor with home context. |
| `identity_entity` | Optional helper or sensor whose state is the current speaker, such as `Guest` or `Unknown`. |
| `memory_entity` | Optional helper or sensor with read-only durable memory summary. |
| `recall_enabled` | Enables optional read-only recall service lookup. |
| `recall_service_domain` | Service domain for the recall adapter. |
| `recall_service_name` | Service name for the recall adapter. |
| `recall_limit` | Maximum number of recall items requested. |
| `recall_include_turns` | Allows recall to include supporting conversation turns. |
| `vision_enabled` | Enables optional event/vision summary context. |
| `vision_entity` | Optional helper or sensor with recent event summary text. |
| `debug_logging` | Enables operational debug logs. |

## Building Helper Entities

House Personality does not create private household context or memory by default. Users choose which Home Assistant helpers, template sensors, or external integrations to connect.

### Personality Prompt

Use the personality prompt for assistant behavior and tone. This can be generic or household-specific in your private Home Assistant instance.

Example:

```text
You are a helpful, concise Home Assistant voice assistant. Use Home Assistant state and tools when answering smart-home questions. Do not invent missing facts.
```

### Context Entity

Use `context_entity` for broad home context that may be useful in many requests.

Suitable sources include:

- `input_text` helper
- template sensor
- markdown/text sensor from another integration
- automation-maintained summary entity

Example state:

```text
Home context summary. Use Home Assistant state for live device status. Use configured memory only for durable facts. Do not invent missing facts.
```

### Identity Entity

Use `identity_entity` only for the current speaker or person identity. Leave it blank if you do not have speaker recognition or another reliable identity source.

Example states:

```text
Guest
Unknown
Person A
Person B
```

Do not put the assistant persona in `identity_entity`; put persona text in the personality prompt or a context helper.

### Memory Entity

Use `memory_entity` for a read-only summary of durable facts, preferences, or project notes. House Personality reads this content into the prompt but does not write back to it.

Example state or attributes:

```text
Shared preferences are available. Recent durable notes are available. Do not treat missing facts as known.
```

### Voice Assist Recall

When enabled, House Personality calls the configured recall service and includes returned text as optional memory context. The recall service is optional and must prepare prompt-safe text.

Default service fields:

```text
recall_service_domain: conversation_memory
recall_service_name: prepare_recall_context
```

### Vision/Event Summary Entity

Use `vision_entity` for read-only text summaries from another integration or helper. House Personality does not analyze camera images or video.

Example state:

```text
Recent event summary: motion was detected near the driveway at 8:42 PM.
```

## Provider Setup

House Personality expects an OpenAI-compatible chat completions API.

For home control through Assist, the provider/model must support OpenAI-compatible tool calls. House Personality passes Home Assistant's built-in Assist tools to the provider and executes returned tool calls through Home Assistant's conversation chat log.

Provider compatibility options:

- Keep **Use Home Assistant tools** enabled for state queries and device control.
- Disable **Use Home Assistant tools** if a provider rejects tool schemas or does not support tool calling.
- Keep **Tool choice** set to `auto` for normal use. Use `none` to disable provider tool passing for the request. Use `required` only when testing a provider's tool-call behavior.
- Keep **Parallel tool calls** disabled unless the provider and target Home Assistant actions have been tested with parallel tool execution.
- Keep **Response format** set to `default` for broad compatibility. `json_object` is useful only for models and prompts that are explicitly expected to return JSON.
- Set **Maximum response tokens** to `0` to let the provider choose its default, or a positive number to cap response length.

The configured base URL is normalized as follows:

- If it already ends with `/chat/completions`, it is used directly.
- Otherwise, `/chat/completions` is appended.

Examples:

- `https://api.openai.com/v1`
- `http://localhost:1234/v1`
- `http://homeassistant.local:8000/v1`

## Privacy Notes

House Personality sends the configured personality prompt, current Assist user message, and any configured context, identity, memory entity, relevant Voice Assist Recall data, or vision/event summary entity data to the configured provider. Context, memory, recall, and event summary content may contain personal home information. Identity entity state may identify a person if you configure it that way.

House Personality does not analyze camera images or video. Vision/event context is read only from text summaries exposed by other integrations or helpers.

The integration does not store conversation memory and does not write to any memory file. API keys are redacted from diagnostics and are not logged.
Configured context, identity, memory, and vision/event entity IDs are also redacted from diagnostics.

Memory proposal services store pending proposal text locally in Home Assistant storage for explicit review. Approving a proposal only marks it approved; it does not write to any external memory system or file.

## Services

House Personality exposes these services:

- `house_personality.create_memory_proposal`: Create a pending memory proposal.
- `house_personality.list_memory_proposals`: List pending proposals, or all proposals when `include_resolved` is true.
- `house_personality.approve_memory_proposal`: Mark a proposal as approved without writing it anywhere else.
- `house_personality.reject_memory_proposal`: Mark a proposal as rejected.

## Testing

See [TESTING.md](TESTING.md) for a repeatable manual test checklist covering installation, config flow, options flow, text Assist, voice Assist, tool control, recall, diagnostics, and privacy checks.

Run lightweight unit tests from the repository root:

```bash
uv run python -m unittest discover -s tests
```

See [CHANGELOG.md](CHANGELOG.md) for private test release notes.

## Troubleshooting

- Confirm the provider base URL points to an OpenAI-compatible chat completions endpoint.
- Confirm the configured model is available on the provider.
- Confirm the API key is valid if the provider requires one.
- If context, identity, or memory is missing, confirm the configured entities exist and are not `unknown` or `unavailable`.
- If recall is missing, confirm the configured service exists. For the current Voice Assist Recall project, use `conversation_memory.prepare_recall_context`.
- If vision/event context is missing, confirm the configured summary entity exists and contains text summary data.
- Increase the timeout for slower local models.
- Enable debug logging in the integration options for operational details.
- Check Home Assistant logs for provider error summaries.

## Roadmap

- Phase 2: optional entity-based context and speaker identity. Implemented.
- Phase 3: generic memory adapter foundation. Implemented as read-only entity memory.
- Phase 4: optional Voice Assist Recall adapter. Implemented as an optional read-only service adapter.
- Phase 5: memory update proposal workflow. Implemented as explicit proposal services.
- Phase 6: optional vision/event summary context. Implemented as read-only entity summary context.
- Phase 7: advanced provider configuration.
- Phase 8: tests, diagnostics hardening, and release validation.
- Phase 9: public release readiness.
