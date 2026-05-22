# Manual Provider Install Report: Hermes

## Environment
- Host: Hermes
- Host version: N/A — `hermes` CLI not installed on this machine
- OS: macOS (Darwin 25.3.0)
- Package/profile ref: `hermes-profile/` (distribution.yaml, SOUL.md, config.yaml)
- Test learner home: temp `TUTOR_HOME`
- Date: 2026-05-22

## Install
- Command: `hermes profile install <local-hermes-profile-path> --name language-tutor-test --alias`
- Result: BLOCKED — `command -v hermes` returns nothing.
- Evidence: tool absent; profile distribution files validated by `tests/packaging/test_hermes_profile_distribution.py`.
- Failures/blockers: Hermes CLI not installed.

## Launch
- Command: `hermes profile info language-tutor-test`
- Result: BLOCKED (CLI absent).

## Capability Check
- Capability profile used: `tutor host capability hermes`
- Text support result: supported (declared)
- Lifecycle/boot trigger result: explicit_command / explicit_tutor_command (verified via `tutor host boot-trigger hermes`)
- Unsupported capabilities / flow gates: audio, image; no flow gates

## Representative Tutor Flows
Underlying tutor CLI flows verified by automated suite (tests/integration, tests/golden):
- Reading comprehension: pass (CLI/automated); host-surface: skipped_pending_live_session
- Guided lesson: pass (CLI/automated); host-surface: skipped_pending_live_session
- Transcript drill: pass (CLI/automated); host-surface: skipped_pending_live_session
- Vocab drill: pass (CLI/automated); host-surface: skipped_pending_live_session
- Free-writing feedback: pass (CLI/automated); host-surface: skipped_pending_live_session
- Progress check: pass (CLI/automated); host-surface: skipped_pending_live_session

## Update Or Reload
- Command: `hermes profile update language-tutor-test`
- Result: BLOCKED (CLI absent). User-owned data preservation enforced by exclude list in distribution.yaml.

## Inspect
- Command: `hermes profile info language-tutor-test`
- Result: BLOCKED (CLI absent).

## Remove
- Command: `hermes profile delete language-tutor-test`
- Result: BLOCKED (CLI absent).

## User Data Preservation
- distribution.yaml hard-excludes secrets/.env, memories, sessions, SQLite state, logs, caches, local/. Verified by packaging privacy tests. No learner data packaged.

## Decision
Decision: blocked — Hermes CLI not installed; live install/update/inspect/remove and host-surface flows require a machine with the `hermes` CLI.
