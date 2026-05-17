# AGENTS.md — WarsawJS Chatbot

This is a **learning project**. The goal is to build a CLI tool that answers
questions about WarsawJS meetup talks using embeddings + LLM.

## Project vision

- User asks natural language questions, e.g. "if and when WarsawJS had talks
  about NestJS"
- A CLI tool retrieves relevant talk descriptions from a pgvector database
- Retrieved context is sent to an LLM to generate the answer

## Stack (planned)

- PostgreSQL with pgvector (Docker)
- Embeddings + LLM calls
- CLI tool (language TBD)
- Scripts to parse scraped talk data into structured JSON

## Guidelines

- This is for learning — experimentation and iteration are encouraged
- Keep documentation updated as understanding evolves
- Pin exact dependency versions everywhere
- Use `yyyy-MM-dd` for dates in code/data; `yyyyMMdd` for file/directory names
- Add `// 🤖 AI-generated` marker at top of new AI-written files
- Wrap AI-generated code blocks in `// 🤖 AI-start` / `// 🤖 AI-end` fences
  for non-trivial changes
- Run tests before any commit
