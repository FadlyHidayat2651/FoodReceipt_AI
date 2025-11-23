# src/backend/db/init_vector_db.py
import os
from vector_service import VectorService

def init_vector_db(db_path="vector_db.pkl", embedding_model="all-MiniLM-L6-v2"):
    """
    Initialize vector DB (pickle file) using VectorService.
    Preloads embedding model.
    """
    if os.path.exists(db_path):
        print(f"Vector DB already exists at {db_path}")
    else:
        # Initialize VectorService which creates the pickle file and loads the embedding model
        vector_service = VectorService(db_path=db_path, embedding_model=embedding_model)
        vector_service._save()  # explicitly save empty vectors
        print(f"Vector DB initialized at {db_path} with embedding model '{embedding_model}'")

    # Preload embedding model even if DB exists
    print("Loading embedding model...")
    vector_service = VectorService(db_path=db_path, embedding_model=embedding_model)
    print("SentenceTransformer model loaded and ready.")

    return vector_service
