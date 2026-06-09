# House Personality Testing Checklist

Use this checklist before tagging a private test release or publishing the repository.

## Release Checklist

- [ ] Confirm `manifest.json` and `const.py` use the same version.
- [ ] Confirm `hacs.json` declares the intended minimum Home Assistant version.
- [ ] Run JSON validation for `hacs.json`, `manifest.json`, `strings.json`, and `translations/en.json`.
- [ ] Run Python compile checks for `custom_components/house_personality`.
- [ ] Run `uv run python -m unittest discover -s tests`.
- [ ] Run `git diff --check`.
- [ ] Search the repository for private names, entity IDs, prompts, secrets, or household-specific examples.
- [ ] Confirm the GitHub Actions validation workflow passes after pushing.
- [ ] Commit the release-readiness changes.
- [ ] Push `main`.
- [ ] Create and push a matching Git tag, such as `v0.1.2`.
- [ ] Create a GitHub Release from the tag so HACS shows the release version instead of a commit hash.
- [ ] Refresh HACS and confirm the displayed version matches the GitHub Release tag.

## Install And Load

- [ ] Install or update House Personality through HACS.
- [ ] If testing a manual install, copy the full `custom_components/house_personality` directory into Home Assistant.
- [ ] Confirm these files exist in Home Assistant:
  - [ ] `custom_components/house_personality/manifest.json`
  - [ ] `custom_components/house_personality/config_flow.py`
  - [ ] `custom_components/house_personality/strings.json`
  - [ ] `custom_components/house_personality/translations/en.json`
- [ ] Restart Home Assistant.
- [ ] Confirm Home Assistant logs show `Setting up house_personality.conversation`.
- [ ] Confirm no import errors are logged.

## Config Flow

- [ ] Add House Personality from **Settings > Devices & services**.
- [ ] Configure assistant display name.
- [ ] Configure provider base URL.
- [ ] Configure API key if required by the provider.
- [ ] Configure model, temperature, and timeout.
- [ ] Leave maximum response tokens at `0` for provider default behavior.
- [ ] Leave provider tools enabled for normal Assist state queries and control.
- [ ] Leave tool choice set to `auto`.
- [ ] Leave parallel tool calls disabled.
- [ ] Leave response format set to `default`.
- [ ] Configure a personality prompt.
- [ ] Leave optional context, identity, memory, and vision entities blank.
- [ ] Submit successfully with optional entity fields blank.

## Options Flow

- [ ] Open House Personality options from the integration entry.
- [ ] Update provider or personality settings.
- [ ] Confirm the API key field is blank by default.
- [ ] Submit with the API key field blank and confirm the existing key still works.
- [ ] Enter a new API key only when intentionally rotating the provider key.
- [ ] Change maximum response tokens to a small value and confirm responses are capped or shortened by the provider.
- [ ] Return maximum response tokens to `0`.
- [ ] Disable provider tools and confirm non-control conversation still works.
- [ ] With provider tools disabled, ask for live entity state and confirm the assistant says tools are disabled instead of guessing.
- [ ] With provider tools disabled, ask for device control and confirm no action is performed and the assistant says tools are disabled.
- [ ] Re-enable provider tools and confirm state queries or control work again.
- [ ] Set `tool_choice` to `none` and confirm live state/control requests are refused instead of guessed.
- [ ] Set `tool_choice` back to `auto`.
- [ ] Confirm `tool_choice=auto`, `parallel_tool_calls=false`, and `response_format=default` work with the primary provider.
- [ ] Set `context_entity` to a helper or sensor with generic home context.
- [ ] Leave `identity_entity` blank unless a reliable speaker identity source exists.
- [ ] Set `memory_entity` to a read-only memory summary helper or sensor.
- [ ] Enable or disable recall.
- [ ] Enable or disable vision/event summary context.
- [ ] Submit successfully.

## Text Assist

- [ ] Select House Personality as the Assist conversation agent.
- [ ] Ask a non-control request, such as `Say hello in one short sentence.`
- [ ] Confirm a provider response is returned.
- [ ] Ask a follow-up that depends on the previous turn.
- [ ] Confirm same-conversation context is preserved.

## Home Control

Use an entity that is exposed to Assist and safe to toggle during testing.

- [ ] Ask for current state, such as `Is the test light on?`
- [ ] Ask to turn the entity on.
- [ ] Confirm the physical or HA entity state changes.
- [ ] Ask a follow-up using a pronoun, such as `Turn it off.`
- [ ] Confirm the correct entity changes.
- [ ] Ask `Turn it on and verify it is on.`
- [ ] Confirm the response waits for state to settle and reports the correct result.

Expected debug log examples:

```text
House Personality Assist LLM API status: enabled=True tools=...
House Personality provider requested ... tool call(s)...
House Personality executed ... Home Assistant tool result(s)
House Personality waiting 1.0s for Home Assistant state to settle after mutating tool call
```

## Voice Assist Pipeline

- [ ] Create or select an Assist pipeline using House Personality as the conversation agent.
- [ ] Configure speech-to-text.
- [ ] Configure text-to-speech.
- [ ] Ask a short non-control question.
- [ ] Confirm STT, provider response, and TTS all complete.
- [ ] Ask a safe home-control request.
- [ ] Confirm the action is completed.

## Context And Memory

- [ ] Configure `context_entity` with generic home context.
- [ ] Ask a question that should use that context.
- [ ] Confirm the response uses the context without inventing unsupported facts.
- [ ] Configure `memory_entity` with a read-only memory summary.
- [ ] Ask a question that should use memory.
- [ ] Confirm memory is included only when relevant.
- [ ] Remove or clear the memory entity.
- [ ] Confirm conversation still works without memory.

## Identity

- [ ] Leave `identity_entity` blank and confirm conversation still works.
- [ ] Configure an identity entity whose state is a speaker label, such as `Guest` or `Unknown`.
- [ ] Ask a question that should adapt to the speaker.
- [ ] Confirm the assistant does not guess identity when the entity is missing, blank, `unknown`, or `unavailable`.

## Recall

- [ ] Leave recall disabled and confirm conversation works.
- [ ] Enable recall with a valid service domain and service name.
- [ ] Ask a question that should retrieve prior conversation context.
- [ ] Confirm recall content is included when available.
- [ ] Temporarily configure an invalid recall service.
- [ ] Confirm recall failure does not break conversation.

## Vision/Event Summary

- [ ] Leave vision/event summary disabled and confirm conversation works.
- [ ] Enable vision/event summary with a text helper or summary sensor.
- [ ] Ask a question about recent events.
- [ ] Confirm the assistant uses only the text summary.
- [ ] Confirm House Personality does not analyze camera images or video.

## Provider Failure Handling

- [ ] Temporarily configure an invalid model or provider URL.
- [ ] Ask a simple request.
- [ ] Confirm the assistant returns the friendly provider error.
- [ ] Confirm logs include useful technical detail without API keys.
- [ ] If a provider rejects tool schemas, disable provider tools and confirm simple non-control conversation works.
- [ ] If a provider rejects `response_format`, set response format back to `default`.
- [ ] If parallel tool calls cause stale verification, leave `parallel_tool_calls` disabled.

## Diagnostics And Privacy

- [ ] Download diagnostics from the integration entry.
- [ ] Confirm API key is redacted.
- [ ] Confirm API key is not exposed by reopening the options flow.
- [ ] Confirm configured context, identity, memory, and vision entity IDs are redacted.
- [ ] Confirm no private names, entity IDs, prompts, or household details are committed to the repository.
- [ ] Search the repository for private test data before release.

## Reload And Restart

- [ ] Reload the integration from Home Assistant if available.
- [ ] Confirm conversation still works after reload.
- [ ] Restart Home Assistant.
- [ ] Confirm the integration loads cleanly after restart.
- [ ] Confirm the configured conversation agent remains selectable in Assist.
