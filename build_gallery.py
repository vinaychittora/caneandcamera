#!/usr/bin/env python3
"""
Build responsive JPEG variants + JSON for a single gallery
(append-only, change-aware, robust EXIF/XMP extraction).

Usage:
  python build_gallery.py wildlife
  python build_gallery.py landscapes

Options:
  --dry-run         Show what would change, do not write
  --force-refresh   Refresh technical fields even if new values are empty
  --json PATH       Custom manifest path (default: assets/img/gallery/generated/photos.json)
  --verbose         Print extractor used and EXIF summary per file

Behavior:
  - Appends only newly found photos.
  - For existing entries, updates technical fields only when changed:
      camera, lens, exposure, aperture, iso, focal, exif, datetime, original, variants
  - Never touches title/description.
  - EXIF/XMP extraction tries Pillow → piexif → exifread → XMP XML, with clear logs.
"""

from __future__ import annotations
import argparse, json, re, sys, time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from PIL import Image, ImageOps

# Optional deps (if installed, we’ll use them)
try:
    import piexif  # type: ignore
except Exception:
    piexif = None

try:
    import exifread  # type: ignore
except Exception:
    exifread = None

ROOT = Path(".")
ORIG_BASE = ROOT / "assets/img/gallery/originals"
GEN_BASE  = ROOT / "assets/img/gallery/generated"
JSON_OUT_DEFAULT = GEN_BASE / "photos.json"

WANTED_LONG_SIDES = [2048, 1024, 512]
JPEG_QUALITY = 82
JPEG_OPTIMIZE = True
JPEG_PROGRESSIVE = True

# Numeric EXIF IDs for Pillow
EXIF = {
    "Make": 271, "Model": 272, "DateTime": 306,
    "ExposureTime": 33434, "FNumber": 33437, "ISOSpeedRatings": 34855,
    "DateTimeOriginal": 36867, "DateTimeDigitized": 36868,
    "FocalLength": 37386, "LensModel": 42036,
}

# ---------- Formatting helpers ----------

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
        if isinstance(v, str) and "/" in v:
            a, b = v.split("/", 1)
            return float(a) / float(b) if float(b) else None
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
    # Convert 2024:11:03 08:21:33 -> 2024-11-03 08:21:33
    if len(s) >= 10 and ":" in s[:10]:
        try:
            y, m, d = s[:10].split(":")
            return f"{y}-{m}-{d}{s[10:]}"
        except Exception:
            return s
    return s

# ---------- Extractors ----------

def _coerce_bytes(v):
    if isinstance(v, bytes):
        try: return v.decode("utf-8", "ignore").strip()
        except Exception: return str(v)
    return v

def extract_with_pillow(image_path: Path) -> Tuple[Dict[str, Any], str]:
    with Image.open(image_path) as im:
        ex = im.getexif() or Image.Exif()
        g  = lambda name: ex.get(EXIF[name]) if name in EXIF else None

        make, model, lens = g("Make"), g("Model"), g("LensModel")
        make, model, lens = _coerce_bytes(make), _coerce_bytes(model), _coerce_bytes(lens)

        camera = " ".join([s for s in [str(make or "").strip(), str(model or "").strip()] if s]).strip()

        exposure  = fmt_exposure(g("ExposureTime"))
        aperture  = fmt_fnumber(g("FNumber"))
        iso_raw   = g("ISOSpeedRatings")
        try:
            if isinstance(iso_raw, (list, tuple)): iso_raw = iso_raw[0]
            iso = int(iso_raw) if iso_raw is not None and str(iso_raw).strip() != "" else None
        except Exception:
            iso = None
        focal     = fmt_focal(g("FocalLength"))

        dt = g("DateTimeOriginal") or g("DateTimeDigitized") or g("DateTime")
        dt = norm_dt(dt)

    parts = []
    if exposure: parts.append(exposure)
    if aperture: parts.append(aperture)
    if iso is not None: parts.append(f"ISO {iso}")
    if focal: parts.append(focal)

    return ({
        "camera": camera or "",
        "lens": lens or "",
        "exposure": exposure or "",
        "aperture": aperture or "",
        "iso": iso if iso is not None else "",
        "focal": focal or "",
        "exif_str": " · ".join(parts) if parts else "",
        "datetime": dt or ""
    }, "pillow")

def extract_with_piexif(image_path: Path) -> Tuple[Dict[str, Any], str]:
    data = piexif.load(str(image_path))
    zeroth = data.get("0th", {}) or {}
    exif   = data.get("Exif", {}) or {}
    makern = data.get("MakerNote", {}) or {}

    def gv(dct, key): 
        v = dct.get(key)
        if isinstance(v, bytes):
            try: v = v.decode("utf-8", "ignore")
            except Exception: v = str(v)
        return v

    make  = gv(zeroth, piexif.ImageIFD.Make if piexif else 271)
    model = gv(zeroth, piexif.ImageIFD.Model if piexif else 272)
    lens  = gv(exif, piexif.ExifIFD.LensModel if piexif else 42036)

    camera = " ".join([s for s in [str(make or "").strip(), str(model or "").strip()] if s]).strip()

    exposure  = gv(exif, piexif.ExifIFD.ExposureTime if piexif else 33434)
    aperture  = gv(exif, piexif.ExifIFD.FNumber if piexif else 33437)
    iso       = gv(exif, piexif.ExifIFD.ISOSpeedRatings if piexif else 34855)
    focal     = gv(exif, piexif.ExifIFD.FocalLength if piexif else 37386)

    exposure  = fmt_exposure(exposure)
    aperture  = fmt_fnumber(aperture)
    try:
        if isinstance(iso, (list, tuple)): iso = iso[0]
        iso = int(iso) if iso not in (None, "", {}) else None
    except Exception:
        iso = None
    focal     = fmt_focal(focal)

    dt = gv(exif, piexif.ExifIFD.DateTimeOriginal if piexif else 36867) or \
         gv(exif, piexif.ExifIFD.DateTimeDigitized if piexif else 36868) or \
         gv(zeroth, piexif.ImageIFD.DateTime if piexif else 306)
    dt = norm_dt(dt)

    parts = []
    if exposure: parts.append(exposure)
    if aperture: parts.append(aperture)
    if iso is not None: parts.append(f"ISO {iso}")
    if focal: parts.append(focal)

    return ({
        "camera": camera or "",
        "lens": lens or "",
        "exposure": exposure or "",
        "aperture": aperture or "",
        "iso": iso if iso is not None else "",
        "focal": focal or "",
        "exif_str": " · ".join(parts) if parts else "",
        "datetime": dt or ""
    }, "piexif")

def extract_with_exifread(image_path: Path) -> Tuple[Dict[str, Any], str]:
    with open(image_path, "rb") as f:
        tags = exifread.process_file(f, details=False, stop_tag="UNDEF")

    def g(*names):
        for n in names:
            if n in tags: 
                return tags[n]
        return None

    def gx(*names):
        v = g(*names)
        return str(v) if v is not None else None

    make  = gx("Image Make")
    model = gx("Image Model")
    lens  = gx("EXIF LensModel") or gx("Image LensModel") or gx("MakerNote LensModel") or ""

    camera = " ".join([s for s in [str(make or "").strip(), str(model or "").strip()] if s]).strip()

    exposure = gx("EXIF ExposureTime")
    aperture = gx("EXIF FNumber")
    iso      = gx("EXIF ISOSpeedRatings") or gx("EXIF PhotographicSensitivity")
    focal    = gx("EXIF FocalLength")
    dt       = gx("EXIF DateTimeOriginal") or gx("EXIF DateTimeDigitized") or gx("Image DateTime")

    exposure = fmt_exposure(exposure)
    aperture = fmt_fnumber(aperture)
    try:
        iso = int(str(iso)) if iso not in (None, "", {}) else None
    except Exception:
        iso = None
    focal = fmt_focal(focal)
    dt    = norm_dt(dt)

    parts = []
    if exposure: parts.append(exposure)
    if aperture: parts.append(aperture)
    if iso is not None: parts.append(f"ISO {iso}")
    if focal: parts.append(focal)

    return ({
        "camera": camera or "",
        "lens": lens or "",
        "exposure": exposure or "",
        "aperture": aperture or "",
        "iso": iso if iso is not None else "",
        "focal": focal or "",
        "exif_str": " · ".join(parts) if parts else "",
        "datetime": dt or ""
    }, "exifread")

# Minimal, fast XMP packet scrape (works even in many PNG/TIFF exports)
_XMP_RE = re.compile(rb"<x:xmpmeta.*?</x:xmpmeta>", re.DOTALL)
def extract_with_xmp(image_path: Path) -> Tuple[Dict[str, Any], str]:
    data = image_path.read_bytes()
    m = _XMP_RE.search(data)
    if not m:
        return ({ "camera":"", "lens":"", "exposure":"", "aperture":"", "iso":"", "focal":"", "exif_str":"", "datetime":"" }, "xmp:none")

    xmp = m.group(0).decode("utf-8", "ignore")

    def x(tag, ns="exif"):
        # very tolerant regex lookups, namespaced attributes
        pat = rf"{ns}:{tag}=['\"]([^'^\"]+)['\"]"
        m2 = re.search(pat, xmp)
        if m2: return m2.group(1)
        # also check element form <exif:Tag>value</exif:Tag>
        pat2 = rf"<{ns}:{tag}[^>]*>(.*?)</{ns}:{tag}>"
        m3 = re.search(pat2, xmp, re.DOTALL)
        return m3.group(1).strip() if m3 else ""

    # These are common XMP tags; vendors vary wildly:
    make   = x("Make", "tiff")
    model  = x("Model", "tiff")
    lens   = x("Lens") or x("LensModel","aux") or x("LensModel","exif") or ""
    camera = " ".join([s for s in [make.strip(), model.strip()] if s]).strip()

    exposure = x("ExposureTime") or x("Exposure", "aux")
    aperture = x("FNumber") or x("ApertureValue")
    iso      = x("ISOSpeedRatings") or x("PhotographicSensitivity")
    focal    = x("FocalLength")
    dt       = x("DateTimeOriginal") or x("CreateDate") or x("ModifyDate")

    exposure = fmt_exposure(exposure)
    aperture = fmt_fnumber(aperture)
    try:
        iso = int(iso) if iso not in (None, "", {}) else None
    except Exception:
        iso = None
    focal    = fmt_focal(focal)
    dt       = norm_dt(dt)

    parts = []
    if exposure: parts.append(exposure)
    if aperture: parts.append(aperture)
    if iso is not None: parts.append(f"ISO {iso}")
    if focal: parts.append(focal)

    return ({
        "camera": camera or "",
        "lens": lens or "",
        "exposure": exposure or "",
        "aperture": aperture or "",
        "iso": iso if iso is not None else "",
        "focal": focal or "",
        "exif_str": " · ".join(parts) if parts else "",
        "datetime": dt or ""
    }, "xmp")

def extract_metadata(image_path: Path, verbose=False) -> Dict[str, Any]:
    # Try Pillow
    try:
        meta, src = extract_with_pillow(image_path)
        if any([meta["camera"], meta["exposure"], meta["aperture"], meta["iso"], meta["focal"], meta["datetime"]]):
            if verbose: print(f"[EXIF] {image_path.name}: using {src}")
            return meta
        elif verbose:
            print(f"[EXIF] {image_path.name}: Pillow empty")
    except Exception as e:
        if verbose: print(f"[EXIF] {image_path.name}: Pillow failed → {e}")

    # Try piexif
    if piexif is not None:
        try:
            meta, src = extract_with_piexif(image_path)
            if any([meta["camera"], meta["exposure"], meta["aperture"], meta["iso"], meta["focal"], meta["datetime"]]):
                if verbose: print(f"[EXIF] {image_path.name}: using {src}")
                return meta
            elif verbose:
                print(f"[EXIF] {image_path.name}: piexif empty")
        except Exception as e:
            if verbose: print(f"[EXIF] {image_path.name}: piexif failed → {e}")

    # Try exifread
    if exifread is not None:
        try:
            meta, src = extract_with_exifread(image_path)
            if any([meta["camera"], meta["exposure"], meta["aperture"], meta["iso"], meta["focal"], meta["datetime"]]):
                if verbose: print(f"[EXIF] {image_path.name}: using {src}")
                return meta
            elif verbose:
                print(f"[EXIF] {image_path.name}: exifread empty")
        except Exception as e:
            if verbose: print(f"[EXIF] {image_path.name}: exifread failed → {e}")

    # Try XMP
    try:
        meta, src = extract_with_xmp(image_path)
        if any([meta["camera"], meta["exposure"], meta["aperture"], meta["iso"], meta["focal"], meta["datetime"]]):
            if verbose: print(f"[EXIF] {image_path.name}: using {src}")
            return meta
        elif verbose:
            print(f"[EXIF] {image_path.name}: no EXIF/XMP found")
    except Exception as e:
        if verbose: print(f"[EXIF] {image_path.name}: XMP failed → {e}")

    # Final fallback
    if verbose:
        print(f"[EXIF] {image_path.name}: giving up; will use file mtime as datetime")

    return {
        "camera": "", "lens": "", "exposure": "", "aperture": "", "iso": "", "focal": "",
        "exif_str": "", "datetime": ""
    }

# ---------- Manifest helpers ----------

def load_manifest(path: Path) -> list[dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def backup_manifest(path: Path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        bak.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

def save_manifest(path: Path, entries: list[dict]):
    entries.sort(key=lambda x: x.get("datetime",""), reverse=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_manifest(path)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

def key_of(item: dict) -> Tuple[str, str]:
    return (item.get("slug",""), item.get("gallery",""))

def index_by_key(items: list[dict]) -> dict[Tuple[str, str], int]:
    return { key_of(it): i for i, it in enumerate(items) }

def shallow_equal(a: Any, b: Any) -> bool:
    return a == b

# ---------- Builder ----------

def build_entry_for_file(p: Path, gallery_key: str, out_dir: Path, verbose=False) -> dict:
    slug = slugify(p.stem)

    # Extract metadata (from file bytes, independent of convert)
    meta = extract_metadata(p, verbose=verbose)

    # Open once for pixel pipeline (orientation + RGB)
    with Image.open(p) as im:
        im_proc = ImageOps.exif_transpose(im)
        im_proc = im_proc.convert("RGB")
        w, h = im_proc.size
        orig_long = max(w, h)

        desired = sorted({min(t, orig_long) for t in WANTED_LONG_SIDES if t > 0}, reverse=True)
        if orig_long not in desired:
            desired.insert(0, orig_long)

        sizes, seen = [], set()
        for s in desired:
            if s not in seen:
                seen.add(s)
                sizes.append(s)

        variants: Dict[str, Dict[str, Any]] = {}
        for target in sizes:
            out_img = im_proc if max(im_proc.size) <= target else im_proc.resize(
                (max(1, int(round(im_proc.width  * (target/max(im_proc.size))))),
                 max(1, int(round(im_proc.height * (target/max(im_proc.size)))))), Image.LANCZOS)

            produced_long = max(out_img.size)
            out_name = f"{slug}-{produced_long}.jpg"
            out_path = out_dir / out_name
            out_img.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=JPEG_OPTIMIZE, progressive=JPEG_PROGRESSIVE)
            variants[str(produced_long)] = {"src": out_path.as_posix(), "w": out_img.width, "h": out_img.height}

    dt = meta["datetime"] or time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))

    return {
        "slug": slug,
        "title": "",
        "description": "",
        "gallery": gallery_key,
        "camera": meta["camera"],
        "lens": meta["lens"],
        "exposure": meta["exposure"],
        "aperture": meta["aperture"],
        "iso": meta["iso"],
        "focal": meta["focal"],
        "exif": meta["exif_str"],
        "datetime": dt,
        "original": {"file": p.as_posix(), "w": w, "h": h},
        "variants": variants
    }

def update_existing_technical_fields(existing: dict, built: dict, prefer_existing_non_empty: bool) -> Tuple[bool, dict]:
    changed = False
    technical_fields = ("camera","lens","exposure","aperture","iso","focal","exif","datetime","original","variants")
    for f in technical_fields:
        new_val = built.get(f)
        old_val = existing.get(f)
        if prefer_existing_non_empty and (old_val not in (None, "", {}) and new_val in (None, "", {})):
            continue
        if not shallow_equal(old_val, new_val):
            existing[f] = new_val
            changed = True
    return changed, existing

# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(description="Append-only, change-aware gallery builder (robust EXIF/XMP)")
    ap.add_argument("gallery", choices=["wildlife","landscapes"], help="Gallery key/folder to build")
    ap.add_argument("--json", default=str(JSON_OUT_DEFAULT), help="Path to manifest JSON")
    ap.add_argument("--dry-run", action="store_true", help="Show what would change, do not write")
    ap.add_argument("--force-refresh", action="store_true", help="Refresh technical fields even if new values are empty")
    ap.add_argument("--verbose", action="store_true", help="Verbose logs with extractor used")
    args = ap.parse_args()

    gallery_key = args.gallery
    json_path = Path(args.json)
    orig_dir = ORIG_BASE / gallery_key
    out_dir  = GEN_BASE / gallery_key
    out_dir.mkdir(parents=True, exist_ok=True)

    if not orig_dir.exists():
        print(f"✖ Originals folder not found: {orig_dir}")
        sys.exit(1)

    manifest = load_manifest(json_path)
    idx = index_by_key(manifest)

    exts = {".jpg",".jpeg",".png",".tif",".tiff"}
    files = sorted([p for p in orig_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts])

    added_count = 0
    refreshed_count = 0
    new_items_buffer: list[dict] = []
    prefer_existing_non_empty = not args.force_refresh

    for p in files:
        slug = slugify(p.stem)
        k = (slug, gallery_key)
        try:
            built = build_entry_for_file(p, gallery_key, out_dir, verbose=args.verbose)
            if k in idx:
                existing = manifest[idx[k]]
                changed, _ = update_existing_technical_fields(existing, built, prefer_existing_non_empty)
                if changed:
                    refreshed_count += 1
            else:
                new_items_buffer.append(built)
                added_count += 1
        except Exception as e:
            print(f"[WARN] {p.name}: {e}")

    if new_items_buffer:
        manifest.extend(new_items_buffer)

    if args.dry_run:
        print(f"[DRY-RUN] Would add {added_count} new item(s), refresh {refreshed_count} item(s).")
        for it in new_items_buffer:
            print("  +", key_of(it), "→", it['original']['file'])
        return

    save_manifest(json_path, manifest)
    print(f"✅ Gallery '{gallery_key}' processed.")
    print(f"   Added    : {added_count}")
    print(f"   Refreshed: {refreshed_count} (technical fields only)")
    print(f"→ Variants in: {out_dir}")
    print(f"→ Manifest   : {json_path}")

if __name__ == "__main__":
    main()
