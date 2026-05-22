# OpenClaw Adapter Subagent Report

## Source

- Official source: `https://docs.openclaw.ai/plugins` (approved; retrieved `2026-05-22`).
- Backed by `specs/006-agent-adapter-setup/research.md` (OpenClaw decision: plugin
  package model, Node >=22 TypeScript ESM, `package.json` + `openclaw.plugin.json`,
  focused SDK subpath imports, `definePluginEntry`/`defineChannelPluginEntry`,
  `api.registerTool`, opt-in side-effectful tools, ClawHub verification).
- Source sections used: Building plugins, Plugin package layout, SDK entry points,
  Registering tools, Verification & publishing (ClawHub).
- No live web fetch performed; research.md is the source-of-truth per task scope.

## Setup decisions

- Implemented `openclaw-plugin/` as a `plugin_package`: ESM `package.json`
  (`"type":"module"`, `engines.node >=22`, name `@language-tutor/openclaw-plugin`),
  `openclaw.plugin.json` manifest, and `src/index.ts` entry.
- Entry uses focused SDK subpath imports (`openclaw/plugin-sdk/entry`,
  `.../tools`, `.../types`) — no whole-SDK wildcard import — and registers tools
  via `api.registerTool` inside a `definePluginEntry` entry.
- Three tools: `language_tutor.boot_context` and `language_tutor.text_exercise`
  (text-only, no side effects), and `language_tutor.run_cli` marked
  `optional: true` (binary-dependent / side-effectful, opt-in via user allowlist).
- Capability values match `registry.py` OpenClaw defaults: text supported,
  lifecycle_start=first_message, lifecycle_end=not_available,
  boot_context_trigger=first_tutor_message,
  setup_entry_point=`openclaw plugins install <package-name>`.
- Added `tsconfig.json` (NodeNext ESM, strict) so `pnpm check` is meaningful.
- No user-owned data placed in `openclaw-plugin/` (no `.env`, `*.sqlite`/`.db`, logs).

## Changed Files

- `openclaw-plugin/package.json` (new)
- `openclaw-plugin/openclaw.plugin.json` (new)
- `openclaw-plugin/src/index.ts` (new)
- `openclaw-plugin/tsconfig.json` (new)
- `specs/006-agent-adapter-setup/contracts/host-setup-profiles/openclaw.md` (new)
- `specs/006-agent-adapter-setup/subagent-reports/openclaw.md` (new, this file)

## Verification

- Profile loader:
  `rtk uv run python -c "from language_tutor.adapters.base import load_host_setup_profile; print(load_host_setup_profile('specs/006-agent-adapter-setup/contracts/host-setup-profiles/openclaw.md').host)"`
  → prints `openclaw`.
- `rtk uv run pytest tests/packaging/test_openclaw_plugin_package.py tests/packaging/test_host_setup_profiles.py -p no:cacheprovider --no-cov -q`
  → `20 passed, 1 skipped` (the skip is a not-yet-present sibling host profile).
- `node --version` → `v25.6.1` (satisfies Node >=22).
- `pnpm --version` available; `pnpm check` (run inside `openclaw-plugin/`) executes
  the `check` script but fails at `tsc: command not found` (no `node_modules`; the
  OpenClaw SDK peer dependency is not installable in this environment). Recorded as
  a blocker, not a code defect.

## Failures

- None in owned scope. `pnpm check` cannot complete type-checking due to missing
  `tsc`/SDK peer dependency (see Blockers); this is environmental.

## Blockers

- `clawhub` is NOT installed → ClawHub publish dry-run is BLOCKED (manual provider step).
- `tsc` / OpenClaw SDK peer dependency not available → `pnpm check` cannot type-check
  against real SDK types here; this is a manual provider step once the OpenClaw
  runtime/SDK is installed.
