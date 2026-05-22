#!/usr/bin/env python3
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

with (ROOT / "assets/img/gallery/generated/photos.json").open() as f:
    photos = json.load(f)
with (ROOT / "data/documentaries.json").open() as f:
    docs_raw = json.load(f)

# De-duplicate videos by id while preserving editorial order.
seen = set()
docs = []
for d in docs_raw:
    vid = d["id"]
    if vid in seen:
        continue
    seen.add(vid)
    docs.append(d)

NAV = [
    ("Home", "index.html", "home"),
    ("Field Index", "gallery.html", "gallery"),
    ("Films", "documentaries.html", "docs"),
    ("About", "about.html", "about"),
    ("Collaborate", "contact.html", "contact"),
]

SOCIAL = {
    "instagram": "https://instagram.com/caneandcamera",
    "youtube": "https://www.youtube.com/@CaneAndCamera/videos",
    "patreon": "https://www.patreon.com/cw/CaneAndCamera",
    "mhtr": "https://mhtr.in",
}

BMC_WIDGET = ""

photo_map = {p["slug"]: p for p in photos}
wildlife = [p for p in photos if p.get("gallery") == "wildlife"]
landscapes = [p for p in photos if p.get("gallery") == "landscapes"]

PHOTO_NOTES = {
    "great-indian-bustard": {
        "habitat": "Thar grassland",
        "role": "Critically endangered grassland bird",
        "tags": ["grassland", "thar", "flagship", "movement"],
        "story": "A rare flight across open country: the frame is about space, silence, and how much a grassland must still hold for this bird to survive.",
    },
    "laggar-falcon": {
        "habitat": "Open scrub and grassland",
        "role": "Resident raptor",
        "tags": ["raptors", "grassland", "watchpoints"],
        "story": "A falcon on a low perch turns the grassland into a map of thermals, rodents, wind and waiting.",
    },
    "laggar-falcon-2": {
        "habitat": "Desert edge scrub",
        "role": "Resident raptor",
        "tags": ["raptors", "grassland", "watchpoints"],
        "story": "A second look at the same hunter's world: sparse perches, clean light and a landscape built for patience.",
    },
    "saker-falcon": {
        "habitat": "Winter desert edge",
        "role": "Scarce winter migrant",
        "tags": ["raptors", "winter", "movement", "grassland"],
        "story": "A winter visitor carrying the scale of continents into one quiet perch.",
    },
    "white-eyed-buzzard": {
        "habitat": "Dry scrub edge",
        "role": "Raptor of open country",
        "tags": ["raptors", "scrub", "watchpoints"],
        "story": "The pale eye, the post, the dry scrub: a simple field sign that open habitats still support hunters.",
    },
    "oriental-honey-buzzard": {
        "habitat": "Forest edge",
        "role": "Specialist raptor",
        "tags": ["raptors", "forest-edge", "insects"],
        "story": "A raptor connected to hives, canopy and quiet forest edges rather than the easy drama of pursuit.",
    },
    "crested-serpent-eagle": {
        "habitat": "Wooded edge",
        "role": "Snake specialist",
        "tags": ["raptors", "forest-edge", "reptiles"],
        "story": "Bold barring, still posture, and a reminder that reptiles are central to the food web.",
    },
    "monitor-lizard": {
        "habitat": "Leaf litter and rocky cover",
        "role": "Predator and scavenger",
        "tags": ["small-lives", "reptiles", "forest-edge", "behavior"],
        "story": "The frame refuses the postcard version of wildlife. Scales, leaf litter, prey and hunger are the real field grammar.",
    },
    "greater-flamingo": {
        "habitat": "Wetland shallows",
        "role": "Wetland filter-feeder",
        "tags": ["wetland", "water", "migration"],
        "story": "Pastel light, saline water and long legs: a wetland portrait that depends on depth, chemistry and safe distance.",
    },
    "gray-heron": {
        "habitat": "Wetland edge",
        "role": "Patient waterbird",
        "tags": ["wetland", "water", "patience"],
        "story": "A bird that makes stillness useful. Wetlands reward the observer who can wait longer than the ripple.",
    },
    "white-breasted-kingfisher": {
        "habitat": "Waterline and farmland edge",
        "role": "Generalist hunter",
        "tags": ["wetland", "water", "edge"],
        "story": "Bright color at the waterline, where village edges, tanks and fields become hunting ground.",
    },
    "baya-weaver": {
        "habitat": "Reeds and wet grass",
        "role": "Nest builder",
        "tags": ["wetland", "grassland", "behavior", "monsoon"],
        "story": "Architecture made from grass, timing and rain.",
    },
    "baya-weaver-2": {
        "habitat": "Monsoon grass",
        "role": "Nest attendant",
        "tags": ["wetland", "grassland", "behavior", "monsoon"],
        "story": "A nest is not scenery; it is labor, risk and seasonality hanging over water.",
    },
    "jacobin-cuckoo": {
        "habitat": "Monsoon woodland",
        "role": "Seasonal signal",
        "tags": ["monsoon", "forest-edge", "movement"],
        "story": "The monsoon has its own field marks, and this bird is one of the loudest.",
    },
    "indian-cuckoo": {
        "habitat": "Monsoon woodland",
        "role": "Canopy caller",
        "tags": ["monsoon", "forest-edge", "sound"],
        "story": "A pause between calls; enough time to notice rain light moving through the leaves.",
    },
    "indian-golden-oriole": {
        "habitat": "Summer canopy",
        "role": "Canopy frugivore and singer",
        "tags": ["forest-edge", "canopy", "summer"],
        "story": "A flash of yellow that makes the canopy feel briefly electric.",
    },
    "plum-headed-parakeet": {
        "habitat": "Fruiting canopy",
        "role": "Canopy feeder",
        "tags": ["forest-edge", "canopy"],
        "story": "Color, fruit and motion: the forest edge as a feeding table.",
    },
    "oriental-white-eye": {
        "habitat": "Flowering scrub",
        "role": "Tiny canopy forager",
        "tags": ["small-lives", "forest-edge", "canopy"],
        "story": "A small bird that makes a shrub feel like a whole forest.",
    },
    "brown-breasted-flycatcher": {
        "habitat": "Shaded woodland pocket",
        "role": "Insect hunter",
        "tags": ["small-lives", "forest-edge", "insects"],
        "story": "Soft shade, alert posture and the invisible flight paths of insects.",
    },
    "eurasian-wryneck": {
        "habitat": "Tree bark and ant trails",
        "role": "Cryptic specialist",
        "tags": ["small-lives", "forest-edge", "insects"],
        "story": "Cryptic plumage is not camouflage in a photograph; it is an entire way of living.",
    },
    "black-rumped-flameback": {
        "habitat": "Trunks and groves",
        "role": "Woodpecker",
        "tags": ["forest-edge", "canopy", "insects"],
        "story": "A trunk becomes a pantry, a drum and a territory marker.",
    },
    "scaly-breasted-munia": {
        "habitat": "Seed grasses",
        "role": "Grassland granivore",
        "tags": ["small-lives", "grassland", "seed"],
        "story": "The scale pattern catches the eye, but the real story is seed, cover and a good patch of grass.",
    },
    "scaly-breasted-munia-2": {
        "habitat": "Seed grasses",
        "role": "Grassland granivore",
        "tags": ["small-lives", "grassland", "seed"],
        "story": "A small bird in soft light, showing why grass is habitat before it is background.",
    },
    "isabelline-wheatear": {
        "habitat": "Open desert scrub",
        "role": "Ground hunter",
        "tags": ["grassland", "thar", "open-country"],
        "story": "A mound, a bird and a lot of empty air: open country at its most honest.",
    },
    "indian-courser": {
        "habitat": "Short grass and bare earth",
        "role": "Ground bird",
        "tags": ["grassland", "thar", "open-country"],
        "story": "Built for running through heat shimmer and short grass, not for disappearing into forest.",
    },
    "towny-lark": {
        "habitat": "Dry grassland",
        "role": "Ground songbird",
        "tags": ["grassland", "thar", "open-country"],
        "story": "A desert palette in bird form: quiet tones, clean posture, useful restraint.",
    },
    "towny-lark-2": {
        "habitat": "Open plains",
        "role": "Ground songbird",
        "tags": ["grassland", "thar", "open-country"],
        "story": "Side light on a small bird, and a whole plain implied around it.",
    },
    "grey-necked-bunting": {
        "habitat": "Stony dry country",
        "role": "Seed eater",
        "tags": ["grassland", "thar", "seed"],
        "story": "Stone, seed and muted color: the desert does not need to shout.",
    },
    "brown-shrike": {
        "habitat": "Thorn scrub",
        "role": "Migrant hunter",
        "tags": ["grassland", "scrub", "movement"],
        "story": "A thorn perch as watchtower, pantry and field note.",
    },
    "siberian-stonechat": {
        "habitat": "Winter grass stems",
        "role": "Migrant insect hunter",
        "tags": ["grassland", "winter", "movement"],
        "story": "A winter migrant turning a single grass stem into a hunting post.",
    },
    "northern-plains-gray-langur": {
        "habitat": "Village grove and forest edge",
        "role": "Primate neighbor",
        "tags": ["forest-edge", "mammals", "coexistence"],
        "story": "A face from the shared edge of settlement and wild habitat.",
    },
    "spotted-owlet": {
        "habitat": "Tree hollow and village grove",
        "role": "Small owl",
        "tags": ["forest-edge", "night", "coexistence"],
        "story": "A familiar neighbor that still asks for respectful distance.",
    },
    "woodswallow": {
        "habitat": "Open sky and wires",
        "role": "Aerial insect hunter",
        "tags": ["open-country", "insects", "coexistence"],
        "story": "A wire is not wild habitat, but fieldwork includes the altered edges animals learn to use.",
    },
    "red-collared-dove": {
        "habitat": "Open scrub",
        "role": "Seed eater",
        "tags": ["grassland", "scrub", "seed"],
        "story": "Soft color, open ground and the understated life between bigger sightings.",
    },
}

FIELD_STUDIES = [
    {
        "id": "raptors",
        "label": "Raptors",
        "title": "Raptors Read the Wind",
        "cover": "laggar-falcon",
        "dek": "Falcons, buzzards and eagles as field indicators of prey, perches, season and open habitat health.",
        "slugs": ["laggar-falcon", "saker-falcon", "white-eyed-buzzard", "oriental-honey-buzzard"],
    },
    {
        "id": "grassland",
        "label": "Grasslands",
        "title": "The Open-Country Ledger",
        "cover": "great-indian-bustard",
        "dek": "Bustards, coursers, larks, buntings and shrikes tell the story of Rajasthan's threatened grassland systems.",
        "slugs": ["great-indian-bustard", "indian-courser", "isabelline-wheatear", "towny-lark-2"],
    },
    {
        "id": "wetland",
        "label": "Wetlands",
        "title": "Edges of Water",
        "cover": "greater-flamingo",
        "dek": "A patient look at tanks, reedbeds and shallows where waterbirds, nest builders and human pressure meet.",
        "slugs": ["greater-flamingo", "gray-heron", "white-breasted-kingfisher", "baya-weaver"],
    },
    {
        "id": "forest-edge",
        "label": "Forest Edge",
        "title": "Canopy, Bark and Shade",
        "cover": "indian-golden-oriole",
        "dek": "The quieter side of the portfolio: groves, calls, insects and the shaded lives around Mukundara-linked edges.",
        "slugs": ["indian-golden-oriole", "jacobin-cuckoo", "eurasian-wryneck", "black-rumped-flameback"],
    },
    {
        "id": "small-lives",
        "label": "Small Lives",
        "title": "The Overlooked Majority",
        "cover": "monitor-lizard",
        "dek": "Reptiles, small birds, insects and behavior-led moments that make biodiversity feel close and consequential.",
        "slugs": ["monitor-lizard", "scaly-breasted-munia-2", "oriental-white-eye", "brown-breasted-flycatcher"],
    },
]

FEATURED_PHOTO_SLUGS = [
    "great-indian-bustard",
    "laggar-falcon",
    "monitor-lizard",
    "jacobin-cuckoo",
    "northern-plains-gray-langur",
    "plum-headed-parakeet",
]

MACAULAY_EMBEDS = [
    {
        "id": "657795282",
        "title": "Small Minivet",
        "note": "Mandirgarh, Rajasthan",
    },
    {
        "id": "657795273",
        "title": "Barred Buttonquail",
        "note": "Mandirgarh, Rajasthan",
    },
    {
        "id": "657795019",
        "title": "Asian Woolly-necked Stork",
        "note": "Mandirgarh, Rajasthan",
    },
    {
        "id": "657794944",
        "title": "Brown-capped Pygmy Woodpecker",
        "note": "Bardha Dam, Rajasthan",
    },
    {
        "id": "657794868",
        "title": "Gray Heron",
        "note": "Bardha Dam, Rajasthan",
    },
    {
        "id": "657794725",
        "title": "Tickell's Blue Flycatcher",
        "note": "Bardha Dam, Rajasthan",
    },
]


def h(text):
    return html.escape(str(text or ""))


def pick_variant(item, target=1024):
    variants = item.get("variants", {})
    if not variants:
        raise ValueError(f"Photo {item.get('slug')} has no variants")
    keys = sorted(int(k) for k in variants)
    chosen = keys[-1]
    for k in keys:
        chosen = k
        if k >= target:
            break
    return variants[str(chosen)]


def srcset_for(item):
    variants = item.get("variants", {})
    pairs = []
    for k in sorted((int(k) for k in variants.keys())):
        v = variants[str(k)]
        pairs.append(f"{v['src']} {v['w']}w")
    return ", ".join(pairs)


def photo_note(item):
    return PHOTO_NOTES.get(item.get("slug"), {})


def photo_tags(item):
    note = photo_note(item)
    tags = set(note.get("tags", []))
    title = f"{item.get('title', '')} {item.get('description', '')}".lower()
    if any(word in title for word in ["falcon", "buzzard", "eagle"]):
        tags.add("raptors")
    if any(word in title for word in ["flamingo", "heron", "kingfisher", "weaver"]):
        tags.add("wetland")
    if any(word in title for word in ["bustard", "courser", "lark", "bunting", "wheatear", "shrike", "stonechat"]):
        tags.add("grassland")
    if any(word in title for word in ["oriole", "cuckoo", "woodpecker", "wryneck", "white-eye", "flycatcher", "langur", "owlet"]):
        tags.add("forest-edge")
    if any(word in title for word in ["monitor", "munia", "white-eye", "flycatcher", "wryneck"]):
        tags.add("small-lives")
    return sorted(tags)


def format_date(raw):
    if not raw:
        return ""
    try:
        dt = datetime.fromisoformat(raw[:10])
        return dt.strftime("%b %Y")
    except ValueError:
        return raw[:10]


def image_html(item, class_name, target=1024, sizes="100vw", alt=None, loading="lazy", fetchpriority=None, data_full=False):
    thumb = pick_variant(item, target)
    full = pick_variant(item, 2048)
    attrs = [
        f'class="{h(class_name)}"',
        f'src="{h(thumb["src"])}"',
        f'srcset="{h(srcset_for(item))}"',
        f'sizes="{h(sizes)}"',
        f'width="{full["w"]}"',
        f'height="{full["h"]}"',
        f'loading="{loading}"',
        'decoding="async"',
        f'alt="{h(alt or item.get("title", ""))}"',
    ]
    if fetchpriority:
        attrs.append(f'fetchpriority="{fetchpriority}"')
    if data_full:
        attrs.append(f'data-full="{h(full["src"])}"')
    return f"<img {' '.join(attrs)}>"


def hero_image(slug):
    item = photo_map[slug]
    return image_html(
        item,
        "hero-portfolio__image",
        target=2048,
        sizes="100vw",
        alt="Great Indian Bustard flying over Rajasthan grassland",
        loading="eager",
        fetchpriority="high",
    )


def mini_strip(slugs):
    imgs = []
    for slug in slugs:
        item = photo_map.get(slug)
        if not item:
            continue
        imgs.append(image_html(item, "study-card__mini", target=512, sizes="96px", alt=item["title"]))
    return "".join(imgs)


def study_card(study):
    cover = photo_map.get(study["cover"])
    cover_img = image_html(
        cover,
        "study-card__cover",
        target=1024,
        sizes="(min-width: 980px) 32vw, 100vw",
        alt=cover["title"],
    )
    return f'''<article class="study-card" data-study="{h(study["id"])}">
  <a class="study-card__link" href="gallery.html#{h(study["id"])}">
    {cover_img}
    <div class="study-card__body">
      <p class="kicker">{h(study["label"])}</p>
      <h3>{h(study["title"])}</h3>
      <p>{h(study["dek"])}</p>
      <div class="study-card__strip" aria-hidden="true">{mini_strip(study["slugs"][1:4])}</div>
    </div>
  </a>
</article>'''


def photo_card(item, sizes="(min-width: 1100px) 31vw, (min-width: 700px) 46vw, 100vw"):
    note = photo_note(item)
    title = item.get("title", "Untitled")
    desc = note.get("story") or item.get("description", "")
    habitat = note.get("habitat") or item.get("gallery", "field").replace("-", " ").title()
    role = note.get("role") or "Field observation"
    camera = item.get("camera", "")
    dt = format_date(item.get("datetime", ""))
    tags = photo_tags(item)
    img = image_html(item, "cc-thumb", target=1024, sizes=sizes, alt=title, data_full=True)
    chips = "".join(f'<span>{h(t.replace("-", " "))}</span>' for t in tags[:3])
    facts = " / ".join(part for part in [dt, camera] if part)
    return f'''<article class="cc-card field-card" data-tags="{h(" ".join(tags))}">
  {img}
  <div class="cc-meta">
    <p class="field-card__eyebrow">{h(habitat)}</p>
    <h3>{h(title)}</h3>
    <p class="field-card__role">{h(role)}</p>
    <p class="cc-desc">{h(desc)}</p>
    <div class="field-card__footer">
      <span class="muted">{h(facts)}</span>
      <span class="field-card__chips">{chips}</span>
    </div>
  </div>
</article>'''


def featured_frame(slug):
    item = photo_map[slug]
    note = photo_note(item)
    img = image_html(
        item,
        "featured-frame__image",
        target=1024,
        sizes="(min-width: 980px) 32vw, 100vw",
        alt=item["title"],
    )
    return f'''<article class="featured-frame">
  <a href="gallery.html#{h((photo_tags(item) or ["all"])[0])}">
    {img}
    <div>
      <p class="kicker">{h(note.get("habitat", "Field observation"))}</p>
      <h3>{h(item["title"])}</h3>
      <p>{h(note.get("story") or item.get("description"))}</p>
    </div>
  </a>
</article>'''


def macaulay_embed_card(item):
    asset_id = item["id"]
    title = item["title"]
    note = item.get("note", "")
    return f'''<article class="macaulay-card">
  <iframe class="macaulay-card__embed" src="https://macaulaylibrary.org/asset/{h(asset_id)}/embed" title="Macaulay Library embed: {h(title)}" loading="lazy" referrerpolicy="strict-origin-when-cross-origin"></iframe>
  <div class="macaulay-card__meta">
    <h3>{h(title)}</h3>
    <p>{h(note)} / <a href="https://macaulaylibrary.org/asset/{h(asset_id)}" target="_blank" rel="noopener">ML{h(asset_id)}</a></p>
  </div>
</article>'''


def doc_card(doc, full=False):
    vid = doc["id"]
    title = doc["title"]
    desc = doc["desc"]
    if full:
        return f'''<article class="docu-card">
  <iframe src="https://www.youtube.com/embed/{vid}" title="{h(title)}" loading="lazy" allowfullscreen></iframe>
  <div class="docu-meta"><p class="kicker">Field film</p><h3>{h(title)}</h3><p>{h(desc)}</p></div>
</article>'''
    return f'''<article class="film-card">
  <a class="film-card__link" href="documentaries.html">
    <img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" width="480" height="360" loading="lazy" decoding="async" alt="{h(title)}">
    <div><p class="kicker">Film</p><h3>{h(title)}</h3><p>{h(desc)}</p></div>
  </a>
</article>'''


def json_ld_common(page_url):
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Vinay Chittora",
        "jobTitle": "Naturalist, Wildlife Filmmaker, Field Storyteller",
        "url": "https://www.caneandcamera.com/about.html",
        "homeLocation": {"@type": "Place", "name": "Rajasthan, India"},
        "sameAs": [SOCIAL["instagram"], SOCIAL["youtube"], SOCIAL["mhtr"]],
        "knowsAbout": [
            "Mukundara Hills Tiger Reserve",
            "Rajasthan wildlife",
            "Grassland ecology",
            "Wetland ecology",
            "Conservation storytelling",
            "Field scouting",
        ],
    }
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Cane & Camera",
        "url": "https://www.caneandcamera.com/",
        "description": "A naturalist portfolio of wildlife filmmaking, field observation, and conservation storytelling from Rajasthan.",
    }
    organization = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Cane & Camera",
        "url": "https://www.caneandcamera.com/",
        "founder": {"@type": "Person", "name": "Vinay Chittora"},
        "sameAs": [SOCIAL["instagram"], SOCIAL["youtube"], SOCIAL["mhtr"]],
    }
    return [person, website, organization]


def page(title, description, canonical, active, body, extra_head="", extra_jsonld=None, body_class="", og_image=None):
    nav = "\n".join(
        f'<a class="nav-link{(" is-active" if key == active else "")}" href="{href}">{label}</a>'
        for label, href, key in NAV
    )
    jsonlds = json_ld_common(canonical)
    if extra_jsonld:
        jsonlds.extend(extra_jsonld)
    ld_tags = "\n".join(
        f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'
        for obj in jsonlds
    )
    og = og_image or "https://www.caneandcamera.com/assets/img/gallery/generated/wildlife/great-indian-bustard-2048.jpg"
    head_extra = f"  {extra_head}\n" if extra_head else ""
    footer_extra = f"  {BMC_WIDGET}\n" if BMC_WIDGET else ""
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(title)}</title>
  <meta name="description" content="{h(description)}">
  <link rel="canonical" href="https://www.caneandcamera.com/{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{h(title)}">
  <meta property="og:description" content="{h(description)}">
  <meta property="og:url" content="https://www.caneandcamera.com/{canonical}">
  <meta property="og:image" content="{h(og)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{h(title)}">
  <meta name="twitter:description" content="{h(description)}">
  <meta name="twitter:image" content="{h(og)}">
  <link rel="icon" type="image/png" href="assets/img/ico/favicon.png">
  <link rel="preload" href="assets/css/style.css" as="style">
  <link rel="stylesheet" href="assets/css/style.css">
  <script defer src="assets/js/main.js"></script>
{head_extra.rstrip()}
  {ld_tags}
</head>
<body class="{h(body_class)}">
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="site-header">
  <div class="container site-header__inner">
    <a href="index.html" class="logo" aria-label="Cane and Camera home">
      <img src="assets/img/ico/logo.svg" alt="Cane & Camera logo" width="48" height="48">
      <span>Cane & Camera</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Toggle navigation menu">Menu</button>
    <nav id="site-nav" class="site-nav" aria-label="Primary">{nav}</nav>
  </div>
</header>
<main id="main-content" class="wrap">{body}</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <section><h4>Navigate</h4><p><a href="index.html">Home</a> / <a href="gallery.html">Field Index</a> / <a href="documentaries.html">Films</a> / <a href="about.html">About</a> / <a href="contact.html">Collaborate</a></p></section>
    <section><h4>Connect</h4><p><a href="{SOCIAL["instagram"]}" target="_blank" rel="noopener">Instagram</a> / <a href="{SOCIAL["youtube"]}" target="_blank" rel="noopener">YouTube</a> / <a href="{SOCIAL["patreon"]}" target="_blank" rel="noopener">Patreon</a></p><p><a href="{SOCIAL["mhtr"]}" target="_blank" rel="noopener">Field notes at mhtr.in</a></p></section>
    <section><h4>Contact</h4><p><b><a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a></b></p><p><a href="contact.html">Start a collaboration inquiry</a></p></section>
  </div>
  <p class="site-footer__legal">(c) 2026 Cane & Camera. All rights reserved.</p>
{footer_extra.rstrip()}
</footer>
</body>
</html>'''


home_body = f'''
<section class="hero-portfolio">
  <div class="hero-portfolio__media">{hero_image("great-indian-bustard")}</div>
  <div class="hero-portfolio__content">
    <p class="kicker">Vinay Chittora / Rajasthan field naturalist</p>
    <h1>Cane &amp; Camera</h1>
    <p class="hero-portfolio__line">A naturalist's portfolio of wildlife films, field notes, and biodiversity stories from Mukundara-linked landscapes, Thar grasslands, wetlands and forest edges.</p>
    <div class="hero-portfolio__actions">
      <a class="btn" href="gallery.html">Enter the field index</a>
      <a class="btn btn-ghost" href="documentaries.html">Watch films</a>
      <a class="btn btn-ghost" href="contact.html">Collaborate</a>
    </div>
  </div>
  <div class="hero-portfolio__specimen">
    <span>Field practice</span>
    <b>Observe first. Film second. Leave the scene intact.</b>
  </div>
</section>

<section class="portfolio-section intro-split">
  <div>
    <p class="kicker">What this is</p>
    <h2>A working field portfolio, not a stock gallery.</h2>
  </div>
  <p>Cane &amp; Camera is built around patient natural history work: reading habitats, understanding behavior, and translating field encounters into photographs, films and conservation communication that still feel close to the ground.</p>
</section>

<section class="portfolio-section">
  <div class="section-head">
    <div><p class="kicker">Current field studies</p><h2>Five ways into the landscape</h2></div>
    <a href="gallery.html">Open the full index</a>
  </div>
  <div class="study-grid">{''.join(study_card(s) for s in FIELD_STUDIES)}</div>
</section>

<section class="portfolio-section field-method">
  <div>
    <p class="kicker">Field method</p>
    <h2>The frame begins before the camera comes up.</h2>
  </div>
  <div class="method-grid">
    <article><span>01</span><h3>Habitat reading</h3><p>Grass height, water level, fruiting trees, perches, tracks and calls decide the story before a subject appears.</p></article>
    <article><span>02</span><h3>Low-disturbance work</h3><p>No baiting, playback, handling or forced proximity. The image is never worth breaking the scene.</p></article>
    <article><span>03</span><h3>Biodiversity-first context</h3><p>Flagship species matter, but so do shrubs, insects, reptiles, seed eaters, wetlands and the overlooked edges that keep systems alive.</p></article>
  </div>
</section>

<section class="portfolio-section">
  <div class="section-head">
    <div><p class="kicker">Selected frames</p><h2>Portfolio edit</h2></div>
    <a href="gallery.html">Browse by habitat</a>
  </div>
  <div class="featured-frame-grid">{''.join(featured_frame(slug) for slug in FEATURED_PHOTO_SLUGS if slug in photo_map)}</div>
</section>

<section class="portfolio-section film-band">
  <div class="section-head">
    <div><p class="kicker">Films</p><h2>Field stories in motion</h2></div>
    <a href="documentaries.html">See all films</a>
  </div>
  <div class="film-grid">{''.join(doc_card(d) for d in docs[:3])}</div>
</section>

<section class="portfolio-section field-note-band">
  <div>
    <p class="kicker">Mukundara context</p>
    <h2>A landscape is more than a headline animal.</h2>
    <p>My field work around Mukundara Hills Tiger Reserve and Rajasthan's connected habitats looks at movement routes, wetland edges, grassland revival, native plants, reptiles, insects, birds and the daily negotiations between people and wild life.</p>
  </div>
  <a class="btn" href="https://mhtr.in" target="_blank" rel="noopener">Read field notes at mhtr.in</a>
</section>

<section class="portfolio-section cta-band">
  <p class="kicker">Collaborations</p>
  <h2>For films, field scouting, conservation campaigns and natural history documentation.</h2>
  <p>If the project needs local ecological context, ethical field execution, or a naturalist's eye behind the camera, start with a short brief.</p>
  <p><a class="btn" href="contact.html">Send a project brief</a></p>
</section>
'''

home = page(
    "Cane & Camera | Naturalist Portfolio of Vinay Chittora",
    "Cane & Camera is Vinay Chittora's naturalist portfolio for wildlife films, field photography, scouting, and conservation storytelling from Rajasthan.",
    "index.html",
    "home",
    home_body,
    body_class="home-page",
)

gallery_filters = [
    ("all", "All"),
    ("raptors", "Raptors"),
    ("grassland", "Grasslands"),
    ("wetland", "Wetlands"),
    ("forest-edge", "Forest edge"),
    ("small-lives", "Small lives"),
]
filter_buttons = "".join(
    f'<button class="filter-chip{(" is-active" if key == "all" else "")}" type="button" data-filter="{key}">{label}</button>'
    for key, label in gallery_filters
)

gallery_body = f'''
<section class="gallery-hero">
  <div class="gallery-hero__media">{image_html(photo_map["monitor-lizard"], "gallery-hero__image", target=2048, sizes="100vw", alt="Bengal monitor feeding in leaf litter", loading="eager", fetchpriority="high")}</div>
  <div class="gallery-hero__content">
    <p class="kicker">Field index</p>
    <h1>Field Index</h1>
    <p>Photographs arranged like a naturalist's notebook: by ecological role, habitat and behavior instead of a loose image dump. The structure can grow as better field photographs are added.</p>
  </div>
</section>

<section class="portfolio-section">
  <div class="section-head">
    <div><p class="kicker">Studies</p><h2>Start with a story system</h2></div>
    <span class="muted">Curated by habitat and behavior</span>
  </div>
  <div class="study-grid study-grid--compact">{''.join(study_card(s) for s in FIELD_STUDIES)}</div>
</section>

<section class="portfolio-section gallery-panel" aria-labelledby="field-index-heading">
  <div class="gallery-panel__head">
    <div><p class="kicker">Browse the plates</p><h2 id="field-index-heading">Field plates</h2></div>
    <div class="gallery-count"><span id="gallery-count">{len(wildlife)}</span> frames shown</div>
  </div>
  <div class="filter-bar" aria-label="Filter photographs">{filter_buttons}</div>
  <div id="cc-masonry" class="cc-masonry">{''.join(photo_card(p) for p in wildlife)}</div>
</section>

<section class="portfolio-section macaulay-section">
  <div class="section-head">
    <div><p class="kicker">Live archive</p><h2>Macaulay Library selections</h2></div>
    <a href="https://search.macaulaylibrary.org/catalog?searchField=user&userId=USER1136410" target="_blank" rel="noopener">Open full Macaulay collection</a>
  </div>
  <p class="macaulay-section__note">Embedded through Macaulay Library's official media embed so credit and archive metadata stay attached to each record.</p>
  <div class="macaulay-grid">{''.join(macaulay_embed_card(item) for item in MACAULAY_EMBEDS)}</div>
</section>

<div id="lgx" class="lgx" role="dialog" aria-modal="true" aria-hidden="true">
  <img class="lgx__img" alt="Expanded image preview">
  <div class="lgx__ui">
    <button class="lgx__btn lgx__close" type="button" aria-label="Close">&times;</button>
    <button class="lgx__btn lgx__prev" type="button" aria-label="Previous">&lsaquo;</button>
    <button class="lgx__btn lgx__next" type="button" aria-label="Next">&rsaquo;</button>
    <div class="lgx__caption" aria-live="polite"></div>
    <div class="lgx__bar"><button class="lgx__btn lgx__play" type="button" aria-label="Start slideshow">&#9654;</button><button class="lgx__btn lgx__pause" type="button" aria-label="Pause slideshow" style="display:none">&#10073;&#10073;</button></div>
  </div>
</div>
'''

gallery = page(
    "Field Index | Wildlife Photography Portfolio | Cane & Camera",
    "A curated field index of Cane & Camera wildlife photographs arranged by raptors, grasslands, wetlands, forest edge species, and overlooked small lives.",
    "gallery.html",
    "gallery",
    gallery_body,
    extra_head='<script defer src="assets/js/gallery-lightbox.js"></script>',
    body_class="gallery-page",
    og_image="https://www.caneandcamera.com/assets/img/gallery/generated/wildlife/monitor-lizard-2048.jpg",
)

land_body = f'''
<section class="gallery-hero gallery-hero--quiet">
  <div class="gallery-hero__media">{image_html(photo_map.get("towny-lark-2", landscapes[0]), "gallery-hero__image", target=2048, sizes="100vw", alt="Open plains habitat frame", loading="eager", fetchpriority="high")}</div>
  <div class="gallery-hero__content">
    <p class="kicker">Habitat frames</p>
    <h1>The landscape is not background.</h1>
    <p>These frames hold the setting: open plains, village groves, wires, scrub and perches that explain why a species is present at all.</p>
  </div>
</section>
<section class="portfolio-section gallery-panel">
  <div class="gallery-panel__head"><div><p class="kicker">Landscape notes</p><h2>Habitat plates</h2></div></div>
  <div id="cc-masonry" class="cc-masonry">{''.join(photo_card(p) for p in landscapes)}</div>
</section>
<div id="lgx" class="lgx" role="dialog" aria-modal="true" aria-hidden="true">
  <img class="lgx__img" alt="Expanded image preview">
  <div class="lgx__ui"><button class="lgx__btn lgx__close" type="button" aria-label="Close">&times;</button><button class="lgx__btn lgx__prev" type="button" aria-label="Previous">&lsaquo;</button><button class="lgx__btn lgx__next" type="button" aria-label="Next">&rsaquo;</button><div class="lgx__caption" aria-live="polite"></div><div class="lgx__bar"><button class="lgx__btn lgx__play" type="button" aria-label="Start slideshow">&#9654;</button><button class="lgx__btn lgx__pause" type="button" aria-label="Pause slideshow" style="display:none">&#10073;&#10073;</button></div></div>
</div>
'''
land = page(
    "Habitat Frames | Cane & Camera",
    "Habitat-focused photographs from Rajasthan that show the ecological setting behind wildlife behavior and natural history storytelling.",
    "landscapes.html",
    "gallery",
    land_body,
    extra_head='<script defer src="assets/js/gallery-lightbox.js"></script>',
    body_class="gallery-page",
)

video_objs = []
for d in docs:
    video_objs.append(
        {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": d["title"],
            "description": d["desc"],
            "thumbnailUrl": f"https://i.ytimg.com/vi/{d['id']}/hqdefault.jpg",
            "embedUrl": f"https://www.youtube.com/embed/{d['id']}",
            "uploadDate": d.get("uploadDate", "2025-01-01"),
        }
    )

docs_body = f'''
<section class="portfolio-section docs-intro">
  <p class="kicker">Films</p>
  <h1>Natural history in motion.</h1>
  <p>Short field documentaries and conservation films from grasslands, wetlands, desert edges and Mukundara-linked landscapes.</p>
</section>
<section class="docu-grid">{''.join(doc_card(d, full=True) for d in docs)}</section>
<section class="portfolio-section cta-band">
  <p class="kicker">Field support</p>
  <h2>Need a naturalist's eye on a film?</h2>
  <p>I can support story scouting, local ecological context, field logistics and low-disturbance cinematography for conservation and natural history productions.</p>
  <p><a class="btn" href="contact.html">Discuss a film collaboration</a></p>
</section>
'''

docsp = page(
    "Wildlife Documentaries & Conservation Films | Cane & Camera",
    "Watch conservation-focused wildlife films by Cane & Camera, including grassland, wetland, desert-edge, and Mukundara natural history stories.",
    "documentaries.html",
    "docs",
    docs_body,
    extra_jsonld=video_objs,
    body_class="docs-page",
)

about_body = '''
<section class="portfolio-section about-page">
  <p class="kicker">About the naturalist</p>
  <h1>Vinay Chittora works where field craft, filmmaking and conservation meet.</h1>
  <p class="about-intro">Cane &amp; Camera is my field practice: patient wildlife photography, natural history filmmaking, story scouting and biodiversity-first conservation communication from Rajasthan, with a deep connection to Mukundara Hills Tiger Reserve and surrounding habitats.</p>
</section>
<section class="about-grid">
  <article class="about-section"><span>01</span><h2>Field orientation</h2><p>I begin with habitat. Grasslands, wetlands, scrub, groves, rocky cover, water edges and altered village landscapes all carry clues before a subject appears.</p></article>
  <article class="about-section"><span>02</span><h2>Conservation position</h2><p>Conservation cannot stop at a single charismatic species. Native plants, insects, reptiles, birds, mammals, water, soil and seasonal movement all belong in the same conversation.</p></article>
  <article class="about-section"><span>03</span><h2>Ethics in practice</h2><p>No baiting, call playback, handling or forced proximity. I prefer the slower image that keeps the animal's choice intact.</p></article>
  <article class="about-section"><span>04</span><h2>Mukundara context</h2><p>My long-term field interest includes movement routes, habitat change, wetland edges, grassland revival and species interactions across Mukundara-linked landscapes. Ongoing notes live at <a href="https://mhtr.in" target="_blank" rel="noopener">mhtr.in</a>.</p></article>
</section>
<section class="portfolio-section cta-band">
  <p class="kicker">Useful for</p>
  <h2>Editorial teams, NGOs, educators, filmmakers and mission-led brands.</h2>
  <p>The work is most useful when a project needs grounded natural history storytelling, field scouting, ecological interpretation or ethical wildlife cinematography support.</p>
  <p><a class="btn" href="contact.html">See collaboration options</a></p>
</section>
'''
about = page(
    "About Vinay Chittora | Naturalist & Wildlife Filmmaker | Cane & Camera",
    "Learn about Vinay Chittora's field-based natural history practice in Mukundara Hills and Rajasthan, and his biodiversity-first conservation storytelling approach.",
    "about.html",
    "about",
    about_body,
    body_class="about-page-body",
)

contact_body = '''
<section class="portfolio-section work-page">
  <p class="kicker">Collaborate</p>
  <h1>Bring a naturalist into the project early.</h1>
  <p class="about-intro">For wildlife filmmaking, cinematography support, field scouting, story research, natural history documentation and conservation communication in Rajasthan and Mukundara-linked landscapes.</p>
</section>
<section class="collab-grid">
  <article><h2>Film and field production</h2><p>Wildlife documentary support, second-camera natural history work, location reading, behavior-aware shot planning and low-disturbance execution.</p></article>
  <article><h2>Scouting and story research</h2><p>Field context for grasslands, wetlands, scrub, village edges, seasonal movement and overlooked biodiversity around Rajasthan and Mukundara.</p></article>
  <article><h2>Conservation communication</h2><p>Campaign visuals, field explainers, editorial licensing, education assets and grounded narratives for habitat protection or restoration work.</p></article>
</section>
<section class="portfolio-section inquiry-panel">
  <div>
    <p class="kicker">Good brief ingredients</p>
    <h2>Send the goal, place, season and intended use.</h2>
    <p>Helpful details: project format, locations, timeline, expected field days, deliverables, usage scope, team size and any sensitive species or site permissions involved.</p>
  </div>
  <div class="contact-panel">
    <h2>Contact</h2>
    <p><b>Email:</b> <a href="mailto:hello@caneandcamera.com">hello@caneandcamera.com</a></p>
    <p><b>Instagram:</b> <a href="https://instagram.com/caneandcamera" target="_blank" rel="noopener">instagram.com/caneandcamera</a></p>
    <p><b>YouTube:</b> <a href="https://www.youtube.com/@CaneAndCamera/videos" target="_blank" rel="noopener">youtube.com/@CaneAndCamera</a></p>
    <p><b>MHTR notes:</b> <a href="https://mhtr.in" target="_blank" rel="noopener">mhtr.in</a></p>
    <p><a class="btn" href="mailto:hello@caneandcamera.com?subject=Collaboration%20Inquiry%20-%20Cane%20and%20Camera">Email project details</a></p>
  </div>
</section>
'''
contact = page(
    "Collaborate With Cane & Camera | Wildlife Film, Field Scouting, Conservation Storytelling",
    "Contact Cane & Camera for wildlife filmmaking, field scouting, ecological story research, and conservation communication collaborations in Rajasthan and Mukundara landscapes.",
    "contact.html",
    "contact",
    contact_body,
    body_class="contact-page-body",
)

pages = {
    "index.html": home,
    "gallery.html": gallery,
    "landscapes.html": land,
    "documentaries.html": docsp,
    "about.html": about,
    "contact.html": contact,
}

for filename, content in pages.items():
    (ROOT / filename).write_text(content)

# Pretty-route mirrors for static hosts that support directory indexes.
mirrors = {
    "about/index.html": about,
    "gallery/index.html": gallery,
    "landscapes/index.html": land,
    "documentaries/index.html": docsp,
    "contact/index.html": contact,
    "work-with-me/index.html": contact,
}
for rel, content in mirrors.items():
    out = content.replace("<head>", '<head>\n  <base href="../">', 1)
    (ROOT / rel).write_text(out)

robots = "User-agent: *\nAllow: /\n\nSitemap: https://www.caneandcamera.com/sitemap.xml\n"
(ROOT / "robots.txt").write_text(robots)

urls = [
    "https://www.caneandcamera.com/index.html",
    "https://www.caneandcamera.com/gallery.html",
    "https://www.caneandcamera.com/landscapes.html",
    "https://www.caneandcamera.com/documentaries.html",
    "https://www.caneandcamera.com/about.html",
    "https://www.caneandcamera.com/contact.html",
    "https://www.caneandcamera.com/gallery/",
    "https://www.caneandcamera.com/landscapes/",
    "https://www.caneandcamera.com/documentaries/",
    "https://www.caneandcamera.com/about/",
    "https://www.caneandcamera.com/contact/",
    "https://www.caneandcamera.com/work-with-me/",
]
lastmod = datetime.now(timezone.utc).date().isoformat()
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    xml.append(f"  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod></url>")
xml.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n")
