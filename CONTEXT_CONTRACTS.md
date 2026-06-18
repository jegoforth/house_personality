# Context Contracts

House Personality can consume optional context from Home Assistant entities and services. These contracts define preferred generic shapes for those sources so users and companion integrations can expose useful context without coupling House Personality to a specific project.

All sources are optional. House Personality should continue working when any context source is blank, missing, stale, unknown, unavailable, or disabled.

House Personality consumes context. It does not calculate speaker identity, person location, room presence, camera analysis, durable memory, or recall results itself.

## General Contract Rules

Preferred context sources should:

- Use ordinary Home Assistant entities or services.
- Keep the entity state short and human-readable.
- Put structured metadata in attributes.
- Include a timestamp when freshness matters.
- Include confidence when the value is inferred.
- Use `unknown`, `unavailable`, or a blank value when the source cannot produce a reliable answer.
- Avoid exposing more private detail than the assistant needs.

Useful common attributes:

```yaml
state: "human readable summary"
attributes:
  updated_at: "2026-06-09T14:30:00-04:00"
  source: "template_sensor"
  confidence: 0.82
  stale_after_seconds: 300
```

Timestamp guidance:

- Use ISO 8601 strings when possible.
- Prefer local timezone offsets or UTC.
- Use `updated_at` for the source calculation time.
- Use `observed_at` for when the underlying event happened.
- Use `expires_at` when a value should be ignored after a specific time.

Confidence guidance:

- Use a numeric range from `0.0` to `1.0`.
- Omit confidence for manually maintained helpers.
- Use lower confidence for inferred location, identity, or room status.
- Treat low confidence as context, not fact.

Staleness guidance:

- Speaker identity should usually expire quickly.
- Room or location context should expire based on sensor quality.
- Memory and policy context can remain valid much longer.
- Event summaries should include when the event happened.

## Identity / Current Speaker

Purpose:

Identify the likely current speaker. This is not the assistant persona.

Preferred entity types:

- `sensor`
- `input_text`
- `select`

Example states:

```yaml
entity_id: sensor.current_speaker
state: "Guest"
attributes:
  accepted: true
  confidence: 0.76
  best_score: 0.76
  score_gap: 0.22
  updated_at: "2026-06-09T14:31:12-04:00"
  stale_after_seconds: 120
  source: "speaker_identity_provider"
```

Rejected or ambiguous identity example:

```yaml
entity_id: sensor.current_speaker
state: "unknown"
attributes:
  accepted: false
  rejection_reason: "low_score_gap"
  best_match: "Person A"
  best_score: 0.53
  second_match: "Person B"
  second_score: 0.46
  score_gap: 0.07
  updated_at: "2026-06-09T14:31:12-04:00"
  stale_after_seconds: 120
  source: "speaker_identity_provider"
```

```yaml
entity_id: input_text.current_speaker
state: "Unknown"
attributes:
  updated_at: "2026-06-09T14:31:12-04:00"
  source: "manual"
```

Recommended behavior:

- Use `Unknown` when identity is not reliable.
- If a provider emits an `accepted` attribute, set it to `true` only when the match passed the provider's confidence and margin checks.
- Preserve diagnostic candidate fields on rejected matches so thresholds and sample quality can be evaluated without injecting the identity as fact.
- Do not include private biographical details in the identity entity.
- Do not put assistant personality instructions here.
- Keep household-specific names private in the user's own Home Assistant instance.

House Personality use:

- May include the state as speaker context when the source is a simple helper.
- Should ignore rich speaker-recognition style entities when `accepted` is present and not `true`.
- May pass speaker context to optional recall lookup.
- Should not require any speaker-recognition integration.

## Person Or Room Location

Purpose:

Provide optional context about where a person or current speaker may be located.

Preferred entity types:

- `sensor`
- `device_tracker`
- `person`
- `input_text`

Example current-speaker room state:

```yaml
entity_id: sensor.current_speaker_room
state: "Kitchen"
attributes:
  person_label: "Current speaker"
  confidence: 0.68
  observed_at: "2026-06-09T14:30:55-04:00"
  updated_at: "2026-06-09T14:31:02-04:00"
  stale_after_seconds: 180
  source: "room_presence_provider"
```

Example person location state:

```yaml
entity_id: sensor.person_location_summary
state: "Person A is probably in the living room."
attributes:
  person_label: "Person A"
  area: "Living room"
  confidence: 0.72
  observed_at: "2026-06-09T14:30:55-04:00"
  stale_after_seconds: 300
```

Privacy notes:

- Location is sensitive. Avoid sending precise room or presence data to a cloud provider unless the user explicitly accepts that privacy tradeoff.
- Prefer broad labels when possible, such as `home`, `away`, `upstairs`, or `main floor`.
- Avoid exposing exact GPS coordinates, device IDs, or tracking details unless needed.

House Personality use:

- May use location as prompt context for ambiguous requests.
- Should not calculate location itself.
- Should not require Bermuda, `person`, `device_tracker`, or any specific location integration.

## Public-Space Room Status

Purpose:

Summarize room state for public or shared spaces without exposing private camera details.

Preferred entity types:

- `sensor`
- `binary_sensor`
- `input_text`
- template sensor

Example room status:

```yaml
entity_id: sensor.kitchen_room_status
state: "Kitchen appears occupied."
attributes:
  room: "Kitchen"
  occupancy: "occupied"
  confidence: 0.81
  observed_at: "2026-06-09T14:29:40-04:00"
  updated_at: "2026-06-09T14:30:00-04:00"
  stale_after_seconds: 300
  source: "presence_summary"
```

Example lower-detail state:

```yaml
entity_id: sensor.shared_space_summary
state: "Main floor shared spaces are active."
attributes:
  rooms:
    - "Kitchen"
    - "Living room"
  confidence: 0.64
  updated_at: "2026-06-09T14:30:00-04:00"
```

Privacy notes:

- Room status can reveal behavior patterns.
- Avoid raw camera labels, image descriptions, face recognition output, or exact activity details unless explicitly desired.
- Prefer public/shared-space summaries over private-room monitoring.
- Do not include images, video frames, or camera URLs.

House Personality use:

- May use public-space room status to resolve ambiguous home-control requests.
- Should not infer room status from camera feeds itself.
- Should not require LLM Vision, Frigate, or any camera integration.

## House / Profile / Policy Context

Purpose:

Provide durable home rules, assistant behavior constraints, household preferences, or policy context.

Preferred entity types:

- `input_text`
- `sensor`
- template sensor

Example state:

```yaml
entity_id: input_text.home_context
state: "Use Home Assistant state for live device status. Treat missing facts as unknown. Keep smart-home confirmations brief."
attributes:
  updated_at: "2026-06-09T10:00:00-04:00"
  source: "manual"
  stale_after_seconds: 86400
```

Example profile/policy attributes:

```yaml
entity_id: sensor.assistant_policy_context
state: "Assistant policy context is available."
attributes:
  rules:
    - "Do not invent missing facts."
    - "Use exposed Home Assistant tools for live state and control."
    - "Ask a clarifying question when a request is ambiguous."
  updated_at: "2026-06-09T10:00:00-04:00"
```

Recommended behavior:

- Keep this context generic when shared publicly.
- Store private preferences only inside the user's Home Assistant instance.
- Keep live state out of policy context; use Home Assistant tools or dedicated state summaries for live state.

House Personality use:

- May include this as configured context.
- Should not treat this as a substitute for live Home Assistant entity state.

## Read-Only Memory Entity

Purpose:

Expose durable facts, preferences, or project notes as read-only prompt context.

Preferred entity types:

- `sensor`
- `input_text`
- template sensor

Example state:

```yaml
entity_id: sensor.assistant_memory_summary
state: "Durable memory summary is available."
attributes:
  summary: "Known preferences and durable notes are available. Missing facts should be treated as unknown."
  updated_at: "2026-06-09T09:15:00-04:00"
  source: "memory_summary_provider"
  stale_after_seconds: 86400
```

Example compact memory:

```yaml
entity_id: input_text.assistant_memory_summary
state: "Prefer concise responses. Confirm smart-home actions briefly. Do not assume missing schedule details."
attributes:
  updated_at: "2026-06-09T09:15:00-04:00"
```

Privacy notes:

- Memory can contain sensitive personal details.
- Review memory summaries before sending them to a cloud provider.
- Prefer summaries over raw conversation history.
- Avoid secrets, credentials, access codes, medical details, or financial details.

House Personality use:

- Reads memory context only.
- Does not write back to this entity.
- Does not write to memory files.
- Uses separate proposal services when a user or automation wants to create reviewable memory proposals.

## Recall Service Results

Purpose:

Return relevant past conversation context for the current request.

Preferred service shape:

```yaml
service: conversation_memory.prepare_recall_context
data:
  query: "current user message"
  speaker: "optional speaker label"
  conversation_id: "optional Home Assistant conversation id"
  limit: 5
  include_turns: false
response:
  context: "Prompt-safe recall summary text."
  items:
    - title: "Short recall title"
      summary: "Relevant prior detail."
      score: 0.84
      occurred_at: "2026-06-07T18:00:00-04:00"
```

Generic response fields:

```yaml
context: "Combined prompt-safe recall text."
items:
  - summary: "Relevant prior conversation or decision."
    score: 0.82
    occurred_at: "2026-06-07T18:00:00-04:00"
    source: "conversation_recall"
```

Recommended behavior:

- Return prompt-safe summaries by default.
- Include raw turns only when explicitly enabled.
- Include relevance scores when available.
- Include occurrence timestamps when available.
- Return an empty context when nothing relevant is found.

House Personality use:

- Calls only the configured service domain and service name.
- Does not require Voice Assist Recall or any specific recall integration.
- Treats recall failures as non-fatal.
- Does not store recall results itself.

## Vision / Event Summary

Purpose:

Expose text summaries of recent camera, security, motion, or event activity.

Preferred entity types:

- `sensor`
- `input_text`
- template sensor

Example state:

```yaml
entity_id: sensor.recent_event_summary
state: "Recent event summary is available."
attributes:
  summary: "Motion was detected near the side gate at 8:42 PM."
  event_type: "motion"
  area: "Side gate"
  confidence: 0.74
  observed_at: "2026-06-09T20:42:00-04:00"
  updated_at: "2026-06-09T20:42:12-04:00"
  stale_after_seconds: 900
  source: "event_summary_provider"
```

Example low-detail public-space summary:

```yaml
entity_id: sensor.public_space_event_summary
state: "Shared-space activity was detected recently."
attributes:
  summary: "Activity was detected in a shared space within the last 10 minutes."
  confidence: 0.66
  updated_at: "2026-06-09T20:42:12-04:00"
```

Privacy notes:

- Camera-derived summaries can reveal private behavior.
- Prefer event summaries over raw image descriptions.
- Avoid names, faces, clothing, biometric attributes, license plates, and camera URLs unless explicitly needed.
- Avoid sending camera-derived context to cloud providers unless the user accepts that privacy tradeoff.

House Personality use:

- Reads text summaries only.
- Does not analyze images or video.
- Does not require LLM Vision, Frigate, or any camera integration.

## Prompt Use Guidance

Context should help the assistant answer better, but it should not override live Home Assistant state or user intent.

Recommended priority:

1. Current user message.
2. Live Home Assistant tool results.
3. Fresh identity/location/event context.
4. Durable policy/profile context.
5. Read-only memory and recall summaries.

When context conflicts with live Home Assistant tool results, the live tool result should win.

When context is stale or low-confidence, the assistant should phrase it as uncertain or ask a clarifying question.
