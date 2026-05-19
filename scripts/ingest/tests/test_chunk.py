# 🤖 AI-generated
from stages.chunk import chunk_text


def test_short_text_stays_whole():
    text = "A single short paragraph."
    chunks = chunk_text(text)
    assert chunks == [text]


def test_paragraph_boundary_splits():
    text = "First paragraph.\n\nSecond paragraph."
    chunks = chunk_text(text)
    assert chunks == ["First paragraph.", "Second paragraph."]


def test_long_paragraph_splits_by_sentence():
    text = (
        "First sentence here. "
        "Second sentence here too. "
        "Third sentence is also here. "
        "Fourth and final sentence ends here."
    )
    chunks = chunk_text(text, max_chars=100)
    assert chunks == [
        "First sentence here. Second sentence here too. Third sentence is also here.",
        "Fourth and final sentence ends here.",
    ]


def test_overlong_sentence_splits_by_word():
    text = (
        "A very very very very very very very very "
        "very very very very very very long sentence "
        "without any punctuation at all"
    )
    chunks = chunk_text(text, max_chars=50)
    assert len(chunks) >= 2
    assert all(len(c) <= 50 for c in chunks)


def test_empty_string():
    assert chunk_text("") == []


def test_exactly_at_limit_stays_whole():
    text = "A" * 500
    chunks = chunk_text(text)
    assert chunks == [text]


def test_one_over_limit_splits():
    text = "A" * 501
    chunks = chunk_text(text)
    assert len(chunks) == 2


def test_mixed_short_and_long_paragraphs():
    short = "Short paragraph one."
    long_para = (
        "This is a much longer paragraph that will need to be "
        "split because it exceeds the maximum character limit "
        "when passed with a small max_chars value. "
        "Second sentence in this long paragraph. "
        "Third sentence that finishes the paragraph."
    )
    text = f"{short}\n\n{long_para}"
    chunks = chunk_text(text, max_chars=80)
    assert chunks[0] == short
    assert len(chunks) >= 2


def test_paragraph_boundary_respected_in_long_text():
    text = "Short one.\n\n" + "A" * 600 + "\n\nAnother short."
    chunks = chunk_text(text)
    assert chunks[0] == "Short one."
    assert chunks[-1] == "Another short."
