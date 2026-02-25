#!/usr/bin/env python3
"""Build static HTML pages from shared templates + JSON content."""
from __future__ import annotations

import json
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent
PHOTOS_JSON = ROOT / "assets/img/gallery/generated/photos.json"
DOCS_JSON = ROOT / "data/documentaries.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def largest_variant(variants: dict) -> dict | None:
    if not variants:
        return None
    sizes = sorted((int(k) for k in variants.keys()), reverse=True)
    return variants[str(sizes[0])] if sizes else None


def srcset(variants: dict) -> str:
    pairs = []
    for size in sorted((int(k) for k in variants.keys())):
        variant = variants[str(size)]
        pairs.append(f"{variant['src']} {size}w")
    return ", ".join(pairs)


def render_header() -> str:
    return """<header class="site-header">
  <a href="index.html" class="logo"><img src="assets/img/ico/logo.svg" alt="Cane & Camera logo"/><span>Cane & Camera</span></a>
  <nav>
    <a href="gallery.html"><img src="assets/img/ico/icon-wildlife.png" alt="Wildlife"/></a>
    <a href="documentaries.html"><img src="assets/img/ico/icon-documentaries.png" style="filter: invert()" alt="Documentaries" /></a>
    <a href="https://www.youtube.com/@CaneAndCamera/videos" target="_blank" rel="noopener"><img src="assets/img/ico/icon-youtube.png" alt="YouTube"/></a>
    <a href="https://instagram.com/caneandcamera" target="_blank" rel="noopener"><img src="assets/img/ico/icon-ig.png" alt="Instagram" /></a>
    <a href="about.html"><img src="assets/img/ico/icon-about.png" alt="About" /></a>
  </nav>
</header>"""

def render_footer() -> str:
    return """<footer class=\"site-footer\">\n  <div class=\"footer-grid\">\n    <div>\n      <p><b><a href=\"mailto:hello@caneandcamera.com\">hello@caneandcamera.com</a></b></p>\n      <p><script type=\"text/javascript\" src=\"https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js\" data-name=\"bmc-button\" data-slug=\"CaneAndCamera\" data-color=\"#FFDD00\" data-emoji=\"☕\"  data-font=\"Cookie\" data-text=\"Buy me a coffee\" data-outline-color=\"#000000\" data-font-color=\"#000000\" data-coffee-color=\"#ffffff\" ></script></p>\n    </div>\n    <div>\n      <h4>Follow</h4>\n      <p>\n        <a href=\"https://www.patreon.com/cw/CaneAndCamera\" target=\"_blank\" rel=\"noopener\">Patreon</a> ·\n        <a href=\"https://instagram.com/caneandcamera\" target=\"_blank\" rel=\"noopener\">Instagram</a> · \n        <a href=\"https://www.youtube.com/@CaneAndCamera/videos\" target=\"_blank\" rel=\"noopener\">YouTube</a>\n       </p>\n    </div>\n    <div>\n      <h4>Legal</h4>\n      <p>© 2025 Cane &amp; Camera · All rights reserved.</p>\n    </div>\n  </div>\n</footer>"""


def render_page(*, title: str, description: str, body: str, canonical_path: str, extra_css: str = "", extra_scripts: str = "") -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(title)}</title>
  <meta name=\"description\" content=\"{escape(description)}\">
  <meta name=\"author\" content=\"Cane & Camera\">
  <meta name=\"keywords\" content=\"wildlife photography, nature photography, conservation storytelling, Rajasthan wildlife, India birds, Cane and Camera\">
  <meta property=\"og:title\" content=\"{escape(title)}\">
  <meta property=\"og:description\" content=\"{escape(description)}\">
  <meta property=\"og:type\" content=\"website\">
  <link rel=\"canonical\" href=\"https://www.caneandcamera.com/{escape(canonical_path)}\">
  <meta name=\"facebook-domain-verification\" content=\"9sb354a61i9s65n18ijqjp9av800ht\" />
  <link rel=\"icon\" type=\"image/png\" href=\"assets/img/ico/favicon.png\">
  <link rel=\"preload\" href=\"assets/css/style.css\" as=\"style\">
  <link rel=\"stylesheet\" href=\"assets/css/style.css\">
  <link rel=\"preconnect\" href=\"https://cdn.shopify.com\" crossorigin>
  {extra_css}
  <script defer src=\"assets/js/main.js\"></script>
  {extra_scripts}
</head>
<body>
{render_header()}
{body}
{render_footer()}
</body>
</html>
"""


def render_gallery_cards(items: list[dict]) -> str:
    cards = []
    for photo in items:
        variant = largest_variant(photo.get("variants", {}))
        if not variant:
            continue

        meta_bits = []
        if photo.get("datetime"):
            meta_bits.append(f"<time class=\"muted\">{escape(photo['datetime'])}</time>")
        if photo.get("camera"):
            meta_bits.append(f"<span class=\"muted\">{escape(photo['camera'])}</span>")
        if photo.get("lens"):
            meta_bits.append(f"<span class=\"muted\">{escape(photo['lens'])}</span>")

        joined_meta = f" · {' · '.join(meta_bits)}" if meta_bits else ""
        exif = f"<div class=\"muted\">{escape(photo['exif'])}</div>" if photo.get("exif") else ""
        desc = f"<div class=\"cc-desc\">{escape(photo['description'])}</div>" if photo.get("description") else ""
        img_srcset = srcset(photo.get("variants", {}))

        cards.append(f"""<article class=\"cc-card\">
  <img class=\"cc-thumb\" src=\"{escape(variant['src'])}\" srcset=\"{escape(img_srcset)}\" sizes=\"(min-width: 1200px) 33vw, (min-width: 800px) 50vw, 100vw\" width=\"{variant['w']}\" height=\"{variant['h']}\" loading=\"lazy\" decoding=\"async\" alt=\"{escape((photo.get('title') or photo.get('slug') or 'Photo').strip())}\">
  <div class=\"cc-meta\">
    <strong>{escape((photo.get('title') or photo.get('slug') or 'Untitled').strip())}</strong>{joined_meta}
    {exif}
    {desc}
  </div>
</article>""")

    return "\n".join(cards)


def build_gallery_page(gallery_keys: tuple[str, ...], title: str, description: str, out_file: str):
    normalized = {k.lower() for k in gallery_keys}
    photos = [p for p in read_json(PHOTOS_JSON) if p.get("gallery", "").lower() in normalized]
    photos.sort(key=lambda item: item.get("datetime", ""), reverse=True)
    gallery_markup = render_gallery_cards(photos)

    body = f"""<main class=\"wrap\">
  <section class=\"gallery-header\">
    <h1>{escape(title)}</h1>
    <p>{escape(description)}</p>
    <div id=\"cc-masonry\" class=\"cc-masonry\">{gallery_markup}</div>
  </section>
</main>
<!-- Lightbox modal -->
<div class=\"lgx\" id=\"lgx\" aria-hidden=\"true\">
  <img class=\"lgx__img\" alt=\"\">
  <div class=\"lgx__ui\">
    <button class=\"lgx__btn lgx__close\" aria-label=\"Close (Esc)\">✕</button>
    <button class=\"lgx__btn lgx__prev\"  aria-label=\"Previous (←)\">←</button>
    <button class=\"lgx__btn lgx__next\"  aria-label=\"Next (→)\">→</button>
    <div class=\"lgx__ctrl lgx__bar\">
      <button class=\"lgx__btn lgx__play\"  aria-label=\"Start slideshow (Space)\">▶</button>
      <button class=\"lgx__btn lgx__pause\" aria-label=\"Pause slideshow (Space)\" style=\"display:none;\">⏸</button>
    </div>
    <div class=\"lgx__caption\" role=\"note\"></div>
  </div>
</div>"""

    extra_css = """<style>
  .cc-masonry { column-width: 320px; column-gap: 16px; }
  @media (min-width: 1200px){ .cc-masonry { column-width: 360px; } }
  .cc-card { break-inside: avoid; margin: 0 0 16px; background:#111; border-radius:12px; overflow:hidden; border:1px solid #222; }
  .cc-thumb { display:block; width:100%; height:auto; background:#0b0b0b; }
  .cc-meta { padding:10px 12px 12px; color:#ddd; font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif; }
  .cc-meta strong { color:#fff; }
  .cc-meta .muted { opacity:.75; }
</style>"""

    page = render_page(
        title=f"Cane & Camera — {title}",
        description=description,
        body=body,
        canonical_path=out_file,
        extra_css=extra_css,
        extra_scripts='<script defer src="assets/js/gallery-lightbox.js"></script>',
    )
    (ROOT / out_file).write_text(page, encoding="utf-8")


def build_documentaries_page():
    videos = read_json(DOCS_JSON)
    cards = []
    for v in videos:
        cards.append(f"""<article class=\"docu-card\">
  <iframe src=\"https://www.youtube.com/embed/{escape(v['id'])}\" title=\"{escape(v['title'])}\" loading=\"lazy\" allowfullscreen></iframe>
  <div class=\"docu-meta\">
    <h3>{escape(v['title'])}</h3>
    <p>{escape(v['desc'])}</p>
  </div>
</article>""")

    body = f"""<main class=\"wrap\">
  <section class=\"gallery-header\">
    <h1>Documentaries</h1>
    <p>Films and stories from the wild.</p>
    <p class="muted">Watch conservation-focused wildlife documentaries from Rajasthan and across India, covering species behavior, habitat loss, and community-led protection efforts.</p>
  </section>
  <section class=\"docu-grid\">{' '.join(cards)}</section>
</main>"""

    page = render_page(
        title="Cane & Camera — Wildlife Documentaries & Conservation Films",
        description="Watch wildlife and conservation documentaries by Cane & Camera, featuring field stories, biodiversity, and habitat protection from Rajasthan and across India.",
        body=body,
        canonical_path="documentaries.html",
        extra_css='<link rel="stylesheet" href="assets/css/docs.css">',
    )
    (ROOT / "documentaries.html").write_text(page, encoding="utf-8")


def build_index_page():
    body = """<main class="wrap">
  <section class="hero">
    <h1>A Disabled Wildlife Photographer documenting India's wild spaces.</h1>
    <p>Cane & Camera shares wildlife photography and conservation storytelling from Rajasthan and across the Indian subcontinent, including raptors, grassland species, mammals, and fragile desert ecosystems.</p>
    <p>Explore a curated fine-art wildlife portfolio, field notes rooted in ethical wildlife observation, and documentaries that spotlight biodiversity, habitat loss, and community-led conservation.</p>
  </section>

  <section class="narrow">
    <h2>Wildlife Photography and Conservation Stories from Rajasthan</h2>
    <p>From Mukundara Hills and the Thar grasslands to wetlands and forest edges, Cane & Camera documents India's biodiversity through responsible field practices and natural-light photography. This platform is built for wildlife enthusiasts, conservation partners, and editors seeking authentic visual storytelling rooted in place.</p>
  </section>

  <section class="grid-2">
    <a class="card" href="gallery.html">
      <img loading="lazy" src="assets/img/thumb/wildlife.jpg" alt="Wildlife portfolio cover">
      <h3>Wildlife</h3>
    </a>
    <a class="card" href="documentaries.html">
      <img loading="lazy" src="assets/img/thumb/documentaries.jpg" alt="Documentaries portfolio cover">
      <h3>Documentaries</h3>
    </a>
  </section>
</main>"""

    page = render_page(
        title="Cane & Camera — Wildlife Photography in Rajasthan & India",
        description="Cane & Camera is a wildlife photography and conservation storytelling platform featuring birds, mammals, raptors, and documentaries from Rajasthan and across India.",
        body=body,
        canonical_path="index.html",
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")

def patch_about_links():
    about = (ROOT / "about.html").read_text(encoding="utf-8")
    about = about.replace('href="/"', 'href="index.html"')
    about = about.replace('gallery.html?g=wildlife', 'gallery.html')
    about = about.replace('gallery.html?g=landscapes', 'gallery.html')
    about = about.replace('documentaries.html?g=documentaries', 'documentaries.html')
    about = about.replace('Cane &<br>Camera', 'Cane & Camera')
    about = about.replace('<a href="landscapes.html"><img src="assets/img/ico/icon-landscape.png"/></a>\n', '')
    (ROOT / "about.html").write_text(about, encoding="utf-8")


def main():
    build_index_page()
    build_gallery_page(
        gallery_keys=("wildlife", "landscapes"),
        title="Wildlife",
        description="Browse a wildlife photography gallery featuring birds, mammals, raptors, and nature moments from Rajasthan and across India.",
        out_file="gallery.html",
    )
    build_documentaries_page()
    patch_about_links()
    print("Built: index.html, gallery.html, documentaries.html (+ about nav links)")


if __name__ == "__main__":
    main()
