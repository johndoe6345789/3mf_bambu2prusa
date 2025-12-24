"""Backward compatibility wrapper for bambu_to_prusa_gui.

This module maintains backward compatibility with the old entry point.
The actual implementation has been moved to frontends.tkinter.
"""

from frontends.tkinter import main

# Re-export main for backward compatibility
__all__ = ["main"]


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    main()
