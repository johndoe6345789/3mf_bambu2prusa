import logging
import os
from pathlib import Path
from tkinter import Button, Canvas, Frame, Label, OptionMenu, PhotoImage, StringVar, Tk, filedialog
from xml.etree import ElementTree as ET

from bambu_to_prusa.cloud_storage import detect_cloud_storage_root
from bambu_to_prusa.converter import BambuToPrusaConverter
from bambu_to_prusa.theme_engine import Theme, ThemeEngine


# Base64-encoded PNG for the Tk window icon so we avoid shipping a binary asset file.
ICON_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABYElEQVR42u3ZR04DQRCF4TkJxjPj"
    "scnpJGQkHDkB8YDkjHM26STFk9Vbb8pCtKi3+KXa9OJ92w5m0lmxXEAAAhCAAMYBcmI5AhAgxGE4"
    "AqTCObEcAQhAAP3jzcMRGqKBbOX7qOfqoo5sF9qo5WrKTrGB6qjmqspu6Q29ul5kr/yMntCj60H2K"
    "/foDt2OOzi6QdfoCl2OmwJgXrT5BaDbQIBUhEOZVwDKDQQwDzAbLYi2SQD542/0JYWTT/Thepfi6Q"
    "gN0cDVl9JZD3VdHSmft1ELNV0NqVzUUQ1VJwJoNxCAAAQggHGAeFG0eQWg3EAAAhDAOEA6XhJtPgFo"
    "NxCAAOYBMjiUeQWg3ACAZdHmF4BuAwEIQADjAGFmRbT5BKDdQIDfAPiLfwE9QIJDmVcAyg0EIECyKt"
    "r8AtBtIMA0AP8hApgHiJI1sVwQZXEYjgAEIMC6WI4ABCCAcYA4tyGW+wGhGmxpm/m3HwAAAABJRU5ErkJggg=="
)


def _parse_dimension(raw, default):
    if raw is None:
        return default
    try:
        cleaned = str(raw).replace("px", "").strip()
        return float(cleaned)
    except ValueError:
        return default


def render_svg_on_canvas(canvas: Canvas, svg_path: Path, x_offset: float = 0, y_offset: float = 0):
    """Render a limited subset of SVG elements onto a Tkinter canvas."""

    tree = ET.parse(svg_path)
    root = tree.getroot()
    width = _parse_dimension(root.attrib.get("width"), 360)
    height = _parse_dimension(root.attrib.get("height"), 140)
    canvas.configure(width=width, height=height)

    def color(value, fallback="#ffffff"):
        return value if value and value.lower() != "none" else fallback

    for elem in root:
        tag = elem.tag.split("}")[-1]
        fill = color(elem.attrib.get("fill"), "")
        outline = color(elem.attrib.get("stroke"), "")
        if tag == "rect":
            x = _parse_dimension(elem.attrib.get("x"), 0) + x_offset
            y = _parse_dimension(elem.attrib.get("y"), 0) + y_offset
            w = _parse_dimension(elem.attrib.get("width"), width)
            h = _parse_dimension(elem.attrib.get("height"), height)
            canvas.create_rectangle(x, y, x + w, y + h, fill=fill, outline=outline, width=float(elem.attrib.get("stroke-width", 0) or 0))
        elif tag == "circle":
            cx = _parse_dimension(elem.attrib.get("cx"), 0) + x_offset
            cy = _parse_dimension(elem.attrib.get("cy"), 0) + y_offset
            r = _parse_dimension(elem.attrib.get("r"), 0)
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=fill, outline=outline, width=float(elem.attrib.get("stroke-width", 0) or 0))
        elif tag in {"polygon", "polyline"}:
            points = []
            for pair in elem.attrib.get("points", "").split():
                if "," in pair:
                    px, py = pair.split(",", maxsplit=1)
                else:
                    coords = pair.split()
                    if len(coords) != 2:
                        continue
                    px, py = coords
                points.extend([
                    _parse_dimension(px, 0) + x_offset,
                    _parse_dimension(py, 0) + y_offset,
                ])
            if points:
                canvas.create_polygon(points, fill=fill, outline=outline if tag == "polygon" else outline or fill, smooth=tag == "polyline")
        elif tag == "line":
            x1 = _parse_dimension(elem.attrib.get("x1"), 0) + x_offset
            y1 = _parse_dimension(elem.attrib.get("y1"), 0) + y_offset
            x2 = _parse_dimension(elem.attrib.get("x2"), 0) + x_offset
            y2 = _parse_dimension(elem.attrib.get("y2"), 0) + y_offset
            canvas.create_line(x1, y1, x2, y2, fill=outline or fill, width=float(elem.attrib.get("stroke-width", 2) or 2))
        elif tag == "text":
            x = _parse_dimension(elem.attrib.get("x"), 0) + x_offset
            y = _parse_dimension(elem.attrib.get("y"), 0) + y_offset
            anchor_map = {"middle": "center", "end": "e"}
            anchor = anchor_map.get(elem.attrib.get("text-anchor", ""), "w")
            content = (elem.text or "").strip()
            size = int(float(elem.attrib.get("font-size", 12)))
            weight = "bold" if "bold" in elem.attrib.get("font-weight", "").lower() else "normal"
            canvas.create_text(x, y, text=content, fill=fill or outline or "white", font=("Segoe UI", size, weight), anchor=anchor)


class ZipProcessorGUI:
    def __init__(self, master):
        logging.debug("Initializing ZipProcessorGUI")
        self.master = master
        master.title("Bambu2Prusa 3mf Processor")

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
                Path(__file__).resolve().parent / "theme_plugins",
                Path.home() / ".bambu2prusa" / "themes",
            ],
        )
        self.theme_name = StringVar(value=self.theme_engine.base_theme.name)
        self.theme = self.theme_engine.palette_for(self.theme_name.get())

        master.configure(bg=self.theme["bg"])
        master.geometry("520x560")
        master.minsize(500, 520)
        master.option_add("*Font", "Segoe UI 11")
        self.icon_image = None
        self._apply_window_icon()

        self.hero = Frame(master, bg=self.theme["panel"], highlightthickness=1, highlightbackground=self.theme["panel_outline"])
        self.hero.pack(fill="x", padx=16, pady=(16, 8))

        self.hero_canvas = Canvas(
            self.hero,
            width=480,
            height=150,
            bg=self.theme["panel"],
            highlightthickness=0,
        )
        self.hero_canvas.pack(fill="both", expand=True, padx=12, pady=12)
        self.render_header_graphic(self.hero_canvas)

        self.title = Label(
            self.hero,
            text="Bambu ➜ Prusa Converter",
            fg=self.theme["text"],
            bg=self.theme["panel"],
            font=("Segoe UI", 15, "bold"),
        )
        self.title.pack(padx=16, anchor="w")

        self.subtitle = Label(
            self.hero,
            text="Theming-ready UI with plugin-friendly palettes.",
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            font=("Segoe UI", 10),
        )
        self.subtitle.pack(padx=16, pady=(0, 12), anchor="w")

        self.content = Frame(master, bg=self.theme["bg"])
        self.content.pack(fill="both", expand=True, padx=16)

        self.theme_row = Frame(self.content, bg=self.theme["bg"])
        self.theme_row.pack(fill="x", pady=(0, 8))

        self.theme_label = Label(
            self.theme_row,
            text="Theme",
            fg=self.theme["text"],
            bg=self.theme["bg"],
        )
        self.theme_label.pack(side="left")

        self.theme_menu = OptionMenu(
            self.theme_row,
            self.theme_name,
            *self.theme_engine.available_themes(),
            command=lambda _: self._on_theme_selected(),
        )
        self._style_option_menu(self.theme_menu)
        self.theme_menu.pack(side="left", padx=10)

        self.label = Label(
            self.content,
            text="Select input and output 3mf files.",
            fg=self.theme["text"],
            bg=self.theme["bg"],
        )
        self.label.pack(pady=8, anchor="w")

        self.buttons = Frame(self.content, bg=self.theme["bg"])
        self.buttons.pack(fill="x", pady=4)

        self.select_input_button = self._styled_button(
            self.buttons,
            text="Select Input Bambu 3mf",
            command=self.select_input,
            primary=True,
        )
        self.select_input_button.pack(pady=6, fill="x")

        self.select_output_button = self._styled_button(
            self.buttons,
            text="Select Output Prusa 3mf",
            command=self.select_output,
        )
        self.select_output_button.pack(pady=6, fill="x")

        self.process_button = self._styled_button(
            self.buttons,
            text="Process",
            command=self.bambu3mf2prusa3mf,
            primary=True,
        )
        self.process_button.pack(pady=(10, 4), fill="x")

        self.status_label = Label(
            self.content,
            text="",
            fg=self.theme["muted"],
            bg=self.theme["bg"],
            wraplength=460,
            justify="left",
        )
        self.status_label.pack(pady=8, anchor="w")

        self.input_file = ""
        self.output_file = ""
        self.default_output_dir = detect_cloud_storage_root()
        self.converter = BambuToPrusaConverter()
        self.apply_theme(self.theme)

    def _apply_window_icon(self):
        try:
            self.icon_image = PhotoImage(data=ICON_IMAGE_BASE64)
            self.master.iconphoto(True, self.icon_image)
            logging.debug("Applied embedded window icon")
        except Exception as exc:  # pragma: no cover - Tk icon loading is platform specific
            logging.error("Unable to set window icon: %s", exc)

    def _styled_button(self, parent, text, command, primary=False):
        """Create a button with Discord/Steam-inspired styling."""

        bg = self.theme["accent"] if primary else self.theme["panel"]
        active_bg = self.theme["accent_alt"] if primary else self.theme["panel_outline"]
        fg = "#ffffff"
        button = Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            highlightthickness=0,
        )
        button.primary = primary
        return button

    def _style_option_menu(self, menu_widget: OptionMenu):
        menu_widget.configure(
            bg=self.theme["panel"],
            fg=self.theme["text"],
            activebackground=self.theme["panel_outline"],
            activeforeground=self.theme["text"],
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        menu_widget["menu"].configure(bg=self.theme["panel"], fg=self.theme["text"], activeborderwidth=0)

    def render_header_graphic(self, canvas):
        svg_path = Path(__file__).resolve().parent / "assets" / "bambu2prusa_badge.svg"
        if not svg_path.exists():
            canvas.create_text(12, 12, anchor="nw", text="Bambu2Prusa", fill=self.theme["text"], font=("Segoe UI", 16, "bold"))
            return

        render_svg_on_canvas(canvas, svg_path)

        canvas.create_rectangle(12, 120, 468, 140, fill=self.theme["panel"], outline="")
        canvas.create_text(
            24,
            130,
            anchor="w",
            text="SVG-driven banner honoring Discord & Steam aesthetics",
            fill=self.theme["muted"],
            font=("Segoe UI", 9),
        )

    def select_input(self):
        logging.debug("Selecting input file")
        self.input_file = filedialog.askopenfilename(filetypes=[("3mf files", "*.3mf")])
        if self.input_file:
            self.status_label.config(
                text=f"Input file selected: {os.path.basename(self.input_file)}",
                fg=self.theme["text"],
            )
        else:
            self.status_label.config(text="Input selection canceled.", fg=self.theme["warning"])

    def select_output(self):
        logging.debug("Selecting output file")
        save_options = {
            "defaultextension": ".3mf",
            "filetypes": [("3mf files", "*.3mf")],
        }
        if self.default_output_dir:
            save_options["initialdir"] = str(self.default_output_dir)

        self.output_file = filedialog.asksaveasfilename(**save_options)
        if self.output_file:
            self.status_label.config(
                text=f"Output file selected: {os.path.basename(self.output_file)}",
                fg=self.theme["text"],
            )
        else:
            self.status_label.config(text="Output selection canceled.", fg=self.theme["warning"])

    def bambu3mf2prusa3mf(self):
        logging.debug("Converting Bambu 3mf to Prusa 3mf via GUI")
        try:
            if not self.input_file or not self.output_file:
                self.status_label.config(text="Please provide both input and output files.", fg=self.theme["warning"])
                return
            self.converter.convert_archive(self.input_file, self.output_file)
            self.status_label.config(
                text=f"Output file created: {os.path.basename(self.output_file)}",
                fg=self.theme["text"],
            )
        except Exception as exc:  # pragma: no cover - GUI messaging
            logging.error("An error occurred during processing: %s", exc)
            self.status_label.config(text=f"Error: {exc}", fg="#ff6b6b")

    def _on_theme_selected(self):
        selected_palette = self.theme_engine.palette_for(self.theme_name.get())
        self.apply_theme(selected_palette)

    def apply_theme(self, palette):
        self.theme = palette
        self.master.configure(bg=self.theme["bg"])
        self.content.configure(bg=self.theme["bg"])
        self.buttons.configure(bg=self.theme["bg"])
        self.hero.configure(bg=self.theme["panel"], highlightbackground=self.theme["panel_outline"])
        self.hero_canvas.configure(bg=self.theme["panel"])
        self.hero_canvas.delete("all")
        self.render_header_graphic(self.hero_canvas)

        self.title.configure(fg=self.theme["text"], bg=self.theme["panel"])
        self.subtitle.configure(fg=self.theme["muted"], bg=self.theme["panel"])
        self.label.configure(fg=self.theme["text"], bg=self.theme["bg"])
        self.status_label.configure(bg=self.theme["bg"])
        self.theme_row.configure(bg=self.theme["bg"])
        self.theme_label.configure(fg=self.theme["text"], bg=self.theme["bg"])
        self._style_option_menu(self.theme_menu)

        for button in (self.select_input_button, self.select_output_button, self.process_button):
            primary = getattr(button, "primary", False)
            bg = self.theme["accent"] if primary else self.theme["panel"]
            active_bg = self.theme["accent_alt"] if primary else self.theme["panel_outline"]
            button.configure(bg=bg, activebackground=active_bg, fg="#ffffff")


def main():
    root = Tk()
    app = ZipProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
