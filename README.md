# MD Work — website

Landing page for **MD Work**, the simple work notebook for daily and hourly workers,
available on Google Play:

<https://play.google.com/store/apps/details?id=app.mdwork.notebook>

Live: <https://mdnexa9.github.io/Ta7mil11/>

## What is here

Static site (no build step). It is published by the GitHub Pages workflow, and the
same files are also served by a tiny Cloudflare Worker for the Sites deployment.

```
public/
  index.html              page markup (English copy, data-i18n keys)
  assets/css/style.css    design system, dark + light themes, phone mockups
  assets/js/i18n/<lang>.js  one dictionary per language: en, it, fr, de, ar (RTL), hi
  assets/js/app.js        language + theme switching, sticky bar, install prompt
  assets/img/             icon set and social image (generated)
  manifest.webmanifest    PWA manifest
  robots.txt, sitemap.xml
worker.js                 Workers entrypoint (assets + headers)
freebuff.deploy.json      deploy manifest used by Sites
wrangler.jsonc            local Wrangler preview config
scripts/generate_assets.py  regenerates icons + og.png
```

## Language loading

English is the page language: `index.html` ships English copy and loads
`assets/js/i18n/en.js` only. The other dictionaries are fetched when a visitor
picks a language, so the first visit stays small (~6 KB of JS instead of ~40 KB).

To add a language: add `public/assets/js/i18n/<code>.js` with the same keys as
`en.js`, add the code to `LANGS` in `app.js`, and add an `<option>` to the header
select.

## GitHub Pages

`.github/workflows/pages.yml` publishes `public/` to GitHub Pages on every push to
`main`. Pages must use **Source: GitHub Actions**; the workflow enables it on the
first run, and if it cannot, set that source once in Settings → Pages.

The site is served from a subpath (`/Ta7mil11/`), so asset references in
`index.html`, the web manifest, `robots.txt` and `sitemap.xml` are relative or
absolute against that URL. Keep them that way instead of using `/assets/...`.

## Local preview

```bash
npx wrangler dev --port 8787     # http://localhost:8787
```

Icons and the social image are drawn by `python3 scripts/generate_assets.py`
(requires Pillow). Change `STROKES` there to adjust the MW monogram.

## Content rules

- Only facts that match the Play listing and the app itself (free with ads, no
  account, local records, 28 languages, EUR/USD/GBP/TND/AED, day or hour mode,
  payments owed, backup file, reminders).
- Download buttons point at the Play listing above. Keep that id exact:
  `app.mdwork.notebook`.

## Translated pages

`public/index.html` is the English page, and `scripts/build_locales.py` writes
`public/it/`, `/fr/`, `/de/`, `/ar/` and `/hi/` from the same HTML with the text
already translated from `public/assets/js/i18n/`, plus a canonical URL, hreflang
alternates and localized structured data. Rebuild them whenever the page or a
dictionary changes:

```bash
python3 scripts/build_locales.py
```

That script also keeps the English page's hreflang block and `sitemap.xml` in
sync. Pages inside a language folder reach shared files through `../assets/` and
declare `data-base="../"`, which `app.js` uses when it needs a dictionary.
