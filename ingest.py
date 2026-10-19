
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

with psycopg.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "resume_chatbot"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "1234"),
) as conn:
    rows = conn.execute("""
        SELECT metadata->>'source' AS source, COUNT(*) AS chunks
        FROM resume_chunks
        GROUP BY metadata->>'source'
        ORDER BY source;
    """).fetchall()

    print("\nChunks stored in PostgreSQL:\n")

    for source, count in rows:
        print(f"{source}: {count} chunks")

    total = conn.execute(
        "SELECT COUNT(*) FROM resume_chunks"
    ).fetchone()[0]

    print(f"\nTotal chunks: {total}")
