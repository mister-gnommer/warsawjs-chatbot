import os
from dataclasses import dataclass

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from stages.chunk import chunk_text

SpeakerTitle = tuple[str, str]


@dataclass
class Talk:
    speaker: str
    title: str
    description: str


load_dotenv()

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _db_conn() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def _load_existing(conn: psycopg.Connection) -> set[SpeakerTitle]:
    with conn.cursor() as cur:
        cur.execute("SELECT speaker, title FROM talks")
        return {(speaker, title) for speaker, title in cur}


def _filter_new(
    records: list[Talk],
    existing: set[SpeakerTitle],
) -> list[Talk]:
    return [r for r in records if (r.speaker, r.title) not in existing]


def _generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


def _insert_talks(
    conn: psycopg.Connection,
    records: list[Talk],
) -> dict[SpeakerTitle, int]:
    talk_ids: dict[SpeakerTitle, int] = {}
    with conn.cursor() as cur:
        for record in records:
            cur.execute(
                """
                INSERT INTO talks (speaker, title, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (speaker, title) DO UPDATE
                    SET description = EXCLUDED.description
                RETURNING id
                """,
                (record.speaker, record.title, record.description),
            )
            row = cur.fetchone()
            assert row is not None, "INSERT … RETURNING id should always produce a row"
            talk_id = row[0]
            talk_ids[(record.speaker, record.title)] = talk_id
    conn.commit()
    return talk_ids


def _insert_chunks(
    conn: psycopg.Connection,
    items: list[tuple[int, str, list[float]]],
) -> None:
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks (talk_id, text, embedding) VALUES (%s, %s, %s)",
            items,
        )
    conn.commit()


def _remove_previous_chunks(conn: psycopg.Connection, talk_ids: list[int]) -> None:
    if not talk_ids:
        return
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM chunks WHERE talk_id = ANY(%s)",
            (talk_ids,),
        )
    conn.commit()


def _collect_ids_for_talks(
    conn: psycopg.Connection,
    records: list[Talk],
) -> list[int]:
    ids: list[int] = []
    with conn.cursor() as cur:
        for r in records:
            cur.execute(
                "SELECT id FROM talks WHERE speaker = %s AND title = %s",
                (r.speaker, r.title),
            )
            row = cur.fetchone()
            if row is not None:
                ids.append(row[0])
    return ids


def _process_chunks(
    conn: psycopg.Connection,
    talk_ids: dict[SpeakerTitle, int],
    records: list[Talk],
) -> int:
    chunk_items: list[tuple[int, str]] = []
    for record in records:
        tid = talk_ids[(record.speaker, record.title)]
        for c in chunk_text(record.description):
            chunk_items.append((tid, c))

    if not chunk_items:
        return 0

    talk_id_list, all_texts = zip(*chunk_items)
    print(f"[embed] generated {len(all_texts)} chunks from {len(records)} talks")
    print(f"[embed] generating embeddings for {len(all_texts)} chunks...")
    embeddings = _generate_embeddings(list(all_texts))

    db_items = list(zip(talk_id_list, all_texts, embeddings))
    _insert_chunks(conn, db_items)

    return len(all_texts)


def embed(records: list[Talk], override_duplicates: bool) -> int:
    conn = _db_conn()

    if override_duplicates:
        to_embed = list(records)
    else:
        to_embed = _filter_new(records, _load_existing(conn))

    if not to_embed:
        print("[embed] nothing new to embed")
        conn.close()
        return 0

    print(f"[embed] inserting {len(to_embed)} talk records...")

    if override_duplicates:
        existing_ids = _collect_ids_for_talks(conn, to_embed)
        if existing_ids:
            _remove_previous_chunks(conn, existing_ids)

    talk_ids = _insert_talks(conn, to_embed)

    chunk_count = _process_chunks(conn, talk_ids, to_embed)
    conn.close()

    print(f"[embed] inserted {len(to_embed)} talks and {chunk_count} chunks")
    return len(to_embed)
