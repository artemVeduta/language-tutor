# Host Setup Profile: Claude

> **Lifecycle superseded by spec 007** (Hook-Free Incremental Lifecycle —
> Constitution Principle IX). The capability profile for `claude` now declares
> `lifecycle_start=first_message`, `lifecycle_end=not_available`,
> `boot_context_trigger=first_tutor_message`, and
> `persistence_mode=incremental_checkpoint`. The plugin ships **no hooks**;
> boot happens on the first tutor message via `tutor session-start --json`.
> The mentions of `SessionStart`/`SessionEnd` hooks and `hooks/hooks.json`
> below are retained as historical context only and no longer reflect the
> shipped package surface.

**Host ID**: `claude`
**Schema Version**: `1`
**Owner Subagent**: `claude-adapter-subagent`
**Official Source Checked**: `2026-05-22`
**Status**: `verified`

## Official Sources

- URL: `https://docs.claude.com/en/docs/claude-code/plugins`
  - Retrieved date: `2026-05-22`
  - Source sections or headings used:
    - "Plugins" overview (self-contained plugin directory model)
    - "Plugin components" (`.claude-plugin/plugin.json` manifest, root-level `skills/`, `agents/`, `hooks/hooks.json`, `bin/`)
    - "Develop and test locally" (`claude --plugin-dir`, `/reload-plugins`)
  - Facts copied into this profile:
    - A Claude Code plugin is a self-contained directory whose entry point is the `.claude-plugin/plugin.json` manifest.
    - Root-level components are auto-discovered: `skills/<name>/SKILL.md`, `agents/*.md`, `hooks/hooks.json`, and `bin/` executables.
    - Local development loads a plugin directory with `claude --plugin-dir <plugin-root>`, then launches the interactive session with `claude`.
    - `/reload-plugins` reloads installed/loaded plugins and refreshes the plugin cache without restarting.
    - `claude plugin validate` checks manifest and component structure (run with `--strict` for the gating check).
  - Unsupported assumptions rejected:
    - Storing learner state, sessions, or SQLite inside the plugin root (plugin roots are versioned/cached package content, not persistent data).
    - Loading `CLAUDE.md` at plugin root as shipped context (docs route shipped context through skills, not the plugin-root `CLAUDE.md`).
  - Ambiguities or blockers: none affecting this profile.

## Package Model

`plugin_package`. The tutor is distributed as a self-contained Claude Code plugin
directory rooted at the repo. Claude discovers the `.claude-plugin/plugin.json`
manifest and auto-loads root-level components. This matches the existing baseline,
which is preserved unchanged; this profile documents and verifies it rather than
rebuilding it.

## Package Files

Required (baseline, preserved as-is):

- `.claude-plugin/plugin.json` — plugin manifest / entry point
- `skills/` — tutor skills (`tutor-setup`, `tutor-vocab`, `tutor-writing`, `tutor-reading`, `tutor-lesson`, `tutor-progress`)
- `hooks/hooks.json` — `SessionStart` and `SessionEnd` hook wiring
- `agents/tutor-judge.md` — judge sub-agent definition
- `bin/tutor` — tutor CLI launcher executable

Optional:

- none beyond the baseline for this profile.

## Prerequisites

- Claude Code CLI (`claude`) installed (verified: `claude --version` → `2.1.148`).
- A local checkout of this repository (the plugin root).
- `uv` available for the tutor CLI's Python runtime.
- No additional credentials or env vars are required by the plugin manifest itself; any provider API keys remain user-owned (see User-Owned Data Boundary).

## Install Flow

- From the repo root, load the plugin directory: `claude --plugin-dir <plugin-root>` (use `.` when invoked from the repo root).

## Launch Flow

- Launch the interactive session: `claude`. The `SessionStart` hook builds boot context; tutor skills and the `tutor` CLI become available in-session.

## Inspect Flow

- Confirm the plugin and its components loaded by running `/reload-plugins` inside the session and reviewing the reported plugin/component list.

## Update Or Reload Flow

- After editing plugin files, run `/reload-plugins` to refresh the loaded plugin and its cache without restarting the session.

## Remove Flow

- Loaded-via-`--plugin-dir` plugins are unloaded by ending the session (or relaunching `claude` without `--plugin-dir`). No persistent install artifact is created by the local-dir flow, so removal is the absence of the `--plugin-dir` flag. No user data is touched on removal.

## User-Owned Data Boundary

The following must never be packaged, copied, overwritten, logged, or published:

- API keys, auth tokens, credentials, and `.env` files (`secrets`)
- Learner memories and conversation sessions (`memories`, `sessions`)
- SQLite state and its sidecar files (`*.sqlite`, `*.sqlite3`, `*.db`, `*.db-wal`, `*.db-shm`)
- Logs and traces (`logs`, `*.log`)
- Generated workspaces, caches, scratch plans (`caches`, `*.cache`)
- Machine-local config and local overrides (`local`, `*.local`, `local_overrides`)

## Capability Profile

References `AdapterCapabilityProfile` defaults for `claude` (single source of truth in `src/language_tutor/adapters/registry.py`):

- Text support: `supported`
- Lifecycle start: `hook` (SessionStart)
- Lifecycle end: `hook` (SessionEnd)
- Boot context trigger: `session_start_hook`
- Setup entry point: `claude --plugin-dir <plugin-root>`
- Update behavior: `/reload-plugins`
- Optional side-effectful capabilities: none
- Unsupported capabilities: `audio`, `image`
- Flow gates: none (all six representative text flows — reading, lesson, transcript, vocab, writing, progress — are supported)

## Verification Expectations

- `claude plugin validate --strict` (host validation command)
- `tests/packaging/test_claude_plugin_package.py`
- `tests/packaging/test_host_setup_profiles.py`
- `tests/adapter_contract/test_plugin_surface.py`
- `load_host_setup_profile("specs/006-agent-adapter-setup/contracts/host-setup-profiles/claude.md")` resolves to host `claude`
- Manual provider install check recorded in the subagent report

## Known Limitations

- `claude plugin validate --strict` now passes. The three baseline schema errors (`author` string→object, `hooks.*.hooks` array shape, missing agent frontmatter) were fixed (maintainer-authorized). One benign warning remains: repo-root `CLAUDE.md` is dev instructions, not plugin context (context ships via `skills/`); it is intentionally retained.
- `audio` and `image` modalities are unsupported by the capability profile and are out of scope for representative-flow conformance.

```json
{
  "host": "claude",
  "schema_version": 1,
  "official_sources": [
    {
      "source_url": "https://docs.claude.com/en/docs/claude-code/plugins",
      "retrieved_on": "2026-05-22",
      "source_sections": [
        "Plugins overview",
        "Plugin components",
        "Develop and test locally"
      ],
      "facts_used": [
        "A Claude Code plugin is a self-contained directory whose entry point is .claude-plugin/plugin.json.",
        "Root-level skills/, agents/, hooks/hooks.json, and bin/ are auto-discovered plugin components.",
        "claude --plugin-dir <plugin-root> loads a local plugin directory; claude launches the session.",
        "/reload-plugins reloads loaded plugins and refreshes the plugin cache.",
        "claude plugin validate checks manifest and component structure (use --strict for the gating check)."
      ],
      "unsupported_assumptions": [
        "Storing learner state/sessions/SQLite inside the plugin root.",
        "Loading plugin-root CLAUDE.md as shipped context instead of a skill."
      ],
      "source_risk": "stable"
    }
  ],
  "package_model": "plugin_package",
  "package_files": [
    ".claude-plugin/plugin.json",
    "skills/",
    "hooks/hooks.json",
    "agents/tutor-judge.md",
    "bin/tutor"
  ],
  "prerequisites": [
    "Claude Code CLI (claude) installed",
    "Local checkout of this repository (the plugin root)",
    "uv available for the tutor CLI Python runtime"
  ],
  "install_flow": [
    "From the repo root, run: claude --plugin-dir <plugin-root>"
  ],
  "launch_flow": [
    "Launch the interactive session: claude"
  ],
  "inspect_flow": [
    "Inside the session, run /reload-plugins and review the reported plugin/component list"
  ],
  "update_or_reload_flow": [
    "After editing plugin files, run /reload-plugins to refresh the loaded plugin and its cache"
  ],
  "remove_flow": [
    "End the session or relaunch claude without --plugin-dir; the local-dir flow creates no persistent install artifact and touches no user data"
  ],
  "required_user_values": [],
  "user_owned_boundaries": [
    "secrets",
    "memories",
    "sessions",
    "logs",
    "local",
    "*.sqlite"
  ],
  "capability_profile_path": "schemas/host_capability_profile.schema.json",
  "verification_expectations": [
    "claude plugin validate --strict",
    "tests/packaging/test_claude_plugin_package.py",
    "tests/packaging/test_host_setup_profiles.py",
    "tests/adapter_contract/test_plugin_surface.py",
    "load_host_setup_profile resolves claude.md to host claude"
  ],
  "known_limitations": [
    "claude plugin validate --strict reports pre-existing baseline manifest/hook/agent shape findings; the baseline is preserved unchanged.",
    "audio and image modalities are unsupported and out of scope for representative-flow conformance."
  ]
}
```
