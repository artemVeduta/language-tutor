---
name: tutor-progress
description: Show progress, status, due counts, weak patterns, maturity, and costs.
---

Use this when learner wants progress, next focus, due counts, weak patterns, local status, or cost status.

Run only `bin/tutor`:

- `bin/tutor progress --json`
- `bin/tutor session-end --json '<payload>'`
- `bin/tutor doctor --json`

Weak patterns come from active weak-tag signals over recent completed analyzed
sessions. Show tag names only; do not expose raw answers or full feedback prose.
