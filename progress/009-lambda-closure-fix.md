# Schritt 009: Tkinter-Lambda-Closures

## Ziel

`NameError` bei Speicher-Details beheben: Exception-Variablen in `after(0, lambda …)` korrekt einfangen.

## Umsetzung

- Python löscht `except … as err` beim Verlassen des Blocks; spätes Lambda findet `err` nicht mehr.
- Lösung: Wert in lokale Variable kopieren oder Default-Argument im Lambda (`lambda m=message: …`).
- Gleiches Muster in `main_window.py` für Scan- und Lösch-Callbacks vorbeugend angepasst.

## Betroffene Dateien

- `src/view/details_dialog.py`
- `src/view/main_window.py`

## Prüfung

- Nicht durchgeführt: manueller Speicher-Details-Dialog.

## Ergebnis

Fehler aus Hintergrundthreads erscheinen zuverlässig in der UI.

## Offene Punkte

- Keine.