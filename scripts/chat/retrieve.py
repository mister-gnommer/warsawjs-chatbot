import os

import psycopg
from dotenv import load_dotenv

from shared.embedding import embed_texts

load_dotenv()


def _db_conn() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def search_similar(
    query: str,
    top_k: int = 5,
    threshold: float = 0.5,
) -> list[dict]:
    query_embedding = embed_texts([query], show_progress_bar=False)[0]
    conn = _db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    t.speaker,
                    t.title,
                    c.text,
                    1 - (c.embedding <=> %s::vector) AS similarity
                FROM chunks c
                JOIN talks t ON t.id = c.talk_id
                WHERE 1 - (c.embedding <=> %s::vector) >= %s
                ORDER BY similarity DESC
                LIMIT %s
                """,
                (query_embedding, query_embedding, threshold, top_k),
            )
            return [
                {
                    "speaker": row[0],
                    "title": row[1],
                    "chunk_text": row[2],
                    "similarity": row[3],
                }
                for row in cur
            ]
    finally:
        conn.close()
