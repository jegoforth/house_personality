# Elspeth Private Deployment Test Plan

This document is a private deployment checklist for testing House Personality as an Elspeth conversation agent in one Home Assistant installation.

House Personality itself must remain generic. Do not add private names, private entity IDs, private prompts, household facts, or Elspeth-specific behavior to integration code. Private identity, memory, location, recall, and room-status sources should stay configurable inside Home Assistant.

## Scope

This plan tests the existing House Personality feature set only.

Do not implement or enable new native features as part of this test pass:

- native speaker recognition
- native person or room location calculation
- native camera analysis
- direct memory writes
- direct writes to `house_memory.json`
- provider fallback chains
- multiple provider profiles
- streaming responses

## Test Rules

- Start with no optional context sources configured.
- Add one optional context source at a time.
- After each change, run the same small Assist checks.
- Prefer helper or template test entities before connecting real private sources.
- Keep Home Assistant tools enabled when testing state queries and control actions.
- Keep parallel tool calls disabled unless explicitly testing them.
- Do not expose raw camera images, raw GPS coordinates, or private-room summaries.
- Do not log API keys or full prompts.

## Loggers To Check

Check Home Assistant logs after each stage:

```text
custom_components.house_personality
custom_components.house_personality.conversation
custom_components.house_personality.providers.openai_compatible
custom_components.house_personality.context.entity_context
custom_components.house_personality.identity.entity_identity
custom_components.house_personality.memory.entity_memory
custom_components.house_personality.memory.recall_adapter
custom_components.house_personality.location.entity_location
custom_components.house_personality.room_status.entity_room_status
custom_components.house_personality.vision.entity_vision
```

Expected log behavior:

- Provider failures are summarized without stack traces in the Assist response.
- API keys are never logged.
- Full prompts are not logged by default.
- Optional missing context sources are skipped gracefully.
- Included/skipped context sections are visible when debug logging is enabled.

## Rollback Steps

Use these rollback steps after any failed stage:

1. Open **Settings > Devices & services > House Personality > Configure**.
2. Clear only the option added in the failed stage.
3. Disable the matching feature toggle when one exists.
4. Submit the options form.
5. Start a fresh Assist conversation.
6. Re-run the last known good plain text, state query, and control tests.

If the provider itself fails:

1. Run `house_personality.test_provider`.
2. Confirm provider base URL, model, and API key.
3. Increase timeout if the provider is slow.
4. Leave optional context sources disabled until provider connectivity is stable.

If Home Assistant tool control fails:

1. Confirm the target entity is exposed to Assist.
2. Confirm **Use Home Assistant tools** is enabled.
3. Keep `tool_choice` set to `auto`.
4. Keep `parallel_tool_calls` disabled.
5. Test a simpler state query before another control action.

## Stage 1: Confirm Version And Load

Goal: Confirm Home Assistant has loaded the expected House Personality release.

Checklist:

1. Open **Settings > Devices & services**.
2. Open the House Personality integration.
3. Confirm the installed version is `v0.3.1` or newer.
4. Confirm the integration has one configured conversation agent.
5. Confirm the agent is selectable in an Assist pipeline.

Expected result:

- House Personality loads without repair issues.
- The configured assistant appears as a conversation agent.
- The integration logs do not show import errors.

Rollback:

- If the version is older than expected, refresh HACS and upgrade House Personality.
- If the integration does not load, disable optional sources and restart only through the normal Home Assistant UI workflow.

## Stage 2: Run Provider Test Service

Goal: Confirm provider connectivity without Home Assistant tools or context sources.

Run this action:

```yaml
action: house_personality.test_provider
data:
  message: "Reply with exactly: ok"
```

Expected result:

```yaml
success: true
model: "<configured model>"
base_url: "<configured base URL>"
latency_ms: 0
response: "ok"
```

`latency_ms` should be a real positive number. Exact casing or punctuation in `response` may vary slightly by provider.

Failure result:

```yaml
success: false
error: "<friendly provider error>"
```

Rollback:

- Fix provider settings before continuing.
- Do not add context sources until this passes.

## Stage 3: Plain Text Assist Conversation

Goal: Confirm basic text conversation works with no optional context.

Options:

- `context_entity`: blank
- `identity_entity`: blank
- `memory_entity`: blank
- `recall_enabled`: off
- `location_entity`: blank
- `room_status_entity`: blank
- `vision_enabled`: off

Assist prompts:

```text
Say hello in one sentence.
```

```text
What can you help with in two short sentences?
```

Expected result:

- The assistant responds naturally.
- No optional context is referenced.
- No provider error appears.

Rollback:

- Re-run `house_personality.test_provider`.
- Confirm the Assist pipeline uses the House Personality agent.

## Stage 4: Safe Home Assistant State Query

Goal: Confirm Home Assistant Assist tools can read exposed entity state.

Use a harmless exposed entity such as a light, switch, sensor, or binary sensor.

Assist prompt:

```text
Is the test light on?
```

Expected result:

- The assistant answers based on the real Home Assistant entity state.
- The response should not invent a state.
- Logs should show provider/tool activity when debug logging is enabled.

Rollback:

- Confirm the entity is exposed to Assist.
- Confirm **Use Home Assistant tools** is enabled.
- Confirm `tool_choice` is `auto`.

## Stage 5: Safe Home Assistant Control Action

Goal: Confirm Assist tool control works on a low-risk entity.

Use a harmless exposed entity such as a test light or non-critical switch.

Assist prompts:

```text
Turn on the test light.
```

```text
Turn off the test light.
```

Optional verification prompt after a short delay:

```text
Verify the test light state.
```

Expected result:

- The entity changes state.
- The assistant confirms the action briefly.
- Verification should match the actual Home Assistant state.

Known behavior:

- Some devices report state a moment after the action. If verification is requested in the same prompt, the assistant may check too quickly.

Rollback:

- Turn the test entity back to its original state through the normal Home Assistant UI.
- Keep parallel tool calls disabled for routine testing.

## Stage 6: Add `context_entity` With A Helper First

Goal: Confirm broad home context can be included from a simple helper before using real private context.

Create or use a text helper with generic test content, for example:

```text
Private deployment test context. Use Home Assistant state for live device status. Do not invent missing facts.
```

Configure:

```text
context_entity: <test helper entity>
```

Assist prompts:

```text
What private deployment context do you have?
```

```text
Is the test light on?
```

Expected result:

- The assistant can summarize the helper context.
- State queries still use Home Assistant tools.
- The helper context does not override live entity state.

Rollback:

- Clear `context_entity`.
- Confirm plain text and state query tests still pass.

## Stage 7: Add `identity_entity` With A Helper First

Goal: Confirm current-speaker context can be included from a helper without requiring Speaker Recognition.

Create or use a text helper with a generic identity value:

```text
Test Speaker
```

Configure:

```text
identity_entity: <test helper entity>
```

Assist prompts:

```text
Who do you think is speaking?
```

```text
Say hello to the current speaker in one sentence.
```

Expected result:

- The assistant uses the helper identity as current speaker context.
- If the helper is blank, `unknown`, or unavailable, conversation still works.
- The assistant persona is not stored in `identity_entity`.

Rollback:

- Clear `identity_entity`.
- Re-run plain text conversation.

## Stage 8: Add `memory_entity` With A Helper First

Goal: Confirm read-only memory context works before connecting real memory summaries.

Create or use a text helper with generic memory test content:

```text
Test memory: the preferred test response style is concise. Do not treat missing facts as known.
```

Configure:

```text
memory_entity: <test helper entity>
```

Assist prompts:

```text
What memory context do you have?
```

```text
Answer in the preferred test response style.
```

Expected result:

- The assistant can use the helper memory summary.
- House Personality does not write to the helper.
- No memory proposal is required for this stage.

Rollback:

- Clear `memory_entity`.
- Confirm conversation still works without memory.

## Stage 9: Add Recall Service After Basic Memory Works

Goal: Confirm recall can add read-only relevant conversation context after entity memory is stable.

Prerequisites:

- Stage 8 passed.
- The recall service exists and returns prompt-safe text.

Configure:

```text
recall_enabled: on
recall_service_domain: conversation_memory
recall_service_name: prepare_recall_context
recall_limit: 5
recall_include_turns: off
```

Assist prompts:

```text
What relevant recall context do you have for this conversation?
```

```text
Use any relevant memory or recall, but do not invent missing facts.
```

Expected result:

- Recall context is included only when the service returns relevant text.
- Recall failures do not block conversation.
- Entity memory still works when recall returns no results.

Rollback:

- Turn `recall_enabled` off.
- Leave `memory_entity` enabled only if Stage 8 remains stable.

## Stage 10: Add `location_entity` With A Helper Or Template First

Goal: Confirm person or room location context works before connecting real location sources.

Create a helper or template sensor with generic state and attributes like:

```yaml
state: Kitchen
attributes:
  person_label: Test Person
  home_state: home
  room: Kitchen
  area: Kitchen
  confidence: 0.78
  updated_at: "2026-06-09T15:30:00-04:00"
  stale_after_seconds: 300
```

Configure:

```text
location_entity: <test helper or template entity>
```

Assist prompts:

```text
What location context do you have?
```

```text
What room is the current person in?
```

Expected result:

- The assistant can use current room or area context.
- Raw GPS fields are not needed.
- Stale, unknown, or unavailable location is skipped gracefully.

Rollback:

- Clear `location_entity`.
- Confirm identity and memory tests still pass.

## Stage 11: Add `room_status_entity` With A Helper Or Template First

Goal: Confirm public-space room status context works before connecting camera-derived or real room summary sources.

Create a helper or template sensor with generic state and attributes like:

```yaml
state: Kitchen appears occupied.
attributes:
  summary: Kitchen appears occupied.
  room: Kitchen
  occupancy: occupied
  confidence: 0.81
  public_space: true
  updated_at: "2026-06-10T09:30:00-04:00"
  stale_after_seconds: 300
```

Configure:

```text
room_status_entity: <test helper or template entity>
```

Assist prompts:

```text
What room status context do you have?
```

```text
Does the public test room appear occupied?
```

Expected result:

- The assistant includes public-space room status when `public_space` is true or absent.
- The assistant skips room status when `public_space` is explicitly false.
- The assistant treats room status as context, not proof.

Rollback:

- Clear `room_status_entity`.
- Confirm previous stages still pass.

## Stage 12: Connect Real Elspeth Sources One At A Time

Only begin this stage after all helper/template stages pass.

Replace helper sources one at a time with private Elspeth deployment sources. Do not replace everything at once.

Suggested order:

1. Replace memory helper with `sensor.house_memory_summary`.
2. Replace identity helper with the Speaker Recognition identity entity.
3. Enable the Voice Assist Recall service.
4. Replace location helper/template with the Bermuda/location template.
5. Replace room-status helper/template with the LLM Vision or room-status summary entity.

After each replacement, run:

```text
Say hello in one sentence.
```

```text
What context do you have right now?
```

```text
Is the test light on?
```

```text
Turn the test light on, then I will verify it separately.
```

Expected result:

- Each real source adds useful context without breaking provider calls.
- The assistant does not invent missing facts.
- State queries and control actions continue to use Home Assistant tools.
- Private source content remains configurable in Home Assistant, not code.

Rollback:

- If a real source causes bad responses, replace only that source with the last working helper.
- Keep all earlier passing sources unchanged.
- Disable recall first if responses become overly long or stale.

## Final Acceptance Checklist

- [ ] House Personality version is `v0.3.1` or newer.
- [ ] `house_personality.test_provider` passes.
- [ ] Plain text Assist conversation passes with no optional context.
- [ ] Safe state query passes.
- [ ] Safe control action passes.
- [ ] Helper `context_entity` passes.
- [ ] Helper `identity_entity` passes.
- [ ] Helper `memory_entity` passes.
- [ ] Recall service passes after helper memory works.
- [ ] Helper/template `location_entity` passes.
- [ ] Helper/template `room_status_entity` passes.
- [ ] Real memory summary source passes.
- [ ] Real speaker identity source passes.
- [ ] Real recall source passes.
- [ ] Real location template passes.
- [ ] Real room-status summary source passes.
- [ ] Logs show no API keys or full prompts.
- [ ] No private configuration has been committed to code.

## Troubleshooting

### Provider test fails

- Confirm base URL points to an OpenAI-compatible `/chat/completions` endpoint.
- Confirm API key is valid.
- Confirm model name exists for the provider.
- Increase timeout.
- Disable optional context and retry.

### Assist says it cannot control the home

- Confirm the House Personality agent is selected in the Assist pipeline.
- Confirm **Use Home Assistant tools** is enabled.
- Confirm the target entity is exposed to Assist.
- Confirm the provider/model supports OpenAI-compatible tool calls.

### State query is wrong

- Ask for a direct state query first.
- Confirm the entity is exposed to Assist.
- Check whether optional context is stale or contradicting live Home Assistant state.
- Temporarily clear context, memory, recall, location, and room-status sources.

### Control action succeeds but verification is wrong

- Wait a few seconds and ask for verification again.
- Keep parallel tool calls disabled.
- Avoid combining action and verification in the same test until the device's state reporting delay is understood.

### Context appears when it should not

- Check which optional entities are configured.
- Clear the most recently added entity first.
- Confirm room status is marked `public_space: false` when it should be suppressed.
- Confirm stale timestamps and `stale_after_seconds` are valid.

### Responses become too personal or too specific

- Review the configured personality prompt and context helpers in Home Assistant.
- Remove private details from helper text if they are not needed for the test.
- Disable recall while narrowing the source of the detail.
- Keep public repository docs and code generic.
