#!/usr/bin/env python3
"""Build static HTML pages from shared templates + JSON content."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

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


def render_header(active: str = "") -> str:
    active_set = set(active.split())

    def active_class(name: str) -> str:
        return " is-active" if name in active_set else ""

    return f"""<header class="site-header">
  <a href="index.html" class="logo" aria-label="Cane and Camera home">
    <img src="assets/img/ico/logo.svg" alt="Cane & Camera logo"/>
    <span>Cane & Camera</span>
  </a>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Toggle navigation menu">
    ☰
  </button>
  <nav id="site-nav" class="site-nav" aria-label="Primary">
    <a class="nav-link{active_class('gallery')}" href="gallery.html">Wildlife</a>
    <a class="nav-link{active_class('documentaries')}" href="documentaries.html">Documentaries</a>
    <a class="nav-link{active_class('about')}" href="about.html">About</a>
    <a class="nav-link{active_class('contact')}" href="contact.html">Work With Me</a>
  </nav>
</header>"""


def render_footer() -> str:
    return """<footer class="site-footer">
  <div class="footer-grid">
    <section>
      <h4>Navigate</h4>
      <p>
        <a href="index.html">Home</a> ·
        <a href="gallery.html">Wildlife</a> ·
        <a href="documentaries.html">Documentaries</a> ·
        <a href="about.html">About</a> ·
        <a href="contact.html">Work With Me</a>
      </p>
    </section>

    <section>
      <h4>Connect</h4>
      <p>
        <a href="https://instagram.com/caneandcamera" target="_blank" rel="noopener">Instagram</a> ·
        <a href="https://www.youtube.com/@CaneAndCamera/videos" target="_blank" rel="noopener">YouTube</a> ·
        <a href="https://www.patreon.com/cw/CaneAndCamera" target="_blank" rel="noopener">Patreon</a>
      </p>
      <p class="muted">X/Twitter · LinkedIn (coming soon)</p>
    </section>

    <section>
      <h4>Contact</h4>
      <p><b><a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a></b></p>
      <p><a href="contact.html">Start a collaboration inquiry</a></p>
    </section>
  </div>

  <p class="site-footer__legal">© 2026 Cane &amp; Camera · All rights reserved.</p>
</footer>"""


def render_page(
    *,
    title: str,
    description: str,
    body: str,
    canonical_path: str,
    active_nav: str = "",
    extra_css: str = "",
    extra_scripts: str = "",
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="author" content="Cane & Camera">
  <meta name="keywords" content="wildlife photography, nature photography, conservation storytelling, Rajasthan wildlife, India birds, Cane and Camera">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:type" content="website">
  <link rel="canonical" href="https://www.caneandcamera.com/{escape(canonical_path)}">
  <meta name="facebook-domain-verification" content="9sb354a61i9s65n18ijqjp9av800ht" />
  <link rel="icon" type="image/png" href="assets/img/ico/favicon.png">
  <link rel="preload" href="assets/css/style.css" as="style">
  <link rel="stylesheet" href="assets/css/style.css">
  <link rel="preconnect" href="https://cdn.shopify.com" crossorigin>
  {extra_css}
  <script defer src="assets/js/main.js"></script>
  {extra_scripts}
</head>
<body>
{render_header(active_nav)}
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

        cards.append(f"""<article class="cc-card">
  <img class="cc-thumb" src="{escape(variant['src'])}" srcset="{escape(img_srcset)}" sizes="(min-width: 1200px) 33vw, (min-width: 800px) 50vw, 100vw" width="{variant['w']}" height="{variant['h']}" loading="lazy" decoding="async" alt="{escape((photo.get('title') or photo.get('slug') or 'Photo').strip())}">
  <div class="cc-meta">
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

    body = f"""<main class="wrap">
  <section class="gallery-header">
    <h1>{escape(title)}</h1>
    <p>{escape(description)}</p>
    <div id="cc-masonry" class="cc-masonry">{gallery_markup}</div>
  </section>
</main>
<!-- Lightbox modal -->
<div class="lgx" id="lgx" aria-hidden="true">
  <img class="lgx__img" alt="">
  <div class="lgx__ui">
    <button class="lgx__btn lgx__close" aria-label="Close (Esc)">✕</button>
    <button class="lgx__btn lgx__prev"  aria-label="Previous (←)">←</button>
    <button class="lgx__btn lgx__next"  aria-label="Next (→)">→</button>
    <div class="lgx__ctrl lgx__bar">
      <button class="lgx__btn lgx__play"  aria-label="Start slideshow (Space)">▶</button>
      <button class="lgx__btn lgx__pause" aria-label="Pause slideshow (Space)" style="display:none;">⏸</button>
    </div>
    <div class="lgx__caption" role="note"></div>
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
        active_nav="gallery",
        extra_css=extra_css,
        extra_scripts='<script defer src="assets/js/gallery-lightbox.js"></script>',
    )
    (ROOT / out_file).write_text(page, encoding="utf-8")


def build_documentaries_page():
    videos = read_json(DOCS_JSON)
    cards = []
    for v in videos:
        cards.append(f"""<article class="docu-card">
  <iframe src="https://www.youtube.com/embed/{escape(v['id'])}" title="{escape(v['title'])}" loading="lazy" allowfullscreen></iframe>
  <div class="docu-meta">
    <h3>{escape(v['title'])}</h3>
    <p>{escape(v['desc'])}</p>
  </div>
</article>""")

    body = f"""<main class="wrap">
  <section class="gallery-header">
    <h1>Documentaries</h1>
    <p>Films and stories from the wild.</p>
    <p class="muted">Watch conservation-focused wildlife documentaries from Rajasthan and across India, covering species behavior, habitat loss, and community-led protection efforts.</p>
  </section>
  <section class="docu-grid">{' '.join(cards)}</section>
</main>"""

    page = render_page(
        title="Cane & Camera — Wildlife Documentaries & Conservation Films",
        description="Watch wildlife and conservation documentaries by Cane & Camera, featuring field stories, biodiversity, and habitat protection from Rajasthan and across India.",
        body=body,
        canonical_path="documentaries.html",
        active_nav="documentaries",
        extra_css='<link rel="stylesheet" href="assets/css/docs.css">',
    )
    (ROOT / "documentaries.html").write_text(page, encoding="utf-8")


def build_index_page():
    body = """<main class="wrap">
  <section class="hero">
    <h1>Wildlife stories from India’s wild spaces.</h1>
    <p>Cane &amp; Camera documents birds, mammals, and threatened ecosystems through ethical photography and documentary storytelling from Rajasthan and across India.</p>
    <div class="hero-cta-row">
      <a class="btn" href="gallery.html">View Wildlife Portfolio</a>
      <a class="btn btn-outline" href="documentaries.html">Watch Documentaries</a>
      <a class="btn btn-outline" href="contact.html">Work With Me</a>
    </div>
  </section>

  <section class="grid-2">
    <a class="card" href="gallery.html">
      <img loading="lazy" src="assets/img/thumb/wildlife.jpg" alt="Wildlife portfolio cover">
      <h3>Wildlife Portfolio</h3>
    </a>
    <a class="card" href="documentaries.html">
      <img loading="lazy" src="assets/img/thumb/documentaries.jpg" alt="Documentaries portfolio cover">
      <h3>Documentaries</h3>
    </a>
  </section>

  <section class="grid-2 info-grid">
    <article class="card card-copy">
      <h3>About</h3>
      <p>Learn about the mission, field ethics, and conservation focus behind Cane &amp; Camera.</p>
      <p><a href="about.html">Read About →</a></p>
    </article>
    <article class="card card-copy">
      <h3>Work With Me</h3>
      <p>Open to conservation campaigns, editorial assignments, screenings, and speaking collaborations.</p>
      <p><a href="contact.html">Start a project →</a></p>
    </article>
  </section>
</main>"""

    page = render_page(
        title="Cane & Camera — Wildlife Photography in Rajasthan & India",
        description="Cane & Camera is a wildlife photography and conservation storytelling platform featuring birds, mammals, raptors, and documentaries from Rajasthan and across India.",
        body=body,
        canonical_path="index.html",
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")


def build_about_page():
    body = """<main class="wrap narrow">
  <h1>About Cane &amp; Camera</h1>
  <p>Cane &amp; Camera is a Rajasthan-based wildlife and nature storytelling initiative blending documentary filmmaking, conservation narratives, and fine-art photography.</p>
  <p>From Mukundara Hills to Thar grasslands, each project is built on ethical field practice and respect for species, habitats, and local communities.</p>
  <p>For collaborations, exhibitions, commissioned stories, and print inquiries, please visit <a href="contact.html">Work With Me</a> or email <a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a>.</p>

  <section class="press" id="press" aria-labelledby="press-title">
    <header class="press__header">
      <h2 id="press-title">Media Coverage</h2>
      <p class="muted">Selected features, interviews, and mentions.</p>
    </header>

    <div class="press__grid">
      <article class="press__card">
        <a class="press__imageLink" href="https://www.thehindu.com/brandhub/pr-release/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan/article70541452.ece" target="_blank" rel="noopener noreferrer">
          <img class="press__img" src="assets/img/press/the-hindu.png" width="1400" height="800" loading="lazy" alt="Screenshot of The Hindu BrandHub coverage" />
        </a>
        <div class="press__body">
          <h3 class="press__headline">Durbar by Godawan Estuary Water: Second Edition in Khetri, Rajasthan</h3>
          <p class="press__meta"><span class="press__outlet">The Hindu — BrandHub</span></p>
        </div>
      </article>

      <article class="press__card">
        <a class="press__imageLink" href="https://www.travelandleisureasia.com/in/destinations/durbar-godawan-khetri-hills-abheygarh/" target="_blank" rel="noopener noreferrer">
          <img class="press__img" src="assets/img/press/travel-leisure.png" width="1400" height="800" loading="lazy" alt="Screenshot of Travel + Leisure Asia coverage" />
        </a>
        <div class="press__body">
          <h3 class="press__headline">Inside Durbar by Godawan Estuary Water At Rajasthan's Khetri Hills Abheygarh</h3>
          <p class="press__meta"><span class="press__outlet">Travel + Leisure Asia</span></p>
        </div>
      </article>
    </div>
  </section>
</main>"""

    page = render_page(
        title="Cane & Camera — About the Wildlife Storytelling Project",
        description="Learn about Cane & Camera, a Rajasthan-based wildlife photography and conservation storytelling initiative focused on ethical fieldwork, documentaries, and biodiversity awareness.",
        body=body,
        canonical_path="about.html",
        active_nav="about",
    )
    (ROOT / "about.html").write_text(page, encoding="utf-8")


def build_contact_page():
    body = """<main class="wrap narrow">
  <h1>Work With Me</h1>
  <p>I collaborate with conservation organizations, editorial teams, and ethical travel/culture platforms on photography, documentary storytelling, campaigns, and field-led narratives.</p>

  <section class="contact-panel" aria-labelledby="contact-title">
    <h2 id="contact-title">Contact</h2>
    <p><b>Email:</b> <a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a></p>
    <p><b>Please include:</b> project brief, timeline, location, and intended usage/licensing.</p>
    <p><a class="btn" href="mailto:hello@caneandcamera.com?subject=Collaboration%20Inquiry%20-%20Cane%20and%20Camera">Send Collaboration Inquiry</a></p>
  </section>

  <section>
    <h2>Common collaboration formats</h2>
    <ul>
      <li>Wildlife documentary shoots and field production</li>
      <li>Editorial/photo essay assignments</li>
      <li>Conservation campaign storytelling</li>
      <li>Talks, screenings, and educational sessions</li>
    </ul>
  </section>
</main>"""

    page = render_page(
        title="Cane & Camera — Work With Me / Contact",
        description="Get in touch with Cane & Camera for collaborations in wildlife photography, documentaries, conservation campaigns, and editorial storytelling.",
        body=body,
        canonical_path="contact.html",
        active_nav="contact",
    )
    (ROOT / "contact.html").write_text(page, encoding="utf-8")


def patch_landscapes_legacy_page():
    landscapes_path = ROOT / "landscapes.html"
    if not landscapes_path.exists():
        return

    html = landscapes_path.read_text(encoding="utf-8")
    header_html = """<header class="site-header">
  <a href="index.html" class="logo" aria-label="Cane and Camera home">
    <img src="assets/img/ico/logo.svg" alt="Cane & Camera logo"/>
    <span>Cane & Camera</span>
  </a>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Toggle navigation menu">
    ☰
  </button>
  <nav id="site-nav" class="site-nav" aria-label="Primary">
    <a class="nav-link is-active" href="gallery.html">Wildlife</a>
    <a class="nav-link" href="documentaries.html">Documentaries</a>
    <a class="nav-link" href="about.html">About</a>
    <a class="nav-link" href="contact.html">Work With Me</a>
  </nav>
</header>"""

    start = html.find("<header class=\"site-header\">")
    end = html.find("</header>", start)
    if start != -1 and end != -1:
        html = html[:start] + header_html + html[end + 9 :]

    fstart = html.find("<footer class=\"site-footer\">")
    fend = html.find("</footer>", fstart)
    if fstart != -1 and fend != -1:
        html = html[:fstart] + render_footer() + html[fend + 9 :]

    landscapes_path.write_text(html, encoding="utf-8")


def main():
    build_index_page()
    build_gallery_page(
        gallery_keys=("wildlife", "landscapes"),
        title="Wildlife",
        description="Browse a wildlife photography gallery featuring birds, mammals, raptors, and nature moments from Rajasthan and across India.",
        out_file="gallery.html",
    )
    build_documentaries_page()
    build_about_page()
    build_contact_page()
    patch_landscapes_legacy_page()
    print("Built: index.html, gallery.html, documentaries.html, about.html, contact.html (+ legacy landscapes nav/footer)")


if __name__ == "__main__":
    main()
