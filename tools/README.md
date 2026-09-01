# shrink_toolkit.py

Shrinks a self-contained B2i toolkit HTML file so it fits a host's character limit.

## Why it's needed

These toolkits are single HTML files with everything inlined as base64. The
markup is tiny; the payloads are not. A representative file:

| Part | Chars | Share |
|---|---|---|
| 81 exported slides (JPEG) | 17.83M | 80.3% |
| 2 embedded PDFs | 4.14M | 18.6% |
| Actual HTML/CSS/JS/text | 0.24M | 1.1% |

Stripping comments and whitespace is not a fix — comments were 3.5K chars,
0.016% of that file. The payloads are the only thing worth touching.

## What it does

1. Re-encodes every embedded image to WebP. Exported slides are flat-colour
   graphics with text; JPEG is a poor fit and WebP roughly halves them.
2. Re-encodes bitmaps inside embedded PDFs to JPEG and downsamples them.
   Screenshot-heavy guides are usually stored losslessly and are very large.
3. Strips HTML comments and indentation, but only after checking the file has
   no `<pre>`, no `white-space: pre`, and no multi-line template literals,
   any of which would make that unsafe.

It never writes a payload back larger than it started.

## Usage

    pip install pillow pikepdf
    python3 tools/shrink_toolkit.py Toolkit.html

Writes `Toolkit_optimized.html` and reports the before/after against the limit.

Still over? Turn the dials down:

    python3 tools/shrink_toolkit.py Toolkit.html --quality 70 --max-width 1280

## Results on the Prospect Meeting Toolkit

22.21M -> 10.43M chars (47% of original), 4.57M under the 15M limit.
All 82 images load, both PDF links intact, no JS errors, text stays crisp.

## Caveat

WebP needs a reasonably modern browser (Safari 14+, 2020 and later). Fine for
every current browser; worth knowing if a client is on something ancient.

---

# hosting_probe.html

A ~17KB diagnostic page. Upload it to the artifact host and read the right-hand
column: each row renders a green box if that technique survives, or stays a red
hatched box if it does not.

It exists because artifacts.ceritypartners.com sits behind Microsoft Entra auth
and returns 401 to anything unauthenticated, so its CSP and sanitizer behaviour
cannot be inspected remotely. The probe answers the question from the inside.

Rows A-C are data-URI `<img>` in PNG / WebP / JPEG. D and E wrap the same base64
in an inline `<svg><image>`. F routes it through CSS. G is true vector SVG with
no data URI. H is an external https image. I and J check inline CSS and JS. K
injects a data URI with JavaScript after load.

**K is the decisive row.** A server-side HTML sanitizer never sees script-created
DOM, so:

- K green, A red -> upload-time markup filtering. Wrapping images in inline SVG
  (D/E) or CSS (F) is worth trying.
- K red, A red -> the browser is refusing `data:` images, almost certainly a CSP
  `img-src` directive. SVG `<image href="data:...">` is governed by that same
  directive and will fail identically. The images have to stop being data URIs:
  export true vector SVG from the source PPTX, or serve them from an allowed
  origin (row H says whether that is possible).

## Probe 1 result (recorded 2026-09-01)

    A img+data:PNG    BLOCKED     G true vector SVG  RENDERED
    B img+data:WebP   BLOCKED     H external https   BLOCKED
    C img+data:JPEG   BLOCKED     I inline <style>   RENDERED
    D svg image href  BLOCKED     J inline <script>  RENDERED
    E svg xlink:href  BLOCKED     K JS-injected img  BLOCKED
    F css background  BLOCKED

K blocked settles it. A server-side sanitizer cannot see DOM created by script,
so a script-injected data URI would have survived one. It did not, which means
the browser is refusing the image itself — a CSP img-src directive. D and E are
blocked by that same directive, so wrapping rasters in inline SVG cannot work.

H blocked as well, so images cannot be served from another origin either.
G, I and J rendering means inline CSS, inline JS and true vector SVG all survive.

---

# hosting_probe2.html

Follow-up probe. Every route in probe 1 that worked avoided loading an image
from a URL, so this one tests whether the slide bitmaps can still be drawn
without one, and reports the host's actual policy text.

    L canvas + createImageBitmap(Blob)   native decode, no URL
    M canvas + blob: URL
    N canvas + putImageData              raw pixels, control case
    O SVG foreignObject
    P SVG pattern fill

It also listens for `securitypolicyviolation` and prints the violated directive
and full policy, which names exactly what the host permits.

If L or M render, the existing WebP slides can stay as they are and only the
drawing path changes. If only N/O/P render, the slides must be rebuilt as true
vector artwork, which means going back to the source PPTX.
