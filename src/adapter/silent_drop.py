from __future__ import annotations

import ctypes
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.adapter.archive_drop import archive_paths_into_trash
from src.adapter.config_store import config_file_path, load_trash_settings


def _log_line(message: str) -> None:
    log_file = config_file_path().parent / "drop.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(f"{stamp} {message}\n")


def _message_box(title: str, text: str) -> None:
    if sys.platform != "win32":
        print(f"{title}: {text}", file=sys.stderr)
        return
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)  # MB_ICONERROR


def run_silent_drops(paths: list[Path]) -> int:
    settings = load_trash_settings()
    if settings.trash_location is None:
        _message_box(
            "Trashcan",
            "Kein Mülleimer konfiguriert.\n\n"
            "Bitte Trashcan einmal normal starten und unter „Öffnen …“ den Mülleimer-Ordner wählen.",
        )
        _log_line("FEHLER: Kein Mülleimer konfiguriert (Drag & Drop abgebrochen).")
        return 2

    results, errors = archive_paths_into_trash(paths, settings.trash_location)

    for result in results:
        _log_line(f"OK: {result.source} -> {result.zip_path}")

    for error in errors:
        _log_line(f"FEHLER: {error}")

    if errors and not results:
        _log_line("Drop fehlgeschlagen (keine ZIP erstellt).")
        return 1

    if errors:
        _log_line(f"Teilweise erfolgreich ({len(results)} OK, {len(errors)} Fehler).")
        return 1

    return 0 if results else 1