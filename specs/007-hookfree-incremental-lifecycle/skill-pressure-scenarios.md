# Skill Pressure Scenarios (T015)

Pressure scenarios for the writing-skills helper RED→GREEN cycle. Each scenario
describes one rule the SKILL.md must teach a future agent. Baseline (T020):
verify these all FAIL against the unmodified SKILL.md. After T025-T026 edits,
verify they all PASS.

Scenarios apply to every tutor skill family (lesson, reading, vocab, writing,
progress). Transcript falls under reading.

## Scenario 1 — Obtain session id on first invocation (FR-001, FR-003)

> Setup: a fresh conversation, no prior `session_id` known to the agent.
> Prompt the agent to run the skill's first stateful step.
> PASS condition: the agent's first `bin/tutor` invocation in the conversation
> is `bin/tutor session-start --json '{"host":"<host>"}'`, and the agent
> stores the returned `session_id` before doing anything else stateful.
> FAIL (RED) condition: the agent jumps straight to `lesson start`, `reading
> start`, `vocab start`, `writing prompt`, or `progress` without calling
> session-start.

## Scenario 2 — Thread session_id into every stateful call (FR-019)

> Setup: conversation already has `session_id = sess_X`.
> Prompt the agent through a full skill flow (generate → validate → judge →
> record).
> PASS condition: every `bin/tutor <skill> ...` payload in the conversation
> embeds `"session_id": "sess_X"`.
> FAIL (RED) condition: any record/answer/persist call omits `session_id`
> or uses a different value (e.g. the default `"default"`).

## Scenario 3 — Checkpoint on presentation (FR-005)

> Setup: agent has a `session_id` and a validated exercise/prompt/queue ready
> to present.
> PASS condition: immediately before showing the exercise/prompt/queue to the
> learner, the agent calls
> `bin/tutor checkpoint --json '{"session_id":"sess_X","modality":"<modality>","step_kind":"prompt_shown","summary":"...","state":{...}}'`.
> FAIL (RED) condition: the agent shows content first or never calls
> checkpoint.

## Scenario 4 — No automatic session close (FR-007)

> Setup: ordinary skill flow with no explicit "close the session" request.
> PASS condition: the agent does NOT call `bin/tutor session-close` or the
> legacy `bin/tutor session-end` at the end of normal flows.
> FAIL (RED) condition: the agent calls session-close or session-end after
> the last record step.

## Scenario 5 — No hook references (FR-011)

> Setup: review the SKILL.md text itself.
> PASS condition: the SKILL.md text describes the no-hook flow only and does
> not mention `hooks/session-start.sh`, `hooks/session-end.sh`, or SessionStart
> hooks as the boot path.
> FAIL (RED) condition: any hook-as-normal-boot wording.

## Per-family checkpoint modality

| Skill          | `modality`  | When to checkpoint                                |
|----------------|-------------|---------------------------------------------------|
| tutor-lesson   | `lesson`    | After step 3 validation, before showing learner.  |
| tutor-reading  | `reading`   | After step 2 validation; submode transcript uses `transcript`. |
| tutor-vocab    | `vocab`     | After `vocab start` returns the queue (`prompt_shown` for first item). |
| tutor-writing  | `writing`   | After `writing prompt` returns the prompt.        |
| tutor-progress | `progress`  | After `progress --json` returns the report (`progress_shown`). |
