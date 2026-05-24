import re

from stages.config import MAX_CHUNK_CHARS



def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.?!])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _accumulate_sentences(sentences: list[str], max_chars: int) -> list[str]:
    chunks = []
    current = ""

    for sentence in sentences:
        candidate = (current + " " + sentence).strip() if current else sentence
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(sentence) > max_chars:
                words = sentence.split()
                current = ""
                for word in words:
                    candidate = (current + " " + word).strip() if current else word
                    if len(candidate) <= max_chars:
                        current = candidate
                    else:
                        chunks.append(current)
                        current = word
            else:
                current = sentence

    if current:
        chunks.append(current)

    return chunks


def chunk_text(text: str, max_chars: int | None = None) -> list[str]:
    limit = max_chars if max_chars is not None else MAX_CHUNK_CHARS
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    for para in paragraphs:
        if len(para) <= limit:
            chunks.append(para)
        else:
            sentences = _split_sentences(para)
            chunks.extend(_accumulate_sentences(sentences, limit))

    return chunks
