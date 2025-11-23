# src/backend/db/init_all.py
import os
from init_db import init_sqlite_db
from init_vector_db import init_vector_db
from sentence_transformers import SentenceTransformer

if __name__ == "__main__":
    # Get the folder of this script
    DB_DIR = "/app/src/backend/app/db"
    os.makedirs(DB_DIR, exist_ok=True)

    # ---------------- SQLite DB ----------------
    SQLITE_DB_PATH = os.path.join(DB_DIR, "receipts.db")
    init_sqlite_db(db_path=SQLITE_DB_PATH)

    # ---------------- Vector DB ----------------
    VECTOR_DB_PATH = os.path.join(DB_DIR, "vector_db.pkl")
    init_vector_db(db_path=VECTOR_DB_PATH)

    # ---------------- Embedding Model ----------------
    print("Initializing embedding model...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("SentenceTransformer model loaded and ready.")

    print(f"SQLite DB and VectorDB initialized successfully in {DB_DIR}.")
