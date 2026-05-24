from collections.abc import Generator

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from chat.config import OLLAMA_BASE_URL, OLLAMA_MODEL

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    return _client


def ask_llm(messages: list[ChatCompletionMessageParam]) -> Generator[str, None, None]:
    client = _get_client()
    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        stream=True,
    )
    for chunk in response:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
