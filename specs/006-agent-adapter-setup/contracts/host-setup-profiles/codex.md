# Host Setup Profile: Codex

**Host ID**: `codex`
**Schema Version**: `1`
**Owner Subagent**: `codex-adapter-subagent`
**Official Source Checked**: `2026-05-22`
**Status**: `implemented`

## Official Sources

- URL: `https://developers.openai.com/codex/plugins`
  - Retrieved date: `2026-05-22`
  - Source sections or headings used:
    - Plugin manifest (`.codex-plugin/plugin.json`)
    - Skills and bundled components
    - Local / repo marketplace files
    - Plugin cache behavior
    - Plugin hooks gating (`[features].plugin_hooks`)
  - Facts copied into this profile:
    - `.codex-plugin/plugin.json` is the required plugin entry point.
    - The manifest can reference root-level `skills/` (reused, not duplicated).
    - Plugins are installed via a local/repo marketplace and cached under Codex's plugin cache.
    - Plugin hooks are disabled by default and require `[features].plugin_hooks = true` opt-in.
    - Installed plugins are visible in the marketplace listing after a Codex restart/reload.
  - Unsupported assumptions rejected:
    - Treating Codex as Claude-compatible without its own `.codex-plugin/plugin.json` entry point.
    - Enabling plugin hooks by default.
  - Ambiguities or blockers: The `codex` CLI (0.130.0) is installed but exposes no documented standalone
    plugin validator; install/restart/visibility are recorded as manual checks.

## Package Model

Codex uses the documented `local_marketplace_plugin` model: a `.codex-plugin/plugin.json` manifest is the
required entry point, a repo-local marketplace file exposes the plugin to Codex, and installed plugins are
cached. This implementation follows that model so the tutor reuses the existing root `skills/` surface without
duplicating skill content or shipping any user-owned data into the cached package.

## Package Files

Required:
- `.codex-plugin/plugin.json` (manifest entry point; references root `./skills/`)
- `.agents/plugins/marketplace.json` (repo-local marketplace entry referencing the plugin)
- `skills/` (reused root skills surface: tutor-setup, tutor-vocab, tutor-writing, tutor-reading, tutor-lesson, tutor-progress)

Optional (not shipped by default):
- `.app.json`, `.mcp.json`, `hooks/` (only added if a future capability requires them; hooks stay disabled by default)

## Prerequisites

- `codex` CLI installed (verified: `codex-cli 0.130.0`).
- Repo checked out locally so the repo-local marketplace path resolves.
- No credentials or env vars required to install the cache-safe plugin package.
- User approval required only if plugin hooks are later opted in via `[features].plugin_hooks`.

## Install Flow

1. From the repo root, add the repo-local marketplace (`.agents/plugins/marketplace.json`).
2. Install the `language-tutor` plugin from that marketplace.
3. Restart/reload Codex so the plugin is loaded from its cache.

## Launch Flow

1. Launch Codex.
2. The `language-tutor` plugin loads from the Codex plugin cache; root `skills/` become available.

## Inspect Flow

1. Open the Codex marketplace/plugin listing.
2. Confirm `language-tutor` appears as an installed plugin and its skills are visible.

## Update Or Reload Flow

1. Update the repo-local marketplace/plugin source.
2. Restart/reload Codex so the cached plugin is refreshed.

## Remove Flow

- Remove the `language-tutor` plugin from the Codex marketplace listing and restart Codex.
- Removal does not touch user-owned data, which is never part of the cached package.

## User-Owned Data Boundary

The cached plugin package must never include, copy, overwrite, log, or publish:
- API keys, auth tokens, credentials, and `.env` / `*.env` files
- `secrets`
- Learner `memories` and conversation `sessions`
- SQLite state and local event data: `*.sqlite`, `*.sqlite3`, `*.db`, `*.db-wal`, `*.db-shm`
- `logs`, `*.log`, traces, generated workspaces
- `caches`, `*.cache`, scratch plans
- `local`, `*.local`, `local_overrides`, and machine-local config

## Capability Profile

Reference: `AdapterCapabilityProfile` for `codex` (see `src/language_tutor/adapters/registry.py`):
- Text support: supported
- Lifecycle start: hook
- Lifecycle end: not_available
- Boot context trigger: codex_plugin_hook
- Setup entry point: local marketplace install via `.codex-plugin/plugin.json`
- Update behavior: Codex restart/reload after marketplace update
- Optional side-effectful capabilities: `plugin_hooks` (opt-in via `[features].plugin_hooks`)
- Unsupported capabilities: audio, image
- Flow gates: none (all Phase 5 text flows supported)

## Verification Expectations

- Automated: `pytest tests/packaging/test_codex_plugin_package.py` (manifest references skills, marketplace
  references the plugin, hooks disabled by default, manifest is cache-safe, root skills present).
- Automated: `pytest tests/packaging/test_host_setup_profiles.py` (this profile validates against
  `HostSetupProfileContract`).
- Manual provider checks (no documented standalone Codex validator): local marketplace add, plugin install,
  Codex restart, and marketplace visibility of `language-tutor`.

## Known Limitations

- The `codex` CLI offers no documented standalone plugin validator; install/restart/visibility are manual.
- Plugin hooks remain disabled by default; lifecycle-end is not available on Codex.

```json
{
  "host": "codex",
  "schema_version": 1,
  "official_sources": [
    {
      "source_url": "https://developers.openai.com/codex/plugins",
      "retrieved_on": "2026-05-22",
      "source_sections": [
        "Plugin manifest (.codex-plugin/plugin.json)",
        "Skills and bundled components",
        "Local/repo marketplace files",
        "Plugin cache behavior",
        "Plugin hooks gating ([features].plugin_hooks)"
      ],
      "facts_used": [
        ".codex-plugin/plugin.json is the required plugin entry point",
        "manifest can reference root-level skills/",
        "plugins install via a local/repo marketplace and are cached",
        "plugin hooks are disabled by default and require [features].plugin_hooks opt-in",
        "installed plugins are visible in the marketplace listing after a Codex restart/reload"
      ],
      "unsupported_assumptions": [
        "treating Codex as Claude-compatible without a .codex-plugin/plugin.json entry point",
        "enabling plugin hooks by default"
      ],
      "source_risk": "stable"
    }
  ],
  "package_model": "local_marketplace_plugin",
  "package_files": [
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
    "skills/"
  ],
  "prerequisites": [
    "codex CLI installed (codex-cli 0.130.0)",
    "repo checked out locally so the repo-local marketplace path resolves"
  ],
  "install_flow": [
    "add the repo-local marketplace (.agents/plugins/marketplace.json) from the repo root",
    "install the language-tutor plugin from that marketplace",
    "restart/reload Codex so the plugin loads from its cache"
  ],
  "launch_flow": [
    "launch Codex",
    "the language-tutor plugin loads from the Codex plugin cache and root skills/ become available"
  ],
  "inspect_flow": [
    "open the Codex marketplace/plugin listing",
    "confirm language-tutor appears as an installed plugin with its skills visible"
  ],
  "update_or_reload_flow": [
    "update the repo-local marketplace/plugin source",
    "restart/reload Codex so the cached plugin is refreshed"
  ],
  "remove_flow": [
    "remove the language-tutor plugin from the Codex marketplace listing and restart Codex"
  ],
  "required_user_values": [],
  "user_owned_boundaries": [
    "API keys, auth tokens, credentials, and .env/*.env files",
    "secrets",
    "learner memories and conversation sessions",
    "SQLite state: *.sqlite, *.sqlite3, *.db, *.db-wal, *.db-shm",
    "logs and *.log traces",
    "caches and *.cache scratch plans",
    "local, *.local, local_overrides, and machine-local config"
  ],
  "capability_profile_path": "schemas/host_capability_profile.schema.json",
  "verification_expectations": [
    "pytest tests/packaging/test_codex_plugin_package.py",
    "pytest tests/packaging/test_host_setup_profiles.py",
    "manual: local marketplace add, plugin install, Codex restart, marketplace visibility of language-tutor"
  ],
  "known_limitations": [
    "codex CLI offers no documented standalone plugin validator; install/restart/visibility are manual",
    "plugin hooks remain disabled by default; lifecycle-end is not available on Codex"
  ]
}
```
