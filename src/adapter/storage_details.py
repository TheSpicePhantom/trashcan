from __future__ import annotations

import heapq
from dataclasses import dataclass
from pathlib import Path

from src.adapter.recycle_bin import _sizes_from_shell_com_by_drive
from src.model.analysis import directory_size_bytes


@dataclass(frozen=True, slots=True)
class StorageDetails:
    path: str
    physical_bytes: int
    shell_bytes: int | None
    sid_breakdown: tuple[tuple[str, int], ...]
    largest_files: tuple[tuple[str, int], ...]


def _drive_key(path: Path) -> str | None:
    if not path.drive:
        return None
    return f"{path.drive}".upper()


def _is_recycle_bin(path: Path) -> bool:
    return path.name.upper() == "$RECYCLE.BIN"


def _sid_breakdown(bin_root: Path) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for child in sorted(bin_root.iterdir()):
        if not child.is_dir():
            continue
        rows.append((child.name, directory_size_bytes(child)))
    rows.sort(key=lambda item: item[1], reverse=True)
    return rows


def _largest_files(root: Path, limit: int = 15) -> list[tuple[str, int]]:
    heap: list[tuple[int, str]] = []
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        try:
            size = file_path.stat().st_size
        except OSError:
            continue
        if len(heap) < limit:
            heapq.heappush(heap, (size, str(file_path)))
        elif size > heap[0][0]:
            heapq.heapreplace(heap, (size, str(file_path)))

    heap.sort(reverse=True)
    return [(path, size) for size, path in heap]


def collect_storage_details(path: str, entry_type: str) -> StorageDetails:
    target = Path(path)
    physical = 0
    shell_bytes: int | None = None
    sid_rows: list[tuple[str, int]] = []
    largest: list[tuple[str, int]] = []

    if target.is_dir():
        physical = directory_size_bytes(target)

    if entry_type == "Papierkorb" or _is_recycle_bin(target):
        drive = _drive_key(target)
        if drive:
            shell_bytes = _sizes_from_shell_com_by_drive().get(drive, 0)
        if _is_recycle_bin(target):
            sid_rows = _sid_breakdown(target)
            largest = _largest_files(target)
    elif target.is_dir():
        for child in sorted(target.iterdir()):
            if child.is_dir():
                sid_rows.append((str(child), directory_size_bytes(child)))
        sid_rows.sort(key=lambda item: item[1], reverse=True)
        largest = _largest_files(target)

    return StorageDetails(
        path=path,
        physical_bytes=physical,
        shell_bytes=shell_bytes,
        sid_breakdown=tuple(sid_rows),
        largest_files=tuple(largest),
    )