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

- `index.html` and `work.html` (see "The walk" below)
- `gallery.html`
- `landscapes.html`
- `documentaries.html`
- `about.html`
- `contact.html`
- Pretty-route mirrors under `about/`, `gallery/`, `landscapes/`, `documentaries/`, and `contact/`
- Minified CSS and JavaScript assets used by the generated pages
- `sitemap.xml`, `robots.txt`, and Netlify-style `_redirects`

The generated canonical URLs, internal links, and sitemap use clean public routes such as `/gallery` and `/about`. The `.html` files remain build artifacts for static hosting and are redirected away from on deploy.

## The walk

The home page is a side-scrolling walk through Vinay's life, and `/work` lists the work. Both are written by hand, not from the templates:

- `walk/walk.page.html` is the home page and `walk/work.page.html` is the work page. Each file holds one page's styles, markup and script without the document shell, and addresses its pictures as `img/...`.
- `scripts/build_walk.py` adds the shell and the metadata, points the pictures at `/assets/img/walk/` and the links at `/` and `/work`, and writes `index.html` and `work.html`. `scripts/build_site.py` runs it at the end, and it can be run on its own:

```bash
python3 scripts/build_walk.py
```

- The pictures live in `assets/img/walk/` (large copies for the photographs that fill the sky) and `assets/img/walk/t/` (800 px copies for the prints and the contact sheet).
- To check one moment of the walk, add `?at=` with a number from 0 to 1 to the address, for example `/?at=0.44`.

The older pages (`/gallery`, `/landscapes`, `/documentaries`, `/about`, `/contact`) are still built and served, but the walk does not link to them.

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
