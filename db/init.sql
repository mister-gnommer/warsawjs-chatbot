CREATE EXTENSION IF NOT EXISTS vector;

-- 384 dims matches all-MiniLM-L6-v2 from sentence-transformers
DROP TABLE IF EXISTS talks CASCADE;
CREATE TABLE talks (
    id          SERIAL PRIMARY KEY,
    speaker     TEXT NOT NULL,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    meta        JSONB NOT NULL DEFAULT '{}',   -- flexible: date, meetup #, URL, etc.
    embedding   VECTOR(384),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (speaker, title)
);

CREATE INDEX IF NOT EXISTS idx_talks_speaker_title ON talks (speaker, title);
