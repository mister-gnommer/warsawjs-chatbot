import os

from dotenv import load_dotenv
import psycopg
from sentence_transformers import SentenceTransformer

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


def _load_existing(conn: psycopg.Connection) -> set[tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute("SELECT speaker, title FROM talks")
        return set(cur)


def _filter_new(
    records: list[dict],
    existing: set[tuple[str, str]],
) -> list[dict]:
    return [
        r for r in records
        if (r["speaker"], r["title"]) not in existing
    ]


def _generate_embeddings(records: list[dict]) -> list[list[float]]:
    descriptions = [r["description"] for r in records]
    if not descriptions:
        return []

    model = _get_model()
    embeddings = model.encode(descriptions, show_progress_bar=True)
    return embeddings.tolist()


def _insert_records(
    conn: psycopg.Connection,
    records: list[dict],
    embeddings: list[list[float]],
) -> None:
    with conn.cursor() as cur:
        for record, embedding in zip(records, embeddings):
            cur.execute(
                """
                INSERT INTO talks (speaker, title, description, embedding)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (speaker, title) DO NOTHING
                """,
                (record["speaker"], record["title"], record["description"], embedding),
            )
    conn.commit()


def embed(records: list[dict], override_duplicates: bool) -> int:
    conn = _db_conn()

    to_embed = records if override_duplicates else _filter_new(records, _load_existing(conn))
    skipped = len(records) - len(to_embed)

    if skipped:
        print(f"[embed] {skipped} records already in DB, skipped")

    if not to_embed:
        print("[embed] nothing new to embed")
        conn.close()
        return 0

    print(f"[embed] generating embeddings for {len(to_embed)} records...")
    embeddings = _generate_embeddings(to_embed)

    _insert_records(conn, to_embed, embeddings)
    conn.close()

    print(f"[embed] inserted {len(to_embed)} records into database")
    return len(to_embed)
