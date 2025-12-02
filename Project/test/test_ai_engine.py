# test/test_ai_engine.py
import numpy as np
import pickle
import pytest
from pathlib import Path

from src.ai_engine import AIEngine, EMBED_CACHE


# -------------------------------
# Helpers to mock SentenceTransformer
# -------------------------------
class MockModel:
    """A minimal fake embedding model for fast deterministic tests."""

    def __init__(self, name):
        self.name = name

    def encode(self, texts, convert_to_numpy=True, show_progress_bar=False):
        # Return deterministic "embeddings": a numeric vector based on text length
        if isinstance(texts, str):
            texts = [texts]
        return np.array([[len(t)] for t in texts], dtype=float)


@pytest.fixture
def mock_model(monkeypatch):
    """Patch SentenceTransformer to avoid loading real models."""
    from src import ai_engine

    monkeypatch.setattr(ai_engine, "SentenceTransformer", lambda name: MockModel(name))


@pytest.fixture
def sample_docs():
    return [
        {"id": "0", "text": "apple pie recipe"},
        {"id": "1", "text": "banana smoothie instructions"},
        {"id": "2", "text": "creamy pasta with mushrooms"},
    ]


# -------------------------------
# Tests
# -------------------------------

def test_index_creates_embeddings(tmp_path, monkeypatch, mock_model, sample_docs):
    """Indexing should create embeddings and write cache."""
    # Patch cache location to temporary directory
    cache_path = tmp_path / "embeddings.pkl"
    monkeypatch.setattr("src.ai_engine.EMBED_CACHE", cache_path)

    engine = AIEngine()
    engine.index(sample_docs)

    assert engine.embeddings is not None
    assert cache_path.exists(), "Embedding cache file should be created"

    with open(cache_path, "rb") as f:
        cached = pickle.load(f)

    assert cached["model"] == engine.model_name
    assert len(cached["docs"]) == len(sample_docs)


def test_index_uses_cache_when_available(tmp_path, monkeypatch, mock_model, sample_docs):
    """If cache exists, index() should skip recomputation."""
    cache_path = tmp_path / "embeddings.pkl"
    monkeypatch.setattr("src.ai_engine.EMBED_CACHE", cache_path)

    # Pre-create a fake cache file
    fake_embeddings = np.array([[1.0], [2.0], [3.0]])
    with open(cache_path, "wb") as f:
        pickle.dump({"model": "all-MiniLM-L6-v2", "docs": sample_docs, "embeddings": fake_embeddings}, f)

    engine = AIEngine()
    engine.index(sample_docs)

    # Should load embeddings from cache, not recompute
    assert np.array_equal(engine.embeddings, fake_embeddings)


def test_index_force_recompute_ignores_cache(tmp_path, monkeypatch, mock_model, sample_docs):
    """force_recompute=True must ignore cache."""
    cache_path = tmp_path / "embeddings.pkl"
    monkeypatch.setattr("src.ai_engine.EMBED_CACHE", cache_path)

    # Write a fake cache that should be ignored
    with open(cache_path, "wb") as f:
        pickle.dump({"model": "bad", "docs": [], "embeddings": np.zeros((1, 1))}, f)

    engine = AIEngine()
    engine.index(sample_docs, force_recompute=True)

    assert engine.embeddings is not None
    assert not np.array_equal(engine.embeddings, np.zeros((1, 1)))


def test_query_returns_ranked_results(monkeypatch, mock_model, sample_docs):
    """query() should return sorted (doc, score) pairs."""
    engine = AIEngine()
    engine.index(sample_docs)

    results = engine.query("banana", top_k=2)

    # Ensure size correct
    assert len(results) == 2

    # Ensure structure correct
    for doc, score in results:
        assert isinstance(doc, dict)
        assert isinstance(score, float)


def test_query_without_index_raises():
    engine = AIEngine()
    with pytest.raises(RuntimeError):
        engine.query("anything")

def test_index_handles_corrupt_cache(tmp_path, monkeypatch, mock_model, sample_docs, capsys):
    """Ensure the exception block runs when the cache file is corrupt."""

    # Create a corrupt cache file (empty → EOFError)
    cache_path = tmp_path / "embeddings.pkl"
    cache_path.write_bytes(b"")  # empty file triggers EOFError

    # Patch EMBED_CACHE to point to our corrupt file
    monkeypatch.setattr("src.ai_engine.EMBED_CACHE", cache_path)

    engine = AIEngine()

    # Run index normally
    engine.index(sample_docs, force_recompute=False)

    # The exception block should have printed an error message
    captured = capsys.readouterr().out
    assert "Failed to load cached embeddings" in captured

    # And embeddings should now be computed fresh
    assert engine.embeddings is not None
