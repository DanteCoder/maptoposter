"""Tests for the config module."""

import os
import pytest
from pathlib import Path
from src.config import (
    CACHE_DIR,
    THEMES_DIR,
    FONTS_DIR,
    POSTERS_DIR,
    DEFAULT_FIGSIZE,
    DEFAULT_DPI,
    FONT_SIZE_CITY,
    FONT_SIZE_COUNTRY,
    FONT_SIZE_COORDS,
    FONT_SIZE_ATTRIBUTION,
    BASE_FONT_SIZE,
    MIN_FONT_SIZE,
    MAX_CITY_CHARS
)


def test_cache_dir_default():
    """Test that CACHE_DIR has a default value."""
    assert isinstance(CACHE_DIR, Path)
    assert CACHE_DIR.exists()


def test_cache_dir_env_variable(monkeypatch, tmp_path):
    """Test that CACHE_DIR respects environment variable."""
    custom_cache = str(tmp_path / "custom_cache")
    monkeypatch.setenv("CACHE_DIR", custom_cache)
    
    # Need to reload the module to pick up new env var
    import importlib
    from src import config
    importlib.reload(config)
    
    assert str(config.CACHE_DIR) == custom_cache


def test_directory_paths():
    """Test that directory path constants are strings."""
    assert THEMES_DIR == "themes"
    assert FONTS_DIR == "fonts"
    assert POSTERS_DIR == "posters"


def test_default_figsize():
    """Test default figure size is 12:16 portrait (3:4 aspect ratio)."""
    assert DEFAULT_FIGSIZE == (12, 16)
    assert DEFAULT_FIGSIZE[0] / DEFAULT_FIGSIZE[1] == pytest.approx(12/16)


def test_default_dpi():
    """Test default DPI is 300."""
    assert DEFAULT_DPI == 300


def test_font_sizes():
    """Test font size constants are positive integers."""
    assert FONT_SIZE_CITY > 0
    assert FONT_SIZE_COUNTRY > 0
    assert FONT_SIZE_COORDS > 0
    assert FONT_SIZE_ATTRIBUTION > 0
    assert BASE_FONT_SIZE > 0
    assert MIN_FONT_SIZE > 0


def test_font_size_hierarchy():
    """Test that font sizes follow logical hierarchy."""
    assert FONT_SIZE_CITY > FONT_SIZE_COUNTRY
    assert FONT_SIZE_COUNTRY > FONT_SIZE_COORDS
    assert FONT_SIZE_COORDS > FONT_SIZE_ATTRIBUTION


def test_dynamic_font_constants():
    """Test dynamic font sizing constants."""
    assert MAX_CITY_CHARS > 0
    assert BASE_FONT_SIZE >= MIN_FONT_SIZE
