#!/usr/bin/env python3
import json, html
from pathlib import Path
from datetime import datetime, UTC

ROOT = Path('/workspace/caneandcamera')

with (ROOT/'assets/img/gallery/generated/photos.json').open() as f:
    photos = json.load(f)
with (ROOT/'data/documentaries.json').open() as f:
    docs_raw = json.load(f)

# de-duplicate videos by id while preserving order
seen = set()
docs = []
for d in docs_raw:
    vid = d['id']
    if vid in seen:
        continue
    seen.add(vid)
    docs.append(d)

NAV = [
    ('Home', 'index.html', 'home'),
    ('Gallery', 'gallery.html', 'gallery'),
    ('Films', 'documentaries.html', 'docs'),
    ('About', 'about.html', 'about'),
    ('Collaborate', 'contact.html', 'contact'),
]

SOCIAL = {
    'instagram': 'https://instagram.com/caneandcamera',
    'youtube': 'https://www.youtube.com/@CaneAndCamera/videos',
    'patreon': 'https://www.patreon.com/cw/CaneAndCamera',
    'mhtr': 'https://mhtr.in'
}

FEATURED_PHOTO_SLUGS = ['laggar-falcon', 'great-indian-bustard', 'saker-falcon', 'monitor-lizard']
photo_map = {p['slug']: p for p in photos}
featured_photos = [photo_map[s] for s in FEATURED_PHOTO_SLUGS if s in photo_map]
landscapes = [p for p in photos if p.get('gallery') == 'landscapes']
wildlife = [p for p in photos if p.get('gallery') == 'wildlife']


def pick_variant(item, target=1024):
    variants = item.get('variants', {})
    keys = sorted(int(k) for k in variants)
    chosen = keys[0]
    for k in keys:
        chosen = k
        if k >= target:
            break
    return variants[str(chosen)]


def srcset_for(item):
    variants = item.get('variants', {})
    pairs = []
    for k in sorted((int(k) for k in variants.keys())):
        v = variants[str(k)]
        pairs.append(f"{v['src']} {v['w']}w")
    return ', '.join(pairs)


def card_html(item, sizes='(min-width: 1000px) 45vw, 95vw'):
    thumb = pick_variant(item, 1024)
    full = pick_variant(item, 2048)
    dt = item.get('datetime', '')
    camera = item.get('camera', '')
    desc = item.get('description', '')
    title = item.get('title', 'Untitled')
    srcset = srcset_for(item)
    return f'''<article class="cc-card">
  <img class="cc-thumb" src="{html.escape(thumb['src'])}" srcset="{html.escape(srcset)}" sizes="{sizes}" data-full="{html.escape(full['src'])}" width="{full['w']}" height="{full['h']}" loading="lazy" decoding="async" alt="{html.escape(title)}">
  <div class="cc-meta">
    <strong>{html.escape(title)}</strong>{(' · <time class="muted">'+html.escape(dt)+'</time>') if dt else ''}{(' · <span class="muted">'+html.escape(camera)+'</span>') if camera else ''}
    <div class="cc-desc">{html.escape(desc)}</div>
  </div>
</article>'''


def feature_card(item):
    thumb = pick_variant(item, 1024)
    srcset = srcset_for(item)
    return f'''<article class="feature-card">
<a class="feature-card__link" href="gallery.html">
  <img src="{html.escape(thumb['src'])}" srcset="{html.escape(srcset)}" sizes="(min-width: 1100px) 24vw, (min-width: 700px) 45vw, 100vw" width="{thumb['w']}" height="{thumb['h']}" loading="lazy" decoding="async" alt="{html.escape(item['title'])}">
  <h3>{html.escape(item['title'])}</h3>
  <p>{html.escape(item['description'])}</p>
</a>
</article>'''


def doc_card(doc, full=False):
    vid = doc['id']
    title = doc['title']
    desc = doc['desc']
    if full:
        return f'''<article class="docu-card">
  <iframe src="https://www.youtube.com/embed/{vid}" title="{html.escape(title)}" loading="lazy" allowfullscreen></iframe>
  <div class="docu-meta"><h3>{html.escape(title)}</h3><p>{html.escape(desc)}</p></div>
</article>'''
    return f'''<article class="feature-card">
<a class="feature-card__link" href="documentaries.html">
  <img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" width="480" height="360" loading="lazy" decoding="async" alt="{html.escape(title)}">
  <h3>{html.escape(title)}</h3>
  <p>{html.escape(desc)}</p>
</a>
</article>'''


def json_ld_common(page_url):
    person = {
        '@context': 'https://schema.org',
        '@type': 'Person',
        'name': 'Vinay Chittora',
        'jobTitle': 'Naturalist, Wildlife Filmmaker, Field Storyteller',
        'url': 'https://www.caneandcamera.com/about.html',
        'homeLocation': {'@type': 'Place', 'name': 'Rajasthan, India'},
        'sameAs': [SOCIAL['instagram'], SOCIAL['youtube'], SOCIAL['mhtr']],
        'knowsAbout': ['Mukundara Hills Tiger Reserve', 'Rajasthan wildlife', 'Grassland ecology', 'Wetland ecology', 'Conservation storytelling']
    }
    website = {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': 'Cane & Camera',
        'url': 'https://www.caneandcamera.com/',
        'description': 'Natural history filmmaking, wildlife cinematography, and field-led conservation storytelling from Rajasthan and Mukundara landscapes.'
    }
    return [person, website]


def page(title, description, canonical, active, body, extra_head='', extra_jsonld=None, body_class=''):
    nav = '\n'.join(
        f'<a class="nav-link{(" is-active" if key==active else "")}" href="{href}">{label}</a>'
        for label, href, key in NAV
    )
    jsonlds = json_ld_common(canonical)
    if extra_jsonld:
        jsonlds.extend(extra_jsonld)
    ld_tags = '\n'.join(f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>' for obj in jsonlds)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="https://www.caneandcamera.com/{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="https://www.caneandcamera.com/{canonical}">
  <meta property="og:image" content="https://www.caneandcamera.com/assets/img/thumb/documentaries.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(description)}">
  <meta name="twitter:image" content="https://www.caneandcamera.com/assets/img/thumb/documentaries.jpg">
  <link rel="icon" type="image/png" href="assets/img/ico/favicon.png">
  <link rel="preload" href="assets/css/style.css" as="style">
  <link rel="stylesheet" href="assets/css/style.css">
  <script defer src="assets/js/main.js"></script>
  {extra_head}
  {ld_tags}
</head>
<body class="{body_class}">
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="site-header">
  <div class="container site-header__inner">
    <a href="index.html" class="logo" aria-label="Cane and Camera home">
      <img src="assets/img/ico/logo.svg" alt="Cane & Camera logo" width="48" height="48"/>
      <span>Cane & Camera</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Toggle navigation menu">☰</button>
    <nav id="site-nav" class="site-nav" aria-label="Primary">{nav}</nav>
  </div>
</header>
<main id="main-content" class="wrap">{body}</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <section><h4>Navigate</h4><p><a href="index.html">Home</a> · <a href="gallery.html">Gallery</a> · <a href="documentaries.html">Films</a> · <a href="about.html">About</a> · <a href="contact.html">Collaborate</a></p></section>
    <section><h4>Connect</h4><p><a href="{SOCIAL['instagram']}" target="_blank" rel="noopener">Instagram</a> · <a href="{SOCIAL['youtube']}" target="_blank" rel="noopener">YouTube</a> · <a href="{SOCIAL['patreon']}" target="_blank" rel="noopener">Patreon</a></p><p><a href="{SOCIAL['mhtr']}" target="_blank" rel="noopener">Field notes at mhtr.in</a></p></section>
    <section><h4>Contact</h4><p><b><a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a></b></p><p><a href="contact.html">Start a collaboration inquiry</a></p></section>
  </div>
  <p class="site-footer__legal">© 2026 Cane & Camera · All rights reserved.</p>
</footer>
</body>
</html>'''

home_body = f'''
<section class="hero hero-editorial">
  <p class="eyebrow">Naturalist • Wildlife Filmmaker • Field Storyteller</p>
  <h1>Field-based natural history storytelling from Mukundara Hills and Rajasthan.</h1>
  <p class="lead">I am Vinay Chittora of Cane & Camera. My work combines wildlife cinematography, ecological observation, and on-ground storytelling across Mukundara Hills Tiger Reserve (MHTR), surrounding forest edges, grasslands, wetlands, and desert landscapes.</p>
  <div class="hero-cta-row">
    <a class="btn" href="contact.html">Collaborate on a project</a>
    <a class="btn btn-outline" href="documentaries.html">Watch films</a>
    <a class="btn btn-outline" href="gallery.html">View still gallery</a>
  </div>
</section>
<section class="editorial-section" id="positioning">
  <h2>What this work supports</h2>
  <div class="pillars-grid">
    <article><h3>Wildlife filmmaking & cinematography</h3><p>Short and long-form factual films rooted in field behavior, habitat context, and ethical practice.</p></article>
    <article><h3>Field scouting & story research</h3><p>Location intelligence, seasonal understanding, and practical support for crews working in Rajasthan and MHTR-linked landscapes.</p></article>
    <article><h3>Conservation communication</h3><p>Visual narratives that help audiences understand biodiversity networks, habitat stress, and restoration priorities.</p></article>
  </div>
</section>
<section class="editorial-section" id="mukundara">
  <h2>Mukundara knowledge, beyond one-species narratives</h2>
  <p>This work is grounded in long-term observation of how grasslands, wetlands, scrub, forest edges, insects, reptiles, birds, raptors, and mammals interact. Conservation is strongest when biodiversity is treated as a system—not a trophy list.</p>
  <ul>
    <li>Support for grassland and wetland revival with native ecological context.</li>
    <li>Advocacy for habitat protection and native restoration over ornamental/exotic planting trends.</li>
    <li>A biodiversity-first approach that includes overlooked life forms, not only flagship megafauna.</li>
  </ul>
</section>
<section class="editorial-section">
  <div class="section-head"><h2>Featured films</h2><a href="documentaries.html">See all films →</a></div>
  <div class="feature-grid feature-grid--docs">{''.join(doc_card(d) for d in docs[:3])}</div>
</section>
<section class="editorial-section">
  <div class="section-head"><h2>Selected stills from the field</h2><a href="gallery.html">Open full gallery →</a></div>
  <div class="feature-grid">{''.join(feature_card(p) for p in featured_photos)}</div>
</section>
<section class="editorial-section cta-band">
  <h2>Work with Cane & Camera</h2>
  <p>Available for wildlife filming, cinematography support, field scouting, story development, conservation campaigns, and natural history documentation assignments.</p>
  <p><a class="btn" href="contact.html">Send project brief</a></p>
</section>
'''

home = page(
    'Cane & Camera | Naturalist, Wildlife Filmmaker, Conservation Storyteller in Rajasthan',
    'Cane & Camera presents Vinay Chittora as a field naturalist and wildlife filmmaker from Rajasthan, with deep Mukundara Hills context for conservation storytelling, scouting, and collaborations.',
    'index.html', 'home', home_body)


gallery_body = f'''
<section class="gallery-header">
  <h1>Field Gallery</h1>
  <p>Still photographs that document species behavior, habitat mood, and ecological relationships across Rajasthan and nearby regions.</p>
  <p class="muted">Thumbnail and responsive image variants are loaded automatically for faster browsing; full-resolution variants open in lightbox.</p>
  <div id="cc-masonry" class="cc-masonry">{''.join(card_html(p) for p in wildlife)}</div>
</section>
<div id="lgx" class="lgx" role="dialog" aria-modal="true" aria-hidden="true">
  <img class="lgx__img" alt="Expanded image preview" />
  <div class="lgx__ui"><button class="lgx__btn lgx__close" type="button" aria-label="Close">✕</button><button class="lgx__btn lgx__prev" type="button" aria-label="Previous">←</button><button class="lgx__btn lgx__next" type="button" aria-label="Next">→</button><div class="lgx__caption" aria-live="polite"></div><div class="lgx__bar"><button class="lgx__btn lgx__play" type="button" aria-label="Start slideshow">▶ Play</button><button class="lgx__btn lgx__pause" type="button" aria-label="Pause slideshow" style="display:none">❚❚ Pause</button></div></div>
</div>
'''

gallery = page(
    'Wildlife & Natural History Gallery | Cane & Camera',
    'Browse wildlife and natural history photographs from Rajasthan, including grassland, wetland, scrub, and forest-edge observations with conservation context.',
    'gallery.html', 'gallery', gallery_body,
    extra_head='<script defer src="assets/js/gallery-lightbox.js"></script>', body_class='gallery-page')

land_body = f'''
<section class="gallery-header">
  <h1>Landscape & Habitat Frames</h1>
  <p>Landscape images focused on ecological setting: wetlands, open scrub, grassland edges, and seasonal transitions.</p>
  <div id="cc-masonry" class="cc-masonry">{''.join(card_html(p) for p in landscapes)}</div>
</section>
<div id="lgx" class="lgx" role="dialog" aria-modal="true" aria-hidden="true">
  <img class="lgx__img" alt="Expanded image preview" />
  <div class="lgx__ui"><button class="lgx__btn lgx__close" type="button" aria-label="Close">✕</button><button class="lgx__btn lgx__prev" type="button" aria-label="Previous">←</button><button class="lgx__btn lgx__next" type="button" aria-label="Next">→</button><div class="lgx__caption" aria-live="polite"></div><div class="lgx__bar"><button class="lgx__btn lgx__play" type="button" aria-label="Start slideshow">▶ Play</button><button class="lgx__btn lgx__pause" type="button" aria-label="Pause slideshow" style="display:none">❚❚ Pause</button></div></div>
</div>
'''
land = page('Landscapes & Habitat Context | Cane & Camera','Habitat-focused landscape photographs from Rajasthan that provide ecological context for field stories and wildlife films.','landscapes.html','gallery',land_body,extra_head='<script defer src="assets/js/gallery-lightbox.js"></script>',body_class='gallery-page')

video_objs = []
for d in docs:
    video_objs.append({
        '@context':'https://schema.org','@type':'VideoObject','name':d['title'],'description':d['desc'],'thumbnailUrl':f"https://i.ytimg.com/vi/{d['id']}/hqdefault.jpg",'embedUrl':f"https://www.youtube.com/embed/{d['id']}", 'uploadDate':'2025-01-01'
    })

docs_body = f'''
<section class="gallery-header">
  <h1>Films & Documentaries</h1>
  <p>Wildlife documentaries and conservation films from Mukundara-linked landscapes, Rajasthan grasslands, wetlands, and arid ecosystems.</p>
</section>
<section class="docu-grid">{''.join(doc_card(d, full=True) for d in docs)}</section>
<section class="editorial-section">
  <h2>Need field support for a film?</h2>
  <p>I can support story scouting, local ecological context, and practical field coordination for conservation and natural history productions.</p>
  <p><a class="btn" href="contact.html">Discuss film collaboration</a></p>
</section>
'''

docsp = page('Wildlife Documentaries & Conservation Films | Cane & Camera','Watch conservation-focused wildlife films by Cane & Camera, including MHTR, grassland, wetland, and desert-edge natural history stories.','documentaries.html','docs',docs_body,extra_jsonld=video_objs,body_class='docs-page')

about_body = '''
<section class="about-page">
  <h1>About Cane &amp; Camera</h1>
  <p class="about-intro">I am Vinay Chittora, a Rajasthan-based naturalist and field storyteller working through stills and films. My fieldwork is deeply connected to Mukundara Hills Tiger Reserve (MHTR) and adjacent ecosystems.</p>
  <section class="about-section"><h2>Field orientation</h2><p>The work is habitat-first: documenting ecological relationships, seasonality, and behavior with low disturbance and careful observation.</p></section>
  <section class="about-section"><h2>Conservation position</h2><p>I advocate biodiversity-led conservation. Forests, wetlands, and grasslands function as networks; meaningful protection cannot focus on one species while neglecting native plants, insects, reptiles, birds, and habitat processes.</p></section>
  <section class="about-section"><h2>Ethics in practice</h2><ul><li>No baiting, call playback, handling, or forced proximity.</li><li>Low-impact movement and strict respect for site protocols.</li><li>Field outputs designed for awareness, accountability, and long-term documentation.</li></ul></section>
  <section class="about-section"><h2>Where this can help</h2><p>Useful for editorial teams, NGOs, educators, mission-led brands, and film crews that need grounded natural history storytelling from Rajasthan and Mukundara landscapes.</p><p><a href="contact.html">See collaboration options →</a></p></section>
</section>
'''
about = page('About Vinay Chittora | Naturalist & Wildlife Filmmaker | Cane & Camera','Learn about Vinay Chittora’s field-based natural history practice in Mukundara Hills and Rajasthan, and his biodiversity-first conservation storytelling approach.','about.html','about',about_body)

contact_body = '''
<section class="work-page">
  <h1>Collaborate / Work With Me</h1>
  <p class="about-intro">For wildlife filmmaking, cinematography support, field scouting, natural history documentation, and conservation storytelling collaborations.</p>
  <section class="about-section"><h2>Project types</h2><ul><li>Wildlife documentary production and cinematography</li><li>Field scouting and story research support (MHTR / Mukundara / Rajasthan)</li><li>Natural history documentation for awareness and education</li><li>Conservation campaign visuals and communication assets</li><li>Editorial licensing and assignment work</li></ul></section>
  <section class="about-section"><h2>What to include in your inquiry</h2><ul><li>Project goal and format (film, campaign, editorial, research support)</li><li>Location, timeline, and expected field days</li><li>Deliverables and usage scope</li></ul></section>
  <section class="contact-panel"><h2>Contact</h2><p><b>Email:</b> <a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a></p><p><b>Instagram:</b> <a href="https://instagram.com/caneandcamera" target="_blank" rel="noopener">instagram.com/caneandcamera</a></p><p><b>YouTube:</b> <a href="https://www.youtube.com/@CaneAndCamera/videos" target="_blank" rel="noopener">youtube.com/@CaneAndCamera</a></p><p><b>MHTR field notes:</b> <a href="https://mhtr.in" target="_blank" rel="noopener">mhtr.in</a></p><p><a class="btn" href="mailto:hello@caneandcamera.com?subject=Collaboration%20Inquiry%20-%20Cane%20and%20Camera">Email project details</a></p></section>
</section>
'''
contact = page('Collaborate With Cane & Camera | Wildlife Film, Field Scouting, Conservation Storytelling','Contact Cane & Camera for wildlife filmmaking, field scouting, ecological story research, and conservation communication collaborations in Rajasthan and Mukundara landscapes.','contact.html','contact',contact_body)

pages = {
    'index.html': home,
    'gallery.html': gallery,
    'landscapes.html': land,
    'documentaries.html': docsp,
    'about.html': about,
    'contact.html': contact,
}

for filename, content in pages.items():
    (ROOT/filename).write_text(content)

# pretty-route mirrors
mirrors = {
    'about/index.html': about,
    'gallery/index.html': gallery,
    'landscapes/index.html': land,
    'documentaries/index.html': docsp,
    'contact/index.html': contact,
    'work-with-me/index.html': contact,
}
for rel, content in mirrors.items():
    out = content.replace('<head>', '<head>\n  <base href="../">', 1)
    (ROOT/rel).write_text(out)

# robots + sitemap
robots = 'User-agent: *\nAllow: /\n\nSitemap: https://www.caneandcamera.com/sitemap.xml\n'
(ROOT/'robots.txt').write_text(robots)

urls = [
'https://www.caneandcamera.com/index.html',
'https://www.caneandcamera.com/gallery.html',
'https://www.caneandcamera.com/landscapes.html',
'https://www.caneandcamera.com/documentaries.html',
'https://www.caneandcamera.com/about.html',
'https://www.caneandcamera.com/contact.html',
'https://www.caneandcamera.com/gallery/',
'https://www.caneandcamera.com/landscapes/',
'https://www.caneandcamera.com/documentaries/',
'https://www.caneandcamera.com/about/',
'https://www.caneandcamera.com/contact/',
'https://www.caneandcamera.com/work-with-me/',
]
lastmod = datetime.now(UTC).date().isoformat()
xml = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    xml.append(f'  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod></url>')
xml.append('</urlset>')
(ROOT/'sitemap.xml').write_text('\n'.join(xml)+'\n')
