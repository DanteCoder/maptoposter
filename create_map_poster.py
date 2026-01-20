#!/usr/bin/env python3
"""
City Map Poster Generator
Generate beautiful map posters for any city.
"""

import sys
import traceback

from src import (
    load_theme,
    load_fonts,
    get_coordinates,
    fetch_map_data,
    render_poster,
    generate_output_filename,
    calculate_dpi_from_resolution,
    calculate_bbox,
    create_parser,
    validate_args,
    DEFAULT_FIGSIZE,
    DEFAULT_DPI
)



def main():
    """Main entry point for the map poster generator."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate arguments
    validate_args(args)
    
    # Determine DPI and figsize
    figsize = DEFAULT_FIGSIZE
    if args.resolution:
        dpi = calculate_dpi_from_resolution(args.resolution, figsize)
        print(f"✓ Target resolution: {args.resolution} -> DPI: {dpi}")
    elif args.dpi:
        dpi = args.dpi
        print(f"✓ Using DPI: {dpi}")
    else:
        dpi = DEFAULT_DPI
        print(f"✓ Using default DPI: {dpi}")
    
    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)
    
    # Load theme and fonts
    theme = load_theme(args.theme)
    fonts = load_fonts()
    
    # Get coordinates and generate poster
    try:
        print(f"\nGenerating map for {args.city}, {args.country}...")
        
        coords = get_coordinates(args.city, args.country)
        bbox = calculate_bbox(coords, args.distance, figsize)
        
        # Fetch map data
        graph, water, parks = fetch_map_data(bbox)
        
        # Generate output filename
        output_file = generate_output_filename(args.city, args.theme, args.format)
        
        # Render poster
        render_poster(
            args.city, args.country, coords,
            graph, water, parks,
            theme, fonts,
            output_file, args.format,
            dpi=dpi, figsize=figsize
        )
        
        print("\n" + "=" * 50)
        print("✓ Poster generation complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
