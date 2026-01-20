"""Map poster generator package."""

from .config import *
from .cache import CacheError, cache_get, cache_set
from .theme import load_theme, load_fonts, get_available_themes, list_themes
from .geocoding import get_coordinates
from .data_fetcher import fetch_map_data
from .renderer import render_poster
from .utils import (
    generate_output_filename,
    parse_resolution,
    calculate_dpi_from_resolution,
    calculate_bbox
)
from .cli import create_parser, validate_args, print_examples

__all__ = [
    'CacheError',
    'cache_get',
    'cache_set',
    'load_theme',
    'load_fonts',
    'get_available_themes',
    'list_themes',
    'get_coordinates',
    'fetch_map_data',
    'render_poster',
    'generate_output_filename',
    'parse_resolution',
    'calculate_dpi_from_resolution',
    'calculate_bbox',
    'create_parser',
    'validate_args',
    'print_examples',
]
