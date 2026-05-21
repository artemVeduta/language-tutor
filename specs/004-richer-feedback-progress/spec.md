# Feature Specification: Richer Feedback Progress

**Feature Branch**: `004-richer-feedback-progress`

**Created**: 2026-05-21

**Status**: Draft

**Input**: User description: "Phase 4 from docs/ROADMAP.md: Richer Feedback & Progress. Renderer / analysis surface. No host dependency. Text/markdown only; no rich analytics dashboard, charts, GUI, or web view. Add per-tag mastery view, text trend / ASCII sparkline, last-N-session recap, and exportable markdown / JSON report that remains terminal-printable. Exit gate: progress views golden-tested deterministic; export round-trips; output is text/markdown only; progress view finishes in under 5 seconds on one year of daily history."

## Clarifications

### Session 2026-05-21

- Q: What recency scope should per-tag mastery use for categorization and evidence? → A: Last 30 completed sessions plus due/weak overrides.
- Q: What primary signal should the ASCII trend encode per completed session? → A: Overall success rate, with severity fallback for writing sessions.
- Q: How should active due/weak status affect tag mastery categories? → A: Due or weak status stays separate; affects priority/cue only.
- Q: Should Phase 4 support any non-default export mode that includes raw answers, full prompts, or full feedback prose? → A: No raw/full-text export mode.
- Q: Which SKILL.md files are included in the Phase 4 skill review? → A: All project SKILL.md files, including the active clarify skill.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See Per-Tag Mastery (Priority: P1)

A learner checks progress and sees a compact mastery summary for each practiced tag, including which tags are strong, improving, or still weak.

**Why this priority**: Phase 4 is valuable only if the learner can understand progress by learning pattern, not just by total review counts.

**Independent Test**: Can be tested by loading local history with multiple tags, strengths, misses, and due reviews, then requesting progress and verifying the per-tag view ranks and labels tags deterministically.

**Acceptance Scenarios**:

1. **Given** a learner has completed vocabulary or writing practice with tagged outcomes, **When** the learner views progress, **Then** the report shows each practiced tag with a mastery category, recent activity count, success signal, and due or weak status.
2. **Given** a tag has repeated recent mistakes, **When** the learner views progress, **Then** that tag appears as a weak or developing area with a next-focus cue.
3. **Given** a tag has mostly successful recent reviews and no current weak signal, **When** the learner views progress, **Then** that tag appears as a stronger area and is not mixed into the weak-tag list.
4. **Given** no tagged practice exists, **When** the learner views progress, **Then** the report explains that tag mastery is not available yet and points to vocabulary or writing practice without failing.

---

### User Story 2 - Review Recent Momentum (Priority: P1)

A learner sees recent session momentum as terminal text: a short trend line, last-N-session recap, streak, due reviews, weak patterns, and month-to-date cost.

**Why this priority**: The existing progress surface should make daily use feel visible without requiring a graphical dashboard.

**Independent Test**: Can be tested by creating a sequence of completed sessions with varied results and requesting recaps for different session counts, then verifying the same trend and recap render every time.

**Acceptance Scenarios**:

1. **Given** at least two completed sessions exist, **When** the learner views progress, **Then** the report shows a text trend over recent sessions using ASCII characters only.
2. **Given** a learner requests the last 5 sessions, **When** progress is shown, **Then** the recap includes no more than the 5 most recent completed sessions and preserves reverse chronological order.
3. **Given** fewer completed sessions exist than requested, **When** progress is shown, **Then** the recap includes all available completed sessions and states the actual count.
4. **Given** month-to-date cost data exists, **When** progress is shown, **Then** the cost appears beside other progress facts without dominating the report.
5. **Given** the learner has no completed sessions, **When** progress is shown, **Then** the report remains valid and provides a concise first-session state.

---

### User Story 3 - Export A Terminal-Printable Report (Priority: P2)

A learner exports the current progress report as Markdown or JSON for personal review, issue reports, or shell workflows without exposing raw answer text.

**Why this priority**: Export makes progress portable while preserving the local-first data model and avoiding a dashboard.

**Independent Test**: Can be tested by exporting the same progress fixture to Markdown and JSON, validating the JSON, rendering the Markdown in a terminal, and confirming both contain the same report facts.

**Acceptance Scenarios**:

1. **Given** a learner has progress data, **When** they export Markdown, **Then** the output is terminal-printable Markdown containing the same summary, tag mastery, trend, recap, and cost facts as the progress view.
2. **Given** a learner has progress data, **When** they export JSON, **Then** the output validates against the report contract and can be read back to reproduce the same report facts.
3. **Given** progress data includes raw answers or full feedback prose in local history, **When** a report is exported, **Then** every Phase 4 export excludes raw answer text, full prompts, full feedback prose, and full event logs.
4. **Given** the same learner state and report request, **When** export runs repeatedly, **Then** the Markdown and JSON outputs are byte-stable except for explicitly requested destination metadata.

### Edge Cases

- A learner has one year of daily sessions and hundreds of tagged events.
- A learner has sessions but no tags because early data predates tagging.
- Multiple tags tie on mastery score, recent attempts, and latest activity.
- A requested recap count is zero, negative, non-numeric, or above the supported limit.
- Session summaries exist for interrupted, incomplete, or invalid sessions.
- Month-to-date cost is missing for older events.
- Export is requested before any completed session exists.
- Markdown rendering is viewed in a terminal without emoji or rich color support.
- The same tag appears with different case, spacing, or legacy naming.
- JSON export is consumed by a tool that expects stable field names and ordering.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a text progress report that includes streak status, due-review counts, top weak patterns, month-to-date cost, per-tag mastery, recent trend, and last-N-session recap when the underlying data exists.
- **FR-002**: System MUST present per-tag mastery for practiced tags using deterministic categories: weak, developing, or strong.
- **FR-003**: System MUST include enough per-tag evidence for the learner to understand each mastery category, including recent attempts, recent successful outcomes, latest activity, and current due or weak status where available.
- **FR-004**: System MUST order tag mastery rows deterministically by priority for learner action: weakest first, then most recently practiced, then normalized tag name.
- **FR-005**: System MUST handle tags with no recent practice by keeping them out of recent mastery rankings unless they have current due reviews or weak signals.
- **FR-006**: System MUST normalize equivalent tag labels before reporting mastery so capitalization, spacing, and legacy spelling differences do not create duplicate rows.
- **FR-007**: System MUST show a recent progress trend using ASCII-only text characters and numeric context; it MUST NOT require color, emoji, graphics, charts, a GUI, or a web view to be understandable.
- **FR-008**: System MUST define the default trend window as the 30 most recent completed sessions, or all completed sessions if fewer than 30 exist.
- **FR-009**: System MUST provide a last-N-session recap where N is learner-selectable from 1 to 30 and defaults to 10 when not specified.
- **FR-010**: System MUST exclude interrupted, incomplete, or invalid sessions from trend and recap calculations while still allowing progress to render.
- **FR-011**: System MUST include recap facts for each included completed session: date, practiced skill, answered item count, success or severity summary, top tags, and short learner-safe summary when available.
- **FR-012**: System MUST provide Markdown export for the same report facts shown in the text progress view.
- **FR-013**: System MUST provide JSON export for the same report facts shown in the text progress view.
- **FR-014**: System MUST validate JSON export against an explicit report contract and allow the exported JSON to be read back to reproduce the same report facts.
- **FR-015**: System MUST keep Markdown export terminal-printable, with headings, lists, and tables only; graphical surfaces, embedded images, HTML-only features, and external assets are forbidden.
- **FR-016**: System MUST exclude raw learner answer text, full feedback prose, full prompts, and full event logs from progress views and all Phase 4 exports.
- **FR-017**: System MUST include only aggregate counts, tag names, dates, due counts, severity totals, cost totals, and concise summaries that are already intended for progress display.
- **FR-018**: System MUST produce deterministic progress rendering and export output for identical learner state, request options, and current date.
- **FR-019**: System MUST complete the standard progress view in under 5 seconds for a local history containing one year of daily completed sessions.
- **FR-020**: System MUST preserve existing progress behavior for streak, due reviews, weak patterns, and month-to-date cost while adding the richer sections.
- **FR-021**: System MUST remain host-independent and local-first; no host adapter changes, cloud services, telemetry, remote storage, authentication, or multi-user behavior may be introduced.
- **FR-022**: System MUST NOT add rich analytics dashboards, graphical charts, GUI screens, web views, notifications, gamification, new exercise modalities, audio, FSRS, or alternate scheduling algorithms.
- **FR-023**: Phase 4 MUST include a review of all project `SKILL.md` files under `.agents/skills/` and `skills/`, including the active `speckit-clarify` skill.
- **FR-024**: Skill review and rewrite work MUST apply documented skill-authoring best practices from the required external references and the local `writing-skills` helper.
- **FR-025**: Skill rewrite tasks MAY use subagents per skill or skill family when each delegated task explicitly uses the `writing-skills` helper and reports changed files.

### Requirement Details

- Per-tag mastery categorization and evidence use the last 30 completed sessions plus active due reviews and active weak-tag signals; tags outside that scope are omitted unless due or weak overrides apply.
- Mastery categories are learner-facing labels. Exact scoring rules may be designed during planning, but they must be deterministic, documented, testable, and based only on local learning history.
- Weak tags and due status must not change the mastery category label; they may influence row priority and next-focus cues only, keeping "weak now" separate from "low mastery overall".
- Trend output is a compact text line with a short legend and numeric totals. It may use ASCII characters such as `.`, `-`, `=`, `#`, and digits, but not graphical chart libraries or non-text surfaces.
- Each trend point encodes overall session success rate when answer outcomes are available, and falls back to the session severity summary for writing sessions without a direct success rate.
- Last-N recap uses completed sessions only. Default N is 10. Learner-selected N below 1 or above 30 is rejected with user-facing guidance.
- Report JSON round-trip means exported JSON can be validated and rendered back into the same report facts. It is not a backup or restore format for learner state.
- Markdown and JSON exports represent the same report request. If a section has no data, both formats include a clear empty-state value for that section.
- Deterministic output includes stable section order, stable row ordering, stable tie-breaks, stable field names, and stable formatting for dates and numeric values.
- Skill review reference sources for planning and implementation are: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices, https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf, and https://github.com/obra/superpowers/tree/main/skills.
- Skill review implementation must also use `/Users/artem.veduta/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-skills` as the local helper reference.

### Key Entities *(include if feature involves data)*

- **Progress Report**: The complete learner-facing summary for a report request, including existing progress facts plus Phase 4 mastery, trend, recap, and export metadata.
- **Tag Mastery Summary**: A per-tag aggregate showing mastery category, recent evidence, due or weak status, latest activity, and next-focus cue.
- **Progress Trend**: A compact text representation of recent completed sessions with numeric context and an ASCII-only trend line.
- **Session Recap Item**: A learner-safe summary of one completed session used in the last-N recap.
- **Report Export**: A Markdown or JSON representation of a progress report that can be validated, re-rendered, and shared without raw learner answers, full prompts, full feedback prose, or full event logs.
- **Report Request**: The user-selected report options, including export format and recap count.
- **Skill Review Finding**: A best-practice compliance observation for one project `SKILL.md`, including the source skill path, issue, recommended change, and whether implementation changed the skill.

## Constitution Alignment *(mandatory)*

- **Affected Layers**: Progress core aggregation, deterministic progress rendering, local repositories for existing learner state, report contracts and schema mirrors, `tutor-progress` skill and command surfaces, project skill documentation, and export validation. Host adapters remain out of scope.
- **Data Ownership**: Human-editable YAML remains limited to profile and preferences. Local transactional state remains the source for answer events, mistake events, vocabulary reviews, session summaries, skill metrics, costs, and due reviews. Phase 4 reports are derived views and exports, not a new editable source of truth.
- **Contract Surfaces**: Progress report contract, tag mastery summary contract, trend contract, session recap contract, report request options, Markdown export contract, JSON export contract, command result JSON, schema mirrors, and any migration only if existing stored state cannot represent required report facts.
- **Required Validation**: Unit tests for tag normalization, mastery categorization, trend construction, recap filtering, privacy filtering, and tie-break ordering; golden tests for progress Markdown and terminal text; contract tests for JSON export and command output; integration tests for one-year local history, no-data states, and existing progress behavior; skill-review checks against the required best-practice references; migration tests only if persisted shape changes.
- **Scope Guardrails**: Phase 4 is renderer and analysis surface work only. It does not add dashboards, graphical charts, GUI or web views, notifications, host adapters, audio, new exercise types, cloud sync, remote analytics, multi-user behavior, gamification, FSRS, alternate schedulers, or any raw/full-text export mode.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In deterministic fixtures with at least 12 practiced tags, 100% of tag mastery rows render with a category, recent evidence, and stable order across repeated runs.
- **SC-002**: In fixtures with mixed complete, interrupted, and invalid sessions, 100% of trend and recap output includes completed sessions only.
- **SC-003**: A learner can request a last-N recap for N values of 1, 5, 10, and 30 and receive no more than N completed sessions in 100% of fixtures.
- **SC-004**: Markdown and JSON exports contain the same report facts for summary, tag mastery, trend, recap, due counts, weak patterns, and cost in 100% of export fixtures.
- **SC-005**: Exported JSON validates and can be read back to reproduce the same report facts in 100% of round-trip fixtures.
- **SC-006**: Progress rendering and export output are byte-stable for identical learner state, request options, and current date in 100% of golden fixtures.
- **SC-007**: Progress views and all Phase 4 exports contain zero raw learner answers, full prompts, full feedback prose, or full event logs in privacy fixtures.
- **SC-008**: The standard progress view completes in under 5 seconds on a local fixture representing one year of daily completed sessions.
- **SC-009**: The rendered report remains understandable in a plain terminal with no color, emoji, image, browser, or GUI support.
- **SC-010**: Existing progress facts from Phase 1 and Phase 3 remain present in the richer report in 100% of regression fixtures.
- **SC-011**: 100% of project `SKILL.md` files are inventoried and either confirmed compliant or updated against the required skill-authoring references.

## Assumptions

- Phase 3 smarter-engine work is available, including active weak-tag summaries and deterministic local progress signals.
- Existing local history contains enough answer events, mistake events, vocabulary reviews, session summaries, skill metrics, due-review state, and cost records to derive reports without introducing a new data source.
- The learner is a single local user and wants reports for self-review, not multi-user analytics or cloud dashboards.
- Markdown and JSON are the only export formats for this phase.
- JSON export is for report portability and validation, not full learner-state backup or restore.
- Raw learner answers, full prompts, full feedback prose, and full event logs remain private even though the underlying local database still owns them.
