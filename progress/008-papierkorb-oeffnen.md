# Schritt 008: Papierkorb korrekt öffnen

## Ziel

„Öffnen“ bei `$RECYCLE.BIN` soll nicht den leeren Systemordner zeigen, sondern die sichtbaren gelöschten Dateien im Explorer.

## Umsetzung

- Ursache: `$RECYCLE.BIN` ist ein geschützter Systemordner; direktes `os.startfile` wirkt oft leer.
- Stattdessen: virtueller Papierkorb (`shell:RecycleBinFolder` / CLSID), Fallback `explorer.exe`, zuletzt SID-Unterordner mit `explorer /root,…`.
- Statushinweis nach dem Öffnen: Einträge nach ursprünglichem Laufwerk gruppiert.

## Betroffene Dateien

- `src/adapter/folder_actions.py`
- `src/view/main_window.py`

## Prüfung

- Nicht durchgeführt: manueller Explorer-Test.

## Ergebnis

Rechtsklick/Doppelklick „Öffnen“ auf Papierkorb-Zeilen öffnet die Windows-Papierkorb-Ansicht.

## Offene Punkte

- Kein reines „nur Laufwerk C“-Fenster; Windows bietet dafür keine einfache Shell-URL – Sortierung nach Ort im Papierkorb.
- Keine.