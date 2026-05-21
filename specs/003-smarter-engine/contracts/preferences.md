# Contract: Review Intensity Preferences

## Source

`LearnerPreferences` from `preferences.yaml`.

```yaml
schema_version: 1
session_length: 10
review_intensity: normal
```

## Allowed Values

| Value | Meaning | Effective queue size |
|-------|---------|----------------------|
| `light` | Lower-pressure review | 50% of `session_length`, minimum 1 |
| `normal` | Preserve configured session length | 100% of `session_length` |
| `heavy` | More aggressive review | 150% of `session_length` |

Final effective queue size is capped at 60 cards.

## Validation Rules

- Missing `review_intensity` uses the Pydantic default `normal`.
- Unsupported `review_intensity` values fail preference validation.
- Repair guidance uses existing setup/YAML validation flows.
- Intensity affects selection size only.
- Intensity must not affect SM-2 interval, ease factor, repetition count, state, or due date.

## Contract Tests

- `light`, `normal`, and `heavy` produce documented queue sizes for fixed session lengths.
- Heavy intensity with `session_length: 60` caps at 60 cards.
- Unsupported values fail validation.
- Identical SM-2 inputs produce identical scheduling outputs across all intensity values.
