# House Personality

House Personality is a Home Assistant custom integration that registers a configurable Assist conversation agent. It sends the current user request and a user-defined personality prompt to an OpenAI-compatible chat completions endpoint, then returns the provider response back to Assist.

This project is intended to be reusable and community-friendly. It does not include any private household configuration, assistant persona, entity IDs, or memory files.

## Current Capabilities

- Registers a Home Assistant Assist conversation agent.
- Supports UI setup through a config flow.
- Lets users configure:
  - assistant display name
  - provider base URL
  - API key
  - model
  - temperature
  - timeout
  - personality prompt
  - optional context entity
  - optional identity entity
  - optional memory entity
  - optional Voice Assist Recall service adapter
  - debug logging
- Calls an OpenAI-compatible `/chat/completions` endpoint.
- Builds prompts from the configured personality prompt, optional entity context, optional speaker identity, optional memory/recall context, and current user message.
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

HACS support is planned for public testing.

When available:

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
- **Timeout**: Provider request timeout in seconds.
- **Personality prompt**: System prompt that defines assistant behavior.
- **Context entity**: Optional entity whose state and attributes are included as home context.
- **Identity entity**: Optional entity whose state is included as the likely speaker identity.
- **Memory entity**: Optional entity whose state and attributes are included as read-only memory context.
- **Use Voice Assist Recall**: Optional read-only recall lookup through a prompt-safe Recall service.
- **Recall service domain**: Service domain for the recall adapter. The current default is `conversation_memory`.
- **Recall service name**: Service name for the recall adapter. The current default is `prepare_recall_context`.
- **Recall result limit**: Maximum number of relevant recall items requested from the service.
- **Include supporting recall turns**: Whether the Recall service may include supporting raw turns when it prepares context.
- **Debug logging**: Adds operational debug logs without logging API keys or full prompts.

## Provider Setup

House Personality expects an OpenAI-compatible chat completions API.

The configured base URL is normalized as follows:

- If it already ends with `/chat/completions`, it is used directly.
- Otherwise, `/chat/completions` is appended.

Examples:

- `https://api.openai.com/v1`
- `http://localhost:1234/v1`
- `http://homeassistant.local:8000/v1`

## Privacy Notes

House Personality sends the configured personality prompt, current Assist user message, and any configured context, identity, memory entity, or relevant Voice Assist Recall data to the configured provider. Context, memory, and recall content may contain personal home information. Identity entity state may identify a person if you configure it that way.

The integration does not store conversation memory and does not write to any memory file. API keys are redacted from diagnostics and are not logged.
Configured context, identity, and memory entity IDs are also redacted from diagnostics.

Memory proposal services store pending proposal text locally in Home Assistant storage for explicit review. Approving a proposal only marks it approved; it does not write to any external memory system or file.

## Services

House Personality exposes these services:

- `house_personality.create_memory_proposal`: Create a pending memory proposal.
- `house_personality.list_memory_proposals`: List pending proposals, or all proposals when `include_resolved` is true.
- `house_personality.approve_memory_proposal`: Mark a proposal as approved without writing it anywhere else.
- `house_personality.reject_memory_proposal`: Mark a proposal as rejected.

## Troubleshooting

- Confirm the provider base URL points to an OpenAI-compatible chat completions endpoint.
- Confirm the configured model is available on the provider.
- Confirm the API key is valid if the provider requires one.
- If context, identity, or memory is missing, confirm the configured entities exist and are not `unknown` or `unavailable`.
- If recall is missing, confirm the configured service exists. For the current Voice Assist Recall project, use `conversation_memory.prepare_recall_context`.
- Increase the timeout for slower local models.
- Enable debug logging in the integration options for operational details.
- Check Home Assistant logs for provider error summaries.

## Roadmap

- Phase 2: optional entity-based context and speaker identity.
- Phase 3: generic memory adapter foundation.
- Phase 4: optional Voice Assist Recall adapter.
- Phase 5: memory update proposal workflow.
- Phase 6: optional vision/event summary context.
- Phase 7: advanced provider configuration.
- Phase 8: tests, diagnostics hardening, and release validation.
- Phase 9: public release readiness.
