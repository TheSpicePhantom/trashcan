from __future__ import annotations

import json
import os
from pathlib import Path

from src.model.trash_config import TrashCanSettings

_CONFIG_KEY = "trash_location"


def config_file_path() -> Path:
    base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    return base / "Trashcan" / "config.json"


def load_trash_settings() -> TrashCanSettings:
    path = config_file_path()
    if not path.is_file():
        return TrashCanSettings(trash_location=None)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return TrashCanSettings(trash_location=None)

    raw = data.get(_CONFIG_KEY)
    if not raw or not isinstance(raw, str):
        return TrashCanSettings(trash_location=None)

    location = Path(raw)
    if not location.is_dir():
        return TrashCanSettings(trash_location=None)

    return TrashCanSettings(trash_location=location)


def save_trash_location(location: Path) -> None:
    path = config_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {_CONFIG_KEY: str(location.resolve())}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")