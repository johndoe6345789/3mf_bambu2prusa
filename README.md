# 3mf_bambu2prusa
This application converts Bambu Studio 3mf files (including painted/colored models) into PrusaSlicer-compatible 3mf files. The project was built by reverse-engineering 3mf archives rather than relying on an official specification.

## Setup
Run the helper script to create a virtual environment and install dependencies:

```
python scripts/setup.py
```

## Launch the GUI
Use the launcher to start the converter interface. If a `.venv` folder exists it will be activated automatically, and on macOS the Homebrew-installed Python is preferred when available.

```
python scripts/launch_gui.py
```

Alternatively, you can run the Python entrypoint directly:

```
python bambu_to_prusa_gui.py
```

An experimental XML-based workflow remains available in `bambu_to_prusa_xml.py`.
