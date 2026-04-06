-- Align DB schema with SQLAlchemy app.schema.chat.Message (messages.user_id).
-- Apply against the same Postgres as DATABASE_URL (e.g. Supabase pooler).
-- No Alembic in this repo: run manually once, e.g.:
--   psql "$DATABASE_URL" -f migrations/001_add_messages_user_id.sql
-- or Supabase SQL Editor: paste and run.

ALTER TABLE messages
  ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Attach messages to the session owner (correct owner for normal chat rows).
UPDATE messages m
SET user_id = s.user_id
FROM sessions s
WHERE m.session_id = s.id
  AND (m.user_id IS DISTINCT FROM s.user_id);

CREATE INDEX IF NOT EXISTS ix_messages_user_id ON messages(user_id);

-- Optional: if sessions table lacked user_id (older DB), un-comment:
-- ALTER TABLE sessions ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);
