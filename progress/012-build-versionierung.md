# Schritt 012: Build-Skript mit Versionierung

## Ziel

Reproduzierbarer EXE-Build mit automatischer Patch-Version (ab 0.1.x) und Kanalwahl alpha/beta/release.

## Umsetzung

- `version.json` speichert `major`, `minor`, `patch` (Start 0.1.0, Patch steigt pro Build).
- `build.py`: Kanal abfragen, Patch erhöhen, `src/version.py` und Windows-`file_version_info` erzeugen, PyInstaller `--onefile --windowed`.
- Ausgabe: `dist/Trashcan.exe` und `dist/Trashcan-<version>.exe`.
- `build.cmd` / aktualisiertes `build_trashcan.ps1` als Starter.
- Fenstertitel zeigt `VERSION` aus `src/version.py`.

## Betroffene Dateien

- `build.py`, `build.cmd`, `build_trashcan.ps1`
- `version.json`, `src/version.py`
- `src/view/main_window.py`

## Prüfung

- Nicht durchgeführt: vollständiger PyInstaller-Lauf (interaktiv).

## Ergebnis

`python build.py` oder `build.cmd` erzeugt eine versionierte Trashcan-EXE.

## Offene Punkte

- Erster Build nach Start fragt Kanal und erzeugt z. B. `0.1.1-alpha`.
- Keine.