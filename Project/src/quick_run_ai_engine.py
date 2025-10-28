# test_ai_engine.py
import numpy as np
from ai_engine import AIEngine

class MockModel:
    """Mock of SentenceTransformer that returns deterministic embeddings."""
    def encode(self, texts, convert_to_numpy=True, show_progress_bar=False):
        # Convert every text into a simple vector based on length for deterministic behavior
        if isinstance(texts, str):
            return np.array([len(texts)], dtype=float)
        return np.array([[len(t)] for t in texts], dtype=float)

def test_ai_engine_index_and_query(monkeypatch, tmp_path):
    # Patch the model inside AIEngine to avoid downloading real embeddings
    monkeypatch.setattr("ai_engine.SentenceTransformer", lambda name: MockModel())

    engine = AIEngine()

    docs = [
        {"id": "1", "text": "Apple pie recipe"},
        {"id": "2", "text": "Banana smoothie"},
        {"id": "3", "text": "Spaghetti with tomato sauce"},
    ]

    engine.index(docs, force_recompute=True)
    results = engine.query("I like spaghetti", top_k=2)

    # Assertions
    assert len(results) == 2
    assert isinstance(results[0], tuple)
    assert isinstance(results[0][0], dict)
    assert isinstance(results[0][1], float)

    # The doc with the longest text should score highest in our mock encoding
    top_doc = results[0][0]
    assert top_doc["id"] == "3"  # "Spaghetti with tomato sauce" is longest text
