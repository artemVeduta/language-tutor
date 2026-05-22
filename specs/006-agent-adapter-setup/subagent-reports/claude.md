# Claude Host Adapter Subagent Report

## Source

- Approved official source: `https://docs.claude.com/en/docs/claude-code/plugins` (retrieved `2026-05-22`).
- Sections used: Plugins overview, Plugin components, Develop and test locally.
- Facts used: self-contained plugin directory with `.claude-plugin/plugin.json` entry point; auto-discovered root-level `skills/`, `agents/`, `hooks/hooks.json`, `bin/`; local load via `claude --plugin-dir <plugin-root>`; launch via `claude`; reload/cache refresh via `/reload-plugins`; validation via `claude plugin validate` (`--strict` for the gate).
- Rejected assumptions: storing learner state/sessions/SQLite in the plugin root; loading plugin-root `CLAUDE.md` as shipped context.

## Setup decisions

- `package_model = plugin_package`. Preserve the existing baseline; this slice documents and verifies it, does not rebuild it.
- Install = `claude --plugin-dir <plugin-root>`; launch = `claude`; inspect/update/reload = `/reload-plugins`.
- Package files declared from the real baseline: `.claude-plugin/plugin.json`, `skills/`, `hooks/hooks.json`, `agents/tutor-judge.md`, `bin/tutor`.
- Capability prose matches `registry.py` Claude defaults exactly: text `supported`, lifecycle_start `hook`, lifecycle_end `hook`, boot trigger `session_start_hook`, unsupported `audio`/`image`, no flow gates.
- User-owned boundaries: `secrets`, `memories`, `sessions`, `logs`, `local`, `*.sqlite`.
- `capability_profile_path = schemas/host_capability_profile.schema.json`.

## Changed Files

- `specs/006-agent-adapter-setup/contracts/host-setup-profiles/claude.md` (created)
- `specs/006-agent-adapter-setup/subagent-reports/claude.md` (created — this report)

Baseline plugin files (`.claude-plugin/plugin.json`, `hooks/hooks.json`, `skills/`, `agents/tutor-judge.md`, `bin/tutor`) were read only and left unmodified. No shared `src/` or other-host files were touched. No `SKILL.md` created/edited. No Antigravity content.

## Verification

- Profile loads as `claude`:
  ```
  rtk uv run python -c "from language_tutor.adapters.base import load_host_setup_profile; print(load_host_setup_profile('specs/006-agent-adapter-setup/contracts/host-setup-profiles/claude.md').host)"
  -> claude
  ```
- Test suite:
  ```
  rtk uv run pytest tests/packaging/test_claude_plugin_package.py tests/packaging/test_host_setup_profiles.py tests/adapter_contract/test_plugin_surface.py -p no:cacheprovider --no-cov -q
  -> 19 passed, 6 skipped in 0.04s
  ```
- Host validation command `rtk claude plugin validate . --strict` (CLI present: `claude` 2.1.148). The subcommand exists and ran; it reports pre-existing baseline findings (preserved, not fixed in this slice):
  ```
  ✘ author: Invalid input: expected object, received string
  ⚠ schema_version: Unknown field 'schema_version'. Claude Code ignores it at load time.
  ⚠ CLAUDE.md at plugin root is not loaded as project context; use a skill instead.
  ⚠ agents/tutor-judge.md: No frontmatter block found.
  ✘ hooks.SessionStart.0.hooks: Invalid input: expected array, received undefined
  ✘ hooks.SessionEnd.0.hooks: Invalid input: expected array, received undefined
  ✘ Validation failed
  ```
  Note: `--strict` is a global flag accepted before or after the path; the working invocation is `claude plugin validate . --strict`.

## Failures

- None in this slice's owned scope. The three target test files pass.

## Blockers

- `claude plugin validate --strict` fails against the existing baseline (manifest `author` shape, `hooks.*.hooks` array shape, missing agent frontmatter, plugin-root `CLAUDE.md`). These predate this slice and are out of my write scope (must preserve baseline). Recorded as a Known Limitation in `claude.md`; resolving them requires a separate baseline-owning decision by the main maintainer.
