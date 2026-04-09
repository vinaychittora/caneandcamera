#!/usr/bin/env python3
"""Generate responsive JPEG variants and update gallery manifest.

Usage:
  python3 scripts/generate_responsive_images.py

Requires Pillow (`pip install pillow`).
"""
import json
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

SIZES = [512, 1024, 1350, 2048]
QUALITY = 84


def normalize_title(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title()


def process_image(src: Path, gallery: str):
    slug = src.stem.lower().strip().replace(" ", "-")
    title = normalize_title(slug)

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
            out = out_dir / f"{slug}-{width}.jpg"
            resized = rgb.resize((width, h), Image.Resampling.LANCZOS)
            resized.save(out, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
            variants[str(width)] = {
                "src": str(out.relative_to(ROOT)).replace("\\", "/"),
                "w": width,
                "h": h,
            }

        maxw = max(int(k) for k in variants)
        full = variants[str(maxw)]

        return {
            "slug": slug,
            "title": title,
            "description": "",
            "gallery": gallery,
            "camera": "",
            "lens": "",
            "exif": "",
            "datetime": "",
            "original": {
                "file": str(src.relative_to(ROOT)).replace("\\", "/"),
                "w": ow,
                "h": oh,
            },
            "variants": variants,
            "exposure": "",
            "aperture": "",
            "iso": "",
            "focal": "",
            "default": full,
        }


def main():
    items = []
    for gallery_dir in sorted(ORIGINALS.iterdir()):
        if not gallery_dir.is_dir():
            continue
        gallery = gallery_dir.name
        for src in sorted(gallery_dir.iterdir()):
            if src.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            items.append(process_image(src, gallery))

    MANIFEST.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(items)} entries to {MANIFEST}")


if __name__ == "__main__":
    main()
