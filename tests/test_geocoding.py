"""Tests for the geocoding module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.geocoding import get_coordinates
from src.cache import CacheError


@patch('src.geocoding.cache_get')
@patch('src.geocoding.cache_set')
@patch('src.geocoding.Nominatim')
@patch('src.geocoding.time.sleep')
def test_get_coordinates_from_cache(mock_sleep, mock_nominatim, mock_cache_set, mock_cache_get, capsys):
    """Test getting coordinates from cache."""
    mock_cache_get.return_value = (40.7128, -74.0060)
    
    result = get_coordinates("New York", "USA")
    
    assert result == (40.7128, -74.0060)
    mock_cache_get.assert_called_once()
    mock_nominatim.assert_not_called()
    
    captured = capsys.readouterr()
    assert "cached" in captured.out.lower()


@patch('src.geocoding.cache_get')
@patch('src.geocoding.cache_set')
@patch('src.geocoding.Nominatim')
@patch('src.geocoding.time.sleep')
def test_get_coordinates_from_api(mock_sleep, mock_nominatim, mock_cache_set, mock_cache_get, capsys):
    """Test getting coordinates from Nominatim API."""
    mock_cache_get.return_value = None
    
    # Mock location object
    mock_location = Mock()
    mock_location.latitude = 48.8566
    mock_location.longitude = 2.3522
    mock_location.address = "Paris, France"
    
    # Mock geolocator
    mock_geolocator = Mock()
    mock_geolocator.geocode.return_value = mock_location
    mock_nominatim.return_value = mock_geolocator
    
    result = get_coordinates("Paris", "France")
    
    assert result == (48.8566, 2.3522)
    mock_cache_get.assert_called_once()
    mock_cache_set.assert_called_once()
    mock_sleep.assert_called_once()  # Rate limiting
    
    captured = capsys.readouterr()
    assert "Paris, France" in captured.out


@patch('src.geocoding.cache_get')
@patch('src.geocoding.cache_set')
@patch('src.geocoding.Nominatim')
@patch('src.geocoding.time.sleep')
def test_get_coordinates_not_found(mock_sleep, mock_nominatim, mock_cache_set, mock_cache_get):
    """Test handling when location is not found."""
    mock_cache_get.return_value = None
    
    # Mock geolocator that returns None
    mock_geolocator = Mock()
    mock_geolocator.geocode.return_value = None
    mock_nominatim.return_value = mock_geolocator
    
    with pytest.raises(ValueError, match="Could not find coordinates"):
        get_coordinates("InvalidCity", "InvalidCountry")


@patch('src.geocoding.cache_get')
@patch('src.geocoding.cache_set')
@patch('src.geocoding.Nominatim')
@patch('src.geocoding.time.sleep')
def test_get_coordinates_cache_error_handled(mock_sleep, mock_nominatim, mock_cache_set, mock_cache_get, capsys):
    """Test that cache errors don't prevent coordinate lookup."""
    mock_cache_get.return_value = None
    mock_cache_set.side_effect = CacheError("Cache write failed")
    
    # Mock location
    mock_location = Mock()
    mock_location.latitude = 35.6762
    mock_location.longitude = 139.6503
    mock_location.address = "Tokyo, Japan"
    
    mock_geolocator = Mock()
    mock_geolocator.geocode.return_value = mock_location
    mock_nominatim.return_value = mock_geolocator
    
    # Should still return coordinates despite cache error
    result = get_coordinates("Tokyo", "Japan")
    assert result == (35.6762, 139.6503)
    
    captured = capsys.readouterr()
    assert "Cache write failed" in captured.out


@patch('src.geocoding.cache_get')
@patch('src.geocoding.cache_set')
@patch('src.geocoding.Nominatim')
@patch('src.geocoding.time.sleep')
def test_get_coordinates_nominatim_config(mock_sleep, mock_nominatim, mock_cache_set, mock_cache_get):
    """Test that Nominatim is configured correctly."""
    mock_cache_get.return_value = None
    
    mock_location = Mock()
    mock_location.latitude = 51.5074
    mock_location.longitude = -0.1278
    mock_location.address = "London, UK"
    
    mock_geolocator = Mock()
    mock_geolocator.geocode.return_value = mock_location
    mock_nominatim.return_value = mock_geolocator
    
    get_coordinates("London", "UK")
    
    # Check Nominatim was initialized with correct parameters
    mock_nominatim.assert_called_once_with(user_agent="city_map_poster", timeout=10)


@patch('src.geocoding.cache_get')
@patch('src.geocoding.cache_set')
@patch('src.geocoding.Nominatim')
@patch('src.geocoding.time.sleep')
def test_get_coordinates_rate_limiting(mock_sleep, mock_nominatim, mock_cache_set, mock_cache_get):
    """Test that rate limiting is applied."""
    mock_cache_get.return_value = None
    
    mock_location = Mock()
    mock_location.latitude = 40.0
    mock_location.longitude = -100.0
    mock_location.address = "Test Location"
    
    mock_geolocator = Mock()
    mock_geolocator.geocode.return_value = mock_location
    mock_nominatim.return_value = mock_geolocator
    
    get_coordinates("Test", "Location")
    
    # Should sleep for rate limiting
    mock_sleep.assert_called_with(1)


@patch('src.geocoding.cache_get')
@patch('src.geocoding.cache_set')
@patch('src.geocoding.Nominatim')
@patch('src.geocoding.time.sleep')
def test_get_coordinates_cache_key_format(mock_sleep, mock_nominatim, mock_cache_set, mock_cache_get):
    """Test that cache key is formatted correctly."""
    mock_cache_get.return_value = None
    
    mock_location = Mock()
    mock_location.latitude = 40.0
    mock_location.longitude = -100.0
    mock_location.address = "Test"
    
    mock_geolocator = Mock()
    mock_geolocator.geocode.return_value = mock_location
    mock_nominatim.return_value = mock_geolocator
    
    get_coordinates("New York", "USA")
    
    # Cache key should be lowercase with underscores
    expected_key = "coords_new york_usa"
    mock_cache_get.assert_called_with(expected_key)
    
    # After successful lookup, should cache with same key
    call_args = mock_cache_set.call_args
    assert call_args[0][0] == expected_key
