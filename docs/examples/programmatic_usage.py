"""
Example: Using the backend converter programmatically
"""

from pathlib import Path
from bambu_to_prusa.converter import BambuToPrusaConverter


def simple_conversion():
    """Simple conversion example."""
    converter = BambuToPrusaConverter()
    converter.convert_archive("input.3mf", "output.3mf")
    print("Conversion complete!")


def conversion_with_error_handling():
    """Conversion with proper error handling."""
    converter = BambuToPrusaConverter()
    
    input_file = Path("input.3mf")
    output_file = Path("output.3mf")
    
    try:
        if not input_file.exists():
            print(f"Error: Input file not found: {input_file}")
            return
        
        print(f"Converting {input_file} to {output_file}...")
        converter.convert_archive(str(input_file), str(output_file))
        print(f"Success! Created {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def batch_conversion():
    """Convert multiple files in a directory."""
    converter = BambuToPrusaConverter()
    
    input_dir = Path("input_files")
    output_dir = Path("output_files")
    output_dir.mkdir(exist_ok=True)
    
    for input_file in input_dir.glob("*.3mf"):
        output_file = output_dir / input_file.name
        print(f"Converting {input_file.name}...")
        
        try:
            converter.convert_archive(str(input_file), str(output_file))
            print(f"  ✓ Created {output_file.name}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")


if __name__ == "__main__":
    # Run the example you want
    simple_conversion()
    # conversion_with_error_handling()
    # batch_conversion()
