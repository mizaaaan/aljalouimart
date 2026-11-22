#!/usr/bin/env python3
"""Generate the 1200x630 Open Graph share image for Al Jaloui Mart.

Run from the project folder:  python3 tools/make_og.py
Then commit the updated og-image.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
NAVY    = (17, 35, 79)
NAVY_D  = (11, 24, 55)
YELLOW  = (255, 224, 14)
GOLD    = (200, 166, 0)
CREAM   = (252, 249, 225)
LINE    = (229, 225, 198)
INK_SOF = (91, 100, 120)
WHITE   = (255, 255, 255)


def find_font(names):
    """First existing font path from a list of candidates."""
    for path in names:
        if os.path.exists(path):
            return path
    raise SystemExit("No usable font found for the OG image.")


FONT_B = find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
])
FONT_R = find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
])

img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)

# --- Soft cream background shapes ---
d.ellipse((650, -320, 1430, 460), fill=CREAM)
d.ellipse((-220, 440, 250, 910), fill=CREAM)

# --- Thin brand frame ---
d.rounded_rectangle((22, 22, W - 22, H - 22), radius=26, outline=LINE, width=3)

# --- Real logo (stacked, full colour) from the web logo files
logo = Image.open(os.path.join(ROOT, "assets", "brand", "logo-stacked.png")).convert("RGBA")
LH = 470
logo = logo.resize((round(logo.width * LH / logo.height), LH), Image.LANCZOS)
img.paste(logo, (330 - logo.width // 2, (H - LH) // 2), logo)

x0 = 640
d.rounded_rectangle((x0 + 4, 150, x0 + 132, 162), radius=6, fill=YELLOW)
d.text((x0 + 4, 186), "Your neighbourhood", font=ImageFont.truetype(FONT_B, 46), fill=NAVY)
d.text((x0 + 4, 244), "mart is now online", font=ImageFont.truetype(FONT_B, 46), fill=NAVY)
d.text((x0 + 4, 330), "To the satisfaction of Almighty.",
       font=ImageFont.truetype(FONT_R, 27), fill=INK_SOF)

# separator
d.line((x0 + 4, 432, x0 + 500, 432), fill=LINE, width=2)


def fit(text, font_path, size, maxw):
    """Largest font size <= size whose rendered text fits maxw."""
    while size > 10:
        f = ImageFont.truetype(font_path, size)
        if d.textbbox((0, 0), text, font=f)[2] - d.textbbox((0, 0), text, font=f)[0] <= maxw:
            return f
        size -= 1
    return ImageFont.truetype(font_path, size)


lines = [
    "Essentials \u00b7 Mother & Baby \u00b7 Personal Care",
    "Health devices \u00b7 Cash on delivery",
    "Doha, Qatar",
]
y = 452
for text in lines:
    f = fit(text, FONT_R, 20, 500)
    d.text((x0 + 4, y), text, font=f, fill=INK_SOF)
    y += 30

order_line = "Order on WhatsApp \u00b7 +974 7473 3400"
d.text((x0 + 4, y + 6), order_line, font=fit(order_line, FONT_B, 22, 500), fill=NAVY)

out = os.path.join(ROOT, "og-image.png")
img.save(out, "PNG", optimize=True)
print("saved", out, img.size, f"{os.path.getsize(out)/1024:.0f} KB")
