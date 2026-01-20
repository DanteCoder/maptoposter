#!/usr/bin/env python3
"""
City Map Poster Generator
Generate beautiful map posters for any city.
"""

import sys
import traceback

from src import (
    calculate_dpi_from_resolution,
    create_parser,
    validate_args,
    generate_single_poster,
    generate_all_themes,
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
    
    # Handle all-themes mode
    if args.all_themes:
        generate_all_themes(
            args.city, args.country, args.distance, 
            args.format, dpi, figsize
        )
        return
    
    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)
    
    # Generate single poster
    try:
        output_file = generate_single_poster(
            args.city, args.country, args.theme, args.distance,
            args.format, dpi, figsize
        )
        
        print("\n" + "=" * 50)
        print("✓ Poster generation complete!")
        print(f"📁 Saved to: {output_file}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
