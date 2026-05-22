# Codex Adapter Subagent Report

## Source

- Official source: `https://developers.openai.com/codex/plugins` (retrieved 2026-05-22).
- Facts used (per `research.md` Codex decision): `.codex-plugin/plugin.json` is the required entry point;
  the manifest may reference root-level `skills/`; plugins install through a local/repo marketplace and are
  cached; plugin hooks are disabled by default and require `[features].plugin_hooks = true`.
- Approved source matches `APPROVED_HOST_SOURCES["codex"]` in `schemas.py`.

## Setup decisions

- Package model: `local_marketplace_plugin`.
- Reused the existing root `skills/` surface (no duplicated SKILL.md), referenced via `"skills": "./skills/"`.
- Plugin hooks left disabled: `"features": { "plugin_hooks": false }`. No `plugin_hooks = true` / `"plugin_hooks": true` anywhere.
- Manifest is cache-safe: contains no `.env`, `*.sqlite`, `memories`, or `sessions` references; no secrets or user data.
- Did NOT create `.app.json`, `.mcp.json`, or `hooks/` (not needed for current text-only requirements; YAGNI).
- Capability prose mirrors `registry.py` Codex defaults: text supported, lifecycle_start=hook,
  lifecycle_end=not_available, boot_context_trigger=codex_plugin_hook.

## Changed Files

- `.codex-plugin/plugin.json` (created) — Codex plugin manifest, references root `./skills/`, hooks disabled.
- `.agents/plugins/marketplace.json` (created) — repo-local marketplace entry referencing the `language-tutor` plugin.
- `specs/006-agent-adapter-setup/contracts/host-setup-profiles/codex.md` (created) — host setup profile with embedded JSON contract.
- `specs/006-agent-adapter-setup/subagent-reports/codex.md` (created) — this report.

No shared `src/` files or other hosts' files were edited.

## Verification

- `load_host_setup_profile('.../codex.md').host` prints `codex` (passed).
- `pytest tests/packaging/test_codex_plugin_package.py tests/packaging/test_host_setup_profiles.py -p no:cacheprovider --no-cov -q` (passed).
- Both JSON files parse via `python -m json.tool`.
- Manual provider checks (no documented standalone Codex validator; `codex-cli 0.130.0` installed):
  - Local marketplace add (`.agents/plugins/marketplace.json`) — manual.
  - Plugin install of `language-tutor` from the marketplace — manual.
  - Codex restart/reload — manual.
  - Marketplace visibility of the installed `language-tutor` plugin — manual.

## Failures

- None.

## Blockers

- None. Note: Codex exposes no documented standalone plugin validator, so install/restart/visibility remain manual checks.
