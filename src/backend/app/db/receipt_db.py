# src/backend/db/receipt_db.py
import sqlite3
import json
from db.vector_service import VectorService
import os

DB_DIR = "/app/src/backend/app/db"
RECEIPT_PATH = os.path.join(DB_DIR, "receipts.db")

class ReceiptDB:
    """
    Handles SQLite receipt storage and optional embedding generation.
    """
    def __init__(self, db_path=RECEIPT_PATH, vector_service: VectorService = None):
        self.db_path = db_path
        self.vector_service = vector_service
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_table()

    def _init_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                doc_id TEXT PRIMARY KEY,
                date_of_purchase TEXT,
                vendor TEXT,
                total_amount REAL,
                currency TEXT,
                items_json TEXT
            )
        """)
        self.conn.commit()

    # ---------------- CRUD ----------------
    def add_receipt(self, doc_id, date, vendor, total, currency, items):
        self.cursor.execute("""
            INSERT OR REPLACE INTO receipts (doc_id, date_of_purchase, vendor, total_amount, currency, items_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, date, vendor, total, currency, json.dumps(items)))
        self.conn.commit()

        # Add vector if vector_service is provided
        if self.vector_service:
            text = f"Vendor: {vendor}, Items: {', '.join(items.keys())}, Total: {total} {currency}"
            self.vector_service.add_vector(doc_id, text)

    def get_receipt(self, doc_id):
        self.cursor.execute("SELECT * FROM receipts WHERE doc_id=?", (doc_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "doc_id": row[0],
            "date_of_purchase": row[1],
            "vendor": row[2],
            "total_amount": row[3],
            "currency": row[4],
            "items": json.loads(row[5])
        }

    def query_all_receipts(self):
        self.cursor.execute("SELECT * FROM receipts")
        rows = self.cursor.fetchall()
        return [
            {
                "doc_id": row[0],
                "date_of_purchase": row[1],
                "vendor": row[2],
                "total_amount": row[3],
                "currency": row[4],
                "items": json.loads(row[5])
            }
            for row in rows
        ]

    def close(self):
        self.conn.close()
