# Cane & Camera — Static Website

A lightweight static site for **Cane & Camera** focused on natural history storytelling, wildlife films, and field-based conservation communication.

## Local preview

```bash
./run.sh
```

Open: `http://localhost:8000`

## Build workflow

Pages are generated from shared templates and JSON data to keep navigation, SEO metadata, and repeated content maintainable.

```bash
python3 scripts/build_site.py
```

This command regenerates:

- `index.html`
- `gallery.html`
- `landscapes.html`
- `documentaries.html`
- `about.html`
- `contact.html`
- Pretty-route mirrors under `about/`, `gallery/`, `landscapes/`, `documentaries/`, `contact/`, and `work-with-me/`
- `sitemap.xml` and `robots.txt`

## Content/data sources

- Gallery manifest: `assets/img/gallery/generated/photos.json`
- Documentary metadata: `data/documentaries.json`

## Responsive image pipeline

Gallery pages consume responsive variants (`srcset` / `sizes`) from the manifest.

To generate variants from originals (optional, requires Pillow):

```bash
python3 scripts/generate_responsive_images.py
```

Source originals should live in:

- `assets/img/gallery/originals/wildlife/`
- `assets/img/gallery/originals/landscapes/`

The script writes optimized variants and updates `assets/img/gallery/generated/photos.json`.
