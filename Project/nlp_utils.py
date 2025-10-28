# src/nlp_utils.py
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
        tokens = [tok.lemma_.lower() for tok in doc if tok.pos_ in {"NOUN", "PROPN", "ADJ"} and not tok.is_stop]
        # dedupe while preserving order
        seen = set()
        out = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
            if len(out) >= top_k:
                break
        return out
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
