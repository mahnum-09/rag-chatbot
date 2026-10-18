
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conninfo = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "resume_chatbot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

try:
    with psycopg.connect(**conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print("PostgreSQL:", cur.fetchone()[0])

            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
            result = cur.fetchone()
            print("pgvector version:", result[0] if result else "Not enabled")

            cur.execute("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'resume_chunks'
                ORDER BY ordinal_position;
            """)
            print("\nresume_chunks columns:")
            for row in cur.fetchall():
                print(row)

    print("\nDatabase connection successful!")

except Exception as e:
    print("Connection failed:", e)
