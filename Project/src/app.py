"""
app.py

Command-Line Interface (CLI) for the AI-driven Recipe Recommender.

This module provides a CLI that allows users to search for recipes based on 
ingredients or text queries. It leverages the AIEngine for embedding-based 
similarity search, and NLP utilities to extract keywords from user queries. 

Main functionality:
- Parse command-line arguments for query text, number of results, and force recompute.
- Load and preprocess recipe data from the dataset.
- Index recipes using AIEngine, with optional caching of embeddings.
- Extract keywords from the query for display purposes.
- Perform similarity-based search and display top-k recipes with details.

Dependencies:
- data_loader: to load and preprocess the recipe dataset
- ai_engine: to index recipes and perform similarity queries
- nlp_utils: to extract keywords from the search query
- argparse: for command-line argument parsing

Usage:
------
Run the CLI from the terminal:

    python app.py --query "chicken pasta" --topk 3

Optional flags:
- --recompute : Forces recomputation of embeddings, ignoring cached embeddings.
"""
from __future__ import annotations
import argparse
from src.data_loader import load_better_recipes, recipes_to_docs
from src.ai_engine import AIEngine
from src.nlp_utils import extract_keywords

def run_cli():
    """
    Run the Recipe Recommender Command-Line Interface (CLI).

    This function handles the full workflow of the CLI:
    1. Parses command-line arguments for a search query, number of top results, 
       and optional recompute flag.
    2. Loads and preprocesses the recipe dataset using `load_better_recipes` and 
       `recipes_to_docs`.
    3. Initializes the AIEngine and indexes the recipes (embeddings are cached 
       for efficiency, unless `--recompute` is specified).
    4. Extracts keywords from the user query for display using `extract_keywords`.
    5. Queries the AIEngine for the top-k most similar recipes.
    6. Prints the keywords, recipe titles, ingredients, cuisine, and similarity scores.

    Command-Line Arguments:
        --query, -q : str
            The search query containing ingredients or recipe description.
        --topk, -k : int, default=5
            Number of top recipes to return.
        --recompute : bool
            Flag to force recomputation of embeddings, ignoring any cached embeddings.

    Example Usage:
        python app.py --query "chicken pasta" --topk 3
    """
    p = argparse.ArgumentParser(prog="recipe-recommender",
                                description="Recommend recipes from available ingredients or " \
                                "text query.")
    p.add_argument("--query",
                   "-q",
                   type=str,
                   help="Search query (ingredients or description)",
                   required=True)
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


   
   
    