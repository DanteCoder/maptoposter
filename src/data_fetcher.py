"""Data fetching from OpenStreetMap using OSMnx."""

import time
import osmnx as ox
from tqdm import tqdm

from .cache import cache_get, cache_set, CacheError


def fetch_graph_bbox(bbox):
    """Fetch graph using bbox with caching."""
    west, south, east, north = bbox
    graph_key = f"graph_bbox_{west}_{south}_{east}_{north}"
    cached = cache_get(graph_key)
    if cached is not None:
        print("✓ Using cached street network")
        return cached
    
    try:
        G = ox.graph_from_bbox(bbox=bbox, network_type='all')
        # Rate limit between requests
        time.sleep(0.5)
        try:
            cache_set(graph_key, G)
        except CacheError as e:
            print(e)
        return G
    except Exception as e:
        print(f"OSMnx error while fetching graph: {e}")
        return None


def fetch_features_bbox(bbox, tags, name):
    """Fetch features using bbox with caching."""
    west, south, east, north = bbox
    tag_str = "_".join(tags.keys())
    features_key = f"{name}_bbox_{west}_{south}_{east}_{north}_{tag_str}"
    cached = cache_get(features_key)
    if cached is not None:
        print(f"✓ Using cached {name}")
        return cached
    
    try:
        data = ox.features_from_bbox(bbox=bbox, tags=tags)
        # Rate limit between requests
        time.sleep(0.3)
        try:
            cache_set(features_key, data)
        except CacheError as e:
            print(e)
        return data
    except Exception as e:
        print(f"OSMnx error while fetching features: {e}")
        return None


def fetch_map_data(bbox):
    """
    Fetch all map data (streets, water, parks) with progress bar.
    Returns tuple: (graph, water, parks)
    """
    with tqdm(total=3, desc="Fetching map data", unit="step", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
        # 1. Fetch Street Network
        pbar.set_description("Downloading street network")
        graph = fetch_graph_bbox(bbox)
        pbar.update(1)
        
        # 2. Fetch Water Features
        pbar.set_description("Downloading water features")
        water = fetch_features_bbox(bbox, {'natural': 'water', 'waterway': 'riverbank'}, 'water')
        pbar.update(1)
        
        # 3. Fetch Parks
        pbar.set_description("Downloading parks/green spaces")
        parks = fetch_features_bbox(bbox, {'leisure': 'park', 'landuse': 'grass'}, 'parks')
        pbar.update(1)
    
    print("✓ All data downloaded successfully!")
    return graph, water, parks
