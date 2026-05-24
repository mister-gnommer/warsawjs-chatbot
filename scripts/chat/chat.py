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
    console.print("Meta+Enter to submit. /quit to exit.\n")

    while True:
        text = read_input(session)
        if text is None:
            break

        if not text.strip():
            continue

        # TODO: show progress indicators (e.g. "Embedding query...", "Searching...", "Generating answer...")
        try:
            results = search_similar(text, top_k=TOP_K, threshold=SIMILARITY_THRESHOLD)
        except Exception as exc:
            console.print(f"[red]Search failed: {exc}[/red]")
            continue

        # TODO: add fallback — ask LLM without context instead of skipping
        if not results:
            console.print("[yellow]No relevant talks found.[/yellow]")
            continue

        context = build_context(results)
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": build_prompt(context)},
            {"role": "user", "content": text},
        ]

        try:
            for token in ask_llm(messages):
                print(token, end="", flush=True)
            print()
        except Exception as exc:
            console.print(f"\n[red]LLM request failed: {exc}[/red]")
            continue

        show_sources(results)


if __name__ == "__main__":
    main()
