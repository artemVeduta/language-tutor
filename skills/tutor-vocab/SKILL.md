---
name: tutor-vocab
description: Practice due vocabulary through the local tutor CLI.
---

Use this when learner wants vocabulary review, starter vocabulary, manual card add, seed
import, tag-filtered drill, cloze practice, review history, or answer correction.

Run only `bin/tutor` for stateful work:

- Start queue: `bin/tutor vocab start --json`
- Start filtered queue: `bin/tutor vocab start --json '<{"tags":["greetings"]}>'`
- Add card: `bin/tutor vocab add --json '<card-json>'`
- Import seed list: `bin/tutor vocab import --json '<{"path":"cards.json"}>'`
- Record answer once: `bin/tutor vocab answer --json '<payload>'`
- Inspect history: `bin/tutor vocab history --json '<{"item_id":"vocab_..."}>'`

Cloze cards use `card_type:"cloze"` and exactly one `{{answer}}` marker in
`prompt`. The CLI hides the marker during drill and reveals the sentence after
answering.

Do not implement SM-2 or persistence in this skill.
