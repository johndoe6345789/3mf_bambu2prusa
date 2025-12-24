# Project Structure Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │   CLI    │  │ Tkinter  │  │  PyQt6   │  │ Custom │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘ │
│       │             │              │            │       │
└───────┼─────────────┼──────────────┼────────────┼───────┘
        │             │              │            │
        └─────────────┴──────────────┴────────────┘
                      │
        ┌─────────────▼──────────────────┐
        │   Common Frontend Utilities    │
        │  (first_existing_dir, etc.)    │
        └─────────────┬──────────────────┘
                      │
        ┌─────────────▼──────────────────┐
        │       Backend/Core Logic       │
        │                                 │
        │  ┌──────────────────────────┐  │
        │  │  BambuToPrusaConverter   │  │
        │  └────────┬─────────────────┘  │
        │           │                     │
        │  ┌────────▼─────────────────┐  │
        │  │  Model Processing        │  │
        │  │  - Read Bambu models     │  │
        │  │  - Transform data        │  │
        │  │  - Build Prusa models    │  │
        │  └────────┬─────────────────┘  │
        │           │                     │
        │  ┌────────▼─────────────────┐  │
        │  │  Package Builder         │  │
        │  │  - Assemble 3MF archive  │  │
        │  │  - Write output file     │  │
        │  └──────────────────────────┘  │
        │                                 │
        └─────────────────────────────────┘
```

## Directory Structure

```
3mf_bambu2prusa/
│
├── frontends/                    # Frontend Domain
│   ├── __init__.py
│   │
│   ├── cli/                      # Command-line Interface
│   │   ├── __init__.py
│   │   └── main.py               # CLI implementation
│   │
│   ├── tkinter/                  # Tkinter GUI
│   │   ├── __init__.py
│   │   └── main.py               # GUI implementation
│   │
│   ├── pyqt6/                    # PyQt6 GUI
│   │   ├── __init__.py
│   │   └── main.py               # PyQt6 implementation
│   │
│   └── common/                   # Shared Utilities
│       ├── __init__.py
│       └── helpers.py            # Common helper functions
│
├── bambu_to_prusa/              # Backend Domain
│   ├── __init__.py
│   ├── converter.py             # Main converter class
│   ├── model_processing.py      # Model transformation
│   ├── model_injection.py       # Prusa model building
│   ├── package_builder.py       # 3MF package assembly
│   ├── file_ops.py              # File operations
│   ├── settings.py              # Settings management
│   ├── cloud_storage.py         # Cloud storage detection
│   ├── theme_engine.py          # UI theming support
│   ├── template_paths.py        # Template management
│   │
│   ├── assets/                  # Static assets
│   │   └── bambu2prusa_badge.svg
│   │
│   ├── data/                    # Template data
│   │   └── 3mf_template/
│   │
│   └── theme_plugins/           # Theme plugins
│       └── retro_terminal.py
│
├── tests/                       # Test Suite
│   ├── test_cli.py              # CLI tests
│   ├── test_gui_helpers.py      # Frontend helper tests
│   ├── test_converter.py        # Backend tests
│   ├── test_settings.py         # Settings tests
│   └── ...
│
├── docs/                        # Documentation
│   ├── FRONTEND_ARCHITECTURE.md # Architecture guide
│   ├── MIGRATION.md             # Migration guide
│   ├── STRUCTURE.md             # This file
│   └── examples/                # Usage examples
│       ├── README.md
│       └── programmatic_usage.py
│
├── scripts/                     # Helper scripts
│   ├── setup.py
│   └── launch_gui.py
│
├── bambu_to_prusa_gui.py       # Backward compat wrapper
├── bambu_to_prusa_xml.py       # Backward compat wrapper
├── pyproject.toml              # Project configuration
├── README.md                   # Main readme
└── requirements.txt            # Dependencies
```

## Data Flow

### GUI Workflow
```
User
  │
  ▼
┌─────────────────┐
│   GUI Frontend  │  (Tkinter/PyQt6)
│   - File select │
│   - Settings    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Converter    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Input: Bambu   │
│  .3mf file      │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Extract  │
    │ & Parse  │
    └────┬─────┘
         │
    ┌────▼──────┐
    │ Transform │
    │ Models    │
    └────┬──────┘
         │
    ┌────▼──────┐
    │  Build    │
    │  Prusa    │
    │  Package  │
    └────┬──────┘
         │
         ▼
┌─────────────────┐
│  Output: Prusa  │
│  .3mf file      │
└─────────────────┘
```

### CLI Workflow
```
Command Line Arguments
  │
  ▼
┌─────────────────┐
│   CLI Parser    │
│   - Validate    │
│   - Parse args  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Converter     │  (Same backend as GUI)
└────────┬────────┘
         │
         ▼
     (Same flow as GUI)
```

## Module Dependencies

```
frontends/cli/
  └─> bambu_to_prusa.converter
  └─> frontends.common

frontends/tkinter/
  └─> bambu_to_prusa.converter
  └─> bambu_to_prusa.settings
  └─> bambu_to_prusa.cloud_storage
  └─> bambu_to_prusa.theme_engine
  └─> frontends.common

frontends/pyqt6/
  └─> bambu_to_prusa.converter
  └─> bambu_to_prusa.settings
  └─> frontends.common

bambu_to_prusa.converter
  └─> bambu_to_prusa.file_ops
  └─> bambu_to_prusa.model_processing
  └─> bambu_to_prusa.model_injection
  └─> bambu_to_prusa.package_builder
  └─> bambu_to_prusa.template_paths
```

## Design Principles

1. **Loose Coupling**: Frontends depend on backend, but backend doesn't know about frontends
2. **Single Responsibility**: Each module has one clear purpose
3. **Open/Closed**: Easy to add new frontends without modifying existing code
4. **DRY**: Common utilities in `frontends/common/` prevent duplication
5. **Testability**: Each layer can be tested independently
