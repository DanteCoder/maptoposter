"""Tests for poster generator module."""

import os
from unittest.mock import Mock, patch, MagicMock, call
import pytest

from src.poster_generator import (
    render_single_poster,
    fetch_map_resources,
    generate_single_poster,
    generate_all_themes
)


# Test render_single_poster
def test_render_single_poster_loads_theme_and_fonts():
    """Test that render_single_poster loads theme and fonts."""
    mock_theme = {'name': 'Test', 'bg': '#FFF'}
    mock_fonts = {'bold': 'font.ttf'}
    
    with patch('src.poster_generator.load_theme', return_value=mock_theme) as mock_load_theme, \
         patch('src.poster_generator.load_fonts', return_value=mock_fonts) as mock_load_fonts, \
         patch('src.poster_generator.render_poster') as mock_render:
        
        coords = (40.7128, -74.0060)
        graph = Mock()
        water = Mock()
        parks = Mock()
        
        result = render_single_poster(
            "New York", "USA", "noir", coords,
            graph, water, parks,
            "png", 300, (16, 9), "output.png"
        )
        
        mock_load_theme.assert_called_once_with("noir")
        mock_load_fonts.assert_called_once()
        mock_render.assert_called_once()
        assert result == "output.png"


def test_render_single_poster_calls_render_with_correct_args():
    """Test that render_single_poster passes correct arguments to render_poster."""
    mock_theme = {'name': 'Test', 'bg': '#FFF'}
    mock_fonts = {'bold': 'font.ttf'}
    
    with patch('src.poster_generator.load_theme', return_value=mock_theme), \
         patch('src.poster_generator.load_fonts', return_value=mock_fonts), \
         patch('src.poster_generator.render_poster') as mock_render:
        
        coords = (40.7128, -74.0060)
        graph = Mock()
        water = Mock()
        parks = Mock()
        
        render_single_poster(
            "Tokyo", "Japan", "midnight_blue", coords,
            graph, water, parks,
            "svg", 150, (20, 10), "/path/to/output.svg"
        )
        
        call_args = mock_render.call_args
        assert call_args[0][0] == "Tokyo"
        assert call_args[0][1] == "Japan"
        assert call_args[0][2] == coords
        assert call_args[0][3] == graph
        assert call_args[0][4] == water
        assert call_args[0][5] == parks
        assert call_args[1]['dpi'] == 150
        assert call_args[1]['figsize'] == (20, 10)


# Test fetch_map_resources
def test_fetch_map_resources_fetches_all_data():
    """Test that fetch_map_resources fetches coordinates, bbox, and map data."""
    with patch('src.poster_generator.get_coordinates', return_value=(35.6762, 139.6503)) as mock_coords, \
         patch('src.poster_generator.calculate_bbox', return_value=(1, 2, 3, 4)) as mock_bbox, \
         patch('src.poster_generator.fetch_map_data', return_value=(Mock(), Mock(), Mock())) as mock_data:
        
        coords, bbox, graph, water, parks = fetch_map_resources(
            "Tokyo", "Japan", 15000, (16, 9)
        )
        
        mock_coords.assert_called_once_with("Tokyo", "Japan")
        mock_bbox.assert_called_once_with((35.6762, 139.6503), 15000, (16, 9))
        mock_data.assert_called_once_with((1, 2, 3, 4))
        
        assert coords == (35.6762, 139.6503)
        assert bbox == (1, 2, 3, 4)
        assert graph is not None
        assert water is not None
        assert parks is not None


def test_fetch_map_resources_returns_tuple():
    """Test that fetch_map_resources returns a 5-tuple."""
    with patch('src.poster_generator.get_coordinates', return_value=(0, 0)), \
         patch('src.poster_generator.calculate_bbox', return_value=(0, 0, 0, 0)), \
         patch('src.poster_generator.fetch_map_data', return_value=(None, None, None)):
        
        result = fetch_map_resources("City", "Country", 10000, (16, 9))
        
        assert isinstance(result, tuple)
        assert len(result) == 5


# Test generate_single_poster
def test_generate_single_poster_with_auto_filename():
    """Test single poster generation with auto-generated filename."""
    with patch('src.poster_generator.fetch_map_resources', return_value=((0, 0), (0, 0, 0, 0), Mock(), Mock(), Mock())), \
         patch('src.poster_generator.generate_output_filename', return_value="auto_output.png") as mock_filename, \
         patch('src.poster_generator.render_single_poster', return_value="auto_output.png") as mock_render:
        
        result = generate_single_poster(
            "Paris", "France", "pastel_dream", 10000,
            "png", 300, (16, 9)
        )
        
        mock_filename.assert_called_once_with("Paris", "pastel_dream", "png")
        assert result == "auto_output.png"


def test_generate_single_poster_with_explicit_filename():
    """Test single poster generation with explicit filename."""
    with patch('src.poster_generator.fetch_map_resources', return_value=((0, 0), (0, 0, 0, 0), Mock(), Mock(), Mock())), \
         patch('src.poster_generator.generate_output_filename') as mock_filename, \
         patch('src.poster_generator.render_single_poster', return_value="/custom/path.png") as mock_render:
        
        result = generate_single_poster(
            "Paris", "France", "noir", 10000,
            "png", 300, (16, 9), output_file="/custom/path.png"
        )
        
        # Should not call generate_output_filename when output_file is provided
        mock_filename.assert_not_called()
        assert result == "/custom/path.png"


def test_generate_single_poster_calls_render_with_fetched_data():
    """Test that generate_single_poster passes fetched data to render."""
    coords = (48.8566, 2.3522)
    bbox = (1, 2, 3, 4)
    graph = Mock()
    water = Mock()
    parks = Mock()
    
    with patch('src.poster_generator.fetch_map_resources', return_value=(coords, bbox, graph, water, parks)), \
         patch('src.poster_generator.generate_output_filename', return_value="output.png"), \
         patch('src.poster_generator.render_single_poster') as mock_render:
        
        generate_single_poster(
            "Paris", "France", "sunset", 10000,
            "png", 300, (16, 9)
        )
        
        call_args = mock_render.call_args
        assert call_args[0][3] == coords
        assert call_args[0][4] == graph
        assert call_args[0][5] == water
        assert call_args[0][6] == parks


# Test generate_all_themes
def test_generate_all_themes_no_themes_available():
    """Test generate_all_themes when no themes are available."""
    with patch('src.poster_generator.get_available_themes', return_value=[]):
        result = generate_all_themes("Tokyo", "Japan", 15000, "png", 300, (16, 9))
        
        assert result['successful'] == 0
        assert result['failed'] == 0
        assert result['output_dir'] is None


def test_generate_all_themes_creates_city_folder():
    """Test that generate_all_themes creates a city-specific folder."""
    with patch('src.poster_generator.get_available_themes', return_value=['theme1']), \
         patch('src.poster_generator.generate_city_folder_name', return_value='new_york'), \
         patch('src.poster_generator.fetch_map_resources', return_value=((0, 0), (0, 0, 0, 0), Mock(), Mock(), Mock())), \
         patch('src.poster_generator.render_single_poster'), \
         patch('os.makedirs') as mock_makedirs:
        
        generate_all_themes("New York", "USA", 12000, "png", 300, (16, 9))
        
        # Check that makedirs was called with the city folder path
        assert any('new_york' in str(call[0][0]) for call in mock_makedirs.call_args_list)


def test_generate_all_themes_fetches_data_once():
    """Test that generate_all_themes fetches map data only once."""
    with patch('src.poster_generator.get_available_themes', return_value=['theme1', 'theme2', 'theme3']), \
         patch('src.poster_generator.generate_city_folder_name', return_value='city'), \
         patch('src.poster_generator.fetch_map_resources', return_value=((0, 0), (0, 0, 0, 0), Mock(), Mock(), Mock())) as mock_fetch, \
         patch('src.poster_generator.render_single_poster'), \
         patch('os.makedirs'):
        
        generate_all_themes("City", "Country", 10000, "png", 300, (16, 9))
        
        # Should only fetch data once despite 3 themes
        mock_fetch.assert_called_once()


def test_generate_all_themes_renders_all_themes():
    """Test that generate_all_themes renders poster for each theme."""
    themes = ['theme1', 'theme2', 'theme3']
    
    with patch('src.poster_generator.get_available_themes', return_value=themes), \
         patch('src.poster_generator.generate_city_folder_name', return_value='city'), \
         patch('src.poster_generator.fetch_map_resources', return_value=((0, 0), (0, 0, 0, 0), Mock(), Mock(), Mock())), \
         patch('src.poster_generator.render_single_poster') as mock_render, \
         patch('os.makedirs'):
        
        result = generate_all_themes("City", "Country", 10000, "png", 300, (16, 9))
        
        # Should call render_single_poster once per theme
        assert mock_render.call_count == 3
        assert result['successful'] == 3
        assert result['failed'] == 0


def test_generate_all_themes_handles_render_failures():
    """Test that generate_all_themes handles individual theme failures gracefully."""
    themes = ['good_theme', 'bad_theme', 'another_good_theme']
    
    def render_side_effect(*args, **kwargs):
        theme_name = args[2]
        if theme_name == 'bad_theme':
            raise Exception("Rendering failed")
        return f"output_{theme_name}.png"
    
    with patch('src.poster_generator.get_available_themes', return_value=themes), \
         patch('src.poster_generator.generate_city_folder_name', return_value='city'), \
         patch('src.poster_generator.fetch_map_resources', return_value=((0, 0), (0, 0, 0, 0), Mock(), Mock(), Mock())), \
         patch('src.poster_generator.render_single_poster', side_effect=render_side_effect), \
         patch('os.makedirs'):
        
        result = generate_all_themes("City", "Country", 10000, "png", 300, (16, 9))
        
        assert result['successful'] == 2
        assert result['failed'] == 1


def test_generate_all_themes_returns_output_directory():
    """Test that generate_all_themes returns the output directory path."""
    with patch('src.poster_generator.get_available_themes', return_value=['theme1']), \
         patch('src.poster_generator.generate_city_folder_name', return_value='tokyo'), \
         patch('src.poster_generator.fetch_map_resources', return_value=((0, 0), (0, 0, 0, 0), Mock(), Mock(), Mock())), \
         patch('src.poster_generator.render_single_poster'), \
         patch('os.makedirs'):
        
        result = generate_all_themes("Tokyo", "Japan", 15000, "png", 300, (16, 9))
        
        assert 'output_dir' in result
        assert 'tokyo' in result['output_dir']


def test_generate_all_themes_handles_fetch_error():
    """Test generate_all_themes when fetching map resources fails."""
    with patch('src.poster_generator.get_available_themes', return_value=['theme1']), \
         patch('src.poster_generator.generate_city_folder_name', return_value='city'), \
         patch('src.poster_generator.fetch_map_resources', side_effect=Exception("Fetch failed")), \
         patch('os.makedirs'):
        
        result = generate_all_themes("City", "Country", 10000, "png", 300, (16, 9))
        
        assert result['successful'] == 0
        assert result['failed'] == 0
        assert result['output_dir'] is None


def test_generate_all_themes_uses_prefetched_data_for_all():
    """Test that all themes use the same pre-fetched data."""
    coords = (35.6762, 139.6503)
    graph = Mock()
    water = Mock()
    parks = Mock()
    
    render_calls = []
    
    def capture_render_call(*args, **kwargs):
        render_calls.append(args[3])  # coords argument
        return "output.png"
    
    with patch('src.poster_generator.get_available_themes', return_value=['theme1', 'theme2']), \
         patch('src.poster_generator.generate_city_folder_name', return_value='city'), \
         patch('src.poster_generator.fetch_map_resources', return_value=(coords, (0, 0, 0, 0), graph, water, parks)), \
         patch('src.poster_generator.render_single_poster', side_effect=capture_render_call), \
         patch('os.makedirs'):
        
        generate_all_themes("Tokyo", "Japan", 15000, "png", 300, (16, 9))
        
        # All calls should use the same coords object
        assert len(render_calls) == 2
        assert all(c == coords for c in render_calls)
