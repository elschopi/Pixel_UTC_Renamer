# ==============================================================================
# MIT License
#
# Copyright (c) 2025 elschopi
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

# Import der notwendigen Bibliotheken
import os
import re
import shutil
import piexif
import threading
from datetime import datetime
from tkinter import Tk, Toplevel, Listbox, Scrollbar, filedialog, messagebox, StringVar, BooleanVar
from tkinter.ttk import Progressbar, Style, Frame, Label, Button, Checkbutton, Radiobutton

# ==============================================================================
# Übersetzungen
# Enthält alle Texte der Benutzeroberfläche in den unterstützten Sprachen.
# ==============================================================================
TRANSLATIONS = {
    "de": {
        "window_title": "Pixel Photo Renamer v1.7",
        "source_folder_label": "1. Quellordner (mit den Pixel-Bildern):",
        "select_source_folder": "Quellordner auswählen...",
        "no_folder_selected": "Noch kein Ordner ausgewählt.",
        "output_folder_label": "2. Ausgabeordner (wo die umbenannten Bilder landen):",
        "select_output_folder": "Ausgabeordner auswählen...",
        "summary_label": "3. Zusammenfassung des Ordners:",
        "total_files": "Dateien Gesamt:",
        "pixel_jpg": "Pixel-Bilder (JPG):",
        "pixel_dng": "Pixel-Bilder (DNG):",
        "videos": "Videos (übersprungen):",
        "other_files": "Andere Dateien (übersprungen):",
        "preview_label": "4. Vorschau der Umbenennung:",
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
        "status_not_pixel": "Kein Pixel-Foto",
        "status_video": "Video",
    },
    "en": {
        "window_title": "Pixel Photo Renamer v1.7",
        "source_folder_label": "1. Source Folder (with the Pixel photos):",
        "select_source_folder": "Select Source Folder...",
        "no_folder_selected": "No folder selected yet.",
        "output_folder_label": "2. Output Folder (where renamed photos will go):",
        "select_output_folder": "Select Output Folder...",
        "summary_label": "3. Folder Summary:",
        "total_files": "Total Files:",
        "pixel_jpg": "Pixel Photos (JPG):",
        "pixel_dng": "Pixel Photos (DNG):",
        "videos": "Videos (skipped):",
        "other_files": "Other Files (skipped):",
        "preview_label": "4. Renaming Preview:",
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
        "status_not_pixel": "Not a Pixel photo",
        "status_video": "Video",
    },
    "fr": {
        "window_title": "Pixel Photo Renamer v1.7",
        "source_folder_label": "1. Dossier Source (avec les photos Pixel):",
        "select_source_folder": "Sélectionner le dossier source...",
        "no_folder_selected": "Aucun dossier sélectionné.",
        "output_folder_label": "2. Dossier de Destination (où les photos iront):",
        "select_output_folder": "Sélectionner le dossier de destination...",
        "summary_label": "3. Résumé du dossier:",
        "total_files": "Total Fichiers:",
        "pixel_jpg": "Photos Pixel (JPG):",
        "pixel_dng": "Photos Pixel (DNG):",
        "videos": "Vidéos (ignorées):",
        "other_files": "Autres Fichiers (ignorés):",
        "preview_label": "4. Aperçu du renommage:",
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
        "status_not_pixel": "Pas une photo Pixel",
        "status_video": "Vidéo",
    }
}


# ==============================================================================
# Hauptanwendungsklasse
# ==============================================================================
class RenamerApp:
    def __init__(self, master):
        """
        Initialisiert die Hauptanwendung. Wird beim Start des Programms aufgerufen.
        'master' ist das Hauptfenster der Anwendung (Tkinter root).
        """
        self.master = master
        
        # Variable zur Speicherung der aktuell ausgewählten Sprache ('de', 'en', 'fr')
        self.language = StringVar(value='de')
        # "Trace" sorgt dafür, dass die Funktion 'update_ui_language' immer aufgerufen wird,
        # wenn sich der Wert der 'language'-Variable ändert.
        self.language.trace_add('write', self.update_ui_language)

        # Fenstereinstellungen
        master.geometry("800x750") # Startgröße des Fensters
        master.minsize(600, 500)   # Minimale Größe, auf die das Fenster verkleinert werden kann

        # Versuch, das Programm-Icon zu laden. Scheitert nicht, wenn die Datei fehlt.
        try:
            master.iconbitmap('icon.ico')
        except Exception:
            print("Hinweis: 'icon.ico' nicht gefunden. Programm startet ohne Icon.")
        
        # Initialisiert die Styles (Farben, Schriften) für die GUI-Elemente
        self.setup_styles()

        # Tkinter-Variablen, die mit den GUI-Elementen verknüpft sind, um ihre Werte zu speichern
        self.source_dir = StringVar() # Speicher für den Pfad des Quellordners
        self.output_dir = StringVar() # Speicher für den Pfad des Ausgabeordners
        self.copy_instead_of_move = BooleanVar(value=True) # Speicher für den Zustand der Checkbox (Kopieren/Verschieben)
        
        # Liste zur Speicherung der Analyseergebnisse für jede Datei
        self.file_list = []
        
        # Dictionary mit Tkinter-Variablen für die Statistik-Anzeige
        self.summary_vars = {
            "total": StringVar(), "jpg": StringVar(),
            "dng": StringVar(), "videos": StringVar(), "other": StringVar()
        }

        # Erstellt alle sichtbaren Elemente (Buttons, Labels etc.) der Benutzeroberfläche
        self.create_widgets()
        # Setzt die Texte der Benutzeroberfläche auf die Standardsprache (Deutsch)
        self.update_ui_language()

    def _(self, key):
        """
        Eine Hilfsfunktion, um den übersetzten Text für einen Schlüssel in der aktuell
        ausgewählten Sprache aus dem TRANSLATIONS-Dictionary zu holen.
        Beispiel: _("window_title") gibt "Pixel Photo Renamer v1.7" zurück.
        """
        return TRANSLATIONS[self.language.get()][key]

    def setup_styles(self):
        """
        Definiert das Aussehen (Styling) der GUI-Elemente.
        Verwendet das modernere ttk-Styling-System.
        """
        self.style = Style()
        try:
            # Versucht, ein modernes Theme zu laden, das ein dunkles Design erlaubt
            self.style.theme_use('clam')
        except Exception:
            # Fällt auf das Standard-System-Theme zurück, wenn 'clam' nicht verfügbar ist
            print("Hinweis: 'clam' Theme nicht gefunden. Verwende Standard-System-Theme.")
        
        # Konfiguriert das Aussehen für verschiedene Widget-Typen
        self.style.configure("TButton", padding=10, font=('Segoe UI', 10))
        self.style.configure("TLabel", background="#2E2E2E", foreground="white", font=('Segoe UI', 10))
        self.style.configure("Header.TLabel", font=('Segoe UI', 12, 'bold')) # Eigener Stil für Überschriften
        self.style.configure("Summary.TLabel", font=('Segoe UI', 10)) # Eigener Stil für die Zusammenfassung
        self.style.configure("TFrame", background="#2E2E2E")
        self.master.configure(bg="#2E2E2E") # Hintergrundfarbe des Hauptfensters
        self.style.configure("TRadiobutton", background="#2E2E2E", foreground="white", font=('Segoe UI', 9))
        self.style.map("TRadiobutton", background=[('active', '#2E2E2E')]) # Verhindert Farbänderung bei Mouse-Over
        self.style.configure("TCheckbutton", background="#2E2E2E", foreground="white", font=('Segoe UI', 10))
        self.style.map("TCheckbutton", indicatorcolor=[('selected', '#007ACC'), ('!selected', '#555555')], background=[('active', '#2E2E2E')])

    def create_widgets(self):
        """
        Erstellt und platziert alle GUI-Elemente im Hauptfenster.
        """
        # Haupt-Frame, der alle anderen Elemente enthält und für den Innenabstand sorgt
        self.main_frame = Frame(self.master, style="TFrame", padding=(20, 10))
        self.main_frame.pack(fill="both", expand=True)

        # Frame für die Sprachauswahl-Buttons (oben rechts)
        lang_frame = Frame(self.main_frame, style="TFrame")
        lang_frame.pack(fill="x", anchor="e")
        Radiobutton(lang_frame, text="DE", variable=self.language, value='de', style="TRadiobutton").pack(side="left", padx=5)
        Radiobutton(lang_frame, text="EN", variable=self.language, value='en', style="TRadiobutton").pack(side="left", padx=5)
        Radiobutton(lang_frame, text="FR", variable=self.language, value='fr', style="TRadiobutton").pack(side="left", padx=5)

        # Frame für die Ordnerauswahl-Elemente
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
        self.output_dir_label.pack(anchor="w", pady=(0, 10))
        
        # Frame für die Zusammenfassung/Statistik
        summary_frame = Frame(self.main_frame, style="TFrame")
        summary_frame.pack(fill="x", pady=10, padx=5)
        self.summary_label = Label(summary_frame, style="Header.TLabel")
        self.summary_label.pack(anchor="w", pady=(0,5))
        self.summary_total_label = Label(summary_frame, textvariable=self.summary_vars["total"], style="Summary.TLabel")
        self.summary_total_label.pack(anchor="w")
        self.summary_jpg_label = Label(summary_frame, textvariable=self.summary_vars["jpg"], style="Summary.TLabel")
        self.summary_jpg_label.pack(anchor="w")
        self.summary_dng_label = Label(summary_frame, textvariable=self.summary_vars["dng"], style="Summary.TLabel")
        self.summary_dng_label.pack(anchor="w")
        self.summary_videos_label = Label(summary_frame, textvariable=self.summary_vars["videos"], style="Summary.TLabel")
        self.summary_videos_label.pack(anchor="w")
        self.summary_other_label = Label(summary_frame, textvariable=self.summary_vars["other"], style="Summary.TLabel")
        self.summary_other_label.pack(anchor="w")

        # Frame für die Vorschau-Liste
        preview_frame = Frame(self.main_frame, style="TFrame")
        preview_frame.pack(fill="both", expand=True, pady=5)
        self.preview_label = Label(preview_frame, style="Header.TLabel")
        self.preview_label.pack(anchor="w", pady=(0, 5))
        list_frame = Frame(preview_frame, style="TFrame")
        list_frame.pack(fill="both", expand=True)
        self.listbox = Listbox(list_frame, bg="#3C3C3C", fg="white", selectbackground="#007ACC", borderwidth=0, highlightthickness=0, font=('Consolas', 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Frame für die Aktions-Buttons (Vorschau, Umbenennen)
        action_frame = Frame(self.main_frame, style="TFrame")
        action_frame.pack(fill="x", pady=(10, 5))
        self.preview_button = Button(action_frame, command=self.start_preview, style="TButton")
        self.preview_button.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.rename_button = Button(action_frame, command=self.start_processing, style="TButton", state="disabled")
        self.rename_button.pack(side="left", expand=True, fill="x")
        
        # Checkbox für Kopieren vs. Verschieben
        self.copy_checkbutton = Checkbutton(self.main_frame, variable=self.copy_instead_of_move, style="TCheckbutton")
        self.copy_checkbutton.pack(anchor="w", pady=5)

    def update_ui_language(self, *args):
        """
        Aktualisiert alle Texte in der GUI basierend auf der gewählten Sprache.
        Wird automatisch aufgerufen, wenn sich die 'language'-Variable ändert.
        """
        self.master.title(self._("window_title"))
        self.source_folder_label.config(text=self._("source_folder_label"))
        self.select_source_button.config(text=self._("select_source_folder"))
        self.output_folder_label.config(text=self._("output_folder_label"))
        self.select_output_button.config(text=self._("select_output_folder"))
        self.summary_label.config(text=self._("summary_label"))
        self.preview_label.config(text=self._("preview_label"))
        self.preview_button.config(text=self._("create_preview"))
        self.rename_button.config(text=self._("start_renaming"))
        self.copy_checkbutton.config(text=self._("copy_files"))
        
        # Setzt den Platzhaltertext für die Ordnerpfade neu, falls noch kein Ordner gewählt wurde
        if self.source_dir.get() in (TRANSLATIONS['de']['no_folder_selected'], TRANSLATIONS['en']['no_folder_selected'], TRANSLATIONS['fr']['no_folder_selected']):
            self.source_dir.set(self._("no_folder_selected"))
        if self.output_dir.get() in (TRANSLATIONS['de']['no_folder_selected'], TRANSLATIONS['en']['no_folder_selected'], TRANSLATIONS['fr']['no_folder_selected']):
            self.output_dir.set(self._("no_folder_selected"))
        
        # Aktualisiert die Texte in der Vorschau-Liste und der Zusammenfassung
        self.update_preview_listbox()
        self.update_summary_display()

    def select_source_dir(self):
        """Öffnet einen Dialog zur Auswahl des Quellordners."""
        path = filedialog.askdirectory(title=self._("select_source_folder"))
        if path:
            self.source_dir.set(path)
            self.listbox.delete(0, "end") # Leert die Vorschau
            self.rename_button.config(state="disabled") # Deaktiviert den Umbenennen-Button
            for var in self.summary_vars.values():
                var.set("") # Leert die Zusammenfassung

    def select_output_dir(self):
        """Öffnet einen Dialog zur Auswahl des Ausgabeordners."""
        path = filedialog.askdirectory(title=self._("select_output_folder"))
        if path:
            self.output_dir.set(path)

    def start_preview(self):
        """Startet den Vorschau-Prozess."""
        # Prüft, ob ein gültiger Quellordner ausgewählt wurde
        if not os.path.isdir(self.source_dir.get()):
            messagebox.showerror(self._("error"), self._("select_source_error"))
            return
        # Bereinigt die GUI für die neue Vorschau
        self.listbox.delete(0, "end")
        self.rename_button.config(state="disabled")
        # Zeigt das "Bitte warten"-Fenster an und startet die Analyse in einem separaten Thread
        self.show_progress_popup(self._("searching_files"), self.generate_preview)

    def generate_preview(self, progress_callback):
        """
        Analysiert die Dateien im Quellordner und erstellt die Vorschau-Daten.
        Läuft in einem separaten Thread, um die GUI nicht einzufrieren.
        """
        self.file_list.clear()
        source_path = self.source_dir.get()
        all_files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
        
        counts = {"total": len(all_files), "jpg": 0, "dng": 0, "videos": 0, "other": 0}
        
        for i, filename in enumerate(all_files):
            # Holt den neuen Namen und Status für jede Datei
            new_name, status_key = self.get_new_filename(os.path.join(source_path, filename))
            self.file_list.append({"original": filename, "new": new_name, "status_key": status_key})

            # Zählt die Dateitypen für die Zusammenfassung
            ext = os.path.splitext(filename)[1].lower()
            if status_key == "status_video":
                counts["videos"] += 1
            elif status_key == "status_not_pixel":
                counts["other"] += 1
            elif ext == ".dng":
                counts["dng"] += 1
            elif ext in [".jpg", ".jpeg"]:
                counts["jpg"] += 1

            # Aktualisiert den Fortschrittsbalken im Popup
            progress_callback((i + 1) / counts["total"] * 100)
            
        # Aktualisiert die GUI-Elemente (Vorschau-Liste und Zusammenfassung) im Haupt-Thread
        self.master.after(0, self.update_preview_listbox)
        self.master.after(0, lambda: self.update_summary_display(counts))

    def update_summary_display(self, counts=None):
        """Aktualisiert die Texte in der Zusammenfassung."""
        if counts:
            self.summary_vars["total"].set(f"{self._('total_files')} {counts['total']}")
            self.summary_vars["jpg"].set(f"{self._('pixel_jpg')} {counts['jpg']}")
            self.summary_vars["dng"].set(f"{self._('pixel_dng')} {counts['dng']}")
            self.summary_vars["videos"].set(f"{self._('videos')} {counts['videos']}")
            self.summary_vars["other"].set(f"{self._('other_files')} {counts['other']}")
        else: # Setzt die Texte zurück, wenn keine Daten vorhanden sind
             for var in self.summary_vars.values():
                var.set("")

    def update_preview_listbox(self):
        """Füllt die Vorschau-Liste mit den analysierten Daten."""
        self.listbox.delete(0, "end")
        if not self.file_list: return

        # Berechnet die maximale Länge der Dateinamen für eine saubere Ausrichtung
        max_len = max((len(f['original']) for f in self.file_list), default=0) + 3
        for item in self.file_list:
            status_text = self._(item['status_key'])
            line = f"{item['original']:{max_len}} -> {item['new']} [{status_text}]"
            self.listbox.insert("end", line)
            # Färbt die Zeile je nach Status (grün für OK, orange für Warnung/Info)
            color = '#90EE90' if item['status_key'] == "status_ok" else '#FFC107'
            self.listbox.itemconfig("end", {'fg': color})
            
        # Aktiviert den Umbenennen-Button nur, wenn es Dateien gibt, die umbenannt werden können
        if any(f['status_key'] == "status_ok" for f in self.file_list):
            self.rename_button.config(state="normal")
        else:
            self.rename_button.config(state="disabled")

    def get_new_filename(self, original_path):
        """
        Ermittelt den neuen Dateinamen und den Status für eine einzelne Datei.
        Dies ist die Kernlogik des Programms.
        """
        filename = os.path.basename(original_path)
        ext = os.path.splitext(filename)[1].lower()

        # Prüft, ob es sich um eine Videodatei handelt
        if ext in ['.mp4', '.mov', '.mkv']:
            return filename, "status_video"
        
        # Prüft, ob die Datei dem Pixel-Namensschema entspricht
        if not filename.lower().startswith('pxl_'):
            return filename, "status_not_pixel"

        try:
            # Versucht, die EXIF-Daten zu laden
            exif_dict = piexif.load(original_path)
            date_bytes = exif_dict.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)
            if not date_bytes: return filename, "status_no_exif" # Kein Aufnahmedatum gefunden
            
            # Formatiert das Datum in den gewünschten Zeitstempel um
            date_obj = datetime.strptime(date_bytes.decode("utf-8"), "%Y:%m:%d %H:%M:%S")
            timestamp = date_obj.strftime("%Y%m%d_%H%M%S")
            
            # Extrahiert den Suffix (z.B. .NIGHT, .RAW-01) aus dem Originalnamen
            match = re.compile(r"PXL_\d{8}_\d{9}(.*?)\..{3,4}$", re.IGNORECASE).match(filename)
            suffix = match.group(1) if match else ""
            
            # Baut den neuen Dateinamen zusammen
            new_name = f"{timestamp}{suffix}{ext}"
            
            # Prüft, ob der Name bereits korrekt ist
            return (filename, "status_already_correct") if new_name.lower() == filename.lower() else (new_name, "status_ok")
        except Exception:
            # Fängt alle anderen Fehler beim Lesen der Datei ab
            return filename, "status_read_error"

    def start_processing(self):
        """Startet den eigentlichen Umbenennungs-/Kopierprozess."""
        # Sicherheitsprüfungen
        if not os.path.isdir(self.output_dir.get()):
            messagebox.showerror(self._("error"), self._("select_output_error"))
            return
        if self.source_dir.get() == self.output_dir.get() and not self.copy_instead_of_move.get():
             messagebox.showwarning(self._("warning"), self._("same_folder_warning"))
             return
        # Startet den Prozess im Hintergrund-Thread
        self.show_progress_popup(self._("processing_files"), self.process_files)

    def process_files(self, progress_callback):
        """
        Kopiert oder verschiebt die Dateien, die zum Umbenennen markiert sind.
        Läuft in einem separaten Thread.
        """
        source = self.source_dir.get()
        output = self.output_dir.get()
        to_process = [f for f in self.file_list if f['status_key'] == "status_ok"]
        total_to_process = len(to_process)
        
        for i, item in enumerate(to_process):
            original_path = os.path.join(source, item['original'])
            new_path = os.path.join(output, item['new'])
            try:
                # Prüft, ob eine Datei mit dem neuen Namen bereits existiert, und fügt eine Nummer hinzu
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(item['new'])
                    count = 1
                    while os.path.exists(new_path):
                        new_path = os.path.join(output, f"{base}_{count}{ext}")
                        count += 1
                
                # Führt je nach Auswahl die Kopier- oder Verschiebe-Operation durch
                if self.copy_instead_of_move.get():
                    shutil.copy2(original_path, new_path)
                else:
                    shutil.move(original_path, new_path)
            except Exception as e:
                print(f"Fehler bei der Verarbeitung von {item['original']}: {e}")
            
            # Aktualisiert den Fortschrittsbalken
            if total_to_process > 0:
                progress_callback((i + 1) / total_to_process * 100)
        
        # Zeigt eine Erfolgsmeldung an und aktualisiert die Vorschau
        processed_count = len(to_process)
        message_text = f"{processed_count} {self._('files_processed')}"
        self.master.after(0, lambda: messagebox.showinfo(self._("done"), message_text))
        self.master.after(0, self.start_preview)

    def show_progress_popup(self, title, task_function):
        """
        Zeigt ein "Bitte warten"-Fenster an und führt eine gegebene Funktion (task_function)
        in einem separaten Thread aus, um die GUI nicht zu blockieren.
        """
        popup = Toplevel(self.master)
        popup.title("")
        popup.geometry("300x120")
        popup.configure(bg="#2E2E2E")
        popup.transient(self.master) # Hält das Popup im Vordergrund des Hauptfensters
        popup.grab_set() # Blockiert die Interaktion mit dem Hauptfenster
        
        Label(popup, text=title, style="Header.TLabel").pack(pady=(10,5))
        Label(popup, text=self._("please_wait"), style="TLabel").pack()
        progress = Progressbar(popup, orient="horizontal", length=250, mode="determinate")
        progress.pack(pady=10)
        
        def run_task():
            """Die Funktion, die im Thread ausgeführt wird."""
            try:
                # Übergibt eine Callback-Funktion, um den Fortschrittsbalken aus dem Thread zu aktualisieren
                task_function(lambda v: self.master.after(0, progress.config, {'value': v}))
            finally:
                # Schließt das Popup, wenn der Task beendet ist (auch bei Fehlern)
                self.master.after(0, popup.destroy)
        
        # Startet den Thread
        threading.Thread(target=run_task, daemon=True).start()

# ==============================================================================
# Programmeinstiegspunkt
# ==============================================================================
if __name__ == "__main__":
    """
    Dieser Block wird nur ausgeführt, wenn das Skript direkt gestartet wird
    (und nicht, wenn es als Modul importiert wird).
    """
    root = Tk() # Erstellt das Hauptfenster
    app = RenamerApp(root) # Erstellt eine Instanz unserer Anwendungsklasse
    root.mainloop() # Startet die Ereignisschleife von Tkinter, die auf Benutzerinteraktionen wartet

