CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  host TEXT NOT NULL,
  host_conversation_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('open', 'closed')),
  started_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  closed_at TEXT,
  CHECK ((status = 'closed' AND closed_at IS NOT NULL) OR (status = 'open' AND closed_at IS NULL))
);

CREATE INDEX IF NOT EXISTS idx_sessions_last_seen ON sessions(last_seen_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);

CREATE TABLE IF NOT EXISTS checkpoints (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES sessions(id),
  modality TEXT NOT NULL CHECK (modality IN ('lesson', 'reading', 'transcript', 'vocab', 'writing', 'progress')),
  step_kind TEXT NOT NULL CHECK (step_kind IN ('started', 'prompt_shown', 'feedback_shown', 'progress_shown')),
  prompt_ref TEXT,
  state_json TEXT NOT NULL,
  summary TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_checkpoints_session ON checkpoints(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_checkpoints_created ON checkpoints(created_at);
