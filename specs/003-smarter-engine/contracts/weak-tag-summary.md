# Contract: Weak Tag Summary

## WeakTagSignal

```json
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
```

## Source Window

- Consider the last 10 completed analyzed sessions.
- A completed analyzed session is represented by a persisted `session_summaries` row.
- If fewer than 10 completed analyzed sessions exist, consider all of them.
- Ignore invalid, incomplete, or missing analysis.

## Contribution Rules

A session contributes a tag when at least one of these is true:

- The session has a `mistake_events` row with that normalized tag.
- The session has a `vocabulary_reviews` row with `quality < 3` and the reviewed `vocabulary_items.tags_json` contains that normalized tag.

Each session contributes a given tag at most once to `session_count`.

## Active Tag Rules

- A tag is active only when `session_count >= 2`.
- Active tags rank by `session_count` descending, then `latest_seen_at` descending, then `tag` ascending.
- Summary output includes at most top 5 active tags.

## Privacy And Context Rules

Weak-tag summaries may include:

- Tag names.
- Relative priority.
- Safe counts.
- Next-focus guidance.

Weak-tag summaries must not include:

- Raw learner answer text.
- Full feedback prose.
- Complete event logs.
- Unbounded history.
