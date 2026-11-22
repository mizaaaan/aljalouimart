#!/usr/bin/env python3
"""Point the site at a new web address (e.g. when a custom domain is connected).

Usage (from the project folder):
    python3 tools/set-domain.py https://www.example.com/
    python3 tools/set-domain.py https://www.example.com/ --cname      # also writes a CNAME file

It rewrites the absolute URLs used by search engines and social sharing in:
index.html, robots.txt, sitemap.xml  — nothing else is touched.
"""
import re, sys, pathlib

OLD = "https://mizaaaan.github.io/aljalouionlineshop/"
root = pathlib.Path(__file__).resolve().parent.parent

args = [a for a in sys.argv[1:] if not a.startswith("--")]
if len(args) != 1 or not re.match(r"^https://[a-z0-9.-]+/?$", args[0], re.I):
    sys.exit("Usage: python3 tools/set-domain.py https://your-domain.com/ [--cname]")
new = args[0].rstrip("/") + "/"

changed = 0
for name in ("index.html", "robots.txt", "sitemap.xml"):
    f = root / name
    text = f.read_text(encoding="utf-8")
    n = text.count(OLD)
    if n:
        f.write_text(text.replace(OLD, new), encoding="utf-8")
        print(f"{name}: {n} address(es) updated")
        changed += n
if not changed:
    print("Nothing to change — the site already uses a different address. Edit the URLs by hand if needed.")
if "--cname" in sys.argv:
    host = re.sub(r"^https://", "", new).rstrip("/")
    (root / "CNAME").write_text(host + "\n")
    print(f"CNAME written: {host}")
