#!/usr/bin/env python3
"""Regenerate favicon.ico, favicon-{16,32}x16.png, apple-touch-icon.png,
icon-192.png, and icon-512.png from logo.svg (#164, refreshed for the
"corrected F" mark - see Fair Code Logo System).

Pillow can't rasterize arbitrary SVG, but logo.svg is deliberately just
three plain rects (stem, top bar, accent crossbar) - this parses that
specific shape with the stdlib's xml.etree and draws it with Pillow,
rather than pulling in a full SVG-rendering dependency (cairosvg/resvg)
for one tiny icon.

The mark is rendered two ways, per the logo system's own rule:
  - Browser favicons (16/32px) sit on transparent, light browser chrome,
    so the stem/bar use the dark "ink" color (#14171A).
  - App/social icons (180/192/512px) need an opaque tile, so they get the
    near-black background (#0D0F0E) with the stem/bar in near-white
    (#F2F1EC) instead - ink-on-transparent would be invisible on that bg.
  - The accent crossbar is always the same green (#4F7A5B) in both -
    it's the one color that never changes context, per the logo system's
    "green marks the correction, not the brand as a whole" rule.

If logo.svg ever grows more complex than exactly three rects, this raises
clearly instead of silently drawing the wrong thing - switch to an actual
SVG renderer at that point.

Run with: python3 scripts/generate_favicons.py
"""
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = ROOT / "assets" / "icons"
LOGO_SVG = ICONS_DIR / "logo.svg"
SVG_NS = "{http://www.w3.org/2000/svg}"

DARK_TILE_BG = "#0D0F0E"
LIGHT_MARK = "#F2F1EC"


def _parse_mark(svg_path):
    root = ET.parse(svg_path).getroot()
    view_box = [float(v) for v in root.get("viewBox").split()]
    if view_box[:2] != [0.0, 0.0] or view_box[2] != view_box[3]:
        raise ValueError("logo.svg: expected a square viewBox starting at 0,0")

    rects = root.findall(f"{SVG_NS}rect")
    if len(rects) != 3 or len(list(root)) != 3:
        raise ValueError(
            "logo.svg is no longer exactly three rects (stem, top bar, crossbar) - "
            "update this script (or switch to a real SVG renderer) before regenerating icons."
        )
    stem, bar, crossbar = rects

    if stem.get("fill") != bar.get("fill"):
        raise ValueError("logo.svg: stem and top bar are expected to share one fill color")

    def box(rect):
        x, y = float(rect.get("x")), float(rect.get("y"))
        w, h = float(rect.get("width")), float(rect.get("height"))
        return (x, y, x + w, y + h)

    return {
        "size": view_box[2],
        "shapes": [box(stem), box(bar)],
        "mark_fill": stem.get("fill"),
        "accent": box(crossbar),
        "accent_fill": crossbar.get("fill"),
    }


def render(spec, px, transparent, mark_fill=None):
    scale = px / spec["size"]
    mode = "RGBA" if transparent else "RGB"
    bg = (0, 0, 0, 0) if transparent else DARK_TILE_BG
    img = Image.new(mode, (px, px), bg)
    draw = ImageDraw.Draw(img)
    fill = mark_fill if mark_fill is not None else spec["mark_fill"]
    for box in spec["shapes"]:
        draw.rectangle(tuple(c * scale for c in box), fill=fill)
    draw.rectangle(tuple(c * scale for c in spec["accent"]), fill=spec["accent_fill"])
    return img


def main():
    spec = _parse_mark(LOGO_SVG)

    # Favicons: transparent, ink mark - logo.svg's own colors.
    favicon_16 = render(spec, 16, transparent=True)
    favicon_16.save(ICONS_DIR / "favicon-16x16.png")
    favicon_32 = render(spec, 32, transparent=True)
    favicon_32.save(ICONS_DIR / "favicon-32x32.png")
    # Pillow's ICO writer builds a listed `sizes` frame by resizing whichever
    # save()-provided image (the base image passed to save(), or one in
    # append_images) exactly matches that size, only falling back to
    # resizing the base image down when no exact match exists - and it skips
    # any requested size larger than the base image entirely, so the base
    # must be the largest frame (favicon_32) with the smaller dedicated
    # render passed via append_images, not the other way around.
    favicon_32.save(ICONS_DIR / "favicon.ico", sizes=[(16, 16), (32, 32)], append_images=[favicon_16])

    # App/social icons: opaque dark tile, light mark.
    render(spec, 180, transparent=False, mark_fill=LIGHT_MARK).save(ICONS_DIR / "apple-touch-icon.png")
    render(spec, 192, transparent=False, mark_fill=LIGHT_MARK).save(ICONS_DIR / "icon-192.png")
    render(spec, 512, transparent=False, mark_fill=LIGHT_MARK).save(ICONS_DIR / "icon-512.png")

    print("Regenerated favicon-16x16.png, favicon-32x32.png, favicon.ico, "
          "apple-touch-icon.png, icon-192.png, and icon-512.png from logo.svg")


if __name__ == "__main__":
    main()
