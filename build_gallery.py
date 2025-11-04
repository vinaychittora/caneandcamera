#!/usr/bin/env python3
"""
Build responsive JPEG variants + JSON for a single gallery.

Usage:
  python build_gallery.py wildlife
  python build_gallery.py landscapes

Folders:
  Originals: assets/img/gallery/originals/<gallery>/
  Output   : assets/img/gallery/generated/<gallery>/...
  Manifest : assets/img/gallery/generated/photos.json

Notes:
  - No upscaling. Long-side targets are tried (2048, 1024, 512), but capped at original long side.
  - EXIF pulled via Pillow numeric tags (aperture, shutter, ISO, focal, camera, lens, datetime).
  - photos.json is merged: we drop previous entries for this <gallery> and append fresh ones, then sort.
"""

from __future__ import annotations
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image, ImageOps

# ---- Config (don’t change the placeholders in PATHS unless you move folders) ----
ROOT = Path(".")
ORIG_BASE = ROOT / "assets/img/gallery/originals"
GEN_BASE  = ROOT / "assets/img/gallery/generated"
JSON_OUT  = GEN_BASE / "photos.json"

WANTED_LONG_SIDES = [2048, 1024, 512]   # tried in this order, but we never upscale
JPEG_QUALITY = 82
JPEG_OPTIMIZE = True
JPEG_PROGRESSIVE = True

# EXIF tag IDs
EXIF = {
    "Make": 271, "Model": 272, "DateTime": 306,
    "ExposureTime": 33434, "FNumber": 33437, "ISOSpeedRatings": 34855,
    "DateTimeOriginal": 36867, "DateTimeDigitized": 36868,
    "FocalLength": 37386, "LensModel": 42036,
}

def slugify(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_-]+", "-", name)
    return re.sub(r"^-+|-+$", "", name)

def _rat_to_float(v) -> Optional[float]:
    try:
        if hasattr(v, "numerator") and hasattr(v, "denominator"):
            return float(v.numerator) / float(v.denominator) if v.denominator else float(v.numerator)
        if isinstance(v, tuple) and len(v) == 2 and v[1] != 0:
            return float(v[0]) / float(v[1])
        return float(v)
    except Exception:
        return None

def fmt_exposure(v) -> str:
    x = _rat_to_float(v)
    if not x: return ""
    if x < 1: return f"1/{round(1/x)}s"
    return f"{int(round(x))}s" if abs(x - round(x)) < 1e-6 else f"{x:.2f}s"

def fmt_fnumber(v) -> str:
    x = _rat_to_float(v)
    return f"f/{x:.1f}" if x else ""

def fmt_focal(v) -> str:
    x = _rat_to_float(v)
    return f"{int(round(x))}mm" if x else ""

def norm_dt(dt) -> str:
    if not dt: return ""
    if isinstance(dt, bytes):
        try: dt = dt.decode("utf-8", "ignore")
        except Exception: dt = str(dt)
    s = str(dt).strip()
    if len(s) >= 10 and ":" in s[:10]:
        try:
            y, m, d = s[:10].split(":")
            return f"{y}-{m}-{d}{s[10:]}"
        except Exception:
            return s
    return s

def extract_exif(im: Image.Image) -> Dict[str, str]:
    ex = im.getexif() or {}
    g  = lambda k: ex.get(EXIF[k])

    make, model, lens = g("Make"), g("Model"), g("LensModel")
    if isinstance(make,  bytes): make  = make.decode("utf-8", "ignore")
    if isinstance(model, bytes): model = model.decode("utf-8", "ignore")
    if isinstance(lens,  bytes): lens  = lens.decode("utf-8", "ignore")

    camera = " ".join([s for s in [str(make or "").strip(), str(model or "").strip()] if s]).strip()

    exp  = fmt_exposure(g("ExposureTime"))
    fnum = fmt_fnumber(g("FNumber"))
    iso_raw = ex.get(EXIF["ISOSpeedRatings"])
    try:
        if isinstance(iso_raw, (list, tuple)): iso_raw = iso_raw[0]
        iso = int(iso_raw) if iso_raw is not None else None
    except Exception:
        iso = None
    focal = fmt_focal(ex.get(EXIF["FocalLength"]))

    dt = g("DateTimeOriginal") or g("DateTimeDigitized") or g("DateTime")
    dt = norm_dt(dt)

    parts = []
    if exp: parts.append(exp)
    if fnum: parts.append(fnum)
    if iso: parts.append(f"ISO {iso}")
    if focal: parts.append(focal)
    pretty = " · ".join(parts)

    return {
        "camera": camera or "",
        "lens": lens or "",
        "exif_str": pretty or "",
        "datetime": dt or ""
    }

def resize_to_long_side(im: Image.Image, target_long: int) -> Image.Image:
    w, h = im.size
    ls = max(w, h)
    if ls <= target_long:             # no upscaling
        return im.copy()
    scale = target_long / ls
    nw, nh = max(1, int(round(w*scale))), max(1, int(round(h*scale)))
    return im.resize((nw, nh), Image.LANCZOS)

def load_existing_manifest() -> list[dict]:
    if JSON_OUT.exists():
        try:
            return json.loads(JSON_OUT.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_manifest(entries: list[dict]):
    # newest first by datetime
    entries.sort(key=lambda x: x.get("datetime",""), reverse=True)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"wildlife","landscapes"}:
        print("Usage: python build_gallery.py [wildlife|landscapes]")
        sys.exit(1)

    gallery_key = sys.argv[1]  # "wildlife" or "landscapes"
    orig_dir = ORIG_BASE / gallery_key
    out_dir  = GEN_BASE / gallery_key
    out_dir.mkdir(parents=True, exist_ok=True)

    if not orig_dir.exists():
        print(f"✖ Originals folder not found: {orig_dir}")
        sys.exit(1)

    # Build fresh entries for this gallery
    new_entries: list[dict] = []
    exts = {".jpg",".jpeg",".png",".tif",".tiff"}
    files = sorted([p for p in orig_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts])

    for p in files:
        slug = slugify(p.stem)
        try:
            with Image.open(p) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                meta = extract_exif(im)

                w, h = im.size
                orig_long = max(w, h)

                # long-sides we’ll emit (no upscaling) + include actual original long side
                desired = sorted({min(t, orig_long) for t in WANTED_LONG_SIDES if t > 0}, reverse=True)
                if orig_long not in desired:
                    desired.insert(0, orig_long)

                # unique sizes
                sizes = []
                seen = set()
                for s in desired:
                    if s not in seen:
                        seen.add(s)
                        sizes.append(s)

                variants: Dict[str, Dict[str, Any]] = {}
                for target in sizes:
                    out_img = resize_to_long_side(im, target)
                    produced_long = max(out_img.size)
                    out_name = f"{slug}-{produced_long}.jpg"
                    out_path = out_dir / out_name
                    out_img.save(
                        out_path, "JPEG",
                        quality=JPEG_QUALITY, optimize=JPEG_OPTIMIZE, progressive=JPEG_PROGRESSIVE
                    )
                    # JSON src must be relative to page root
                    rel_src = (out_path.as_posix())
                    variants[str(produced_long)] = {
                        "src": rel_src,
                        "w": out_img.width,
                        "h": out_img.height
                    }

                # fallback datetime
                dt = meta["datetime"] or time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))

                new_entries.append({
                    "slug": slug,
                    "title": "",
                    "description": "",
                    "gallery": gallery_key,              # ← set from CLI
                    "camera": meta["camera"],
                    "lens": meta["lens"],
                    "exif": meta["exif_str"],
                    "datetime": dt,
                    "original": {"file": str(p.as_posix()), "w": w, "h": h},
                    "variants": variants
                })

        except Exception as e:
            print(f"[WARN] {p.name}: {e}")

    # Merge with existing manifest: drop old entries for this gallery, keep others
    manifest = load_existing_manifest()
    manifest = [e for e in manifest if (e.get("gallery") != gallery_key)]
    manifest.extend(new_entries)
    save_manifest(manifest)

    print(f"✅ Built {len(new_entries)} items for '{gallery_key}'")
    print(f"→ Variants in: {out_dir}")
    print(f"→ Manifest   : {JSON_OUT}")

if __name__ == "__main__":
    main()
