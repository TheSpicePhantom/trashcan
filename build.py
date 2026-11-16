#!/usr/bin/env python3
"""Trashcan-Build: Versionsnummer, Kanal (alpha/beta/release), PyInstaller-EXE."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "version.json"
DIST_DIR = ROOT / "dist"
BUILD_WORK = ROOT / "build" / "pyinstaller"
VERSION_INFO_PATH = ROOT / "build" / "file_version_info.txt"
SRC_VERSION_PATH = ROOT / "src" / "version.py"


def _load_version_data() -> dict[str, int]:
    if not VERSION_FILE.is_file():
        data = {"major": 0, "minor": 1, "patch": 0}
        VERSION_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return data

    data = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    for key in ("major", "minor", "patch"):
        if key not in data:
            raise ValueError(f"version.json: Feld „{key}“ fehlt.")
    return data


def _save_version_data(data: dict[str, int]) -> None:
    VERSION_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _ask_channel() -> str:
    print()
    print("Release-Kanal wählen:")
    print("  [1] alpha")
    print("  [2] beta")
    print("  [3] release")
    print()

    while True:
        choice = input("Eingabe (1/2/3): ").strip().lower()
        if choice in {"1", "alpha", "a"}:
            return "alpha"
        if choice in {"2", "beta", "b"}:
            return "beta"
        if choice in {"3", "release", "r"}:
            return "release"
        print("Bitte 1, 2 oder 3 eingeben.")


def _compose_version(major: int, minor: int, patch: int, channel: str) -> str:
    base = f"{major}.{minor}.{patch}"
    if channel == "release":
        return base
    return f"{base}-{channel}"


def _file_version_tuple(version: str) -> tuple[int, int, int, int]:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        return (0, 1, 0, 0)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)), 0)


def _write_src_version(version: str, channel: str, file_version: tuple[int, int, int, int]) -> None:
    content = f'''"""Versionsinformation – generiert von build.py am {datetime.now(timezone.utc).isoformat()}."""

VERSION = "{version}"
CHANNEL = "{channel}"
FILE_VERSION = {file_version!r}
'''
    SRC_VERSION_PATH.write_text(content, encoding="utf-8")


def _write_version_info(version: str, file_version: tuple[int, int, int, int]) -> None:
    VERSION_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={file_version},
    prodvers={file_version},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [
            StringStruct('CompanyName', 'Trashcan'),
            StringStruct('FileDescription', 'Trashcan – persönlicher Mülleimer'),
            StringStruct('FileVersion', '{version}'),
            StringStruct('InternalName', 'Trashcan'),
            StringStruct('LegalCopyright', ''),
            StringStruct('OriginalFilename', 'Trashcan.exe'),
            StringStruct('ProductName', 'Trashcan'),
            StringStruct('ProductVersion', '{version}'),
          ],
        )
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])]),
  ]
)
"""
    VERSION_INFO_PATH.write_text(text, encoding="utf-8")


def _prepare_app_icon() -> tuple[Path, Path]:
    from src.icon.convert import ICON_PNG, ensure_icon_ico

    ico = ensure_icon_ico()
    build_ico = ROOT / "build" / "trashcan.ico"
    build_ico.parent.mkdir(parents=True, exist_ok=True)
    build_ico.write_bytes(ico.read_bytes())
    print(f"Icon: {build_ico}")
    return build_ico.resolve(), ICON_PNG.resolve()


def _run_pyinstaller(version: str, ico_path: Path, png_path: Path) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        "Trashcan",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_WORK}",
        f"--specpath={ROOT / 'build'}",
        f"--paths={ROOT}",
        "--hidden-import=windnd",
        "--hidden-import=win32com.client",
        "--hidden-import=PIL.Image",
        f"--version-file={VERSION_INFO_PATH}",
        f"--icon={ico_path}",
        f"--add-data={ico_path}{os.pathsep}src/icon",
        f"--add-data={png_path}{os.pathsep}src/icon",
        str(ROOT / "trashcan.py"),
    ]

    print()
    print("PyInstaller:", " ".join(cmd))
    print()
    subprocess.run(cmd, cwd=ROOT, check=True)

    default_exe = DIST_DIR / "Trashcan.exe"
    if not default_exe.is_file():
        raise FileNotFoundError(f"EXE nicht gefunden: {default_exe}")

    safe_label = version.replace(" ", "_")
    versioned_exe = DIST_DIR / f"Trashcan-{safe_label}.exe"
    versioned_exe.write_bytes(default_exe.read_bytes())
    return versioned_exe


def _ensure_pyinstaller() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(ROOT / "requirements.txt"),
            "pyinstaller",
            "pillow",
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    if sys.platform != "win32":
        print("Build ist für Windows (EXE) vorgesehen.")
        return 1

    data = _load_version_data()
    data["patch"] = int(data["patch"]) + 1
    channel = _ask_channel()

    version = _compose_version(int(data["major"]), int(data["minor"]), int(data["patch"]), channel)
    file_version = _file_version_tuple(version)

    print()
    print(f"Neue Version: {version}")
    print(f"Windows FileVersion: {file_version[0]}.{file_version[1]}.{file_version[2]}.{file_version[3]}")
    confirm = input("Build starten? (j/n): ").strip().lower()
    if not confirm.startswith("j"):
        print("Abgebrochen.")
        return 0

    _save_version_data(data)
    _write_src_version(version, channel, file_version)
    _write_version_info(version, file_version)

    try:
        _ensure_pyinstaller()
        ico_path, png_path = _prepare_app_icon()
        exe_path = _run_pyinstaller(version, ico_path, png_path)
    except subprocess.CalledProcessError as err:
        print(f"Build fehlgeschlagen (Exit {err.returncode}).")
        return err.returncode or 1

    print()
    print("Build erfolgreich.")
    print(f"  {exe_path}")
    print(f"  {DIST_DIR / 'Trashcan.exe'}")
    print()
    print("Tipp: Desktop-Verknüpfung auf die EXE – Drag & Drop auf das Icon.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())