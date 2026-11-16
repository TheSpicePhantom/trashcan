# Schritt 005: Kontextmenü in der Tabelle

## Ziel

Rechtsklick auf eine Tabellenzeile mit Aktionen Kopieren, Öffnen und Inhalt löschen (mit Bestätigung).

## Umsetzung

- `ttk.Treeview`: Binding `<Button-3>`, Zeile unter dem Cursor auswählen, natives `tk.Menu`.
- **Kopieren**: Pfad in die Zwischenablage.
- **Öffnen**: Explorer via `open_in_explorer` (wie Doppelklick).
- **Inhalt löschen**: `messagebox.askyesno` mit Warnung, Standard „Nein“; danach Löschen im Hintergrundthread.
- Adapter `folder_actions.py`: Ordner-Inhalt per `shutil`/`unlink`; Papierkorb über `SHEmptyRecycleBinW` fürs jeweilige Laufwerk (ohne zweites Windows-Bestätigungsfenster).
- Nach erfolgreichem Löschen: Größe der Zeile neu berechnen, Tabelle und Summe aktualisieren.

## Betroffene Dateien

- `src/view/main_window.py` – Kontextmenü und Ablauf
- `src/adapter/folder_actions.py` – neu
- `src/adapter/__init__.py` – Exporte

## Prüfung

- Durchgeführt: Module-Import erfolgreich.
- Nicht durchgeführt: manuelles Rechtsklick- und Lösch-Szenario.

## Ergebnis

Rechtsklick-Menü mit den drei Aktionen; Löschen nur nach expliziter Bestätigung in der App.

## Offene Punkte

- Beim Löschen großer Ordner kann es je nach Berechtigungen zu Teilfehlern kommen (Fehlermeldung mit Pfad).
- Keine.