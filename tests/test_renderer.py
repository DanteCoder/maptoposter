"""Tests for the renderer module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.renderer import (
    get_edge_colors_by_type,
    get_edge_widths_by_type,
    calculate_dynamic_font_size
)


@pytest.fixture
def sample_graph():
    """Create a sample graph with different road types."""
    graph = Mock()
    edges = [
        (1, 2, {'highway': 'motorway'}),
        (2, 3, {'highway': 'primary'}),
        (3, 4, {'highway': 'secondary'}),
        (4, 5, {'highway': 'tertiary'}),
        (5, 6, {'highway': 'residential'}),
        (6, 7, {'highway': 'footway'}),
        (7, 8, {'highway': ['motorway', 'trunk']}),  # List of types
        (8, 9, {}),  # Missing highway key
    ]
    graph.edges = Mock(return_value=edges)
    return graph


def test_get_edge_colors_by_type_motorway(sample_graph, sample_theme):
    """Test that motorways get the correct color."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    # First edge is motorway
    assert colors[0] == sample_theme['road_motorway']


def test_get_edge_colors_by_type_primary(sample_graph, sample_theme):
    """Test that primary roads get the correct color."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    # Second edge is primary
    assert colors[1] == sample_theme['road_primary']


def test_get_edge_colors_by_type_secondary(sample_graph, sample_theme):
    """Test that secondary roads get the correct color."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    # Third edge is secondary
    assert colors[2] == sample_theme['road_secondary']


def test_get_edge_colors_by_type_tertiary(sample_graph, sample_theme):
    """Test that tertiary roads get the correct color."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    # Fourth edge is tertiary
    assert colors[3] == sample_theme['road_tertiary']


def test_get_edge_colors_by_type_residential(sample_graph, sample_theme):
    """Test that residential roads get the correct color."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    # Fifth edge is residential
    assert colors[4] == sample_theme['road_residential']


def test_get_edge_colors_by_type_default(sample_graph, sample_theme):
    """Test that unknown road types get the default color."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    # Sixth edge is footway (should use default)
    assert colors[5] == sample_theme['road_default']


def test_get_edge_colors_by_type_list(sample_graph, sample_theme):
    """Test handling of highway type as list."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    # Seventh edge has list ['motorway', 'trunk'] - should use first
    assert colors[6] == sample_theme['road_motorway']


def test_get_edge_colors_by_type_missing_key(sample_graph, sample_theme):
    """Test handling of missing highway key."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    # Eighth edge has no highway key - should use residential
    assert colors[7] == sample_theme['road_residential']


def test_get_edge_colors_by_type_count(sample_graph, sample_theme):
    """Test that all edges get colors."""
    colors = get_edge_colors_by_type(sample_graph, sample_theme)
    
    assert len(colors) == 8


def test_get_edge_widths_by_type_motorway(sample_graph):
    """Test that motorways get the widest lines."""
    widths = get_edge_widths_by_type(sample_graph)
    
    # Motorway should be 1.2
    assert widths[0] == 1.2


def test_get_edge_widths_by_type_primary(sample_graph):
    """Test that primary roads get appropriate width."""
    widths = get_edge_widths_by_type(sample_graph)
    
    # Primary should be 1.0
    assert widths[1] == 1.0


def test_get_edge_widths_by_type_secondary(sample_graph):
    """Test that secondary roads get appropriate width."""
    widths = get_edge_widths_by_type(sample_graph)
    
    # Secondary should be 0.8
    assert widths[2] == 0.8


def test_get_edge_widths_by_type_tertiary(sample_graph):
    """Test that tertiary roads get appropriate width."""
    widths = get_edge_widths_by_type(sample_graph)
    
    # Tertiary should be 0.6
    assert widths[3] == 0.6


def test_get_edge_widths_by_type_default(sample_graph):
    """Test that other roads get minimum width."""
    widths = get_edge_widths_by_type(sample_graph)
    
    # Other roads should be 0.4
    assert widths[5] == 0.4


def test_get_edge_widths_by_type_hierarchy(sample_graph):
    """Test that widths follow hierarchy (motorway > primary > secondary > tertiary > other)."""
    widths = get_edge_widths_by_type(sample_graph)
    
    assert widths[0] > widths[1]  # motorway > primary
    assert widths[1] > widths[2]  # primary > secondary
    assert widths[2] > widths[3]  # secondary > tertiary
    assert widths[3] > widths[5]  # tertiary > other


def test_calculate_dynamic_font_size_short_name():
    """Test font size for short city names."""
    from src.config import BASE_FONT_SIZE, MAX_CITY_CHARS
    
    # Short name should use base font size
    size = calculate_dynamic_font_size("Paris")
    assert size == BASE_FONT_SIZE


def test_calculate_dynamic_font_size_exact_max():
    """Test font size for city name at MAX_CITY_CHARS."""
    from src.config import BASE_FONT_SIZE, MAX_CITY_CHARS
    
    # Name exactly at max should still use base size
    name = "A" * MAX_CITY_CHARS
    size = calculate_dynamic_font_size(name)
    assert size == BASE_FONT_SIZE


def test_calculate_dynamic_font_size_long_name():
    """Test font size for long city names."""
    from src.config import BASE_FONT_SIZE, MIN_FONT_SIZE
    
    # Long name should be scaled down
    long_name = "VeryLongCityName"
    size = calculate_dynamic_font_size(long_name)
    assert size < BASE_FONT_SIZE
    assert size >= MIN_FONT_SIZE


def test_calculate_dynamic_font_size_very_long_name():
    """Test font size doesn't go below minimum."""
    from src.config import MIN_FONT_SIZE
    
    # Very long name should hit minimum
    very_long_name = "A" * 100
    size = calculate_dynamic_font_size(very_long_name)
    assert size == MIN_FONT_SIZE


def test_calculate_dynamic_font_size_scaling():
    """Test that font size scales proportionally."""
    from src.config import BASE_FONT_SIZE, MAX_CITY_CHARS, MIN_FONT_SIZE
    
    # Name twice the max chars should be roughly half the base size (but not below MIN)
    name = "A" * (MAX_CITY_CHARS * 2)
    size = calculate_dynamic_font_size(name)
    expected = max(BASE_FONT_SIZE * 0.5, MIN_FONT_SIZE)
    assert abs(size - expected) < 1  # Allow small rounding difference


def test_get_edge_colors_empty_graph(sample_theme):
    """Test handling of empty graph."""
    graph = Mock()
    graph.edges = Mock(return_value=[])
    
    colors = get_edge_colors_by_type(graph, sample_theme)
    assert colors == []


def test_get_edge_widths_empty_graph():
    """Test handling of empty graph."""
    graph = Mock()
    graph.edges = Mock(return_value=[])
    
    widths = get_edge_widths_by_type(graph)
    assert widths == []
