from __future__ import annotations

import sys

APP_USER_MODEL_ID = "Trashcan.Personal.Muelleimer.1"


def apply_windows_app_id() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except OSError:
        pass