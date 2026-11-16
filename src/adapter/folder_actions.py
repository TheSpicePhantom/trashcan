from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
from pathlib import Path

RECYCLE_BIN_SHELL = "shell:RecycleBinFolder"
RECYCLE_BIN_CLSID = "::{645FF040-5081-101B-9F08-00AA002F954E}"


class FolderActionError(Exception):
    pass


def _is_recycle_bin_path(path: Path) -> bool:
    name = path.name.upper()
    if name == "$RECYCLE.BIN":
        return True
    return "$RECYCLE.BIN" in {part.upper() for part in path.parts}


def _current_user_sid_folder(bin_root: Path) -> Path | None:
    if not bin_root.is_dir():
        return None

    try:
        import win32api
        import win32security
    except ImportError:
        return _first_sid_folder(bin_root)

    try:
        username = win32api.GetUserName()
        sid, _domain, _acc_type = win32security.LookupAccountName(None, username)
        sid_str = win32security.ConvertSidToStringSid(sid)
    except OSError:
        return _first_sid_folder(bin_root)

    candidate = bin_root / sid_str
    if candidate.is_dir():
        return candidate
    return _first_sid_folder(bin_root)


def _first_sid_folder(bin_root: Path) -> Path | None:
    for child in sorted(bin_root.iterdir()):
        if child.is_dir() and child.name.upper().startswith("S-"):
            return child
    return None


def _open_recycle_bin_in_shell(drive: str | None) -> None:
    last_error: OSError | None = None
    for target in (RECYCLE_BIN_SHELL, RECYCLE_BIN_CLSID):
        try:
            os.startfile(target)  # type: ignore[attr-defined]
            return
        except OSError as err:
            last_error = err

    try:
        subprocess.Popen(["explorer.exe", RECYCLE_BIN_SHELL], close_fds=True)
        return
    except OSError as err:
        last_error = err

    if drive:
        bin_root = Path(f"{drive}\\$RECYCLE.BIN")
        sid_folder = _current_user_sid_folder(bin_root)
        if sid_folder is not None:
            # Explorer mit /root zeigt versteckte $R-Dateien statt leerer Ansicht.
            arg = f'/root,"{sid_folder}"'
            subprocess.Popen(["explorer.exe", arg], close_fds=True)
            return

    message = "Papierkorb konnte nicht im Explorer geöffnet werden."
    if last_error is not None:
        message = f"{message} ({last_error})"
    raise FolderActionError(message)


def open_in_explorer(path: str) -> None:
    if not path:
        raise FolderActionError("Kein Pfad angegeben.")

    target = Path(path)
    if _is_recycle_bin_path(target):
        _open_recycle_bin_in_shell(target.drive)
        return

    if not target.is_dir():
        raise FolderActionError("Pfad existiert nicht oder ist kein Ordner.")

    os.startfile(path)  # type: ignore[attr-defined]


def _empty_recycle_bin_on_drive(path: Path) -> None:
    if not path.drive:
        raise FolderActionError("Kein Laufwerk für Papierkorb erkannt.")

    drive_root = f"{path.drive}\\"
    shell32 = ctypes.windll.shell32
    # Kein zweites Windows-Dialogfenster – Bestätigung erfolgt in der App.
    flags = 0x00000001 | 0x00000002  # SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI
    result = shell32.SHEmptyRecycleBinW(None, drive_root, flags)
    if result != 0:
        raise FolderActionError(f"Papierkorb konnte nicht geleert werden (Fehlercode {result}).")


def _delete_directory_contents(path: Path) -> None:
    if not path.is_dir():
        raise FolderActionError("Pfad ist kein Ordner.")

    if path.drive and str(path).rstrip("\\/") == f"{path.drive}\\":
        raise FolderActionError("Laufwerkswurzel darf nicht geleert werden.")

    for child in path.iterdir():
        try:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        except OSError as err:
            raise FolderActionError(f"Fehler bei „{child}“: {err}") from err


def delete_contents(path: str, entry_type: str) -> None:
    target = Path(path)

    if entry_type == "Datei":
        if not target.is_file():
            raise FolderActionError("Datei existiert nicht mehr.")
        target.unlink()
        return

    if entry_type == "Papierkorb" or _is_recycle_bin_path(target):
        _empty_recycle_bin_on_drive(target)
        return

    _delete_directory_contents(target)