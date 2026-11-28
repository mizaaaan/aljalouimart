# Al Jaloui Mart — Client Handover Guide

Your online shop is a single static website. There is no server, database or monthly
software fee to maintain. Customers browse products, build an order list ("chit") and
send it to your WhatsApp, or fill in delivery details for **Cash on Delivery** (which
also arrives as a WhatsApp message).

> **Orders are not stored anywhere except in your WhatsApp chat.** Keep the shop phone
> (+974 7473 3400) logged in to WhatsApp and check it regularly.

---

## ✅ Before you go live — please confirm these

| # | Item | Why it matters |
|---|------|----------------|
| 1 | **Prices** | The four prices in the site are *placeholders* (the original prices were in Bangladeshi Taka; they were converted to Qatari Riyals at roughly 33 ৳ = 1 QAR). Replace them with your real prices. |
| 2 | **Product list** | Only 4 products are shown. Artwork for 11 more products is included in `assets/products/` and can be switched on (see "Add a product"). Confirm the brands (Napa, Seclo, Fexo, ORSaline-N) are what you actually stock in Qatar. |
| 3 | **Medicines** | The site lists medicine and a medicines category. Please confirm you are permitted to sell and deliver medicines online in Qatar; if not, remove that category and product. |
| 4 | **Facebook page** | `facebook.com/aljalouimart` could not be verified. Open it and confirm it is yours, or change it (see "Change phone numbers"). |
| 5 | **Missing shop information** | The site doesn't state opening hours, delivery charge, minimum order, delivery areas or a street address. Customers will ask — consider adding them to the About text. |
| 6 | **Web address** | The site currently lives at `https://aljaloui.com/`. See "Use your own domain" below. |

---

## Day-to-day changes

Open `index.html` in any text editor (VS Code, Notepad++, even Notepad) and use Search (Ctrl+F).

### Change a price
Search `const PRODUCTS`. Find the product and edit `price:`. Prices are in **QAR**; decimals are fine (`price:3.5`).

### Add a product
Copy one whole line starting with `{id:` inside `PRODUCTS`, paste it below, and change:
`id` (must be a **new unique number**), `cat` (`medicine`, `baby`, `personal`, `devices` or `wellness`),
`img` (picture path), `nameEn` / `nameAr`, `descEn` / `descAr`, `price`.
Set `rx:true` for prescription-only items — the customer is then reminded to send a photo of the prescription.

Spare artwork already in `assets/products/`: multivitamin, seclo-20mg, fexo-120mg, orsaline-n, gripe-water, baby-lotion,
surgical-mask, antiseptic-liquid, blood-pressure-monitor, glucometer, protein-supplement.

### Remove a product
Delete its whole `{id:... }` line (a category with no products hides itself automatically). Mind the commas: every line ends with a comma **except the last one**.

### Use a real photo instead of the drawing
Put the photo (square, ~800×800 px, `.jpg`/`.png`/`.webp`) in `assets/products/` and set that product's `img:` to its path.

### Change the logo (replace it or resize it)
All logo pictures live in `assets/brand/`. To **replace** one, overwrite the file with a new transparent PNG using the *same file name*:

| File | Where it appears |
|------|------------------|
| `logo-horizontal.png` | Top header (full colour) |
| `logo-horizontal-light.png` | Footer, on the dark blue background (all-yellow version) |
| `logo-stacked.png` | Big round badge on the home page (also the web-search logo and link-preview picture) |
| `logo-mark.png` | Small round badge in the About section |

To make a logo **bigger or smaller**, open `index.html`, search `LOGO SIZES` and change the numbers
(`--logo-h` = header, `--logo-h-footer` = footer, `--hero-d` = home badge size, `--hero-logo-scale` = how much of the badge the logo fills, `--seal-d` = round badge in the About section).
Phones and computers are handled automatically; the logo never overflows the screen.
Your original high-resolution logo files are kept in `brand-source/` (not used by the website itself).
If you also change the logo, re-run `tools/make_brand_assets.py`, `tools/make_icons.py` and `tools/make_og.py` to refresh the browser tab icon, phone home-screen icon and the picture shown when the link is shared.

### The home-page top section (hero)
Edit the wording in `const I18N` (`hero_title_1`, `hero_title_2`, `hero_title_3`, `hero_sub`, `hero_cta_browse`, `hero_cta_contact`) — English and Arabic blocks.

### Change phone numbers, WhatsApp, email, Facebook
Search `const CONTACT`. Change the values there — the footer, buttons and floating WhatsApp button all update from it.
The WhatsApp number must be digits only with the country code (e.g. `97474733400`).
Also change the phone and email in the `<script type="application/ld+json">` block near the top (this is the data Google shows about your shop).

### Change wording (English / Arabic)
Search `const I18N`. There is an `en` block and an `ar` block; each line is `key:'text'`. Keep the quote marks.

---

## Publishing changes (GitHub Pages)
1. Edit the file(s).
2. Upload/commit them to the `main` branch of the repository.
3. Wait about one minute — the live site updates automatically.

Always open the live site on your phone after a change and place a test order (you can close WhatsApp without sending).

## Use your own domain (optional)
1. Buy a domain (e.g. `aljaloui.qa` via a registrar).
2. In the repository: **Settings → Pages → Custom domain** → enter it and save.
3. At your domain provider add the DNS records listed in `README.md`.
4. When HTTPS is ready, tick **Enforce HTTPS**.
5. Run once on a computer with Python: `python3 tools/set-domain.py https://www.your-domain.com/`
   (updates the addresses used by Google and WhatsApp/Facebook link previews). Commit the result.

## Support files you can ignore
`robots.txt`, `sitemap.xml`, `site.webmanifest`, `favicon.ico` and the other icons, `404.html`, `og-image.png` (the picture shown when the link is shared),
and the `tools/` folder (scripts to regenerate images / change the domain).

## What was tested
Phones (320–414 px), tablet and desktop widths; English and Arabic (right-to-left); cart add/remove/limits;
Cash-on-Delivery form validation; the exact WhatsApp message text; saved cart after reload; keyboard use;
Escape-to-close; pop-up-blocker fallback. See `README.md` for the technical change list.
