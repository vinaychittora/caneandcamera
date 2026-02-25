# Cane & Camera — Static Photo Site

A clean, fast, SEO-friendly static site for fine-art photography.

## Templated build workflow

The repository now uses a small Python build step to generate static HTML pages from shared templates and JSON content:

- `build_site.py` renders:
  - `index.html`
  - `gallery.html` (wildlife)
  - `documentaries.html`
- Gallery images are rendered directly in HTML (SEO-friendly) with native lazy loading.
- Documentary cards are rendered from `data/documentaries.json` into static HTML.

## Commands

```bash
python3 build_site.py
./run.sh
```

## How to verify the changes locally

1. Generate pages from templates:
   ```bash
   python3 build_site.py
   ```
2. Start the local server:
   ```bash
   ./run.sh
   ```
3. Open the generated pages in your browser:
   - `http://localhost:8000/gallery.html`
   - `http://localhost:8000/documentaries.html`

### Quick checks

- Confirm gallery and documentary cards are present in page source (not inserted by JS).
- Confirm images include `loading="lazy"` attributes.
- Confirm lightbox behavior still works on gallery pages.
