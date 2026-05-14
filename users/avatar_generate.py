from __future__ import annotations

import io
import random
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

_FONTS_DIR = Path(__file__).resolve().parent / "fonts"

BACKGROUND_COLORS = [
    (196, 206, 218),
    (202, 212, 204),
    (214, 206, 198),
    (208, 202, 214),
    (198, 210, 214),
    (216, 208, 200),
    (200, 208, 216),
    (210, 204, 210),
    (204, 214, 206),
    (212, 208, 202),
    (206, 200, 214),
    (198, 204, 212),
    (218, 210, 204),
    (204, 208, 218),
    (210, 216, 208),
]

SIZE = 256
MAX_GLYPH_RATIO = 0.62


def _first_letter(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return "?"
    return name[0].upper()


def _luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def _text_color_for_bg(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    if _luminance(bg) > 0.45:
        return (58, 64, 78)
    return (236, 238, 242)


def _font_file_paths() -> list[Path]:
    return [
        _FONTS_DIR / "DejaVuSans-Bold.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\calibrib.ttf"),
    ]


def _try_load_font(path: Path, size: int) -> ImageFont.FreeTypeFont | None:
    if not path.is_file():
        return None
    try:
        return ImageFont.truetype(str(path), size=size)
    except OSError:
        return None


def _best_font_for_letter(letter: str) -> ImageFont.ImageFont:
    max_side = int(SIZE * MAX_GLYPH_RATIO)
    tmp = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    draw = ImageDraw.Draw(tmp)

    for path in _font_file_paths():
        lo, hi = 24, int(SIZE * 0.78)
        best: ImageFont.FreeTypeFont | None = None
        while lo <= hi:
            mid = (lo + hi) // 2
            font = _try_load_font(path, mid)
            if font is None:
                break
            bbox = draw.textbbox((0, 0), letter, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            side = max(w, h, 1)
            if side <= max_side:
                best = font
                lo = mid + 1
            else:
                hi = mid - 1
        if best is not None:
            return best

    return ImageFont.load_default()


def build_registration_avatar_png(name: str) -> ContentFile:
    letter = _first_letter(name)
    bg = random.choice(BACKGROUND_COLORS)
    text_color = _text_color_for_bg(bg)

    image = Image.new("RGB", (SIZE, SIZE), bg)
    draw = ImageDraw.Draw(image)
    font = _best_font_for_letter(letter)

    cx, cy = SIZE // 2, SIZE // 2
    draw.text((cx, cy), letter, font=font, fill=text_color, anchor="mm")

    buf = io.BytesIO()
    image.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return ContentFile(buf.read(), name="avatar.png")
