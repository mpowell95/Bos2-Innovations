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

## Probe 2 result — the host's actual policy

    default-src 'self' https://unpkg.com https://cdn.jsdelivr.net https://esm.sh
    script-src  'self' 'unsafe-inline' 'unsafe-eval' <cdns> blob:
    style-src   'self' 'unsafe-inline'
    connect-src https: data:
    form-action 'none'

    L createImageBitmap(Blob)  RENDERED      O foreignObject  RENDERED
    M blob: URL                BLOCKED       P pattern fill   RENDERED
    N putImageData             RENDERED

There is no `img-src`, so images fall back to `default-src`, which allows neither
`data:` nor `blob:` nor ceritypartners.com. That is the whole bug, and it covers
both the 82 inlined slides and the 24 bio headshots loaded from the website.

L rendering is the opening: `createImageBitmap()` on a Blob receives bytes
directly and performs no fetch, so no fetch directive applies to it. M is blocked
because it goes through a `blob:` URL, which `default-src` does not list.

Note `connect-src https: data:` — `fetch()` to any https origin is permitted, and
ceritypartners.com returns `access-control-allow-origin: *`, so bio photos could
be fetched at runtime instead of inlined. They are inlined anyway so the toolkit
does not depend on a live website during a client meeting.

---

# canvas_shim.py

Rewrites the toolkit so every image is drawn into a `<canvas>` from bytes rather
than loaded from a URL. See the module docstring for the mechanism.

    python3 tools/canvas_shim.py IN.html OUT.html --bios bios_b64.json

# cspserve.py

Serves the current directory with the host's exact CSP header on port 8899, so
changes can be verified against the real policy locally instead of by uploading.

    python3 tools/cspserve.py

Verified this way: the pre-shim file produces 82 "Refused to load the image"
errors, and the shimmed file produces zero, with 82/82 slide canvases and 4/4
sampled bio photos painted, lightbox and builder thumbnails working, no JS errors.

## Enlarging: intrinsic sizing

Two places sized the image from the image itself rather than from CSS:

    #slideLightbox .lightbox-img-wrap img { max-width:100%; max-height:calc(100vh - 140px) }
    .ppt-slide-card.presenting img        { width:auto; height:auto; max-width:100%; max-height:100% }

Neither sets a width or height, so an `<img>` lays out at its natural size and is
then capped. A canvas has no natural size — it is exactly the resolution it was
painted at, and it is painted to fit the box it is in, so both contexts settled
at the small size they started from. The lightbox opened but barely grew, and the
presenting stage had the same fault.

The loader now publishes each image's real ratio as `--ar`, and SIZING_CSS gives
those two contexts a definite box built from it. Everywhere else already sets an
explicit width and was unaffected.

Checked against the original file, same slide, same viewport:

    lightbox    original 1013x760   shimmed 1013x760
    presenting  original 1031x773   shimmed 1031x773

## Quality

Two things governed sharpness, only one of which costs bytes.

Canvas downscaling defaults to `imageSmoothingQuality = 'low'`, which is visibly
softer than how a browser scales an `<img>`. Setting it to `'high'` costs nothing
and applies wherever an image is drawn smaller than its source — every grid tile.

The rest is encoder quality. Measured, at method 6:

    slides q80   8.66M      q85  10.35M      q88  11.68M
    bios 700px q78 0.83M    1200px q84 2.43M

Shipped: slides q85, headshots 1200px q84 RGBA, for 14.56M against the 15M cap.
Slides stay at their native 1500x1125 throughout — resolution was never reduced,
only the encoder setting — and the lightbox paints the full 1500x1125 at 2x.

Headroom is now 0.44M. To buy more room, the two `data:application/pdf` download
links are 1.55M and are unlikely to work under this CSP anyway; dropping or
externalising them is the cheapest source of space.

## Embedded PDFs replaced with links

Eight of the ten documents in the resources table were already SharePoint links;
two were embedded as `data:application/pdf` payloads costing 1.55M characters.
Those two were also the least likely to work once hosted, since the CSP does not
allow `data:` and browsers block top-level navigation to a data: URL anyway.

`externalize_pdfs.py` swaps them for ordinary links, matching how the other eight
are handled. The label changes from "Download PDF" to "Open PDF", which is what
now happens.

    python3 tools/externalize_pdfs.py IN.html OUT.html \
        --link Initial-Wealth-Forecast-Plan-Preparation.pdf=<url> \
        --link Add-Accounts-Guide.pdf=<url>

Both now point at ceritypartners.box.com. File is 13.01M, 1.99M under the limit.

## Build order

    shrink_toolkit.py    original -> re-encoded images and PDFs
    externalize_pdfs.py  embedded PDFs -> links
    canvas_shim.py       <img> -> <canvas>, bio photos inlined

---

# pdf_export.py

Replaces window.print() on the presentation's button with a real PDF download.

Printing hands the page to the browser's print engine, which re-flows it onto
paper; that is why the output looked poor. This composes the PDF instead:

  * Pages are 10 x 7.5in (720x540pt), the 4:3 slide size, so a slide fills the
    page exactly with no margins.
  * A slide page is drawn from its original 1500x1125 bitmap, never screen
    scraped.
  * Text sections are rendered with html2canvas, trimmed of trailing blank
    space, and either shrunk onto one page or split at card boundaries rather
    than through the middle of a bio.
  * The file is named from the title-page fields:
    "Cerity Partners - <client> - <date>.pdf".

Three CSP details drove the implementation:

  * jsPDF and html2canvas are embedded, not loaded from cdn.jsdelivr.net. The
    policy does allow that CDN, but a corporate network blocking it would break
    the button in front of a prospect. Costs ~0.58M characters.
  * html2canvas rasterises inline SVG via a data: URL, which is blocked, so
    logos vanished from the PDF. Chrome also cannot decode an SVG blob through
    createImageBitmap. Every SVG here is paths and circles with at most one
    transform, so they are drawn with Path2D instead.
  * Any failure falls back to the original window.print() path.

    python3 tools/pdf_export.py IN.html OUT.html \
        --lib jspdf.min.js --lib html2canvas.min.js

Verified under the host policy: the button downloads a valid PDF, slide pages
carry 1500x1125 images, the logo renders, bio pages break between cards, and no
CSP refusal names a logo.

## PDF layout corrections

Three faults showed up in the first real export:

  * Text sections were captured at 1400px while the presenting view constrains
    content to ~1050px and applies zoom:1.35. Text therefore came out small and
    sat in the top half of the page. The stage is now 1040px wide.
  * Content was pinned to the top-left corner with no margin. Sections that fit
    on one page are now centred inside a 30pt margin; sliced pages use the same
    margin. Slides remain full bleed.
  * The disclosures section rendered as a bare heading. Its body lives in a
    closed <details>, which contributes no height even though the presenting CSS
    displays the body. Every <details> is opened on the clone before capture —
    this was omitting required disclosure text from every PDF.

---

# audit_sections.py

Hunts for content that exists in the file but never reaches a presentation or a
PDF — the class of fault the disclosures section had, where required text was
dropped silently with nothing failing and nothing logged.

    python3 tools/cspserve.py &
    python3 tools/audit_sections.py http://127.0.0.1:8899/Toolkit.html

## Audit results (this build)

Only one section flags, and it is correct: `sec-contact` hides 16,247 characters
in `#bioStore`, the data store the bio cards are generated from.

Everything else is clean. The short renders on sec-wealthplanning, familyoffice,
foundations, invmgmt, onboard and whycerity are expected: those are
`data-gallery-only`, so `expandForPresentation` never emits the section itself,
only the individual slides chosen from it.

Checks that came back clean: no duplicate element ids, no clipped containers, no
malformed links (29 links, all http/mailto), no 404s, no console errors during a
full click-through, and the fee calculator is arithmetically correct
($2M → 1.00%/$20,000; $5M → 0.90%/$45,000; $15M → 0.72%/$107,500).

## Open bug, not fixed

Ticking only gallery-only sections and choosing no slides from them launches a
presentation containing nothing but the title page and the disclosure, with no
warning. The "On Deck" list shows those sections as included, so the builder
says one thing and the presentation does another. `launchBtn` only guards
`presentationOrder.length === 0`, which is non-empty here.

The fix is to check what `expandForPresentation` actually returns, and warn
naming the sections that contributed no slides. Left alone because it changes
presentation behaviour rather than export behaviour.

---

# empty_deck_guard.py

Fixes the open bug above. `launchBtn` only tested
`presentationOrder.length === 0`, so ticking gallery-only sections and choosing
no slides passed the guard and launched a deck of title page plus disclosure,
silently, while "On Deck" showed those sections as included.

The guard works out what `expandForPresentation` will actually return and:

  * blocks the launch when nothing would be presented, naming the sections;
  * otherwise confirms when some sections would contribute nothing, since
    ticking a gallery-only section and picking no slides is never deliberate.

It listens on document in the capture phase; a listener on the button itself
would run after the existing one, because listeners on the target fire in
registration order regardless of the capture flag.

Verified: empty selection blocks, a normal section launches untouched, a gallery
section with slides launches untouched, a mixed selection confirms, and
cancelling that confirm does not launch.

## Injection anchoring

All three injectors now anchor to the LAST `</body>`, not the first. jsPDF's
minified source contains `</body>` inside string literals, so a replace-first
spliced the guard into the middle of the library and truncated it from 365,673
to 49,084 characters. The page still loaded; the only symptom was one
"Invalid or unexpected token" in the console and a guard that never ran.

Check script integrity after any injection:

    python3 - <<'X'
    import re, subprocess
    s = open('Toolkit.html', encoding='utf-8').read()
    for i, b in enumerate(re.findall(r'<script>(.*?)</script>', s, re.S)):
        open(f'/tmp/b{i}.js','w').write(b)
        r = subprocess.run(['node','--check',f'/tmp/b{i}.js'], capture_output=True)
        print(i, 'OK' if r.returncode == 0 else 'FAIL', len(b))
    X

---

# builder_ux.py

    python3 tools/builder_ux.py IN.html OUT.html --plain-rows --collapsible

`--plain-rows` drops the "Aa" placeholder. `resolveThumb()` fell back to a grey
tile for any card without a slide image — the three Onboarding Process sub-items
and the New Client Welcome Email. Those now render as plain checkbox + label
rows, and a picker whose cards all lack images lays out as a list rather than a
thumbnail grid. The five pickers that do have thumbnails are untouched.

`--collapsible` separates collapsing from selecting. The nested slide list had
no collapse control: its visibility was wired straight to the section checkbox,
so collapsing a 23-slide section meant unchecking it, which called
removeFromOrder() and dropped the section. A caret now toggles the list
independently.

The row is a `<label>` wrapping its checkbox, so anything inside it toggles the
checkbox. The caret is therefore a sibling before the label, positioned into the
gutter, and verified with a real hit-tested click rather than a synthetic one.

# save_templates.py

    python3 tools/save_templates.py IN.html OUT.html

Saves a named selection — sections, the slides chosen within them and their
order, and the colleagues — to localStorage, with one markable as the default.

Two things worth knowing:

  * `Array.prototype.slice` cannot read a `Set`; it has no `length`, so
    `[].slice.call(selectedContactIds)` returned `[]` and templates silently
    saved no colleagues. Use `Array.from`.
  * `buildChecklist()` runs only when the Build a Presentation tab is opened, so
    a default applied at page load has no checkboxes to act on. The default is
    applied the first time the builder is built, once.

Applying drives the checkboxes and fires their change events rather than writing
internal state, so the existing handlers stay the single source of truth; the
recorded orders are restored afterwards, since check order alone does not
preserve a dragged deck. Ids that no longer exist are skipped and reported.

Storage is per-browser and per-device — not shared between advisors. Export or
import would be the next step for that.

## Not changed

Alphabetising was already done: both the Meet Your Team roster and the builder's
colleague picker are in surname order (24 each, verified). Bio cards in the
presentation stay in seniority order by request.

---

# sidebar_groups.py

    python3 tools/sidebar_groups.py IN.html OUT.html

Groups the presentation's On Deck sidebar by section instead of listing every
slide. Membership is derived from the DOM — a slide card reports the
`.content-block` it sits in — so nothing about how the deck is built changes.

Three shapes, all present in this deck:

  * A section with no slides of its own (Title Page, Fee Structure, Meet Your
    Team, Disclosure) stays a single plain row.
  * A gallery-only section has no page of its own, so its header jumps to its
    first slide.
  * General Resources appears both as its own page and as the parent of a slide,
    so its page becomes the group header.

Only the group holding the current slide is open. Every header navigates, and
navigating is what opens a group, so there is no separate expand state to drift
out of step with the deck position.

## Sidebar was unclickable during slides — pre-existing

`.ppt-slide-card.presenting` is `position:absolute; inset:0`, but
`.present-stage` was not a positioned ancestor, so the card resolved against the
full-screen overlay and rendered 1440px wide starting at x=0 — covering the
250px sidebar. `elementFromPoint` over the sidebar returned the slide card, in
this build and in the original alike, so On Deck could not be clicked whenever a
slide image was on screen and the deck could only be driven by the arrows.

`.present-stage{ position:relative }` confines the card to the stage. Measured
after the fix, the card and the stage occupy the same box (left 250, width
1190), so the slide itself is unchanged.
