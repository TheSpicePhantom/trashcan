# Schritt 015: Icon EXE und Fenster reparieren

## Ziel

Korrektes Papierkorb-Icon in Explorer/EXE und in der Taskleiste/Fensterleiste.

## Umsetzung

- ICO-Erzeugung mit mehreren Auflösungen (`append_images`) plus `icon.png` (256×256) für Tk `iconphoto`.
- `SetCurrentProcessExplicitAppUserModelID` unter Windows (Taskleiste).
- `iconbitmap(default=…)` + `iconphoto` kombiniert.
- Build: Kopie nach `build/trashcan.ico`, `--add-data` für ICO und PNG.
- Frozen-Bundle: Icons unter `src/icon/` in `_MEIPASS`.

## Betroffene Dateien

- `src/icon/convert.py`, `paths.py`, `windows.py`
- `src/view/app_icon.py`, `trashcan.py`
- `build.py`

## Prüfung

- Durchgeführt: ICO/PNG neu erzeugt.
- Nicht durchgeführt: EXE-Neubuild und visueller Check.

## Ergebnis

Nach erneutem `build.cmd` sollten EXE- und Fenster-Icon stimmen.

## Offene Punkte

- Windows cached Explorer-Icons; ggf. Kurz warten oder neuen Dateinamen nutzen.
- Keine.