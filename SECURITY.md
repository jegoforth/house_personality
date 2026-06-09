# Security Policy

## Supported Versions

House Personality is currently in private/public-test readiness. Security fixes should target the latest tagged release and `main`.

## Reporting A Vulnerability

Please open a private security advisory or contact the repository maintainer if GitHub advisories are not available.

Do not include API keys, private prompts, private entity IDs, addresses, names, camera details, or household-specific memory in public issues.

## Sensitive Data

House Personality may send these values to the configured language model provider:

- the current Assist message
- the configured personality prompt
- configured context entity content
- configured identity entity content
- configured read-only memory entity content
- optional Voice Assist Recall context
- optional vision/event summary entity content
- Home Assistant Assist tool definitions and tool results when tools are enabled

The integration does not intentionally log API keys, full prompts, full memory content, or full provider responses. Diagnostics redact API keys and configured private entity IDs.

## User Responsibilities

- Review provider privacy policies before using a cloud provider.
- Use a local provider if household context should not leave the local network.
- Keep API keys out of issues, logs, screenshots, and shared diagnostics.
- Avoid putting private household details in public example configuration.
- Expose only safe Home Assistant entities to Assist.
