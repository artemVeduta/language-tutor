# CLI Contract: `session-close` (explicit manual close only)

Marks a session `closed`. Never invoked automatically by any lifecycle path
(FR-007). Only runs when the learner explicitly asks to wrap up.

## Invocation

```bash
rtk bin/tutor session-close --json '{"session_id":"sess_...","analysis":{...},"costs":{...}}'
```

## Input

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `session_id` | string | yes | the active session to close. |
| `analysis` | SessionAnalysis | yes | final summary input (existing shape). |
| `costs` | cost payload | yes | cost flush (existing shape). |

## Output

```json
{ "session_id": "sess_...", "status": "complete", "summary_id": "...", "next_focus": "..." }
```

## Behavior

1. Set `status=closed`, `closed_at=now`, durably commit.
2. Write final summary, cost flush, and next-focus decision (reuses existing
   `record_session_end` path) (FR-015).
3. Idempotent-safe: closing an already-closed session is a no-op error per
   existing error contract.

## Guarantees

- No boot/checkpoint/record path ever calls this command (asserted by
  integration test SC-003 / FR-007).
- This replaces the old `session-end.sh` hook usage; the hook is removed or
  deprecated legacy-only.
