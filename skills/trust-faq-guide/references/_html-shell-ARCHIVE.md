<!-- ============================================================================
     ARCHIVE — NOT READ AT RUN TIME. DO NOT COPY FROM THIS FILE.

     This file is 50,866 bytes / 774 lines. The file-view tool truncates at about
     16,000 characters, so reading it WHOLE silently drops lines 137-638 — the rest
     of the <style> block, ALL of the <script> block, ALL of Part 4's snippets, ALL
     of Part 5's assembly rules, and the entire Part 6 binder stylesheet. Six
     versions of shell drift were caused by exactly that.

     The runtime source of truth is now assets/guide-template.html, which is read
     only by assets/build.py using open().read() — not subject to this truncation.

     This file is kept for maintainers, to explain what the shell means and why.
     If you must read it, read EXPLICIT LINE RANGES, never the whole file.
       Part 1 skeleton  13-45     Part 2 <style>   46-283
       Part 3 <script>  287-330   Part 4 snippets  334-562
       Part 5 rules     563-597   Part 6 binder    598-774
     ============================================================================ -->

# HTML Shell — Detailed FAQ Guide (single source of truth)

**Read this before writing any HTML. Copy the `<style>` and `<script>` blocks VERBATIM — do not re-author, rename, minify, or "improve" them.** Every guide must ship the exact same shell so any two guides look and behave identically. Your only job is to fill the component snippets in Part 4 with real facts.

This is the **Cerity Partners** theme: cobalt masthead with the Cerity logo, DM Sans / Cormorant font stacks, the brand palette, colorblind-safe section colors, and a "Built by Matt Powell · BOS2" attribution in the footer. Two layouts share one stylesheet:
- **Single-column** — a single trust, a Will, a Will+Trust package, a personal-documents bundle, or the binder index.
- **Two-column** — two mirror/paired revocable living trusts only (Part 4.J).

**The logo:** `references/cerity-logo.svg` holds the Cerity Partners logo as complete, self-contained inline `<svg>` markup. Read that file and paste its exact bytes into the header in place of the logo markup. Never wrap it in, or convert it to, an `<img>` tag or a `data:` URI — this guide is hosted on a platform whose CSP silently blocks any image loaded from a URL (including `data:` URIs), so an `<img src="data:...">` logo renders as a blank/missing image with no console error. Inline `<svg>` is the only form that survives that CSP. Give the pasted `<svg>` (or a wrapping element) the class `hdr-logo` so the existing CSS sizing rule still applies, since the asset's own class is `cp-logo`.

---

## Part 1 — Page skeleton (order is fixed)

```
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="author" content="Matt Powell - Cerity Partners BOS2">
<!-- Trust & Estate Guide | Built by Matt Powell · Cerity Partners BOS2 | 2026 -->
<title>Cerity Partners — [Document Name] Guide</title>
<!-- No Google Fonts <link> — this guide is hosted on a platform whose CSP has no
     allowance for external stylesheets, so a fonts.googleapis.com <link> would be
     silently blocked (same CSP that blocks data: images — see the logo note above).
     The font-family stacks below already lead with 'DM Sans'/'Cormorant Garamond' and
     fall through to system-ui/Segoe UI/Arial/serif, so the page still looks correct;
     it just renders in the viewer's installed fonts rather than the literal brand font. -->
<style> … Part 2, verbatim … </style>
</head>
<body>                            <!-- two-column guides only: <body data-view="both"> -->
  <div class="page-header"> … </div>
  <div class="toolbar-strip"> … </div>     <!-- always BETWEEN header and main; never inside either -->
  <main> … sections … </main>
  <div class="page-footer"> … </div>
  <script> … Part 3, verbatim … </script>
</body>
</html>
```

There's no Google Fonts `<link>` to load — see the note above. The font-family stacks already have system fallbacks built in, so the guide renders correctly everywhere (offline, in Box, on any machine) with no dependency on an external font request; only the exact typeface varies by viewer.

---

## Part 2 — The `<style>` block (VERBATIM)

```html
<style>
  :root {
    /* Cerity Partners brand palette (from the CP Portfolio Tool) */
    --cobalt: #293340;
    --fiord: #3A5772;
    --fiord-l: #61798E;
    --clay: #5C574D;
    --clay-l: #6F665A;
    --desert: #D7C8B6;
    --vellum: #F4F1EE;
    --tradewind: #5FC3B1;
    --mandarin: #D26431;
    --white: #ffffff;
    --maxw: 1240px;   /* shared content width — header, toolbar, and main all align to this column */

    /* Section categories — colorblind-safe: each differs in HUE *and* lightness,
       and never relies on red/green discrimination. Reinforced by the section label text. */
    --cat-overview: #344D63;      --cat-overview-bg: #eaeff3;
    --cat-trustee: #2f7d6e;       --cat-trustee-bg: #e3f2ee;
    --cat-lifecycle: #b5561f;     --cat-lifecycle-bg: #fbeadd;
    --cat-distribution: #7D5E3D;  --cat-distribution-bg: #f2ebe1;
    --cat-legal: #5C574D;         --cat-legal-bg: #eeece7;

    --ink: #293340;
    --muted: #6F665A;
    --border: #D7C8B6;
    --bg: #F4F1EE;

    /* Status banners — distinct ICON SHAPE per type so meaning survives without color */
    --warn-bg: #fdf1e3;  --warn-bd: #D26431;  --warn-tx: #8a3d16;
    --flag-bg: #fbe9e4;  --flag-bd: #c0492a;  --flag-tx: #8f2f18;
    --info-bg: #e3f2ee;  --info-bd: #2f7d6e;  --info-tx: #1f5147;

    --amt: #3A5772;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Sans', system-ui, 'Segoe UI', Arial, sans-serif;
    font-size: 15px; line-height: 1.6;
    background: var(--bg); color: var(--ink);
  }

  /* ── ICONS (SVG only — never emoji) ── */
  .ic { width: 1em; height: 1em; display: inline-block; vertical-align: -0.125em; flex-shrink: 0; fill: currentColor; }
  .chevron {
    width: 0; height: 0; display: inline-block; flex-shrink: 0; transition: transform 0.2s;
    border-style: solid; border-width: 0.33em 0 0.33em 0.46em;
    border-color: transparent transparent transparent currentColor;
  }
  /* Pure CSS border-triangle — deliberately not a mask/background-image data: URI.
     Same CSP that blocks <img src="data:..."> also blocks mask/background-image
     url(data:...), so any data:-URI icon here would render invisible with no error. */
  [aria-expanded="true"] > .chevron { transform: rotate(90deg); }

  /* ── HEADER (Cerity cobalt bar + logo — no byline; that lives in the footer only) ── */
  .page-header { background: var(--cobalt); color: white; padding: 13px 0 10px; }
  .hdr-inner { max-width: var(--maxw); margin: 0 auto; padding: 0 24px; }
  .hdr-top { display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
  .hdr-main { display: flex; align-items: center; gap: 14px; }
  .hdr-logo, .hdr-logo.cp-logo, .hdr-main > svg { height: 42px; width: auto; color: #fff; }
  .hdr-div { width: 1px; height: 46px; background: rgba(255,255,255,.22); }
  .hdr-text { display: flex; flex-direction: column; gap: 4px; }
  .hdr-eyebrow { font-family: 'DM Sans', sans-serif; font-size: 11.5px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; color: var(--tradewind); }
  .hdr-title { font-family: 'DM Sans', system-ui, sans-serif; font-size: 27px; font-weight: 700; color: white; letter-spacing: 0; line-height: 1.05; }
  .hdr-dates { font-size: 12px; color: rgba(255,255,255,.55); text-align: right; white-space: nowrap; }
  .hdr-bottom { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,.1); }
  .crumb { display: inline-flex; align-items: center; gap: 5px; color: #bfe6dd; text-decoration: none; font-size: 11.5px; }
  .crumb:hover { text-decoration: underline; }
  .irrev-badge { font-size: 10px; font-weight: 700; letter-spacing: .5px; background: var(--mandarin); color: white; border-radius: 4px; padding: 3px 9px; text-transform: uppercase; }

  /* ── TOOLBAR (light band; content aligned to the body column) ── */
  .toolbar-strip { background: #efe9e1; border-bottom: 1px solid var(--desert); padding: 7px 0; }
  .toolbar-inner { max-width: var(--maxw); margin: 0 auto; padding: 0 24px; display: flex; align-items: center; gap: 9px; flex-wrap: wrap; }
  .toolbar-inner .label { color: var(--clay); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; margin-right: 4px; }
  /* Two-column guides only: View (row 1) + Show/filters (row 2), separated by a thin rule */
  .toolbar-inner.toolbar-row { padding-top: 4px; padding-bottom: 4px; }
  .toolbar-inner.toolbar-row + .toolbar-inner.toolbar-row { border-top: 1px solid var(--desert); margin-top: 3px; padding-top: 7px; }
  .toolbar-btn {
    font-family: 'DM Sans', system-ui, sans-serif; background: transparent; color: var(--cobalt);
    border: 1px solid var(--desert); border-radius: 5px; padding: 6px 14px; font-size: 12.5px; font-weight: 600;
    letter-spacing: .02em; cursor: pointer; transition: all .15s; display: inline-flex; align-items: center; gap: 6px;
  }
  .toolbar-btn:hover { background: #e6ded2; border-color: var(--clay-l); }
  .toolbar-btn.active { background: var(--tradewind); border-color: var(--tradewind); color: var(--cobalt); }
  .toolbar-btn:focus-visible { outline: 2px solid var(--cobalt); outline-offset: 2px; }
  /* Expand/Collapse — secondary "utility" controls, visually distinct from the filter pills */
  .util-btn { font-family: 'DM Sans', system-ui, sans-serif; border: none; background: transparent; color: var(--clay-l); font-size: 12px; font-weight: 600; padding: 6px 4px; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; text-decoration-color: var(--desert); }
  .util-btn:hover { color: var(--cobalt); text-decoration-color: var(--clay-l); }
  .util-btn:focus-visible { outline: 2px solid var(--cobalt); outline-offset: 2px; }
  .toolbar-sep { color: var(--desert); margin: 0 3px; }
  .print-btn { margin-left: auto; background: var(--tradewind); border-color: var(--tradewind); color: var(--cobalt); font-weight: 700; }
  .print-btn:hover { background: #4fb3a1; }

  main { max-width: var(--maxw); margin: 24px auto; padding: 0 24px 60px; }

  /* ── QUICK REF (dense two-column facts table with left/right pairing) ── */
  .quick-ref { background: white; border-radius: 6px; border: 1px solid #e5e0d7; box-shadow: 0 1px 3px rgba(41,51,64,.05); overflow: hidden; margin-bottom: 28px; }
  .quick-ref-header { padding: 14px 20px 12px; font-size: 13px; font-weight: 600; color: var(--clay); letter-spacing: .01em; border-bottom: 1px solid var(--border); }
  .quick-ref-header + table { border-top: none; }
  .qr-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
  .qr-table tr { border-bottom: 1px solid #efe9e1; }
  .qr-table tr:last-child { border-bottom: none; }
  .qr-table td { padding: 11px 18px; vertical-align: top; line-height: 1.45; }
  .qr-table td.qr-k { color: var(--ink); font-weight: 600; width: 18%; white-space: nowrap; }
  .qr-table td.qr-v { color: #3d4653; width: 32%; }
  .qr-table td.qr-v.qr-v-wide { width: 82%; }
  .qr-table td.qr-k + td.qr-v { border-right: 1px solid #efe9e1; }
  /* dim citations inside Quick Reference so answers dominate */
  .qr-table .section-ref { background: #eee9e2; color: var(--clay-l); font-size: 10.5px; padding: 1px 5px; margin-left: 5px; font-family: ui-monospace, monospace; opacity: .95; }
  /* subtle highlight for the one or two facts a reader's eye should land on */
  .qr-hl { background: linear-gradient(transparent 55%, #fce9a8 55%, #fce9a8 92%, transparent 92%); padding: 0 2px; font-weight: 600; }
  .qr-hl-row td.qr-v { background: #fef7e0; }
  /* multi-person values: stack one per line so each name reads cleanly */
  .qr-people { list-style: none; margin: 0; padding: 0; }
  .qr-people li { padding: 1px 0; line-height: 1.4; }
  .qr-people li + li { margin-top: 2px; }
  /* numbered chip list for successor trustees */
  .qr-num-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
  .qr-num-list li { display: flex; align-items: baseline; gap: 10px; }
  .qr-num-list .n { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; background: var(--cobalt); color: white; font-size: 11px; font-weight: 700; border-radius: 3px; flex-shrink: 0; position: relative; top: 2px; }
  .qr-diff-badge { display: inline-block; background: #fbdb6a; color: #5a4200; font-size: 10.5px; font-weight: 700; letter-spacing: .04em; padding: 2px 8px; border-radius: 3px; text-transform: uppercase; margin-left: 8px; vertical-align: middle; }
  @media (max-width: 820px) {
    .qr-table, .qr-table tbody, .qr-table tr, .qr-table td { display: block; width: 100% !important; }
    .qr-table td.qr-k { padding-bottom: 2px; }
    .qr-table td.qr-k + td.qr-v { border-right: none; }
    .qr-table td.qr-v { padding-top: 2px; padding-bottom: 14px; }
  }

  /* ── BANNERS (class="banner <type>-banner"; each type has a distinct icon shape) ── */
  .banner { border-radius: 8px; padding: 12px 16px; margin: 14px 0 12px; font-size: 13px; line-height: 1.55; display: flex; gap: 12px; align-items: flex-start; border: 1px solid transparent; }
  .banner .ic { margin-top: 1px; font-size: 17px; }
  .banner strong { font-weight: 700; }
  .warning-banner { background: #fbf3e6; border-color: #eed9bd; }
  .warning-banner .ic, .warning-banner strong { color: var(--warn-tx); }
  .flag-banner { background: #fbeeea; border-color: #f0d2c8; }
  .flag-banner .ic, .flag-banner strong { color: var(--flag-tx); }
  .info-banner { background: #e9f4f0; border-color: #cbe4dc; }
  .info-banner .ic, .info-banner strong { color: var(--info-tx); }

  /* ── SECTIONS ── */
  .faq-section { background: white; border-radius: 8px; border: 1px solid var(--border); box-shadow: 0 1px 4px rgba(41,51,64,.06); margin-bottom: 16px; overflow: hidden; }
  .faq-section[hidden] { display: none; }
  .section-title {
    width: 100%; font-family: 'DM Sans', system-ui, sans-serif; text-align: left; border: none;
    display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 13px 20px;
    cursor: pointer; user-select: none; font-size: 14px; font-weight: 700; letter-spacing: .01em; transition: filter .12s;
    border-left: 4px solid transparent;
  }
  .section-title:hover { filter: brightness(0.97); }
  .section-title:focus-visible { outline: 2px solid var(--cobalt); outline-offset: -2px; }
  .faq-section[data-cat="overview"] .section-title { background: var(--cat-overview-bg); color: var(--cat-overview); border-left-color: var(--cat-overview); }
  .faq-section[data-cat="trustee"] .section-title { background: var(--cat-trustee-bg); color: var(--cat-trustee); border-left-color: var(--cat-trustee); }
  .faq-section[data-cat="lifecycle"] .section-title { background: var(--cat-lifecycle-bg); color: var(--cat-lifecycle); border-left-color: var(--cat-lifecycle); }
  .faq-section[data-cat="distribution"] .section-title { background: var(--cat-distribution-bg); color: var(--cat-distribution); border-left-color: var(--cat-distribution); }
  .faq-section[data-cat="legal"] .section-title { background: var(--cat-legal-bg); color: var(--cat-legal); border-left-color: var(--cat-legal); }
  .section-title .title-text { display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .section-body { padding: 0 20px 16px; display: none; }
  .section-body.open { display: block; }

  /* ── Q&A ── */
  .faq-item { border-bottom: 1px solid #f0ede8; padding-bottom: 6px; margin-bottom: 4px; }
  .faq-item:last-child { border-bottom: none; }
  .faq-q {
    width: 100%; font-family: 'DM Sans', system-ui, sans-serif; text-align: left; background: none; border: none;
    display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; padding: 11px 0 6px;
    cursor: pointer; font-weight: 600; font-size: 14px; color: var(--cobalt);
  }
  .faq-q:focus-visible { outline: 2px solid var(--cobalt); outline-offset: 2px; }
  .faq-q .chevron { color: var(--clay-l); margin-top: 3px; }
  .faq-a { display: none; padding: 2px 0 10px 0; font-size: 13.5px; color: #3d4653; line-height: 1.65; max-width: 760px; }
  .faq-a.open { display: block; }
  .faq-a ul, .faq-a ol { margin: 8px 0 0 20px; font-size: 13.5px; }

  /* ── INLINE ── */
  .section-ref { font-size: 11px; background: #e9e3da; color: var(--clay); border-radius: 3px; padding: 1px 5px; margin-left: 4px; font-family: ui-monospace, monospace; white-space: nowrap; }
  .doc-badge { display: inline-block; background: #e9e3da; color: var(--clay); border-radius: 3px; padding: 2px 8px; font-size: 11.5px; font-weight: 600; margin-left: 6px; font-family: ui-monospace, monospace; }
  .amt { color: var(--amt); font-weight: 700; }
  .amt-lapse { color: var(--flag-tx); font-weight: 600; font-style: italic; }
  .na { color: var(--mandarin); font-weight: 600; }
  .not-found { color: var(--flag-tx); font-style: italic; }

  /* ── TABLES ── */
  .data-table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 10px 0; }
  .data-table th { background: var(--vellum); color: var(--clay); font-weight: 700; padding: 7px 12px; text-align: left; border-bottom: 2px solid var(--desert); letter-spacing: .02em; }
  .data-table td { padding: 7px 12px; border-bottom: 1px solid #f0ede8; vertical-align: top; }
  .data-table tr:last-child td { border-bottom: none; }
  .data-table tr:hover td { background: #faf8f5; }

  /* ── FLOWCHART — neutral stages so color carries ONE meaning: mandarin = the stage active now ── */
  .flowchart { margin: 14px 0; }
  .flow-stage { border: 1px solid var(--desert); border-left: 3px solid var(--fiord-l); border-radius: 6px; padding: 14px 18px 13px; background: #fff; margin-bottom: 6px; }
  .flow-stage .stage-label { display: block; font-family: 'DM Sans', system-ui, sans-serif; font-size: 15px; font-weight: 700; color: var(--cobalt); letter-spacing: -.005em; margin-bottom: 6px; line-height: 1.2; }
  .flow-stage .stage-label::before { content: ""; display: inline-block; width: 6px; height: 6px; background: var(--fiord-l); border-radius: 50%; margin-right: 9px; vertical-align: 3px; }
  .flow-stage .stage-content { font-size: 13.5px; color: #3d4653; line-height: 1.55; padding-left: 15px; }
  .flow-arrow { display: flex; justify-content: center; margin: 0 0 4px; }
  .flow-arrow::before { content: ""; width: 0; height: 0; border-left: 7px solid transparent; border-right: 7px solid transparent; border-top: 9px solid var(--fiord-l); }
  .flow-branch { display: flex; gap: 10px; margin-bottom: 6px; }
  .flow-branch .flow-stage { flex: 1; }
  .flow-stage.active-now { border: 1px solid var(--mandarin); border-left: 3px solid var(--mandarin); background: #fdf1e3; }
  .flow-stage.active-now .stage-label { color: var(--mandarin); }
  .flow-stage.active-now .stage-label::before { background: var(--mandarin); }

  /* ── TWO-COLUMN (mirror/paired trusts only) ── */
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 10px 0; }
  .col { border: 1px solid var(--border); border-radius: 6px; padding: 10px 12px; background: #fcfbf9; }
  .col-head { font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
  .col-g1 .col-head { color: var(--cat-overview); }
  .col-g2 .col-head { color: var(--cat-distribution); }
  .identical-row { display: flex; gap: 9px; align-items: flex-start; background: var(--info-bg); border-left: 4px solid var(--info-bd); border-radius: 4px; padding: 10px 14px; margin: 10px 0; }
  .badge-identical { background: var(--tradewind); color: var(--cobalt); border-radius: 20px; padding: 2px 10px; font-size: 11px; font-weight: 700; letter-spacing: .04em; flex-shrink: 0; }
  body[data-view="g1"] .col-g2 { display: none; } body[data-view="g1"] .two-col { grid-template-columns: 1fr; }
  body[data-view="g2"] .col-g1 { display: none; } body[data-view="g2"] .two-col { grid-template-columns: 1fr; }
  body[data-view="same"] .two-col { display: none; }

  /* ── FOOTER ── */
  .page-footer { border-top: 3px solid var(--desert); padding: 16px 40px; background: white; }
  .footer-row { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; font-size: 11.5px; color: var(--clay); }
  .footer-row .attrib { font-size: 10px; color: var(--clay-l); opacity: .7; letter-spacing: .04em; }
  .footer-disclaimer { margin-top: 8px; font-size: 10.5px; color: var(--clay-l); line-height: 1.5; }

  @media (max-width: 640px) { .two-col { grid-template-columns: 1fr; } }
  @media print {
    .toolbar-strip, .print-btn { display: none !important; }
    .faq-a, .section-body { display: block !important; }
    .page-header { background: var(--cobalt) !important; padding: 8px 24px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    main { max-width: 100%; padding: 0 16px; margin-top: 14px; }
    .faq-section { break-inside: avoid; }
    .chevron { display: none; }
    body[data-view] .col-g1, body[data-view] .col-g2 { display: block !important; }
    body[data-view] .two-col { grid-template-columns: 1fr 1fr !important; }
  }
</style>
```

---

## Part 3 — The `<script>` block (VERBATIM)

Toggles are real `<button>`s wired with inline `onclick`, so keyboard (Tab/Enter/Space) and `aria-expanded` work automatically — do not add `addEventListener`/`keydown` handlers.

```html
<script>
  function toggleSection(btn) {
    var open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!open));
    btn.nextElementSibling.classList.toggle('open', !open);
  }
  function toggleQ(btn) {
    var open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!open));
    btn.nextElementSibling.classList.toggle('open', !open);
  }
  function filterSections(cat, btn) {
    document.querySelectorAll('.toolbar-btn[data-filter]').forEach(function (b) {
      b.classList.remove('active'); b.setAttribute('aria-pressed', 'false');
    });
    btn.classList.add('active'); btn.setAttribute('aria-pressed', 'true');
    document.querySelectorAll('.faq-section').forEach(function (sec) {
      sec.hidden = !(cat === 'all' || sec.dataset.cat === cat);
    });
  }
  function setView(mode, btn) {
    document.querySelectorAll('.view-btn').forEach(function (b) {
      b.classList.remove('active'); b.setAttribute('aria-pressed', 'false');
    });
    if (btn) { btn.classList.add('active'); btn.setAttribute('aria-pressed', 'true'); }
    document.body.setAttribute('data-view', mode);
  }
  function expandAll() {
    document.querySelectorAll('.section-title, .faq-q').forEach(function (b) {
      b.setAttribute('aria-expanded', 'true'); b.nextElementSibling.classList.add('open');
    });
  }
  function collapseAll() {
    document.querySelectorAll('.section-title, .faq-q').forEach(function (b) {
      b.setAttribute('aria-expanded', 'false'); b.nextElementSibling.classList.remove('open');
    });
  }
</script>
```

---

## Part 4 — Component snippets (fill with real facts)

### A. Reusable SVG icons
Paste these exact `<svg>`s where an icon is needed (`aria-hidden` because adjacent text carries the meaning). Each banner type uses a **different shape**, so severity is legible without color.

- **Warning triangle** — `warning-banner` and the header context alert (caution / action needed):
```html
<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M12 3 22.5 21.5 1.5 21.5Z M12 7 18.9 19 5.1 19Z M11 10h2v5h-2z M11 16.5h2v2h-2z"/></svg>
```
- **Octagon** — `flag-banner` (superseded / stale / critical):
```html
<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M7.5 2H16.5L22 7.5V16.5L16.5 22H7.5L2 16.5V7.5Z M11 6h2v8h-2z M11 16h2v2.4h-2z"/></svg>
```
- **Info circle** — `info-banner` (clarifying note):
```html
<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm-1 5h2v2h-2zm0 4h2v6h-2z"/></svg>
```
- **Printer** — Print/PDF button only:
```html
<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v4H6z"/><path d="M4 8h16a2 2 0 0 1 2 2v6h-4v-3H6v3H2v-6a2 2 0 0 1 2-2zm14 3a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/><path d="M6 14h12v7H6z"/></svg>
```
- **Check** — a completed/occurred item (e.g. a binder timeline stage):
```html
<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>
```
Chevrons are drawn by CSS — write `<span class="chevron" aria-hidden="true"></span>` (empty).

### B. Header (insert the logo from references/cerity-logo.svg)
Logo sits top-left. The teal `.hdr-eyebrow` says "Trust & Estate FAQ" (signals this is a summary/FAQ, not the executed document). One right-aligned `.hdr-dates` line. No byline anywhere in the header or toolbar — the footer's `.attrib` (Part 4.E) is the only place "Built by Matt Powell · BOS2" appears. `.hdr-bottom` exists only to hold the binder back-link, so it's omitted entirely for a standalone guide (no crumb, nothing else to put there). Everything is inside `.hdr-inner` so it aligns with the body column.
```html
<div class="page-header">
  <div class="hdr-inner">
    <div class="hdr-top">
      <div class="hdr-main">
        <!-- PASTE inline <svg>…</svg> from references/cerity-logo.svg here, verbatim, with class="hdr-logo" added -->
        <div class="hdr-div"></div>
        <div class="hdr-text">
          <span class="hdr-eyebrow">Trust &amp; Estate FAQ</span>
          <span class="hdr-title">[Full Document Name, e.g. Lynn A. Stofer Revocable Trust]</span>
        </div>
      </div>
      <div class="hdr-dates">[document type · dates / amendment history]</div>
    </div>
    <div class="hdr-bottom">
      <a class="crumb" href="[Family]_Estate_Plan_Index.html">&#8592; [Family] Family Estate Plan index</a>
    </div>
  </div>
</div>
```
If the guide is standalone (not part of a binder), drop `.hdr-bottom` entirely — it existed only to hold the crumb, and there's nothing else to right-align there now that the byline is gone. Any survivor/active-event context goes in a `warning-banner` at the top of `<main>` (not a second header bar).

### C. Toolbar (single-column)
Contents live in `.toolbar-inner` so they align with the body column. Filters are bordered pills; Expand/Collapse are `.util-btn` (borderless, underlined — clearly secondary); Print is the teal primary action.
```html
<div class="toolbar-strip">
  <div class="toolbar-inner">
    <span class="label">Show:</span>
    <button type="button" class="toolbar-btn active" data-filter aria-pressed="true" onclick="filterSections('all', this)">All Sections</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('overview', this)">Overview</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('trustee', this)">Trustee</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('distribution', this)">Distributions</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('lifecycle', this)">Lifecycle</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('legal', this)">Legal / Admin</button>
    <span class="toolbar-sep" aria-hidden="true">|</span>
    <button type="button" class="util-btn" onclick="expandAll()">Expand all</button>
    <button type="button" class="util-btn" onclick="collapseAll()">Collapse all</button>
    <button type="button" class="toolbar-btn print-btn" onclick="window.print()">
      <svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v4H6z"/><path d="M4 8h16a2 2 0 0 1 2 2v6h-4v-3H6v3H2v-6a2 2 0 0 1 2-2zm14 3a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/><path d="M6 14h12v7H6z"/></svg>
      Print / PDF
    </button>
  </div>
</div>
```
Two-column guides split the toolbar into two rows instead of cramming everything into one (see Part 4.J).

### D. Quick Reference (§1) — never collapsible
A dense two-column facts table, not a hero strip and not a flowing chip cloud. The `.quick-ref-header` is a light section label (not a dark bar). `.qr-table` renders each row as `<td class="qr-k">` (label) followed by `<td class="qr-v">` (value), twice per row (left pair, right pair) — a subtle vertical divider between the left value and the right label separates the two pairs. Citations inside Quick Reference render as small greyish chips (`.qr-table .section-ref`) so they don't compete with the answers.
```html
<div class="quick-ref">
  <div class="quick-ref-header">§1 — Key facts</div>
  <table class="qr-table">
    <tr>
      <td class="qr-k">Document</td><td class="qr-v">[what this is in a phrase]</td>
      <td class="qr-k">Governing version</td><td class="qr-v"><span class="qr-hl">Restated [date]</span>, original [date]</td>
    </tr>
    <tr>
      <td class="qr-k">Grantors</td>
      <td class="qr-v"><ul class="qr-people"><li>[Name 1]</li><li>[Name 2]</li></ul></td>
      <td class="qr-k">Governing law</td><td class="qr-v">[State] <span class="section-ref">1.4</span></td>
    </tr>
    <tr>
      <td class="qr-k">Successor trustees</td>
      <td class="qr-v qr-v-wide" colspan="3">
        <ol class="qr-num-list">
          <li><span class="n">1</span><span>[First successor]</span></li>
          <li><span class="n">2</span><span>[Second]</span><span class="qr-diff-badge">Only difference</span></li>
          <li><span class="n">3</span><span>[Third]</span></li>
          <li><span class="n">4</span><span>[Corporate fallback] <span class="section-ref">3.2</span></span></li>
        </ol>
      </td>
    </tr>
    <tr>
      <td class="qr-k">[Missing item]</td><td class="qr-v"><span class="not-found">[NOT FOUND — verify in original document]</span></td>
      <td class="qr-k"></td><td class="qr-v"></td>
    </tr>
  </table>
</div>
```
**Rules for filling this table:**
- **Multi-person values ALWAYS stack one per line** using `<ul class="qr-people">` — Grantors, Remainder beneficiaries, any field that lists two or more people. Never combine names with `·` or `,` on one line — even short names become harder to parse when mashed together. This rule applies inside `.qr-num-list` too (when the "only difference" involves two people, stack them).
- **Full-width rows** (Successor trustees, or any list-based value): use `<td class="qr-v qr-v-wide" colspan="3">` on the value cell so it spans the remaining three column slots.
- **Highlight the 1–2 facts a reader's eye should land on FIRST** using `<span class="qr-hl">` — typically the current governing version's date and the payout ages. Don't highlight more than 2–3 things total, or the highlighting stops meaning anything.
- **Trailing empty cells are fine** — if the last row has only one fact, leave the second `qr-k`/`qr-v` pair empty rather than forcing an unrelated fact into it.
- Every value cell that has a citation keeps its `.section-ref`.

### E. Collapsible section + Q&A
```html
<div class="faq-section" data-cat="overview">
  <button type="button" class="section-title" aria-expanded="true" onclick="toggleSection(this)">
    <span class="title-text">§2 — [Section Title] <span class="doc-badge">[opt. doc id]</span></span>
    <span class="chevron" aria-hidden="true"></span>
  </button>
  <div class="section-body open">
    <div class="faq-item">
      <button type="button" class="faq-q" aria-expanded="false" onclick="toggleQ(this)">
        <span>[Question?]</span><span class="chevron" aria-hidden="true"></span>
      </button>
      <div class="faq-a">[Answer with <span class="section-ref">§X.XX</span> citations.]</div>
    </div>
  </div>
</div>
```
Set `aria-expanded` and `.open` per the defaults in Part 5. A section's `aria-expanded` must always equal its body's `.open` (and each `.faq-q` its `.faq-a`).

### F. Data table (distributions, trustees/executors, agents, charities, schedules)
```html
<table class="data-table">
  <tr><th>Priority</th><th>Name</th><th>Condition</th><th>§Ref</th></tr>
  <tr><td>[..]</td><td>[..]</td><td>[..]</td><td><span class="section-ref">§X.XX</span></td></tr>
</table>
```

### G. Flowchart (Trust Structure Overview)
```html
<div class="flowchart">
  <div class="flow-stage active-now">          <!-- .active-now = the stage in effect right now -->
    <div class="stage-label">[Event-based title, e.g. "Now — Both Grantors Living"]</div>
    <div class="stage-content">[text] <span class="section-ref">§X.XX</span></div>
  </div>
  <div class="flow-arrow" aria-hidden="true"></div>
  <div class="flow-branch">
    <div class="flow-stage"><div class="stage-label">[e.g. "Marital Trust"]</div><div class="stage-content">...</div></div>
    <div class="flow-stage family-trust"><div class="stage-label">[e.g. "Family Trust"]</div><div class="stage-content">...</div></div>
  </div>
  <div class="flow-arrow" aria-hidden="true"></div>
  <div class="flow-stage children"><div class="stage-label">[e.g. "Children's Shares"]</div><div class="stage-content">...</div></div>
</div>
```
Stage titles name the *event* ("First Death", "Family Trust", "Now — Both Grantors Living") — never a vague category label ("Stage 1", "Active Now" on its own). Titles render at 15px sentence-case with a small colored dot marker; body text indents beneath.

### H. Banners — ALWAYS `banner` + a type, each with its own icon
```html
<div class="banner warning-banner"><svg class="ic" …triangle…></svg><div><strong>[Label:]</strong> [text]</div></div>
<div class="banner flag-banner"><svg class="ic" …octagon…></svg><div><strong>[Label:]</strong> [text]</div></div>
<div class="banner info-banner"><svg class="ic" …info circle…></svg><div><strong>[Label:]</strong> [text]</div></div>
```
- `warning-banner` (amber + triangle) — action needed / caution.
- `flag-banner` (red + octagon) — stale/superseded document, conflict, critical issue.
- `info-banner` (teal + info circle) — clarifying note.
Writing the type class without `banner` breaks the icon/flex layout — always pair them.

### I. Inline formatting
- Amounts/fractions: `<span class="amt">$100,000</span>` / `<span class="amt">1/3</span>`
- Lapses: `<span class="amt-lapse">LAPSES if deceased</span>` · Inapplicable: `<span class="na">N/A — [reason]</span>`
- Missing: `<span class="not-found">[NOT FOUND — verify in original document]</span>`
- Citation on every material fact: `<span class="section-ref">§X.XX</span>` (Wills: `Art. Three`; personal docs: `POA Art. One`)

### J. Two-column (mirror/paired RLTs only)
Set `<body data-view="both">`. Two-column guides get two intentional toolbar rows instead of one crowded, unpredictably-wrapping row — `.toolbar-inner.toolbar-row` draws a thin rule between them. **Row 1** is View (the primary way to navigate a mirror-trust guide) + Print, since Print is the one action that matters regardless of which column view is active. **Row 2** is the same Show/filters + Expand/Collapse group every single-column guide already has (Part 4.C) — copy it verbatim, just drop its own `print-btn` since Print now lives on row 1 only, never both.
```html
<div class="toolbar-strip">
  <div class="toolbar-inner toolbar-row">
    <span class="label">View:</span>
    <button type="button" class="toolbar-btn view-btn active" aria-pressed="true" onclick="setView('both', this)">Both</button>
    <button type="button" class="toolbar-btn view-btn" aria-pressed="false" onclick="setView('g1', this)">[Grantor 1]'s Trust</button>
    <button type="button" class="toolbar-btn view-btn" aria-pressed="false" onclick="setView('g2', this)">[Grantor 2]'s Trust</button>
    <button type="button" class="toolbar-btn view-btn" aria-pressed="false" onclick="setView('same', this)">Identical Only</button>
    <button type="button" class="toolbar-btn print-btn" onclick="window.print()">
      <svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v4H6z"/><path d="M4 8h16a2 2 0 0 1 2 2v6h-4v-3H6v3H2v-6a2 2 0 0 1 2-2zm14 3a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/><path d="M6 14h12v7H6z"/></svg>
      Print / PDF
    </button>
  </div>
  <div class="toolbar-inner toolbar-row">
    <span class="label">Show:</span>
    <button type="button" class="toolbar-btn active" data-filter aria-pressed="true" onclick="filterSections('all', this)">All Sections</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('overview', this)">Overview</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('trustee', this)">Trustee</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('distribution', this)">Distributions</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('lifecycle', this)">Lifecycle</button>
    <button type="button" class="toolbar-btn" data-filter aria-pressed="false" onclick="filterSections('legal', this)">Legal / Admin</button>
    <span class="toolbar-sep" aria-hidden="true">|</span>
    <button type="button" class="util-btn" onclick="expandAll()">Expand all</button>
    <button type="button" class="util-btn" onclick="collapseAll()">Collapse all</button>
  </div>
</div>
```
Inside a section body use one of:
```html
<div class="two-col">
  <div class="col col-g1"><div class="col-head">[Grantor 1]</div>[content]</div>
  <div class="col col-g2"><div class="col-head">[Grantor 2]</div>[content]</div>
</div>
<div class="identical-row"><span class="badge-identical">IDENTICAL</span><div>[shared content]</div></div>
```
"Grantor 1" is whoever is named first in the preamble. `setView('same')` shows only `.identical-row` blocks; `g1`/`g2` collapse to that grantor's column while keeping identical rows.

### K. Footer (VERBATIM left cell + byline + disclaimer)
```html
<div class="page-footer">
  <div class="footer-row">
    <span>Matt Powell | Cerity Partners, LLC | 53 State St, 39th Floor, Boston, MA 02109</span>
    <span class="attrib">Built by Matt Powell · BOS2 · Prepared [month year]</span>
  </div>
  <div class="footer-disclaimer">This guide summarizes the referenced estate planning documents for advisor and client reference. The executed documents control in all cases; this is not legal advice. Confirm any action with counsel.</div>
</div>
```

---

## Part 5 — Assembly rules

**`data-cat` on every `.faq-section`** (drives color + filter). Mapping:

| data-cat | Color (colorblind-safe) | Sections |
|---|---|---|
| `overview` | Navy | Quick-Ref context, Flowchart, Family Info, Basic Info, Will Overview, Guardian |
| `trustee` | Teal | Trustee Succession, Trust Protector, Executor/PR Succession, Durable POA |
| `lifecycle` | Rust | Incapacity, Administration Upon Death / Termination, Marital Trust, Health Care Proxy |
| `distribution` | Brown | All distribution sections, Specific Bequests, Residuary/Pour-Over, Tangible Property, Taxes |
| `legal` | Clay grey | Administrative, Protective, Duration, Key Definitions, HIPAA, "How Documents Work Together" |

(The Quick Reference is a `.quick-ref` block, not a `.faq-section`, so it has no `data-cat` and always stays visible.)

**Open / closed defaults** (a section's `aria-expanded` = its body's `.open`):

| Position | Section header | First question | Others |
|---|---|---|---|
| §1 Quick Reference | (not collapsible) | — | — |
| §2 | `aria-expanded="true"` + body `.open` | open | closed |
| §3 – §4 | `aria-expanded="true"` + body `.open` | closed | closed |
| §5 onward | `aria-expanded="false"` (no `.open`) | closed | closed |

**Section numbering.** Quick Reference is §1; the first collapsible section is §2; continue sequentially. Number every section you emit; omit inapplicable ones (no gaps).

**Icons, not emoji.** Never place an emoji (⚠ 🖨 ▶ ▼ ✅ ❌ ✓ etc.) in markup. Use the Part 4.A SVG icons and CSS `.chevron`/`.flow-arrow`. The only bare glyphs permitted are `|` in `.toolbar-sep`, `·` in the byline/subtitle, and `&#8592;` in the `.crumb`.

**Fonts + logo.** Include the `<meta author>`/comment byline tags (Part 1) — no Google Fonts `<link>` is needed or wanted; the font-family stacks already fall through to system fonts, per the Part 1 note. Insert the logo by reading `references/cerity-logo.svg` and pasting its inline `<svg>` markup verbatim (add class `hdr-logo`) — never as an `<img>`/`data:` URI, since the hosting platform's CSP silently blocks those.

**Do not rename.** Class names, function names, `data-cat`/`data-view`/`data-filter`, and the four `setView` modes (`g1`,`g2`,`both`,`same`) are fixed. The question caret uses the same `.chevron` class as section headers (no separate `q-chevron`).

**No fabrication.** If a provision isn't in the document, write `<span class="not-found">[NOT FOUND — verify in original document]</span>` and list it in the post-output notes.

---

## Part 6 — Family Estate Plan Binder (index page)

The binder index is a panel-based page (no collapsible sections, no `<script>`). It shares the Cerity masthead, palette, icons, and fonts. **Copy the `<style>` block below verbatim.** Save as `[FamilyName]_Estate_Plan_Index.html` alongside the individual guides; link with relative paths.

### Binder `<style>` block (VERBATIM)

```html
<style>
  :root {
    --cobalt: #293340; --fiord: #3A5772; --fiord-l: #61798E;
    --clay: #5C574D; --clay-l: #6F665A; --desert: #D7C8B6; --vellum: #F4F1EE;
    --tradewind: #5FC3B1; --mandarin: #D26431; --white: #fff;
    --cat-overview: #344D63; --cat-trustee: #2f7d6e; --cat-lifecycle: #b5561f;
    --border: #D7C8B6; --bg: #F4F1EE; --ink: #293340;
    --warn-bg: #fdf1e3; --warn-bd: #D26431; --warn-tx: #8a3d16;
    --flag-bg: #fbe9e4; --flag-bd: #c0492a; --flag-tx: #8f2f18;
    --info-bg: #e3f2ee; --info-bd: #2f7d6e; --info-tx: #1f5147;
    --maxw: 1240px;   /* matches the guide's --maxw so header/main widths line up when linked together */
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'DM Sans', system-ui, 'Segoe UI', Arial, sans-serif; font-size: 15px; line-height: 1.6; background: var(--bg); color: var(--ink); }
  .ic { width: 1em; height: 1em; display: inline-block; vertical-align: -0.125em; flex-shrink: 0; fill: currentColor; }

  .page-header { background: var(--cobalt); color: white; padding: 13px 0 12px; }
  .hdr-inner { max-width: var(--maxw); margin: 0 auto; padding: 0 24px; }
  .hdr-top { display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
  .hdr-main { display: flex; align-items: center; gap: 14px; }
  .hdr-logo, .hdr-logo.cp-logo, .hdr-main > svg { height: 42px; width: auto; color: #fff; }
  .hdr-div { width: 1px; height: 46px; background: rgba(255,255,255,.22); }
  .hdr-text { display: flex; flex-direction: column; gap: 4px; }
  .hdr-eyebrow { font-size: 11.5px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; color: var(--tradewind); }
  .hdr-title { font-family: 'DM Sans', system-ui, sans-serif; font-size: 27px; font-weight: 700; color: white; line-height: 1.05; }
  .hdr-dates { font-size: 12px; color: rgba(255,255,255,.55); text-align: right; }
  .context-banner { display: inline-flex; align-items: flex-start; gap: 8px; margin-top: 12px; background: #fbeeea; color: var(--flag-tx); border: 1px solid #f0d2c8; border-radius: 8px; padding: 9px 14px; font-size: 12.5px; font-weight: 600; }
  .context-banner .ic { color: var(--flag-tx); }

  main { max-width: var(--maxw); margin: 24px auto; padding: 0 24px 60px; }

  .panel { background: white; border-radius: 8px; border: 1px solid var(--border); box-shadow: 0 1px 4px rgba(41,51,64,.06); margin-bottom: 20px; overflow: hidden; }
  .panel-header { padding: 13px 20px; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: white; }
  .panel-header.overview { background: var(--cat-overview); }
  .panel-header.trustee { background: var(--cat-trustee); }
  .panel-header.lifecycle { background: var(--cat-lifecycle); }
  .panel-header.flag { background: var(--mandarin); }
  .panel-body { padding: 16px 20px; }

  .data-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
  .data-table th { background: var(--vellum); color: var(--clay); font-weight: 700; padding: 9px 12px; text-align: left; border-bottom: 2px solid var(--desert); }
  .data-table td { padding: 9px 12px; border-bottom: 1px solid #f0ede8; vertical-align: top; }
  .data-table tr:last-child td { border-bottom: none; }
  .data-table tr:hover td { background: #faf8f5; }
  .data-table a { color: var(--fiord); text-decoration: none; font-weight: 600; }
  .data-table a:hover { text-decoration: underline; }

  .pill { display: inline-block; border-radius: 20px; padding: 2px 10px; font-size: 11.5px; font-weight: 700; letter-spacing: .03em; }
  .pill-active { background: #dbeee9; color: #1f5147; }
  .pill-revocable { background: #e4ebf1; color: #344D63; }
  .pill-irrevocable { background: #f7e2d6; color: #8a3d16; }
  .pill-super { background: #efe9e1; color: var(--clay); }

  .person { font-weight: 700; color: var(--cat-overview); }
  .role-list { margin: 4px 0 0 0; padding-left: 18px; font-size: 13px; }
  .role-list li { margin-bottom: 2px; }
  .deceased { color: var(--mandarin); font-weight: 600; }

  .flow-timeline { display: flex; flex-direction: column; gap: 0; }
  .flow-row { display: grid; grid-template-columns: 150px 1fr; gap: 0; border-bottom: 1px solid #efe9e1; }
  .flow-row:last-child { border-bottom: none; }
  .flow-when { background: var(--vellum); padding: 12px 14px; font-weight: 700; font-size: 12.5px; color: var(--cat-overview); border-right: 3px solid var(--cat-overview); }
  .flow-when.done { color: var(--mandarin); border-right-color: var(--mandarin); }
  .flow-what { padding: 12px 16px; font-size: 13px; }
  .flow-what .doc { font-weight: 600; color: var(--cat-trustee); }

  .banner { border-radius: 4px; padding: 10px 16px; margin: 0 0 10px; font-size: 13.5px; display: flex; gap: 9px; align-items: flex-start; }
  .banner:last-child { margin-bottom: 0; }
  .banner .ic { margin-top: 2px; }
  .warning-banner { background: var(--warn-bg); border-left: 4px solid var(--warn-bd); }
  .warning-banner .ic, .warning-banner strong { color: var(--warn-tx); }
  .flag-banner { background: var(--flag-bg); border-left: 4px solid var(--flag-bd); }
  .flag-banner .ic, .flag-banner strong { color: var(--flag-tx); }
  .info-banner { background: var(--info-bg); border-left: 4px solid var(--info-bd); }
  .info-banner .ic, .info-banner strong { color: var(--info-tx); }
  .section-ref { font-size: 11px; background: #e9e3da; color: var(--clay); border-radius: 3px; padding: 1px 5px; margin-left: 4px; font-family: ui-monospace, monospace; white-space: nowrap; }

  .page-footer { border-top: 3px solid var(--desert); padding: 16px 40px; background: white; font-size: 11.5px; color: var(--clay); display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; }

  @media (max-width: 640px) { .flow-row { grid-template-columns: 1fr; } .flow-when { border-right: none; border-bottom: 2px solid var(--cat-overview); } }
  @media print { .page-header { -webkit-print-color-adjust: exact; print-color-adjust: exact; } .panel { break-inside: avoid; } }
</style>
```

### Binder body skeleton
```
<body>
  <div class="page-header">
    <div class="hdr-inner">
      <div class="hdr-top">
        <div class="hdr-main">
          <!-- PASTE inline <svg>…</svg> from references/cerity-logo.svg here, verbatim, with class="hdr-logo" added -->
          <div class="hdr-div"></div>
          <div class="hdr-text">
            <span class="hdr-eyebrow">Estate Plan Binder</span>
            <span class="hdr-title">[Family] Family Estate Plan</span>
          </div>
        </div>
        <div class="hdr-dates">[location] · Prepared [month year]</div>
      </div>
      <div class="context-banner"><svg class="ic" …triangle…></svg>[family-wide status]</div>
    </div>
  </div>
  <main>
    [Panel: Documents in This Plan]      (panel-header overview)
    [Panel: Who's Who]                   (panel-header trustee)
    [Panel: How the Plan Works Together] (panel-header lifecycle)
    [Panel: Action Items Across the Plan](panel-header flag)
  </main>
  <div class="page-footer"><span>Matt Powell | Cerity Partners, LLC | 53 State St, 39th Floor, Boston, MA 02109</span><span>[Family] Estate Plan — Prepared [month year]</span></div>
</body>
```

### Binder components

**Document inventory** (relative links + status pills `pill-active`/`pill-revocable`/`pill-irrevocable`/`pill-super`):
```html
<div class="panel">
  <div class="panel-header overview">Documents in This Plan</div>
  <div class="panel-body" style="padding:0;">
    <table class="data-table">
      <tr><th>Owner</th><th>Document</th><th>Type</th><th>Dated</th><th>Status</th><th>Guide</th></tr>
      <tr><td>[owner]</td><td>[doc]</td><td>[type]</td><td>[date]</td>
        <td><span class="pill pill-active">Active</span> <span class="pill pill-irrevocable">Now Irrevocable</span></td>
        <td><a href="[Owner]_[Doc]_FAQ.html">Open &#8594;</a></td></tr>
    </table>
  </div>
</div>
```

**Who's Who** (roles collated across every document; deceased → `.person.deceased` + `.deceased` note):
```html
<div class="panel">
  <div class="panel-header trustee">Who's Who — Roles Across All Documents</div>
  <div class="panel-body" style="padding:0;">
    <table class="data-table">
      <tr><th style="width:210px;">Person</th><th>Roles across the plan</th></tr>
      <tr><td><span class="person">[Name]</span><br><span style="font-size:12px;color:#8a857c;">[relation]</span></td>
        <td><ul class="role-list"><li>[role — document]</li></ul></td></tr>
    </table>
  </div>
</div>
```

**Family timeline** (a completed stage → `.flow-when.done` + check icon):
```html
<div class="panel">
  <div class="panel-header lifecycle">How the Plan Works Together — Family Timeline</div>
  <div class="panel-body">
    <div class="flow-timeline">
      <div class="flow-row"><div class="flow-when">[stage]</div><div class="flow-what">[what happens] <span class="doc">Documents:</span> [docs]</div></div>
      <div class="flow-row"><div class="flow-when done">[stage] <svg class="ic" …check…></svg></div><div class="flow-what">…</div></div>
    </div>
  </div>
</div>
```

**Action items across the plan** (aggregate the warning/flag items from the individual guides):
```html
<div class="panel">
  <div class="panel-header flag">Action Items Across the Plan</div>
  <div class="panel-body">
    <div class="banner flag-banner"><svg class="ic" …octagon…></svg><div><strong>[item]</strong> [detail] <span class="section-ref">[Guide §]</span></div></div>
    <div class="banner warning-banner"><svg class="ic" …triangle…></svg>…</div>
    <div class="banner info-banner"><svg class="ic" …info circle…></svg>…</div>
  </div>
</div>
```

**Binder notes:** panel-header color classes mirror the guide `data-cat` palette. Every cross-link is a relative path to a file delivered in the same folder. Add the `.crumb` back-to-index banner (Part 4.B) to each individual guide. Use the SVG check for a completed stage — never a `✓` glyph.
