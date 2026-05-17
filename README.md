# WarsawJS Chatbot

A CLI tool that answers questions about WarsawJS meetup talks using semantic
search and LLMs.

Talks are embedded into a PostgreSQL + pgvector database. User questions are
matched against the embeddings to find relevant context, which is then sent to
an LLM for a natural-language answer.

## Status

🚧 Learning project — early prototyping.
