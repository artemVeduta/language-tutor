# Quickstart: Smarter Engine

## Goal

Verify that Phase 3 changes make vocabulary selection weak-aware and deterministic while preserving SM-2 scheduling behavior.

## Setup

Use local fixtures only. Keep all commands repo-rooted and RTK-prefixed.

```bash
rtk pytest tests/unit/test_vocab_selection.py
```

## Expected Implementation Flow

1. Add Pydantic contracts for weak-tag signals, selection reasons, and extended `VocabularySessionPlan`.
2. Add repository read methods for recent completed analyzed sessions and vocabulary selection candidates.
3. Add core weak-tag derivation and deterministic queue selection.
4. Update `tutor vocab start` JSON and schema export.
5. Update boot-context/progress weak-pattern summary to reuse the same weak-signal helper.
6. Add tests before implementation for weak ranking, queue order, explicit filters, intensity cap, and SM-2 invariance.

## Verification Commands

```bash
rtk pytest tests/unit/test_vocab_selection.py tests/unit/test_schemas.py tests/unit/test_repositories.py tests/unit/test_srs.py
rtk pytest tests/golden/test_boot_context.py tests/golden/test_vocab_feedback.py
rtk pytest tests/adapter_contract/test_vocab_cli.py tests/adapter_contract/test_cli_json_contract.py
rtk pytest tests/integration/test_vocabulary_flow.py
rtk pytest tests/migration/test_migrations.py
rtk pyright
rtk ruff check .
```

## Acceptance Fixtures

- Repeated `case` mistakes in two recent sessions and competing due cards: weak-tag due card changes selected queue compared with due-date-only baseline.
- One-off weak tag in one recent session: no active weak signal.
- Overdue card plus weak-tag due-today card: overdue card ranks first.
- Due queue with at least two due slots and non-weak due card: one due slot remains reserved for highest-ranked non-weak due card.
- Explicit tag filter `aspect`: all selected cards contain normalized `aspect`, even when active weak tag is `case`.
- Due pool smaller than queue size: weak-tagged new cards fill before unrelated new cards.
- Missing/invalid session analysis: selection falls back to existing due-first behavior.
- Same learner state and frozen `now`: 100 repeated queue builds return identical IDs and reasons.
- Same SM-2 previous state, verdict, and review timestamp across all intensities: schedule output is identical.

## Out Of Scope Checks

Do not add or test FSRS, alternate scheduling algorithms, dashboards, exports, host adapters, audio, cloud sync, gamification, bundled curricula, or unrelated writing-feedback changes for this feature.
