"""Map poster generator package."""

from .config import *
from .cache import CacheError, cache_get, cache_set
from .theme import load_theme, load_fonts, get_available_themes, list_themes
from .geocoding import get_coordinates
from .data_fetcher import fetch_map_data
from .renderer import render_poster
from .utils import (
    generate_output_filename,
    generate_city_folder_name,
    parse_resolution,
    calculate_dpi_from_resolution,
    calculate_bbox
)
from .cli import create_parser, validate_args, print_examples
from .poster_generator import (
    render_single_poster,
    fetch_map_resources,
    generate_single_poster,
    generate_all_themes
)

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
    'generate_city_folder_name',
    'parse_resolution',
    'calculate_dpi_from_resolution',
    'calculate_bbox',
    'create_parser',
    'validate_args',
    'print_examples',
    'render_single_poster',
    'fetch_map_resources',
    'generate_single_poster',
    'generate_all_themes',
]
