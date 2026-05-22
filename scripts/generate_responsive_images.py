#!/usr/bin/env python3
"""Generate responsive JPEG variants and update gallery manifest.

Usage:
  python3 scripts/generate_responsive_images.py

Requires Pillow (`pip install pillow`).
"""
import json
import os
import re
from pathlib import Path

try:
    from PIL import Image
except Exception as exc:  # noqa: BLE001
    raise SystemExit(
        "Pillow is required for image generation. Install it with: pip install pillow"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "assets/img/gallery/originals"
GENERATED = ROOT / "assets/img/gallery/generated"
MANIFEST = GENERATED / "photos.json"

SIZES = [160, 320, 512, 768, 1024, 1350, 2048]
JPEG_QUALITY = 84
WEBP_QUALITY = 78


def normalize_title(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title()


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def photo_key(gallery: str, slug: str) -> str:
    return f"{gallery}/{slug}"


def process_image(src: Path, gallery: str, existing: dict):
    slug = slugify(src.stem)
    previous = existing.get(photo_key(gallery, slug), {})
    title = previous.get("title") or normalize_title(slug)

    with Image.open(src) as im:
        rgb = im.convert("RGB")
        ow, oh = rgb.size

        variants = {}
        for width in SIZES:
            if width > ow:
                continue
            h = int((oh / ow) * width)
            out_dir = GENERATED / gallery
            out_dir.mkdir(parents=True, exist_ok=True)
            jpg_out = out_dir / f"{slug}-{width}.jpg"
            webp_out = out_dir / f"{slug}-{width}.webp"
            resized = rgb.resize((width, h), Image.Resampling.LANCZOS)
            resized.save(jpg_out, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
            resized.save(webp_out, format="WEBP", quality=WEBP_QUALITY, method=6)
            variants[str(width)] = {
                "src": str(jpg_out.relative_to(ROOT)).replace("\\", "/"),
                "webp": str(webp_out.relative_to(ROOT)).replace("\\", "/"),
                "w": width,
                "h": h,
            }

        maxw = max(int(k) for k in variants)
        full = variants[str(maxw)]

        item = {
            "slug": slug,
            "title": title,
            "description": previous.get("description", ""),
            "gallery": gallery,
            "camera": previous.get("camera", ""),
            "lens": previous.get("lens", ""),
            "exif": previous.get("exif", ""),
            "datetime": previous.get("datetime", ""),
            "original": {
                "file": str(src.relative_to(ROOT)).replace("\\", "/"),
                "w": ow,
                "h": oh,
            },
            "variants": variants,
            "exposure": previous.get("exposure", ""),
            "aperture": previous.get("aperture", ""),
            "iso": previous.get("iso", ""),
            "focal": previous.get("focal", ""),
            "default": full,
        }
        for key, value in previous.items():
            if key not in item and key not in {"original", "variants", "default"}:
                item[key] = value
        return item


def main():
    existing_items = []
    base_manifest = Path(os.environ.get("PHOTO_MANIFEST_BASE", MANIFEST))
    if base_manifest.exists():
        existing_items = json.loads(base_manifest.read_text())
    existing = {photo_key(item["gallery"], item["slug"]): item for item in existing_items}

    processed = {}
    for gallery_dir in sorted(ORIGINALS.iterdir()):
        if not gallery_dir.is_dir():
            continue
        gallery = gallery_dir.name
        for src in sorted(gallery_dir.iterdir()):
            if src.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            item = process_image(src, gallery, existing)
            processed[photo_key(item["gallery"], item["slug"])] = item

    ordered_keys = [
        photo_key(item["gallery"], item["slug"])
        for item in existing_items
        if photo_key(item["gallery"], item["slug"]) in processed
    ]
    known_keys = set(ordered_keys)
    ordered_keys.extend(key for key in sorted(processed) if key not in known_keys)
    items = [processed[key] for key in ordered_keys]

    MANIFEST.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(items)} entries to {MANIFEST}")


if __name__ == "__main__":
    main()
