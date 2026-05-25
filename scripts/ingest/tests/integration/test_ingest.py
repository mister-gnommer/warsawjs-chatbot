import os

import psycopg
import pytest
from stages.embed import Talk, embed

TEST_DB = "warsawjs_test"

TEST_TALKS = [
    Talk(
        speaker="Alice",
        title="Talk One",
        description="Lorem ipsum dolor sit amet consectetur adipiscing elit.",
    ),
    Talk(
        speaker="Bob",
        title="Talk Two",
        description="Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    ),
]

# Long enough to produce more than 1 chunk per talk at MAX_CHUNK_CHARS=500
LONG_DESC = "Lorem ipsum dolor sit amet consectetur adipiscing elit. " * 50

TALKS_WITH_LONG_DESC = [
    Talk(speaker="Alice", title="Talk One", description=LONG_DESC),
    Talk(speaker="Bob", title="Talk Two", description=LONG_DESC),
]


def _db_conn():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=TEST_DB,
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


@pytest.fixture(autouse=True)
def use_test_db():
    old = os.environ.get("DB_NAME")
    os.environ["DB_NAME"] = TEST_DB
    yield
    if old:
        os.environ["DB_NAME"] = old
    else:
        del os.environ["DB_NAME"]
    conn = _db_conn()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE talks CASCADE")
    conn.commit()
    conn.close()


def test_inserts_talks_and_chunks():
    count = embed(TEST_TALKS, override_duplicates=False)
    assert count == 2

    conn = _db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT speaker, title, description FROM talks ORDER BY id")
        rows = cur.fetchall()
        assert len(rows) == 2
        assert rows[0] == (
            TEST_TALKS[0].speaker,
            TEST_TALKS[0].title,
            TEST_TALKS[0].description,
        )
        assert rows[1] == (
            TEST_TALKS[1].speaker,
            TEST_TALKS[1].title,
            TEST_TALKS[1].description,
        )

        cur.execute("SELECT COUNT(*) FROM chunks")
        row = cur.fetchone()
        assert row is not None
        assert row[0] == 4  # 2 title chunks + 2 description chunks
    conn.close()


def test_dedup_skips_existing():
    embed(TEST_TALKS, override_duplicates=False)
    count = embed(TEST_TALKS, override_duplicates=False)
    assert count == 0


def test_override_duplicates_rechunks():
    embed(TEST_TALKS, override_duplicates=False)

    conn = _db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, length(description) FROM talks WHERE speaker = 'Alice'")
        row = cur.fetchone()
        assert row is not None
        talk_id, short_len = row
    conn.close()

    embed(TALKS_WITH_LONG_DESC, override_duplicates=True)

    conn = _db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, length(description) FROM talks WHERE speaker = 'Alice'")
        row = cur.fetchone()
        assert row is not None
        assert row[0] == talk_id
        assert row[1] > short_len

        cur.execute("SELECT text FROM chunks WHERE length(text) > 200 LIMIT 1")
        row = cur.fetchone()
        assert row is not None
        assert len(row[0]) > 200
    conn.close()


def test_embed_empty_records():
    count = embed([], override_duplicates=False)
    assert count == 0
