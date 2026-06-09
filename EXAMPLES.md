# Example Configurations

These examples are intentionally generic. Do not copy private household details into public issues or documentation.

## Basic Personality Agent

Use this when you only want a configurable Assist conversation agent backed by an OpenAI-compatible provider.

```text
assistant_name: House Assistant
base_url: https://api.openai.com/v1
model: gpt-4o-mini
temperature: 0.7
max_tokens: 0
tools_enabled: true
tool_choice: auto
parallel_tool_calls: false
response_format: default
personality_prompt: You are a helpful, concise Home Assistant voice assistant.
context_entity: blank
identity_entity: blank
memory_entity: blank
recall_enabled: false
vision_enabled: false
```

## Local Provider

Use this shape for a local OpenAI-compatible server.

```text
assistant_name: Local Assistant
base_url: http://homeassistant.local:1234/v1
model: local-model-name
temperature: 0.5
max_tokens: 0
tools_enabled: true
tool_choice: auto
parallel_tool_calls: false
response_format: default
personality_prompt: You are a concise local Home Assistant voice assistant. Use tools for live home state and control.
```

Some local providers do not support tool calls or reject Home Assistant tool schemas. If that happens, set:

```text
tools_enabled: false
```

With tools disabled, general conversation can still work, but live Home Assistant state and control will not.

## Context Entity

Use `context_entity` for broad home context maintained by a helper, template sensor, or another integration.

Example helper state:

```text
Home context summary. Use Home Assistant state for live device status. Use configured memory only for durable facts. Do not invent missing facts.
```

## Identity Entity

Use `identity_entity` only for the current speaker identity, not the assistant personality.

Example states:

```text
Guest
Unknown
Person A
Person B
```

Leave this blank if you do not have a reliable identity source.

## Read-Only Memory Entity

Use `memory_entity` for a text summary of durable facts or preferences. House Personality reads this content but does not write back to it.

Example state:

```text
Shared preferences are available. Missing facts should be treated as unknown.
```

## Event Summary Entity

Use `vision_entity` for text summaries produced by another integration or helper.

Example state:

```text
Recent event summary: motion was detected near the side gate at 8:42 PM.
```

House Personality does not analyze camera images or video.
