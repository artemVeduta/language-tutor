---
name: tutor-vocab
description: Practice due vocabulary through the local tutor CLI.
---

Use this when learner wants vocabulary review, starter vocabulary, manual card add, seed
import, tag-filtered drill, cloze practice, review history, or answer correction.

**Session precondition (first stateful step of the conversation):** before any
`vocab start` / `vocab add` / `vocab import` / `vocab answer`, call
`bin/tutor session-start --json '{"host":"<host>"}'` and capture the returned
`session_id` (`sess_...`). Reuse it for the rest of the conversation. Do NOT
call `session-close` or `session-end` automatically.

Run only `bin/tutor` for stateful work:

- Start queue: `bin/tutor vocab start --json`
- Start filtered queue: `bin/tutor vocab start --json '<{"tags":["greetings"]}>'`
- Checkpoint immediately after `vocab start` returns a non-empty queue and
  BEFORE showing the first card:
  `bin/tutor checkpoint --json '{"session_id":"sess_...","modality":"vocab","step_kind":"prompt_shown","summary":"...","state":{"step_index":0,"total_steps":<queue_len>}}'`
- Add card: `bin/tutor vocab add --json '<card-json>'`
- Import seed list: `bin/tutor vocab import --json '<{"path":"cards.json"}>'`
- Record answer once: `bin/tutor vocab answer --json '<payload>'` — payload
  MUST include `"session_id":"sess_..."` (replaces default `"default"`), the
  `"item_id"`, the learner `"answer"`, and a unique `"idempotency_key"` (any
  UUID; dedupes retries). Omitting `idempotency_key` fails validation.
- Inspect history: `bin/tutor vocab history --json '<{"item_id":"vocab_..."}>'`

Queue JSON includes `effective_count`, `active_weak_tags`, `selection_reasons`,
and `selection_policy`. `review_intensity` means light = 50%, normal = 100%, and
heavy = 150% of configured session length, capped at 60 cards. Tag filters are
hard boundaries.

Cloze cards use `card_type:"cloze"` and exactly one `{{answer}}` marker in
`prompt`. The CLI hides the marker during drill and reveals the sentence after
answering.

Do not implement SM-2 or persistence in this skill.

## Payload schemas (build every request against these)

Read the referenced `schemas/*.schema.json` before constructing the payload; do not guess fields.

- `session-start` input: `{"host":"claude|codex|openclaw|hermes","host_conversation_id"?:str}` → output `schemas/boot_result.schema.json`.
- `vocab start` input (optional): `{"tags"?:[str],"requested_count"?:1-100}` → output `schemas/vocabulary_session_plan.schema.json`.
- `checkpoint` input → `schemas/checkpoint.schema.json`. Required: `session_id`, `modality` (`vocab`), `step_kind`, `summary`. `prompt_ref` exists at BOTH the top level and inside `state` — set `state.prompt_ref` when you have one. `state` also takes `step_index`, `total_steps`, `modality_hint`, `labels` (≤16).
- `vocab add` input → `schemas/vocabulary_card_definition.schema.json`.
- `vocab import` input: `{"path":"...json"}` → output `schemas/vocabulary_import_summary.schema.json`.
- `vocab answer` input: `{"session_id":"sess_...","item_id":"vocab_...","answer":str,"idempotency_key":str}` (omit `idempotency_key` → validation fails).
- `vocab history` input: `{"item_id":"vocab_..."}` → output `schemas/vocabulary_review_history.schema.json`.
