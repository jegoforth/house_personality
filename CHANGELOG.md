# Changelog

## Unreleased

- Added local Home Assistant brand icon PNG assets generated from the source SVG.
- Added optional generic location entity context with stale-context handling and GPS field filtering.
- Added lightweight unit tests for prompt assembly, provider payload construction, diagnostics redaction, and no-tools conversation policy.
- Added GitHub Actions validation for JSON files, unit tests, Python compilation, and private-data scanning.
- Added GitHub issue and pull request templates.
- Added public-release readiness docs, examples, security guidance, release checklist, known limitations, and community post draft.

## v0.2.2 - Tool Choice None Behavior

- Treat `tool_choice=none` as an effective no-tools mode.
- Prevent live state or home-control claims when `tool_choice=none` is selected.
- Document that parallel tool calls may cause stale verification and should remain disabled unless tested.

## v0.2.1 - Provider Tools Disabled Behavior

- Added explicit prompt instructions for the tools-disabled mode.
- Prevented the assistant from claiming live Home Assistant checks or actions when provider tools are disabled.

## v0.2.0 - Provider Configuration

- Added single-profile provider tuning for maximum response tokens.
- Added a provider tool-use switch for compatibility with providers that reject tool schemas.
- Added configurable OpenAI-compatible tool choice.
- Added configurable parallel tool-call behavior.
- Added configurable OpenAI-compatible response format.
- Documented provider compatibility guidance.

## v0.1.2 - Private Test Release

- Added HACS-compatible release metadata and confirmed GitHub release-based version display.
- Hid existing API keys in the options flow; leaving the field blank preserves the stored key.
- Raised the minimum Home Assistant Core version to 2025.3.0 for current ConversationEntity and ChatLog API compatibility.
- Documented helper entity setup, manual testing, and privacy expectations.
- Cleaned release-facing architecture and decision notes to avoid private household examples.

## v0.1.1 - Private Test Baseline

- Added Assist tool-call support for querying and controlling exposed Home Assistant entities.
- Added optional read-only context, identity, memory, recall, and event summary inputs.
- Added memory proposal services for explicit review without direct memory writes.
- Added diagnostics with secret and configured entity redaction.

## v0.1.0 - Initial Private Baseline

- Added the HACS-friendly custom integration structure.
- Added UI configuration for an OpenAI-compatible provider and assistant personality.
- Registered House Personality as a Home Assistant Assist conversation agent.
- Added basic provider request handling, prompt assembly, friendly provider failures, and README documentation.
