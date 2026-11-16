from __future__ import annotations

import sys
from pathlib import Path

from src.icon.convert import ICON_ICO, ICON_PNG


def icon_directory() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS) / "src" / "icon"
        if base.is_dir():
            return base
    return ICON_ICO.parent


def icon_path_for_runtime() -> Path | None:
    directory = icon_directory()
    for name in ("icon.ico", "icon.png"):
        candidate = directory / name
        if candidate.is_file():
            return candidate.resolve()
    if ICON_ICO.is_file():
        return ICON_ICO.resolve()
    if ICON_PNG.is_file():
        return ICON_PNG.resolve()
    return None