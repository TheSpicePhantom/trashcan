# Schritt 010: Umstellung auf Trashcan

## Ziel

Sizer wird zu Trashcan: ein gespeicherter Mülleimer-Ordner, automatische Analyse beim Start, keine System-Papierkörbe mehr.

## Umsetzung

- Modell `TrashCanSettings` für den Mülleimer-Pfad.
- Persistenz unter `%APPDATA%\Trashcan\config.json` via `config_store.py`.
- Scan nur noch `collect_trash_entries` (Unterordner des Mülleimers).
- GUI: Trashcan-Branding, „Mülleimer wählen …“, „Im Explorer öffnen“, „Neu analysieren“.
- Beim Start: gespeicherten Pfad laden und analysieren; ohne Konfiguration Ordnerdialog, speichern, analysieren.
- Neuer Einstieg `trashcan.py`; `sizer.py` leitet nur noch weiter.

## Betroffene Dateien

- `src/model/trash_config.py` – neu
- `src/adapter/config_store.py` – neu
- `src/adapter/scan_service.py` – vereinfacht
- `src/view/main_window.py` – TrashCanApp
- `trashcan.py`, `sizer.py`

## Prüfung

- Nicht durchgeführt: manueller Erststart und erneuter Start mit gespeichertem Pfad.

## Ergebnis

`python trashcan.py` öffnet Trashcan, merkt sich den Mülleimer und analysiert beim Öffnen automatisch.

## Offene Punkte

- `recycle_bin.py` und Papierkorb-Logik in `folder_actions.py` sind Altbestand, derzeit ungenutzt.
- Keine.