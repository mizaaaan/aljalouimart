#!/usr/bin/env python3
"""Build one shareable landing page per product, at p/<slug>.html.

Each page carries its own Open Graph tags so WhatsApp, Facebook and the
rest show that product's photo and price when the link is pasted. The
share cards themselves are built by tools/make-product-og.py.

Everything is read out of index.html, so this is the one place products
are defined. Re-run after changing a product:

    python tools/make-product-pages.py

It also refreshes the product URLs in sitemap.xml.
"""
import datetime
import html
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://aljaloui.com"
OG_BASE = "https://pub-75ddd09c0ee44e93be11c31762842a79.r2.dev/products/v5/og"
OUT_DIR = os.path.join(ROOT, "p")

SRC = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()


def const(name):
    return re.search(name + r" = '([^']*)'", SRC).group(1)


MEDIA = const("const MEDIA")
R2_HOST = re.match(r"(https://[^/]+)", MEDIA).group(1)
WHATSAPP = re.search(r"whatsapp: '(\d+)'", SRC).group(1)
PHONE = re.search(r"phone: '(\+\d+)'", SRC).group(1)
EMAIL = re.search(r"email: '([^']+)'", SRC).group(1)


def read_categories():
    cats = {}
    for m in re.finditer(r"\{ key: '([a-z]+)', en: '([^']*)', ar: '([^']*)'", SRC):
        cats[m.group(1)] = {"en": m.group(2), "ar": m.group(3)}
    return cats


def read_products():
    out = []
    for line in SRC.split("\n"):
        line = line.strip()
        if not line.startswith("{ id:") or "slug:" not in line:
            continue

        def grab(key):
            m = re.search(key + r": '((?:[^'\\]|\\.)*)'", line)
            return m.group(1).replace("\\'", "'") if m else ""

        out.append({
            "id": int(re.search(r"id: (\d+)", line).group(1)),
            "slug": grab("slug"),
            "cat": grab("cat"),
            "nameEn": grab("nameEn"),
            "nameAr": grab("nameAr"),
            "descEn": grab("descEn"),
            "descAr": grab("descAr"),
            "price": int(re.search(r"price: (\d+)", line).group(1)),
            "img": MEDIA + re.search(r"img: MEDIA \+ '([^']+)'", line).group(1),
        })
    if not out:
        raise SystemExit("No products found in index.html")
    return out


CATS = read_categories()
PRODUCTS = read_products()

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{--brand:#11234F;--brand-dark:#0B1837;--accent:#FFE00E;--accent-deep:#EBC900;
--gold:#C8A600;--ink:#11234F;--ink-soft:#5B6478;--paper:#FFFFFF;--band:#FCF9E1;
--line:#E5E1C6;--radius:14px;--shadow:0 10px 30px rgba(27,42,78,.12)}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'Hind',system-ui,sans-serif;
font-size:16px;line-height:1.6}
[dir=rtl] body{font-family:'Cairo',system-ui,sans-serif}
img{max-width:100%;height:auto;display:block}
a{color:inherit}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.site-head{border-bottom:1.5px solid var(--line);background:var(--paper);position:sticky;top:0;z-index:5}
.site-head .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-block:12px}
.site-head img{height:48px;width:auto}
.lang-btn{min-width:44px;padding:9px 14px;border:1.5px solid var(--line);background:var(--paper);
border-radius:10px;font:inherit;font-weight:700;color:var(--ink);cursor:pointer}
.lang-btn:hover{border-color:var(--brand)}
.crumb{font-size:14px;color:var(--ink-soft);padding:18px 0 0}
.crumb a{color:var(--ink-soft);text-decoration:none}
.crumb a:hover{color:var(--brand);text-decoration:underline}
.product{display:grid;gap:30px;padding:22px 0 46px}
@media(min-width:860px){.product{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:46px;align-items:start;padding-block:32px 60px}}
.shot{border:1.5px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);
overflow:hidden;background:var(--paper)}
.shot img{width:100%;aspect-ratio:1/1;object-fit:cover}
.tag{display:inline-block;font-size:13px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
color:var(--brand);background:var(--band);border:1.5px solid var(--line);border-radius:999px;padding:5px 14px}
h1{font-family:'Barlow Condensed',system-ui,sans-serif;font-size:clamp(30px,5vw,46px);
line-height:1.12;margin:14px 0 6px;font-weight:700}
[dir=rtl] h1{font-family:'Cairo',system-ui,sans-serif}
.price{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:28px;font-weight:600;
color:var(--brand);margin:6px 0 14px}
.desc{color:var(--ink-soft);margin:0 0 22px;font-size:17px}
.btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:14px 18px;
border-radius:12px;font:inherit;font-weight:700;font-size:16px;text-decoration:none;cursor:pointer;
border:1.5px solid transparent;margin-bottom:10px}
.btn svg{width:20px;height:20px;flex:none;fill:none;stroke:currentColor;stroke-width:2;
stroke-linecap:round;stroke-linejoin:round}
.btn-wa{background:#1FA855;color:#fff}
.btn-wa:hover{background:#17893f}
.btn-copy{background:var(--accent);color:var(--brand);border-color:var(--accent-deep)}
.btn-copy:hover{background:var(--accent-deep)}
.btn-ghost{background:var(--paper);color:var(--brand);border-color:var(--line)}
.btn-ghost:hover{border-color:var(--brand)}
.order-form{display:flex;flex-direction:column;gap:12px;margin:0 0 10px;padding:18px;
border:1.5px solid var(--line);border-radius:var(--radius);background:var(--band)}
.order-intro{margin:0;font-size:14px;font-weight:700;color:var(--ink)}
.order-form label{font-size:13px;font-weight:600;color:var(--ink);display:block;margin-bottom:5px}
.order-form label.req::after{content:' *';color:#C0392B}
.order-form input,.order-form textarea{width:100%;padding:11px 12px;border:1.5px solid var(--line);
border-radius:10px;font:inherit;font-size:15px;background:var(--paper);color:var(--ink)}
.order-form input:focus,.order-form textarea:focus{outline:2px solid var(--brand);outline-offset:1px}
.order-form textarea{min-height:68px;resize:vertical}
.field-hint{font-size:12px;color:var(--ink-soft);margin-top:4px}
.order-form .btn{margin-bottom:0}
.order-disclaimer{margin:0;font-size:12px;color:var(--ink-soft)}
.assure{list-style:none;margin:20px 0 0;padding:16px 0 0;border-top:1.5px solid var(--line);
display:grid;gap:8px;font-size:15px;color:var(--ink-soft)}
.assure li{display:flex;gap:9px;align-items:flex-start}
.assure svg{width:18px;height:18px;flex:none;margin-top:3px;fill:none;stroke:var(--gold);
stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.site-foot{border-top:1.5px solid var(--line);background:var(--band);padding:26px 0;font-size:15px}
.site-foot .wrap{display:flex;flex-wrap:wrap;gap:10px 26px;align-items:center;justify-content:center;
text-align:center;color:var(--ink-soft)}
.site-foot a{color:var(--brand);font-weight:600;text-decoration:none}
.site-foot a:hover{text-decoration:underline}
.toast{position:fixed;left:50%;bottom:26px;transform:translate(-50%,16px);background:var(--brand);
color:#fff;padding:12px 20px;border-radius:12px;font-weight:600;box-shadow:var(--shadow);
opacity:0;pointer-events:none;transition:opacity .22s,transform .22s;z-index:40}
.toast.show{opacity:1;transform:translate(-50%,0)}
@media (prefers-reduced-motion:reduce){.toast{transition:none}}
""".strip()

PAGE = """<!DOCTYPE html>
<!--
  Al Jaloui Mart — product share page.
  GENERATED FILE. Do not edit by hand: change the product in index.html,
  then re-run  python tools/make-product-pages.py
-->
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="{url}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#11234F">
  <meta http-equiv="Content-Security-Policy"
    content="upgrade-insecure-requests; default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: {r2_host}; connect-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none'">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
  <meta property="og:type" content="product">
  <meta property="og:site_name" content="Al Jaloui Mart">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{name_en} — Al Jaloui Mart, Doha">
  <meta property="og:locale" content="en_US">
  <meta property="og:locale:alternate" content="ar_QA">
  <meta property="product:price:amount" content="{price}">
  <meta property="product:price:currency" content="QAR">
  <meta property="product:availability" content="in stock">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{og_title}">
  <meta name="twitter:description" content="{meta_desc}">
  <meta name="twitter:image" content="{og_image}">
  <meta name="twitter:image:alt" content="{name_en} — Al Jaloui Mart, Doha">
  <script type="application/ld+json">
{jsonld}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Hind:wght@400;500;600;700&family=Cairo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap">
  <style>
{css}
  </style>
</head>

<body>
  <header class="site-head">
    <div class="wrap">
      <a href="/" aria-label="Al Jaloui Mart — home">
        <img src="/assets/brand/logo-horizontal.png" alt="Al Jaloui Mart" width="200" height="48">
      </a>
      <button type="button" class="lang-btn" id="langBtn">عربي</button>
    </div>
  </header>

  <main class="wrap">
    <nav class="crumb" aria-label="Breadcrumb">
      <a href="/" data-t="home">Home</a> <span aria-hidden="true">›</span>
      <a href="/#products" data-t="cat">{cat_en}</a>
    </nav>

    <div class="product">
      <div class="shot">
        <img src="{img}" alt="{name_en}" id="shot" width="800" height="800" fetchpriority="high" decoding="async">
      </div>
      <div class="info">
        <span class="tag" data-t="cat">{cat_en}</span>
        <h1 data-t="name">{name_en}</h1>
        <p class="price"><bdi data-t="price">QAR {price}</bdi></p>
        <p class="desc" data-t="desc">{desc_en}</p>

        <form class="order-form" id="orderForm" novalidate>
          <p class="order-intro" data-t="intro">Cash on delivery — we need these to bring your
            order to you.</p>
          <div>
            <label class="req" for="ofName" data-t="l_name">Full name</label>
            <input type="text" id="ofName" name="name" autocomplete="name" maxlength="120" required
              aria-required="true">
          </div>
          <div>
            <label class="req" for="ofPhone" data-t="l_phone">Phone number</label>
            <input type="tel" id="ofPhone" name="tel" autocomplete="tel" inputmode="tel" dir="ltr"
              maxlength="30" required aria-required="true" aria-describedby="ofPhoneHint">
            <div class="field-hint" id="ofPhoneHint" data-t="hint">e.g. +974 5555 1234</div>
          </div>
          <div>
            <label class="req" for="ofAddress" data-t="l_addr">Delivery address</label>
            <textarea id="ofAddress" name="address" autocomplete="street-address" maxlength="300"
              required aria-required="true"></textarea>
          </div>
          <div>
            <label for="ofNote" data-t="l_note">Order note (optional)</label>
            <textarea id="ofNote" name="note" maxlength="300"></textarea>
          </div>
          <button type="submit" class="btn btn-wa" id="waBtn">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M21 11.5a8.4 8.4 0 0 1-12.6 7.3L3 20.5l1.7-5.3A8.5 8.5 0 1 1 21 11.5z" />
            </svg><span data-t="order">Order this on WhatsApp</span>
          </button>
          <p class="order-disclaimer" data-t="disc">We'll message you on WhatsApp to confirm your
            order and delivery time.</p>
        </form>
        <button type="button" class="btn btn-copy" id="copyBtn">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M10 13a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1" />
            <path d="M14 11a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1" />
          </svg><span data-t="copy">Copy link to share</span>
        </button>
        <a class="btn btn-ghost" href="/#products"><span data-t="all">See all products</span></a>

        <ul class="assure">
          <li><svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20 6 9 17l-5-5" />
            </svg><span data-t="a1">Cash on delivery</span></li>
          <li><svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20 6 9 17l-5-5" />
            </svg><span data-t="a2">Delivered around Doha</span></li>
          <li><svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20 6 9 17l-5-5" />
            </svg><span data-t="a3">Order in a chat — no app, no account</span></li>
        </ul>
      </div>
    </div>
  </main>

  <footer class="site-foot">
    <div class="wrap">
      <span>Al Jaloui Mart <span aria-hidden="true">·</span> <span data-t="doha">Doha, Qatar</span></span>
      <a href="https://wa.me/{whatsapp}" target="_blank" rel="noopener"><bdi dir="ltr">{wa_pretty}</bdi></a>
      <a href="tel:{phone}"><bdi dir="ltr">{phone_pretty}</bdi></a>
      <a href="mailto:{email}">{email}</a>
    </div>
  </footer>

  <div class="toast" id="toast" role="status" aria-live="polite"></div>

  <script>
    (function () {{
      var AR = {ar_json};
      var EN = {en_json};
      var LANG_KEY = 'ajm_lang';
      var lang = 'en';
      try {{ var v = localStorage.getItem(LANG_KEY); if (v === 'ar' || v === 'en') lang = v; }} catch (e) {{ }}

      function apply() {{
        var dict = lang === 'ar' ? AR : EN;
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
        document.querySelectorAll('[data-t]').forEach(function (el) {{
          var k = el.getAttribute('data-t');
          if (dict[k]) el.textContent = dict[k];
        }});
        document.title = dict.title;
        document.getElementById('shot').alt = dict.name;
        document.getElementById('langBtn').textContent = lang === 'ar' ? 'EN' : 'عربي';
      }}

      /* Delivery details, shared with the shop page under the same key. */
      var COD_KEY = 'ajm_cod';
      var FIELDS = [['ofName', 'name'], ['ofPhone', 'phone'],
                    ['ofAddress', 'address'], ['ofNote', 'note']];
      var cod = {{ name: '', phone: '', address: '', note: '' }};
      try {{
        var saved = JSON.parse(localStorage.getItem(COD_KEY) || '{{}}');
        FIELDS.forEach(function (f) {{
          if (typeof saved[f[1]] === 'string') cod[f[1]] = saved[f[1]].slice(0, 300);
        }});
      }} catch (e) {{ }}

      FIELDS.forEach(function (f) {{
        var el = document.getElementById(f[0]);
        el.value = cod[f[1]];
        el.addEventListener('input', function () {{
          cod[f[1]] = el.value;
          el.setCustomValidity('');
          try {{ localStorage.setItem(COD_KEY, JSON.stringify(cod)); }} catch (e) {{ }}
        }});
      }});

      document.getElementById('orderForm').addEventListener('submit', function (e) {{
        e.preventDefault();
        var dict = lang === 'ar' ? AR : EN;
        var name = cod.name.trim(), phone = cod.phone.trim(), addr = cod.address.trim();
        var digits = phone.replace(/\\D/g, '');
        var bad = null;
        if (!name) bad = ['ofName', dict.required];
        else if (!phone) bad = ['ofPhone', dict.required];
        else if (digits.length < 7 || digits.length > 15) bad = ['ofPhone', dict.badphone];
        else if (!addr) bad = ['ofAddress', dict.required];
        if (bad) {{
          var el = document.getElementById(bad[0]);
          el.setCustomValidity(bad[1]);
          el.reportValidity();
          return;
        }}
        var lines = ['*Al Jaloui Mart — New Order* (Chit #AJM-'
          + Math.floor(1000 + Math.random() * 9000) + ')', '',
          '• {name_en} x1 — QAR {price}', '',
          'Subtotal: QAR {price}', '',
          'Name: ' + name, 'Phone: ' + phone, 'Address: ' + addr];
        if (cod.note.trim()) lines.push('Note: ' + cod.note.trim());
        lines.push('Payment: Cash on Delivery', '', '{url}');
        var url = 'https://wa.me/{whatsapp}?text=' + encodeURIComponent(lines.join('\\n'));
        cod.note = '';
        document.getElementById('ofNote').value = '';
        try {{ localStorage.setItem(COD_KEY, JSON.stringify(cod)); }} catch (e) {{ }}
        say(dict.sending);
        if (!window.open(url, '_blank')) window.location.href = url;
      }});

      document.getElementById('langBtn').addEventListener('click', function () {{
        lang = lang === 'ar' ? 'en' : 'ar';
        try {{ localStorage.setItem(LANG_KEY, lang); }} catch (e) {{ }}
        apply();
      }});

      var toast = document.getElementById('toast'), timer;
      function say(msg) {{
        toast.textContent = msg;
        toast.classList.add('show');
        clearTimeout(timer);
        timer = setTimeout(function () {{ toast.classList.remove('show'); }}, 2600);
      }}

      document.getElementById('copyBtn').addEventListener('click', function () {{
        var url = location.origin + location.pathname;
        var done = function () {{ say((lang === 'ar' ? AR : EN).copied); }};
        if (navigator.clipboard && navigator.clipboard.writeText) {{
          navigator.clipboard.writeText(url).then(done, fallback);
        }} else fallback();
        function fallback() {{
          var t = document.createElement('textarea');
          t.value = url; t.setAttribute('readonly', '');
          t.style.position = 'fixed'; t.style.opacity = '0';
          document.body.appendChild(t); t.select();
          try {{ document.execCommand('copy'); done(); }}
          catch (e) {{ say(url); }}
          document.body.removeChild(t);
        }}
      }});

      apply();
    }})();
  </script>
</body>

</html>
"""


def esc(s):
    return html.escape(s, quote=True)


def pretty_phone(digits):
    d = re.sub(r"\D", "", digits)
    if d.startswith("974") and len(d) == 11:
        return "+974 %s %s" % (d[3:7], d[7:])
    return "+" + d


def build(p):
    cat = CATS.get(p["cat"], {"en": p["cat"], "ar": p["cat"]})
    url = "%s/p/%s" % (SITE, p["slug"])
    price_en = "QAR %d" % p["price"]
    price_ar = "%d ر.ق" % p["price"]
    meta_desc = "%s — %s. %s Order on WhatsApp from Al Jaloui Mart, Doha, Qatar. Cash on delivery." % (
        p["nameEn"], price_en, p["descEn"])
    og_title = "%s — %s | Al Jaloui Mart" % (p["nameEn"], price_en)

    jsonld = """{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": %s,
  "description": %s,
  "image": [%s, %s],
  "sku": %s,
  "category": %s,
  "brand": { "@type": "Brand", "name": "Al Jaloui Mart" },
  "offers": {
    "@type": "Offer",
    "url": %s,
    "priceCurrency": "QAR",
    "price": "%d",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "seller": { "@type": "Store", "name": "Al Jaloui Mart", "url": "%s/" }
  }
}""" % (
        _j(p["nameEn"]), _j(p["descEn"]),
        _j("%s/%s.jpg" % (OG_BASE, p["slug"])), _j(p["img"]),
        _j("AJM-%03d" % p["id"]), _j(cat["en"]), _j(url), p["price"], SITE,
    )

    ar = {
        "title": "%s — %s | الجلوي مارت" % (p["nameAr"], price_ar),
        "name": p["nameAr"], "desc": p["descAr"], "price": price_ar, "cat": cat["ar"],
        "home": "الرئيسية",
        "order": "اطلب على واتساب",
        "copy": "انسخ الرابط للمشاركة",
        "copied": "تم نسخ الرابط.",
        "all": "شاهد كل المنتجات",
        "a1": "الدفع عند الاستلام",
        "a2": "توصيل داخل الدوحة",
        "a3": "اطلب عبر المحادثة — دون تطبيق أو حساب",
        "doha": "الدوحة، قطر",
        "intro": "الدفع عند الاستلام — نحتاج هذه البيانات لتوصيل طلبك.",
        "l_name": "الاسم الكامل",
        "l_phone": "رقم الهاتف",
        "l_addr": "عنوان التوصيل",
        "l_note": "ملاحظة على الطلب (اختياري)",
        "hint": "مثال: ‎+974 5555 1234",
        "required": "يرجى ملء هذا الحقل قبل تأكيد الطلب.",
        "badphone": "يرجى إدخال رقم هاتف صحيح.",
        "disc": "سنراسلك على واتساب لتأكيد طلبك وموعد التوصيل.",
        "sending": "جارٍ فتح واتساب لتأكيد طلبك…",
    }
    en = {
        "title": "%s — %s | Al Jaloui Mart" % (p["nameEn"], price_en),
        "name": p["nameEn"], "desc": p["descEn"], "price": price_en, "cat": cat["en"],
        "home": "Home", "order": "Order this on WhatsApp", "copy": "Copy link to share",
        "copied": "Link copied.", "all": "See all products",
        "a1": "Cash on delivery", "a2": "Delivered around Doha",
        "a3": "Order in a chat — no app, no account",
        "doha": "Doha, Qatar",
        "intro": "Cash on delivery — we need these to bring your order to you.",
        "l_name": "Full name", "l_phone": "Phone number",
        "l_addr": "Delivery address", "l_note": "Order note (optional)",
        "hint": "e.g. +974 5555 1234",
        "required": "Please fill in this field before confirming your order.",
        "badphone": "Please enter a valid phone number.",
        "disc": "We'll message you on WhatsApp to confirm your order and delivery time.",
        "sending": "Opening WhatsApp to confirm your order…",
    }

    return PAGE.format(
        title=esc(en["title"]), meta_desc=esc(meta_desc), og_title=esc(og_title),
        url=esc(url), og_image=esc("%s/%s.jpg" % (OG_BASE, p["slug"])),
        img=esc(p["img"]), r2_host=R2_HOST, price=p["price"],
        name_en=esc(p["nameEn"]), desc_en=esc(p["descEn"]), cat_en=esc(cat["en"]),
        whatsapp=WHATSAPP, wa_pretty=pretty_phone(WHATSAPP),
        phone=PHONE, phone_pretty=pretty_phone(PHONE), email=EMAIL,
        jsonld=jsonld, css=CSS,
        ar_json=_js(ar), en_json=_js(en),
    )


def _j(s):
    """JSON string literal."""
    import json
    return json.dumps(s, ensure_ascii=False)


def _js(d):
    """JS object literal, safe to inline inside <script>."""
    import json
    return json.dumps(d, ensure_ascii=False).replace("</", "<\\/")


def _q(s):
    from urllib.parse import quote
    return quote(s, safe="")


def write_sitemap(products):
    path = os.path.join(ROOT, "sitemap.xml")
    today = datetime.date.today().isoformat()
    urls = ['  <url>\n    <loc>%s/</loc>\n    <lastmod>%s</lastmod>\n'
            '    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>' % (SITE, today)]
    for p in products:
        urls.append('  <url>\n    <loc>%s/p/%s</loc>\n    <lastmod>%s</lastmod>\n'
                    '    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>'
                    % (SITE, p["slug"], today))
    body = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")
    io.open(path, "w", encoding="utf-8", newline="\n").write(body)
    print("sitemap.xml  ->  %d urls" % (len(products) + 1))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    keep = set()
    for p in PRODUCTS:
        name = p["slug"] + ".html"
        keep.add(name)
        io.open(os.path.join(OUT_DIR, name), "w", encoding="utf-8", newline="\n").write(build(p))
        print("p/%-38s %s/p/%s" % (name, SITE, p["slug"]))

    for stale in sorted(set(os.listdir(OUT_DIR)) - keep):
        if stale.endswith(".html"):
            os.remove(os.path.join(OUT_DIR, stale))
            print("removed stale p/%s" % stale)

    write_sitemap(PRODUCTS)


if __name__ == "__main__":
    main()
