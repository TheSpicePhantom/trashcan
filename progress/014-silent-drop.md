# Schritt 014: Stiller Drag & Drop auf die EXE

## Ziel

Drop auf Icon/EXE ohne Hauptfenster; Komprimierung im Hintergrund.

## Umsetzung

- `silent_drop.py`: Mülleimer aus Config laden, archivieren, in `drop.log` protokollieren.
- `trashcan.py`: Bei Pfad-Argumenten ohne `--gui` nur stiller Modus, sofort beenden.
- Fehler ohne Konfiguration: einmaliges Windows-MessageBox (kein Tk-Fenster).
- GUI-Start nur noch ohne Drop-Argumente (Doppelklick).

## Betroffene Dateien

- `src/adapter/silent_drop.py` – neu
- `trashcan.py`
- `src/view/main_window.py`
- `src/adapter/__init__.py`

## Prüfung

- Nicht durchgeführt: Drop-Test auf gebauter EXE.

## Ergebnis

Drag & Drop auf die EXE erzeugt ZIP(s) ohne sichtbares Trashcan-Fenster.

## Offene Punkte

- Log: `%APPDATA%\Trashcan\drop.log`
- Mit GUI trotz Drop: `Trashcan.exe --gui` (optional).
- Keine.