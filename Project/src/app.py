# src/app.py
from __future__ import annotations
from typing import List
import argparse
from pathlib import Path
from src.data_loader import load_better_recipes, recipes_to_docs
from src.ai_engine import AIEngine
from src.nlp_utils import extract_keywords

def run_cli():
    p = argparse.ArgumentParser(prog="recipe-recommender", description="Recommend recipes from available ingredients or text query.")
    p.add_argument("--query", "-q", type=str, help="Search query (ingredients or description)", required=True)
    p.add_argument("--topk", "-k", type=int, default=5, help="Number of recipes to return")
    p.add_argument("--recompute", action="store_true", help="Force recompute embeddings")
    args = p.parse_args()

    df = load_better_recipes()
    docs = recipes_to_docs(df)
    engine = AIEngine()
    engine.index(docs, force_recompute=args.recompute)

    # small pre-processing + show keywords
    keywords = extract_keywords(args.query, top_k=8)
    print(f"Query keywords: {', '.join(keywords)}\n")

    results = engine.query(args.query, top_k=args.topk)
    print("Top recipes:")
    for doc, score in results:
        print(f"- [{doc['id']}] {doc['title']} (score: {score:.3f})")
        print(f"  Ingredients: {doc['ingredients']}")
        print(f"  Cuisine: {doc.get('cuisine','')}")
        print()
        
if __name__ == "__main__":
    run_cli()
