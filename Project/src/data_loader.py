# src/data_loader.py
from __future__ import annotations
import pandas as pd
import pathlib
import ast
from typing import List, Dict, Any

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
