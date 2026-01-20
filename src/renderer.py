"""Map rendering and visualization functionality."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import osmnx as ox

from .config import BASE_FONT_SIZE, MIN_FONT_SIZE, MAX_CITY_CHARS, DEFAULT_FIGSIZE, DEFAULT_DPI
from .theme import create_font_properties


def create_gradient_fade(ax, color, location='bottom', zorder=10):
    """
    Creates a fade effect at the edges of the map.
    Supports: 'bottom', 'top', 'left', 'right'
    """
    rgb = mcolors.to_rgb(color)
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    
    if location in ['bottom', 'top']:
        vals = np.linspace(0, 1, 256).reshape(-1, 1)
        gradient = np.hstack((vals, vals))
        
        my_colors = np.zeros((256, 4))
        my_colors[:, 0] = rgb[0]
        my_colors[:, 1] = rgb[1]
        my_colors[:, 2] = rgb[2]
        
        if location == 'bottom':
            my_colors[:, 3] = np.linspace(1, 0, 256)
            extent_y_start = 0
            extent_y_end = 0.15
        else:  # top
            my_colors[:, 3] = np.linspace(0, 1, 256)
            extent_y_start = 0.85
            extent_y_end = 1.0
        
        y_bottom = ylim[0] + y_range * extent_y_start
        y_top = ylim[0] + y_range * extent_y_end
        
        custom_cmap = mcolors.ListedColormap(my_colors)
        ax.imshow(gradient, extent=[xlim[0], xlim[1], y_bottom, y_top], 
                  aspect='auto', cmap=custom_cmap, zorder=zorder, origin='lower')
    
    else:  # left or right
        vals = np.linspace(0, 1, 256).reshape(1, -1)
        gradient = np.vstack((vals, vals))
        
        my_colors = np.zeros((256, 4))
        my_colors[:, 0] = rgb[0]
        my_colors[:, 1] = rgb[1]
        my_colors[:, 2] = rgb[2]
        
        if location == 'left':
            my_colors[:, 3] = np.linspace(1, 0, 256)
            extent_x_start = 0
            extent_x_end = 0.10
        else:  # right
            my_colors[:, 3] = np.linspace(0, 1, 256)
            extent_x_start = 0.90
            extent_x_end = 1.0
        
        x_left = xlim[0] + x_range * extent_x_start
        x_right = xlim[0] + x_range * extent_x_end
        
        custom_cmap = mcolors.ListedColormap(my_colors)
        ax.imshow(gradient, extent=[x_left, x_right, ylim[0], ylim[1]], 
                  aspect='auto', cmap=custom_cmap, zorder=zorder, origin='lower')


def get_edge_colors_by_type(G, theme):
    """
    Assigns colors to edges based on road type hierarchy.
    Returns a list of colors corresponding to each edge in the graph.
    """
    edge_colors = []
    
    for u, v, data in G.edges(data=True):
        # Get the highway type (can be a list or string)
        highway = data.get('highway', 'unclassified')
        
        # Handle list of highway types (take the first one)
        if isinstance(highway, list):
            highway = highway[0] if highway else 'unclassified'
        
        # Assign color based on road type
        if highway in ['motorway', 'motorway_link']:
            color = theme['road_motorway']
        elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
            color = theme['road_primary']
        elif highway in ['secondary', 'secondary_link']:
            color = theme['road_secondary']
        elif highway in ['tertiary', 'tertiary_link']:
            color = theme['road_tertiary']
        elif highway in ['residential', 'living_street', 'unclassified']:
            color = theme['road_residential']
        else:
            color = theme['road_default']
        
        edge_colors.append(color)
    
    return edge_colors


def get_edge_widths_by_type(G):
    """
    Assigns line widths to edges based on road type.
    Major roads get thicker lines.
    """
    edge_widths = []
    
    for u, v, data in G.edges(data=True):
        highway = data.get('highway', 'unclassified')
        
        if isinstance(highway, list):
            highway = highway[0] if highway else 'unclassified'
        
        # Assign width based on road importance
        if highway in ['motorway', 'motorway_link']:
            width = 1.2
        elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
            width = 1.0
        elif highway in ['secondary', 'secondary_link']:
            width = 0.8
        elif highway in ['tertiary', 'tertiary_link']:
            width = 0.6
        else:
            width = 0.4
        
        edge_widths.append(width)
    
    return edge_widths


def calculate_dynamic_font_size(city_name):
    """
    Dynamically adjust font size based on city name length to prevent truncation.
    """
    city_char_count = len(city_name)
    if city_char_count > MAX_CITY_CHARS:
        # Scale down font size for longer names
        scale_factor = MAX_CITY_CHARS / city_char_count
        adjusted_font_size = max(BASE_FONT_SIZE * scale_factor, MIN_FONT_SIZE)
    else:
        adjusted_font_size = BASE_FONT_SIZE
    return adjusted_font_size


def render_poster(city, country, point, graph, water, parks, theme, fonts, 
                  output_file, output_format, dpi=DEFAULT_DPI, figsize=DEFAULT_FIGSIZE):
    """
    Render the final map poster with all layers and typography.
    """
    print("Rendering map...")
    
    # Setup Plot
    fig, ax = plt.subplots(figsize=figsize, facecolor=theme['bg'])
    ax.set_facecolor(theme['bg'])
    ax.set_position((0, 0, 1, 1))
    
    # Project graph to UTM for proper metric plotting
    graph_proj = ox.project_graph(graph)
    
    # Plot Layers
    # Layer 1: Polygons (filter to only plot polygon/multipolygon geometries)
    if water is not None and not water.empty:
        water_polys = water[water.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        if not water_polys.empty:
            # Project water to same CRS as graph
            water_polys = water_polys.to_crs(graph_proj.graph['crs'])
            water_polys.plot(ax=ax, facecolor=theme['water'], edgecolor='none', zorder=1)
    
    if parks is not None and not parks.empty:
        parks_polys = parks[parks.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        if not parks_polys.empty:
            # Project parks to same CRS as graph
            parks_polys = parks_polys.to_crs(graph_proj.graph['crs'])
            parks_polys.plot(ax=ax, facecolor=theme['parks'], edgecolor='none', zorder=2)
    
    # Layer 2: Roads with hierarchy coloring
    print("Applying road hierarchy colors...")
    edge_colors = get_edge_colors_by_type(graph_proj, theme)
    edge_widths = get_edge_widths_by_type(graph_proj)
    
    ox.plot_graph(
        graph_proj, ax=ax, bgcolor=theme['bg'],
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=edge_widths,
        show=False, close=False
    )
    
    # Set equal aspect to prevent geographic distortion
    ax.set_aspect('equal', adjustable='datalim')
    
    # Adjust data limits to match figure aspect ratio
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_center = (xlim[0] + xlim[1]) / 2
    y_center = (ylim[0] + ylim[1]) / 2
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    
    fig_width, fig_height = figsize
    target_aspect = fig_width / fig_height  # 12/16 = 0.75
    current_aspect = x_range / y_range
    
    if current_aspect > target_aspect:
        # Data is wider than figure, need to expand vertically
        new_y_range = x_range / target_aspect
        ax.set_ylim(y_center - new_y_range/2, y_center + new_y_range/2)
    else:
        # Data is taller than figure, need to expand horizontally
        new_x_range = y_range * target_aspect
        ax.set_xlim(x_center - new_x_range/2, x_center + new_x_range/2)
    
    # Layer 3: Gradients (All edges)
    create_gradient_fade(ax, theme['gradient_color'], location='bottom', zorder=10)
    create_gradient_fade(ax, theme['gradient_color'], location='top', zorder=10)
    create_gradient_fade(ax, theme['gradient_color'], location='left', zorder=10)
    create_gradient_fade(ax, theme['gradient_color'], location='right', zorder=10)
    
    # Typography
    adjusted_font_size = calculate_dynamic_font_size(city)
    font_props = create_font_properties(fonts, adjusted_font_size)
    
    spaced_city = "  ".join(list(city.upper()))
    
    # Bottom text
    ax.text(0.5, 0.14, spaced_city, transform=ax.transAxes,
            color=theme['text'], ha='center', fontproperties=font_props['main'], zorder=11)
    
    ax.text(0.5, 0.10, country.upper(), transform=ax.transAxes,
            color=theme['text'], ha='center', fontproperties=font_props['sub'], zorder=11)
    
    lat, lon = point
    coords = f"{lat:.4f}° N / {lon:.4f}° E" if lat >= 0 else f"{abs(lat):.4f}° S / {lon:.4f}° E"
    if lon < 0:
        coords = coords.replace("E", "W")
    
    ax.text(0.5, 0.07, coords, transform=ax.transAxes,
            color=theme['text'], alpha=0.7, ha='center', fontproperties=font_props['coords'], zorder=11)
    
    ax.plot([0.4, 0.6], [0.125, 0.125], transform=ax.transAxes, 
            color=theme['text'], linewidth=1, zorder=11)
    
    # Attribution (bottom right)
    ax.text(0.98, 0.02, "© OpenStreetMap contributors", transform=ax.transAxes,
            color=theme['text'], alpha=0.5, ha='right', va='bottom', 
            fontproperties=font_props['attr'], zorder=11)
    
    # Save
    print(f"Saving to {output_file}...")
    
    fmt = output_format.lower()
    save_kwargs = dict(facecolor=theme["bg"], bbox_inches="tight", pad_inches=0.05)
    
    # DPI matters mainly for raster formats
    if fmt == "png":
        save_kwargs["dpi"] = dpi
        width_px = int(figsize[0] * dpi)
        height_px = int(figsize[1] * dpi)
        print(f"  Resolution: {width_px}x{height_px} pixels ({dpi} DPI)")
    
    plt.savefig(output_file, format=fmt, **save_kwargs)
    plt.close()
    
    print(f"✓ Done! Poster saved as {output_file}")
