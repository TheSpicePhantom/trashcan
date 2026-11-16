# Trashcan

Persönlicher **Mülleimer-Ordner** für Windows: Inhalte analysieren, per Drag & Drop als ZIP archivieren und verwalten. Das Projekt entstand als Python-Nachfolger von **Sizer** (`sizer.ps1`) und wurde schrittweise zur Desktop-App **Trashcan** ausgebaut.

## Funktionen (aktuell)

- **Mülleimer-Ordner** wählen und in `%APPDATA%\Trashcan\config.json` speichern
- **Analyse** der Unterordner und Dateien (ZIPs) im Mülleimer – Tabelle mit Größen, sortierbar
- **Drag & Drop auf die EXE**: still komprimieren → ZIP im Mülleimer, Quelle entfernen, **kein Fenster**
- **Drag & Drop ins geöffnete Fenster**: Archivierung mit Fortschrittsanzeige
- **Kontextmenü** in der Tabelle: Kopieren, Zeile kopieren, Öffnen, Speicher-Details, Inhalt löschen (mit Bestätigung)
- **EXE-Build** mit Versionierung (alpha / beta / release), ab Zeile **0.1.x**

## Schnellstart

```text
pip install -r requirements.txt
python trashcan.py
```

Alternativ: `python sizer.py` (leitet auf Trashcan weiter).

### Stiller Drop (nach Build)

Desktop-Verknüpfung auf `dist\Trashcan.exe` oder `Trashcan.cmd` – Dateien/Ordner aufs Icon ziehen. Log: `%APPDATA%\Trashcan\drop.log`.

### EXE bauen

```text
build.cmd
```

Fragt **alpha / beta / release**, erhöht die Patch-Version in `version.json`, baut `dist\Trashcan.exe` und `dist\Trashcan-<version>.exe`. Icon aus `src/icon/icon_256x256.jpg` (transparenter Hintergrund).

## Architektur (Model / View / Adapter)

```text
src/
  model/     … Fachlogik (Größen, TrashCanSettings)
  adapter/   … Config, ZIP, stilles Drop, Ordneraktionen
  view/      … Tkinter-GUI, Icon, Drag & Drop
  icon/      … Icon-Konvertierung (ICO/PNG)
trashcan.py  … Composition Root
build.py     … Versionierung + PyInstaller
```

## Abhängigkeiten

- Windows, Python 3.11+
- `pywin32`, `windnd` (Windows), `Pillow` (Icon)
- Build: `pyinstaller`

---

## Projektverlauf (Zusammenfassung der `progress/`-Dokumentation)

Die einzelnen Schritte liegen weiterhin als Detaildateien unter `progress/001-…` bis `016-…`. Hier die inhaltliche Gesamtfassung.

| Nr. | Thema | Kurzüberblick |
|-----|--------|----------------|
| **001** | Python-Port | `sizer.ps1` → Python (Model/View/Adapter), Papierkorb per COM, CSV |
| **002** | Papierkorb-Dialog | Checkbox im Startdialog statt Konsolenfrage; Papierkorb standardmäßig an |
| **003** | Papierkorb pro Laufwerk | Zeilen pro `X:\$RECYCLE.BIN` statt einer Summenzeile |
| **004** | GUI-Tabelle | CSV entfernt; `ttk.Treeview`, Hintergrund-Scan, Sortierung |
| **005** | Kontextmenü | Kopieren, Öffnen, Inhalt löschen (mit Bestätigung) |
| **006** | Zeile kopieren | Pfad vs. mehrzeilige Zeileninfo (Ort, Größe, Typ) |
| **007** | Speicher-Details | Dialog: physisch vs. Shell, SIDs, größte Dateien |
| **008** | Papierkorb öffnen | Shell-Ansicht statt leerem `$RECYCLE.BIN`-Ordner |
| **009** | Lambda-Closures | `NameError` bei Tk-`after` + Exception-Variable behoben |
| **010** | Trashcan | Fokus auf einen konfigurierbaren Mülleimer; Auto-Analyse beim Start |
| **011** | Drag & Drop → ZIP | `archive_drop.py`, Dateien im Mülleimer sichtbar |
| **012** | Build-Versionierung | `build.py`, `version.json`, Kanalwahl, PyInstaller-EXE |
| **013** | App-Icon | JPG → ICO, EXE- und Fenster-Icon |
| **014** | Silent Drop | Drop auf EXE ohne GUI; `drop.log` |
| **015** | Icon-Fix | Multi-ICO, AppUserModelID, `iconphoto`, Bundle in EXE |
| **016** | Icon-Transparenz | `icon_256x256.jpg`, Checkerboard per Flood-Fill → Alpha |

### Evolution in einem Satz

Von **Sizer** (Ordnergrößen + Windows-Papierkorb, CSV) über **GUI und Papierkorb-Details** zu **Trashcan** (eigener Mülleimer, Tabelle, Kontextmenü), dann **ZIP per Drag & Drop**, **stille EXE-Drops**, **versionierte Builds** und **transparentes Icon**.

### Bekannte Altbestände / Hinweise

- `recycle_bin.py` und Teile der Papierkorb-Logik in `folder_actions.py` stammen aus der Sizer-Phase und sind im Trashcan-Hauptfluss nicht mehr aktiv.
- `sizer.ps1` kann im Repo noch liegen; Einstieg ist `trashcan.py`.
- Explorer-Icon-Cache kann nach Icon-/EXE-Wechsel kurz veraltet wirken → EXE mit neuem Versionsnamen oder neu anmelden.

### Offene Ideen (aus den Fortschrittsdateien)

- Optional wieder CSV/Export aus der Tabelle
- Papierkorb nur noch relevant, falls Sizer-Funktionen reaktiviert werden
- Icon: PNG mit echtem Alpha als Quelle ist robuster als JPG + Hintergrundentfernung

---

## Lizenz / Hinweis

Privates Projekt. Für Bugs und Tests: nach Änderungen an Icon oder Packaging `build.cmd` erneut ausführen.