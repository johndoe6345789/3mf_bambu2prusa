"""Backward compatibility wrapper for bambu_to_prusa_xml.

This module maintains backward compatibility with the old XML-based entry point.
The actual CLI implementation has been moved to frontends.cli.
"""

import logging
from pathlib import Path

from bambu_to_prusa.converter import BambuToPrusaConverter


def convert_file(input_path: str, output_path: str) -> str:
    """Convert a Bambu 3mf file to a Prusa 3mf file.
    
    Args:
        input_path: Path to input Bambu 3mf file
        output_path: Path to output Prusa 3mf file
        
    Returns:
        Path to the output file
    """
    converter = BambuToPrusaConverter()
    return converter.convert_archive(input_path, output_path)


def main():
    """Main entrypoint for XML-based workflow.
    
    Note: This is a legacy entry point. Use the CLI module for better functionality.
    """
    input_path = Path("input.3mf")
    output_path = Path("output.3mf")
    converter = BambuToPrusaConverter()
    converter.convert_archive(str(input_path), str(output_path))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
