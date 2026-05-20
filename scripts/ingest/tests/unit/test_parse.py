from pathlib import Path

from stages.embed import Talk
from stages.parse import parse

INPUT_DIR = Path(__file__).resolve().parent.parent.parent / "input"

SINGLE_TALK_INPUT = """Avatar of John Doe
John Doe
My Great Talk
Lorem ipsum dolor sit amet consectetur adipiscing elit.
"""

SINGLE_TALK_EXPECTED = Talk(
    speaker="John Doe",
    title="My Great Talk",
    description="Lorem ipsum dolor sit amet consectetur adipiscing elit.",
)

MULTIPLE_TALKS_INPUT = """Avatar of Alice
Alice
Talk One
Lorem ipsum dolor sit amet.

Avatar of Bob
Bob
Talk Two
Consectetur adipiscing elit sed do eiusmod tempor.
"""

MULTIPLE_TALKS_EXPECTED = [
    Talk(speaker="Alice", title="Talk One", description="Lorem ipsum dolor sit amet."),
    Talk(speaker="Bob", title="Talk Two", description="Consectetur adipiscing elit sed do eiusmod tempor."),
]

MULTI_PARAGRAPH_INPUT = """Avatar of Charlie
Charlie
My Talk
Lorem ipsum dolor sit amet consectetur adipiscing elit.

Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

Ut enim ad minim veniam quis nostrud exercitation ullamco laboris.
"""

MULTI_PARAGRAPH_EXPECTED_DESC = (
    "Lorem ipsum dolor sit amet consectetur adipiscing elit.\n\n"
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n\n"
    "Ut enim ad minim veniam quis nostrud exercitation ullamco laboris."
)

LEADING_GARBAGE_INPUT = """Some random junk before the first entry.

Avatar of Eve
Eve
The Real Talk
Lorem ipsum dolor sit amet consectetur.
"""

LEADING_GARBAGE_EXPECTED = Talk(
    speaker="Eve",
    title="The Real Talk",
    description="Lorem ipsum dolor sit amet consectetur.",
)

BLANK_LINES_INPUT = (
    "Avatar of A\nA\nTitle A\nDesc A.\n\n\n\n\n"
    "Avatar of B\nB\nTitle B\nDesc B.\n"
)

BLANK_LINES_EXPECTED = [
    Talk(speaker="A", title="Title A", description="Desc A."),
    Talk(speaker="B", title="Title B", description="Desc B."),
]

MULTI_LINE_DESC_INPUT = """Avatar of Speaker
Speaker
Title
First line of description.
Second line of description.
Third line.
"""

MULTI_LINE_DESC_EXPECTED = (
    "First line of description.\n"
    "Second line of description.\n"
    "Third line."
)


def test_single_talk():
    assert parse(SINGLE_TALK_INPUT) == [SINGLE_TALK_EXPECTED]


def test_multiple_talks():
    assert parse(MULTIPLE_TALKS_INPUT) == MULTIPLE_TALKS_EXPECTED


def test_multi_paragraph_description():
    result = parse(MULTI_PARAGRAPH_INPUT)
    assert len(result) == 1
    assert result[0].description == MULTI_PARAGRAPH_EXPECTED_DESC


def test_empty_input():
    assert parse("") == []


def test_empty_input_with_whitespace():
    assert parse("   \n  \n  ") == []


def test_talk_without_title():
    result = parse("Avatar of Jane\nJane")
    assert result == [Talk(speaker="Jane", title="", description="")]


def test_leading_garbage_skipped():
    result = parse(LEADING_GARBAGE_INPUT)
    assert len(result) == 1
    assert result[0] == LEADING_GARBAGE_EXPECTED


def test_multiple_blank_lines_between_entries():
    assert parse(BLANK_LINES_INPUT) == BLANK_LINES_EXPECTED


def test_talk_with_multi_line_description():
    result = parse(MULTI_LINE_DESC_INPUT)
    assert result[0].description == MULTI_LINE_DESC_EXPECTED


def test_full_sample_file():
    file_path = INPUT_DIR / "tmp-example-data.md"
    raw = file_path.read_text(encoding="utf-8")
    result = parse(raw)
    assert len(result) == 26
    assert result[0].speaker == "Łukasz Rybka"
    assert result[0].title == "Breaking Into Tech in the Age of AI: Why It's Getting Harder for Junior Developers"
    assert result[5].speaker == "Gideon Awolesi"
    assert result[5].title == "Classifying Intelligence: Mental Models for Designing AI Products"
