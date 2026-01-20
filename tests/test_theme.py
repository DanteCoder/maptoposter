"""Tests for the theme module."""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.theme import (
    load_fonts,
    get_available_themes,
    load_theme,
    create_font_properties,
    list_themes
)


def test_get_available_themes_empty_directory(tmp_path, monkeypatch):
    """Test getting themes from an empty directory."""
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    
    monkeypatch.setattr("src.theme.THEMES_DIR", str(themes_dir))
    
    result = get_available_themes()
    assert result == []


def test_get_available_themes_with_files(tmp_path, monkeypatch):
    """Test getting themes with multiple theme files."""
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    
    # Create theme files
    (themes_dir / "theme1.json").write_text('{"name": "Theme 1"}')
    (themes_dir / "theme2.json").write_text('{"name": "Theme 2"}')
    (themes_dir / "not_a_theme.txt").write_text("ignore this")
    
    monkeypatch.setattr("src.theme.THEMES_DIR", str(themes_dir))
    
    result = get_available_themes()
    assert sorted(result) == ["theme1", "theme2"]


def test_load_theme_existing(tmp_path, monkeypatch, sample_theme):
    """Test loading an existing theme file."""
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    
    theme_file = themes_dir / "test_theme.json"
    with open(theme_file, "w") as f:
        json.dump(sample_theme, f)
    
    monkeypatch.setattr("src.theme.THEMES_DIR", str(themes_dir))
    
    result = load_theme("test_theme")
    assert result["name"] == "Test Theme"
    assert result["bg"] == "#FFFFFF"
    assert result["text"] == "#000000"


def test_load_theme_nonexistent(tmp_path, monkeypatch, capsys):
    """Test loading a non-existent theme returns default."""
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    
    monkeypatch.setattr("src.theme.THEMES_DIR", str(themes_dir))
    
    result = load_theme("nonexistent")
    
    # Should return default theme
    assert result["name"] == "Feature-Based Shading"
    assert result["bg"] == "#FFFFFF"
    
    # Should print warning
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_load_theme_with_description(tmp_path, monkeypatch, capsys):
    """Test that theme description is printed when present."""
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    
    theme_data = {
        "name": "Test Theme",
        "description": "A test theme description",
        "bg": "#FFFFFF",
        "text": "#000000"
    }
    
    theme_file = themes_dir / "test.json"
    with open(theme_file, "w") as f:
        json.dump(theme_data, f)
    
    monkeypatch.setattr("src.theme.THEMES_DIR", str(themes_dir))
    
    load_theme("test")
    
    captured = capsys.readouterr()
    assert "Test Theme" in captured.out
    assert "A test theme description" in captured.out


def test_load_fonts_missing_files(tmp_path, monkeypatch, capsys):
    """Test load_fonts returns None when font files don't exist."""
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    
    monkeypatch.setattr("src.theme.FONTS_DIR", str(fonts_dir))
    
    result = load_fonts()
    assert result is None
    
    captured = capsys.readouterr()
    assert "Font not found" in captured.out


def test_load_fonts_all_present(tmp_path, monkeypatch):
    """Test load_fonts returns font dict when all fonts exist."""
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    
    # Create dummy font files
    (fonts_dir / "Roboto-Bold.ttf").write_bytes(b"fake font data")
    (fonts_dir / "Roboto-Regular.ttf").write_bytes(b"fake font data")
    (fonts_dir / "Roboto-Light.ttf").write_bytes(b"fake font data")
    
    monkeypatch.setattr("src.theme.FONTS_DIR", str(fonts_dir))
    
    result = load_fonts()
    assert result is not None
    assert "bold" in result
    assert "regular" in result
    assert "light" in result
    assert result["bold"].endswith("Roboto-Bold.ttf")


def test_create_font_properties_with_fonts(tmp_path):
    """Test creating font properties with fonts."""
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    
    # Create dummy font files
    (fonts_dir / "Roboto-Bold.ttf").write_bytes(b"fake")
    (fonts_dir / "Roboto-Regular.ttf").write_bytes(b"fake")
    (fonts_dir / "Roboto-Light.ttf").write_bytes(b"fake")
    
    fonts = {
        'bold': str(fonts_dir / "Roboto-Bold.ttf"),
        'regular': str(fonts_dir / "Roboto-Regular.ttf"),
        'light': str(fonts_dir / "Roboto-Light.ttf")
    }
    
    result = create_font_properties(fonts)
    
    assert 'main' in result
    assert 'sub' in result
    assert 'coords' in result
    assert 'attr' in result


def test_create_font_properties_without_fonts():
    """Test creating font properties without fonts (fallback)."""
    result = create_font_properties(None)
    
    assert 'main' in result
    assert 'sub' in result
    assert 'coords' in result
    assert 'attr' in result


def test_create_font_properties_custom_city_size(tmp_path):
    """Test creating font properties with custom city font size."""
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    
    (fonts_dir / "Roboto-Bold.ttf").write_bytes(b"fake")
    (fonts_dir / "Roboto-Regular.ttf").write_bytes(b"fake")
    (fonts_dir / "Roboto-Light.ttf").write_bytes(b"fake")
    
    fonts = {
        'bold': str(fonts_dir / "Roboto-Bold.ttf"),
        'regular': str(fonts_dir / "Roboto-Regular.ttf"),
        'light': str(fonts_dir / "Roboto-Light.ttf")
    }
    
    result = create_font_properties(fonts, adjusted_city_font_size=30)
    
    # Font size should be adjusted
    assert result['main'].get_size() == 30


def test_list_themes_empty(tmp_path, monkeypatch, capsys):
    """Test listing themes when directory is empty."""
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    
    monkeypatch.setattr("src.theme.THEMES_DIR", str(themes_dir))
    
    list_themes()
    
    captured = capsys.readouterr()
    assert "No themes found" in captured.out


def test_list_themes_with_themes(tmp_path, monkeypatch, capsys):
    """Test listing themes with available themes."""
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    
    theme1 = {"name": "Theme One", "description": "First theme"}
    theme2 = {"name": "Theme Two"}
    
    with open(themes_dir / "theme1.json", "w") as f:
        json.dump(theme1, f)
    with open(themes_dir / "theme2.json", "w") as f:
        json.dump(theme2, f)
    
    monkeypatch.setattr("src.theme.THEMES_DIR", str(themes_dir))
    
    list_themes()
    
    captured = capsys.readouterr()
    assert "theme1" in captured.out
    assert "theme2" in captured.out
    assert "Theme One" in captured.out
    assert "First theme" in captured.out
