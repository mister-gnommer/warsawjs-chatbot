# 🤖 AI-generated
from pathlib import Path

from stages.embed import Talk
from stages.parse import parse

INPUT_DIR = Path(__file__).resolve().parent.parent / "input"


SINGLE_TALK = """Avatar of John Doe
John Doe
My Great Talk
A description of the great talk.
"""


MULTIPLE_TALKS = """Avatar of Alice
Alice
Talk One
Description one.

Avatar of Bob
Bob
Talk Two
Description two.
"""


MULTI_PARAGRAPH_DESC = """Avatar of Charlie
Charlie
My Talk
First paragraph of the description.

Second paragraph after a blank line.

Third and final paragraph.
"""

LEADING_GARBAGE = """This is some random text before the first entry.

Avatar of Eve
Eve
The Real Talk
Description here.
"""


def test_single_talk():
    result = parse(SINGLE_TALK)
    assert result == [
        Talk(speaker="John Doe", title="My Great Talk", description="A description of the great talk."),
    ]


def test_multiple_talks():
    result = parse(MULTIPLE_TALKS)
    assert len(result) == 2
    assert result[0] == Talk(speaker="Alice", title="Talk One", description="Description one.")
    assert result[1] == Talk(speaker="Bob", title="Talk Two", description="Description two.")


def test_multi_paragraph_description():
    result = parse(MULTI_PARAGRAPH_DESC)
    assert len(result) == 1
    assert result[0].description == (
        "First paragraph of the description.\n\n"
        "Second paragraph after a blank line.\n\n"
        "Third and final paragraph."
    )


def test_empty_input():
    assert parse("") == []


def test_empty_input_with_whitespace():
    assert parse("   \n  \n  ") == []


def test_talk_without_title():
    text = "Avatar of NoTitle\nNoTitle"
    result = parse(text)
    assert result == [Talk(speaker="NoTitle", title="", description="")]


def test_leading_garbage_skipped():
    result = parse(LEADING_GARBAGE)
    assert len(result) == 1
    assert result[0] == Talk(speaker="Eve", title="The Real Talk", description="Description here.")


def test_multiple_blank_lines_between_entries():
    text = "Avatar of A\nA\nTitle A\nDesc A.\n\n\n\n\nAvatar of B\nB\nTitle B\nDesc B.\n"
    result = parse(text)
    assert len(result) == 2


def test_talk_with_multi_line_description():
    text = """Avatar of Speaker
Speaker
Title
First line of the description.
Second line of the description.
Third line.
"""
    result = parse(text)
    assert result[0].description == "First line of the description.\nSecond line of the description.\nThird line."


def test_full_sample_file():
    file_path = INPUT_DIR / "tmp-example-data.md"
    raw = file_path.read_text(encoding="utf-8")
    result = parse(raw)
    assert len(result) == 26
    assert result[0].speaker == "Łukasz Rybka"
    assert result[0].title == "Breaking Into Tech in the Age of AI: Why It's Getting Harder for Junior Developers"
    assert result[5].speaker == "Gideon Awolesi"
    assert result[5].title == "Classifying Intelligence: Mental Models for Designing AI Products"
