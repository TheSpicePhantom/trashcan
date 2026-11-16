"""Trashcan – persönlicher Mülleimer (Composition Root)."""

from __future__ import annotations

import sys
from pathlib import Path


def _drops_from_argv(argv: list[str]) -> list[Path]:
    drops: list[Path] = []
    for argument in argv:
        if argument.startswith("-"):
            continue
        candidate = Path(argument.strip('"').strip("'"))
        if candidate.exists():
            drops.append(candidate)
    return drops


def main() -> int:
    from src.icon.windows import apply_windows_app_id

    apply_windows_app_id()

    argv = sys.argv[1:]
    pending = _drops_from_argv(argv)
    force_gui = "--gui" in argv

    if pending and not force_gui:
        from src.adapter.silent_drop import run_silent_drops

        return run_silent_drops(pending)

    from src.view.main_window import run

    return run()


if __name__ == "__main__":
    raise SystemExit(main())