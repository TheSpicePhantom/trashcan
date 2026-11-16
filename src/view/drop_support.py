from __future__ import annotations

from collections.abc import Callable


def hook_drop_files(widget, on_paths: Callable[[list[str]], None]) -> bool:
    try:
        import windnd
    except ImportError:
        return False

    def _callback(files: list[bytes]) -> None:
        decoded = [item.decode("utf-8") if isinstance(item, bytes) else str(item) for item in files]
        on_paths(decoded)

    windnd.hook_dropfiles(widget, func=_callback)
    return True