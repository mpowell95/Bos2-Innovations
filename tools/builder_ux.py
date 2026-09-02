#!/usr/bin/env python3
"""
Builder checklist fixes.

  --plain-rows  Drop the "Aa" placeholder thumbnails.

    resolveThumb() falls back to a grey "Aa" tile for any card without a slide
    image. Four cards hit it — the three Onboarding Process sub-items and the
    New Client Welcome Email — and the tile carries no information, it just
    makes the rows tall and inconsistent with every other checklist row. Those
    cards now render as a plain checkbox + label, and a picker whose cards all
    lack images lays out as a list rather than a thumbnail grid.

  --collapsible  Let a section collapse without losing its slide selections.

    The nested slide list has no collapse control: its visibility is wired
    directly to the section checkbox. Collapsing a 23-slide section therefore
    means unchecking it, which calls removeFromOrder() and drops the section
    from the presentation. This adds a caret that toggles the list independently
    of the checkbox, so selections survive.

Usage:
    python3 builder_ux.py IN.html OUT.html --plain-rows --collapsible
"""

import argparse
import sys

# --------------------------------------------------------------------------
# --plain-rows
# --------------------------------------------------------------------------

THUMB_OLD = """const imgEl = card.querySelector('canvas.cimg');
if(imgEl) return '<canvas class="cimg" data-i="'+imgEl.dataset.i+'" role="img" aria-label=""></canvas>';
return '<div class="gci-placeholder">Aa</div>';"""

THUMB_NEW = """const imgEl = card.querySelector('canvas.cimg');
if(imgEl) return '<canvas class="cimg" data-i="'+imgEl.dataset.i+'" role="img" aria-label=""></canvas>';
// No image and no icon: show nothing rather than an "Aa" tile that says nothing.
return '';"""

ROW_OLD = """'<div class="gallery-picker-body">'+
cards.map(card=>{
const sid = card.id, title = card.dataset.title;
const thumb = resolveThumb(card);
const checked = selectedGallerySlides.has(sid) ? 'checked' : '';
return '<label class="gallery-check-item" data-title="'+title+'">'+thumb+'<span class="gci-label">'+
'<input type="checkbox" value="'+sid+'" '+checked+'><span>'+title+'</span></span></label>';
}).join('')+
'</div>';"""

ROW_NEW = """'<div class="gallery-picker-body'+(cards.some(c=>resolveThumb(c)) ? '' : ' plain-list')+'">'+
cards.map(card=>{
const sid = card.id, title = card.dataset.title;
const thumb = resolveThumb(card);
const checked = selectedGallerySlides.has(sid) ? 'checked' : '';
return '<label class="gallery-check-item'+(thumb ? '' : ' no-thumb')+'" data-title="'+title+'">'+thumb+'<span class="gci-label">'+
'<input type="checkbox" value="'+sid+'" '+checked+'><span>'+title+'</span></span></label>';
}).join('')+
'</div>';"""

PLAIN_CSS = """
/* Cards with no slide image render as ordinary checklist rows, matching
   .builder-item, instead of a thumbnail tile. */
.gallery-picker-body.plain-list{ display:block; padding:4px 16px 10px; }
.gallery-check-item.no-thumb{
flex-direction:row; align-items:center; gap:10px;
padding:9px 0; border-bottom:1px solid var(--rule);
font-size:14px; color:#33404d;
}
.gallery-picker-body.plain-list .gallery-check-item.no-thumb:last-child{ border-bottom:none; }
.gallery-check-item.no-thumb .gci-label{ align-items:center; gap:10px; }
.gallery-check-item.no-thumb input{ width:16px; height:16px; accent-color:var(--fiord); flex-shrink:0; }
"""

# --------------------------------------------------------------------------
# --collapsible
# --------------------------------------------------------------------------

# The row is a <label>, so anything inside it toggles the checkbox. The caret is
# inserted as a sibling before the label and positioned into the row's gutter.
COLLAPSE_OLD = """cb.addEventListener('change', ()=>{
if(cb.checked) addToOrder(id); else removeFromOrder(id);
if(nested) nested.style.display = cb.checked ? '' : 'none';
});"""

COLLAPSE_NEW = """if(nested){
// Collapse is independent of selection: the checkbox decides whether the
// section is in the presentation, the caret only decides whether its slide
// list is on screen. Previously the two were the same control, so collapsing
// a long section meant unchecking it and losing the section.
const caret = document.createElement('button');
caret.type = 'button';
caret.className = 'nested-caret';
caret.setAttribute('aria-label', 'Show or hide the items in this section');
caret.textContent = '▾';
row.insertAdjacentElement('beforebegin', caret);
row.classList.add('has-caret');
nested.dataset.collapsed = 'false';
function syncNested(){
const collapsed = nested.dataset.collapsed === 'true';
nested.style.display = (cb.checked && !collapsed) ? '' : 'none';
caret.style.visibility = cb.checked ? '' : 'hidden';
caret.textContent = collapsed ? '▸' : '▾';
caret.setAttribute('aria-expanded', String(!collapsed));
}
caret.addEventListener('click', (e)=>{
e.preventDefault(); e.stopPropagation();
nested.dataset.collapsed = nested.dataset.collapsed === 'true' ? 'false' : 'true';
syncNested();
});
nested.__sync = syncNested;
syncNested();
}
cb.addEventListener('change', ()=>{
if(cb.checked) addToOrder(id); else removeFromOrder(id);
if(nested){
// Reopen on re-check so the slides are visible again; selections are untouched.
if(cb.checked) nested.dataset.collapsed = 'false';
nested.__sync();
}
});"""

# "Select all" / "Clear" set display directly, which would fight the caret.
ALL_OLD = """list.querySelectorAll(':scope > .builder-item-nested').forEach(n=>{ n.style.display=''; });"""
ALL_NEW = """list.querySelectorAll(':scope > .builder-item-nested').forEach(n=>{
n.dataset.collapsed='false'; if(n.__sync) n.__sync(); else n.style.display='';
});"""

NONE_OLD = """list.querySelectorAll(':scope > .builder-item-nested').forEach(n=>{ n.style.display='none'; });"""
NONE_NEW = """list.querySelectorAll(':scope > .builder-item-nested').forEach(n=>{
if(n.__sync) n.__sync(); else n.style.display='none';
});"""

COLLAPSE_CSS = """
/* Caret that shows or hides a section's slide list without changing the
   selection. It sits outside the row's <label> so clicking it cannot toggle
   the checkbox. */
.nested-caret{
appearance:none; background:none; border:none; cursor:pointer;
font-size:11px; line-height:1; color:var(--clay);
padding:0; margin:0 0 -28px -14px; width:14px; height:14px;
position:relative; top:19px; z-index:2;
}
.nested-caret:hover{ color:var(--fiord); }
.builder-item.has-caret{ padding-left:2px; }
"""


def apply(html, old, new, label):
    if old not in html:
        sys.exit(f"could not find the source for: {label}")
    return html.replace(old, new, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--plain-rows", action="store_true")
    ap.add_argument("--collapsible", action="store_true")
    args = ap.parse_args()

    if not (args.plain_rows or args.collapsible):
        sys.exit("nothing to do: pass --plain-rows and/or --collapsible")

    html = open(args.input, encoding="utf-8").read()
    before = len(html)
    css = ""

    if args.plain_rows:
        html = apply(html, THUMB_OLD, THUMB_NEW, "resolveThumb fallback")
        html = apply(html, ROW_OLD, ROW_NEW, "gallery picker rows")
        css += PLAIN_CSS
        print("plain rows: 'Aa' placeholder removed")

    if args.collapsible:
        html = apply(html, COLLAPSE_OLD, COLLAPSE_NEW, "section checkbox handler")
        html = apply(html, ALL_OLD, ALL_NEW, "category Select all")
        html = apply(html, NONE_OLD, NONE_NEW, "category Clear")
        css += COLLAPSE_CSS
        print("collapsible: caret added, independent of the checkbox")

    cut = html.find("</style>")
    if cut == -1:
        sys.exit("no </style> to extend")
    html = html[:cut] + css + html[cut:]

    open(args.output, "w", encoding="utf-8").write(html)
    print(f"\n{before/1e6:.2f}M -> {len(html)/1e6:.2f}M chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
