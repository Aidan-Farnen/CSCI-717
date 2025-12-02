"""Tests for the nlp_utils.extract_keywords function."""
from src import nlp_utils


# ------------------------------
# Basic behavior
# ------------------------------

def test_extract_keywords_empty_string():
    """Empty string should return no keywords."""
    assert not nlp_utils.extract_keywords("")


def test_extract_keywords_simple_sentence():
    """Extracts nouns, proper nouns, and adjectives from a simple sentence."""
    text = "The quick brown fox jumps over the lazy dog."
    keywords = nlp_utils.extract_keywords(text)

    # Should contain important nouns/adj
    assert "fox" in keywords
    assert "dog" in keywords or "lazy" in keywords  # lemmatized adj or noun


def test_extract_keywords_deduplication():
    """Repeated words should appear only once in keywords."""
    text = "Apple apple APPLES banana banana"
    keywords = nlp_utils.extract_keywords(text)

    # Only one "apple" despite repeats
    assert keywords.count("apple") == 1
    assert "banana" in keywords


def test_extract_keywords_top_k_limit():
    """Respects top_k limit when extracting keywords."""
    text = "red car fast car shiny car broken car cool car"
    keywords = nlp_utils.extract_keywords(text, top_k=2)

    assert len(keywords) == 2


# ------------------------------
# Fallback mode (simulate no spaCy)
# ------------------------------

def test_extract_keywords_fallback(monkeypatch):
    """Fallback mode returns filtered tokens when spaCy is unavailable."""
    monkeypatch.setattr(nlp_utils, "_nlp", None)

    text = "Hello world! This fallback mode extracts tokens."
    keywords = nlp_utils.extract_keywords(text)

    # No spaCy → fallback: simple splitting & filtering
    assert isinstance(keywords, list)
    assert "hello" in keywords
    assert "world" in keywords
    assert "fallback" in keywords

    # should filter small words (len <= 2)
    assert "to" not in keywords
    assert "is" not in keywords


def test_extract_keywords_fallback_top_k(monkeypatch):
    """Fallback mode respects top_k limit."""
    monkeypatch.setattr(nlp_utils, "_nlp", None)

    text = "one two three four five six seven eight nine ten eleven"
    keywords = nlp_utils.extract_keywords(text, top_k=3)

    assert len(keywords) == 3
