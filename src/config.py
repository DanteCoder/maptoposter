"""Configuration constants for the map poster generator."""

import os
from pathlib import Path

# Cache configuration
CACHE_DIR_PATH = os.environ.get("CACHE_DIR", "cache")
CACHE_DIR = Path(CACHE_DIR_PATH)
CACHE_DIR.mkdir(exist_ok=True)

# Directory paths
THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"

# Default figure dimensions and resolution
DEFAULT_FIGSIZE = (12, 16)  # 3:4 portrait aspect ratio (12x16 inches)
DEFAULT_DPI = 300

# Font size constants for 12:16 portrait layout
FONT_SIZE_CITY = 60
FONT_SIZE_COUNTRY = 22
FONT_SIZE_COORDS = 14
FONT_SIZE_ATTRIBUTION = 8

# Dynamic font sizing for long city names
BASE_FONT_SIZE = 60
MIN_FONT_SIZE = 24
MAX_CITY_CHARS = 10  # Chars before scaling kicks in

# Text positioning (absolute distances from bottom in inches)
TEXT_CITY_POSITION = 2.0
TEXT_LINE_POSITION = 1.75
TEXT_COUNTRY_POSITION = 1.4
TEXT_COORDS_POSITION = 1.0

# Decorative line dimensions (absolute in inches)
LINE_WIDTH_INCHES = 2.4  # Total line width in inches

# Font scaling reference (base figure dimensions in inches)
BASE_FIGURE_HEIGHT = 16.0
BASE_FIGURE_WIDTH = 12.0
