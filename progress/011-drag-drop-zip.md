# Schritt 011: Drag & Drop → ZIP im Mülleimer

## Ziel

Eigenständige Trashcan-Datei mit Drag & Drop: Datei/Ordner zippen, ins Mülleimer-Verzeichnis legen, Quelle entfernen.

## Umsetzung

- `archive_drop.py`: ZIP mit Zeitstempel, Quelle nach Erfolg löschen.
- Drop auf laufendes Fenster via `windnd`.
- Drop auf Icon/Verknüpfung: Pfade als `sys.argv` in `trashcan.py`.
- `Trashcan.cmd` und `build_trashcan.ps1` für Desktop-Verknüpfung bzw. `Trashcan.exe`.
- Scan zeigt ZIPs und Dateien im Mülleimer (`Typ=Datei`).

## Betroffene Dateien

- `src/adapter/archive_drop.py`, `scan_service.py`, `folder_actions.py`
- `src/view/drop_support.py`, `main_window.py`
- `trashcan.py`, `Trashcan.cmd`, `build_trashcan.ps1`, `requirements.txt`

## Prüfung

- Durchgeführt: `pip install windnd`, Import erfolgreich.
- Nicht durchgeführt: EXE-Build und Icon-Drop.

## Ergebnis

Drag & Drop (Fenster oder Verknüpfung) erzeugt ZIPs im konfigurierten Mülleimer und aktualisiert die Tabelle.

## Offene Punkte

- Einmalig `pip install -r requirements.txt`.
- Für Icon-Drop: `Trashcan.cmd` oder `dist\Trashcan.exe` als Verknüpfung verwenden.