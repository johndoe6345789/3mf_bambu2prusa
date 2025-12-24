"""PyQt6 GUI implementation for Bambu2Prusa converter.

This is a basic implementation that provides a minimal PyQt6 interface.
It demonstrates the modular frontend architecture.
"""

import logging
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from PyQt6.QtWidgets import (
        QApplication,
        QComboBox,
        QDialog,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPainter, QColor
    from PyQt6.QtSvgWidgets import QSvgWidget
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # Define placeholder classes to avoid NameError during import
    QDialog = object
    QMainWindow = object


from bambu_to_prusa.converter import BambuToPrusaConverter
from bambu_to_prusa.settings import SettingsManager
from bambu_to_prusa.theme_engine import Theme, ThemeEngine
from frontends.common.helpers import first_existing_dir


class SettingsDialog(QDialog):
    """Settings dialog for configuring default directories."""

    def __init__(self, parent, settings, theme):
        super().__init__(parent)
        self.settings = settings
        self.theme = theme
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.init_ui()

    def init_ui(self):
        """Initialize the settings dialog UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Input directory row
        input_layout = QHBoxLayout()
        input_label = QLabel("Default input directory:")
        input_label.setStyleSheet(f"color: {self.theme['text']};")
        self.input_dir_edit = QLineEdit(self.settings.last_input_dir)
        self.input_dir_edit.setStyleSheet(
            f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
            f"border: 1px solid {self.theme['panel_outline']}; padding: 5px;"
        )
        input_browse_btn = QPushButton("Browse")
        input_browse_btn.setStyleSheet(
            f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
            f"border: none; padding: 8px 16px;"
        )
        input_browse_btn.clicked.connect(self.choose_input_dir)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_dir_edit)
        input_layout.addWidget(input_browse_btn)
        layout.addLayout(input_layout)

        # Output directory row
        output_layout = QHBoxLayout()
        output_label = QLabel("Default output directory:")
        output_label.setStyleSheet(f"color: {self.theme['text']};")
        self.output_dir_edit = QLineEdit(self.settings.last_output_dir)
        self.output_dir_edit.setStyleSheet(
            f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
            f"border: 1px solid {self.theme['panel_outline']}; padding: 5px;"
        )
        output_browse_btn = QPushButton("Browse")
        output_browse_btn.setStyleSheet(
            f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
            f"border: none; padding: 8px 16px;"
        )
        output_browse_btn.clicked.connect(self.choose_output_dir)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(output_browse_btn)
        layout.addLayout(output_layout)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            f"background-color: {self.theme['accent']}; color: white; "
            f"border: none; padding: 10px; margin-top: 10px; font-weight: bold;"
        )
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def choose_input_dir(self):
        """Open directory dialog for input directory."""
        initial_dir = first_existing_dir(self.input_dir_edit.text()) or str(Path.home())
        directory = QFileDialog.getExistingDirectory(self, "Select Input Directory", initial_dir)
        if directory:
            self.input_dir_edit.setText(directory)

    def choose_output_dir(self):
        """Open directory dialog for output directory."""
        initial_dir = first_existing_dir(self.output_dir_edit.text()) or str(Path.home())
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", initial_dir)
        if directory:
            self.output_dir_edit.setText(directory)

    def save_settings(self):
        """Save settings and close dialog."""
        self.settings.update_last_input_dir(self.input_dir_edit.text())
        self.settings.update_last_output_dir(self.output_dir_edit.text())
        self.accept()


class BambuToPrusaWindow(QMainWindow):
    """Main window for PyQt6 GUI."""

    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.converter = BambuToPrusaConverter()
        self.input_file = ""
        self.output_file = ""

        # Initialize ThemeEngine
        self.theme_engine = ThemeEngine(
            base_theme=Theme(
                name="Discord + Steam",
                description="Blend of Discord blurple and Steam blues.",
                palette={
                    "bg": "#1e2127",
                    "panel": "#242833",
                    "panel_outline": "#2e3442",
                    "text": "#e9eef7",
                    "muted": "#a6b3c6",
                    "accent": "#5865f2",  # Discord-inspired blurple
                    "accent_alt": "#66c0f4",  # Steam-inspired blue
                    "warning": "#fcbf49",
                },
            ),
            plugin_dirs=[
                Path(__file__).resolve().parent.parent.parent / "bambu_to_prusa" / "theme_plugins",
                Path.home() / ".bambu2prusa" / "themes",
            ],
        )
        self.current_theme_name = self.theme_engine.base_theme.name
        self.theme = self.theme_engine.palette_for(self.current_theme_name)

        self.settings_dialog = None
        
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Bambu2Prusa Converter (PyQt6)")
        self.setMinimumSize(520, 650)
        
        # Apply theme to window
        self.setStyleSheet(f"background-color: {self.theme['bg']};")
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Hero panel with SVG badge
        self.hero_panel = QWidget()
        self.hero_panel.setStyleSheet(
            f"background-color: {self.theme['panel']}; "
            f"border: 1px solid {self.theme['panel_outline']};"
        )
        hero_layout = QVBoxLayout()
        self.hero_panel.setLayout(hero_layout)
        hero_layout.setContentsMargins(12, 12, 12, 12)
        
        # SVG Badge
        svg_path = Path(__file__).resolve().parent.parent.parent / "bambu_to_prusa" / "assets" / "bambu2prusa_badge.svg"
        if svg_path.exists():
            self.svg_widget = QSvgWidget(str(svg_path))
            self.svg_widget.setFixedHeight(150)
            hero_layout.addWidget(self.svg_widget)
        
        # Title
        self.title = QLabel("Bambu ➜ Prusa Converter")
        self.title.setStyleSheet(
            f"font-size: 15pt; font-weight: bold; color: {self.theme['text']}; "
            f"background-color: transparent; margin-top: 5px;"
        )
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hero_layout.addWidget(self.title)
        
        # Subtitle
        self.subtitle = QLabel("Theming-ready UI with plugin-friendly palettes.")
        self.subtitle.setStyleSheet(
            f"font-size: 10pt; color: {self.theme['muted']}; "
            f"background-color: transparent; margin-bottom: 5px;"
        )
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hero_layout.addWidget(self.subtitle)
        
        layout.addWidget(self.hero_panel)
        
        # Theme selector row
        theme_row = QWidget()
        theme_row.setStyleSheet(f"background-color: transparent;")
        theme_layout = QHBoxLayout()
        theme_row.setLayout(theme_layout)
        theme_layout.setContentsMargins(0, 8, 0, 8)
        
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet(f"color: {self.theme['text']}; background-color: transparent;")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.theme_engine.available_themes())
        self.theme_combo.setCurrentText(self.current_theme_name)
        self.theme_combo.setStyleSheet(
            f"QComboBox {{ "
            f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
            f"border: 1px solid {self.theme['panel_outline']}; padding: 5px; "
            f"}} "
            f"QComboBox::drop-down {{ border: none; }} "
            f"QComboBox QAbstractItemView {{ "
            f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
            f"selection-background-color: {self.theme['panel_outline']}; "
            f"}}"
        )
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        layout.addWidget(theme_row)
        
        # Label
        label = QLabel("Select input and output 3mf files.")
        label.setStyleSheet(f"color: {self.theme['text']}; background-color: transparent; margin-top: 8px;")
        layout.addWidget(label)
        
        # Input file button
        self.input_button = self._create_button("Select Input Bambu 3mf", self.select_input, primary=True)
        layout.addWidget(self.input_button)
        
        # Input file label
        self.input_label = QLabel("No input file selected")
        self.input_label.setStyleSheet(f"color: {self.theme['muted']}; background-color: transparent; margin: 5px;")
        layout.addWidget(self.input_label)
        
        # Output file button
        self.output_button = self._create_button("Select Output Prusa 3mf", self.select_output)
        layout.addWidget(self.output_button)
        
        # Output file label
        self.output_label = QLabel("No output file selected")
        self.output_label.setStyleSheet(f"color: {self.theme['muted']}; background-color: transparent; margin: 5px;")
        layout.addWidget(self.output_label)
        
        # Convert button
        self.convert_button = self._create_button("Process", self.convert, primary=True)
        self.convert_button.setMinimumHeight(50)
        self.convert_button.setStyleSheet(
            f"background-color: {self.theme['accent']}; color: white; "
            f"border: none; padding: 10px; font-weight: bold; margin-top: 10px;"
        )
        layout.addWidget(self.convert_button)
        
        # Settings button
        self.settings_button = self._create_button("Settings", self.open_settings_dialog)
        layout.addWidget(self.settings_button)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            f"color: {self.theme['muted']}; background-color: transparent; "
            f"margin: 10px; padding: 10px;"
        )
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        layout.addStretch()

    def _create_button(self, text, callback, primary=False):
        """Create a styled button."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setMinimumHeight(40)
        
        if primary:
            button.setStyleSheet(
                f"background-color: {self.theme['accent']}; color: white; "
                f"border: none; padding: 10px; font-weight: bold;"
            )
        else:
            button.setStyleSheet(
                f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
                f"border: none; padding: 10px;"
            )
        
        button.setProperty("primary", primary)
        return button

    def on_theme_changed(self, theme_name):
        """Handle theme selection change."""
        self.current_theme_name = theme_name
        self.theme = self.theme_engine.palette_for(theme_name)
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to all UI elements."""
        # Window background
        self.setStyleSheet(f"background-color: {self.theme['bg']};")
        
        # Hero panel
        self.hero_panel.setStyleSheet(
            f"background-color: {self.theme['panel']}; "
            f"border: 1px solid {self.theme['panel_outline']};"
        )
        
        # Title and subtitle
        self.title.setStyleSheet(
            f"font-size: 15pt; font-weight: bold; color: {self.theme['text']}; "
            f"background-color: transparent; margin-top: 5px;"
        )
        self.subtitle.setStyleSheet(
            f"font-size: 10pt; color: {self.theme['muted']}; "
            f"background-color: transparent; margin-bottom: 5px;"
        )
        
        # Theme combo
        self.theme_combo.setStyleSheet(
            f"QComboBox {{ "
            f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
            f"border: 1px solid {self.theme['panel_outline']}; padding: 5px; "
            f"}} "
            f"QComboBox::drop-down {{ border: none; }} "
            f"QComboBox QAbstractItemView {{ "
            f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
            f"selection-background-color: {self.theme['panel_outline']}; "
            f"}}"
        )
        
        # Labels
        for label in [self.input_label, self.output_label]:
            label.setStyleSheet(f"color: {self.theme['muted']}; background-color: transparent; margin: 5px;")
        
        self.status_label.setStyleSheet(
            f"color: {self.theme['muted']}; background-color: transparent; "
            f"margin: 10px; padding: 10px;"
        )
        
        # Buttons
        for button in [self.input_button, self.output_button, self.convert_button, self.settings_button]:
            is_primary = button.property("primary")
            if is_primary:
                button.setStyleSheet(
                    f"background-color: {self.theme['accent']}; color: white; "
                    f"border: none; padding: 10px; font-weight: bold;"
                )
            else:
                button.setStyleSheet(
                    f"background-color: {self.theme['panel']}; color: {self.theme['text']}; "
                    f"border: none; padding: 10px;"
                )

    def open_settings_dialog(self):
        """Open the settings dialog."""
        if self.settings_dialog and self.settings_dialog.isVisible():
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            return
        
        self.settings_dialog = SettingsDialog(self, self.settings, self.theme)
        self.settings_dialog.setStyleSheet(f"background-color: {self.theme['bg']};")
        self.settings_dialog.exec()

    def select_input(self):
        """Open file dialog to select input file."""
        initial_dir = first_existing_dir(self.settings.last_input_dir) or str(Path.home())
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input Bambu 3mf File",
            initial_dir,
            "3MF Files (*.3mf);;All Files (*)"
        )
        
        if file_path:
            self.input_file = file_path
            self.input_label.setText(f"Input: {Path(file_path).name}")
            self.input_label.setStyleSheet(f"color: {self.theme['text']}; background-color: transparent; margin: 5px;")
            self.settings.update_last_input_dir(str(Path(file_path).parent))
            self.status_label.setText(f"Input file selected: {Path(file_path).name}")
            self.status_label.setStyleSheet(f"color: {self.theme['text']}; background-color: transparent; margin: 10px; padding: 10px;")
        else:
            self.status_label.setText("Input selection canceled.")
            self.status_label.setStyleSheet(f"color: {self.theme['warning']}; background-color: transparent; margin: 10px; padding: 10px;")

    def select_output(self):
        """Open file dialog to select output file."""
        initial_dir = first_existing_dir(
            self.settings.last_output_dir,
            self.settings.last_input_dir,
        ) or str(Path.home())
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output Prusa 3mf File",
            initial_dir,
            "3MF Files (*.3mf);;All Files (*)"
        )
        
        if file_path:
            # Ensure .3mf extension
            if not file_path.lower().endswith('.3mf'):
                file_path += '.3mf'
            
            self.output_file = file_path
            self.output_label.setText(f"Output: {Path(file_path).name}")
            self.output_label.setStyleSheet(f"color: {self.theme['text']}; background-color: transparent; margin: 5px;")
            self.settings.update_last_output_dir(str(Path(file_path).parent))
            self.status_label.setText(f"Output file selected: {Path(file_path).name}")
            self.status_label.setStyleSheet(f"color: {self.theme['text']}; background-color: transparent; margin: 10px; padding: 10px;")
        else:
            self.status_label.setText("Output selection canceled.")
            self.status_label.setStyleSheet(f"color: {self.theme['warning']}; background-color: transparent; margin: 10px; padding: 10px;")

    def convert(self):
        """Perform the conversion."""
        if not self.input_file:
            QMessageBox.warning(self, "No Input File", "Please select an input file.")
            self.status_label.setText("Please provide both input and output files.")
            self.status_label.setStyleSheet(f"color: {self.theme['warning']}; background-color: transparent; margin: 10px; padding: 10px;")
            return
        
        if not self.output_file:
            QMessageBox.warning(self, "No Output File", "Please select an output file.")
            self.status_label.setText("Please provide both input and output files.")
            self.status_label.setStyleSheet(f"color: {self.theme['warning']}; background-color: transparent; margin: 10px; padding: 10px;")
            return
        
        try:
            self.status_label.setText("Converting...")
            self.status_label.setStyleSheet(f"color: {self.theme['text']}; background-color: transparent; margin: 10px; padding: 10px;")
            self.convert_button.setEnabled(False)
            QApplication.processEvents()  # Update UI
            
            self.converter.convert_archive(self.input_file, self.output_file)
            
            self.status_label.setText(f"Output file created: {Path(self.output_file).name}")
            self.status_label.setStyleSheet(f"color: {self.theme['text']}; background-color: transparent; margin: 10px; padding: 10px;")
            QMessageBox.information(
                self,
                "Success",
                f"File converted successfully!\n\nOutput: {self.output_file}"
            )
        except Exception as exc:
            logging.error("Conversion failed: %s", exc)
            self.status_label.setText(f"Error: {exc}")
            self.status_label.setStyleSheet(f"color: #ff6b6b; background-color: transparent; margin: 10px; padding: 10px;")
            QMessageBox.critical(
                self,
                "Conversion Failed",
                f"An error occurred during conversion:\n\n{exc}"
            )
        finally:
            self.convert_button.setEnabled(True)


def main():
    """Main entrypoint for PyQt6 GUI."""
    if not PYQT6_AVAILABLE:
        print("Error: PyQt6 is not installed.", file=sys.stderr)
        print("Install it with: pip install PyQt6", file=sys.stderr)
        sys.exit(1)
    
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    window = BambuToPrusaWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
