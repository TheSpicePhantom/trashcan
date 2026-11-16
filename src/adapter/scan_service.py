from __future__ import annotations

from pathlib import Path

from src.model.analysis import FolderSizeEntry, analyze_immediate_subfolders, sort_by_size_desc


def collect_trash_entries(trash_root: Path) -> list[FolderSizeEntry]:
    if not trash_root.is_dir():
        return []

    entries = list(analyze_immediate_subfolders(trash_root))
    for child in sorted(trash_root.iterdir()):
        if not child.is_file():
            continue
        try:
            size = child.stat().st_size
        except OSError:
            continue
        entries.append(
            FolderSizeEntry(
                path=str(child.resolve()),
                bytes_total=size,
                entry_type="Datei",
            )
        )
    return sort_by_size_desc(entries)