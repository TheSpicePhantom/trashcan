# Schritt 004: GUI-Tabelle statt CSV

## Ziel

Ergebnisse in einer grafischen Tabelle anzeigen; CSV-Export und Konsolenfluss entfernen.

## Umsetzung

- Neues Hauptfenster `SizerApp` in `src/view/main_window.py`: Toolbar (Ordnerwahl, Papierkorb-Checkbox, Analysieren), `ttk.Treeview` mit Spalten Ordner/MB/GB/Bytes/Typ, Scrollbars, Statuszeile.
- Analyse im Hintergrundthread, Fortschrittsbalken während des Laufens.
- Spaltenköpfe klickbar zum Sortieren; Doppelklick öffnet den Pfad im Explorer.
- Orchestrierung in `src/adapter/scan_service.py`.
- Entfernt: `export_csv.py`, `run_options.py`, `filesystem.py`, `console.py`.

## Betroffene Dateien

- `src/view/main_window.py` – neu
- `src/adapter/scan_service.py` – neu
- `src/view/__init__.py`, `sizer.py` – Einstieg auf GUI
- `src/adapter/__init__.py` – bereinigt
- Gelöscht: CSV-, Dialog- und Konsolenmodule

## Prüfung

- Durchgeführt: Import `from src.view.main_window import run` erfolgreich.
- Nicht durchgeführt: manueller GUI-Lauf.

## Ergebnis

Start mit `python sizer.py` öffnet ein durchgängiges Fenster mit Tabelle; keine `Ordnergroessen.csv` mehr.

## Offene Punkte

- Kein Excel-/CSV-Export mehr; bei Bedarf später als optionaler Button.
- Keine.