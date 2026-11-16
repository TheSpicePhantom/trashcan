# Schritt 001: Python-Port des Sizer-Tools

## Ziel

Die Funktionalität von `sizer.ps1` (Unterordner-Größen, optional Papierkorb, CSV auf dem Desktop) in Python ohne PowerShell/STA-Umwege bereitstellen.

## Umsetzung

- Model: Rekursive Größenberechnung und Datentyp `FolderSizeEntry` in `src/model/analysis.py`.
- Adapter: Ordnerdialog (tkinter), Papierkorb (pywin32/COM), CSV-Export und `os.startfile` unter `src/adapter/`.
- View: Konsolenfluss analog zum Skript in `src/view/console.py`.
- Einstieg: `sizer.py` als Composition Root.
- Abhängigkeit `pywin32` nur für Windows/Papierkorb in `requirements.txt`.

## Betroffene Dateien

- `sizer.py` – Startskript
- `requirements.txt` – pywin32 (Windows)
- `src/model/analysis.py` – Fachlogik
- `src/adapter/filesystem.py`, `recycle_bin.py`, `export_csv.py` – externe Anbindung
- `src/view/console.py` – Ablauf und Ausgabe

## Prüfung

- Durchgeführt: `python -c "from src.view.console import run"` im Projektverzeichnis – Import erfolgreich.
- Nicht durchgeführt: End-to-end-Lauf mit Ordnerdialog und Papierkorb (interaktiv/GUI).

## Ergebnis

Start mit `python sizer.py` aus der Projektwurzel. Verhalten entspricht dem PowerShell-Skript; Ordnerwahl per tkinter-Dialog.

## Offene Punkte

- `sizer.ps1` bleibt unverändert im Repo; bei Bedarf entfernen oder durch README-Hinweis ersetzen.
- Papierkorb ohne `pip install pywin32` schlägt mit klarer Meldung fehl.