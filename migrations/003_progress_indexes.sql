CREATE INDEX IF NOT EXISTS idx_progress_sessions_created
  ON session_summaries(created_at DESC, session_id);

CREATE INDEX IF NOT EXISTS idx_progress_reviews_session_time
  ON vocabulary_reviews(session_id, reviewed_at);

CREATE INDEX IF NOT EXISTS idx_progress_mistakes_session_time
  ON mistake_events(session_id, created_at);

CREATE INDEX IF NOT EXISTS idx_progress_answers_session_skill_time
  ON answer_events(session_id, skill, recorded_at);

CREATE INDEX IF NOT EXISTS idx_progress_vocab_due_state
  ON vocabulary_items(due_at, state);
