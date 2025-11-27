import logging
import os
from tkinter import Button, Entry, Label, StringVar, Tk, Toplevel, filedialog

from bambu_to_prusa.converter import BambuToPrusaConverter
from bambu_to_prusa.settings import SettingsManager


class ZipProcessorGUI:
    def __init__(self, master):
        logging.debug("Initializing ZipProcessorGUI")
        self.master = master
        master.title("Bambu2Prusa 3mf Processor")

        self.settings = SettingsManager()

        self.label = Label(master, text="Select input and output 3mf files.")
        self.label.pack(pady=10)

        self.select_input_button = Button(master, text="Select Input Bambu 3mf", command=self.select_input)
        self.select_input_button.pack(pady=5)

        self.select_output_button = Button(master, text="Select Output Prusa 3mf", command=self.select_output)
        self.select_output_button.pack(pady=5)

        self.process_button = Button(master, text="Process", command=self.bambu3mf2prusa3mf)
        self.process_button.pack(pady=10)

        self.settings_button = Button(master, text="Settings", command=self.open_settings_dialog)
        self.settings_button.pack(pady=5)

        self.status_label = Label(master, text="")
        self.status_label.pack(pady=5)

        self.input_file = ""
        self.output_file = ""
        self.converter = BambuToPrusaConverter()
        self.settings_window = None
        self.input_dir_var = StringVar(value=self.settings.last_input_dir)
        self.output_dir_var = StringVar(value=self.settings.last_output_dir)

    def select_input(self):
        logging.debug("Selecting input file")
        self.input_file = filedialog.askopenfilename(
            filetypes=[("3mf files", "*.3mf")], initialdir=self.settings.last_input_dir or None
        )
        if self.input_file:
            input_dir = os.path.dirname(self.input_file)
            self.settings.update_last_input_dir(input_dir)
            self.input_dir_var.set(input_dir)
            self.status_label.config(text=f"Input file selected: {os.path.basename(self.input_file)}")

    def select_output(self):
        logging.debug("Selecting output file")
        initial_dir = self.settings.last_output_dir or self.settings.last_input_dir or None
        self.output_file = filedialog.asksaveasfilename(
            defaultextension=".3mf", filetypes=[("3mf files", "*.3mf")], initialdir=initial_dir
        )
        if self.output_file:
            output_dir = os.path.dirname(self.output_file)
            self.settings.update_last_output_dir(output_dir)
            self.output_dir_var.set(output_dir)
            self.status_label.config(text=f"Output file selected: {os.path.basename(self.output_file)}")

    def bambu3mf2prusa3mf(self):
        logging.debug("Converting Bambu 3mf to Prusa 3mf via GUI")
        try:
            if not self.input_file or not self.output_file:
                self.status_label.config(text="Please provide both input and output files.")
                return
            self.converter.convert_archive(self.input_file, self.output_file)
            self.status_label.config(text=f"Output file created: {os.path.basename(self.output_file)}")
        except Exception as exc:  # pragma: no cover - GUI messaging
            logging.error("An error occurred during processing: %s", exc)
            self.status_label.config(text=f"Error: {exc}")

    def open_settings_dialog(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = Toplevel(self.master)
        self.settings_window.title("Settings")

        Label(self.settings_window, text="Default input directory:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        Entry(self.settings_window, textvariable=self.input_dir_var, width=50).grid(row=0, column=1, padx=10, pady=5)
        Button(self.settings_window, text="Browse", command=self.choose_input_dir).grid(row=0, column=2, padx=10, pady=5)

        Label(self.settings_window, text="Default output directory:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        Entry(self.settings_window, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, padx=10, pady=5)
        Button(self.settings_window, text="Browse", command=self.choose_output_dir).grid(row=1, column=2, padx=10, pady=5)

        Button(self.settings_window, text="Save", command=self.save_settings).grid(row=2, column=1, pady=10)

    def choose_input_dir(self):
        directory = filedialog.askdirectory(initialdir=self.input_dir_var.get() or None)
        if directory:
            self.input_dir_var.set(directory)

    def choose_output_dir(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get() or None)
        if directory:
            self.output_dir_var.set(directory)

    def save_settings(self):
        self.settings.update_last_input_dir(self.input_dir_var.get())
        self.settings.update_last_output_dir(self.output_dir_var.get())
        if self.settings_window:
            self.settings_window.destroy()


def main():
    root = Tk()
    app = ZipProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
