"""
ai_engine.py

This module defines the AIEngine class, which provides functionality for indexing
and querying textual documents using sentence embeddings. It is designed for 
applications like a recipe recommender, where each recipe is represented as a text
document and similarity-based search is required.

Key features:
- Index a list of documents (each a dictionary with 'id' and 'text')
- Cache embeddings to disk for faster subsequent loads
- Query documents based on cosine similarity with a text input
- Supports top-k retrieval of most relevant documents

Dependencies:
- sentence_transformers: for computing embeddings and cosine similarity
- numpy: for handling vector operations
- pickle: for caching embeddings
- pathlib: for handling file paths
"""
from __future__ import annotations
from typing import List, Dict, Optional, Tuple
import pathlib
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer, util

EMBED_CACHE = pathlib.Path(__file__).resolve().parents[1] / "data" / "embeddings.pkl"

class AIEngine:
    """
    AIEngine indexes and searches textual documents using sentence embeddings.

    Attributes:
        model_name (str): Name of the SentenceTransformer model to use for embeddings.
        model (SentenceTransformer): The instantiated sentence transformer model.
        docs (List[Dict[str, str]]): List of indexed documents.
        embeddings (Optional[np.ndarray]): Embedding vectors corresponding to `docs`.

    Methods:
        index(docs, force_recompute=False):
            Compute and cache embeddings for a list of documents.
        query(text, top_k=5):
            Return the top_k most similar documents to the input text.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.docs: List[Dict[str, str]] = []
        self.embeddings: Optional[np.ndarray] = None

    def index(self, docs: List[Dict[str, str]], force_recompute: bool = False) -> None:
        """Index documents (list of dicts with 'id' and 'text'). Caches embeddings to disk."""
        self.docs = docs
        if EMBED_CACHE.exists() and not force_recompute:
            try:
                with open(EMBED_CACHE, "rb") as f:
                    data = pickle.load(f)
                if data.get("model") == self.model_name and len(data.get("docs", [])) == len(docs):
                    self.embeddings = data["embeddings"]
                    # quick sanity: doc ids match?
                    return
            except (FileNotFoundError, OSError, pickle.UnpicklingError, EOFError) as e:
                print(f"Failed to load cached embeddings: {e}")

        texts = [d["text"] for d in docs]
        self.embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        with open(EMBED_CACHE, "wb") as f:
            pickle.dump({"model": self.model_name, "docs": docs, "embeddings": self.embeddings}, f)

    def query(self, text: str, top_k: int = 5) -> List[Tuple[Dict[str, str], float]]:
        """Return top_k (doc, score) pairs using cosine similarity."""
        if self.embeddings is None or not self.docs:
            raise RuntimeError("Engine has not been indexed with documents.")
        q_emb = self.model.encode(text, convert_to_numpy=True)
        scores = util.cos_sim(q_emb, self.embeddings)[0].cpu().numpy()  # shape (n_docs,)
        # Get top indices
        idx = np.argsort(-scores)[:top_k]
        results = []
        for i in idx:
            results.append((self.docs[int(i)], float(scores[int(i)])))
        return results
