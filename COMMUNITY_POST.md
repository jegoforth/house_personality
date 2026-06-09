# Community Post Draft

Title:

```text
House Personality: a configurable Assist conversation agent for Home Assistant
```

Body:

```text
House Personality is a Home Assistant custom integration that registers a configurable Assist conversation agent backed by an OpenAI-compatible chat completions provider.

The goal is to provide a reusable personality/context layer for Assist without hardcoding any specific household, assistant persona, provider, memory system, or speaker-recognition setup.

Current capabilities:

- UI configuration flow
- configurable assistant name and personality prompt
- OpenAI-compatible provider support
- Home Assistant Assist tool support for exposed-entity state and control
- optional read-only context entity
- optional read-only identity entity
- optional read-only memory entity
- optional read-only recall service adapter
- optional read-only event summary entity
- memory proposal services that do not write to external memory
- diagnostics with redaction

Not implemented:

- speaker recognition
- direct memory writing
- camera analysis
- native LLM Vision integration
- provider fallback chains
- multiple provider profiles
- streaming

Install through HACS as a custom repository, restart Home Assistant, then add House Personality from Settings > Devices & services.

The project is looking for testing feedback around installation, provider compatibility, Assist tool calls, diagnostics redaction, and documentation clarity.

Please do not post API keys, private prompts, private entity IDs, names, addresses, screenshots with household details, or memory contents in public issues.
```
