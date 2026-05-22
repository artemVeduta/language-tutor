# T020 — Skill Pressure Baseline (RED)

Captured before T025-T026 SKILL.md edits. Verifies the five tutor skill
SKILL.md files at HEAD do NOT teach the hook-free incremental lifecycle (FR-005,
FR-019). Per `specs/007-hookfree-incremental-lifecycle/skill-pressure-scenarios.md`,
the five scenarios all fail in this baseline.

## Evidence

For each file, the SKILL.md content was inspected with grep. None of the five
contains either `session-start` or `checkpoint`:

| File                              | mentions `session-start` | mentions `checkpoint` |
|-----------------------------------|--------------------------|-----------------------|
| skills/tutor-lesson/SKILL.md      | no                       | no                    |
| skills/tutor-reading/SKILL.md     | no                       | no                    |
| skills/tutor-vocab/SKILL.md       | no                       | no                    |
| skills/tutor-writing/SKILL.md     | no                       | no                    |
| skills/tutor-progress/SKILL.md    | no                       | no                    |

## Scenario outcomes against baseline

- Scenario 1 (obtain session id) — FAIL: skills jump straight to start commands.
- Scenario 2 (thread session_id) — FAIL: only `tutor-vocab` and writing record
  payloads mention `session_id`, and they accept the default `"default"`.
- Scenario 3 (checkpoint on presentation) — FAIL: no skill calls any
  `checkpoint` subcommand.
- Scenario 4 (no automatic close) — PASS in baseline (none of the skills call
  `session-close`/`session-end` automatically except `tutor-progress`, which
  references `session-end` as part of its CLI surface; that wording is
  reviewed in T047).
- Scenario 5 (no hook references) — PASS in baseline (no SKILL.md hard-codes a
  hook command).

T027 will re-run these scenarios after T025-T026 SKILL.md edits land and
record the GREEN outcomes.
