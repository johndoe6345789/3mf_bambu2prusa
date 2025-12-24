# Migration Summary: Frontend/Backend Split

## Overview

This document summarizes the changes made to split the Bambu2Prusa project into modular frontend and backend domains.

## What Changed

### New Directory Structure

```
3mf_bambu2prusa/
├── bambu_to_prusa/          # Backend (unchanged location)
│   ├── converter.py
│   ├── model_processing.py
│   ├── settings.py
│   └── ...
├── frontends/               # NEW: Modular frontends
│   ├── cli/                 # NEW: Command-line interface
│   ├── tkinter/             # Refactored from bambu_to_prusa_gui.py
│   ├── pyqt6/               # NEW: PyQt6 GUI
│   └── common/              # NEW: Shared utilities
├── bambu_to_prusa_gui.py    # Now a compatibility wrapper
├── bambu_to_prusa_xml.py    # Now a compatibility wrapper
└── docs/
    ├── FRONTEND_ARCHITECTURE.md  # NEW: Architecture docs
    └── examples/                 # NEW: Usage examples
```

### Entry Points Updated

The following command-line entry points are now available:

| Command | Description | Location |
|---------|-------------|----------|
| `bambu2prusa` | Default GUI (Tkinter) | `frontends.tkinter:main` |
| `bambu2prusa-cli` | Command-line interface | `frontends.cli:main` |
| `bambu2prusa-tkinter` | Tkinter GUI (explicit) | `frontends.tkinter:main` |
| `bambu2prusa-pyqt6` | PyQt6 GUI | `frontends.pyqt6:main` |

### Code Moved

1. **`bambu_to_prusa_gui.py`** → `frontends/tkinter/main.py`
   - Full Tkinter GUI implementation
   - Original file is now a compatibility wrapper

2. **Helper function** → `frontends/common/helpers.py`
   - `_first_existing_dir()` → `first_existing_dir()`
   - Now shared across all frontends

3. **XML-based workflow** → `frontends/cli/main.py`
   - Upgraded to full CLI with argparse
   - Original `bambu_to_prusa_xml.py` is now a compatibility wrapper

### New Additions

1. **`frontends/cli/`** - Full-featured command-line interface
   - Argument parsing
   - File validation
   - Verbose logging option

2. **`frontends/pyqt6/`** - Modern PyQt6 GUI
   - Native Qt widgets
   - Better cross-platform support
   - Optional dependency

3. **`frontends/common/`** - Shared utilities
   - Common helper functions
   - Reusable across all frontends

4. **Documentation**
   - `docs/FRONTEND_ARCHITECTURE.md` - Complete architecture guide
   - `docs/examples/` - Usage examples

## Backward Compatibility

All existing code continues to work:

```python
# These still work (compatibility wrappers)
from bambu_to_prusa_gui import main
from bambu_to_prusa_xml import convert_file

# Backend usage unchanged
from bambu_to_prusa.converter import BambuToPrusaConverter
```

## Benefits

1. **Separation of Concerns**: UI code separated from business logic
2. **Modularity**: Each frontend is independent and self-contained
3. **Extensibility**: Easy to add new frontends (e.g., web, mobile)
4. **Maintainability**: Changes to one frontend don't affect others
5. **Testability**: Frontend and backend can be tested separately

## Migration for Developers

### If you were using the backend directly:
No changes needed! The backend API remains the same.

```python
from bambu_to_prusa.converter import BambuToPrusaConverter
converter = BambuToPrusaConverter()
converter.convert_archive(input_file, output_file)
```

### If you were importing GUI code:
Update imports to use the new locations:

```python
# Old
from bambu_to_prusa_gui import _first_existing_dir

# New
from frontends.common import first_existing_dir
```

Or continue using the compatibility wrappers (not recommended for new code).

### If you were extending the GUI:
Place custom frontends in the `frontends/` directory:

```python
# frontends/myfrontend/main.py
from bambu_to_prusa.converter import BambuToPrusaConverter

def main():
    converter = BambuToPrusaConverter()
    # Your UI code here
    converter.convert_archive(input_file, output_file)
```

Then add an entry point in `pyproject.toml`:

```toml
[project.scripts]
bambu2prusa-myfrontend = "frontends.myfrontend:main"
```

## Testing

All tests have been updated and pass:

- `tests/test_cli.py` - CLI frontend tests (new)
- `tests/test_gui_helpers.py` - Common utilities tests (updated)
- All existing backend tests continue to pass

Run tests:
```bash
python3 -m pytest tests/ -v
```

## Installation

No changes to installation process:

```bash
# Standard installation
pip install .

# With PyQt6 support
pip install .[pyqt6]

# Development installation
pip install -e .[dev]
```

## Summary

This refactoring modernizes the codebase by:
- Clearly separating frontend and backend concerns
- Making it easy to add new interfaces
- Improving code organization and maintainability
- Maintaining full backward compatibility

The backend (`bambu_to_prusa/`) remains stable and unchanged, while the frontend is now modular and extensible.
