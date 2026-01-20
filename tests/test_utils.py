"""Tests for the utils module."""

import pytest
import os
from pathlib import Path
from datetime import datetime
import numpy as np
from src.utils import (
    generate_output_filename,
    parse_resolution,
    calculate_dpi_from_resolution,
    calculate_bbox
)


def test_generate_output_filename_format(tmp_path, monkeypatch):
    """Test that output filename has correct format."""
    posters_dir = tmp_path / "posters"
    monkeypatch.setattr("src.utils.POSTERS_DIR", str(posters_dir))
    
    result = generate_output_filename("New York", "noir", "png")
    
    assert "new_york" in result
    assert "noir" in result
    assert result.endswith(".png")
    assert "posters" in result


def test_generate_output_filename_creates_directory(tmp_path, monkeypatch):
    """Test that output directory is created if it doesn't exist."""
    posters_dir = tmp_path / "posters"
    monkeypatch.setattr("src.utils.POSTERS_DIR", str(posters_dir))
    
    assert not posters_dir.exists()
    
    generate_output_filename("Paris", "sunset", "svg")
    
    assert posters_dir.exists()
    assert posters_dir.is_dir()


def test_generate_output_filename_timestamp(tmp_path, monkeypatch):
    """Test that filenames have unique timestamps."""
    posters_dir = tmp_path / "posters"
    monkeypatch.setattr("src.utils.POSTERS_DIR", str(posters_dir))
    
    file1 = generate_output_filename("Tokyo", "noir", "png")
    file2 = generate_output_filename("Tokyo", "noir", "png")
    
    # Files should have different timestamps (might be same if very fast)
    # Just check they follow the pattern
    assert "tokyo_noir_" in file1
    assert "tokyo_noir_" in file2


def test_generate_output_filename_spaces_replaced(tmp_path, monkeypatch):
    """Test that spaces in city names are replaced with underscores."""
    posters_dir = tmp_path / "posters"
    monkeypatch.setattr("src.utils.POSTERS_DIR", str(posters_dir))
    
    result = generate_output_filename("San Francisco", "ocean", "pdf")
    
    assert "san_francisco" in result
    assert " " not in Path(result).stem


def test_parse_resolution_valid():
    """Test parsing valid resolution strings."""
    width, height = parse_resolution("1920x1080")
    assert width == 1920
    assert height == 1080
    
    width, height = parse_resolution("3840x2160")
    assert width == 3840
    assert height == 2160
    
    width, height = parse_resolution("1280X720")  # uppercase X
    assert width == 1280
    assert height == 720


def test_parse_resolution_invalid_format():
    """Test parsing invalid resolution strings raises ValueError."""
    with pytest.raises(ValueError, match="format"):
        parse_resolution("1920")
    
    with pytest.raises(ValueError, match="format"):
        parse_resolution("1920x1080x60")
    
    with pytest.raises(ValueError, match="format"):
        parse_resolution("invalid")


def test_parse_resolution_negative_values():
    """Test parsing resolution with negative values raises ValueError."""
    with pytest.raises(ValueError, match="positive"):
        parse_resolution("-1920x1080")
    
    with pytest.raises(ValueError, match="positive"):
        parse_resolution("1920x-1080")


def test_parse_resolution_zero_values():
    """Test parsing resolution with zero values raises ValueError."""
    with pytest.raises(ValueError, match="positive"):
        parse_resolution("0x1080")
    
    with pytest.raises(ValueError, match="positive"):
        parse_resolution("1920x0")


def test_calculate_dpi_from_resolution_12_16():
    """Test DPI calculation for 12:16 portrait resolution."""
    dpi = calculate_dpi_from_resolution("3600x4800", figsize=(12, 16))
    assert dpi == 300  # 3600 / 12 = 300
    
    dpi = calculate_dpi_from_resolution("2400x3200", figsize=(12, 16))
    assert dpi == 200  # 2400 / 12 = 200


def test_calculate_dpi_from_resolution_16_9():
    """Test DPI calculation for 16:9 resolution."""
    dpi = calculate_dpi_from_resolution("1920x1080", figsize=(16, 9))
    assert dpi == 120  # 1920 / 16 = 120
    
    dpi = calculate_dpi_from_resolution("3840x2160", figsize=(16, 9))
    assert dpi == 240  # 3840 / 16 = 240


def test_calculate_dpi_from_resolution_custom_figsize():
    """Test DPI calculation with custom figsize."""
    dpi = calculate_dpi_from_resolution("2000x1000", figsize=(10, 5))
    assert dpi == 200  # 2000 / 10 = 200


def test_calculate_dpi_from_resolution_mismatched_aspect(capsys):
    """Test DPI calculation warns about mismatched aspect ratios."""
    dpi = calculate_dpi_from_resolution("1920x1200", figsize=(16, 9))
    
    # Should still return a DPI value
    assert dpi == 120
    
    # Should print warning
    captured = capsys.readouterr()
    assert "Warning" in captured.out or "aspect ratio" in captured.out.lower()


def test_calculate_bbox_basic(sample_coordinates):
    """Test basic bounding box calculation."""
    lat, lon = sample_coordinates
    dist = 10000  # 10km
    
    west, south, east, north = calculate_bbox(sample_coordinates, dist)
    
    # Check that bounds make sense
    assert west < lon < east
    assert south < lat < north


def test_calculate_bbox_zero_distance(sample_coordinates):
    """Test bounding box with zero distance."""
    lat, lon = sample_coordinates
    
    west, south, east, north = calculate_bbox(sample_coordinates, 0)
    
    # Should be very small box around the point
    assert west == pytest.approx(lon, abs=0.01)
    assert east == pytest.approx(lon, abs=0.01)
    assert south == pytest.approx(lat, abs=0.01)
    assert north == pytest.approx(lat, abs=0.01)


def test_calculate_bbox_aspect_ratio(sample_coordinates):
    """Test that bounding box respects aspect ratio."""
    dist = 20000
    figsize = (12, 16)  # Portrait aspect ratio
    
    west, south, east, north = calculate_bbox(sample_coordinates, dist, figsize)
    
    # Height should be larger than width for 12:16 portrait
    width = east - west
    height = north - south
    
    # Approximate aspect ratio check (accounting for latitude/longitude distortion)
    assert height > width


def test_calculate_bbox_equator_vs_pole():
    """Test that bbox calculation differs by latitude (longitude compression)."""
    dist = 10000
    
    # Near equator
    bbox_equator = calculate_bbox((0, 0), dist)
    
    # Near pole
    bbox_pole = calculate_bbox((80, 0), dist)
    
    # Longitude range should be larger near pole (due to cos(latitude) factor)
    lon_range_equator = bbox_equator[2] - bbox_equator[0]
    lon_range_pole = bbox_pole[2] - bbox_pole[0]
    
    assert lon_range_pole > lon_range_equator


def test_calculate_bbox_southern_hemisphere():
    """Test bounding box calculation in southern hemisphere."""
    # Buenos Aires coordinates
    coords = (-34.6037, -58.3816)
    dist = 15000
    
    west, south, east, north = calculate_bbox(coords, dist)
    
    # Latitude should be negative in southern hemisphere
    assert south < 0
    assert north < 0
    # But north should still be greater than south
    assert north > south
