#!/usr/bin/env python3
"""
Rewrite a toolkit HTML file so its images survive a strict CSP.

artifacts.ceritypartners.com serves pages under:

    default-src 'self' https://unpkg.com https://cdn.jsdelivr.net https://esm.sh
    script-src  'self' 'unsafe-inline' 'unsafe-eval' ... blob:
    style-src   'self' 'unsafe-inline'
    connect-src https: data:

There is no img-src, so images fall back to default-src, which permits neither
`data:` nor `blob:` nor ceritypartners.com. Every `<img>` in the toolkit is
therefore blocked: the 82 inlined slides because they are data URIs, and the 24
bio headshots because they load from ceritypartners.com.

Nothing about the images themselves is disallowed — only *loading them from a
URL* is. So this script stops using URLs. Each `<img>` becomes a `<canvas>`, and
the bytes are decoded with createImageBitmap() on a Blob, which takes the data
directly and never performs a fetch. `object-fit` applies to canvas exactly as it
does to img, so the existing stylesheet keeps working once its `img` selectors
are mirrored onto `canvas.cimg`.

Bio photos are downloaded and inlined too, so the toolkit does not depend on a
live website while an advisor is in front of a prospect.

Usage:
    python3 canvas_shim.py INPUT.html OUTPUT.html [--bios bios_b64.json]
"""

import argparse
import base64
import io
import json
import re
import sys

from PIL import Image

IMG_TAG = re.compile(r"<img\b[^>]*?>", re.S)
DATA_URI = re.compile(r"data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)")
# `img` as a standalone type selector: not part of lightbox-img-wrap, .img, #img
BARE_IMG_SEL = re.compile(r"(?<![\w.#-])img(?![\w-])")


def attr(tag, name):
    m = re.search(r'\b%s="([^"]*)"' % name, tag)
    return m.group(1) if m else ""


def build_assets(html, bios_path):
    """Collect every image into one indexed table, and note the bio URL order."""
    def sized(mime, b64):
        w, h = Image.open(io.BytesIO(base64.b64decode(b64 + "=="))).size
        return (mime, b64, w, h)

    assets = []  # list of (mime, b64, natural width, natural height)
    for m in DATA_URI.finditer(html):
        assets.append(sized(m.group(1), m.group(2)))

    bio_urls = re.findall(r'data-photo="([^"]+)"', html)
    if bios_path:
        bios = json.load(open(bios_path))
        if len(bios) != len(bio_urls):
            sys.exit(
                f"bio count mismatch: {len(bio_urls)} data-photo attributes "
                f"but {len(bios)} encoded photos"
            )
        for b in bios:
            assets.append(sized("webp", b))
    return assets, bio_urls


def replace_img_tags(html, index_of):
    """Swap every data-URI <img> for a canvas carrying the asset index."""
    n = [0]

    def repl(tag):
        src = attr(tag.group(0), "src")
        m = DATA_URI.fullmatch(src.strip())
        if not m:
            return tag.group(0)
        idx = index_of[m.group(2)]
        cls = (attr(tag.group(0), "class") + " cimg").strip()
        alt = attr(tag.group(0), "alt")
        n[0] += 1
        return (
            f'<canvas class="{cls}" data-i="{idx}" role="img" aria-label="{alt}"></canvas>'
        )

    return IMG_TAG.sub(repl, html), n[0]


def mirror_css(html):
    """Duplicate every `img` type selector onto canvas.cimg."""
    start, end = html.find("<style>"), html.find("</style>")
    css = html[start + 7 : end]
    out = []
    changed = 0
    for chunk in re.split(r"(?<=\})", css):
        sel_end = chunk.find("{")
        if sel_end == -1:
            out.append(chunk)
            continue
        sel, body = chunk[:sel_end], chunk[sel_end:]
        parts = [p for p in sel.split(",")]
        extra = [BARE_IMG_SEL.sub("canvas.cimg", p) for p in parts if BARE_IMG_SEL.search(p)]
        if extra:
            changed += 1
            out.append(sel.rstrip() + ", " + ", ".join(x.strip() for x in extra) + body)
        else:
            out.append(chunk)
    return html[: start + 7] + "".join(out) + html[end:], changed


# --- exact source fragments the toolkit's own script uses -------------------

JS_PATCHES = [
    # thumbnails in the builder
    ("""const imgEl = card.querySelector('img');
if(imgEl) return '<img src="'+imgEl.getAttribute('src')+'" alt="">';""",
     """const imgEl = card.querySelector('canvas.cimg');
if(imgEl) return '<canvas class="cimg" data-i="'+imgEl.dataset.i+'" role="img" aria-label=""></canvas>';"""),

    # inline sizing applied to those thumbnails
    ("""thumb = thumb.replace('<img ', '<img style="width:44px;aspect-ratio:4/3;object-fit:cover;" ')""",
     """thumb = thumb.replace('<canvas ', '<canvas style="width:44px;aspect-ratio:4/3;object-fit:cover;" ')"""),

    # lightbox: which elements open it, and what counts as "inside" it
    ("""const img = e.target.closest('.ppt-slide-card img, .gallery-check-item img');""",
     """const img = e.target.closest('.ppt-slide-card canvas.cimg, .gallery-check-item canvas.cimg');"""),

    ("""if(e.target.closest('#slideLightbox') && !e.target.closest('#slideLightbox img')){""",
     """if(e.target.closest('#slideLightbox') && !e.target.closest('#slideLightbox canvas')){"""),
]

BIO_OLD = """const img = photo ? '<img src="'+photo+'" alt="'+name+'" loading="eager" onerror="this.outerHTML=\\'<div class=&quot;initials&quot;>'+initialsOf(name)+'</div>\\'">'"""
BIO_NEW = """const img = photo ? '<canvas class="cimg" data-i="'+photo+'" data-fb="'+initialsOf(name)+'" role="img" aria-label="'+name+'"></canvas>'"""

# Two contexts sized an <img> from the image's own dimensions rather than from
# CSS: the lightbox and the presenting stage. A canvas has no size until it is
# painted, and it is painted to fit the box it is in, so those two collapse to
# the small size they started at. Give them a definite box built from the real
# aspect ratio the loader publishes as --ar.
SIZING_CSS = """
#slideLightbox .lightbox-img-wrap canvas.cimg{
aspect-ratio:var(--ar, 4 / 3);
width:auto; height:calc(100vh - 140px);
max-width:100%; max-height:calc(100vh - 140px);
object-fit:contain;
}
.ppt-slide-card.presenting canvas.cimg{
aspect-ratio:var(--ar, 4 / 3);
width:auto; height:100%;
max-width:100%; max-height:100%;
object-fit:contain;
}
"""

LOADER = r"""
<script>
// ---------------------------------------------------------------------------
// Image loader.
//
// The host's CSP has no img-src, so images fall back to default-src, which
// allows neither data: nor blob: nor ceritypartners.com. Loading an image from
// any URL therefore fails. createImageBitmap() on a Blob takes the bytes
// directly and performs no fetch, so it is unaffected; the result is drawn into
// a canvas. object-fit behaves on canvas exactly as it does on img, so the
// stylesheet governs layout as before.
//
// Bitmaps are decoded on demand and closed straight after drawing, and canvases
// are only painted near the viewport, so 106 full-size images never sit in
// memory at once.
// ---------------------------------------------------------------------------
(function(){
  var A = window.__IMG_ASSETS__ || [];
  var MAXW = 1600;

  function bytes(b64){
    var s = atob(b64), a = new Uint8Array(s.length);
    for (var i = 0; i < s.length; i++) a[i] = s.charCodeAt(i);
    return a;
  }

  function fallback(el){
    var fb = el.dataset.fb;
    if (fb) { var d = document.createElement('div'); d.className = 'initials'; d.textContent = fb; el.replaceWith(d); }
  }

  function paint(el){
    var i = +el.dataset.i, a = A[i];
    if (!a) return;
    var box = el.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var bw = box.width || 320, bh = box.height || 240;
    // object-fit decides how much of the source actually lands in the box. A
    // landscape headshot cover-cropped into a portrait slot needs far more
    // pixels than the box is wide; sizing from box width alone renders it soft.
    var fit = (getComputedStyle(el).objectFit || 'fill');
    var rw = bw / a.w, rh = bh / a.h;
    var s = (fit === 'cover') ? Math.max(rw, rh)
          : (fit === 'contain' || fit === 'scale-down') ? Math.min(rw, rh)
          : rw;
    var want = Math.min(a.w, MAXW, Math.max(64, Math.ceil(a.w * s * dpr)));
    // Repaint only when meaningfully larger than what is already drawn.
    if (el._w && el._w >= want * 0.85) return;
    el._w = want;
    if (el._busy) return;
    el._busy = true;
    createImageBitmap(new Blob([bytes(a.d)], {type: 'image/' + a.m}))
      .then(function(bm){
        var s = Math.min(1, want / bm.width);
        var w = Math.max(1, Math.round(bm.width * s)), h = Math.max(1, Math.round(bm.height * s));
        el.width = w; el.height = h;
        el.getContext('2d').drawImage(bm, 0, 0, w, h);
        if (bm.close) bm.close();
        el._busy = false;
      })
      .catch(function(){ el._busy = false; fallback(el); });
  }

  var io = ('IntersectionObserver' in window)
    ? new IntersectionObserver(function(es){
        es.forEach(function(e){ if (e.isIntersecting) paint(e.target); });
      }, {rootMargin: '600px'})
    : null;

  var ro = ('ResizeObserver' in window)
    ? new ResizeObserver(function(es){ es.forEach(function(e){ paint(e.target); }); })
    : null;

  function hook(el){
    if (el._hooked) return;
    el._hooked = true;
    // A canvas has no intrinsic size until it is painted, so contexts that size
    // an image from the image itself (the lightbox, the presenting stage) have
    // nothing to work from. Publish the real ratio for the stylesheet to use.
    var a0 = A[+el.dataset.i];
    if (a0 && a0.w && a0.h) el.style.setProperty('--ar', a0.w + ' / ' + a0.h);
    if (io) io.observe(el); else paint(el);
    if (ro) ro.observe(el);
  }

  function scan(root){
    if (!root || root.nodeType !== 1) return;
    if (root.matches && root.matches('canvas.cimg')) hook(root);
    if (root.querySelectorAll) root.querySelectorAll('canvas.cimg').forEach(hook);
  }

  // Clones (the lightbox) and generated markup (bio cards, builder thumbnails)
  // arrive after load, so watch for them rather than scanning once.
  new MutationObserver(function(ms){
    ms.forEach(function(m){ m.addedNodes.forEach(scan); });
  }).observe(document.documentElement, {childList: true, subtree: true});

  scan(document.body);
  window.__paintCanvas__ = paint;
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--bios", help="JSON array of base64 bio photos, in data-photo order")
    args = ap.parse_args()

    html = open(args.input, encoding="utf-8").read()
    before = len(html)

    assets, bio_urls = build_assets(html, args.bios)
    index_of = {a[1]: i for i, a in enumerate(assets)}
    print(f"assets: {len(assets)} ({len(assets) - len(bio_urls)} slides + {len(bio_urls)} bios)")

    html, n_img = replace_img_tags(html, index_of)
    print(f"img tags -> canvas: {n_img}")

    # Bio photos: the URL becomes an index into the same table.
    if args.bios:
        base = len(assets) - len(bio_urls)
        for k, url in enumerate(bio_urls):
            html = html.replace('data-photo="%s"' % url, 'data-photo="%d"' % (base + k), 1)
        print(f"bio photos inlined: {len(bio_urls)}")

    html, n_css = mirror_css(html)
    print(f"css rules mirrored onto canvas.cimg: {n_css}")

    # Appended last so it wins over the mirrored intrinsic-sizing rules.
    html = html.replace("</style>", SIZING_CSS + "</style>", 1)

    applied = 0
    for old, new in JS_PATCHES:
        if old not in html:
            sys.exit("FAILED to locate JS fragment:\n" + old[:120])
        html = html.replace(old, new, 1)
        applied += 1
    if BIO_OLD not in html:
        sys.exit("FAILED to locate the bio photo fragment")
    html = html.replace(BIO_OLD, BIO_NEW, 1)
    applied += 1
    print(f"js fragments patched: {applied}")

    payload = json.dumps(
        [{"m": m, "d": d, "w": w, "h": h} for m, d, w, h in assets],
        separators=(",", ":"),
    )
    block = '<script>window.__IMG_ASSETS__=' + payload + ';</script>' + LOADER
    html = html.replace("</body>", block + "\n</body>", 1)

    open(args.output, "w", encoding="utf-8").write(html)
    after = len(html)
    print(f"\n{before/1e6:.2f}M -> {after/1e6:.2f}M chars")
    print(f"remaining <img> tags in markup: {len(re.findall(r'<img', html))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
