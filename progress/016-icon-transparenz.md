# Schritt 016: Transparentes Icon aus icon_256x256.jpg

## Ziel

Neues Quellbild nutzen; Schachbrett-Hintergrund aus JPG entfernen, echte Alpha-Kanäle in PNG/ICO.

## Umsetzung

- Quelle: `src/icon/icon_256x256.jpg` (Fallback PNG/`icon.jpg`).
- Flood-Fill vom Bildrand: weiße/graue Checkerboard-Farben → Alpha 0.
- ICO und `icon.png` (256×256) mit Transparenz für EXE, Taskleiste und Tk.

## Betroffene Dateien

- `src/icon/convert.py`

## Prüfung

- Durchgeführt: PNG mit RGBA, Randpixel transparent.
- Nicht durchgeführt: visueller EXE-Check nach Rebuild.

## Ergebnis

Nach `build.cmd` Icon ohne grauen Kasten im Explorer/Fenster.

## Offene Punkte

- PNG-Quelle mit echtem Alpha ist noch besser als JPG + Entfernung.
- Keine.