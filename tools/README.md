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
