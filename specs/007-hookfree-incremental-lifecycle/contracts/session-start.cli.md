# CLI Contract: `session-start`

Mints and owns the tutor session id, persists an `open` session row, returns it
with boot context. Called by the agent on the **first** tutor-skill invocation of
a conversation (no id passed). Side-effectful (writes one session row).

## Invocation

```bash
rtk bin/tutor session-start --json '{"host":"codex","host_conversation_id":"<optional>"}'
```

## Input

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `host` | enum(claude,codex,openclaw,hermes) | yes | rejected otherwise. |
| `host_conversation_id` | string | no | optional non-key enrichment only. |

No `session_id` is accepted on input — the CLI always mints a new one.

## Output

Conforms to `boot-result.schema.json`:

```json
{ "session_id": "sess_...", "context": { "sections": [ ... ], "prior_sessions": [ ... ] } }
```

## Behavior

1. Mint a new `session_id` (`tutor_generated`; `host_conversation` recorded as
   enrichment when supplied).
2. INSERT session row `status=open`, `started_at=last_seen_at=now`, durably
   commit.
3. Read N most-recent prior sessions (default 3) by `last_seen_at`, apply
   read-time labels, build prior-session block within token budget.
4. Return `{session_id, context}`. MUST NOT mutate any prior session id.

The agent then passes the returned `session_id` to every subsequent `bin/tutor`
call this conversation (checkpoint/record/close). A new conversation carries no
id → calls `session-start` again → new session.

## Errors

- Unsupported host → `HostSetupFailure` (existing error contract).
- Backward compatibility: existing `boot-context` command is unchanged and does
  NOT create a session.
