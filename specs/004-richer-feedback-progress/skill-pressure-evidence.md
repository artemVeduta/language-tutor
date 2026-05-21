# Skill Pressure Evidence: tutor-progress

## Inventory

- Skill: `skills/tutor-progress/SKILL.md`.
- Original surface: `progress --json`, `session-end --json`, `doctor --json`.
- Phase 4 export surfaces: `progress --json '{"format":"markdown"}'` and `render progress-report --json '<ProgressReport JSON>'`.
- Scope: skill routes requests only. Python CLI owns scoring, pedagogy, aggregation, validation, and markdown rendering.

## References

- Local helper read first: `/Users/artem.veduta/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-skills/SKILL.md`.
- Subagent testing reference: `/Users/artem.veduta/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-skills/testing-skills-with-subagents.md`.
- Skill authoring reference: `/Users/artem.veduta/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-skills/anthropic-best-practices.md`.
- Phase 4 contracts: `specs/004-richer-feedback-progress/contracts/progress-cli.md`, `progress-json-report.md`, `progress-markdown-report.md`.

## RED Baseline

Subagent: `rtk codex exec --sandbox read-only --ephemeral`; no file edits.

| Scenario | Baseline choice | Pressure failure |
| --- | --- | --- |
| Markdown export | Run `bin/tutor progress --json`, then manually format markdown | Missing markdown route; duplicates renderer logic outside CLI |
| Validated JSON export | Run `bin/tutor progress --json` | Validation/version contract unclear from skill |
| Privacy-safe examples | Summarize from progress JSON or recent sessions | Skill only banned raw answers/full feedback for weak patterns, not prompts, spans, event logs, host metadata, or examples |
| Multi-format export | Generate one report and transform twice manually | JSON/markdown could diverge because single source of truth was not explicit |

## GREEN Evidence

- Skill now routes JSON export to `bin/tutor progress --json`.
- Skill now routes direct markdown export to `bin/tutor progress --json '{"format":"markdown"}'`.
- Skill now routes markdown rendering from an existing report to `bin/tutor render progress-report --json '<ProgressReport JSON>'`.
- Skill explicitly says not to hand-format markdown, recompute scoring, invent examples, or read raw storage.
- Export privacy guardrails cover raw answers, mistake spans, prompts, full feedback prose, event logs, host metadata, and local paths.
- GREEN subagent chose CLI-rendered markdown, CLI JSON as-is, and refused examples unless already present in privacy-safe CLI output.

## REFACTOR Evidence

- Description reviewed for activation: starts with `Use when`, includes progress/export/status/cost triggers, and does not summarize workflow.
- Body kept short and command-focused to avoid duplicating Phase 4 scoring or pedagogy.
- Loophole closed: "shareable examples" cannot justify raw prompt/answer excerpts; use aggregate CLI output only.
- Loophole closed after GREEN review: learner-specific examples are forbidden unless the CLI emits sanitized aggregate examples explicitly intended for export.
- Loophole closed: markdown export cannot be hand-built from JSON; use direct markdown format or renderer command.
- Loophole closed: cost/status stays on `progress` or `doctor`, not DB inspection.

## Changed Files

- `skills/tutor-progress/SKILL.md`
- `specs/004-richer-feedback-progress/skill-pressure-evidence.md`

## Remaining Gaps

- Full Phase 4 pass still depends on existing code/test changes outside this task ownership.
- No separate schema-validation command is exposed; JSON validation remains via CLI/Pydantic contracts and schema mirrors.
- Focused progress tests pass with `--no-cov`; running those same subsets without `--no-cov` hits the repo-wide 80% coverage gate because only a narrow slice is executed.
