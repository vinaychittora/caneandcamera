
# Cane & Camera — Static Photo Site

A clean, fast, SEO-friendly static site for fine-art photography, inspired by classic gallery sites.

## Features
- Landing grid → 4 galleries (Wildlife, Landscapes, Panoramas, Documentaries)
- Gallery pages load from `/data/photos.json`
- Individual photo pages with story, EXIF, location, and purchase buttons
- Responsive `<picture>` with AVIF/WebP/JPEG fallback
- Ready for **Razorpay Payment Links** or **Shopify Buy Button** (uncomment and configure)
- Deployed easily to **Cloudflare Pages** or **Netlify**

## Quick Start
1. Edit `data/photos.json` — add your photos. Keep `thumb_*` and `hero_*` paths to your images under `assets/img/`.
2. Replace placeholder cover images on `index.html` (wildlife-cover.jpg, etc. in `assets/img/`).
3. For purchases:
   - **Razorpay**: put your payment links in each photo's `buy.razorpay` (A4/A3/A2).
   - **Shopify Buy Button**: uncomment the embed in `photo.html` and fill domain, token, product ID.
4. Deploy:
   - **Cloudflare Pages**: create a new project from this folder, set build = None (static).
   - **Netlify**: drag & drop the folder, or connect a repo.

## SEO Tips
- Give each photo a unique `slug`, `title`, `alt`, and `story`. These become page content.
- Add Open Graph/Twitter meta if you want rich sharing (optional).
- Consider JSON-LD `Product` schema on `photo.html` via inline script using the photo's data.

## Image Prep
- Export 3 versions per image:
  - `*-thumb` around 1200px on the long side (for grid)
  - `*-hero` 2000–2800px on the long side (for detail page)
  - Provide AVIF/WebP to save bandwidth (Cloudflare Images can auto-convert).

## Folder
```
caneandcamera-site/
  index.html
  gallery.html
  photo.html
  about.html
  contact.html
  assets/
    css/style.css
    js/main.js
    img/   # put your images here
  data/photos.json
```

## License
Do whatever you want with it. Attribution appreciated but not required.
