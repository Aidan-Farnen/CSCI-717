"""Tests for the src.data_loader module."""
# pylint: disable=redefined-outer-name, unused-argument
import pandas as pd
import pytest

from src.data_loader import (
    _safe_eval,
    load_better_recipes,
    recipes_to_docs,
)


# ------------------------------
# _safe_eval tests
# ------------------------------

def test_safe_eval_valid_list():
    """Evaluates a string list literal correctly."""
    assert _safe_eval("['a', 'b']") == ["a", "b"]


def test_safe_eval_valid_dict():
    """Evaluates a string dict literal correctly."""
    assert _safe_eval("{'a': 1, 'b': 2}") == {"a": 1, "b": 2}


def test_safe_eval_invalid_string_returns_original():
    """Returns original string if not a literal."""
    assert _safe_eval("not a literal") == "not a literal"


def test_safe_eval_non_string_pass_through():
    """Passes through non-string inputs unchanged."""
    assert _safe_eval(10) == 10


# ------------------------------
# load_better_recipes tests
# ------------------------------

@pytest.fixture
def sample_csv_file(tmp_path):
    """Generate a temporary CSV containing minimal valid recipe rows."""
    p = tmp_path / "recipes.csv"

    df = pd.DataFrame(
        {
            "recipe_name": ["Chicken Pasta", "Veggie Salad"],
            "ingredients": ["['chicken', 'pasta']", "['lettuce', 'tomato']"],
            "directions": ["['cook', 'mix']", "['chop', 'serve']"],
            "nutrition": ["{'calories': 200}", "{'calories': 120}"],
            "timing": ["{'prep': 10}", "{'prep': 5}"],
            "cuisine_path": ["italian", "american"],
            "rating": [4.5, 4.7],
            "url": ["http://example.com/1", "http://example.com/2"]
        }
    )
    df.to_csv(p, index=False)
    return p


def test_load_better_recipes_returns_dataframe(sample_csv_file):
    """Returns a DataFrame when loading recipes."""
    df = load_better_recipes(sample_csv_file)
    assert isinstance(df, pd.DataFrame)


def test_load_better_recipes_parses_literal_columns(sample_csv_file):
    """Parses ingredients, directions, nutrition, and timing columns correctly."""
    df = load_better_recipes(sample_csv_file)

    assert df.loc[0, "ingredients"] == ["chicken", "pasta"]
    assert df.loc[0, "directions"] == ["cook", "mix"]
    assert isinstance(df.loc[0, "nutrition"], dict)
    assert isinstance(df.loc[0, "timing"], dict)


def test_load_better_recipes_creates_string_fields(sample_csv_file):
    """Creates string representations of ingredients, directions, nutrition, and timing."""
    df = load_better_recipes(sample_csv_file)

    assert df.loc[0, "ingredients_str"] == "chicken, pasta"
    assert df.loc[0, "directions_str"] == "cook. mix"
    assert "calories: 200" in df.loc[0, "nutrition_str"]
    assert "prep: 10" in df.loc[0, "timing_str"]


def test_load_better_recipes_combined_text(sample_csv_file):
    """Generates combined_text field including all relevant recipe info."""
    df = load_better_recipes(sample_csv_file)
    text = df.loc[0, "combined_text"]

    assert "Chicken Pasta" in text
    assert "Ingredients: chicken, pasta" in text
    assert "Directions: cook. mix" in text
    assert "Cuisine: italian" in text
    assert "Nutrition:" in text
    assert "Timing:" in text


def test_load_better_recipes_adds_id(sample_csv_file):
    """Adds a unique ID to each recipe."""
    df = load_better_recipes(sample_csv_file)
    assert list(df["id"]) == ["0", "1"]


def test_load_better_recipes_drops_duplicate_recipe_names(sample_csv_file, tmp_path):
    """Duplicate recipe_name should collapse into a single row."""
    p = tmp_path / "dupe.csv"

    df = pd.DataFrame(
        {
            "recipe_name": ["A", "A"],  # duplicate names
            "ingredients": ["['x']", "['y']"],
            "directions": ["['a']", "['b']"],
            "nutrition": ["{'cal':1}", "{'cal':2}"],
            "timing": ["{'prep':1}", "{'prep':2}"],
            "cuisine_path": ["type", "type"],
        }
    )
    df.to_csv(p, index=False)

    df_loaded = load_better_recipes(p)
    assert len(df_loaded) == 1
    assert df_loaded.iloc[0]["recipe_name"] == "A"


# ------------------------------
# recipes_to_docs tests
# ------------------------------

def test_recipes_to_docs_output_format(sample_csv_file):
    """Converts DataFrame rows to a list of dicts with expected keys."""
    df = load_better_recipes(sample_csv_file)
    docs = recipes_to_docs(df)

    assert isinstance(docs, list)
    assert isinstance(docs[0], dict)

    doc = docs[0]
    expected_keys = {
        "id", "title", "ingredients", "directions",
        "cuisine", "rating", "text", "url"
    }
    assert expected_keys.issubset(doc.keys())


def test_recipes_to_docs_matches_dataframe_content(sample_csv_file):
    """Docs content matches the source DataFrame fields."""
    df = load_better_recipes(sample_csv_file)
    docs = recipes_to_docs(df)

    first = docs[0]

    assert first["title"] == "Chicken Pasta"
    assert "chicken, pasta" in first["ingredients"]
    assert "cook. mix" in first["directions"]
    assert first["cuisine"] == "italian"
    assert first["rating"] == "4.5"
    assert first["url"] == "http://example.com/1"
    assert "Ingredients:" in first["text"]
