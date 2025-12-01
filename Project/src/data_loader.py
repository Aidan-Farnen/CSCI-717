"""
data_loader.py

Module for loading and preprocessing the "Better Recipes for a Better Life" dataset.

This module provides functions to:
- Load the recipe CSV file and handle nested list/dictionary columns safely.
- Clean and preprocess text fields for embedding-based AI applications.
- Convert recipe DataFrame rows into a format suitable for AIEngine indexing.

Main Functions:
- load_better_recipes(path: str | pathlib.Path = DATA_DIR / "recipes.csv") -> pd.DataFrame
    Loads the CSV dataset, parses nested columns, and creates combined text fields
    for each recipe. Returns a cleaned pandas DataFrame.

- recipes_to_docs(df: pd.DataFrame) -> List[Dict[str, str]]
    Converts a DataFrame of recipes into a list of dictionaries suitable for 
    embedding and similarity searches. Each dictionary includes fields like 'id',
    'title', 'ingredients', 'directions', 'cuisine', 'rating', 'text', and 'url'.

Dependencies:
- pandas: for DataFrame manipulation
- pathlib: for filesystem paths
- ast: for safe evaluation of string representations of Python lists/dicts

df = load_better_recipes("data/recipes.csv")
docs = recipes_to_docs(df)
print(docs[0]["title"], docs[0]["text"])
"""
from __future__ import annotations
import pathlib
import ast
from typing import List, Dict, Any
import pandas as pd

DATA_DIR = pathlib.Path(__file__).resolve().parents[1] / "data"


def _safe_eval(value: Any) -> Any:
    """Safely evaluate string representations of Python literals (lists/dicts)."""
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
    return value


def load_better_recipes(path: str | pathlib.Path = DATA_DIR / "recipes.csv") -> pd.DataFrame:
    """
    Load and preprocess the Kaggle 'Better Recipes for a Better Life' dataset.
    Handles nested columns (lists/dicts) and prepares text fields for embeddings.
    """
    df = pd.read_csv(path)
    df = df.fillna("")

    # Safely parse list/dict columns
    for col in ["ingredients", "directions", "nutrition", "timing"]:
        df[col] = df[col].apply(_safe_eval)

    # Convert lists/dicts to strings for embedding
    df["ingredients_str"] = df["ingredients"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x)
    )
    df["directions_str"] = df["directions"].apply(
        lambda x: ". ".join(x) if isinstance(x, list) else str(x)
    )
    df["nutrition_str"] = df["nutrition"].apply(
        lambda x: ", ".join([f"{k}: {v}" for k, v in x.items()]) if isinstance(x, dict) else str(x)
    )
    df["timing_str"] = df["timing"].apply(
        lambda x: ", ".join([f"{k}: {v}" for k, v in x.items()]) if isinstance(x, dict) else str(x)
    )

    # Combine all text into one field for embeddings
    df["combined_text"] = (
        df["recipe_name"].astype(str)
        + ". Ingredients: " + df["ingredients_str"]
        + ". Directions: " + df["directions_str"]
        + ". Cuisine: " + df["cuisine_path"].astype(str)
        + ". Nutrition: " + df["nutrition_str"]
        + ". Timing: " + df["timing_str"]
    )

    # Clean up whitespace and duplicates
    df = df.drop_duplicates(subset=["recipe_name"]).reset_index(drop=True)
    df["id"] = df.index.astype(str)

    return df


def recipes_to_docs(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Convert DataFrame rows into list of recipe dicts for embedding search.
    """
    docs = []
    for _, row in df.iterrows():
        docs.append({
            "id": str(row["id"]),
            "title": str(row["recipe_name"]),
            "ingredients": str(row["ingredients_str"]),
            "directions": str(row["directions_str"]),
            "cuisine": str(row["cuisine_path"]),
            "rating": str(row.get("rating", "")),
            "text": str(row["combined_text"]),
            "url": str(row.get("url", "")),
        })
    return docs
