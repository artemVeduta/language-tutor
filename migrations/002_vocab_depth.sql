ALTER TABLE vocabulary_items
  ADD COLUMN card_type TEXT NOT NULL DEFAULT 'standard'
  CHECK (card_type IN ('standard', 'cloze'));

ALTER TABLE vocabulary_items
  ADD COLUMN notes_json TEXT NOT NULL DEFAULT '[]';

ALTER TABLE vocabulary_items
  ADD COLUMN sources_json TEXT NOT NULL DEFAULT '[]';

UPDATE vocabulary_items
SET dedupe_key = 'standard:' || lower(trim(coalesce(lemma, prompt))) || ':' || lower(trim(prompt));
