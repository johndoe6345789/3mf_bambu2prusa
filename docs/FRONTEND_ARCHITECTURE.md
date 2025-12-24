# Frontend Architecture

## Overview

The Bambu2Prusa project has been split into two main domains:

1. **Backend** - Core conversion logic in `bambu_to_prusa/` package
2. **Frontend** - Modular user interfaces in `frontends/` package

## Backend Domain

The backend is located in the `bambu_to_prusa/` package and contains:

- `converter.py` - Main conversion orchestration
- `model_processing.py` - Model file processing and transformation
- `model_injection.py` - Prusa model building
- `package_builder.py` - 3MF package assembly
- `file_ops.py` - File operations (zip/unzip)
- `settings.py` - User settings management
- `cloud_storage.py` - Cloud storage detection
- `theme_engine.py` - UI theming support
- `template_paths.py` - Template file path management

All backend modules are UI-agnostic and can be used by any frontend.

## Frontend Domain

The frontend is organized into modular implementations in the `frontends/` package:

### Directory Structure

```
frontends/
├── __init__.py
├── common/          # Shared utilities across all frontends
│   ├── __init__.py
│   └── helpers.py   # Common helper functions
├── cli/             # Command-line interface
│   ├── __init__.py
│   └── main.py
├── tkinter/         # Tkinter GUI (default)
│   ├── __init__.py
│   └── main.py
└── pyqt6/           # PyQt6 GUI (optional)
    ├── __init__.py
    └── main.py
```

### CLI Frontend (`frontends/cli/`)

A command-line interface for batch processing and scripting.

**Features:**
- Argument parsing with `argparse`
- File validation
- Verbose logging option
- Clear error messages

**Usage:**
```bash
bambu2prusa-cli input.3mf output.3mf
bambu2prusa-cli --verbose input.3mf output.3mf
```

### Tkinter Frontend (`frontends/tkinter/`)

The default GUI implementation using Tkinter (Python's standard GUI library).

**Features:**
- Theme support with plugin system
- File dialogs for input/output selection
- Settings management
- SVG rendering for custom graphics
- Persistent directory preferences

**Usage:**
```bash
bambu2prusa              # Default entry point
bambu2prusa-tkinter      # Explicit entry point
```

### PyQt6 Frontend (`frontends/pyqt6/`)

An optional GUI implementation using PyQt6 for a more modern look.

**Features:**
- Modern Qt-based interface
- Native file dialogs
- Better cross-platform support
- Responsive UI

**Installation:**
```bash
pip install bambu2prusa[pyqt6]
```

**Usage:**
```bash
bambu2prusa-pyqt6
```

### Common Utilities (`frontends/common/`)

Shared utilities that are used across multiple frontends:

- `first_existing_dir()` - Find the first existing directory from a list of paths

## Entry Points

The package defines the following console scripts in `pyproject.toml`:

- `bambu2prusa` - Default entry point (launches Tkinter GUI)
- `bambu2prusa-cli` - Command-line interface
- `bambu2prusa-tkinter` - Tkinter GUI (explicit)
- `bambu2prusa-pyqt6` - PyQt6 GUI (requires PyQt6)

## Backward Compatibility

The following modules maintain backward compatibility:

- `bambu_to_prusa_gui.py` - Wrapper that redirects to `frontends.tkinter`
- `bambu_to_prusa_xml.py` - Legacy XML-based workflow

These wrappers allow existing code that imports from the old locations to continue working.

## Adding a New Frontend

To add a new frontend implementation:

1. Create a new directory under `frontends/` (e.g., `frontends/myui/`)
2. Create `__init__.py` and `main.py` in the new directory
3. Implement a `main()` function in `main.py` that:
   - Imports `BambuToPrusaConverter` from `bambu_to_prusa.converter`
   - Implements the UI logic
   - Calls `converter.convert_archive(input_file, output_file)`
4. Add an entry point in `pyproject.toml`:
   ```toml
   bambu2prusa-myui = "frontends.myui:main"
   ```
5. Optionally add dependencies in `[project.optional-dependencies]`

Example minimal frontend:

```python
# frontends/myui/main.py
from bambu_to_prusa.converter import BambuToPrusaConverter

def main():
    converter = BambuToPrusaConverter()
    # Your UI code here
    converter.convert_archive(input_file, output_file)
```

## Testing

Tests are organized by module:

- `tests/test_cli.py` - CLI frontend tests
- `tests/test_gui_helpers.py` - Common frontend helper tests
- `tests/test_converter.py` - Backend converter tests
- `tests/test_settings.py` - Settings management tests

Run all tests:
```bash
python3 -m pytest tests/
```

Run specific frontend tests:
```bash
python3 -m pytest tests/test_cli.py -v
```

## Design Principles

1. **Separation of Concerns**: Backend logic is completely separate from UI
2. **Modularity**: Each frontend is self-contained and independent
3. **Reusability**: Common utilities are shared via `frontends.common`
4. **Extensibility**: New frontends can be added without modifying existing code
5. **Backward Compatibility**: Old import paths continue to work via wrapper modules
