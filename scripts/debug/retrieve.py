#!/usr/bin/env python3
"""Debug tool for inspecting vector similarity search results.

Usage:
    python scripts/debug/retrieve.py "your query here"

Shows the top 5 matching chunks with full text, similarity scores, and chunk sizes.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from shared.embedding import embed_texts

load_dotenv()
console = Console()


def _db_conn() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def _count_words(text: str) -> int:
    return len(text.split())


def search_top_k(
    query: str,
    k: int = 5,
) -> list[dict]:
    query_embedding = embed_texts([query], show_progress_bar=False)[0]
    conn = _db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    t.speaker,
                    t.title,
                    c.text,
                    1 - (c.embedding <=> %s::vector) AS similarity
                FROM chunks c
                JOIN talks t ON t.id = c.talk_id
                ORDER BY similarity DESC
                LIMIT %s
                """,
                (query_embedding, k),
            )
            return [
                {
                    "speaker": row[0],
                    "title": row[1],
                    "chunk_text": row[2],
                    "similarity": row[3],
                }
                for row in cur
            ]
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Debug vector similarity search — shows top 5 matching chunks"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Search query (e.g. talk title or topic)",
    )
    args = parser.parse_args()

    query = args.query.strip()
    if not query:
        console.print("[red]Query is empty or whitespace-only[/red]")
        sys.exit(1)

    console.print(f"[bold]Query:[/bold] {query}")
    console.print(f"[bold]Query length:[/bold] {len(query)} chars")

    console.print("\n[bold]Embedding query...[/bold]")
    query_embedding = embed_texts([query], show_progress_bar=False)[0]
    console.print("[bold]Embedding dims:[/bold] 384")
    console.print(f"[bold]Vector preview:[/bold] [{', '.join(f'{v:.4f}' for v in query_embedding[:3])}, ...]")

    console.print("\n[bold]Searching pgvector...[/bold]")
    try:
        results = search_top_k(query, k=5)
    except Exception as exc:
        console.print(f"[red]Search failed: {exc}[/red]")
        sys.exit(1)

    if not results:
        console.print("[yellow]No chunks found in the database[/yellow]")
        sys.exit(0)

    console.print(f"\n[bold]Found {len(results)} matches[/bold]\n")

    # Summary table
    summary = Table(show_header=True, header_style="bold")
    summary.add_column("#", style="dim", width=3)
    summary.add_column("Speaker", width=18)
    summary.add_column("Talk", width=35)
    summary.add_column("Score", width=8, justify="right")
    summary.add_column("Chars", width=6, justify="right")
    summary.add_column("Words", width=6, justify="right")

    for i, r in enumerate(results, 1):
        chunk_text = r["chunk_text"]
        summary.add_row(
            str(i),
            r["speaker"][:18],
            r["title"][:35],
            f"{r['similarity']:.4f}",
            str(len(chunk_text)),
            str(_count_words(chunk_text)),
        )

    console.print(summary)

    # Full details for each match
    console.print("\n[bold]Full chunk details:[/bold]\n")
    for i, r in enumerate(results, 1):
        console.print(f"[bold]#{i}[/bold] — {r['speaker']} | [italic]{r['title']}[/italic]")
        console.print(f"    Score: {r['similarity']:.4f} | Chars: {len(r['chunk_text'])} | Words: {_count_words(r['chunk_text'])}")
        console.print(f"    ━" * 40)
        console.print(r["chunk_text"])
        console.print()


if __name__ == "__main__":
    main()
