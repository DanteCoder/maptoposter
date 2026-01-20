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
DEFAULT_FIGSIZE = (16, 9)  # 16:9 aspect ratio
DEFAULT_DPI = 300

# Font size constants for 16:9 landscape layout
FONT_SIZE_CITY = 40
FONT_SIZE_COUNTRY = 16
FONT_SIZE_COORDS = 10
FONT_SIZE_ATTRIBUTION = 8

# Dynamic font sizing for long city names
BASE_FONT_SIZE = 40
MIN_FONT_SIZE = 24
MAX_CITY_CHARS = 10  # Chars before scaling kicks in
