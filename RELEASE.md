# Release Checklist

Use this checklist before publishing a public or private test release.

## Local Validation

1. Confirm `manifest.json` and `const.py` use the same version.
2. Confirm `CHANGELOG.md` has release notes for the version.
3. Validate JSON files:

   ```bash
   uv run python -m json.tool hacs.json
   uv run python -m json.tool custom_components/house_personality/manifest.json
   uv run python -m json.tool custom_components/house_personality/strings.json
   uv run python -m json.tool custom_components/house_personality/translations/en.json
   ```

4. Run tests:

   ```bash
   uv run python -m unittest discover -s tests
   ```

5. Compile Python files:

   ```bash
   uv run python -m compileall custom_components/house_personality tests
   ```

6. Run `git diff --check`.
7. Search for private names, private entity IDs, prompts, API keys, and household-specific examples.

## Home Assistant Validation

1. Install or update through HACS custom repository.
2. Restart Home Assistant.
3. Confirm the integration loads without import errors.
4. Confirm the options form loads.
5. Confirm API key is not pre-filled in options.
6. Run a basic text Assist request.
7. Run a state query.
8. Run a safe control request.
9. Run a control-and-verify request.
10. Run a voice pipeline request if voice support is part of the release claim.
11. Download diagnostics and confirm redaction.

## GitHub Release

1. Commit release changes.
2. Push `main`.
3. Confirm the GitHub Actions validation workflow passes.
4. Create and push a matching tag, for example:

   ```bash
   git tag v0.2.2
   git push origin v0.2.2
   ```

5. Create a GitHub Release from the tag.
6. Refresh HACS and confirm the displayed version matches the release tag.

## Public Release Review

- README explains installation, configuration, provider setup, privacy, limitations, troubleshooting, and roadmap.
- SECURITY.md is present.
- Issue and pull request templates are present.
- No private household data is committed.
- Optional integrations are clearly marked optional.
- No direct memory writing, camera analysis, provider fallback chains, or streaming support are claimed.
