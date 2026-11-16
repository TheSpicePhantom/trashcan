from __future__ import annotations

import os
import re
from pathlib import Path

from src.model.analysis import FolderSizeEntry, directory_size_bytes

_DRIVE_FROM_PATH = re.compile(r"^([A-Za-z]):[\\/]")


def _item_size_bytes(item) -> int:
    try:
        size = int(item.Size)
    except (TypeError, ValueError, AttributeError):
        size = 0

    if size > 0:
        return size

    try:
        path = item.Path
    except AttributeError:
        return 0

    if not path or not os.path.isfile(path):
        return 0

    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def _drive_from_path(path: str) -> str | None:
    match = _DRIVE_FROM_PATH.match(path)
    if not match:
        return None
    return f"{match.group(1).upper()}:"


def _sizes_from_shell_com_by_drive() -> dict[str, int]:
    import win32com.client  # type: ignore[import-untyped]

    shell = win32com.client.Dispatch("Shell.Application")
    recycle = shell.NameSpace(0x0A)
    if recycle is None:
        return {}

    by_drive: dict[str, int] = {}
    items = recycle.Items()
    count = int(items.Count)
    for index in range(count):
        item = items.Item(index)
        size = _item_size_bytes(item)
        if size <= 0:
            continue
        try:
            path = item.Path
        except AttributeError:
            continue
        drive = _drive_from_path(str(path))
        if drive is None:
            continue
        by_drive[drive] = by_drive.get(drive, 0) + size
    return by_drive


def list_recycle_bin_roots() -> list[Path]:
    roots: list[Path] = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = Path(f"{letter}:/")
        if not drive.exists():
            continue
        bin_root = drive / "$RECYCLE.BIN"
        if bin_root.is_dir():
            roots.append(bin_root)
    return roots


def recycle_bin_location_entries() -> list[FolderSizeEntry]:
    try:
        import win32com.client  # type: ignore[import-untyped]  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Papierkorb-Analyse benötigt pywin32. Installiere mit: pip install pywin32"
        ) from exc

    com_by_drive: dict[str, int] = {}
    try:
        com_by_drive = _sizes_from_shell_com_by_drive()
    except Exception:
        pass

    entries: list[FolderSizeEntry] = []
    seen_drives: set[str] = set()

    for bin_root in sorted(list_recycle_bin_roots(), key=lambda p: str(p).upper()):
        drive_key = f"{bin_root.drive}".upper()
        seen_drives.add(drive_key)
        size = directory_size_bytes(bin_root)
        if size <= 0:
            size = com_by_drive.get(drive_key, 0)

        entries.append(
            FolderSizeEntry(
                path=str(bin_root),
                bytes_total=size,
                entry_type="Papierkorb",
            )
        )

    for drive in sorted(com_by_drive):
        if drive in seen_drives:
            continue
        size = com_by_drive[drive]
        if size <= 0:
            continue
        entries.append(
            FolderSizeEntry(
                path=f"{drive}\\$RECYCLE.BIN",
                bytes_total=size,
                entry_type="Papierkorb",
            )
        )

    return entries


def recycle_bin_size_bytes() -> int:
    return sum(entry.bytes_total for entry in recycle_bin_location_entries())