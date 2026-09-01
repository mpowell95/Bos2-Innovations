#!/usr/bin/env python3
"""
Shrink a self-contained B2i toolkit HTML file so it fits a host's character limit.

The size in these files is almost entirely embedded base64 payloads, not markup.
This script attacks them in place and leaves the HTML structure alone:

  1. Every embedded image is re-encoded to WebP. Exported slides are flat-colour
     graphics with text, which JPEG handles badly and WebP handles very well.
  2. Every embedded PDF has its bitmaps re-encoded to JPEG and downsampled.
     Screenshot-heavy guides are usually stored losslessly and are huge.
  3. HTML comments and leading indentation are stripped. This is a rounding
     error on size, but it is free.

Usage:
    python3 shrink_toolkit.py INPUT.html [OUTPUT.html] [--quality 80] [--limit 15000000]

Requires: pillow, pikepdf
"""

import argparse
import base64
import io
import re
import sys

from PIL import Image

try:
    import pikepdf
    from pikepdf import Name
except ImportError:
    pikepdf = None

IMG_RE = re.compile(r"data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)")
PDF_RE = re.compile(r"data:application/pdf;base64,([A-Za-z0-9+/=]+)")

# PDF bitmaps below this raw size are not worth touching.
PDF_IMAGE_MIN_BYTES = 20_000


def convert_images(html, quality, max_width):
    """Re-encode every embedded image as WebP, keeping whichever is smaller."""
    stats = {"n": 0, "before": 0, "after": 0}

    def repl(match):
        original = match.group(0)
        raw = base64.b64decode(match.group(2) + "==")
        try:
            im = Image.open(io.BytesIO(raw))
        except Exception:
            return original

        has_alpha = im.mode in ("RGBA", "LA") or (
            im.mode == "P" and "transparency" in im.info
        )
        im = im.convert("RGBA" if has_alpha else "RGB")

        if max_width and im.width > max_width:
            height = round(im.height * max_width / im.width)
            im = im.resize((max_width, height), Image.LANCZOS)

        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=quality, method=6)
        candidate = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

        # Never make a payload bigger than it started.
        if len(candidate) >= len(original):
            return original

        stats["n"] += 1
        stats["before"] += len(original)
        stats["after"] += len(candidate)
        return candidate

    return IMG_RE.sub(repl, html), stats


def shrink_pdf(raw, quality, max_dim):
    """Re-encode the bitmaps inside a PDF as JPEG. Returns new bytes, or None."""
    if pikepdf is None:
        return None

    try:
        pdf = pikepdf.open(io.BytesIO(raw))
    except Exception:
        return None

    changed = 0
    for page in pdf.pages:
        xobjects = page.get("/Resources", {}).get("/XObject", {}) or {}
        for obj in xobjects.values():
            try:
                if obj.get("/Subtype") != Name("/Image"):
                    continue
                original_size = len(obj.read_raw_bytes())
                if original_size < PDF_IMAGE_MIN_BYTES:
                    continue

                im = pikepdf.PdfImage(obj).as_pil_image().convert("RGB")
                if max(im.size) > max_dim:
                    scale = max_dim / max(im.size)
                    im = im.resize(
                        (max(1, int(im.width * scale)), max(1, int(im.height * scale))),
                        Image.LANCZOS,
                    )

                buf = io.BytesIO()
                im.save(buf, "JPEG", quality=quality, optimize=True)
                data = buf.getvalue()
                if len(data) >= original_size:
                    continue

                obj.write(data, filter=Name("/DCTDecode"))
                obj.Width, obj.Height = im.size
                obj.ColorSpace = Name("/DeviceRGB")
                obj.BitsPerComponent = 8
                for key in ("/DecodeParms", "/SMask", "/Decode"):
                    if key in obj:
                        del obj[key]
                changed += 1
            except Exception:
                continue

    if not changed:
        return None

    out = io.BytesIO()
    pdf.save(
        out,
        compress_streams=True,
        object_stream_mode=pikepdf.ObjectStreamMode.generate,
    )
    return out.getvalue()


def convert_pdfs(html, quality, max_dim):
    stats = {"n": 0, "before": 0, "after": 0}

    def repl(match):
        original = match.group(0)
        raw = base64.b64decode(match.group(1) + "==")
        data = shrink_pdf(raw, quality, max_dim)
        if data is None:
            return original

        candidate = "data:application/pdf;base64," + base64.b64encode(data).decode()
        if len(candidate) >= len(original):
            return original

        stats["n"] += 1
        stats["before"] += len(original)
        stats["after"] += len(candidate)
        return candidate

    return PDF_RE.sub(repl, html), stats


def strip_markup(html):
    """Drop comments and indentation.

    Safe only because these toolkits use no <pre> blocks, no white-space:pre,
    and no multi-line template literals. The caller checks that first.
    """
    html = re.sub(r"<!--(?!\[if).*?-->", "", html, flags=re.S)
    html = re.sub(r"^[ \t]+", "", html, flags=re.M)
    return re.sub(r"\n{3,}", "\n", html)


def markup_strip_is_safe(html):
    body = IMG_RE.sub("", PDF_RE.sub("", html))
    if "<pre" in body or re.search(r"white-space:\s*pre", body):
        return False
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", body, re.S)
    return not any("\n" in m.group(0) for s in scripts for m in re.finditer(r"`[^`]*`", s, re.S))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--quality", type=int, default=80, help="WebP quality (default 80)")
    ap.add_argument("--max-width", type=int, default=0, help="cap image width in px (0 = keep)")
    ap.add_argument("--pdf-quality", type=int, default=72)
    ap.add_argument("--pdf-max-dim", type=int, default=1100)
    ap.add_argument("--limit", type=int, default=15_000_000, help="host character limit")
    args = ap.parse_args()

    out_path = args.output or args.input.replace(".html", "_optimized.html")
    html = open(args.input, encoding="utf-8").read()
    before = len(html)

    html, img_stats = convert_images(html, args.quality, args.max_width)
    print(
        f"images: {img_stats['n']} converted, "
        f"{img_stats['before'] / 1e6:.2f}M -> {img_stats['after'] / 1e6:.2f}M chars"
    )

    if pikepdf is None:
        print("pdfs:   skipped (pikepdf not installed)")
    else:
        html, pdf_stats = convert_pdfs(html, args.pdf_quality, args.pdf_max_dim)
        print(
            f"pdfs:   {pdf_stats['n']} rebuilt, "
            f"{pdf_stats['before'] / 1e6:.2f}M -> {pdf_stats['after'] / 1e6:.2f}M chars"
        )

    if markup_strip_is_safe(html):
        stripped = strip_markup(html)
        print(f"markup: saved {(len(html) - len(stripped)) / 1000:.0f}K chars")
        html = stripped
    else:
        print("markup: skipped (file uses <pre>, white-space:pre, or template literals)")

    open(out_path, "w", encoding="utf-8").write(html)
    after = len(html)
    print(f"\n{before / 1e6:.2f}M -> {after / 1e6:.2f}M chars ({100 * after / before:.0f}% of original)")
    print(f"wrote {out_path}")

    if after > args.limit:
        over = (after - args.limit) / 1e6
        print(f"\nSTILL {over:.2f}M OVER the {args.limit / 1e6:.2f}M limit.")
        print("Try --quality 70 --max-width 1280, or move the PDFs out to their own host.")
        return 1

    print(f"under the {args.limit / 1e6:.2f}M limit, {(args.limit - after) / 1e6:.2f}M to spare")
    return 0


if __name__ == "__main__":
    sys.exit(main())
