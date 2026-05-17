CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS talks (
    id          SERIAL PRIMARY KEY,
    speaker     TEXT NOT NULL,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    meta        JSONB NOT NULL DEFAULT '{}',   -- flexible: date, meetup #, URL, etc.
    embedding   VECTOR(1536),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (speaker, title)
);

CREATE INDEX IF NOT EXISTS idx_talks_speaker_title ON talks (speaker, title);
