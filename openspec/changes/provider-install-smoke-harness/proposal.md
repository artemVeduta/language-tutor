# Change: provider-install-smoke-harness

## Status
Proposed - 2026-05-29

## Summary
Add one maintainer-only executable that runs repeatable provider installation smoke checks for Claude, Codex, Hermes, and OpenClaw from a disposable local environment. The harness focuses on installation confidence before merge/release: clean package install, isolated `HOME`, `tutor init` per provider, `tutor doctor --json`, managed-file checks, secret-leak checks, and machine-readable evidence reports.

## Motivation
`docs/internal/pr12-merge-checklist.md` currently keeps per-provider install checks as manual checklist work. That makes release confidence depend on remembering the same sequence four times, and failures are hard to compare across providers.

The repository already has reusable provider installer tests and conformance tests. What is missing is a laptop-run smoke harness that exercises the packaged CLI in an isolated install-like environment without touching the maintainer's real host config or learner data.

## Goals
1. Provide one executable command that runs provider install smoke checks for all supported providers by default.
2. Support `--provider <id>` for focused runs.
3. Use a temporary `HOME` and clean package environment so smoke checks do not mutate the maintainer's real host config or learner data.
4. Delete the temporary workdir on success, keep it on failure, and support `--keep-workdir`.
5. Produce per-provider JSON reports with enough evidence to copy into manual provider install reports.
6. Treat live host CLI validation as best-effort: run safe non-interactive commands when available, otherwise record `skipped` or `manual_needed`.

## Non-goals
- No Docker implementation in the first version.
- No automatic interaction with Claude, Codex, Hermes, or OpenClaw UI/session surfaces.
- No replacement for final live manual provider verification.
- No changes to pedagogy, SRS, feedback, learner profile/history schemas, lifecycle persistence, or tutor skills.
- No new provider support.

## Proposed Command

```bash
rtk scripts/provider-smoke.sh
rtk scripts/provider-smoke.sh --provider claude
rtk scripts/provider-smoke.sh --provider codex --keep-workdir
```

Default provider order:

```text
claude
codex
hermes
openclaw
```

## Workdir Lifecycle

The harness creates a temp workdir with:

```text
workdir/
|-- home/       # fake HOME
|-- package/    # clean package install area
|-- reports/    # per-provider JSON reports
|-- logs/       # stdout/stderr captures
`-- wheel/      # built wheel, if wheel mode is used
```

On success, the workdir is removed. On failure, it is kept and the harness prints the path. With `--keep-workdir`, it is always kept.

## Risks

| Risk | Mitigation |
|---|---|
| Harness accidentally mutates real host config | Force `HOME`/XDG paths into the temp workdir for every command. |
| Host CLIs require interactive login or UI state | Only run safe non-interactive host checks; record `manual_needed` otherwise. |
| Reports become a second source of truth | Reports are evidence artifacts only; provider contracts and installer profiles remain source of truth. |
| Scope drifts into Docker or live session automation | Keep Docker and interactive host testing explicitly out of v1. |
