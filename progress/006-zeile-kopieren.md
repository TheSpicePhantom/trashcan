# Schritt 006: Zeile kopieren

## Ziel

Im Kontextmenü zusätzlich die komplette Tabellenzeile als lesbarer Text (Ort, Größe, Typ) in die Zwischenablage kopieren.

## Umsetzung

- Menüpunkt „Zeile kopieren“ unter „Kopieren“.
- Textformat: mehrzeilig mit Ort, Größe (GB/MB/Bytes) und Typ.
- Hilfsmethode `_clipboard_set` für Pfad- und Zeilenkopie.

## Betroffene Dateien

- `src/view/main_window.py`

## Prüfung

- Nicht durchgeführt: manueller Rechtsklick-Test.

## Ergebnis

Zwei Kopier-Varianten: nur Pfad vs. vollständige Zeileninfo.

## Offene Punkte

- Keine.