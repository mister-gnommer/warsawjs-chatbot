# WarsawJS Chatbot

A CLI tool that answers questions about WarsawJS meetup talks using semantic
search and LLMs.

Talks are embedded into a PostgreSQL + pgvector database. User questions are
matched against the embeddings to find relevant context, which is then sent to
an LLM for a natural-language answer.

## Ingest pipeline

Scraped talk descriptions go into `scripts/ingest/input/` as text files.
Run the pipeline to parse them into structured JSON:

```
python scripts/ingest/ingest.py
```

By default the future embedding stage will skip records already in the
database. To force a full re-embed:

```
python scripts/ingest/ingest.py --override-duplicates
```

## Status

🚧 Learning project — early prototyping.

### Potential refactors

- **`scripts/ingest/stages/embed.py`** — the file mixes SQL, embedding logic, and
  orchestration in a single module. If it grows significantly, consider splitting
  into infra (DB), service (embedding), and orchestration layers — not before.
