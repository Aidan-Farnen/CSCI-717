"""
nlp_utils.py

Module providing simple natural language processing utilities for the recipe recommender.

This module includes functions for text preprocessing and keyword extraction. It is
designed to support AI-driven search and recommendation tasks by providing relevant
keywords from user queries or recipe text.

Main Function:
- extract_keywords(text: str, top_k: int = 10) -> List[str]
    Extracts the most relevant keywords from a given text using spaCy's POS tagging.
    Only nouns, proper nouns, and adjectives are considered. Returns a list of lemmatized
    and deduplicated keywords up to the specified top_k number. Falls back to a simple
    tokenization method if spaCy is unavailable.

Dependencies:
- spacy: for tokenization, lemmatization, and POS tagging


text = "Quick and easy chicken pasta recipe with fresh herbs and garlic."
keywords = extract_keywords(text, top_k=5)
print(keywords)  # Example output: ['chicken', 'pasta', 'recipe', 'herb', 'garlic']
"""
from typing import List
import spacy

_nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str, top_k: int = 10) -> List[str]:
    """
    Simple keyword extraction:
    - If spaCy is available uses POS tagging to pick NOUN/PROPN/ADJ tokens
    - Else falls back to splitting and returning lowercased tokens (filtered)
    """
    if not text:
        return []
    if _nlp:
        doc = _nlp(text)
        tokens = [tok.lemma_.lower()
                  for tok in doc if tok.pos_ in {"NOUN", "PROPN", "ADJ"} and not tok.is_stop]
        # dedupe while preserving order
        seen = set()
        out = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
            if len(out) >= top_k:
                break
    else:
        # fallback
        tokens = [t.strip(".,!?:;()[]").lower() for t in text.split()]
        tokens = [t for t in tokens if len(t) > 2]
        seen = set()
        out = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
            if len(out) >= top_k:
                break
    return out
