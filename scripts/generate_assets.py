#!/usr/bin/env python3
"""Generate the MD Work icon set and social sharing image.

Run from the repo root:  python3 scripts/generate_assets.py
Requires Pillow.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "assets" / "img"

ACCENT = (255, 201, 60)
INK = (10, 14, 21)
BG = (7, 11, 18)
SURFACE = (14, 23, 39)
TEXT = (243, 246, 250)
MUTED = (149, 163, 184)
GREEN = (67, 217, 163)

# "MW" monogram drawn in a 512x512 coordinate space.
STROKES = (
    ((60, 372), (60, 140), (150, 310), (240, 140), (240, 372)),
    ((284, 140), (326, 372), (368, 150), (410, 372), (452, 140)),
)
STROKE_WIDTH = 38

FONT_GLOBS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/**/DejaVuSans-Bold.ttf",
    "/opt/**/DejaVuSans-Bold.ttf",
    "/opt/**/LiberationSans-Bold.ttf",
)

_FONT_CACHE = {}


def font_path():
    for pattern in FONT_GLOBS:
        if "*" not in pattern and Path(pattern).exists():
            return pattern
        matches = sorted(Path("/").glob(pattern.lstrip("/")))
        if matches:
            return str(matches[0])
    raise SystemExit("No bold TTF font found; install fonts-dejavu-core.")


def font(size):
    size = int(size)
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(font_path(), size)
    return _FONT_CACHE[size]


def draw_mw(draw, size, origin=(0, 0), color=INK, stroke=STROKE_WIDTH):
    scale = size / 512.0
    ox, oy = origin
    width = max(1, int(round(stroke * scale)))
    for points in STROKES:
        draw.line(
            [(ox + x * scale, oy + y * scale) for x, y in points],
            fill=color,
            width=width,
            joint="curve",
        )


def rounded_bg(size, radius_ratio=0.22):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * radius_ratio), fill=ACCENT)
    return img


def icon(size):
    img = rounded_bg(size)
    draw_mw(ImageDraw.Draw(img), size)
    return img


def fit_text(draw, text, max_width, start_size, min_size=18):
    size = start_size
    while size > min_size and draw.textlength(text, font=font(size)) > max_width:
        size -= 2
    return font(size)


def social_image():
    width, height = 1200, 630
    base = Image.new("RGB", (width, height), BG)

    # warm glow on the right
    glow_mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(glow_mask).ellipse([760, -260, 1420, 460], fill=110)
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(140))
    base = Image.composite(Image.new("RGB", (width, height), ACCENT), base, glow_mask)

    draw = ImageDraw.Draw(base)
    draw.rectangle([0, 0, width, 4], fill=ACCENT)

    mark = icon(96)
    base.paste(mark, (72, 62), mark)
    draw.text((192, 78), "MD Work", font=font(46), fill=TEXT)
    draw.text((194, 130), "MD NEXA PRODUCT", font=font(18), fill=(255, 201, 60))

    max_text = 676
    draw.text((72, 212), "Track work days,", font=fit_text(draw, "Track work days,", max_text, 64), fill=TEXT)
    draw.text((72, 294), "earnings & expenses.", font=fit_text(draw, "earnings & expenses.", max_text, 64), fill=ACCENT)
    draw.text(
        (74, 396),
        "The simple work notebook for daily and hourly workers.",
        font=fit_text(draw, "The simple work notebook for daily and hourly workers.", max_text, 26),
        fill=MUTED,
    )

    # Google Play style badge
    badge_x, badge_y, badge_w, badge_h = 72, 470, 388, 74
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=18,
        fill=ACCENT,
    )
    draw.polygon(
        [(badge_x + 34, badge_y + 24), (badge_x + 62, badge_y + 37), (badge_x + 34, badge_y + 50)],
        fill=INK,
    )
    draw.text((badge_x + 78, badge_y + 12), "GET IT ON", font=font(15), fill=(70, 60, 20))
    draw.text((badge_x + 78, badge_y + 29), "Google Play", font=font(31), fill=INK)

    # mini app card
    card = [770, 150, 1128, 470]
    draw.rounded_rectangle(card, radius=30, fill=SURFACE, outline=(46, 60, 82), width=2)
    draw.text((800, 184), "OCTOBER 2026", font=font(16), fill=MUTED)
    draw.text((800, 216), "Remaining", font=font(24), fill=MUTED)
    draw.text((800, 248), "\u20ac1,087", font=font(58), fill=TEXT)
    draw.rounded_rectangle([800, 330, 1098, 380], radius=12, fill=(255, 201, 60))
    draw.text((850, 342), "Share report", font=font(24), fill=INK)
    summary = "19 work days \u00b7 \u20ac1,140 earned"
    draw.text((800, 404), summary, font=fit_text(draw, summary, 296, 20), fill=GREEN)

    return base


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    for size in (192, 512):
        icon(size).save(OUT / f"icon-{size}.png")

    icon(180).convert("RGB").save(OUT / "icon-180.png")

    big = icon(64)
    big.save(OUT / "favicon.ico", sizes=[(64, 64), (32, 32), (16, 16)])

    social_image().save(OUT / "og.png", optimize=True)

    print("Wrote:", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
