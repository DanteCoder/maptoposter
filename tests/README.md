# Tests

Comprehensive test suite for the map poster generator.

## Running Tests

Install test dependencies:

```bash
pip install pytest pytest-cov
```

Run all tests:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

Run specific test file:

```bash
pytest tests/test_cache.py
pytest tests/test_theme.py -v
```

Run tests matching a pattern:

```bash
pytest -k "cache"
pytest -k "test_load_theme"
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_config.py` - Configuration constants and environment variables
- `test_cache.py` - Caching functionality
- `test_theme.py` - Theme and font loading
- `test_utils.py` - Utility functions (filenames, resolution, bbox)
- `test_geocoding.py` - Coordinate fetching with mocked API calls
- `test_data_fetcher.py` - OSM data fetching with mocked API calls
- `test_renderer.py` - Rendering helper functions
- `test_cli.py` - Command-line argument parsing and validation

## Test Coverage

The test suite covers:

- ✅ Configuration management
- ✅ Cache operations with error handling
- ✅ Theme loading and font properties
- ✅ Utility functions (resolution, DPI, bbox calculations)
- ✅ Geocoding with API mocking
- ✅ OSM data fetching with API mocking
- ✅ Road hierarchy and color assignment
- ✅ Dynamic font sizing
- ✅ CLI argument parsing and validation

## Fixtures

Common fixtures defined in `conftest.py`:

- `temp_cache_dir` - Temporary cache directory
- `temp_themes_dir` - Temporary themes directory with sample themes
- `temp_fonts_dir` - Temporary fonts directory
- `sample_theme` - Sample theme dictionary
- `sample_coordinates` - Sample coordinates (NYC)

## Writing New Tests

Example test structure:

```python
def test_your_feature(fixture_name):
    """Test description."""
    # Arrange
    input_data = "test"

    # Act
    result = your_function(input_data)

    # Assert
    assert result == expected_value
```

Use mocking for external dependencies:

```python
from unittest.mock import patch, Mock

@patch('module.external_function')
def test_with_mock(mock_external):
    mock_external.return_value = "mocked_value"
    result = function_that_calls_external()
    assert result == expected
```
