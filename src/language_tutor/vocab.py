from __future__ import annotations

import json
import re
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

from language_tutor.errors import TutorError
from language_tutor.feedback import vocabulary_feedback
from language_tutor.schemas import (
    LearnerPreferences,
    SeedImportEntryResult,
    SeedImportRequest,
    SeedImportResult,
    VocabularyAnswerInput,
    VocabularyAnswerResult,
    VocabularyCardAddResult,
    VocabularyCardDefinition,
    VocabularyDrillRequest,
    VocabularyItem,
    VocabularyReviewHistory,
    VocabularyReviewHistoryRequest,
    VocabularySessionPlan,
)
from language_tutor.srs import quality_for_verdict, schedule_review

if TYPE_CHECKING:
    from language_tutor.dal.repositories import TutorRepository


APOSTROPHE_VARIANTS = str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "＇": "'"})
CLOZE_MARKER = "{{answer}}"


def queue_size(preferences: LearnerPreferences) -> int:
    multiplier = {"light": 0.5, "normal": 1.0, "heavy": 1.5}[str(preferences.review_intensity)]
    return max(1, round(preferences.session_length * multiplier))


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).translate(APOSTROPHE_VARIANTS).casefold()
    text = re.sub(r"\s+", " ", text.strip())
    while text and unicodedata.category(text[0]).startswith("P"):
        text = text[1:].strip()
    while text and unicodedata.category(text[-1]).startswith("P"):
        text = text[:-1].strip()
    return text


def normalize_tag(value: str) -> str:
    return normalize_text(value)


def dedupe_key(card_type: str, target: str, prompt: str) -> str:
    return f"{card_type}:{normalize_text(target)}:{normalize_text(prompt)}"


def dedupe_key_for_item(item: VocabularyItem) -> str:
    return dedupe_key(item.card_type, item.lemma or item.prompt, item.prompt)


def merge_display_values(existing: list[str], incoming: list[str]) -> tuple[list[str], bool]:
    merged = list(existing)
    seen = {normalize_text(value) for value in existing}
    changed = False
    for value in incoming:
        key = normalize_text(value)
        if key and key not in seen:
            merged.append(value.strip())
            seen.add(key)
            changed = True
    return merged, changed


def merge_tags(existing: list[str], incoming: list[str]) -> tuple[list[str], bool]:
    merged = list(existing)
    seen = {normalize_tag(value) for value in existing}
    changed = False
    for value in incoming:
        key = normalize_tag(value)
        if key and key not in seen:
            merged.append(value.strip())
            seen.add(key)
            changed = True
    return merged, changed


def normalized_tag_filter(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        key = normalize_tag(tag)
        if key and key not in seen:
            normalized.append(key)
            seen.add(key)
    if not normalized:
        raise TutorError("invalid_vocab_filter", "Tag filter is empty.", "Pass at least one tag.")
    return normalized


def cloze_prompt(prompt: str) -> str:
    return prompt.replace(CLOZE_MARKER, "____")


def cloze_reveal(prompt: str, answer: str) -> str:
    return prompt.replace(CLOZE_MARKER, answer)


def presentation_item(item: VocabularyItem) -> VocabularyItem:
    if item.card_type != "cloze":
        return item
    return item.model_copy(update={"prompt": cloze_prompt(item.prompt)})


def item_from_definition(
    definition: VocabularyCardDefinition, target_language: str, item_id: str
) -> VocabularyItem:
    return VocabularyItem(
        id=item_id,
        card_type=definition.card_type,
        target_language=target_language,
        prompt=definition.prompt,
        lemma=definition.target,
        accepted_answers=definition.accepted_answers,
        hint=definition.hint,
        notes=definition.notes_list(),
        sources=definition.sources_list(),
        tags=definition.tags,
    )


def start_vocab(
    repo: TutorRepository,
    target_language: str,
    preferences: LearnerPreferences,
    request: VocabularyDrillRequest | None = None,
) -> VocabularySessionPlan:
    limit = request.requested_count if request and request.requested_count else queue_size(preferences)
    now = datetime.now(UTC)
    filter_tags = normalized_tag_filter(request.tags) if request and request.tags is not None else []
    if filter_tags:
        items, matching_count, due_matching_count = repo.due_vocabulary_by_tags(
            limit, now, filter_tags
        )
        empty_reason = None
        if not items:
            empty_reason = "no_matching_cards" if matching_count == 0 else "matching_cards_not_due"
        return VocabularySessionPlan(
            items=[presentation_item(item) for item in items],
            requested_count=limit,
            filter=filter_tags,
            matching_count=matching_count,
            due_matching_count=due_matching_count,
            empty_reason=empty_reason,
        )

    items = repo.due_vocabulary(limit, now)
    if not items:
        repo.seed_default_vocabulary(target_language)
        items = repo.due_vocabulary(limit, datetime.now(UTC))
    return VocabularySessionPlan(
        items=[presentation_item(item) for item in items],
        requested_count=limit,
        starter_content_required=not bool(items),
    )


def add_vocab_card(
    repo: TutorRepository,
    definition: VocabularyCardDefinition,
    target_language: str,
) -> VocabularyCardAddResult:
    item = item_from_definition(definition, target_language, repo.create_id("vocab"))
    existing_id = repo.find_vocabulary_duplicate(item)
    if existing_id is not None:
        return VocabularyCardAddResult(
            status="duplicate",
            item_id=existing_id,
            duplicate=True,
            message="Duplicate card rejected.",
            repair_hint="Use a different target, prompt, or card_type.",
        )
    item_id = repo.insert_vocabulary_item(item)
    return VocabularyCardAddResult(
        status="created", item_id=item_id, duplicate=False, message="Card created."
    )


def import_seed_list(
    repo: TutorRepository,
    request: SeedImportRequest,
    target_language: str,
) -> SeedImportResult:
    path = Path(request.path)
    if path.suffix != ".json":
        raise TutorError("invalid_seed_path", "Seed path must be a .json file.", "Pass a JSON file.")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TutorError(
            "seed_file_unreadable", "Seed file cannot be read.", "Check the path and permissions."
        ) from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TutorError(
            "invalid_seed_json", "Seed file is not valid JSON.", "Fix JSON syntax and retry."
        ) from exc
    if not isinstance(payload, list):
        raise TutorError("invalid_seed_json", "Seed JSON must be a list.", "Use a top-level list.")
    if not payload:
        raise TutorError("empty_seed_json", "Seed list is empty.", "Add at least one card object.")

    entries: list[SeedImportEntryResult] = []
    seed_entries = cast(list[object], payload)
    for index, raw_entry in enumerate(seed_entries):
        if not isinstance(raw_entry, dict):
            entries.append(
                SeedImportEntryResult(
                    index=index,
                    status="invalid",
                    code="invalid_seed_entry",
                    message="Seed entry must be an object.",
                    repair_hint="Use a JSON object for each card.",
                )
            )
            continue
        try:
            definition = VocabularyCardDefinition.model_validate(raw_entry)
            item = item_from_definition(definition, target_language, repo.create_id("vocab"))
            status, item_id = repo.import_vocabulary_item(item)
            entries.append(SeedImportEntryResult(index=index, status=status, item_id=item_id))
        except Exception as exc:  # noqa: BLE001
            entries.append(
                SeedImportEntryResult(
                    index=index,
                    status="invalid",
                    code="invalid_seed_entry",
                    message="Seed entry failed validation.",
                    repair_hint=str(exc),
                )
            )
    return SeedImportResult(
        path=str(path),
        created_count=sum(entry.status == "created" for entry in entries),
        updated_count=sum(entry.status == "updated" for entry in entries),
        skipped_count=sum(entry.status == "skipped" for entry in entries),
        invalid_count=sum(entry.status == "invalid" for entry in entries),
        entries=entries,
    )


def answer_vocab(
    repo: TutorRepository, payload: VocabularyAnswerInput, preferences: LearnerPreferences
) -> VocabularyAnswerResult:
    item = repo.get_vocabulary_item(payload.item_id)
    feedback = vocabulary_feedback(
        payload.answer, item.accepted_answers, preferences.transliteration_tolerance
    )
    if item.card_type == "cloze":
        reveal = cloze_reveal(item.prompt, item.lemma or item.accepted_answers[0])
        feedback = feedback.model_copy(
            update={
                "cloze_sentence": reveal,
                "accepted_answer": item.accepted_answers[0],
                "explanation": f"{feedback.explanation} Sentence: {reveal}",
            }
        )
    next_state = schedule_review(item.state, feedback.verdict)
    quality = quality_for_verdict(feedback.verdict)
    return repo.record_vocab_answer(
        item=item,
        session_id=payload.session_id,
        answer=payload.answer,
        idempotency_key=payload.idempotency_key,
        feedback=feedback,
        previous_state=item.state,
        next_state=next_state,
        quality=quality,
    )


def review_history(
    repo: TutorRepository, request: VocabularyReviewHistoryRequest
) -> VocabularyReviewHistory:
    return repo.vocabulary_review_history(request.item_id, datetime.now(UTC))
