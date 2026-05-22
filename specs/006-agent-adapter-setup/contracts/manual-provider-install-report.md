# Contract: Manual Provider Install Report

## Purpose

Record the final human-run install/update verification for each supported host.

## Required Files

Implementation creates:

- `specs/006-agent-adapter-setup/manual-install-reports/hermes.md`
- `specs/006-agent-adapter-setup/manual-install-reports/openclaw.md`
- `specs/006-agent-adapter-setup/manual-install-reports/claude.md`
- `specs/006-agent-adapter-setup/manual-install-reports/codex.md`

Antigravity reports are forbidden.

## Required Sections

### Environment

- Host
- Host version
- OS
- Package/profile/plugin ref
- Test learner home
- Date

### Install

- Command or manual steps
- Result
- Evidence
- Failures/blockers

### Launch

- Command or host action
- Result
- Evidence

### Capability Check

- Capability profile used
- Text support result
- Lifecycle/boot trigger result
- Unsupported capabilities or flow gates

### Representative Tutor Flows

Record result for:

- Reading comprehension
- Guided lesson
- Transcript drill
- Vocab drill
- Free-writing feedback
- Progress check

Each result is `pass`, `fail`, or `skipped_capability_gated`. Skips require a capability profile reference and explanation.

### Update Or Reload

- Command or host action
- Result
- Evidence that user-owned data was preserved

### Inspect

- Command or host action
- Result
- Evidence that host recognizes the package/profile/plugin

### Remove

- Command or host action
- Result or not-applicable rationale

### User Data Preservation

Confirm that install/update/remove did not package, overwrite, or expose:

- Secrets and `.env`
- Learner memories and sessions
- SQLite state
- Logs and traces
- Local overrides
- Machine-local config

### Decision

`pass`, `fail`, or `blocked`.

## Blocking Rules

- `fail` on install, launch, update/reload, inspect, or data preservation blocks readiness.
- Any representative flow failure blocks readiness unless marked `skipped_capability_gated`.
- Missing report blocks readiness.
