# MD Work — website

Landing page for **MD Work**, the simple work notebook for daily and hourly workers,
available on Google Play:

<https://play.google.com/store/apps/details?id=app.mdwork.notebook>

Live: <https://mdnexa9.github.io/saf7atta7mil/>

## What is here

Static site (no build step) served by a tiny Cloudflare Worker that forwards requests
to the static asset binding and adds a few security headers.

```
public/
  index.html            page markup (English defaults, data-i18n keys)
  assets/css/style.css  design system, dark + light themes, phone mockups
  assets/js/i18n.js     translations: en, it, fr, de, ar (RTL), hi
  assets/js/app.js      language + theme switching, sticky bar, reveal, install prompt
  assets/img/           icon set and social image (generated)
  manifest.webmanifest  PWA manifest
  robots.txt, sitemap.xml
worker.js               Workers entrypoint (assets + headers)
freebuff.deploy.json     deploy manifest used by Sites
wrangler.jsonc           local Wrangler preview config
scripts/generate_assets.py  regenerates icons + og.png
```

## GitHub Pages

`.github/workflows/pages.yml` publishes the `public/` folder to GitHub Pages on
every push to `main`. Pages must use **Source: GitHub Actions**; the first run
enables it, and if it cannot, set that source once in Settings → Pages.

The site is served from a subpath (`/saf7atta7mil/`), so asset references in
`index.html`, the web manifest, `robots.txt` and `sitemap.xml` are relative or
absolute against that URL. Keep them that way instead of using `/assets/...`.

## Local preview

```bash
npx wrangler dev --port 8787     # http://localhost:8787
```

Icons and the social image are drawn by `python3 scripts/generate_assets.py`
(requires Pillow). Change `STROKES` there to adjust the MW monogram.

## Content rules

- Only facts that match the Play store listing and the app itself (free with ads,
  no account, local records, 8 languages, EUR/USD/GBP/TND/AED, day or hour mode).
- Every visible string lives in `public/assets/js/i18n.js`; add a language by adding
  a dictionary with the same keys and an `<option>` in the header.
- Download buttons point at the Play listing above. Keep that id exact:
  `app.mdwork.notebook`.
