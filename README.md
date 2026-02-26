# Cane & Camera — Static Website

A clean, fast, SEO-friendly static website for Cane & Camera.

## Run locally

```bash
./run.sh
```

Then open `http://localhost:8000`.

## Site structure

- Core pages are static HTML (`index.html`, `about.html`, `gallery.html`, `documentaries.html`, `landscapes.html`, `contact.html`).
- Pretty URL directories (`about/`, `gallery/`, `documentaries/`, etc.) mirror the same page output for route compatibility.
- Shared design system lives in:
  - `assets/css/style.css` (global layout, spacing, header/footer, buttons)
  - `assets/css/docs.css` (documentaries grid/cards)

## Maintenance notes

- Header and footer markup are kept consistent across all page variants.
- SEO metadata (title, description, canonical, OpenGraph, Twitter) is set per page with consistent defaults.
- `robots.txt` and `sitemap.xml` are versioned in repo and should be updated when new public pages are added.
