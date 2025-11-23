# src/backend/app/db/init_db.py
import sqlite3
import os
DB_PATH = "/app/src/backend/app/db/receipts.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_sqlite_db(db_path=DB_PATH):
    """
    Initialize the SQLite receipts database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create receipts table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            doc_id TEXT PRIMARY KEY,
            date_of_purchase TEXT,
            vendor TEXT,
            total_amount REAL,
            currency TEXT,
            items_json TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"SQLite DB initialized: {db_path}")
