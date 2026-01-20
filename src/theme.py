"""Theme and font management for map posters."""

import json
import os
from matplotlib.font_manager import FontProperties

from .config import THEMES_DIR, FONTS_DIR, FONT_SIZE_CITY, FONT_SIZE_COUNTRY, FONT_SIZE_COORDS, FONT_SIZE_ATTRIBUTION, BASE_FIGURE_HEIGHT


def load_fonts():
    """
    Load Roboto fonts from the fonts directory.
    Returns dict with font paths for different weights.
    """
    fonts = {
        'bold': os.path.join(FONTS_DIR, 'Roboto-Bold.ttf'),
        'regular': os.path.join(FONTS_DIR, 'Roboto-Regular.ttf'),
        'light': os.path.join(FONTS_DIR, 'Roboto-Light.ttf')
    }
    
    # Verify fonts exist
    for weight, path in fonts.items():
        if not os.path.exists(path):
            print(f"⚠ Font not found: {path}")
            return None
    
    return fonts


def get_available_themes():
    """
    Scans the themes directory and returns a list of available theme names.
    """
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
        return []
    
    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith('.json'):
            theme_name = file[:-5]  # Remove .json extension
            themes.append(theme_name)
    return themes


def load_theme(theme_name="feature_based"):
    """
    Load theme from JSON file in themes directory.
    """
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")
    
    if not os.path.exists(theme_file):
        print(f"⚠ Theme file '{theme_file}' not found. Using default feature_based theme.")
        # Fallback to embedded default theme
        return {
            "name": "Feature-Based Shading",
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
    
    with open(theme_file, 'r') as f:
        theme = json.load(f)
        print(f"✓ Loaded theme: {theme.get('name', theme_name)}")
        if 'description' in theme:
            print(f"  {theme['description']}")
        return theme


def create_font_properties(fonts, adjusted_city_font_size=None, figsize=None):
    """
    Create FontProperties objects for different text elements.
    Returns a dict with font properties for: main, sub, coords, attr.
    Scales font sizes based on figure height to maintain proportions.
    """
    # Scale factor based on figure height
    if figsize:
        scale_factor = figsize[1] / BASE_FIGURE_HEIGHT
    else:
        scale_factor = 1.0
    
    if fonts:
        city_size = adjusted_city_font_size if adjusted_city_font_size else FONT_SIZE_CITY
        return {
            'main': FontProperties(fname=fonts['bold'], size=city_size * scale_factor),
            'sub': FontProperties(fname=fonts['light'], size=FONT_SIZE_COUNTRY * scale_factor),
            'coords': FontProperties(fname=fonts['regular'], size=FONT_SIZE_COORDS * scale_factor),
            'attr': FontProperties(fname=fonts['light'], size=FONT_SIZE_ATTRIBUTION * scale_factor)
        }
    else:
        # Fallback to system fonts
        city_size = adjusted_city_font_size if adjusted_city_font_size else FONT_SIZE_CITY
        return {
            'main': FontProperties(family='monospace', weight='bold', size=city_size * scale_factor),
            'sub': FontProperties(family='monospace', weight='normal', size=FONT_SIZE_COUNTRY * scale_factor),
            'coords': FontProperties(family='monospace', size=FONT_SIZE_COORDS * scale_factor),
            'attr': FontProperties(family='monospace', size=FONT_SIZE_ATTRIBUTION * scale_factor)
        }


def list_themes():
    """List all available themes with descriptions."""
    available_themes = get_available_themes()
    if not available_themes:
        print("No themes found in 'themes/' directory.")
        return
    
    print("\nAvailable Themes:")
    print("-" * 60)
    for theme_name in available_themes:
        theme_path = os.path.join(THEMES_DIR, f"{theme_name}.json")
        try:
            with open(theme_path, 'r') as f:
                theme_data = json.load(f)
                display_name = theme_data.get('name', theme_name)
                description = theme_data.get('description', '')
        except:
            display_name = theme_name
            description = ''
        print(f"  {theme_name}")
        print(f"    {display_name}")
        if description:
            print(f"    {description}")
        print()
