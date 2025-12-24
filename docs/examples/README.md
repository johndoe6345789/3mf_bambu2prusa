# Examples

This directory contains example code showing how to use the Bambu2Prusa converter in different ways.

## Programmatic Usage (`programmatic_usage.py`)

Shows how to use the backend converter directly in your Python code:

- Simple conversion
- Conversion with error handling
- Batch conversion of multiple files

Run it:
```bash
python docs/examples/programmatic_usage.py
```

## Creating a Custom Frontend

To create a custom frontend, see the `FRONTEND_ARCHITECTURE.md` document in the parent directory.

The basic pattern is:

```python
from bambu_to_prusa.converter import BambuToPrusaConverter

def main():
    converter = BambuToPrusaConverter()
    # Your UI code to get input_file and output_file
    converter.convert_archive(input_file, output_file)
```

All frontends should be placed in the `frontends/` directory and registered as entry points in `pyproject.toml`.
