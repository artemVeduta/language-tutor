# Manual Provider Install Report: Codex

> **Spec 007 note:** any plugin-hooks lifecycle assertions in this report
> predate the hook-free lifecycle. The Codex plugin does not require
> `[features].plugin_hooks` — boot happens on the first tutor message via
> `tutor session-start --json`. See
> `specs/007-hookfree-incremental-lifecycle/` for the current contract.

## Environment
- Host: Codex
- Host version: codex-cli 0.130.0
- OS: macOS (Darwin 25.3.0)
- Package ref: `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json` (reuses root skills/)
- Test learner home: temp `TUTOR_HOME`
- Date: 2026-05-22

## Install
- Steps: add repo-local marketplace entry → restart Codex → enable plugin from marketplace.
- Result: manifest + marketplace JSON valid (parse-checked); live marketplace install pending interactive session.
- Evidence: `tests/packaging/test_codex_plugin_package.py` pass (manifest references ./skills/, hooks disabled by default, cache-safe).

## Launch
- Action: launch Codex with plugin enabled. Result: pending live session.

## Capability Check
- Capability profile used: `tutor host capability codex`
- Text support: supported
- Lifecycle/boot trigger: hook / codex_plugin_hook (hooks opt-in via `[features].plugin_hooks`)
- Unsupported capabilities: audio, image; no flow gates

## Representative Tutor Flows
Underlying tutor CLI flows verified by automated suite — pass:
- Reading, Lesson, Transcript, Vocab, Free-writing feedback, Progress check: pass (CLI/automated); in-host run: skipped_pending_live_session

## Update Or Reload
- Action: update marketplace entry → Codex restart/reload. Result: pending live session. No user state in package.

## Inspect
- Action: confirm plugin visible in selected marketplace and skills exposed. Result: pending live session (Codex has no documented standalone validator).

## Remove
- Action: remove marketplace entry / disable plugin. Result: pending live session.

## User Data Preservation
- `.codex-plugin/plugin.json` carries no secrets/SQLite/memories/sessions; `plugin_hooks=false`. Verified by tests.

## Decision
Decision: blocked — manifest/marketplace/automated checks pass, but Codex has no standalone validator and the live marketplace install + six-flow run is pending an interactive session.
