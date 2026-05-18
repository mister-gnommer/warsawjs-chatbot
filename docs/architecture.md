<!-- 🤖 AI-generated -->
# Architecture Decision Record — WarsawJS Chatbot

## 1. Ingest and app are separate components

The ingest pipeline (`scripts/ingest/`) and the CLI query tool are independent.
Different run frequencies, different concerns, no shared code.

## 2. Single-command pipeline

`ingest.py` orchestrates all stages internally (parse → embed → insert).
No manual intermediate steps. One command goes from raw file to database.

## 3. Checkpoint output

Parsed JSON is written to `output/talks.json`. Useful for debugging parsing
without re-running. Not consumed by later stages — they receive data in-memory.

## 4. Parser input format

Input: text files with entries delimited by lines starting with
`"Avatar of <speaker>"`. Speaker name is repeated on the next line (skipped).
Title on the following non-empty line. Everything else is the description.
Empty lines separate entries.

## 5. Output schema per entry

```
{speaker: str, title: str, description: str}
```

Description preserves paragraph breaks as `\n\n`.

## 6. Dedup at embed stage, not parse stage

Parse stage is dumb — it reads all files in `input/` and concatenates records.
Duplicates are neither checked nor removed at this stage.

The embed stage (future) will accept a `--override-duplicates` flag:
- **false** (default): query pgvector for existing records by `(speaker, title)`,
  skip those already present before calling the embedding API
- **true**: skip the DB check, embed everything

This avoids wasting embedding API calls on duplicates while letting the user
force a full re-embed when needed (e.g., after changing the embedding model).

## 7. Embedding model

`sentence-transformers` with `all-MiniLM-L6-v2` (384 dims). Runs in-process as
a Python library — no separate server, no API key.

Ollama stays in `docker-compose.yml` to serve a 3B chat model for the CLI app
(not used by the ingest pipeline).

## 8. Database

PostgreSQL 17 with pgvector 0.8.0, running in Docker. Schema is created on
container start via `db/init.sql`.

Connection is configured via environment variables (see `.env.example`).

A `meta JSONB` column is included in the talks table for ad-hoc metadata
(e.g. event date, meetup number, scraped-from URL). Adding extra fields there
doesn't require migrations.

Vector dimension is 384 (matching `all-MiniLM-L6-v2`).

## 9. Language

Python for ingest scripts. Stdlib only until a dependency is actually needed.
