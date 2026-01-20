"""Shared test fixtures and configuration."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_cache_dir(monkeypatch):
    """Create a temporary cache directory for testing."""
    temp_dir = tempfile.mkdtemp()
    monkeypatch.setenv("CACHE_DIR", temp_dir)
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_themes_dir(tmp_path):
    """Create a temporary themes directory with sample themes."""
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    
    # Create a sample theme
    sample_theme = {
        "name": "Test Theme",
        "description": "A test theme",
        "bg": "#FFFFFF",
        "text": "#000000",
        "gradient_color": "#FFFFFF",
        "water": "#C0C0C0",
        "parks": "#F0F0F0",
        "road_motorway": "#0A0A0A",
        "road_primary": "#1A1A1A",
        "road_secondary": "#2A2A2A",
        "road_tertiary": "#3A3A3A",
        "road_residential": "#4A4A4A",
        "road_default": "#3A3A3A"
    }
    
    import json
    with open(themes_dir / "test_theme.json", "w") as f:
        json.dump(sample_theme, f)
    
    return themes_dir


@pytest.fixture
def temp_fonts_dir(tmp_path):
    """Create a temporary fonts directory."""
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    return fonts_dir


@pytest.fixture
def sample_theme():
    """Return a sample theme dictionary."""
    return {
        "name": "Test Theme",
        "bg": "#FFFFFF",
        "text": "#000000",
        "gradient_color": "#FFFFFF",
        "water": "#C0C0C0",
        "parks": "#F0F0F0",
        "road_motorway": "#0A0A0A",
        "road_primary": "#1A1A1A",
        "road_secondary": "#2A2A2A",
        "road_tertiary": "#3A3A3A",
        "road_residential": "#4A4A4A",
        "road_default": "#3A3A3A"
    }


@pytest.fixture
def sample_coordinates():
    """Return sample coordinates for testing."""
    return (40.7128, -74.0060)  # New York City
