# Data Model: Smarter Engine

## WeakTagSignal

Derived from recent local session state. Not persisted as a dedicated table.

**Fields**:

- `tag`: normalized controlled tag string.
- `session_count`: number of considered sessions that contributed the tag; must be at least 2 to be active.
- `latest_seen_at`: latest event/review timestamp for this tag within the considered sessions.
- `priority_rank`: 1-based rank after frequency, recency, and tag tie-breaking.
- `source_counts`: learner-safe counts for `mistake_events` and `low_quality_reviews`.

**Relationships**:

- Reads `session_summaries.session_id` to define the recent completed analyzed session window.
- Reads `mistake_events.tag` for tagged mistake signals.
- Reads `vocabulary_reviews.quality` joined to `vocabulary_items.tags_json` for low-quality vocabulary-review signals.

**Validation rules**:

- Tags are normalized with the existing vocabulary tag normalization helper.
- Invalid/incomplete session analysis is ignored by requiring a `session_summaries` row.
- Top-level summaries expose at most 5 active signals.

## VocabularySelectionCandidate

Internal core model used to rank vocabulary items. It may include repository-only ordering fields but is not directly exposed to learners.

**Fields**:

- `item`: `VocabularyItem`.
- `normalized_tags`: normalized tags from `VocabularyItem.tags`.
- `due_at`: current due timestamp from `VocabularyItem.state`.
- `created_at`: stored row creation timestamp for stable tie-breaking.
- `is_new`: true when `VocabularyItem.state.state == "new"`.
- `is_due`: true when not new and `due_at <= now`.
- `is_overdue`: true when not new and `due_at.date() < now.date()` in UTC.
- `matched_weak_tags`: active weak tags intersecting normalized card tags.
- `matches_explicit_filter`: true when the card passed a requested tag filter.

**Relationships**:

- Built from `vocabulary_items`.
- Annotated with active `WeakTagSignal` values.

**Validation rules**:

- Explicit tag filters are applied before weak-tag annotation.
- Cards excluded by an explicit filter cannot be reintroduced by weak targeting.
- Existing cards with no tags are valid but cannot be weak-targeted.

## SelectionQueue

Validated response for `tutor vocab start`, represented by `VocabularySessionPlan`.

**Fields**:

- `items`: selected presentation-safe `VocabularyItem` entries.
- `requested_count`: raw requested or preference-derived count.
- `effective_count`: count after review-intensity multiplier and 60-card cap.
- `filter`: normalized explicit filter tags.
- `active_weak_tags`: active weak signals considered for this queue.
- `selection_reasons`: one `SelectionReason` per selected item.
- `starter_content_required`, `matching_count`, `due_matching_count`, `empty_reason`: existing Phase 2 fields retained for compatibility.

**State transitions**:

1. Build effective count from request/preference.
2. Fetch candidates inside explicit filter if present.
3. Partition into overdue due, due-today, future/not-due, and new.
4. Select due cards first.
5. Fill from new cards only if due cards do not fill the queue.
6. Render cloze cards through existing presentation path.

**Validation rules**:

- Queue order is deterministic for identical learner state and current time.
- Due reviews stay ahead of new cards.
- Weak-tag priority cannot break explicit filters.
- Queue size is at least 1 and at most 60 after intensity.

## SelectionReason

Learner-safe explanation attached to a selected card.

**Fields**:

- `item_id`: selected vocabulary card ID.
- `rank`: 1-based queue position.
- `bucket`: one of `overdue_due`, `due_today`, or `new_fill`.
- `reasons`: ordered reason labels such as `overdue`, `due`, `weak_tag_match`, `explicit_filter_match`, `reserved_non_weak_due`, `new_card_fill`.
- `matched_weak_tags`: normalized active weak tags matched by this card.
- `due_at`: due timestamp used for ordering.

**Validation rules**:

- Must not include raw learner answer text, full feedback prose, or event logs.
- `item_id` must appear in `SelectionQueue.items`.
- `matched_weak_tags` must be a subset of `active_weak_tags.tag`.

## ReviewIntensityPreference

Existing `LearnerPreferences.review_intensity`.

**Fields**:

- `review_intensity`: one of `light`, `normal`, `heavy`.
- `session_length`: configured base session length, 1 through 60.

**Rules**:

- `light`: effective count is 50% of session length, rounded like current queue sizing, minimum 1.
- `normal`: effective count is 100% of session length.
- `heavy`: effective count is 150% of session length.
- Final effective count is capped at 60.
- Intensity never changes SM-2 scheduling output.
- Missing intensity defaults to `normal`; unsupported intensity fails validation and is repaired through existing setup/YAML validation flows.

## SessionAnalysisSummary

Existing session-end analysis persisted through `session_summaries`.

**Fields used by this feature**:

- `session_id`: session identifier for joining to events/reviews.
- `summary_for_next_boot`: learner-safe recap.
- `weak_tags_json`: existing repeated-tag summary, retained for compatibility.
- `created_at`: recent-window ordering.

**Rules**:

- Only sessions with a persisted summary are eligible for weak-tag calculation.
- A maximum of 10 recent completed analyzed sessions are considered.
- Invalid or missing analysis falls back to baseline due-first selection.

## VocabularyCardTag

Normalized label on a vocabulary card.

**Fields**:

- `display_tag`: stored card tag as entered/imported.
- `normalized_tag`: normalized value used for matching filters and weak signals.

**Rules**:

- A card matches weak targeting when at least one normalized tag matches an active weak tag.
- Multiple matching tags increase reason detail but do not duplicate the card.
- Untagged cards remain selectable as due or new cards.

## Storage Mapping

No new SQLite table is planned.

- `vocabulary_items`: source for cards, tags, state, due timestamps, created ordering, and new/due buckets.
- `vocabulary_reviews`: source for low-quality review signals and SM-2 invariance fixtures.
- `mistake_events`: source for tagged mistake signals.
- `session_summaries`: source for recent completed analyzed session window.
- `preferences.yaml`: source for review intensity and session length.

If implementation later requires a schema change, add `migrations/003_smarter_engine.sql` and update migration tests. Current design does not require one.
