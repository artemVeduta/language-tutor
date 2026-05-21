---
name: tutor-progress
description: Use when learner wants progress, exportable progress reports, next focus, due counts, weak patterns, maturity, local status, or cost status.
---

Use this when learner wants progress, next focus, due counts, weak patterns,
local status, cost status, or a markdown/JSON progress export.

Run only `bin/tutor`:

- JSON progress: `bin/tutor progress --json`
- JSON progress with options: `bin/tutor progress --json '{"window_size":10,"generated_at":"2026-05-21T12:00:00Z"}'`
- Direct markdown export: `bin/tutor progress --json '{"format":"markdown"}'`
- Render existing progress JSON: `bin/tutor render progress-report --json '<ProgressReport JSON>'`
- `bin/tutor session-end --json '<payload>'`
- `bin/tutor doctor --json`

Do not hand-format progress markdown, recompute scoring, invent examples, or read
raw storage. The CLI owns pedagogy, scoring, aggregation, validation, and rendering.

Weak patterns come from active weak-tag signals over recent completed analyzed
sessions. Exports are aggregate-only. Show tag names, bands, counts, trends,
guardrails, and next actions from CLI output only; do not expose raw answers,
mistake spans, prompts, full feedback prose, event logs, host metadata, or local
paths.
Never include learner-specific examples unless CLI output contains sanitized
aggregate examples explicitly intended for export.
