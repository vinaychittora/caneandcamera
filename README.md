# Cane & Camera — Static Website

A lightweight static website for Cane & Camera.

## Run locally

```bash
./run.sh
```

Open `http://localhost:8000`.

## Project structure

- Public pages:
  - Top-level routes: `index.html`, `gallery.html`, `documentaries.html`, `about.html`, `contact.html`, `landscapes.html`
  - Pretty-route mirrors: `about/`, `gallery/`, `documentaries/`, `contact/`, `landscapes/`, `work-with-me/`
- Styles:
  - `assets/css/style.css` (global layout, nav/footer, gallery, lightbox)
  - `assets/css/docs.css` (documentaries layout)
- Scripts:
  - `assets/js/main.js` (navigation + small UI behavior)
  - `assets/js/gallery-lightbox.js` (gallery overlay behavior)

## Cleanup notes

Legacy build artifacts/scripts are removed. The site is now maintained directly as static HTML/CSS/JS.

## Maintenance checklist

When editing pages, keep both top-level and pretty-route variants synchronized.
