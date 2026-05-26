import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table
from openai.types.chat import ChatCompletionMessageParam

from chat.config import SIMILARITY_THRESHOLD, TOP_K
from chat.llm import ask_llm
from chat.repl import create_repl, read_input
from chat.retrieve import search_similar

SYSTEM_PROMPT = """You are a WarsawJS meetup assistant. Answer questions about WarsawJS meetup talks using only the context below. If the context doesn't contain enough information to answer, say "I don't know". Cite the speaker and talk title when relevant.

Context:
{context}"""

FALLBACK_PROMPT = "You are a WarsawJS meetup assistant. No relevant talks were found for this question. If you don't know the answer, say so honestly."

console = Console()


def build_context(chunks: list[dict]) -> str:
    lines = []
    for i, r in enumerate(chunks, 1):
        lines.append(f"{i}. {r['speaker']} \u2014 \"{r['title']}\": {r['chunk_text']}")
    return "\n".join(lines)


def build_prompt(context: str) -> str:
    return SYSTEM_PROMPT.replace("{context}", context)


def show_sources(chunks: list[dict]) -> None:
    table = Table(title="Sources", show_header=True, header_style="bold")
    table.add_column("#", style="dim")
    table.add_column("Speaker")
    table.add_column("Talk")
    table.add_column("Score")
    for i, r in enumerate(chunks, 1):
        table.add_row(str(i), r["speaker"], r["title"], f"{r['similarity']:.2f}")
    console.print(table)


def main() -> None:
    session = create_repl()
    console.print("WarsawJS Chatbot \u2014 ask me about meetup talks", style="bold")
    console.print("Enter to submit, Meta+Enter for newline. /quit to exit.\n")

    while True:
        text = read_input(session)
        if text is None:
            break

        if not text.strip():
            continue

        try:
            with console.status("[dim]Searching...[/dim]"):
                results = search_similar(text, top_k=TOP_K, threshold=SIMILARITY_THRESHOLD)
        except Exception as exc:
            console.print(f"[red]Search failed: {exc}[/red]")
            continue

        if results:
            prompt = build_prompt(build_context(results))
        else:
            prompt = FALLBACK_PROMPT

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ]

        try:
            token_iter = ask_llm(messages)
            with console.status("[dim]Generating answer...[/dim]"):
                first_token = next(token_iter)
            print(first_token, end="", flush=True)
            for token in token_iter:
                print(token, end="", flush=True)
            print()
        except Exception as exc:
            console.print(f"\n[red]LLM request failed: {exc}[/red]")
            continue

        if results:
            show_sources(results)


if __name__ == "__main__":
    main()
