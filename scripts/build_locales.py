#!/usr/bin/env python3
"""Build the translated copies of the landing page.

public/index.html is the English page. This script writes public/<lang>/index.html
for every other language using the dictionaries in public/assets/js/i18n, with
the text already baked in, its own canonical URL, hreflang alternates and
localized structured data — so search engines can index each language instead of
only English. It also keeps the English page's hreflang block and sitemap.xml in
sync.

Run it after editing public/index.html or any dictionary:

    python3 scripts/build_locales.py
"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
BASE = "https://mdnexa9.github.io/Ta7mil11/"
PLAY = "https://play.google.com/store/apps/details?id=app.mdwork.notebook"
LANGS = ["en", "it", "fr", "de", "ar", "hi"]
BUILT = ["it", "fr", "de", "ar", "hi"]

# Page metadata per language. The dictionaries drive the visible text; these two
# strings only live in <head>, which the runtime never swaps.
SEO = {
    "it": (
        "MD Work — App per ore di lavoro, guadagni e spese",
        "MD Work registra giorni lavorati, ore, guadagni e spese: sai quanto ti resta a fine mese. Gratuito su Google Play, offline e senza account.",
    ),
    "fr": (
        "MD Work — Suivi des jours travaillés, gains et dépenses",
        "MD Work enregistre vos jours travaillés, vos heures, vos gains et vos dépenses : vous savez ce qu'il vous reste en fin de mois. Gratuit sur Google Play, hors ligne, sans compte.",
    ),
    "de": (
        "MD Work — Arbeitszeiten, Verdienst und Ausgaben im Blick",
        "MD Work erfasst Arbeitstage, Stunden, Verdienst und Ausgaben – du siehst, was am Monatsende bleibt. Kostenlos bei Google Play, offline, ohne Konto.",
    ),
    "ar": (
        "MD Work — تطبيق تسجيل أيام العمل والأرباح والمصاريف",
        "MD Work يسجّل أيام العمل والساعات والأرباح والمصاريف، فتعرف ما تبقّى في نهاية الشهر. مجاني على Google Play، ويعمل دون إنترنت ودون حساب.",
    ),
    "hi": (
        "MD Work — काम के दिन, कमाई और खर्च का हिसाब",
        "MD Work काम के दिन, घंटे, कमाई और खर्च दर्ज करता है — महीने के अंत में कितना बचा, साफ़ दिखता है। Google Play पर मुफ़्त, बिना इंटरनेट और बिना अकाउंट।",
    ),
}
OG_LOCALE = {"en": "en_US", "it": "it_IT", "fr": "fr_FR", "de": "de_DE", "ar": "ar_AR", "hi": "hi_IN"}
RTL = {"ar", "he", "fa", "ur"}

TAG = re.compile(
    r'(<(?P<tag>[a-zA-Z][a-zA-Z0-9]*)\b[^>]*data-i18n="(?P<key>[^"]+)"[^>]*>)(?P<text>.*?)(?P<close></(?P=tag)>)',
    re.S,
)


def read_dictionary(code):
    source = (PUBLIC / "assets" / "js" / "i18n" / f"{code}.js").read_text(encoding="utf-8")
    pairs = re.findall(r'"([^"]+)"\s*:\s*("(?:[^"\\]|\\.)*")', source)
    return {key: json.loads(value) for key, value in pairs}


def page_url(code):
    return BASE if code == "en" else f"{BASE}{code}/"


def alternates():
    lines = ['<link rel="alternate" hreflang="%s" href="%s">' % (code, page_url(code)) for code in LANGS]
    lines.append('<link rel="alternate" hreflang="x-default" href="%s">' % page_url("en"))
    return "\n".join(lines)


def structured_data(code, dictionary):
    url = page_url(code)
    description = dictionary.get("hero.sub", "").replace("\n", " ").strip()
    faq = [(dictionary.get(k + ".q"), dictionary.get(k + ".a")) for k in ("fa1", "fa2", "fa3", "fa4", "fa6", "fa7")]
    graph = [
        {
            "@type": "SoftwareApplication",
            "@id": url + "#app",
            "name": "MD Work",
            "operatingSystem": "Android 7.0 and up",
            "applicationCategory": "ProductivityApplication",
            "applicationSubCategory": "Work hours and expense tracker",
            "url": url,
            "downloadUrl": PLAY,
            "installUrl": PLAY,
            "sameAs": [PLAY],
            "description": description,
            "inLanguage": [code],
            "isAccessibleForFree": True,
            "screenshot": [f"{BASE}assets/img/play/{n}.webp" for n in (
                "01-home", "02-day-hours", "03-history", "04-expenses",
                "05-quick-tools", "06-lists", "07-languages", "08-reports")],
            "author": {"@type": "Organization", "name": "MD Nexa",
                       "url": "https://play.google.com/store/apps/developer?id=MD+Nexa"},
            "publisher": {"@id": BASE + "#org"},
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        },
        {"@type": "Organization", "@id": BASE + "#org", "name": "MD Nexa",
         "url": "https://play.google.com/store/apps/developer?id=MD+Nexa", "sameAs": [PLAY]},
        {"@type": "WebSite", "@id": BASE + "#site", "url": BASE, "name": "MD Work",
         "inLanguage": "en", "publisher": {"@id": BASE + "#org"}},
        {"@type": "FAQPage", "@id": url + "#faq",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in faq if q and a]},
    ]
    body = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    return '<script type="application/ld+json">\n' + body + "\n</script>"


def translate_text(source, dictionary):
    missing = set()

    def replace(match):
        value = dictionary.get(match.group("key"))
        if value is None:
            missing.add(match.group("key"))
            return match.group(0)
        return match.group(1) + html.escape(value, quote=False) + match.group("close")

    return TAG.sub(replace, source), missing


def localize(source, dictionary, code):
    title, description = SEO[code]
    url = page_url(code)

    source = re.sub(
        r'<html lang="en" dir="ltr" data-theme="dark">',
        '<html lang="%s" dir="%s" data-theme="dark" data-base="../">' % (code, "rtl" if code in RTL else "ltr"),
        source,
        count=1,
    )
    source = re.sub(r"<title>.*?</title>", "<title>%s</title>" % html.escape(title, quote=False), source, count=1, flags=re.S)
    source = re.sub(r'<meta name="description" content="[^"]*">',
                    '<meta name="description" content="%s">' % html.escape(description, quote=False), source, count=1)
    source = source.replace('<link rel="canonical" href="%s">' % BASE, '<link rel="canonical" href="%s">' % url, 1)
    source = re.sub(r'<meta property="og:locale" content="[^"]*">',
                    '<meta property="og:locale" content="%s">' % OG_LOCALE[code], source, count=1)
    source = re.sub(r'<meta property="og:url" content="[^"]*">',
                    '<meta property="og:url" content="%s">' % url, source, count=1)
    source = re.sub(r'<meta property="og:title" content="[^"]*">',
                    '<meta property="og:title" content="%s">' % html.escape(title, quote=False), source, count=1)
    source = re.sub(r'<meta property="og:description" content="[^"]*">',
                    '<meta property="og:description" content="%s">' % html.escape(description, quote=False), source, count=1)

    source, _ = translate_text(source, dictionary)

    start = source.index('<script type="application/ld+json">')
    end = source.index("</script>", start) + len("</script>")
    source = source[:start] + structured_data(code, dictionary) + source[end:]

    # Relative asset paths gain one level; absolute URLs keep their own.
    marker = "\x00ABS\x00"
    source = source.replace(BASE + "assets/", marker)
    source = source.replace('"assets/', '"../assets/').replace(", assets/", ", ../assets/")
    source = source.replace(marker, BASE + "assets/")
    source = source.replace('href="manifest.webmanifest"', 'href="../manifest.webmanifest"')
    # The text is baked in; the dictionary script is not needed here.
    source = source.replace('<script src="../assets/js/i18n/en.js" defer></script>\n', "")
    return source


def main():
    english = (PUBLIC / "index.html").read_text(encoding="utf-8")
    if 'hreflang="x-default"' not in english:
        english = english.replace(
            '<link rel="canonical" href="%s">' % BASE,
            '<link rel="canonical" href="%s">\n%s' % (BASE, alternates()),
            1,
        )
        (PUBLIC / "index.html").write_text(english, encoding="utf-8")
        print("index.html: hreflang added")

    for code in BUILT:
        dictionary = read_dictionary(code)
        page = localize(english, dictionary, code)
        _, missing = translate_text(english, dictionary)
        target = PUBLIC / code / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")
        print(f"{code}: {target.relative_to(ROOT)} written" + (f" — missing keys: {sorted(missing)}" if missing else ""))

    urls = "\n".join(
        "  <url>\n    <loc>%s</loc>\n    <lastmod>2026-11-23</lastmod>\n"
        "    <changefreq>monthly</changefreq>\n    <priority>%s</priority>\n  </url>"
        % (page_url(code), "1.0" if code == "en" else "0.8")
        for code in LANGS
    )
    (PUBLIC / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + urls + "\n</urlset>\n",
        encoding="utf-8",
    )
    print("sitemap.xml: %d URLs" % len(LANGS))


if __name__ == "__main__":
    main()
