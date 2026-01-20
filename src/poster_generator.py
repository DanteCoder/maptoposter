"""Poster generation logic for single and batch processing."""

import os
from datetime import datetime

from .theme import load_theme, load_fonts, get_available_themes
from .geocoding import get_coordinates
from .data_fetcher import fetch_map_data
from .renderer import render_poster
from .utils import generate_output_filename, generate_city_folder_name, calculate_bbox
from .config import POSTERS_DIR


def render_single_poster(city, country, theme_name, coords, graph, water, parks, 
                         output_format, dpi, figsize, output_file):
    """
    Core rendering function that creates a poster from pre-loaded data.
    
    Args:
        city, country: Location info
        theme_name: Theme to use
        coords: Coordinates tuple (lat, lon)
        graph, water, parks: Map data
        output_format, dpi, figsize: Rendering parameters
        output_file: Output file path
    
    Returns:
        Path to the generated file
    """
    # Load theme and fonts
    theme = load_theme(theme_name)
    fonts = load_fonts()
    
    # Render poster
    render_poster(
        city, country, coords,
        graph, water, parks,
        theme, fonts,
        output_file, output_format,
        dpi=dpi, figsize=figsize
    )
    
    return output_file


def fetch_map_resources(city, country, distance, figsize):
    """
    Fetch all map resources (coordinates, bbox, and map data) for a city.
    
    Args:
        city: City name
        country: Country name
        distance: Map radius in meters
        figsize: Figure size tuple
    
    Returns:
        Tuple of (coords, bbox, graph, water, parks)
    """
    coords = get_coordinates(city, country)
    bbox = calculate_bbox(coords, distance, figsize)
    graph, water, parks = fetch_map_data(bbox)
    
    return coords, bbox, graph, water, parks


def generate_single_poster(city, country, theme_name, distance, output_format, 
                          dpi, figsize, output_file=None):
    """
    Generate a single poster for the given parameters.
    Fetches all necessary data and renders the poster.
    
    Args:
        city: City name
        country: Country name  
        theme_name: Theme to use
        distance: Map radius in meters
        output_format: Output format (png, svg, pdf)
        dpi: DPI for rendering
        figsize: Figure size tuple
        output_file: Optional output file path (auto-generated if None)
    
    Returns:
        Path to the generated file
    """
    # Fetch map resources
    coords, bbox, graph, water, parks = fetch_map_resources(city, country, distance, figsize)
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = generate_output_filename(city, theme_name, output_format)
    
    # Render poster
    return render_single_poster(
        city, country, theme_name, coords, 
        graph, water, parks,
        output_format, dpi, figsize, output_file
    )


def generate_all_themes(city, country, distance, output_format, dpi, figsize):
    """
    Generate posters for all available themes for a given city.
    Fetches map data once and reuses it for all themes.
    
    Args:
        city, country: Location info
        distance: Map radius in meters
        output_format, dpi, figsize: Rendering parameters
    
    Returns:
        Dict with 'successful', 'failed', and 'output_dir' keys
    """
    print("=" * 50)
    print(f"Generating posters for ALL THEMES - {city}, {country}")
    print("=" * 50)
    
    # Get all available themes
    available_themes = get_available_themes()
    if not available_themes:
        print("✗ No themes found!")
        return {'successful': 0, 'failed': 0, 'output_dir': None}
    
    print(f"✓ Found {len(available_themes)} themes: {', '.join(available_themes)}")
    
    # Create city folder
    city_folder = generate_city_folder_name(city)
    city_dir = os.path.join(POSTERS_DIR, city_folder)
    os.makedirs(city_dir, exist_ok=True)
    print(f"✓ Created folder: {city_dir}")
    
    # Fetch map resources once (reuse for all themes)
    try:
        coords, bbox, graph, water, parks = fetch_map_resources(city, country, distance, figsize)
        print(f"✓ Coordinates: {coords}")
        print(f"✓ Bounding box calculated for {distance}m radius")
        print("✓ Map data fetched successfully")
    except Exception as e:
        print(f"✗ Error fetching map resources: {e}")
        return {'successful': 0, 'failed': 0, 'output_dir': None}
    
    # Generate poster for each theme
    successful = 0
    failed = 0
    
    for i, theme_name in enumerate(available_themes, 1):
        try:
            print(f"\n[{i}/{len(available_themes)}] Generating {theme_name}...")
            
            # Generate output filename in city folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = output_format.lower()
            filename = f"{city_folder}_{theme_name}_{timestamp}.{ext}"
            output_file = os.path.join(city_dir, filename)
            
            # Render poster with pre-fetched data
            render_single_poster(
                city, country, theme_name, coords, 
                graph, water, parks,
                output_format, dpi, figsize, output_file
            )
            
            print(f"✓ Saved: {filename}")
            successful += 1
            
        except Exception as e:
            print(f"✗ Failed {theme_name}: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("Batch generation complete!")
    print(f"✓ Successful: {successful}")
    if failed > 0:
        print(f"✗ Failed: {failed}")
    print(f"📁 Output folder: {city_dir}")
    print("=" * 50)
    
    return {
        'successful': successful,
        'failed': failed,
        'output_dir': city_dir
    }
