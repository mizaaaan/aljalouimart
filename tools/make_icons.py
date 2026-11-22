#!/usr/bin/env python3
"""Generate favicons / app icons from the real logo mark (brand-source/logo-mark.png).

Run from the project folder:  python3 tools/make_icons.py     (needs Pillow)
Writes: favicon.ico, favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAM = (252, 249, 225, 255)
mark = Image.open(os.path.join(ROOT, "brand-source", "logo-mark.png")).convert("RGBA")
mark = mark.crop(mark.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())


def tile(size, pad, radius=0.0):
    """Cream tile with the mark centred; pad = empty margin as a share of the tile."""
    S = 4                                              # supersample for smooth edges
    big = size * S
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, big - 1, big - 1), radius=int(big * radius), fill=CREAM)
    inner = big * (1 - 2 * pad)
    k = min(inner / mark.width, inner / mark.height)
    m = mark.resize((round(mark.width * k), round(mark.height * k)), Image.LANCZOS)
    img.alpha_composite(m, ((big - m.width) // 2, (big - m.height) // 2))
    return img.resize((size, size), Image.LANCZOS)


tile(180, 0.17).convert("RGB").save(os.path.join(ROOT, "apple-touch-icon.png"), optimize=True)
tile(192, 0.17).convert("RGB").save(os.path.join(ROOT, "icon-192.png"), optimize=True)
tile(512, 0.17).convert("RGB").save(os.path.join(ROOT, "icon-512.png"), optimize=True)
tile(32, 0.08, 0.2).save(os.path.join(ROOT, "favicon-32.png"), optimize=True)
tile(48, 0.08, 0.2).save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
print("icons written")
