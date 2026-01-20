"""Tests for the CLI module."""

import pytest
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from src.cli import (
    create_parser,
    validate_args,
    print_examples
)


def test_create_parser():
    """Test that parser is created correctly."""
    parser = create_parser()
    
    assert parser is not None
    assert parser.description == "Generate beautiful map posters for any city"


def test_parser_city_argument():
    """Test city argument parsing."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France'])
    
    assert args.city == 'Paris'


def test_parser_country_argument():
    """Test country argument parsing."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France'])
    
    assert args.country == 'France'


def test_parser_theme_argument():
    """Test theme argument parsing."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France', '--theme', 'noir'])
    
    assert args.theme == 'noir'


def test_parser_theme_default():
    """Test theme has default value."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France'])
    
    assert args.theme == 'feature_based'


def test_parser_distance_argument():
    """Test distance argument parsing."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France', '--distance', '15000'])
    
    assert args.distance == 15000


def test_parser_distance_default():
    """Test distance has default value."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France'])
    
    assert args.distance == 29000


def test_parser_format_argument():
    """Test format argument parsing."""
    parser = create_parser()
    
    args_png = parser.parse_args(['--city', 'Paris', '--country', 'France', '--format', 'png'])
    assert args_png.format == 'png'
    
    args_svg = parser.parse_args(['--city', 'Paris', '--country', 'France', '--format', 'svg'])
    assert args_svg.format == 'svg'
    
    args_pdf = parser.parse_args(['--city', 'Paris', '--country', 'France', '--format', 'pdf'])
    assert args_pdf.format == 'pdf'


def test_parser_format_default():
    """Test format has default value."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France'])
    
    assert args.format == 'png'


def test_parser_resolution_argument():
    """Test resolution argument parsing."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France', '--resolution', '3840x2160'])
    
    assert args.resolution == '3840x2160'


def test_parser_dpi_argument():
    """Test DPI argument parsing."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France', '--dpi', '600'])
    
    assert args.dpi == 600


def test_parser_list_themes_flag():
    """Test list-themes flag parsing."""
    parser = create_parser()
    args = parser.parse_args(['--list-themes'])
    
    assert args.list_themes is True


def test_parser_short_options():
    """Test short option aliases."""
    parser = create_parser()
    args = parser.parse_args(['-c', 'Tokyo', '-C', 'Japan', '-t', 'noir', '-d', '20000', '-f', 'svg'])
    
    assert args.city == 'Tokyo'
    assert args.country == 'Japan'
    assert args.theme == 'noir'
    assert args.distance == 20000
    assert args.format == 'svg'


@patch('src.cli.sys.exit')
@patch('src.cli.sys.argv', ['script.py'])
def test_validate_args_no_arguments(mock_exit):
    """Test that validate_args exits when no arguments provided."""
    parser = create_parser()
    args = parser.parse_args([])
    
    # With no args, both city and country are None, so it should exit with 1
    validate_args(args)
    
    # Should be called at least once (may be called multiple times due to arg checks)
    assert mock_exit.called


@patch('src.cli.sys.exit')
@patch('src.theme.list_themes')
def test_validate_args_list_themes(mock_list_themes, mock_exit):
    """Test that validate_args handles list-themes flag."""
    parser = create_parser()
    args = parser.parse_args(['--list-themes'])
    
    validate_args(args)
    mock_list_themes.assert_called_once()
    # Should exit (may be called multiple times due to validation flow)
    assert mock_exit.called


@patch('src.cli.sys.exit')
@patch('src.cli.print_examples')
def test_validate_args_missing_city(mock_print_examples, mock_exit, capsys):
    """Test that validate_args exits when city is missing."""
    parser = create_parser()
    args = parser.parse_args(['--country', 'France'])
    
    validate_args(args)
    
    captured = capsys.readouterr()
    assert "required" in captured.out.lower()
    mock_exit.assert_called_once_with(1)


@patch('src.cli.sys.exit')
@patch('src.cli.print_examples')
def test_validate_args_missing_country(mock_print_examples, mock_exit, capsys):
    """Test that validate_args exits when country is missing."""
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris'])
    
    validate_args(args)
    
    captured = capsys.readouterr()
    assert "required" in captured.out.lower()
    mock_exit.assert_called_once_with(1)


@patch('src.cli.sys.exit')
@patch('src.cli.get_available_themes')
def test_validate_args_invalid_theme(mock_get_themes, mock_exit, capsys):
    """Test that validate_args exits when theme doesn't exist."""
    mock_get_themes.return_value = ['noir', 'sunset', 'ocean']
    
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France', '--theme', 'nonexistent'])
    
    validate_args(args)
    
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()
    mock_exit.assert_called_once_with(1)


@patch('src.cli.sys.exit')
@patch('src.cli.get_available_themes')
def test_validate_args_valid_theme(mock_get_themes, mock_exit):
    """Test that validate_args passes with valid theme."""
    mock_get_themes.return_value = ['noir', 'sunset', 'ocean']
    
    parser = create_parser()
    args = parser.parse_args(['--city', 'Paris', '--country', 'France', '--theme', 'noir'])
    
    # Should not raise or exit
    result = validate_args(args)
    assert result is True


@patch('src.cli.sys.exit')
def test_validate_args_both_resolution_and_dpi(mock_exit, capsys):
    """Test that validate_args exits when both resolution and DPI are specified."""
    parser = create_parser()
    args = parser.parse_args([
        '--city', 'Paris', '--country', 'France',
        '--resolution', '3840x2160', '--dpi', '600'
    ])
    
    validate_args(args)
    
    captured = capsys.readouterr()
    assert "both" in captured.out.lower()
    mock_exit.assert_called_once_with(1)


@patch('src.cli.sys.exit')
@patch('src.cli.get_available_themes')
def test_validate_args_resolution_only(mock_get_themes, mock_exit):
    """Test that validate_args accepts resolution without DPI."""
    mock_get_themes.return_value = ['noir']
    
    parser = create_parser()
    args = parser.parse_args([
        '--city', 'Paris', '--country', 'France',
        '--resolution', '3840x2160'
    ])
    
    result = validate_args(args)
    assert result is True


@patch('src.cli.sys.exit')
@patch('src.cli.get_available_themes')
def test_validate_args_dpi_only(mock_get_themes, mock_exit):
    """Test that validate_args accepts DPI without resolution."""
    mock_get_themes.return_value = ['noir']
    
    parser = create_parser()
    args = parser.parse_args([
        '--city', 'Paris', '--country', 'France',
        '--dpi', '600'
    ])
    
    result = validate_args(args)
    assert result is True


def test_print_examples_output(capsys):
    """Test that print_examples outputs usage information."""
    print_examples()
    
    captured = capsys.readouterr()
    assert "City Map Poster Generator" in captured.out
    assert "Usage:" in captured.out
    assert "Examples:" in captured.out
    assert "New York" in captured.out
    assert "Paris" in captured.out


def test_print_examples_has_distance_guide(capsys):
    """Test that print_examples includes distance guide."""
    print_examples()
    
    captured = capsys.readouterr()
    assert "Distance guide:" in captured.out
    assert "4000-6000m" in captured.out
