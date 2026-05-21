# Feature Specification: Smarter Engine

**Feature Branch**: `003-smarter-engine`

**Created**: 2026-05-21

**Status**: Draft

**Input**: User description: "Phase 3 from docs/ROADMAP.md: Smarter Engine. Core analysis depth. No host dependency. SM-2 stays the only algorithm; FSRS remains out of scope. Richer SessionAnalysis uses cross-session weak-tag targeting for the next due queue, adaptive item selection biases due and new items by weak-pattern signals, and SM-2 parameter tuning is surfaced through preferences. Exit gate: weak-tag targeting changes surfaced cards, deterministic selection golden-tested, SM-2 math unchanged."

## Clarifications

### Session 2026-05-21

- Q: What cap should weak-tag targeting use so weak-tagged due cards bias selection without monopolizing due review slots? → A: Reserve one due slot for a non-weak due card when at least two due slots and non-weak due cards exist.
- Q: Which data should count toward a weak tag appearing in a session? → A: Tagged mistake events plus vocabulary reviews with SM-2 quality below 3 count.
- Q: How should review intensity affect the selected queue size? → A: Session length is the normal target: light selects 50%, normal 100%, heavy 150%, capped at 60 cards.
- Q: Within the due-review pool, should weak-tag priority outrank due-date urgency? → A: Overdue cards rank first by due date; weak-tag priority ranks within the non-overdue due-card group.
- Q: How many active weak tags may appear in the next-session summary? → A: Top 5 active weak tags.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Target Recurring Weak Tags (Priority: P1)

A learner who repeatedly misses the same grammar, vocabulary, or spelling tags across sessions gets future vocabulary practice biased toward cards that can exercise those weak areas.

**Why this priority**: Phase 3 must turn stored learning history into better next-session choices, not just reports after the fact.

**Independent Test**: Can be tested by recording multiple sessions with repeated weak tags, starting a limited vocabulary drill with enough due cards to require selection, and confirming weak-tag-matching due cards replace otherwise eligible non-matching due cards.

**Acceptance Scenarios**:

1. **Given** a learner has at least two recent sessions with the same weak tag, **When** the learner starts a vocabulary drill with more due cards than the session can show, **Then** due cards matching that weak tag are selected ahead of comparable due cards without that tag.
2. **Given** weak tags exist from prior sessions, **When** the next session context is prepared, **Then** it includes a compact ranked summary of active weak tags without raw answer text or full feedback history.
3. **Given** prior sessions contain one-off weak tags that do not repeat, **When** weak targeting is calculated, **Then** those low-signal tags do not displace cards tied to recurring weak tags.
4. **Given** no recurring weak tags are available, **When** the learner starts a drill, **Then** the tutor keeps the existing due-first selection behavior.

---

### User Story 2 - Adapt Due And New Item Selection (Priority: P1)

A learner's limited session queue balances overdue reviews, weak-tag practice, and new cards so the session feels focused without hiding urgent reviews.

**Why this priority**: The engine should use analysis to choose better practice items while preserving the learner's trust in due reviews.

**Independent Test**: Can be tested with a fixture containing overdue cards, due cards with weak tags, due cards without weak tags, and new cards with and without weak tags, then verifying the selected queue order and contents are deterministic.

**Acceptance Scenarios**:

1. **Given** overdue cards and weak-tag due cards are both available, **When** the tutor builds a session queue, **Then** overdue cards remain eligible and weak targeting only ranks within the allowed due-review pool.
2. **Given** the due-review pool does not fill the learner's session length, **When** new cards are added to the queue, **Then** new cards matching active weak tags are preferred over unrelated new cards.
3. **Given** the learner explicitly starts a tag-filtered drill, **When** weak targeting is active, **Then** the explicit tag filter remains a hard boundary and weak targeting only ranks cards inside that filter.
4. **Given** identical learner state and the same current time, **When** the tutor builds a selection queue repeatedly, **Then** the selected cards and order are identical.

---

### User Story 3 - Tune Review Intensity Safely (Priority: P2)

A learner can choose how aggressive daily review should feel while the underlying SM-2 scheduling results remain stable and explainable.

**Why this priority**: Review intensity already exists as a learner preference; Phase 3 must make its effect clear and deterministic without introducing a new scheduling algorithm.

**Independent Test**: Can be tested by setting each supported intensity, building queues from the same learning state, answering the same cards with the same outcomes, and confirming queue size or selection pressure changes while next-review calculations stay unchanged for identical item state and answer quality.

**Acceptance Scenarios**:

1. **Given** the learner sets a light review intensity, **When** a session queue is prepared, **Then** the tutor favors a smaller, lower-pressure queue while still showing due reviews before new cards.
2. **Given** the learner sets a heavy review intensity, **When** a session queue is prepared, **Then** the tutor can include more due or weak-tag practice within the documented intensity cap.
3. **Given** two learners answer the same card with the same outcome but different intensity settings, **When** the next review state is calculated, **Then** the resulting SM-2 interval, ease factor, repetition count, and due date are the same.
4. **Given** a missing intensity setting, **When** preferences are loaded, **Then** the tutor uses the documented normal default.
5. **Given** an unsupported intensity setting, **When** preferences are loaded, **Then** validation rejects the value and reports repair guidance through existing setup or validation flows.

### Edge Cases

- Weak tags repeat across old sessions but are absent from the most recent practice window.
- Weak tags come from writing mistakes but no vocabulary cards share those tags.
- Multiple weak tags compete for a queue that can only show a few cards.
- A card has several tags and matches more than one active weak tag.
- Explicit tag filters conflict with active weak tags.
- The due pool contains fewer cards than the learner's configured session length.
- All weak-tag cards are not due yet.
- New cards match weak tags but the due pool already fills the queue.
- Session analysis is missing, invalid, incomplete, or from an interrupted session.
- Learner preferences contain an unsupported review intensity.
- Existing cards have no tags because they were created before vocabulary tagging.
- Multiple cards tie on due date, weak-tag score, and creation time.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST identify active weak tags from recent completed sessions using tagged mistake events and vocabulary reviews whose SM-2 quality is below 3.
- **FR-002**: System MUST require a weak tag to appear in at least two recent completed sessions before it can influence future item selection.
- **FR-003**: System MUST rank active weak tags by session frequency descending, most recent occurrence descending, and normalized tag name ascending so identical learner state produces identical rankings.
- **FR-004**: System MUST include up to the top 5 active weak tags in the next-session learning context as a compact summary of tag names, relative priority, and next-focus guidance.
- **FR-005**: System MUST NOT include raw learner answer text, full feedback prose, or complete event logs in the weak-tag summary used for the next session.
- **FR-006**: System MUST use active weak tags to bias vocabulary due-item selection when the number of eligible due cards exceeds the session queue size.
- **FR-007**: System MUST keep due reviews ahead of new cards; weak targeting MUST NOT show new cards before eligible due cards when due cards can fill the queue.
- **FR-008**: System MUST prefer new cards matching active weak tags over unrelated new cards only when the due-review pool leaves room for new cards.
- **FR-009**: System MUST preserve explicit learner tag filters as hard boundaries; weak targeting MAY only rank cards that already match the learner-selected filter.
- **FR-010**: System MUST handle cards with multiple tags by counting a card as weak-targeted when it matches at least one active weak tag.
- **FR-011**: System MUST reserve one due slot for the highest-ranked non-weak due card when the due selection has at least two due slots and at least one non-weak eligible due card.
- **FR-012**: System MUST provide a deterministic item-selection order for all ties: due-card ties use due timestamp before stored creation order, while new-card ties with no due timestamp start at stored creation order; both chains end with normalized prompt text and item ID.
- **FR-013**: System MUST preserve existing unfiltered vocabulary drill behavior when no active weak tags exist.
- **FR-014**: System MUST surface review intensity preferences with documented learner-facing meanings for light, normal, and heavy review.
- **FR-015**: System MUST use review intensity to adjust selected queue size from the learner's configured session length: light selects 50%, normal selects 100%, and heavy selects 150%, with effective queue size calculated as `min(60, max(1, round(session_length * multiplier)))`.
- **FR-016**: System MUST keep SM-2 scheduling calculations unchanged for the same previous card state, answer outcome, and review time, regardless of review intensity.
- **FR-017**: System MUST default missing review intensity values to normal and reject unsupported review intensity values through existing preference validation or repair flows.
- **FR-018**: System MUST maintain compatibility with existing vocabulary cards, review history, answer events, mistake events, session summaries, and preference files.
- **FR-019**: System MUST keep all Phase 3 workflows local-first and host-independent.
- **FR-020**: System MUST NOT add FSRS, alternate scheduling algorithms, cloud sync, dashboards, gamification, audio, new hosts, or new exercise modalities.
- **FR-021**: System MUST expose selection decisions in validated machine-readable output so tests and future user-facing summaries can explain why a card was selected.
- **FR-022**: System MUST keep weak-tag targeting bounded to the recent-practice window so next-session context remains within the established context budget; the weak-tag summary cap is defined by FR-004.

### Requirement Details

- Recent weak-tag targeting considers the 10 most recent completed analyzed sessions after excluding missing, invalid, incomplete, or interrupted session analyses. If fewer than 10 valid completed analyzed sessions exist, all valid completed analyzed sessions are considered.
- A weak tag is active when it appears in at least two considered sessions. A session contributes a weak tag when it contains a tagged mistake event or a vocabulary review with SM-2 quality below 3 whose reviewed card has that normalized tag. Tags from invalid or incomplete session analysis are ignored.
- Weak-tag priority is based on session frequency first, then most recent occurrence, then tag name for stable ties.
- The next-session weak-tag summary includes only the top 5 active weak tags by priority.
- A card is weak-targeted when at least one of its normalized tags matches an active weak tag.
- Selection remains due-first: eligible due cards are selected before new cards, and new cards are considered only when the due pool does not fill the session queue.
- Within eligible due cards, overdue cards rank first by due date. Weak-tag priority applies within due cards that are due but not overdue.
- Weak-tag due selection reserves one due slot for the highest-ranked non-weak due card when at least two due slots and non-weak eligible due cards exist; otherwise weak-tag ranking may fill the available due slots.
- After bucket rules, weak-tag priority, and reserved non-weak due-slot rules are applied, remaining due-card ties resolve by due timestamp ascending, stored creation timestamp ascending, normalized prompt text ascending, then item ID ascending. New-card ties with no due timestamp resolve by stored creation timestamp ascending, normalized prompt text ascending, then item ID ascending.
- Explicit tag filters remain strict: a card excluded by the learner's selected filter cannot be reintroduced by weak targeting.
- The learner-facing intensity meanings are: light reduces daily pressure by selecting about half the configured session length, normal preserves the configured session length, and heavy allows up to 150% of the configured session length without exceeding 60 cards. Fractional queue sizes use the existing Python `round()` nearest-integer behavior and never select fewer than one card.
- SM-2 unchanged means the same previous state, answer outcome, and review timestamp produce the same next interval, ease factor, repetition count, state, and due date for every intensity setting.
- Selection explanations identify broad reasons such as overdue, due, weak-tag match, explicit filter match, and new-card fill. They do not expose private raw answers.

### Key Entities *(include if feature involves data)*

- **Weak Tag Signal**: A repeated learner weakness derived from recent completed sessions. It includes the tag name, session count, most recent occurrence, and priority.
- **Selection Queue**: The ordered set of vocabulary cards chosen for a practice session after due status, explicit filters, weak tags, new-card allowance, and intensity are applied.
- **Selection Reason**: A learner-safe explanation for why a card was selected or ranked, such as due review, weak-tag match, or new-card fill.
- **Review Intensity Preference**: A learner-controlled setting that changes session pressure and selection load without changing SM-2 review math.
- **Session Analysis Summary**: The validated end-of-session summary used to derive weak-tag signals and next-focus guidance.
- **Vocabulary Card Tag**: A normalized label on a card that can match an active weak tag or an explicit drill filter.

## Constitution Alignment *(mandatory)*

- **Affected Layers**: Vocabulary core selection, session analysis aggregation, boot-context summary, local repositories, preference validation, contract schemas, deterministic renderers, and vocabulary/progress skill surfaces that present selection results. Host adapters remain out of scope.
- **Data Ownership**: Human-editable preferences own the learner's review intensity. Local transactional learning state owns answer events, mistake events, vocabulary reviews, session summaries, weak-tag derived state, and selection decisions exposed through validated output. No cloud or remote storage is introduced.
- **Contract Surfaces**: Session analysis contract, weak-tag signal contract, selection queue contract, selection-reason output, preference contract, command result JSON, schema mirrors, and any local state migration needed to preserve existing data.
- **Required Validation**: Unit tests for weak-tag ranking, intensity validation, and SM-2 invariance; golden tests for deterministic selection and next-session context rendering; contract tests for selection output and preference handling; integration tests for cross-session targeting and explicit filter precedence; migration tests if stored selection or analysis shape changes.
- **Scope Guardrails**: Phase 3 deepens the existing engine only. It does not add FSRS, alternate scheduling, dashboards, host adapters, audio, reading, lessons, cloud sync, multi-user behavior, gamification, bundled curricula, or unrelated writing-feedback changes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In deterministic fixtures with recurring weak tags and competing due cards, weak-tag targeting changes at least one selected card compared with baseline due-date-only selection.
- **SC-002**: With identical learner state and current time, vocabulary selection returns the same card order in 100% of repeated runs.
- **SC-003**: Explicit tag-filtered drills contain only cards matching the selected filter in 100% of weak-targeting fixtures.
- **SC-004**: New weak-tag-matching cards are selected ahead of unrelated new cards in 100% of fixtures where due cards leave open queue slots.
- **SC-005**: For the same card state, answer outcome, and review time, SM-2 next-review outputs are identical across light, normal, and heavy intensity in 100% of scheduling fixtures.
- **SC-006**: The next-session weak-tag summary stays below the established context budget in 100% of fixtures containing 10 analyzed sessions and at least 25 weak-tag events.
- **SC-007**: Invalid or missing session analysis does not block vocabulary practice and produces baseline due-first selection in 100% of recovery fixtures.
- **SC-008**: A learner can complete two practice sessions with repeated weak tags and see targeted vocabulary selection in the following session without using any host-specific workflow.

## Assumptions

- Phase 2 vocabulary depth is complete, including card tags, tag-filtered drills, cloze cards, seed imports, and per-card review history.
- Existing answer events, mistake events, vocabulary reviews, and session summaries provide enough tag history to derive weak-tag signals.
- Weak targeting uses the existing controlled tag vocabulary and normalized card tags.
- Review intensity already exists as a learner preference and remains the learner-facing control for review pressure.
- The learner is a single local user, and all analysis stays on local learning state.
- The first Phase 3 implementation focuses on vocabulary selection. Existing boot and progress summaries may reuse the shared weak-tag signal helper to keep weak-tag rules single-source, but richer new progress reports and export remain Phase 4.
