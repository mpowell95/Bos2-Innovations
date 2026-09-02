#!/usr/bin/env python3
"""
Show how much has been selected, before the presentation is built.

Two counts:

  * Each gallery picker headed "16 items available", a fixed number that never
    reacted to anything. It now reads "2 of 16 items selected" and updates live.
  * A running total above the Launch button, so the length of the deck is
    visible before committing to it. It counts what expandForPresentation will
    actually produce, including the Title Page and Disclosure that are always
    added, and excluding gallery-only sections that contribute nothing.

Both hang off renderOrderList(), which every path that changes a selection
already calls — the checkbox handlers, Select All, Clear, and adding or removing
a section. The Select All buttons set .checked directly without dispatching an
event, so listening for change events would have missed them.

Usage:
    python3 deck_counts.py IN.html OUT.html
"""

import argparse
import sys

HEAD_OLD = """nested.innerHTML = '<div class="contact-picker-head"><h3>'+cards.length+' items available</h3><div class="cat-actions">'+"""
HEAD_NEW = """nested.innerHTML = '<div class="contact-picker-head"><h3 class="gp-count" data-total="'+cards.length+'">0 of '+cards.length+' items selected</h3><div class="cat-actions">'+"""

TOTAL_MARKUP = """<p class="deck-total" id="deckTotal"></p>"""
LAUNCH_ANCHOR = """<button id="launchBtn" class="launch-btn">"""

CSS = """
/* Running deck length, shown before the presentation is launched. */
.deck-total{
margin:18px 0 10px; padding:12px 16px;
border:1px solid var(--rule); border-left:3px solid var(--tradewind);
border-radius:6px; background:var(--vellum);
font-family:'Helvetica Neue', Arial, sans-serif; font-size:14px; color:#33404d;
}
.deck-total strong{ font-size:16px; color:var(--cobalt); }
.deck-total .dt-note{ display:block; margin-top:3px; font-size:12px; color:var(--clay); }

/* How much is selected in a section, readable while it is collapsed. */
.row-badge{
margin-left:auto; flex-shrink:0;
background:var(--tradewind); color:#fff;
font-family:'Helvetica Neue', Arial, sans-serif; font-size:10.5px; font-weight:600;
letter-spacing:.02em; padding:3px 10px; border-radius:20px;
}
.builder-item .tag.stale + .row-badge{ margin-left:8px; }
"""

SCRIPT = r"""
<script>
// ---------------------------------------------------------------------------
// Selection counts. See deck_counts.py.
// ---------------------------------------------------------------------------
(function(){
  // A collapsed section hides its picker, and with it the only sign of how much
  // was chosen there. Put the count on the row itself so it survives collapsing.
  function updateRowBadges(){
    document.querySelectorAll('#builderList .builder-item-nested').forEach(function(nested){
      var row = nested.previousElementSibling;
      if (!row || !row.classList.contains('builder-item')) return;
      var boxes = nested.querySelectorAll('.gallery-check-item input[type="checkbox"], #contactCheckboxes input[type="checkbox"]');
      if (!boxes.length) return;
      var picked = 0;
      boxes.forEach(function(b){ if (b.checked) picked++; });
      var badge = row.querySelector('.row-badge');
      if (!badge){
        badge = document.createElement('span');
        badge.className = 'row-badge';
        row.appendChild(badge);
      }
      var noun = nested.querySelector('#contactCheckboxes') ? 'colleague' : 'slide';
      badge.textContent = picked + ' ' + noun + (picked === 1 ? '' : 's');
      badge.hidden = picked === 0;
    });
  }

  function updateGalleryCounts(){
    document.querySelectorAll('.gp-count').forEach(function(h){
      var body = h.closest('.builder-item-nested');
      if (!body) return;
      var boxes = body.querySelectorAll('.gallery-check-item input[type="checkbox"]');
      var picked = 0;
      boxes.forEach(function(b){ if (b.checked) picked++; });
      h.textContent = picked + ' of ' + boxes.length + ' items selected';
    });
  }

  // Mirrors expandForPresentation, plus the Title Page and Disclosure that are
  // always added, so the number matches the deck that actually gets built.
  function deckLength(){
    var total = 0, sections = 0;
    (typeof presentationOrder !== 'undefined' ? presentationOrder : []).forEach(function(id){
      var block = document.getElementById(id);
      if (!block) return;
      if (block.dataset.gallery === 'true'){
        var slides = [].slice.call(block.querySelectorAll('.ppt-slide-card'))
          .filter(function(card){
            return card.id && document.querySelector(
              'input[type="checkbox"][value="' + card.id + '"]:checked');
          }).length;
        var self = block.dataset.galleryOnly === 'true' ? 0 : 1;
        total += slides + self;
        if (slides + self) sections++;
      } else {
        total += 1; sections++;
      }
    });
    return {slides: total + 2, sections: sections};   // + Title Page, + Disclosure
  }

  function updateDeckTotal(){
    var el = document.getElementById('deckTotal');
    if (!el) return;
    var d = deckLength();
    if (d.sections === 0){
      el.innerHTML = '<strong>Nothing selected yet.</strong>' +
        '<span class="dt-note">Check sections above to build the deck.</span>';
      return;
    }
    el.innerHTML = '<strong>' + d.slides + ' slides</strong> across ' +
      d.sections + ' section' + (d.sections === 1 ? '' : 's') +
      '<span class="dt-note">Includes the Title Page and Disclosure, which are always added.</span>';
  }

  // Every path that changes a selection calls renderOrderList — including the
  // Select All buttons, which set .checked directly and fire no event.
  if (typeof renderOrderList === 'function'){
    var original = renderOrderList;
    renderOrderList = function(){
      var r = original.apply(this, arguments);
      try { updateGalleryCounts(); updateRowBadges(); updateDeckTotal(); } catch (e){}
      return r;
    };
  }
  document.addEventListener('click', function(e){
    if (e.target.closest && e.target.closest('.modebtn'))
      setTimeout(function(){ updateGalleryCounts(); updateRowBadges(); updateDeckTotal(); }, 0);
  });
  updateGalleryCounts(); updateRowBadges(); updateDeckTotal();
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()

    html = open(args.input, encoding="utf-8").read()
    before = len(html)

    if 'id="deckTotal"' in html:
        sys.exit("counts already applied")
    if HEAD_OLD not in html:
        sys.exit("could not find the gallery picker heading")
    if LAUNCH_ANCHOR not in html:
        sys.exit("could not find the launch button")

    html = html.replace(HEAD_OLD, HEAD_NEW, 1)
    html = html.replace(LAUNCH_ANCHOR, TOTAL_MARKUP + "\n" + LAUNCH_ANCHOR, 1)

    cut = html.find("</style>")
    if cut == -1:
        sys.exit("no </style> to extend")
    html = html[:cut] + CSS + html[cut:]

    cut = html.rfind("</body>")
    if cut == -1:
        sys.exit("no </body> to anchor to")
    html = html[:cut] + SCRIPT + "\n" + html[cut:]

    open(args.output, "w", encoding="utf-8").write(html)
    print(f"counts added -> {before/1e6:.2f}M -> {len(html)/1e6:.2f}M chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
