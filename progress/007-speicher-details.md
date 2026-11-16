# Schritt 007: Speicher-Details für große Papierkörbe

## Ziel

Große Papierkorb-Werte einordnen und sichtbar machen, was den Speicher auf dem Datenträger belegt.

## Umsetzung

- Adapter `storage_details.py`: physischer Umfang unter dem Pfad, Shell-Größe pro Laufwerk (COM), Aufteilung nach SID-Unterordnern, größte Dateien.
- Dialog `details_dialog.py` mit Zusammenfassung und zwei Tabellen.
- Kontextmenü: „Speicher-Details …“
- Hinweistext, wenn physisch deutlich über Shell liegt (mehrere Benutzer / $RECYCLE.BIN-Rohdaten).

## Betroffene Dateien

- `src/adapter/storage_details.py` – neu
- `src/view/details_dialog.py` – neu
- `src/view/main_window.py` – Menüeintrag

## Prüfung

- Durchgeführt: Import erfolgreich.
- Nicht durchgeführt: Dialog auf E:\$RECYCLE.BIN (in dieser Umgebung kein Zugriff).

## Ergebnis

Nutzer können prüfen, ob ~25 GB real belegt ist und welche SID-/Dateien dominieren.

## Offene Punkte

- Details-Scan bei sehr großen Papierkörben kann einige Sekunden dauern.
- Keine.