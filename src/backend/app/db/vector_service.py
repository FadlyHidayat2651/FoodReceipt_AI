# src/backend/db/vector_service.py
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import os

DB_DIR = "/app/src/backend/app/db"
VECTOR_PATH = os.path.join(DB_DIR, "vector_db.pkl")

class VectorService:
    """
    Combined embedding generator + manual vector DB using numpy.
    Supports preloaded embedding model.
    """
    def __init__(self, db_path=VECTOR_PATH , embedding_model="all-MiniLM-L6-v2", model=None):
        self.db_path = db_path
        self.model = model or SentenceTransformer(embedding_model)
        
        # Load existing vectors or initialize empty dict
        if os.path.exists(db_path):
            try:
                with open(db_path, "rb") as f:
                    self.vectors = pickle.load(f)
            except Exception:
                print(f"Failed to load {db_path}, initializing empty vector DB.")
                self.vectors = {}
        else:
            self.vectors = {}

    # ---------------- Embedding ----------------
    def embed_text(self, text):
        """
        Convert text to deterministic embedding (numpy array)
        """
        return np.array(self.model.encode(text))

    # ---------------- VectorDB ----------------
    def add_vector(self, doc_id, text):
        """
        Generate embedding from text and store it in vector DB
        """
        vector = self.embed_text(text)
        self.vectors[doc_id] = vector
        self._save()
        return vector

    def query_vector(self, query_text, top_k=5):
        """
        Query top-k similar documents given a text
        """
        query_vector = self.embed_text(query_text)
        similarities = {}
        for doc_id, vec in self.vectors.items():
            if np.linalg.norm(vec) == 0 or np.linalg.norm(query_vector) == 0:
                sim = 0.0
            else:
                sim = np.dot(query_vector, vec) / (np.linalg.norm(vec) * np.linalg.norm(query_vector))
            similarities[doc_id] = sim

        # Return top_k sorted
        return sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]

    def _save(self):
        with open(self.db_path, "wb") as f:
            pickle.dump(self.vectors, f)
