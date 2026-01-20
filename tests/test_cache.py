"""Tests for the cache module."""

import pytest
import pickle
from pathlib import Path
from src.cache import CacheError, cache_file, cache_get, cache_set


def test_cache_file_hashing():
    """Test that cache_file generates consistent hashes."""
    key1 = "test_key"
    key2 = "test_key"
    key3 = "different_key"
    
    assert cache_file(key1) == cache_file(key2)
    assert cache_file(key1) != cache_file(key3)
    assert cache_file(key1).endswith(".pkl")


def test_cache_get_nonexistent(temp_cache_dir):
    """Test that cache_get returns None for non-existent keys."""
    result = cache_get("nonexistent_key")
    assert result is None


def test_cache_set_and_get(temp_cache_dir):
    """Test basic cache set and get functionality."""
    test_data = {"key": "value", "number": 42}
    cache_name = "test_cache"
    
    cache_set(cache_name, test_data)
    result = cache_get(cache_name)
    
    assert result == test_data
    assert result["key"] == "value"
    assert result["number"] == 42


def test_cache_set_different_types(temp_cache_dir):
    """Test caching different data types."""
    # Test dict
    cache_set("dict_test", {"a": 1, "b": 2})
    assert cache_get("dict_test") == {"a": 1, "b": 2}
    
    # Test list
    cache_set("list_test", [1, 2, 3, 4])
    assert cache_get("list_test") == [1, 2, 3, 4]
    
    # Test tuple
    cache_set("tuple_test", (1, 2, 3))
    assert cache_get("tuple_test") == (1, 2, 3)
    
    # Test string
    cache_set("string_test", "hello world")
    assert cache_get("string_test") == "hello world"
    
    # Test number
    cache_set("number_test", 12345)
    assert cache_get("number_test") == 12345


def test_cache_overwrite(temp_cache_dir):
    """Test that cache_set overwrites existing cache."""
    cache_name = "overwrite_test"
    
    cache_set(cache_name, "first_value")
    assert cache_get(cache_name) == "first_value"
    
    cache_set(cache_name, "second_value")
    assert cache_get(cache_name) == "second_value"


def test_cache_error_unpicklable(temp_cache_dir):
    """Test that CacheError is raised for unpicklable objects."""
    import threading
    lock = threading.Lock()
    
    with pytest.raises((CacheError, TypeError)):
        cache_set("unpicklable", lock)


def test_cache_error_invalid_path(monkeypatch, temp_cache_dir):
    """Test that CacheError is raised for file I/O errors."""
    import src.cache as cache_module
    
    # Mock the cache directory to an invalid path
    monkeypatch.setattr(cache_module, 'CACHE_DIR', Path("/invalid/path/that/does/not/exist"))
    
    with pytest.raises(CacheError) as exc_info:
        cache_set("test", {"data": "value"})
    
    assert "File error" in str(exc_info.value)


def test_cache_file_created(temp_cache_dir, monkeypatch):
    """Test that cache files are actually created in the cache directory."""
    # Ensure the module uses our temp cache dir
    from src import cache as cache_module
    monkeypatch.setattr(cache_module, 'CACHE_DIR', temp_cache_dir)
    
    cache_name = "file_test"
    cache_set(cache_name, {"test": "data"})
    
    expected_filename = cache_file(cache_name)
    expected_path = temp_cache_dir / expected_filename
    
    assert expected_path.exists()
    assert expected_path.is_file()


def test_cache_complex_nested_data(temp_cache_dir):
    """Test caching complex nested data structures."""
    complex_data = {
        "users": [
            {"name": "Alice", "age": 30, "scores": [95, 87, 92]},
            {"name": "Bob", "age": 25, "scores": [88, 91, 85]}
        ],
        "metadata": {
            "version": "1.0",
            "timestamp": 1234567890
        }
    }
    
    cache_set("complex_test", complex_data)
    result = cache_get("complex_test")
    
    assert result == complex_data
    assert result["users"][0]["name"] == "Alice"
    assert result["users"][1]["scores"][2] == 85
