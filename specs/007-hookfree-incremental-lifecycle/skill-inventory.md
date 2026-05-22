# Skill Inventory + Subagent Assignments (T014)

Per FR-005 (checkpoint on presentation) and FR-019 (single session_id threaded
into every `bin/tutor` call), the following five tutor skill families require
SKILL.md edits. Each edit lands through one subagent using the local
`writing-skills` helper at
`/Users/artem.veduta/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-skills`.

| Skill family            | Path                              | Subagent role             | Edit scope (per FR-005, FR-019)                                                                 |
|-------------------------|-----------------------------------|---------------------------|-------------------------------------------------------------------------------------------------|
| tutor-lesson            | `skills/tutor-lesson/SKILL.md`    | lesson-skill-author       | Add session-start step, thread `session_id` into every `bin/tutor lesson ...`, checkpoint after step 3 (validate). |
| tutor-reading           | `skills/tutor-reading/SKILL.md`   | reading-skill-author      | Same for reading; transcript drills are a submode and share the same flow.                      |
| tutor-vocab             | `skills/tutor-vocab/SKILL.md`     | vocab-skill-author        | Session-start before first start; checkpoint after queue start; thread `session_id` into answer.|
| tutor-writing           | `skills/tutor-writing/SKILL.md`   | writing-skill-author      | Session-start before prompt; checkpoint after prompt step; thread `session_id` into record.     |
| tutor-progress          | `skills/tutor-progress/SKILL.md`  | progress-skill-author     | Session-start before progress; checkpoint on `progress_shown`; thread `session_id` into session-end.|

Transcript is handled as a submode of `tutor-reading` (no separate skill).

**Author baseline:** All five current SKILL.md files describe their CLI surface
but do NOT (a) obtain a session id, (b) thread a session id, or (c) call any
checkpoint subcommand. This is the RED baseline asserted by T020.
