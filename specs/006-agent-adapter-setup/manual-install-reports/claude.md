# Manual Provider Install Report: Claude

## Environment
- Host: Claude Code
- Host version: claude CLI v2.1.148
- OS: macOS (Darwin 25.3.0)
- Package ref: repo root `.claude-plugin/` baseline (skills/, hooks/, agents/, bin/tutor)
- Test learner home: temp `TUTOR_HOME`
- Date: 2026-05-22

## Install
- Command: `claude --plugin-dir <plugin-root>`
- Result: command form valid; baseline plugin dir present.
- Evidence: `tests/packaging/test_claude_plugin_package.py` + `tests/adapter_contract/test_plugin_surface.py` pass.

## Launch
- Command: `claude`; Result: launches (CLI present). Tutor `bin/tutor doctor --json` → all checks ok.

## Capability Check
- Capability profile used: `tutor host capability claude` (verified output)
- Text support: supported
- Lifecycle/boot trigger: hook / session_start_hook (verified via `tutor host boot-trigger claude` → SessionStart)
- Unsupported capabilities: audio, image; no flow gates

## Representative Tutor Flows
Underlying tutor CLI flows verified by automated suite (tests/integration, tests/golden) — pass:
- Reading, Lesson, Transcript, Vocab, Free-writing feedback, Progress check: pass (CLI/automated); in-host `/reload-plugins` interactive run: skipped_pending_live_session

## Update Or Reload
- Action: `/reload-plugins` inside Claude. Result: pending live interactive session. User data preserved (no state in package).

## Inspect
- Command: `claude plugin validate . --strict`
- Result: PASS on all errors. The three baseline schema errors (`author`
  string→object, `hooks.*.hooks` nested-array shape, `agents/tutor-judge.md`
  missing frontmatter) were FIXED this session. `--strict` now emits only one
  benign warning: repo-root `CLAUDE.md` is dev instructions, not plugin context
  (tutor ships context via `skills/`); removing it is not desired. Expected.

## Remove
- Action: remove `--plugin-dir` flag / disable plugin. Result: not applicable for local dir load.

## User Data Preservation
- Manifest carries no secrets/SQLite/memories/sessions (verified). Learner state stays in local SQLite/YAML.

## Decision
Decision: blocked — `claude plugin validate --strict` errors now pass and the
baseline is modernized; only the live in-host `/reload-plugins` six-flow run is
pending an interactive session.
