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


  <a href="/index.html" class="logo"><img src="/assets/img/ico/logo.svg" alt="Cane & Camera logo"/><span>Cane & Camera</span></a>
    <a href="/gallery.html"><img src="/assets/img/ico/icon-wildlife.png" alt="Wildlife"/></a>
    <a href="/documentaries.html"><img src="/assets/img/ico/icon-documentaries.png" style="filter: invert()" alt="Documentaries" /></a>
    <a href="https://www.youtube.com/@CaneAndCamera/videos" target="_blank" rel="noopener"><img src="/assets/img/ico/icon-youtube.png" alt="YouTube"/></a>
    <a href="https://instagram.com/caneandcamera" target="_blank" rel="noopener"><img src="/assets/img/ico/icon-ig.png" alt="Instagram" /></a>
    <a href="/about.html"><img src="/assets/img/ico/icon-about.png" alt="About" /></a>
  <link rel=\"icon\" type=\"image/png\" href=\"/assets/img/ico/favicon.png\">
  <link rel=\"preload\" href=\"/assets/css/style.css\" as=\"style\">
  <link rel=\"stylesheet\" href=\"/assets/css/style.css\">
  <script defer src=\"/assets/js/main.js\"></script>
    film_icon = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="M7 5v14M17 5v14M3 9h4M3 15h4M17 9h4M17 15h4"></path></svg>'
    person_icon = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="3.2"></circle><path d="M5 19c1.5-3 4-4.5 7-4.5s5.5 1.5 7 4.5"></path></svg>'
    brief_icon = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2"></rect><path d="M9 7V5h6v2M3 12h18"></path></svg>'

    return f"""<header class="site-header">
  <a href="index.html" class="logo" aria-label="Cane and Camera home">
    <img src="assets/img/ico/logo.svg" alt="Cane & Camera logo" width="48" height="48"/>
    <span>Cane & Camera</span>
  </a>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Toggle navigation menu">
    ☰
  </button>
  <nav id="site-nav" class="site-nav" aria-label="Primary">
    {nav_link('gallery', 'gallery.html', 'Wildlife', camera_icon)}
    {nav_link('documentaries', 'documentaries.html', 'Documentaries', film_icon)}
    {nav_link('about', 'about.html', 'About', person_icon)}
    {nav_link('contact', 'contact.html', 'Work With Me', brief_icon)}
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
      <p><a href="https://mhtr.in" target="_blank" rel="noopener">Explore field stories at mhtr.in</a></p>
    </section>

    <section>
      <h4>Contact</h4>
      <p><b><a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a></b></p>
      <p><a href="contact.html">Start a collaboration inquiry</a></p>
      <p><a class="btn support-btn" href="https://www.patreon.com/cw/CaneAndCamera" target="_blank" rel="noopener">Support on Patreon</a></p>
    </section>
  </div>

  <p class="footer-cta">Licensing, assignments, collaborations, and responsible field guiding — <a href="contact.html">Get in touch</a>.</p>
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
    og_image: str = "assets/img/thumb/wildlife.jpg",
    extra_head: str = "",
) -> str:
    og_url = f"https://www.caneandcamera.com/{escape(canonical_path)}"
    og_image_url = f"https://www.caneandcamera.com/{escape(og_image)}"
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
  <meta property="og:url" content="{og_url}">
  <meta property="og:image" content="{og_image_url}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{og_image_url}">
  <link rel="canonical" href="{og_url}">
        extra_scripts='<script defer src="/assets/js/gallery-lightbox.js"></script>',
        extra_css='<link rel="stylesheet" href="/assets/css/docs.css">',
    <a class="card" href="/gallery.html">
      <img loading="lazy" src="/assets/img/thumb/wildlife.jpg" alt="Wildlife portfolio cover">
    <a class="card" href="/documentaries.html">
      <img loading="lazy" src="/assets/img/thumb/documentaries.jpg" alt="Documentaries portfolio cover">
    about = about.replace('href="/"', 'href="/index.html"')
    about = about.replace('href="index.html"', 'href="/index.html"')
    about = about.replace('href="gallery.html"', 'href="/gallery.html"')
    about = about.replace('href="documentaries.html"', 'href="/documentaries.html"')
    about = about.replace('href="about.html"', 'href="/about.html"')
    about = about.replace('href="contact.html"', 'href="/contact.html"')
    about = about.replace('gallery.html?g=wildlife', '/gallery.html')
    about = about.replace('gallery.html?g=landscapes', '/gallery.html')
    about = about.replace('documentaries.html?g=documentaries', '/documentaries.html')
def build_pretty_routes() -> None:
    routes = {
        "gallery.html": "gallery",
        "documentaries.html": "documentaries",
        "about.html": "about",
        "landscapes.html": "landscapes",
    }
    for source_file, route in routes.items():
        source = ROOT / source_file
        destination = ROOT / route / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


    build_pretty_routes()
</head>
<body>
<a class="skip-link" href="#main-content">Skip to content</a>
{render_header(active_nav)}
{body}
{render_footer()}
</body>
    body = f"""<main class=\"wrap docs-page\">
  <section class=\"docu-grid\">{'\n'.join(cards)}</section>


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

    seen_sources = set()
    deduped = []
    for photo in photos:

        variant = largest_variant(photo.get("variants", {}))
        if not variant:
            continue
        src = variant.get("src")
        if src in seen_sources:
            continue
        seen_sources.add(src)
        deduped.append(photo)

    gallery_markup = render_gallery_cards(deduped)

    body = f"""<main id="main-content" class="wrap">
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
    for index, v in enumerate(videos, start=1):
        title = escape(v['title'])
        desc = escape(v['desc'])
        vid = escape(v['id'])
        cards.append(f"""<article class="docu-card">
  <iframe src="https://www.youtube.com/embed/{vid}" title="{title}" loading="lazy" allowfullscreen></iframe>
  <div class="docu-meta">
    <h3>{title}</h3>
    <p>{desc}</p>
    <p class="muted">Film {index} · Field notes from Rajasthan wildlife photography and conservation film work.</p>
    <p><a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Watch on YouTube ↗</a></p>
  </div>
</article>""")

    body = f"""<main id="main-content" class="wrap">
  <section class="gallery-header">
    <h1>Documentaries</h1>
    <p>Films and stories from the wild.</p>
    <p class="muted">These short conservation films cover field realities across Mukundara Hills, Rajasthan grasslands, wetlands, and the Thar, with practical context for species, habitat pressure, and coexistence.</p>
  </section>
  <section class="docu-grid">{' '.join(cards)}</section>
</main>"""

    page = render_page(
        title="Cane & Camera — Wildlife Documentaries & Conservation Films",
        description="Watch Cane & Camera documentaries on wildlife and conservation across Rajasthan and India, with stories on species behavior, habitats, and local care.",
        body=body,
        canonical_path="documentaries.html",
        active_nav="documentaries",
        extra_css='<link rel="stylesheet" href="assets/css/docs.css">',
    )
    (ROOT / "documentaries.html").write_text(page, encoding="utf-8")

def build_index_page():
    photos = [p for p in read_json(PHOTOS_JSON) if p.get("gallery", "").lower() == "wildlife"]
    photos.sort(key=lambda item: item.get("datetime", ""), reverse=True)

    seen_sources = set()
    featured_photos = []
    for photo in photos:
        variant = largest_variant(photo.get("variants", {}))
        if not variant:
            continue
        src = variant.get("src")
        if src in seen_sources:
            continue
        seen_sources.add(src)
        featured_photos.append(photo)
        if len(featured_photos) == 6:
            break

    wildlife_cards = []
    for photo in featured_photos:
        variant = largest_variant(photo.get("variants", {}))
        if not variant:
            continue
        title = (photo.get("title") or photo.get("slug") or "Wildlife moment").strip()
        desc = (photo.get("description") or "Featured wildlife photograph from Rajasthan and the Indian subcontinent.").strip()
        wildlife_cards.append(
            f"""<article class="feature-card">
      <a class="feature-card__link" href="gallery.html" aria-label="View wildlife portfolio: {escape(title)}">
        <img src="{escape(variant['src'])}" loading="lazy" decoding="async" width="{variant['w']}" height="{variant['h']}" alt="Featured wildlife photograph: {escape(title)}">
        <h3>{escape(title)}</h3>
        <p>{escape(desc)}</p>
      </a>
    </article>"""
        )

    docs = read_json(DOCS_JSON)[:3]
    documentary_cards = []
    for doc in docs:
        doc_title = doc.get("title", "Featured documentary").strip()
        doc_desc = doc.get("desc", "Watch this conservation story from Cane & Camera.").strip()
        doc_id = escape(doc.get("id", ""))
        documentary_cards.append(
            f"""<article class="feature-card">
      <a class="feature-card__link" href="documentaries.html" aria-label="Watch documentary collection: {escape(doc_title)}">
        <img src="https://i.ytimg.com/vi/{doc_id}/hqdefault.jpg" loading="lazy" decoding="async" width="480" height="360" alt="Documentary thumbnail: {escape(doc_title)}">
        <h3>{escape(doc_title)}</h3>
        <p>{escape(doc_desc)}</p>
      </a>
    </article>"""
        )

    body = f"""<main id="main-content" class="wrap">
  <section class="hero hero-clean">
    <h1>Cane &amp; Camera</h1>
    <p class="subhead">Wildlife photography and conservation films from Rajasthan—told on foot, often with a cane.</p>
    <p>I’m Vinay Chittora, a disabled wildlife photographer, aspiring filmmaker, and ethical field naturalist. My work focuses on Rajasthan wildlife photography across Mukundara Hills, grasslands, wetlands, and the Thar, with clear, grounded conservation storytelling.</p>
    <div class="hero-cta-row">
      <a class="btn" href="gallery.html">View Wildlife Portfolio</a>
      <a class="btn" href="documentaries.html">Watch Documentaries</a>
      <a class="btn btn-outline" href="about.html">About</a>
      <a class="btn btn-outline" href="contact.html">Work with me</a>
      <a class="btn support-btn" href="https://www.patreon.com/cw/CaneAndCamera" target="_blank" rel="noopener">Support this work on Patreon</a>
    </div>
  </section>

  <section class="why-cc" aria-labelledby="why-cc-title">
    <h2 id="why-cc-title">Why Cane &amp; Camera</h2>
    <p>The cane is mobility support and a reminder to move slowly, observe deeply, and keep disturbance low.</p>
    <p>The camera is my field notebook for stories from Mukundara Hills, grasslands, wetlands, and the Thar.</p>
    <p><a href="about.html">Learn more about the approach →</a></p>
  </section>

  <section aria-labelledby="featured-wildlife-title">
    <div class="section-head">
      <h2 id="featured-wildlife-title">Featured Wildlife</h2>
      <a href="gallery.html">View all wildlife →</a>
    </div>
    <div class="feature-grid">{''.join(wildlife_cards)}</div>
  </section>

  <section aria-labelledby="featured-docs-title">
    <div class="section-head">
      <h2 id="featured-docs-title">Featured Documentaries</h2>
      <a href="documentaries.html">View all documentaries →</a>
    </div>
    <div class="feature-grid feature-grid--docs">{''.join(documentary_cards)}</div>
  </section>

  <section class="trust-strip" aria-label="Trust and field practice">
    Ethical field practice • Natural light • Rajasthan + Indian subcontinent + Mukundara Hills Tiger Reserve
  </section>
</main>"""

    homepage_schema = json.dumps([
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Cane & Camera",
            "url": "https://www.caneandcamera.com/",
            "description": "Wildlife photography and conservation films from Rajasthan and India.",
        },
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Vinay Chittora",
            "jobTitle": "Wildlife Photographer & Aspiring Filmmaker",
            "url": "https://www.caneandcamera.com/about.html",
            "sameAs": [
                "https://instagram.com/caneandcamera",
                "https://www.youtube.com/@CaneAndCamera/videos",
            ],
        },
    ], ensure_ascii=False)

    page = render_page(
        title="Cane & Camera — Wildlife Photography in Rajasthan & India",
        description="Explore Cane & Camera wildlife photography and conservation films from Rajasthan and India, featuring birds, mammals, habitats, and ethical storytelling.",
        body=body,
        canonical_path="index.html",
        extra_head=f'<script type="application/ld+json">{homepage_schema}</script>',
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")

def build_about_page():
    press_items = [
        {
            "img": "assets/img/press/the-hindu.png",
            "alt": "Screenshot of The Hindu BrandHub coverage about Durbar by Godawan in Khetri, Rajasthan",
            "title": "Durbar by Godawan Estuary Water: Second Edition in Khetri, Rajasthan",
            "outlet": "The Hindu — BrandHub",
            "url": "https://www.thehindu.com/brandhub/pr-release/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan/article70541452.ece",
            "excerpt": "A BrandHub feature on Godawan Durbar’s Khetri edition, bringing together craft, culture, and conservation in Rajasthan.",
        },
        {
            "img": "assets/img/press/the-wire.png",
            "alt": "Screenshot of The Wire coverage of Godawan Durbar in Khetri, Rajasthan",
            "title": "Durbar by Godawan Estuary Water marked a powerful second edition in Khetri, Rajasthan",
            "outlet": "The Wire",
            "url": "https://thewire.in/brand-studio/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan",
            "excerpt": "Coverage highlighting place-based programming and conservation dialogue in the Aravalli landscape.",
        },
        {
            "img": "assets/img/press/travel-media.png",
            "alt": "Screenshot of Travel and Tour World coverage of Godawan Durbar in Khetri",
            "title": "Durbar by Godawan Estuary Water brings conservation-led storytelling to Khetri",
            "outlet": "Travel and Tour World",
            "url": "https://www.travelandtourworld.com/news/article/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan/",
            "excerpt": "Travel trade coverage of heritage, ecology, and storytelling-led event programming in Rajasthan.",
        },
        {
            "img": "assets/img/press/free-press-journal.png",
            "alt": "Screenshot of Free Press Journal coverage: Durbar by Godawan Estuary Water sets a new benchmark in experiential events",
            "title": "Durbar By Godawan Estuary Water Sets A New Benchmark In Experiential Events",
            "outlet": "Free Press Journal",
            "url": "https://www.freepressjournal.in/lifestyle/durbar-by-godawan-estuary-water-sets-a-new-benchmark-in-experiential-events",
            "excerpt": "A feature on conservation-rooted experiential programming and documentary storytelling.",
        },
        {
            "img": "assets/img/press/media-brief.png",
            "alt": "Screenshot of MediaBrief article on Durbar by Godawan in Rajasthan",
            "title": "Durbar by Godawan Estuary Water marked a powerful second edition in Khetri",
            "outlet": "MediaBrief",
            "url": "https://mediabrief.com/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan/",
            "excerpt": "Coverage of a collaboration between hospitality, conservation communication, and regional storytelling.",
        },
        {
            "img": "assets/img/press/eventfaqs.png",
            "alt": "Screenshot of EventFAQs article featuring Durbar by Godawan in Khetri",
            "title": "Durbar by Godawan Estuary Water marked a powerful second edition in Khetri, Rajasthan",
            "outlet": "EventFAQs",
            "url": "https://www.eventfaqs.com/news/ef-21517/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan",
            "excerpt": "Event industry reporting on purpose-led field storytelling and immersive programming.",
        },
        {
            "img": "assets/img/press/exchange4media.png",
            "alt": "Screenshot of exchange4media story on Durbar by Godawan",
            "title": "Durbar by Godawan Estuary Water marked a powerful second edition in Khetri, Rajasthan",
            "outlet": "exchange4media",
            "url": "https://www.exchange4media.com/industry-briefing-news/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan-143064.html",
            "excerpt": "Industry coverage of conservation-led storytelling formats and strategic regional communication.",
        },
        {
            "img": "assets/img/press/indiantelevision.png",
            "alt": "Screenshot of IndianTelevision.com coverage of Durbar by Godawan",
            "title": "Durbar by Godawan Estuary Water marked a powerful second edition in Khetri, Rajasthan",
            "outlet": "IndianTelevision.com",
            "url": "https://www.indiantelevision.com/mam/media-and-advertising/brand-activations/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan-250527",
            "excerpt": "A report on event storytelling, destination narratives, and conservation-linked communication.",
        },
        {
            "img": "assets/img/press/adgully.png",
            "alt": "Screenshot of Adgully article featuring Durbar by Godawan's second edition",
            "title": "Durbar by Godawan Estuary Water marked a powerful second edition in Khetri, Rajasthan",
            "outlet": "Adgully",
            "url": "https://www.adgully.com/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan-158953.html",
            "excerpt": "Coverage of brand storytelling that connects regional identity, ecology, and audience engagement.",
        },
        {
            "img": "assets/img/press/aninews.png",
            "alt": "Screenshot of ANI syndicated coverage of Durbar by Godawan event",
            "title": "Durbar by Godawan Estuary Water marked a powerful second edition in Khetri, Rajasthan",
            "outlet": "ANI News",
            "url": "https://www.aninews.in/news/business/business/durbar-by-godawan-estuary-water-marked-a-powerful-second-edition-in-khetri-rajasthan20250527172444/",
            "excerpt": "Syndicated coverage highlighting conservation dialogue and place-led storytelling in Rajasthan.",
        },
    ]

    press_cards = []
    for item in press_items:
        press_cards.append(f"""<article class="press__card">
  <a class="press__imageLink" href="{escape(item['url'])}" target="_blank" rel="noopener noreferrer" aria-label="Read: {escape(item['title'])}">
    <img class="press__img" src="{escape(item['img'])}" loading="lazy" decoding="async" alt="{escape(item['alt'])}">
  </a>
  <div class="press__body">
    <p class="press__meta"><span class="press__outlet">{escape(item['outlet'])}</span></p>
    <h3 class="press__headline"><a href="{escape(item['url'])}" target="_blank" rel="noopener noreferrer">{escape(item['title'])}</a></h3>
    <p class="muted">{escape(item['excerpt'])}</p>
  </div>
</article>""")

    body = f"""<main id="main-content" class="wrap narrow about-page">
  <h1>About</h1>
  <p class="about-intro">I’m Vinay Chittora, a disabled wildlife photographer and aspiring filmmaker based in Rajasthan. I work across Mukundara Hills, grasslands, wetlands, and the Thar to create practical, field-led visual stories.</p>

  <section class="about-section" aria-labelledby="why-cane-camera">
    <h2 id="why-cane-camera">Why Cane &amp; Camera</h2>
    <p>The cane is mobility support and a discipline: move slowly, read habitat carefully, and avoid unnecessary disturbance. The camera is my storytelling tool for Rajasthan wildlife photography and conservation films that are useful for public understanding.</p>
  </section>

  <section class="about-section" aria-labelledby="mukundara">
    <h2 id="mukundara">Rooted in Mukundara Hills</h2>
    <p>I grew up around the Mukundara Hills landscape. That mix of scrub, forest edge, wetlands, and grasslands shaped how I track seasonality, behaviour, and habitat change. We also document field stories through <a href="https://mhtr.in" target="_blank" rel="noopener">mhtr.in</a> to build stronger place-based awareness.</p>
  </section>

  <section class="about-section" aria-labelledby="how-i-work">
    <h2 id="how-i-work">How I work</h2>
    <p>I use a customised vehicle setup with a window mount for stable long-lens work and minimal movement around animals. This lets me work quietly and safely while following forest department guidance and location protocols.</p>
    <ul>
      <li>No bird-call playback on Bluetooth speakers.</li>
      <li>No touching, handling, or feeding wildlife.</li>
      <li>No baiting, crowding, or forced encounters.</li>
      <li>No littering; we carry back all waste and prefer reusable, long-life gear.</li>
      <li>Low-footprint travel with bare minimum field load.</li>
    </ul>
  </section>

  <section class="about-section" aria-labelledby="what-im-building">
    <h2 id="what-im-building">What I’m building</h2>
    <p>I’m building a long-term body of work across <a href="gallery.html">Wildlife</a>, <a href="documentaries.html">Documentaries</a>, and conservation storytelling that supports ethical nature interpretation and future collaboration with researchers, NGOs, and editorial teams.</p>
  </section>

  <section class="about-section" aria-labelledby="work-with-me">
    <h2 id="work-with-me">Work with me</h2>
    <p>I take on editorial assignments, NGO collaborations, licensing, screenings, talks, and responsible nature-guide projects. If your brief needs reliable field execution and clear communication, <a href="contact.html">let’s connect</a>.</p>
  </section>

  <section class="press" id="press" aria-labelledby="press-title">
    <header class="press__header">
      <h2 id="press-title">Media Coverage</h2>
      <p class="muted">Selected features, interviews, and mentions.</p>
    </header>
    <div class="press__grid press__grid--two">{''.join(press_cards)}</div>
  </section>
</main>"""

    about_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Vinay Chittora",
        "jobTitle": "Wildlife Photographer & Aspiring Filmmaker",
        "url": "https://www.caneandcamera.com/about.html",
        "homeLocation": {"@type": "Place", "name": "Rajasthan, India"},
        "sameAs": [
            "https://instagram.com/caneandcamera",
            "https://www.youtube.com/@CaneAndCamera/videos",
            "https://mhtr.in",
        ],
    }, ensure_ascii=False)

    page = render_page(
        title="About Vinay Chittora | Cane & Camera",
        description="About Vinay Chittora: Rajasthan wildlife photography, conservation films, field ethics, and long-term storytelling rooted in Mukundara Hills and surrounding habitats.",
        body=body,
        canonical_path="about.html",
        active_nav="about",
        og_image="assets/img/thumb/wildlife.jpg",
        extra_head=f'<script type="application/ld+json">{about_schema}</script>',
    )
    (ROOT / "about.html").write_text(page, encoding="utf-8")

def build_contact_page():
    person_schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Vinay Chittora",
        "jobTitle": "Wildlife Photographer & Aspiring Filmmaker",
        "url": "https://www.caneandcamera.com/contact.html",
        "homeLocation": {
            "@type": "Place",
            "name": "Rajasthan, India"
        },
        "sameAs": [
            "https://instagram.com/caneandcamera",
            "https://www.youtube.com/@CaneAndCamera/videos",
            "https://mhtr.in"
        ]
    }

    contact_page_schema = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Work With Me | Cane & Camera",
        "url": "https://www.caneandcamera.com/contact.html",
        "mainEntity": {
            "@type": "Person",
            "name": "Vinay Chittora",
            "email": "mailto:hello@caneandcamera.com"
        }
    }

    ld_json = json.dumps([person_schema, contact_page_schema], ensure_ascii=False)

    body = f"""<main id="main-content" class="wrap narrow work-page">
  <h1>Work With Me</h1>
  <p class="about-intro">I collaborate with editorial teams, conservation organisations, destinations, and mission-led brands on Rajasthan wildlife photography, conservation films, and responsible field storytelling.</p>

  <section class="about-section" aria-labelledby="services-title">
    <h2 id="services-title">Services</h2>
    <ul>
      <li>Wildlife photography assignments for editorial and destination narratives</li>
      <li>Editorial image licensing with usage-specific documentation</li>
      <li>Conservation film collaborations and short factual documentary production</li>
      <li>Screenings, talks, and field interpretation sessions</li>
      <li>Responsible nature-guide and field planning support</li>
    </ul>
  </section>

  <section class="about-section" aria-labelledby="expertise-title">
    <h2 id="expertise-title">Field expertise and process</h2>
    <p>I work with a customised car and window-mount setup that reduces movement and keeps observation stable at longer focal lengths. This workflow supports low-disruption wildlife documentation across Mukundara Hills, wetlands, grasslands, and the Thar.</p>
    <ul>
      <li>Strict adherence to forest department rules and local field protocols</li>
      <li>No bird-call playback, no baiting, and no interference with behaviour</li>
      <li>No touching or feeding wildlife in any form</li>
      <li>Pack-in/pack-out field discipline; reusable materials where possible</li>
      <li>Lean travel footprint and sustainable field logistics</li>
    </ul>
  </section>

  <section class="about-section" aria-labelledby="deliverables-title">
    <h2 id="deliverables-title">Deliverables</h2>
    <ul>
      <li>Edited still image sets for web, editorial, and print pipelines</li>
      <li>Short documentary films and narrative reels</li>
      <li>Social cutdowns and trailers</li>
      <li>Field notes, species context, and location storytelling where relevant</li>
    </ul>
  </section>

  <section class="about-section" aria-labelledby="licensing-title">
    <h2 id="licensing-title">Licensing</h2>
    <p>Usage terms are discussed case-by-case based on format, territory, duration, language, and distribution scope.</p>
  </section>

  <section class="contact-panel" aria-labelledby="contact-title">
    <h2 id="contact-title">Contact</h2>
    <p><b>Email:</b> <a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a></p>
    <p><b>Instagram:</b> <a href="https://instagram.com/caneandcamera" target="_blank" rel="noopener">instagram.com/caneandcamera</a></p>
    <p><b>YouTube:</b> <a href="https://www.youtube.com/@CaneAndCamera/videos" target="_blank" rel="noopener">youtube.com/@CaneAndCamera</a></p>
    <p><b>MHTR field stories:</b> <a href="https://mhtr.in" target="_blank" rel="noopener">mhtr.in</a></p>
    <p><b>How to reach out:</b> Share your goals, dates, location, and usage needs. I’ll respond with scope, timeline, and licensing options.</p>
    <p><a class="btn" href="mailto:hello@caneandcamera.com?subject=Work%20With%20Me%20Inquiry%20-%20Cane%20and%20Camera">Email project details</a></p>
    <p><a class="btn support-btn" href="https://www.patreon.com/cw/CaneAndCamera" target="_blank" rel="noopener">Support this independent fieldwork on Patreon</a></p>
  </section>

  <section class="about-section" aria-labelledby="faq-title">
    <h2 id="faq-title">FAQ</h2>
    <details>
      <summary>What is your typical turnaround?</summary>
      <p>Turnaround depends on assignment complexity; I share realistic delivery windows and milestones before we start.</p>
    </details>
    <details>
      <summary>Where are you based?</summary>
      <p>I am based in Rajasthan, with regular work in Mukundara Hills and across nearby grassland and wetland belts.</p>
    </details>
    <details>
      <summary>Can you travel for assignments?</summary>
      <p>Yes. Travel is possible across India for assignments aligned with schedule, logistics, and low-impact field standards.</p>
    </details>
  </section>

  <p class="muted">See recent work in <a href="gallery.html">Wildlife</a>, <a href="documentaries.html">Documentaries</a>, and field updates via <a href="https://mhtr.in" target="_blank" rel="noopener">mhtr.in</a>.</p>

  <script type="application/ld+json">{ld_json}</script>
</main>"""

    page = render_page(
        title="Work With Me | Wildlife Photography, Conservation Film & Field Collaboration",
        description="Work with Vinay Chittora on Rajasthan wildlife photography, conservation films, ethical field storytelling, licensing, and responsible nature-guide collaborations.",
        body=body,
        canonical_path="contact.html",
        active_nav="contact",
        og_image="assets/img/thumb/documentaries.jpg",
    )
    (ROOT / "contact.html").write_text(page, encoding="utf-8")

def patch_landscapes_legacy_page():
    landscapes_path = ROOT / "landscapes.html"
    if not landscapes_path.exists():
        return

    html = landscapes_path.read_text(encoding="utf-8")
    header_html = render_header("gallery")

    start = html.find("<header class=\"site-header\">")
    end = html.find("</header>", start)
    if start != -1 and end != -1:
        html = html[:start] + header_html + html[end + 9 :]

    fstart = html.find("<footer class=\"site-footer\">")
    fend = html.find("</footer>", fstart)
    if fstart != -1 and fend != -1:
        html = html[:fstart] + render_footer() + html[fend + 9 :]

    landscapes_path.write_text(html, encoding="utf-8")




def build_pretty_routes():
    route_map = {
        "gallery": "gallery.html",
        "landscapes": "landscapes.html",
        "documentaries": "documentaries.html",
        "about": "about.html",
        "contact": "contact.html",
        "work-with-me": "contact.html",
    }
    for route, html_file in route_map.items():
        src = ROOT / html_file
        if not src.exists():
            continue
        dest_dir = ROOT / route
        dest_dir.mkdir(parents=True, exist_ok=True)
        html = src.read_text(encoding="utf-8")
        if '<base href="/">' not in html:
            html = html.replace('<head>', '<head>\n  <base href="/">', 1)
        (dest_dir / "index.html").write_text(html, encoding="utf-8")

def build_sitemap():
    routes = [
        "index.html",
        "gallery.html",
        "landscapes.html",
        "documentaries.html",
        "about.html",
        "contact.html",
        "gallery/",
        "landscapes/",
        "documentaries/",
        "about/",
        "contact/",
        "work-with-me/",
    ]
    urls = "\n".join(
        f"  <url><loc>https://www.caneandcamera.com/{route}</loc></url>" for route in routes
    )
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def build_robots():
    robots = """User-agent: *
Allow: /

Sitemap: https://www.caneandcamera.com/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")

def main():
    build_index_page()
    build_gallery_page(
        gallery_keys=("wildlife", "landscapes"),
        title="Wildlife",
        description="Browse wildlife photography from Rajasthan and India featuring birds, mammals, raptors, and habitat moments captured in natural light with ethical practice.",
        out_file="gallery.html",
    )
    build_gallery_page(
        gallery_keys=("landscapes",),
        title="Landscapes",
        description="Explore Cane & Camera landscapes from Rajasthan and India, including desert horizons, grasslands, and natural-light habitat scenes shaped by seasons.",
        out_file="landscapes.html",
    )
    build_documentaries_page()
    build_about_page()
    build_contact_page()
    patch_landscapes_legacy_page()
    build_pretty_routes()
    build_sitemap()
    build_robots()
    print("Built: index/gallery/landscapes/documentaries/about/contact + pretty routes + sitemap.xml + robots.txt")


if __name__ == "__main__":
    main()
