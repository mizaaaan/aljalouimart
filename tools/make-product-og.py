#!/usr/bin/env python3
"""Build the 1200x630 social share card for every product in index.html.

Each product page needs its own og:image. WhatsApp and some other link
previews will not render a WebP, so these cards are written as JPEG.

Run from the project folder:

    python tools/make-product-og.py            # build cards into build/og/
    python tools/make-product-og.py --upload   # build, then push them to R2

The cards live in R2 next to the product photos, under products/v5/og/.
"""
import argparse
import io
import os
import re
import subprocess
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "build", "og")
BUCKET = "aljalouimart-media"
OG_PREFIX = "products/v5/og"

W, H = 1200, 630
NAVY = (17, 35, 79)
YELLOW = (255, 224, 14)
CREAM = (252, 249, 225)
LINE = (229, 225, 198)
INK_SOFT = (91, 100, 120)
WHITE = (255, 255, 255)

CAT_LABELS = {
    "islamic": "Islamic Products",
    "bukhoor": "Bukhoor & Fragrance",
    "wellness": "Health & Wellness",
    "tools": "Tools & Car Care",
    "toys": "Toys & Games",
    "art": "Art & Stationery",
}


def find_font(names):
    for path in names:
        if os.path.exists(path):
            return path
    raise SystemExit("No usable font found. Looked for: " + ", ".join(names))


FONT_B = find_font([
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
])
FONT_R = find_font([
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
])


def read_products():
    """Pull id / slug / name / price / category / image out of index.html."""
    src = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    media = re.search(r"const MEDIA = '([^']+)'", src).group(1)
    out = []
    for line in src.split("\n"):
        line = line.strip()
        if not line.startswith("{ id:") or "slug:" not in line:
            continue
        def grab(key):
            m = re.search(key + r": '((?:[^'\\]|\\.)*)'", line)
            return m.group(1) if m else ""
        img = re.search(r"img: MEDIA \+ '([^']+)'", line).group(1)
        out.append({
            "slug": grab("slug"),
            "cat": grab("cat"),
            "name": grab("nameEn"),
            "price": int(re.search(r"price: (\d+)", line).group(1)),
            "img_url": media + img,
        })
    if not out:
        raise SystemExit("No products found in index.html")
    return out


def fetch(url, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    dest = os.path.join(cache_dir, url.rsplit("/", 1)[-1])
    if not os.path.exists(dest):
        req = urllib.request.Request(url, headers={"User-Agent": "og-card-builder"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            f.write(r.read())
    return dest


def fit_font(draw, text, path, size, max_w):
    """Largest size <= size whose rendered text fits max_w."""
    while size > 12:
        f = ImageFont.truetype(path, size)
        box = draw.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_w:
            return f
        size -= 1
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        box = draw.textbbox((0, 0), trial, font=font)
        if box[2] - box[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build_card(product, cache_dir):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # Soft brand shapes, echoing the site's hero.
    d.ellipse((760, -340, 1480, 380), fill=CREAM)
    d.ellipse((-260, 420, 220, 900), fill=CREAM)
    d.rounded_rectangle((22, 22, W - 22, H - 22), radius=26, outline=LINE, width=3)

    # ---- product photo, contained in a white card on the left ----
    PX, PY, PW, PH = 62, 62, 496, 506
    d.rounded_rectangle((PX, PY, PX + PW, PY + PH), radius=18, fill=WHITE, outline=LINE, width=2)
    photo = Image.open(fetch(product["img_url"], cache_dir)).convert("RGBA")
    pad = 22
    photo.thumbnail((PW - pad * 2, PH - pad * 2), Image.LANCZOS)
    plate = Image.new("RGB", photo.size, WHITE)
    plate.paste(photo, (0, 0), photo)
    img.paste(plate, (PX + (PW - photo.width) // 2, PY + (PH - photo.height) // 2))

    # ---- right hand column ----
    x = 600
    max_w = W - x - 80

    logo_path = os.path.join(ROOT, "assets", "brand", "logo-horizontal.png")
    y = 74
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        lh = 54
        logo = logo.resize((round(logo.width * lh / logo.height), lh), Image.LANCZOS)
        img.paste(logo, (x, y), logo)
        y += lh + 30
    else:
        d.text((x, y), "Al Jaloui Mart", font=ImageFont.truetype(FONT_B, 40), fill=NAVY)
        y += 72

    cat = CAT_LABELS.get(product["cat"], product["cat"].title())
    d.rounded_rectangle((x, y, x + 10, y + 22), radius=5, fill=YELLOW)
    d.text((x + 24, y - 1), cat.upper(), font=ImageFont.truetype(FONT_B, 19), fill=INK_SOFT)
    y += 46

    name_font = ImageFont.truetype(FONT_B, 54)
    lines = wrap(d, product["name"], name_font, max_w)
    while len(lines) > 3 and name_font.size > 32:
        name_font = ImageFont.truetype(FONT_B, name_font.size - 3)
        lines = wrap(d, product["name"], name_font, max_w)
    for line in lines:
        d.text((x, y), line, font=name_font, fill=NAVY)
        y += round(name_font.size * 1.18)

    # price pill
    y += 18
    price = "QAR %d" % product["price"]
    pf = ImageFont.truetype(FONT_B, 40)
    box = d.textbbox((0, 0), price, font=pf)
    pw, ph = box[2] - box[0], box[3] - box[1]
    d.rounded_rectangle((x, y, x + pw + 48, y + ph + 34), radius=12, fill=YELLOW)
    d.text((x + 24, y + 11), price, font=pf, fill=NAVY)
    y += ph + 34

    # footer lines, pinned to the bottom of the card
    foot = "Doha, Qatar  \u00b7  Cash on delivery"
    order = "Order on WhatsApp \u00b7 no app needed"
    d.line((x, H - 150, x + max_w, H - 150), fill=LINE, width=2)
    d.text((x, H - 132), foot, font=fit_font(d, foot, FONT_R, 24, max_w), fill=INK_SOFT)
    d.text((x, H - 94), order, font=fit_font(d, order, FONT_B, 26, max_w), fill=NAVY)

    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upload", action="store_true", help="push the cards to R2")
    args = ap.parse_args()

    cache_dir = os.path.join(ROOT, "build", "src-photos")
    os.makedirs(OUT_DIR, exist_ok=True)
    products = read_products()

    made = []
    for p in products:
        card = build_card(p, cache_dir)
        dest = os.path.join(OUT_DIR, p["slug"] + ".jpg")
        card.save(dest, "JPEG", quality=86, optimize=True, progressive=True)
        made.append((p["slug"], dest))
        print("built %-34s %5.0f KB" % (p["slug"] + ".jpg", os.path.getsize(dest) / 1024))

    if not args.upload:
        print("\n%d cards in %s (re-run with --upload to push them to R2)" % (len(made), OUT_DIR))
        return

    for slug, path in made:
        key = "%s/%s.jpg" % (OG_PREFIX, slug)
        cmd = ["npx", "wrangler", "r2", "object", "put", "%s/%s" % (BUCKET, key),
               "--file", path, "--content-type", "image/jpeg", "--remote"]
        r = subprocess.run(cmd, shell=(os.name == "nt"), capture_output=True, text=True)
        if r.returncode != 0:
            print("FAILED %s\n%s" % (key, r.stderr.strip()[-500:]), file=sys.stderr)
            sys.exit(1)
        print("uploaded", key)


if __name__ == "__main__":
    main()
