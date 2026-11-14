#!/usr/bin/env python3
"""Build the site: the home page (the walk), /work and the not-found page.

The files in walk/ each hold one page's styles, markup and script without the
document shell, and address their pictures as img/... so they can be previewed
on their own. This script adds the shell and the metadata, points the pictures
at /assets/img/walk/ and the links at the public routes, and writes index.html,
work.html and 404.html at the site root.

It also writes _redirects (the old site's addresses, sent to where that content
lives now), sitemap.xml and robots.txt.

    python3 scripts/build_walk.py
"""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "walk"
SITE_URL = "https://www.caneandcamera.com"
IMG = "/assets/img/walk/"

PAGES = [
    {
        "source": "walk.page.html",
        "out": "index.html",
        "route": "/",
        "title": "Cane & Camera | Naturalist Portfolio of Vinay Chittora",
        "description": (
            "Cane & Camera is Vinay Chittora's naturalist portfolio for wildlife films, field photography, "
            "scouting, and conservation storytelling from Rajasthan."
        ),
        "image": IMG + "gib-sun.jpg",
        "changefreq": "weekly",
        "priority": "1.0",
    },
    {
        "source": "work.page.html",
        "out": "work.html",
        "route": "/work",
        "title": "My work | Cane & Camera",
        "description": (
            "Photographs, films, software and field data by Vinay Chittora from Kota, Rajasthan: "
            "citizen science in Mukundara Hills Tiger Reserve, the FALCON field recorder, mhtr.in and wildlife films."
        ),
        "image": IMG + "gib-sun.jpg",
        "changefreq": "monthly",
        "priority": "0.9",
    },
    {
        # Served by the host, with a 404 status, for any address that does not exist.
        # It has no route of its own, so it stays out of the sitemap and out of search.
        "source": "404.page.html",
        "out": "404.html",
        "route": None,
        "title": "Nothing here | Cane & Camera",
    },
]

# The site this one replaced had a page for each of these. Each old address goes to where that content lives now.
MOVED = [
    ("/gallery", "/work#photographs"),
    ("/landscapes", "/work#photographs"),
    ("/documentaries", "/work#films"),
    ("/contact", "/work#write"),
    ("/work-with-me", "/work#write"),
    ("/about", "/"),
]

SAME_AS = [
    "https://instagram.com/caneandcamera",
    "https://www.youtube.com/@CaneAndCamera/videos",
    "https://mhtr.in",
]

JSON_LD = [
    {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": SITE_URL + "/#vinay-chittora",
        "name": "Vinay Chittora",
        "jobTitle": "Naturalist, Wildlife Filmmaker, Field Storyteller",
        "url": SITE_URL + "/",
        "homeLocation": {"@type": "Place", "name": "Rajasthan, India"},
        "sameAs": SAME_AS,
    },
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": SITE_URL + "/#website",
        "name": "Cane & Camera",
        "url": SITE_URL + "/",
        "publisher": {"@id": SITE_URL + "/#vinay-chittora"},
    },
]


def split(fragment):
    """Return the font link and style block, and everything after them.

    A page body opens with a title and a meta line that only the preview host
    reads; both are dropped here, because the shell below carries the real ones.
    """
    end = fragment.index("</style>") + len("</style>")
    head, body = fragment[:end], fragment[end:]
    head = re.sub(r"<title>.*?</title>\s*", "", head, count=1, flags=re.S)
    head = re.sub(r'<meta name="claude:[^>]*>\s*', "", head)
    return head.strip(), body.strip()


def localise(text):
    """Point pictures and page links at their public addresses."""
    text = text.replace('"img/', '"' + IMG).replace("'img/", "'" + IMG)
    text = text.replace('href="work.html"', 'href="/work"').replace('href="life.html"', 'href="/"')
    return text


def document(page, head, body):
    title = escape(page["title"])
    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"  <title>{title}</title>",
    ]
    if page["route"] is None:
        lines.append('  <meta name="robots" content="noindex,follow">')
    else:
        url = SITE_URL + page["route"]
        description = escape(page["description"], quote=True)
        image = SITE_URL + page["image"]
        lines += [
            f'  <meta name="description" content="{description}">',
            '  <meta name="robots" content="index,follow,max-image-preview:large">',
            '  <meta name="author" content="Vinay Chittora">',
            f'  <link rel="canonical" href="{url}">',
            '  <meta property="og:type" content="website">',
            '  <meta property="og:site_name" content="Cane &amp; Camera">',
            f'  <meta property="og:title" content="{title}">',
            f'  <meta property="og:description" content="{description}">',
            f'  <meta property="og:url" content="{url}">',
            f'  <meta property="og:image" content="{image}">',
            '  <meta name="twitter:card" content="summary_large_image">',
            f'  <meta name="twitter:title" content="{title}">',
            f'  <meta name="twitter:description" content="{description}">',
            f'  <meta name="twitter:image" content="{image}">',
        ]
    lines += [
        '  <link rel="icon" type="image/png" href="/assets/img/ico/favicon.png">',
        '  <link rel="preconnect" href="https://fonts.googleapis.com">',
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    ]
    if page["route"] is not None:
        lines += [
            '  <script type="application/ld+json">' + json.dumps(block, ensure_ascii=False) + "</script>"
            for block in JSON_LD
        ]
    lines += [head, "</head>", "<body>", body, "</body>", "</html>", ""]
    return "\n".join(lines)


def redirects():
    """One line per old address, in the form the host reads: from, to, status.

    The host matches an address exactly, so each page is listed the four ways it could be asked for.
    """
    lines = ["/favicon.ico /assets/img/ico/favicon.png 301"]
    for old, new in MOVED:
        for form in (old, old + "/", old + ".html", old + "/index.html"):
            lines.append(f"{form} {new} 301")
    return "\n".join(lines) + "\n"


def sitemap():
    today = datetime.now(timezone.utc).date().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in PAGES:
        if page["route"] is not None:
            lines.append(
                f"  <url><loc>{SITE_URL}{page['route']}</loc><lastmod>{today}</lastmod>"
                f"<changefreq>{page['changefreq']}</changefreq><priority>{page['priority']}</priority></url>"
            )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


ROBOTS = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""


def build():
    for page in PAGES:
        fragment = (SOURCE / page["source"]).read_text(encoding="utf-8")
        head, body = split(localise(fragment))
        (ROOT / page["out"]).write_text(document(page, head, body), encoding="utf-8")
        print(f"built {page['out']} from walk/{page['source']}")
    for name, text in (("_redirects", redirects()), ("sitemap.xml", sitemap()), ("robots.txt", ROBOTS)):
        (ROOT / name).write_text(text, encoding="utf-8")
        print(f"wrote {name}")


if __name__ == "__main__":
    build()
