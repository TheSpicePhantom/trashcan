from __future__ import annotations

from pathlib import Path

ICON_DIR = Path(__file__).resolve().parent
ICON_SOURCE_CANDIDATES = (
    ICON_DIR / "icon_256x256.jpg",
    ICON_DIR / "icon_256x256.png",
    ICON_DIR / "icon.jpg",
    ICON_DIR / "icon.png",
)
ICON_ICO = ICON_DIR / "icon.ico"
ICON_PNG = ICON_DIR / "icon.png"

_ICON_SIZES = (16, 32, 48, 64, 128, 256)

_CHECKERBOARD_REFS = (
    (255, 255, 255),
    (254, 254, 254),
    (240, 240, 240),
    (204, 204, 204),
    (192, 192, 192),
    (220, 220, 220),
)


def _find_source_image() -> Path:
    for path in ICON_SOURCE_CANDIDATES:
        if path.is_file():
            return path
    raise FileNotFoundError(
        "Kein App-Icon gefunden. Erwartet z. B.: src/icon/icon_256x256.jpg"
    )


def _color_close(a: tuple[int, int, int], b: tuple[int, int, int], tolerance: int) -> bool:
    return all(abs(int(a[i]) - int(b[i])) <= tolerance for i in range(3))


def _remove_checkerboard_background(image, *, tolerance: int = 32):
    from PIL import Image

    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size

    reference_colors: list[tuple[int, int, int]] = list(_CHECKERBOARD_REFS)
    for x, y in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
        r, g, b, _ = pixels[x, y]
        reference_colors.append((r, g, b))

    def is_background(r: int, g: int, b: int) -> bool:
        return any(_color_close((r, g, b), ref, tolerance) for ref in reference_colors)

    visited: set[tuple[int, int]] = set()
    stack: list[tuple[int, int]] = []
    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        if not (0 <= x < width and 0 <= y < height):
            continue
        visited.add((x, y))
        r, g, b, _ = pixels[x, y]
        if not is_background(r, g, b):
            continue
        pixels[x, y] = (r, g, b, 0)
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    return rgba


def ensure_icon_ico() -> Path:
    source = _find_source_image()

    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow fehlt (pip install Pillow) für die Icon-Konvertierung.") from exc

    opened = Image.open(source)
    image = opened if source.suffix.lower() == ".png" else _remove_checkerboard_background(opened)
    if source.suffix.lower() == ".png" and image.mode != "RGBA":
        image = image.convert("RGBA")

    frames = [image.resize((size, size), Image.Resampling.LANCZOS) for size in _ICON_SIZES]

    frames[0].save(
        ICON_ICO,
        format="ICO",
        sizes=[(frame.width, frame.height) for frame in frames],
        append_images=frames[1:],
    )

    frames[-1].save(ICON_PNG, format="PNG", optimize=True)

    return ICON_ICO.resolve()


def resolve_icon_ico() -> Path | None:
    if ICON_ICO.is_file() and ICON_PNG.is_file():
        return ICON_ICO.resolve()
    try:
        return ensure_icon_ico()
    except (FileNotFoundError, RuntimeError, OSError):
        return None