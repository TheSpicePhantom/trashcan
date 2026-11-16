from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

FolderEntryType = Literal["Ordner", "Datei", "Papierkorb"]


@dataclass(frozen=True, slots=True)
class FolderSizeEntry:
    path: str
    bytes_total: int
    entry_type: FolderEntryType

    @property
    def size_mb(self) -> float:
        return round(self.bytes_total / (1024 * 1024), 2)

    @property
    def size_gb(self) -> float:
        return round(self.bytes_total / (1024 * 1024 * 1024), 2)


def directory_size_bytes(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        if path.is_file():
            try:
                total += path.stat().st_size
            except OSError:
                continue
    return total


def analyze_immediate_subfolders(root: Path) -> list[FolderSizeEntry]:
    if not root.is_dir():
        return []

    entries: list[FolderSizeEntry] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        entries.append(
            FolderSizeEntry(
                path=str(child.resolve()),
                bytes_total=directory_size_bytes(child),
                entry_type="Ordner",
            )
        )
    return entries


def sort_by_size_desc(entries: Iterable[FolderSizeEntry]) -> list[FolderSizeEntry]:
    return sorted(entries, key=lambda e: e.bytes_total, reverse=True)