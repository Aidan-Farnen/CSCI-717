"""
module docstring placeholder
"""
from src import nlp_utils


# ------------------------------
# Basic behavior
# ------------------------------

def test_extract_keywords_empty_string():
    """
    test docstring placeholder
    """
    assert not nlp_utils.extract_keywords("")


def test_extract_keywords_simple_sentence():
    """
    spaCy should extract nouns, proper nouns, and adjectives.
    The exact results may vary slightly between spaCy versions,
    but for common sentences they are stable.
    """
    text = "The quick brown fox jumps over the lazy dog."
    keywords = nlp_utils.extract_keywords(text)

    # Should contain important nouns/adj
    assert "fox" in keywords
    assert "dog" in keywords or "lazy" in keywords  # lemmatized adj or noun


def test_extract_keywords_deduplication():
    """
    test docstring placeholder
    """
    text = "Apple apple APPLES banana banana"
    keywords = nlp_utils.extract_keywords(text)

    # Only one "apple" despite repeats
    assert keywords.count("apple") == 1
    assert "banana" in keywords


def test_extract_keywords_top_k_limit():
    """
    test docstring placeholder
    """
    text = "red car fast car shiny car broken car cool car"
    keywords = nlp_utils.extract_keywords(text, top_k=2)

    assert len(keywords) == 2


# ------------------------------
# Fallback mode (simulate no spaCy)
# ------------------------------

def test_extract_keywords_fallback(monkeypatch):
    """
    Monkeypatch `_nlp` to None to test fallback branch.
    """
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
    """
    test docstring placeholder
    """
    monkeypatch.setattr(nlp_utils, "_nlp", None)

    text = "one two three four five six seven eight nine ten eleven"
    keywords = nlp_utils.extract_keywords(text, top_k=3)

    assert len(keywords) == 3
