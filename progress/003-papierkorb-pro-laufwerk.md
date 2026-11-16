# Schritt 003: Papierkorb pro Laufwerk

## Ziel

Statt einer aggregierten Zeile „Papierkorb“ alle physischen Papierkorb-Standorte (`X:\$RECYCLE.BIN`) mit jeweiliger Größe in CSV und Konsole ausgeben.

## Umsetzung

- `list_recycle_bin_roots()` ermittelt vorhandene `$RECYCLE.BIN`-Ordner auf allen Laufwerken A–Z.
- Größe primär per Dateiscan im jeweiligen Ordner; bei 0 Bytes Fallback aus COM-Shell, gruppiert nach Laufwerksbuchstabe aus `item.Path`.
- Zusätzliche COM-Laufwerke ohne sichtbaren Ordner erscheinen als `D:\$RECYCLE.BIN` (synthetischer Pfad).
- `recycle_bin_location_entries()` liefert eine `FolderSizeEntry` pro Standort; View hängt alle an die Ergebnisliste.

## Betroffene Dateien

- `src/adapter/recycle_bin.py` – Aufschlüsselung pro Laufwerk
- `src/view/console.py` – Ausgabe und CSV-Einträge pro Standort
- `src/adapter/__init__.py` – Export `recycle_bin_location_entries`

## Prüfung

- Durchgeführt: `recycle_bin_location_entries()` listet mehrere `X:\$RECYCLE.BIN`-Pfade mit Größen.
- Nicht durchgeführt: CSV-Export manuell geöffnet.

## Ergebnis

In `Ordnergroessen.csv` erscheinen zeilenweise alle Papierkorb-Pfade mit `Typ=Papierkorb`, sortiert zusammen mit Ordnern nach Größe.

## Offene Punkte

- Benutzer-Papierkorb pro Laufwerk nutzt `$RECYCLE.BIN\<SID>`; die Summe liegt auf Laufwerksebene, nicht pro SID-Ordner.
- Keine.