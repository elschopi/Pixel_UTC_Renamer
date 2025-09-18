# ==============================================================================
# MIT License
#
# Copyright (c) 2025 [Dein Name oder Pseudonym hier eintragen]
#
# Permission is hereby granted, free of charge, to a any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

import os
import re
import shutil
import piexif
import threading
from datetime import datetime
# --- UPDATE: Radiobutton aus dem Standard-Import entfernt ---
from tkinter import Tk, Toplevel, Listbox, Scrollbar, filedialog, messagebox, StringVar, BooleanVar
# --- UPDATE: Radiobutton zum ttk-Import hinzugefügt ---
from tkinter.ttk import Progressbar, Style, Frame, Label, Button, Checkbutton, Radiobutton

# ==============================================================================
# Übersetzungen
# ==============================================================================
TRANSLATIONS = {
    "de": {
        "window_title": "Pixel Photo Renamer v1.4",
        "source_folder_label": "1. Quellordner (mit den Pixel-Bildern):",
        "select_source_folder": "Quellordner auswählen...",
        "no_folder_selected": "Noch kein Ordner ausgewählt.",
        "output_folder_label": "2. Ausgabeordner (wo die umbenannten Bilder landen):",
        "select_output_folder": "Ausgabeordner auswählen...",
        "preview_label": "3. Vorschau der Umbenennung:",
        "create_preview": "Vorschau erstellen",
        "start_renaming": "Umbenennung starten",
        "copy_files": "Dateien kopieren statt verschieben (empfohlen)",
        "error": "Fehler",
        "select_source_error": "Bitte wähle zuerst einen gültigen Quellordner aus.",
        "select_output_error": "Bitte wähle zuerst einen gültigen Ausgabeordner aus.",
        "warning": "Warnung",
        "same_folder_warning": "Quell- und Zielordner sind identisch. Bitte 'Kopieren' wählen oder einen anderen Ausgabeordner, um Datenverlust zu vermeiden.",
        "done": "Fertig",
        "files_processed": "Dateien wurden erfolgreich verarbeitet.",
        "searching_files": "Durchsuche Dateien...",
        "processing_files": "Verarbeite Dateien...",
        "please_wait": "Bitte warten...",
        "status_ok": "OK",
        "status_no_exif": "Kein EXIF-Datum",
        "status_already_correct": "Bereits korrekt",
        "status_read_error": "Fehler beim Lesen",
    },
    "en": {
        "window_title": "Pixel Photo Renamer v1.4",
        "source_folder_label": "1. Source Folder (with the Pixel photos):",
        "select_source_folder": "Select Source Folder...",
        "no_folder_selected": "No folder selected yet.",
        "output_folder_label": "2. Output Folder (where renamed photos will go):",
        "select_output_folder": "Select Output Folder...",
        "preview_label": "3. Renaming Preview:",
        "create_preview": "Create Preview",
        "start_renaming": "Start Renaming",
        "copy_files": "Copy files instead of moving (recommended)",
        "error": "Error",
        "select_source_error": "Please select a valid source folder first.",
        "select_output_error": "Please select a valid output folder first.",
        "warning": "Warning",
        "same_folder_warning": "Source and output folders are the same. Please select 'Copy' or a different output folder to avoid data loss.",
        "done": "Done",
        "files_processed": "files have been processed successfully.",
        "searching_files": "Searching files...",
        "processing_files": "Processing files...",
        "please_wait": "Please wait...",
        "status_ok": "OK",
        "status_no_exif": "No EXIF date",
        "status_already_correct": "Already correct",
        "status_read_error": "Read error",
    },
    "fr": {
        "window_title": "Pixel Photo Renamer v1.4",
        "source_folder_label": "1. Dossier Source (avec les photos Pixel):",
        "select_source_folder": "Sélectionner le dossier source...",
        "no_folder_selected": "Aucun dossier sélectionné.",
        "output_folder_label": "2. Dossier de Destination (où les photos iront):",
        "select_output_folder": "Sélectionner le dossier de destination...",
        "preview_label": "3. Aperçu du renommage:",
        "create_preview": "Créer l'aperçu",
        "start_renaming": "Démarrer le renommage",
        "copy_files": "Copier les fichiers au lieu de déplacer (recommandé)",
        "error": "Erreur",
        "select_source_error": "Veuillez d'abord sélectionner un dossier source valide.",
        "select_output_error": "Veuillez d'abord sélectionner un dossier de destination valide.",
        "warning": "Avertissement",
        "same_folder_warning": "Les dossiers source et de destination sont identiques. Veuillez sélectionner 'Copier' ou un autre dossier pour éviter la perte de données.",
        "done": "Terminé",
        "files_processed": "fichiers ont été traités avec succès.",
        "searching_files": "Recherche de fichiers...",
        "processing_files": "Traitement des fichiers...",
        "please_wait": "Veuillez patienter...",
        "status_ok": "OK",
        "status_no_exif": "Pas de date EXIF",
        "status_already_correct": "Déjà correct",
        "status_read_error": "Erreur de lecture",
    }
}


# ==============================================================================
# Hauptanwendungsklasse
# ==============================================================================
class RenamerApp:
    def __init__(self, master):
        self.master = master
        self.language = StringVar(value='de')
        self.language.trace_add('write', self.update_ui_language)

        master.geometry("800x600")
        master.minsize(600, 400)
        
        self.setup_styles()

        self.source_dir = StringVar()
        self.output_dir = StringVar()
        self.copy_instead_of_move = BooleanVar(value=True)
        self.file_list = []

        self.create_widgets()
        self.update_ui_language()

    def _(self, key):
        """Holt den übersetzten Text für einen gegebenen Schlüssel."""
        return TRANSLATIONS[self.language.get()][key]

    def setup_styles(self):
        self.style = Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            print("Hinweis: 'clam' Theme nicht gefunden. Verwende Standard-System-Theme.")
        self.style.configure("TButton", padding=10, font=('Segoe UI', 10))
        self.style.configure("TLabel", background="#2E2E2E", foreground="white", font=('Segoe UI', 10))
        self.style.configure("Header.TLabel", font=('Segoe UI', 12, 'bold'))
        self.style.configure("TFrame", background="#2E2E2E")
        self.master.configure(bg="#2E2E2E")
        self.style.configure("TRadiobutton", background="#2E2E2E", foreground="white", font=('Segoe UI', 9))
        self.style.map("TRadiobutton", background=[('active', '#2E2E2E')])
        self.style.configure("TCheckbutton", background="#2E2E2E", foreground="white", font=('Segoe UI', 10))
        self.style.map("TCheckbutton", indicatorcolor=[('selected', '#007ACC'), ('!selected', '#555555')], background=[('active', '#2E2E2E')])

    def create_widgets(self):
        self.main_frame = Frame(self.master, style="TFrame", padding=(20, 10))
        self.main_frame.pack(fill="both", expand=True)

        # --- Sprachauswahl ---
        lang_frame = Frame(self.main_frame, style="TFrame")
        lang_frame.pack(fill="x", anchor="e")
        Radiobutton(lang_frame, text="DE", variable=self.language, value='de', style="TRadiobutton").pack(side="left", padx=5)
        Radiobutton(lang_frame, text="EN", variable=self.language, value='en', style="TRadiobutton").pack(side="left", padx=5)
        Radiobutton(lang_frame, text="FR", variable=self.language, value='fr', style="TRadiobutton").pack(side="left", padx=5)

        # --- Ordnerauswahl ---
        folder_frame = Frame(self.main_frame, style="TFrame")
        folder_frame.pack(fill="x", pady=5)

        self.source_folder_label = Label(folder_frame, style="Header.TLabel")
        self.source_folder_label.pack(anchor="w")
        self.select_source_button = Button(folder_frame, command=self.select_source_dir, style="TButton")
        self.select_source_button.pack(fill="x", pady=(5, 10))
        self.source_dir_label = Label(folder_frame, textvariable=self.source_dir, wraplength=700, style="TLabel")
        self.source_dir_label.pack(anchor="w", pady=(0, 10))
        
        self.output_folder_label = Label(folder_frame, style="Header.TLabel")
        self.output_folder_label.pack(anchor="w")
        self.select_output_button = Button(folder_frame, command=self.select_output_dir, style="TButton")
        self.select_output_button.pack(fill="x", pady=(5, 10))
        self.output_dir_label = Label(folder_frame, textvariable=self.output_dir, wraplength=700, style="TLabel")
        self.output_dir_label.pack(anchor="w", pady=(0, 20))

        # --- Vorschau-Bereich ---
        preview_frame = Frame(self.main_frame, style="TFrame")
        preview_frame.pack(fill="both", expand=True)
        self.preview_label = Label(preview_frame, style="Header.TLabel")
        self.preview_label.pack(anchor="w", pady=(0, 5))
        
        list_frame = Frame(preview_frame, style="TFrame")
        list_frame.pack(fill="both", expand=True)
        self.listbox = Listbox(list_frame, bg="#3C3C3C", fg="white", selectbackground="#007ACC", borderwidth=0, highlightthickness=0, font=('Consolas', 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # --- Aktionen ---
        action_frame = Frame(self.main_frame, style="TFrame")
        action_frame.pack(fill="x", pady=(20, 10))
        self.preview_button = Button(action_frame, command=self.start_preview, style="TButton")
        self.preview_button.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.rename_button = Button(action_frame, command=self.start_processing, style="TButton", state="disabled")
        self.rename_button.pack(side="left", expand=True, fill="x")
        self.copy_checkbutton = Checkbutton(self.main_frame, variable=self.copy_instead_of_move, style="TCheckbutton")
        self.copy_checkbutton.pack(anchor="w", pady=10)

    def update_ui_language(self, *args):
        """Aktualisiert alle Texte in der GUI basierend auf der gewählten Sprache."""
        self.master.title(self._("window_title"))
        self.source_folder_label.config(text=self._("source_folder_label"))
        self.select_source_button.config(text=self._("select_source_folder"))
        self.output_folder_label.config(text=self._("output_folder_label"))
        self.select_output_button.config(text=self._("select_output_folder"))
        self.preview_label.config(text=self._("preview_label"))
        self.preview_button.config(text=self._("create_preview"))
        self.rename_button.config(text=self._("start_renaming"))
        self.copy_checkbutton.config(text=self._("copy_files"))
        
        # Prüfen, ob der String ein Platzhalter ist, bevor er überschrieben wird
        if self.source_dir.get() in (TRANSLATIONS['de']['no_folder_selected'], TRANSLATIONS['en']['no_folder_selected'], TRANSLATIONS['fr']['no_folder_selected']):
            self.source_dir.set(self._("no_folder_selected"))
        if self.output_dir.get() in (TRANSLATIONS['de']['no_folder_selected'], TRANSLATIONS['en']['no_folder_selected'], TRANSLATIONS['fr']['no_folder_selected']):
            self.output_dir.set(self._("no_folder_selected"))
        
        self.update_preview_listbox()

    def select_source_dir(self):
        path = filedialog.askdirectory(title=self._("select_source_folder"))
        if path:
            self.source_dir.set(path)
            self.listbox.delete(0, "end")
            self.rename_button.config(state="disabled")

    def select_output_dir(self):
        path = filedialog.askdirectory(title=self._("select_output_folder"))
        if path:
            self.output_dir.set(path)

    def start_preview(self):
        if not os.path.isdir(self.source_dir.get()):
            messagebox.showerror(self._("error"), self._("select_source_error"))
            return
        self.listbox.delete(0, "end")
        self.rename_button.config(state="disabled")
        self.show_progress_popup(self._("searching_files"), self.generate_preview)

    def generate_preview(self, progress_callback):
        self.file_list.clear()
        source_path = self.source_dir.get()
        all_files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
        total_files = len(all_files)
        
        for i, filename in enumerate(all_files):
            new_name, status_key = self.get_new_filename(os.path.join(source_path, filename))
            self.file_list.append({"original": filename, "new": new_name, "status_key": status_key})
            if total_files > 0:
                progress_callback((i + 1) / total_files * 100)
        self.master.after(0, self.update_preview_listbox)

    def update_preview_listbox(self):
        self.listbox.delete(0, "end")
        if not self.file_list: return

        max_len = max((len(f['original']) for f in self.file_list), default=0) + 3
        for item in self.file_list:
            status_text = self._(item['status_key'])
            line = f"{item['original']:{max_len}} -> {item['new']} [{status_text}]"
            self.listbox.insert("end", line)
            color = '#90EE90' if item['status_key'] == "status_ok" else '#FFC107'
            self.listbox.itemconfig("end", {'fg': color})
            
        if any(f['status_key'] == "status_ok" for f in self.file_list):
            self.rename_button.config(state="normal")
        else:
            self.rename_button.config(state="disabled")

    def get_new_filename(self, original_path):
        filename = os.path.basename(original_path)
        try:
            exif_dict = piexif.load(original_path)
            date_bytes = exif_dict.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)
            if not date_bytes: return filename, "status_no_exif"
            
            date_obj = datetime.strptime(date_bytes.decode("utf-8"), "%Y:%m:%d %H:%M:%S")
            timestamp = date_obj.strftime("%Y%m%d_%H%M%S")
            
            match = re.compile(r"PXL_\d{8}_\d{9}(.*?)\..{3,4}$", re.IGNORECASE).match(filename)
            suffix = match.group(1) if match else ""
            ext = os.path.splitext(filename)[1]
            new_name = f"{timestamp}{suffix}{ext}"
            
            return (filename, "status_already_correct") if new_name.lower() == filename.lower() else (new_name, "status_ok")
        except Exception:
            return filename, "status_read_error"

    def start_processing(self):
        if not os.path.isdir(self.output_dir.get()):
            messagebox.showerror(self._("error"), self._("select_output_error"))
            return
        if self.source_dir.get() == self.output_dir.get() and not self.copy_instead_of_move.get():
             messagebox.showwarning(self._("warning"), self._("same_folder_warning"))
             return
        self.show_progress_popup(self._("processing_files"), self.process_files)

    def process_files(self, progress_callback):
        source = self.source_dir.get()
        output = self.output_dir.get()
        to_process = [f for f in self.file_list if f['status_key'] == "status_ok"]
        total_to_process = len(to_process)
        
        for i, item in enumerate(to_process):
            original_path = os.path.join(source, item['original'])
            new_path = os.path.join(output, item['new'])
            try:
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(item['new'])
                    count = 1
                    while os.path.exists(new_path):
                        new_path = os.path.join(output, f"{base}_{count}{ext}")
                        count += 1
                if self.copy_instead_of_move.get():
                    shutil.copy2(original_path, new_path)
                else:
                    shutil.move(original_path, new_path)
            except Exception as e:
                print(f"Error processing {item['original']}: {e}")
            
            if total_to_process > 0:
                progress_callback((i + 1) / total_to_process * 100)
        
        processed_count = len(to_process)
        message_text = f"{processed_count} {self._('files_processed')}"
        self.master.after(0, lambda: messagebox.showinfo(self._("done"), message_text))
        self.master.after(0, self.start_preview)

    def show_progress_popup(self, title, task_function):
        popup = Toplevel(self.master)
        popup.title("")
        popup.geometry("300x120")
        popup.configure(bg="#2E2E2E")
        popup.transient(self.master)
        popup.grab_set()
        Label(popup, text=title, style="Header.TLabel").pack(pady=(10,5))
        Label(popup, text=self._("please_wait"), style="TLabel").pack()
        progress = Progressbar(popup, orient="horizontal", length=250, mode="determinate")
        progress.pack(pady=10)
        
        def run_task():
            try:
                task_function(lambda v: self.master.after(0, progress.config, {'value': v}))
            finally:
                self.master.after(0, popup.destroy)
        
        threading.Thread(target=run_task, daemon=True).start()

if __name__ == "__main__":
    root = Tk()
    app = RenamerApp(root)
    root.mainloop()

