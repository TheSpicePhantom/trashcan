from __future__ import annotations

import tkinter as tk
from pathlib import Path

from src.icon.convert import ICON_ICO, ICON_PNG, resolve_icon_ico
from src.icon.paths import icon_directory
from src.icon.windows import apply_windows_app_id


def _apply_photo_icon(root: tk.Tk, path: Path) -> None:
    try:
        photo = tk.PhotoImage(file=str(path))
    except tk.TclError:
        return
    root.iconphoto(True, photo)
    root._trashcan_icon_ref = photo


def apply_window_icon(root: tk.Tk) -> None:
    apply_windows_app_id()
    resolve_icon_ico()

    base = icon_directory()
    ico_path = base / "icon.ico"
    png_path = base / "icon.png"
    if not ico_path.is_file() and ICON_ICO.is_file():
        ico_path = ICON_ICO
    if not png_path.is_file() and ICON_PNG.is_file():
        png_path = ICON_PNG

    if ico_path.is_file():
        try:
            root.iconbitmap(default=str(ico_path.resolve()))
        except tk.TclError:
            pass

    if png_path.is_file():
        _apply_photo_icon(root, png_path.resolve())