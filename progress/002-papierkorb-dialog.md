# Schritt 002: Papierkorb sichtbar machen

## Ziel

Papierkorb-Option und Ergebniszeile zuverlässig anzeigen; Papierkorb-Größe robuster ermitteln.

## Umsetzung

- Neuer Startdialog `pick_run_options()` mit Checkbox „Papierkorb mit analysieren“ (standardmäßig aktiviert) statt versteckter Konsolenfrage nach dem Ordnerdialog.
- Nur Papierkorb: Checkbox an, ohne Ordnerwahl möglich.
- Papierkorb-Größe: COM-Enumeration per Index; bei `Size == 0` Fallback über `item.Path` und Dateisystem; bei COM-Total 0 Scan von `$RECYCLE.BIN` auf allen Laufwerken.
- Konsolenausgabe der Papierkorb-Zeile vor dem CSV-Export.

## Betroffene Dateien

- `src/adapter/run_options.py` – neuer Dialog
- `src/adapter/recycle_bin.py` – robustere Größenberechnung
- `src/view/console.py` – nutzt Startdialog
- `src/adapter/__init__.py` – Exporte ergänzt

## Prüfung

- Durchgeführt: `recycle_bin_size_bytes()` liefert auf dem Entwicklungsrechner einen Wert > 0 (COM).
- Nicht durchgeführt: manueller GUI-Test des neuen Dialogs.

## Ergebnis

Beim Start ist die Papierkorb-Option im Fenster sichtbar; in der CSV erscheint weiterhin eine Zeile `Typ=Papierkorb`.

## Offene Punkte

- `$RECYCLE.BIN`-Scan kann bei vielen Dateien länger dauern als COM (nur Fallback).
- Keine.