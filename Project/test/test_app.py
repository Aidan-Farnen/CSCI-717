"""Tests for the app CLI and related helpers."""
from unittest.mock import patch, MagicMock
from io import StringIO
import sys as sys_module
import pytest
from src import app

# ---------------------------
# Fixtures / helpers
# ---------------------------

@pytest.fixture
def fake_docs():
    """Return sample documents for testing."""
    return [
        {"id": "0", "title": "Apple Pie", "ingredients": "apple, sugar, flour",
         "text": "apple pie text", "cuisine": "american"},
        {"id": "1", "title": "Banana Smoothie", "ingredients": "banana, milk",
         "text": "banana smoothie text", "cuisine": "american"},
    ]

# ---------------------------
# Test: run_cli prints expected output
# ---------------------------

def test_run_cli_basic(monkeypatch, fake_docs):  # pylint: disable=redefined-outer-name
    """Test CLI workflow with mocked dependencies."""
    monkeypatch.setattr(sys_module, "argv", ["app.py", "--query", "apple", "--topk", "1"])

    # Patch all external dependencies
    with patch("src.app.load_better_recipes") as mock_load, \
         patch("src.app.recipes_to_docs") as mock_docs, \
         patch("src.app.AIEngine") as mock_engine, \
         patch("src.app.extract_keywords") as mock_keywords:

        # Setup return values
        mock_load.return_value = fake_docs
        mock_docs.return_value = fake_docs
        mock_keywords.return_value = ["apple", "pie"]

        # Mock AIEngine instance
        mock_engine_instance = MagicMock()
        mock_engine_instance.query.return_value = [(fake_docs[0], 0.95)]
        mock_engine.return_value = mock_engine_instance

        # Capture printed output
        out = StringIO()
        monkeypatch.setattr(sys_module, "stdout", out)

        # Run CLI
        app.run_cli()

        # Validate printed keywords and top recipe
        output = out.getvalue()
        assert "Query keywords: apple, pie" in output
        assert "Top recipes:" in output
        assert "Apple Pie" in output
        assert "score: 0.950" in output

        # Ensure engine.index was called
        mock_engine_instance.index.assert_called_once_with(fake_docs, force_recompute=False)
        mock_engine_instance.query.assert_called_once_with("apple", top_k=1)


def test_run_cli_force_recompute(monkeypatch, fake_docs):   # pylint: disable=redefined-outer-name
    """Test CLI behavior with the --recompute flag."""
    monkeypatch.setattr(sys_module, "argv", ["app.py", "--query", "banana", "--recompute"])

    with patch("src.app.load_better_recipes") as mock_load, \
         patch("src.app.recipes_to_docs") as mock_docs, \
         patch("src.app.AIEngine") as mock_engine, \
         patch("src.app.extract_keywords") as mock_keywords:

        mock_load.return_value = fake_docs
        mock_docs.return_value = fake_docs
        mock_keywords.return_value = ["banana"]

        mock_engine_instance = MagicMock()
        mock_engine_instance.query.return_value = [(fake_docs[1], 0.99)]
        mock_engine.return_value = mock_engine_instance

        out = StringIO()
        monkeypatch.setattr(sys_module, "stdout", out)

        app.run_cli()

        output = out.getvalue()
        assert "banana" in output
        assert "Banana Smoothie" in output

        mock_engine_instance.index.assert_called_once_with(fake_docs, force_recompute=True)
