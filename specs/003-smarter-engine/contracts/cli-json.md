# Contract: CLI JSON For Smarter Engine

## `tutor vocab start`

Starts a vocabulary queue using existing local profile, preferences, vocabulary cards, review history, and recent weak-tag signals.

### Request Payload

The positional payload remains optional JSON.

```json
{
  "tags": ["case", "aspect"],
  "requested_count": 10
}
```

**Fields**:

- `tags`: optional non-empty list of explicit tag filters. When present, this is a hard boundary.
- `requested_count`: optional positive integer. If omitted, the effective queue size is derived from `LearnerPreferences.session_length` and `review_intensity`.

### Success Response

Extends the existing `VocabularySessionPlan` response.

```json
{
  "items": [
    {
      "id": "vocab_001",
      "card_type": "standard",
      "target_language": "uk",
      "prompt": "Translate: book",
      "lemma": "книга",
      "accepted_answers": ["книга"],
      "hint": null,
      "notes": [],
      "sources": [],
      "tags": ["case"],
      "state": {
        "state": "review",
        "ease_factor": 2.5,
        "repetition_count": 2,
        "interval_days": 6,
        "due_at": "2026-05-21T09:00:00Z"
      }
    }
  ],
  "requested_count": 10,
  "effective_count": 10,
  "starter_content_required": false,
  "filter": ["case"],
  "matching_count": 12,
  "due_matching_count": 8,
  "empty_reason": null,
  "active_weak_tags": [
    {
      "tag": "case",
      "session_count": 3,
      "latest_seen_at": "2026-05-21T08:00:00Z",
      "priority_rank": 1,
      "source_counts": {
        "mistake_events": 4,
        "low_quality_reviews": 2
      }
    }
  ],
  "selection_reasons": [
    {
      "item_id": "vocab_001",
      "rank": 1,
      "bucket": "due_today",
      "reasons": ["due", "explicit_filter_match", "weak_tag_match"],
      "matched_weak_tags": ["case"],
      "due_at": "2026-05-21T09:00:00Z"
    }
  ],
  "selection_policy": {
    "due_first": true,
    "weak_tag_limit": 5,
    "recent_session_limit": 10,
    "reserved_non_weak_due_slot": true,
    "intensity": "normal"
  }
}
```

### Invariants

- `items[*].id` order is the practice order.
- `selection_reasons` has exactly one entry per selected item.
- Every `selection_reasons[*].item_id` appears in `items`.
- `active_weak_tags` contains at most 5 entries.
- `effective_count` is between 1 and 60.
- Due cards appear before new cards.
- Explicit filter tags are hard boundaries.
- Response must not include raw learner answer text, full feedback prose, or event logs.

### Error Behavior

- Invalid payload shape returns existing `invalid_vocab_start`.
- Invalid or empty `tags` returns existing `invalid_vocab_filter`.
- Unsupported preference values surface through existing YAML/setup validation errors before queue selection.

## `tutor boot-context`

Boot context includes a compact weak-tag summary derived from the same weak-signal helper.

### Invariants

- Weak-pattern section includes at most top 5 active weak tags.
- Summary contains tag names, relative priority, and next-focus guidance only.
- Summary excludes raw answers, full feedback prose, and complete event logs.

## Compatibility

Existing consumers that read only `items`, `requested_count`, `filter`, `matching_count`, `due_matching_count`, `empty_reason`, or `starter_content_required` continue to work. New fields are additive in the Pydantic/JSON schema contract for Phase 3.
