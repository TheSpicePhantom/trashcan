# Schritt 013: App-Icon (EXE und Fenster)

## Ziel

`src/icon/icon.jpg` beim Build in ICO wandeln und für PyInstaller-EXE sowie Tkinter-Fenster nutzen.

## Umsetzung

- `src/icon/convert.py`: JPG → multi-size `icon.ico` (Pillow).
- Build: `ensure_icon_ico()` vor PyInstaller, `--icon` und `--add-data` für Laufzeit.
- `src/view/app_icon.py`: `iconbitmap` im Hauptfenster; in der EXE Pfad unter `sys._MEIPASS`.
- Abhängigkeit `Pillow` in `requirements.txt`.

## Betroffene Dateien

- `src/icon/convert.py`, `paths.py`
- `src/view/app_icon.py`, `main_window.py`
- `build.py`, `requirements.txt`

## Prüfung

- Durchgeführt: `ensure_icon_ico()` erzeugt `src/icon/icon.ico`.
- Nicht durchgeführt: erneuter Full-Build mit Icon.

## Ergebnis

Nach `build.cmd` trägt die EXE das Papierkorb-Icon; das Fenster zeigt dasselbe.

## Offene Punkte

- Nach Änderung an `icon.jpg` neu bauen, damit ICO/EXE aktualisiert werden.
- Keine.