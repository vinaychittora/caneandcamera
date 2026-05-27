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
- Pretty-route mirrors under `about/`, `gallery/`, `landscapes/`, `documentaries/`, and `contact/`
- Minified CSS and JavaScript assets used by the generated pages
- `sitemap.xml`, `robots.txt`, and Netlify-style `_redirects`

The generated canonical URLs, internal links, and sitemap use clean public routes such as `/gallery` and `/about`. The `.html` files remain build artifacts for static hosting and are redirected away from on deploy.

## Content/data sources

- Gallery manifest: `assets/img/gallery/generated/photos.json`
- Documentary metadata: `data/documentaries.json`
- Portfolio taxonomy and page copy: `scripts/build_site.py`

The gallery is now presented as a **Field Index**. Photos are grouped client-side by field-study tags such as raptors, grasslands, wetlands, forest edge, and small lives. Those tags and narrative notes live in `scripts/build_site.py`, so the site stays static while still feeling curated.

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

## How to add a new photo

1. Copy the original high-resolution file into one of these folders:
   - `assets/img/gallery/originals/wildlife/`
   - `assets/img/gallery/originals/landscapes/`
2. Use a clear filename slug (example: `desert-fox-family.jpg`).
3. Run:

```bash
python3 scripts/generate_responsive_images.py
```

4. This generates responsive variants at widths `512`, `1024`, `1350`, and `2048` (when source size allows) and rewrites:
   - `assets/img/gallery/generated/photos.json`
5. Open `assets/img/gallery/generated/photos.json` and fill/edit metadata for the new entry:
   - `title`
   - `description`
   - `datetime`
   - `camera` (if available)
6. Rebuild the site pages:

```bash
python3 scripts/build_site.py
```

The responsive image generator preserves existing manifest metadata for matching slugs, so rerunning it should not wipe the titles, descriptions, camera info, or custom fields you already edited.

### Concrete example

If you add:

- `assets/img/gallery/originals/wildlife/desert-fox-family.jpg`

the generator will create files like:

- `assets/img/gallery/generated/wildlife/desert-fox-family-512.jpg`
- `assets/img/gallery/generated/wildlife/desert-fox-family-1024.jpg`
- `assets/img/gallery/generated/wildlife/desert-fox-family-1350.jpg`
- `assets/img/gallery/generated/wildlife/desert-fox-family-2048.jpg`

Then `scripts/build_site.py` will automatically include the photo in gallery pages with:

- responsive thumbnails via `srcset`/`sizes`
- lazy loading in gallery lists
- larger image opened in the lightbox (`data-full`)
