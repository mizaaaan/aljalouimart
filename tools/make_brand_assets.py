#!/usr/bin/env python3
"""Build the web-ready logo files from the master logos in brand-source/.

Run from the project folder:  python3 tools/make_brand_assets.py      (needs Pillow)

brand-source/  (transparent PNG masters, any size)      ->   assets/brand/  (optimised for the web)
  logo-horizontal.png        full colour, mark beside name  ->  logo-horizontal.png   (640 px wide)
  logo-horizontal-light.png  all-yellow, for dark areas     ->  logo-horizontal-light.png
  logo-stacked.png           full colour, name below mark   ->  logo-stacked.png       (640 px wide)
  logo-stacked-light.png     all-yellow                     ->  logo-stacked-light.png
  logo-mark.png              icon only                      ->  logo-mark.png          (512 px wide)

To change the logo: replace the files in brand-source/ (keep the names), run this script,
then run tools/make_icons.py and tools/make_og.py to refresh favicons and the share image.
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(ROOT, "brand-source"), os.path.join(ROOT, "assets", "brand")
WIDTHS = {"logo-horizontal": 640, "logo-horizontal-light": 640,
          "logo-stacked": 640, "logo-stacked-light": 640, "logo-mark": 512}
os.makedirs(OUT, exist_ok=True)

for name, w in WIDTHS.items():
    path = os.path.join(SRC, name + ".png")
    if not os.path.exists(path):
        sys.exit(f"Missing master: brand-source/{name}.png")
    im = Image.open(path).convert("RGBA")
    box = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()   # trim empty padding
    im = im.crop(box)
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)
    print(f"{name}.png  {w}x{h}  {os.path.getsize(os.path.join(OUT, name + '.png'))//1024} KB")
