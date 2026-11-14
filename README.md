# Cane & Camera

The website of Vinay Chittora, a field naturalist in Kota, Rajasthan: <https://www.caneandcamera.com>

The home page is a side-scrolling walk through Vinay's life, and `/work` lists the work. It is a static site with no dependencies. Pushing to `main` deploys it.

## What is where

- `walk/walk.page.html` is the home page, `walk/work.page.html` is the work page, and `walk/404.page.html` is the page shown for an address that does not exist. Each file holds one page's styles, markup and script without the document shell, and addresses its pictures as `img/...`.
- `scripts/build_walk.py` adds the shell and the metadata, points the pictures at `/assets/img/walk/` and the links at `/` and `/work`, and writes `index.html`, `work.html` and `404.html`. It also writes `_redirects`, `sitemap.xml` and `robots.txt`.
- `assets/img/walk/` holds the large copies of the photographs that fill the sky, the logo and the UPI code. `assets/img/walk/t/` holds 800 px copies for the prints, the contact sheet and the work page.
- `_headers` is written by hand.

Edit the files in `walk/`, never `index.html`, `work.html` or `404.html`: the build overwrites those.

## Build and preview

```bash
python3 scripts/build_walk.py
```

```bash
./run.sh
```

Then open `http://localhost:8000`. The local server does not read `_redirects`, and it shows `404.html` only at `/404.html`.

## Checking the walk

- Add `?at=` with a number from 0 to 1 to pin the walk at one moment, for example `/?at=0.44`.
- Add `&t=` to that with a number of steps to see him walk on after the end, for example `/?at=1&t=200`.
- Add `&upi=1` to open the UPI card in the ending.

The walk moves by scrolling the page. Arrow keys, the two arrow buttons, Play, and a tap or a hold on either side of the picture all scroll it.

## Adding a photograph

1. Save a large copy (about 2400 px wide) in `assets/img/walk/` if it will fill the sky, and an 800 px copy in `assets/img/walk/t/`.
2. Add it to `walk/walk.page.html` or `walk/work.page.html`.
3. Run the build.

Keep the watermark on every photograph, and never publish a photograph of a nest.

## Old addresses

The site this one replaced had `/gallery`, `/landscapes`, `/documentaries`, `/about` and `/contact`. `_redirects` sends each of them to the walk or to the matching part of `/work`. Anything else that no longer exists gets `404.html`.

That site, with its pages, pictures and build scripts, is kept in git under the tag `old-site`. To bring something back:

```bash
git checkout old-site -- assets/img/gallery
```
