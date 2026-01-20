"""Tests for the data_fetcher module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.data_fetcher import (
    fetch_graph_bbox,
    fetch_features_bbox,
    fetch_map_data
)
from src.cache import CacheError


@patch('src.data_fetcher.cache_get')
@patch('src.data_fetcher.cache_set')
@patch('src.data_fetcher.ox.graph_from_bbox')
@patch('src.data_fetcher.time.sleep')
def test_fetch_graph_bbox_from_cache(mock_sleep, mock_osmnx, mock_cache_set, mock_cache_get, capsys):
    """Test fetching graph from cache."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    mock_graph = Mock()
    mock_cache_get.return_value = mock_graph
    
    result = fetch_graph_bbox(bbox)
    
    assert result == mock_graph
    mock_cache_get.assert_called_once()
    mock_osmnx.assert_not_called()
    mock_sleep.assert_not_called()
    
    captured = capsys.readouterr()
    assert "cached" in captured.out.lower()


@patch('src.data_fetcher.cache_get')
@patch('src.data_fetcher.cache_set')
@patch('src.data_fetcher.ox.graph_from_bbox')
@patch('src.data_fetcher.time.sleep')
def test_fetch_graph_bbox_from_osm(mock_sleep, mock_osmnx, mock_cache_set, mock_cache_get):
    """Test fetching graph from OSM."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    mock_cache_get.return_value = None
    mock_graph = Mock()
    mock_osmnx.return_value = mock_graph
    
    result = fetch_graph_bbox(bbox)
    
    assert result == mock_graph
    mock_osmnx.assert_called_once_with(bbox=bbox, network_type='all')
    mock_cache_set.assert_called_once()
    mock_sleep.assert_called_once_with(0.5)  # Rate limiting


@patch('src.data_fetcher.cache_get')
@patch('src.data_fetcher.cache_set')
@patch('src.data_fetcher.ox.graph_from_bbox')
@patch('src.data_fetcher.time.sleep')
def test_fetch_graph_bbox_osm_error(mock_sleep, mock_osmnx, mock_cache_set, mock_cache_get, capsys):
    """Test handling OSM errors when fetching graph."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    mock_cache_get.return_value = None
    mock_osmnx.side_effect = Exception("OSM error")
    
    result = fetch_graph_bbox(bbox)
    
    assert result is None
    captured = capsys.readouterr()
    assert "OSMnx error" in captured.out


@patch('src.data_fetcher.cache_get')
@patch('src.data_fetcher.cache_set')
@patch('src.data_fetcher.ox.graph_from_bbox')
@patch('src.data_fetcher.time.sleep')
def test_fetch_graph_bbox_cache_error_handled(mock_sleep, mock_osmnx, mock_cache_set, mock_cache_get, capsys):
    """Test that cache errors don't prevent graph fetching."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    mock_cache_get.return_value = None
    mock_graph = Mock()
    mock_osmnx.return_value = mock_graph
    mock_cache_set.side_effect = CacheError("Cache write failed")
    
    result = fetch_graph_bbox(bbox)
    
    assert result == mock_graph
    captured = capsys.readouterr()
    assert "Cache write failed" in captured.out


@patch('src.data_fetcher.cache_get')
@patch('src.data_fetcher.cache_set')
@patch('src.data_fetcher.ox.features_from_bbox')
@patch('src.data_fetcher.time.sleep')
def test_fetch_features_bbox_from_cache(mock_sleep, mock_osmnx, mock_cache_set, mock_cache_get, capsys):
    """Test fetching features from cache."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    tags = {'natural': 'water'}
    mock_features = Mock()
    mock_cache_get.return_value = mock_features
    
    result = fetch_features_bbox(bbox, tags, 'water')
    
    assert result == mock_features
    mock_cache_get.assert_called_once()
    mock_osmnx.assert_not_called()
    
    captured = capsys.readouterr()
    assert "cached water" in captured.out.lower()


@patch('src.data_fetcher.cache_get')
@patch('src.data_fetcher.cache_set')
@patch('src.data_fetcher.ox.features_from_bbox')
@patch('src.data_fetcher.time.sleep')
def test_fetch_features_bbox_from_osm(mock_sleep, mock_osmnx, mock_cache_set, mock_cache_get):
    """Test fetching features from OSM."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    tags = {'leisure': 'park'}
    mock_features = Mock()
    mock_cache_get.return_value = None
    mock_osmnx.return_value = mock_features
    
    result = fetch_features_bbox(bbox, tags, 'parks')
    
    assert result == mock_features
    mock_osmnx.assert_called_once_with(bbox=bbox, tags=tags)
    mock_cache_set.assert_called_once()
    mock_sleep.assert_called_once_with(0.3)  # Rate limiting


@patch('src.data_fetcher.cache_get')
@patch('src.data_fetcher.cache_set')
@patch('src.data_fetcher.ox.features_from_bbox')
@patch('src.data_fetcher.time.sleep')
def test_fetch_features_bbox_osm_error(mock_sleep, mock_osmnx, mock_cache_set, mock_cache_get, capsys):
    """Test handling OSM errors when fetching features."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    tags = {'natural': 'water'}
    mock_cache_get.return_value = None
    mock_osmnx.side_effect = Exception("OSM error")
    
    result = fetch_features_bbox(bbox, tags, 'water')
    
    assert result is None
    captured = capsys.readouterr()
    assert "OSMnx error" in captured.out


@patch('src.data_fetcher.fetch_graph_bbox')
@patch('src.data_fetcher.fetch_features_bbox')
@patch('src.data_fetcher.tqdm')
def test_fetch_map_data_all_successful(mock_tqdm, mock_fetch_features, mock_fetch_graph, capsys):
    """Test fetching all map data successfully."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    
    # Mock progress bar
    mock_pbar = MagicMock()
    mock_tqdm.return_value.__enter__.return_value = mock_pbar
    
    # Mock data
    mock_graph = Mock()
    mock_water = Mock()
    mock_parks = Mock()
    
    mock_fetch_graph.return_value = mock_graph
    mock_fetch_features.side_effect = [mock_water, mock_parks]
    
    graph, water, parks = fetch_map_data(bbox)
    
    assert graph == mock_graph
    assert water == mock_water
    assert parks == mock_parks
    
    # Should fetch graph and two feature sets
    mock_fetch_graph.assert_called_once_with(bbox)
    assert mock_fetch_features.call_count == 2
    
    # Progress bar should be updated 3 times
    assert mock_pbar.update.call_count == 3
    
    captured = capsys.readouterr()
    assert "successfully" in captured.out.lower()


@patch('src.data_fetcher.fetch_graph_bbox')
@patch('src.data_fetcher.fetch_features_bbox')
@patch('src.data_fetcher.tqdm')
def test_fetch_map_data_with_progress_descriptions(mock_tqdm, mock_fetch_features, mock_fetch_graph):
    """Test that progress descriptions are set correctly."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    
    mock_pbar = MagicMock()
    mock_tqdm.return_value.__enter__.return_value = mock_pbar
    
    mock_fetch_graph.return_value = Mock()
    mock_fetch_features.side_effect = [Mock(), Mock()]
    
    fetch_map_data(bbox)
    
    # Check that descriptions were set
    description_calls = [call[0][0] for call in mock_pbar.set_description.call_args_list]
    assert "street" in description_calls[0].lower()
    assert "water" in description_calls[1].lower()
    assert "parks" in description_calls[2].lower()


@patch('src.data_fetcher.fetch_graph_bbox')
@patch('src.data_fetcher.fetch_features_bbox')
@patch('src.data_fetcher.tqdm')
def test_fetch_map_data_correct_tags(mock_tqdm, mock_fetch_features, mock_fetch_graph):
    """Test that correct tags are passed for features."""
    bbox = (-74.0, 40.7, -73.9, 40.8)
    
    mock_pbar = MagicMock()
    mock_tqdm.return_value.__enter__.return_value = mock_pbar
    
    mock_fetch_graph.return_value = Mock()
    mock_fetch_features.side_effect = [Mock(), Mock()]
    
    fetch_map_data(bbox)
    
    # Check water tags
    water_call = mock_fetch_features.call_args_list[0]
    assert water_call[0][1] == {'natural': 'water', 'waterway': 'riverbank'}
    assert water_call[0][2] == 'water'
    
    # Check parks tags
    parks_call = mock_fetch_features.call_args_list[1]
    assert parks_call[0][1] == {'leisure': 'park', 'landuse': 'grass'}
    assert parks_call[0][2] == 'parks'
