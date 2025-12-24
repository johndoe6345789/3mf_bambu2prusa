"""Tests for the CLI frontend."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_cli_import():
    """Test that CLI module can be imported."""
    from frontends.cli import main
    assert callable(main)


def test_cli_help_output(capsys):
    """Test CLI help output."""
    from frontends.cli.main import main
    
    with patch.object(sys, 'argv', ['bambu2prusa-cli', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    
    captured = capsys.readouterr()
    assert 'Convert Bambu Studio 3mf files' in captured.out
    assert 'input' in captured.out
    assert 'output' in captured.out


def test_cli_missing_input_file(tmp_path, capsys):
    """Test CLI with missing input file."""
    from frontends.cli.main import main
    
    input_file = tmp_path / "missing.3mf"
    output_file = tmp_path / "output.3mf"
    
    with patch.object(sys, 'argv', ['bambu2prusa-cli', str(input_file), str(output_file)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    assert 'Input file not found' in captured.err


def test_cli_invalid_input_extension(tmp_path, capsys):
    """Test CLI with invalid input file extension."""
    from frontends.cli.main import main
    
    input_file = tmp_path / "input.txt"
    input_file.touch()
    output_file = tmp_path / "output.3mf"
    
    with patch.object(sys, 'argv', ['bambu2prusa-cli', str(input_file), str(output_file)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    assert 'must be a .3mf file' in captured.err


def test_cli_invalid_output_extension(tmp_path, capsys):
    """Test CLI with invalid output file extension."""
    from frontends.cli.main import main
    
    input_file = tmp_path / "input.3mf"
    input_file.touch()
    output_file = tmp_path / "output.txt"
    
    with patch.object(sys, 'argv', ['bambu2prusa-cli', str(input_file), str(output_file)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    assert 'must have .3mf extension' in captured.err


def test_cli_successful_conversion(tmp_path, capsys):
    """Test CLI with successful conversion."""
    from frontends.cli.main import main
    
    input_file = tmp_path / "input.3mf"
    input_file.touch()
    output_file = tmp_path / "output.3mf"
    
    with patch('frontends.cli.main.BambuToPrusaConverter') as mock_converter:
        mock_instance = MagicMock()
        mock_converter.return_value = mock_instance
        
        with patch.object(sys, 'argv', ['bambu2prusa-cli', str(input_file), str(output_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        
        mock_instance.convert_archive.assert_called_once_with(str(input_file), str(output_file))
    
    captured = capsys.readouterr()
    assert 'Success' in captured.out
