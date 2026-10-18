
import os
from dotenv import load_dotenv
import psycopg
from sentence_transformers import SentenceTransformer

# 1. Load database settings from .env
load_dotenv()

# 2. Connect to PostgreSQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# 3. Load the same embedding model used during ingestion
print("Loading embedding model...")
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

def search_documents(question, top_k=3):
    # 4. Convert the question into a 384-dimensional vector
    query_embedding = model.encode(question)
    embedding_string = str(query_embedding.tolist())

    # 5. Search for the most similar document chunks
    sql = """
        SELECT
            content,
            metadata,
            embedding <=> %s::vector AS distance
        FROM resume_chunks
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (embedding_string, embedding_string, top_k)
            )
            results = cur.fetchall()

    # 6. Display the retrieved chunks
    if not results:
        print("No matching document chunks found.")
        return

    print(f"\nQuestion: {question}")
    print(f"Top {len(results)} relevant results:\n")

    for i, (content, metadata, distance) in enumerate(results, 1):
        metadata = metadata or {}
        source = metadata.get("source", "Unknown source")
        similarity = 1 - float(distance)

        print("=" * 60)
        print(f"Result {i}")
        print(f"Source: {source}")
        print(f"Cosine similarity: {similarity:.4f}")
        print("\nContent:")
        print(content)
        print()

if __name__ == "__main__":
    question = input("Enter your question: ").strip()

    if question:
        search_documents(question)
    else:
        print("Please enter a question.")
