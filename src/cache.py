"""Caching functionality for map data."""

import pickle
from hashlib import md5
from pathlib import Path

from .config import CACHE_DIR


class CacheError(Exception):
    """Raised when a cache operation fails."""
    pass


def cache_file(key: str) -> str:
    """Generate cache filename from key."""
    encoded = md5(key.encode()).hexdigest()
    return f"{encoded}.pkl"


def cache_get(name: str) -> dict | None:
    """Retrieve cached data by name."""
    path = CACHE_DIR / cache_file(name)
    if path.exists():
        with path.open("rb") as f:
            return pickle.load(f)
    return None


def cache_set(name: str, obj) -> None:
    """Store data in cache."""
    path = CACHE_DIR / cache_file(name)
    try:
        with path.open("wb") as f:
            pickle.dump(obj, f)
    except pickle.PickleError as e:
        raise CacheError(
            f"Serialization error while saving cache for '{name}': {e}"
        ) from e
    except (OSError, IOError) as e:
        raise CacheError(
            f"File error while saving cache for '{name}': {e}"
        ) from e
