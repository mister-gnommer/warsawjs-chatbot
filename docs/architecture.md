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

The embed stage accepts a `--override-duplicates` flag:
- **false** (default): query pgvector for existing records by `(speaker, title)`,
  skip those already present before calling the embedding API
- **true**: skip the DB check, embed everything (previous chunks are deleted)

This avoids wasting embedding API calls on duplicates while letting the user
force a full re-embed when needed (e.g., after changing the embedding model).

## 7. Chunking

Talk descriptions are chunked before embedding to improve retrieval precision.

The chunker uses a recursive approach:
1. Split on `\n\n` paragraph boundaries
2. Paragraphs under the char limit stay whole
3. Longer paragraphs are split on sentence boundaries (`[.?!]\s+`)
4. If a single sentence still exceeds the limit, it's split on word boundaries

The char limit is ~500 (`all-MiniLM-L6-v2` context ~256 tokens).

Each chunk is stored as a separate row in the `chunks` table with its own
embedding, linked to the parent talk via FK. Retrieval returns the parent
talk's full description regardless of which chunk matched.

Chunks do **not** overlap. Since splitting happens at sentence or paragraph
boundaries, each fragment is self-contained — overlap would add storage cost
with no retrieval benefit.

## 8. Embedding model

`sentence-transformers` with `all-MiniLM-L6-v2` (384 dims). Runs in-process as
a Python library — no separate server, no API key.

Ollama stays in `docker-compose.yml` to serve a 3B chat model for the CLI app
(not used by the ingest pipeline).

## 9. Database

PostgreSQL 17 with pgvector 0.8.0, running in Docker. Schema is created on
container start via `db/init.sql`.

Connection is configured via environment variables (see `.env.example`).

Two tables:
- `talks` — speaker, title, description, meta JSONB, timestamps. No embedding
  column (embeddings live on chunks).
- `chunks` — FK to talks, text fragment, VECTOR(384) embedding, timestamps.

Vector dimension is 384 (matching `all-MiniLM-L6-v2`).

## 10. Language

Python for ingest scripts. Stdlib only until a dependency is actually needed.
