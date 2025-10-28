# src/ai_engine.py
from __future__ import annotations
from typing import List, Dict, Optional, Tuple
import numpy as np
import pathlib
import pickle

from sentence_transformers import SentenceTransformer, util

EMBED_CACHE = pathlib.Path(__file__).resolve().parents[1] / "data" / "embeddings.pkl"

class AIEngine:
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
            except Exception:
                pass

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
