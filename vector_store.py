import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_DIR = os.path.join(BASE_DIR, "Metadata")
INDEX_PATH = os.path.join(METADATA_DIR, "faiss.index")
METADATA_PATH = os.path.join(METADATA_DIR, "metadata.json")
MODEL_INFO_PATH = os.path.join(METADATA_DIR, "model_info.json")

class VectorStore:
    def __init__(self):
        self.model = None
        self.index = None
        self.metadata = []
        self.model_name = None

    def load(self):
        print("Loading Vector Store...")
        
        # Load Model Info if available
        if os.path.exists(MODEL_INFO_PATH):
            with open(MODEL_INFO_PATH, "r", encoding="utf-8") as f:
                info = json.load(f)
                self.model_name = info.get("model", self.model_name)
        
        print(f"Loading Model: {self.model_name}")
        self.model = SentenceTransformer(
            self.model_name,
            device="cpu",
            trust_remote_code=True
        )
        # CRITICAL FIX FOR NV-Embed-v2 (as per user script, keeping it safe)
        # Check if attribute exists before setting to avoid errors if model structure differs
        try:
            if hasattr(self.model, "_first_module"):
                first_mod = self.model._first_module()
                if hasattr(first_mod, "auto_model") and hasattr(first_mod.auto_model, "config"):
                     first_mod.auto_model.config.use_cache = False
        except Exception as e:
            print(f"Warning: Could not set use_cache=False: {e}")

        # Load Index
        if os.path.exists(INDEX_PATH):
            print(f"Loading FAISS Index from {INDEX_PATH}")
            self.index = faiss.read_index(INDEX_PATH)
        else:
            raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")

        # Load Metadata
        if os.path.exists(METADATA_PATH):
            print(f"Loading Metadata from {METADATA_PATH}")
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            raise FileNotFoundError(f"Metadata not found at {METADATA_PATH}")
        
        print("Vector Store Loaded Successfully.")

    def search(self, query: str, threshold: float = 0.4, top_k: int = 5):
        if not self.model or not self.index:
            raise RuntimeError("VectorStore is not loaded. Call load() first.")

        # Encode query
        print(f"DEBUG: Encoding query: '{query}'")
        query_vector = self.model.encode([query], normalize_embeddings=True)
        query_vector = np.asarray(query_vector, dtype="float32")
        print(f"DEBUG: Query Vector Shape: {query_vector.shape}")

        # Search
        distances, indices = self.index.search(query_vector, top_k)
        
        print(f"DEBUG: Raw Distances: {distances}")
        print(f"DEBUG: Raw Indices: {indices}")

        results = []
        found_tables = set()

        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                print(f"DEBUG: Skipping Invalid Index {idx}")
                continue
            
            print(f"DEBUG: Checking Index {idx}, Distance: {dist}, Threshold: {threshold}")
            
            if dist < threshold:
                print(f"DEBUG: Distance {dist} < Threshold {threshold} -> REJECTED")
                continue
            
            meta = self.metadata[idx]
            table_name = meta.get("table_name")
            
            if table_name and table_name not in found_tables:
                results.append(table_name)
                found_tables.add(table_name)
                print(f"DEBUG: Found Table: {table_name}")

        print(f"DEBUG: Final Results: {results}")
        return list(results)

# Global Instance
vector_store = VectorStore()
