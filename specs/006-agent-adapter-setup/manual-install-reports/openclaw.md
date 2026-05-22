# Manual Provider Install Report: OpenClaw

## Environment
- Host: OpenClaw
- Host version: N/A — `openclaw`/`clawhub` CLIs not installed; Node v25.6.1, pnpm present
- OS: macOS (Darwin 25.3.0)
- Package ref: `openclaw-plugin/` (package.json ESM, openclaw.plugin.json, src/index.ts)
- Test learner home: temp `TUTOR_HOME`
- Date: 2026-05-22

## Install
- Command: `openclaw plugins install <package-name>`
- Result: BLOCKED — `openclaw` CLI not installed.
- Evidence: package validated by `tests/packaging/test_openclaw_plugin_package.py` (ESM type=module, focused SDK imports, manifest present).

## Launch
- Result: BLOCKED (CLI absent).

## Capability Check
- Capability profile used: `tutor host capability openclaw`
- Text support: supported (declared)
- Lifecycle/boot trigger: first_message / first_tutor_message
- Unsupported capabilities / flow gates: audio, image; binary-dependent tool opt-in; no flow gates

## Representative Tutor Flows
Underlying tutor CLI flows verified by automated suite:
- Reading / Lesson / Transcript / Vocab / Free-writing feedback / Progress check: pass (CLI/automated); host-surface: skipped_pending_live_session

## Update Or Reload
- Command: reinstall/upgrade plugin package; Result: BLOCKED (CLI absent).

## Inspect
- Command: `pnpm test -- <openclaw-plugin-root>` / `pnpm check`
- Result: PARTIAL — pnpm present; `tsc`/OpenClaw SDK peer dep not installed locally, so type-check could not complete. No defects in owned files.
- `clawhub package publish <org>/<plugin> --dry-run`: BLOCKED — `clawhub` not installed.

## Remove
- Result: BLOCKED (CLI absent).

## User Data Preservation
- No `.env`, SQLite, logs in `openclaw-plugin/`. Verified by privacy tests. Plugin calls tutor CLI/core contracts only.

## Decision
Decision: blocked — OpenClaw/ClawHub CLIs and SDK peer deps not installed; live install/publish and host-surface flows require an OpenClaw environment.
