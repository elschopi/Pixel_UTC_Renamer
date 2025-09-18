import os
import re
import shutil
import piexif
import threading
from datetime import datetime
from tkinter import Tk, Label, Button, Frame, filedialog, Toplevel, Listbox, Scrollbar, Checkbutton
from tkinter import messagebox, StringVar, BooleanVar, font as tkfont
from tkinter.ttk import Progressbar, Style

# ==============================================================================
# Hauptanwendungsklasse
# ==============================================================================
class RenamerApp:
    def __init__(self, master):
        self.master = master
        master.title("Pixel Photo Renamer v1.0")
        master.geometry("800x600")
        master.minsize(600, 400)
        master.configure(bg="#2E2E2E")

        # --- Style Konfiguration ---
        self.setup_styles()

        # --- Variablen ---
        self.source_dir = StringVar()
        self.output_dir = StringVar()
        self.copy_instead_of_move = BooleanVar(value=True)
        self.file_list = []

        # --- GUI Elemente erstellen ---
        self.create_widgets()

    def setup_styles(self):
        """Konfiguriert die Styles für die Tkinter-Widgets."""
        style = Style()
        style.theme_use('clam')
        
        # Style für Buttons
        style.configure("TButton",
                        background="#555555",
                        foreground="white",
                        bordercolor="#666666",
                        lightcolor="#666666",
                        darkcolor="#2E2E2E",
                        padding=10,
                        font=('Segoe UI', 10))
        style.map("TButton",
                  background=[('active', '#666666')],
                  foreground=[('active', 'white')])

        # Style für Labels
        style.configure("TLabel", background="#2E2E2E", foreground="white", font=('Segoe UI', 10))
        style.configure("Header.TLabel", font=('Segoe UI', 12, 'bold'))
        
        # Style für Frames
        style.configure("TFrame", background="#2E2E2E")

    def create_widgets(self):
        """Erstellt und platziert alle GUI-Elemente im Hauptfenster."""
        main_frame = Frame(self.master, style="TFrame", padding=(20, 10))
        main_frame.pack(fill="both", expand=True)

        # --- Ordnerauswahl ---
        folder_frame = Frame(main_frame, style="TFrame")
        folder_frame.pack(fill="x", pady=5)

        Label(folder_frame, text="1. Quellordner (mit den Pixel-Bildern):", style="Header.TLabel").pack(anchor="w")
        Button(folder_frame, text="Quellordner auswählen...", command=self.select_source_dir, style="TButton").pack(fill="x", pady=(5, 10))
        self.source_label = Label(folder_frame, textvariable=self.source_dir, wraplength=700, style="TLabel")
        self.source_label.pack(anchor="w", pady=(0, 10))
        self.source_dir.set("Noch kein Ordner ausgewählt.")

        Label(folder_frame, text="2. Ausgabeordner (wo die umbenannten Bilder landen):", style="Header.TLabel").pack(anchor="w")
        Button(folder_frame, text="Ausgabeordner auswählen...", command=self.select_output_dir, style="TButton").pack(fill="x", pady=(5, 10))
        self.output_label = Label(folder_frame, textvariable=self.output_dir, wraplength=700, style="TLabel")
        self.output_label.pack(anchor="w", pady=(0, 20))
        self.output_dir.set("Noch kein Ordner ausgewählt.")

        # --- Vorschau-Bereich ---
        preview_frame = Frame(main_frame, style="TFrame")
        preview_frame.pack(fill="both", expand=True)

        Label(preview_frame, text="3. Vorschau der Umbenennung:", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        
        list_frame = Frame(preview_frame)
        list_frame.pack(fill="both", expand=True)

        self.listbox = Listbox(list_frame, bg="#3C3C3C", fg="white", selectbackground="#007ACC", borderwidth=0, highlightthickness=0, font=('Consolas', 10))
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # --- Aktionen ---
        action_frame = Frame(main_frame, style="TFrame")
        action_frame.pack(fill="x", pady=(20, 10))

        self.preview_button = Button(action_frame, text="Vorschau erstellen", command=self.start_preview, style="TButton")
        self.preview_button.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.rename_button = Button(action_frame, text="Umbennenung starten", command=self.start_processing, style="TButton", state="disabled")
        self.rename_button.pack(side="left", expand=True, fill="x")

        Checkbutton(main_frame, text="Dateien kopieren statt verschieben (empfohlen)", variable=self.copy_instead_of_move,
                    bg="#2E2E2E", fg="white", selectcolor="#2E2E2E", activebackground="#2E2E2E", activeforeground="white",
                    font=('Segoe UI', 10)).pack(anchor="w", pady=10)


    def select_source_dir(self):
        """Öffnet einen Dialog zur Auswahl des Quellordners."""
        path = filedialog.askdirectory(title="Quellordner auswählen")
        if path:
            self.source_dir.set(path)
            self.listbox.delete(0, "end")
            self.rename_button.config(state="disabled")

    def select_output_dir(self):
        """Öffnet einen Dialog zur Auswahl des Zielordners."""
        path = filedialog.askdirectory(title="Ausgabeordner auswählen")
        if path:
            self.output_dir.set(path)

    def start_preview(self):
        """Startet den Vorschau-Prozess in einem separaten Thread."""
        if not os.path.isdir(self.source_dir.get()):
            messagebox.showerror("Fehler", "Bitte wähle zuerst einen gültigen Quellordner aus.")
            return

        self.listbox.delete(0, "end")
        self.rename_button.config(state="disabled")
        self.show_progress_popup("Durchsuche Dateien...", self.generate_preview)

    def generate_preview(self, progress_callback):
        """Sammelt und analysiert die Dateien für die Vorschau."""
        self.file_list.clear()
        source_path = self.source_dir.get()
        all_files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
        total_files = len(all_files)
        
        for i, filename in enumerate(all_files):
            original_path = os.path.join(source_path, filename)
            new_name, status = self.get_new_filename(original_path)
            self.file_list.append({"original": filename, "new": new_name, "status": status})
            progress_callback((i + 1) / total_files * 100)

        self.master.after(0, self.update_preview_listbox)

    def update_preview_listbox(self):
        """Aktualisiert die Listbox mit den Vorschau-Daten."""
        self.listbox.delete(0, "end")
        
        # Finde die maximale Länge des Original-Dateinamens für die Formatierung
        max_len = 0
        if self.file_list:
             max_len = max(len(f['original']) for f in self.file_list) + 3

        for item in self.file_list:
            # Formatierte Ausgabe für die Listbox
            original_formatted = f"{item['original']:{max_len}}"
            line = f"{original_formatted} -> {item['new']} [{item['status']}]"
            self.listbox.insert("end", line)
            
            # Färbung basierend auf dem Status
            if item['status'] != "OK":
                self.listbox.itemconfig("end", {'fg': '#FFC107'}) # Orange für Warnungen/Fehler
            else:
                 self.listbox.itemconfig("end", {'fg': '#90EE90'}) # Grün für OK

        if any(f['status'] == "OK" for f in self.file_list):
            self.rename_button.config(state="normal")
        else:
            self.rename_button.config(state="disabled")
        
    def get_new_filename(self, original_path):
        """Ermittelt den neuen Dateinamen basierend auf den EXIF-Daten."""
        filename = os.path.basename(original_path)
        
        try:
            exif_dict = piexif.load(original_path)
            aufnahmezeit_bytes = exif_dict.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)
            if not aufnahmezeit_bytes:
                return filename, "Kein EXIF-Datum"

            aufnahmezeit_str = aufnahmezeit_bytes.decode("utf-8")
            aufnahmezeit_obj = datetime.strptime(aufnahmezeit_str, "%Y:%m:%d %H:%M:%S")
            neuer_zeitstempel = aufnahmezeit_obj.strftime("%Y%m%d_%H%M%S")

            suffix_regex = re.compile(r"PXL_\d{8}_\d{9}(.*?)\..{3,4}$", re.IGNORECASE)
            match = suffix_regex.match(filename)
            suffix = match.group(1) if match else ""
            
            dateiendung = os.path.splitext(filename)[1]
            neuer_dateiname = f"{neuer_zeitstempel}{suffix}{dateiendung}"

            if neuer_dateiname.lower() == filename.lower():
                return filename, "Bereits korrekt"

            return neuer_dateiname, "OK"

        except Exception:
            return filename, "Fehler beim Lesen"

    def start_processing(self):
        """Startet den Umbenennungs-/Kopier-Prozess in einem separaten Thread."""
        if not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Fehler", "Bitte wähle zuerst einen gültigen Ausgabeordner aus.")
            return
        if self.source_dir.get() == self.output_dir.get() and not self.copy_instead_of_move.get():
             messagebox.showwarning("Warnung", "Quell- und Zielordner sind identisch. Bitte wähle 'Kopieren' oder einen anderen Ausgabeordner, um Datenverlust zu vermeiden.")
             return
             
        self.show_progress_popup("Verarbeite Dateien...", self.process_files)

    def process_files(self, progress_callback):
        """Führt die eigentliche Umbenennung oder das Kopieren durch."""
        source_path = self.source_dir.get()
        output_path = self.output_dir.get()
        files_to_process = [f for f in self.file_list if f['status'] == "OK"]
        total_files = len(files_to_process)
        
        for i, item in enumerate(files_to_process):
            original_file_path = os.path.join(source_path, item['original'])
            new_file_path = os.path.join(output_path, item['new'])

            try:
                # Stelle sicher, dass der Zielname nicht bereits existiert
                if os.path.exists(new_file_path):
                    # Einfache Logik, um Konflikte zu vermeiden: Füge eine Nummer hinzu
                    base, ext = os.path.splitext(item['new'])
                    count = 1
                    while os.path.exists(new_file_path):
                        new_file_path = os.path.join(output_path, f"{base}_{count}{ext}")
                        count += 1

                if self.copy_instead_of_move.get():
                    shutil.copy2(original_file_path, new_file_path) # copy2 erhält Metadaten
                else:
                    shutil.move(original_file_path, new_file_path)
            except Exception as e:
                print(f"Fehler bei Datei {item['original']}: {e}") # Log für Debugging
            
            progress_callback((i + 1) / total_files * 100)

        self.master.after(0, lambda: messagebox.showinfo("Fertig", f"{total_files} Dateien wurden erfolgreich verarbeitet."))
        self.master.after(0, self.start_preview) # Aktualisiere die Vorschau nach der Operation


    def show_progress_popup(self, title, task_function):
        """Zeigt ein Popup-Fenster mit einem Fortschrittsbalken für langwierige Aufgaben."""
        popup = Toplevel(self.master)
        popup.title(title)
        popup.geometry("300x100")
        popup.configure(bg="#2E2E2E")
        popup.transient(self.master)
        popup.grab_set()

        Label(popup, text="Bitte warten...", style="TLabel").pack(pady=10)
        progress = Progressbar(popup, orient="horizontal", length=250, mode="determinate")
        progress.pack(pady=5)
        
        def update_progress(value):
            progress['value'] = value
            popup.update_idletasks()

        def run_task():
            try:
                task_function(update_progress)
            finally:
                popup.destroy()
        
        # Starte die Aufgabe in einem neuen Thread, um die GUI nicht zu blockieren
        thread = threading.Thread(target=run_task)
        thread.start()

# ==============================================================================
# Skript starten
# ==============================================================================
if __name__ == "__main__":
    root = Tk()
    app = RenamerApp(root)
    root.mainloop()