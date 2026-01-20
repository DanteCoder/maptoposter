"""Utility functions for file handling and resolution calculations."""

import os
import numpy as np
from datetime import datetime

from .config import POSTERS_DIR, DEFAULT_FIGSIZE


def generate_output_filename(city, theme_name, output_format):
    """
    Generate unique output filename with city, theme, and datetime.
    """
    if not os.path.exists(POSTERS_DIR):
        os.makedirs(POSTERS_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = city.lower().replace(' ', '_')
    ext = output_format.lower()
    filename = f"{city_slug}_{theme_name}_{timestamp}.{ext}"
    return os.path.join(POSTERS_DIR, filename)


def parse_resolution(resolution_str):
    """
    Parse resolution string (e.g., '3840x2160') and return width, height.
    """
    try:
        parts = resolution_str.lower().split('x')
        if len(parts) != 2:
            raise ValueError("Resolution must be in format WIDTHxHEIGHT (e.g., 3840x2160)")
        width = int(parts[0])
        height = int(parts[1])
        if width <= 0 or height <= 0:
            raise ValueError("Resolution dimensions must be positive")
        return width, height
    except ValueError as e:
        raise ValueError(f"Invalid resolution format: {e}")


def calculate_dpi_from_resolution(resolution_str, figsize=DEFAULT_FIGSIZE):
    """
    Calculate DPI needed to achieve target resolution with given figsize.
    Returns DPI value.
    """
    width_px, height_px = parse_resolution(resolution_str)
    width_in, height_in = figsize
    
    dpi_x = width_px / width_in
    dpi_y = height_px / height_in
    
    # Check if aspect ratios match
    if abs(dpi_x - dpi_y) > 1:
        print(f"⚠ Warning: Resolution aspect ratio ({width_px}:{height_px}) doesn't perfectly match figure aspect ratio ({width_in}:{height_in})")
        print(f"  Using DPI: {dpi_x:.1f}")
    
    return int(dpi_x)


def calculate_bbox(point, dist, figsize=DEFAULT_FIGSIZE):
    """
    Calculate bounding box for a given point and distance.
    Returns (west, south, east, north).
    """
    lat, lon = point
    
    # Convert distance to degrees (approximate)
    # 1 degree latitude ≈ 111km
    # 1 degree longitude ≈ 111km * cos(latitude)
    width_ratio, height_ratio = figsize
    aspect_ratio = height_ratio / width_ratio
    
    lon_dist_deg = dist / (111000 * np.cos(np.radians(lat)))
    lat_dist_deg = (dist * aspect_ratio) / 111000
    
    north = lat + lat_dist_deg
    south = lat - lat_dist_deg
    east = lon + lon_dist_deg
    west = lon - lon_dist_deg
    
    return (west, south, east, north)
