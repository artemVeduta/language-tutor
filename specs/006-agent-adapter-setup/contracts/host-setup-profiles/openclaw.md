# Host Setup Profile: OpenClaw

**Host ID**: `openclaw`
**Schema Version**: `1`
**Owner Subagent**: `openclaw-adapter-subagent`
**Official Source Checked**: `2026-05-22`
**Status**: `implemented`

## Official Sources

- URL: `https://docs.openclaw.ai/plugins`
  - Retrieved date: `2026-05-22`
  - Source sections used: `Building plugins`, `Plugin package layout`, `SDK entry points`, `Registering tools`, `Verification & publishing (ClawHub)`
  - Facts copied into this profile:
    - OpenClaw plugins are Node `>=22`, TypeScript ESM packages.
    - Package layout requires `package.json` (`"type": "module"`) and an `openclaw.plugin.json` manifest, with a TypeScript entry under `src/`.
    - Entry points use `definePluginEntry` (or `defineChannelPluginEntry`) and register tools via `api.registerTool`.
    - SDK is imported through focused subpaths (`openclaw/plugin-sdk/<subpath>`), not a whole-SDK wildcard import.
    - Side-effectful or binary-dependent tools are opt-in (`{ optional: true }`) and gated behind a user allowlist.
    - Verification uses package-metadata checks, manifest validation, type checks (`pnpm check`), tests, and ClawHub dry-run/publish/install flows.
  - Unsupported assumptions rejected:
    - Python-only OpenClaw package (rejected: model is Node/TypeScript with SDK entry points).
    - Required side-effectful tools (rejected: side-effectful tools are documented as opt-in).
  - Ambiguities or blockers: `clawhub` CLI is not installed in this environment, so the ClawHub publish dry-run is blocked and recorded as a manual provider step.

## Package Model

OpenClaw uses a documented `plugin_package` model: a Node `>=22` TypeScript ESM
package with a `package.json` and an `openclaw.plugin.json` manifest, whose entry
point registers tools through the OpenClaw plugin SDK. The implementation follows
this model directly under `openclaw-plugin/`.

## Package Files

Required:

- `openclaw-plugin/package.json` (`"type": "module"`, `engines.node >=22`)
- `openclaw-plugin/openclaw.plugin.json` (plugin manifest)
- `openclaw-plugin/src/index.ts` (entry; `definePluginEntry` + `api.registerTool`)

Optional:

- `openclaw-plugin/tsconfig.json` (NodeNext ESM type-check config)

## Prerequisites

- Node.js `>=22`
- `pnpm` (used for `pnpm check` / install in OpenClaw docs)
- OpenClaw runtime with the plugin SDK available as a peer dependency
- `clawhub` CLI for publish/install via ClawHub (optional; manual provider step)
- No credentials or env vars are required to build or type-check the package.

## Install Flow

- `openclaw plugins install <package-name>` (host-supported install)
- For local development: build with `pnpm build` then load the package directory
  through the OpenClaw plugin loader.

## Launch Flow

- After install, the tutor activates on the first tutor message (lifecycle start
  = `first_message`); the boot-context tool assembles learner context on that
  first message. No SessionStart-style hook is used.

## Inspect Flow

- Confirm the manifest validates and the package metadata is correct.
- `pnpm check` (TypeScript `tsc --noEmit`) confirms the ESM entry type-checks.
- Confirm the registered tools (`language_tutor.boot_context`,
  `language_tutor.text_exercise`, opt-in `language_tutor.run_cli`) appear in the
  host's plugin/tool listing.

## Update Or Reload Flow

- Reinstall/upgrade the plugin package (`openclaw plugins install <package-name>`
  at a newer version), then reload the OpenClaw plugin.

## Remove Flow

- Remove the plugin via the OpenClaw plugin manager / uninstall the package.
- Removal only deletes packaged plugin files; user-owned data lives outside the
  package and is untouched.

## User-Owned Data Boundary

The package must never include, copy, overwrite, log, or publish:

- API keys, auth tokens, credentials, and `.env` files
- Learner memories and conversation sessions
- SQLite state and `*.sqlite` / `*.db` files, WAL/SHM, and local event data
- Logs, traces, generated workspaces, caches, and scratch plans
- Machine-local config and local overrides (`local`)

## Capability Profile

Matches `src/language_tutor/adapters/registry.py` OpenClaw defaults:

- Text support: `supported`
- Lifecycle start: `first_message`
- Lifecycle end: `not_available`
- Boot context trigger: `first_tutor_message`
- Setup entry point: `openclaw plugins install <package-name>`
- Update behavior: reinstall/upgrade plugin package
- Optional side-effectful capabilities: binary-dependent tools (opt-in via user allowlist)
- Unsupported capabilities: `audio`, `image`
- Flow gates: none (all six text flows supported)

## Verification Expectations

- `pytest tests/packaging/test_openclaw_plugin_package.py` (ESM, manifest, entry, privacy)
- `pytest tests/packaging/test_host_setup_profiles.py` (profile contract validates)
- `pytest tests/packaging/test_distribution_privacy.py` (no user-owned data packaged)
- `pnpm check` (TypeScript ESM type-check) — requires the OpenClaw SDK peer dependency present
- ClawHub dry-run / publish / install verification (manual provider step; blocked here because `clawhub` is not installed)

## Known Limitations

- `clawhub` CLI is not installed in this environment, so the ClawHub publish
  dry-run is a manual provider step and is currently blocked.
- `pnpm check` cannot resolve the `openclaw` SDK peer dependency until the
  OpenClaw runtime/SDK is installed; type-checking against real SDK types is a
  manual provider step.
- OpenClaw exposes no SessionEnd-style lifecycle hook (`lifecycle_end =
  not_available`), so end-of-session work must be triggered explicitly by a flow.

```json
{
  "host": "openclaw",
  "schema_version": 1,
  "official_sources": [
    {
      "source_url": "https://docs.openclaw.ai/plugins",
      "retrieved_on": "2026-05-22",
      "source_sections": [
        "Building plugins",
        "Plugin package layout",
        "SDK entry points",
        "Registering tools",
        "Verification & publishing (ClawHub)"
      ],
      "facts_used": [
        "OpenClaw plugins are Node >=22 TypeScript ESM packages",
        "Package requires package.json (type=module) and openclaw.plugin.json manifest",
        "Entry points use definePluginEntry or defineChannelPluginEntry and register tools via api.registerTool",
        "SDK imported via focused subpaths openclaw/plugin-sdk/<subpath>, not whole-SDK wildcard",
        "Side-effectful or binary-dependent tools are opt-in via { optional: true } and user allowlist",
        "Verification uses package-metadata checks, manifest validation, pnpm check, tests, and ClawHub dry-run/publish/install"
      ],
      "unsupported_assumptions": [
        "Python-only OpenClaw package",
        "Required (non-optional) side-effectful tools"
      ],
      "source_risk": "stable"
    }
  ],
  "package_model": "plugin_package",
  "package_files": [
    "openclaw-plugin/package.json",
    "openclaw-plugin/openclaw.plugin.json",
    "openclaw-plugin/src/index.ts",
    "openclaw-plugin/tsconfig.json"
  ],
  "prerequisites": [
    "Node.js >=22",
    "pnpm",
    "OpenClaw runtime with plugin SDK peer dependency",
    "clawhub CLI for ClawHub publish/install (optional, manual provider step)"
  ],
  "install_flow": [
    "openclaw plugins install <package-name>",
    "For local development: pnpm build, then load the package directory via the OpenClaw plugin loader"
  ],
  "launch_flow": [
    "Tutor activates on the first tutor message (lifecycle start = first_message)",
    "Boot-context tool assembles learner context on that first message; no SessionStart hook"
  ],
  "inspect_flow": [
    "Validate openclaw.plugin.json manifest and package metadata",
    "pnpm check (tsc --noEmit) confirms the ESM entry type-checks",
    "Confirm registered tools appear in the host plugin/tool listing"
  ],
  "update_or_reload_flow": [
    "Reinstall/upgrade the plugin package via openclaw plugins install <package-name>",
    "Reload the OpenClaw plugin"
  ],
  "remove_flow": [
    "Remove/uninstall the plugin via the OpenClaw plugin manager",
    "Removal deletes only packaged plugin files; user-owned data outside the package is untouched"
  ],
  "required_user_values": [],
  "user_owned_boundaries": [
    "API keys, auth tokens, credentials, and .env files (secrets)",
    "learner memories",
    "conversation sessions",
    "SQLite state and *.sqlite / *.db files, WAL/SHM, local event data",
    "logs, traces, generated workspaces, caches, scratch plans",
    "machine-local config and local overrides (local)"
  ],
  "capability_profile_path": "schemas/host_capability_profile.schema.json",
  "verification_expectations": [
    "pytest tests/packaging/test_openclaw_plugin_package.py",
    "pytest tests/packaging/test_host_setup_profiles.py",
    "pytest tests/packaging/test_distribution_privacy.py",
    "pnpm check (TypeScript ESM type-check; requires OpenClaw SDK peer dependency)",
    "ClawHub dry-run/publish/install verification (manual provider step; blocked because clawhub is not installed)"
  ],
  "known_limitations": [
    "clawhub CLI not installed; ClawHub publish dry-run blocked (manual provider step)",
    "pnpm check cannot resolve the openclaw SDK peer dependency until the OpenClaw runtime/SDK is installed",
    "OpenClaw exposes no SessionEnd-style hook (lifecycle_end = not_available)"
  ]
}
```
