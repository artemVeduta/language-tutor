# Quickstart: Hook-Free Incremental Lifecycle

End-to-end of the no-hook lifecycle on any host. No hook install required.

## 1. First tutor message → boot + session

```bash
rtk bin/tutor session-start --json '{"host":"codex"}'
# -> {"session_id":"sess_ab12","context":{"sections":[...],"prior_sessions":[...]}}
```

Agent captures `sess_ab12` and threads it into every later call this conversation.

## 2. Tutor presents a lesson/exercise → immediate checkpoint

```bash
rtk bin/tutor checkpoint --json '{
  "session_id":"sess_ab12","modality":"lesson","step_kind":"prompt_shown",
  "prompt_ref":"lesson_42_step3","state":{"step_index":3,"total_steps":8},
  "summary":"Showed past-tense drill step 3/8"
}'
```

## 3. Learner answers → existing answer/review/mistake persistence

```bash
rtk bin/tutor record-answer --json '{"session_id":"sess_ab12", ...}'
```

All writes share `sess_ab12` (FR-019).

## 4. App closes mid-lesson — no end event

Nothing runs. Session stays `open`. All checkpoints + answers through the last
step are already durably committed (FR-013, SC-002).

## 5. New conversation later → new session, prior read as history

```bash
rtk bin/tutor session-start --json '{"host":"codex"}'
# -> {"session_id":"sess_cd34","context":{"prior_sessions":[
#      {"session_id":"sess_ab12","label":"stale","last_seen_at":"..."}]}}
```

`sess_ab12` is unchanged (FR-004, SC-003); labeled `stale` (newer session exists)
or `abandoned` (last_seen_at > 14 days old). New data writes only under
`sess_cd34`.

## 6. Optional explicit close

```bash
rtk bin/tutor session-close --json '{"session_id":"sess_cd34","analysis":{...},"costs":{...}}'
# -> status=closed, closed_at set, final summary + cost flush + next focus
```

Never automatic.

## Verification gates

```bash
rtk pytest          # unit, golden, contract, integration, migration, conformance, packaging-privacy
rtk pyright
rtk ruff check
```

Expect: all four host profiles declare the shared lifecycle values and pass
first-message-boot + checkpoint persistence with zero hooks installed (SC-001);
no shipped user-owned session/checkpoint data (SC-004).
