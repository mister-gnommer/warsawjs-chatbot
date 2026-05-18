# 🤖 AI-generated
import re

# all-MiniLM-L6-v2 has a 256-token context window
# ~500 chars is a safe upper bound
MAX_CHUNK_CHARS = 500


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.?!])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _accumulate_sentences(sentences: list[str]) -> list[str]:
    chunks = []
    current = ""

    for sentence in sentences:
        candidate = (current + " " + sentence).strip() if current else sentence
        if len(candidate) <= MAX_CHUNK_CHARS:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # sentence alone exceeds MAX_CHUNK_CHARS — force split by words
            if len(sentence) > MAX_CHUNK_CHARS:
                words = sentence.split()
                current = ""
                for word in words:
                    candidate = (current + " " + word).strip() if current else word
                    if len(candidate) <= MAX_CHUNK_CHARS:
                        current = candidate
                    else:
                        chunks.append(current)
                        current = word
            else:
                current = sentence

    if current:
        chunks.append(current)

    return chunks


def chunk_text(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    for para in paragraphs:
        if len(para) <= MAX_CHUNK_CHARS:
            chunks.append(para)
        else:
            sentences = _split_sentences(para)
            chunks.extend(_accumulate_sentences(sentences))

    return chunks
