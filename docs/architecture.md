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

## 6. Language

Python for ingest scripts. Stdlib only until a dependency is actually needed.
