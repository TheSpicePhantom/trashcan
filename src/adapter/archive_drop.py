from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class ArchiveDropError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class ArchiveResult:
    source: Path
    zip_path: Path


def _safe_stem(path: Path) -> str:
    name = path.name or "drop"
    for char in '<>:"/\\|?*':
        name = name.replace(char, "_")
    return name.strip() or "drop"


def _unique_zip_path(trash_root: Path, stem: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = trash_root / f"{stem}_{stamp}.zip"
    counter = 0
    while candidate.exists():
        counter += 1
        candidate = trash_root / f"{stem}_{stamp}_{counter}.zip"
    return candidate


def _write_zip(source: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        if source.is_file():
            archive.write(source, arcname=source.name)
            return

        if not source.is_dir():
            raise ArchiveDropError(f"Keine Datei oder kein Ordner: {source}")

        for file_path in source.rglob("*"):
            if not file_path.is_file():
                continue
            arcname = file_path.relative_to(source.parent)
            archive.write(file_path, arcname=str(arcname))


def _remove_source(source: Path) -> None:
    if source.is_file():
        source.unlink()
        return
    if source.is_dir():
        shutil.rmtree(source)


def archive_into_trash(source: Path, trash_root: Path) -> ArchiveResult:
    if not trash_root.is_dir():
        raise ArchiveDropError(f"Mülleimer existiert nicht: {trash_root}")
    if not source.exists():
        raise ArchiveDropError(f"Quelle existiert nicht: {source}")

    resolved = source.resolve()
    trash_resolved = trash_root.resolve()
    if resolved == trash_resolved or trash_resolved in resolved.parents:
        raise ArchiveDropError("Der Mülleimer kann nicht in sich selbst archiviert werden.")

    zip_path = _unique_zip_path(trash_resolved, _safe_stem(resolved))
    try:
        _write_zip(resolved, zip_path)
        _remove_source(resolved)
    except Exception as err:
        if zip_path.exists():
            try:
                zip_path.unlink()
            except OSError:
                pass
        raise ArchiveDropError(str(err)) from err

    return ArchiveResult(source=resolved, zip_path=zip_path)


def archive_paths_into_trash(paths: list[Path], trash_root: Path) -> tuple[list[ArchiveResult], list[str]]:
    results: list[ArchiveResult] = []
    errors: list[str] = []

    for raw in paths:
        source = Path(raw)
        try:
            results.append(archive_into_trash(source, trash_root))
        except (ArchiveDropError, OSError) as err:
            errors.append(f"{source}: {err}")

    return results, errors