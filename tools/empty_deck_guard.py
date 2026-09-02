#!/usr/bin/env python3
"""
Stop the builder from launching a presentation that contains nothing.

Sections marked data-gallery-only contribute only the individual slides ticked
inside them, never the section itself. Tick two of those, pick no slides, and
launchBtn's guard still passes because it only tests
`presentationOrder.length === 0` — which is not zero. The result is a deck of
just the title page and the disclosure, launched without a word, while the
builder's "On Deck" list shows those sections as though they were included.

This adds the check the guard is missing: work out what expandForPresentation
will actually produce, and

  * block the launch when nothing at all would be presented, naming the sections
    and saying what to do about it;
  * otherwise, if some sections would contribute nothing while others are fine,
    confirm before continuing, since ticking a gallery-only section and choosing
    no slides from it is never deliberate.

The listener runs on document in the capture phase. A listener added to the
button itself would fire after the existing one, because listeners on the target
run in registration order regardless of the capture flag.

Usage:
    python3 empty_deck_guard.py IN.html OUT.html
"""

import argparse
import sys

SCRIPT = r"""
<script>
// ---------------------------------------------------------------------------
// Guard against launching an empty presentation. See empty_deck_guard.py.
// ---------------------------------------------------------------------------
(function(){
  function selected(id){
    return !!document.querySelector('input[type="checkbox"][value="' + id + '"]:checked');
  }

  // Mirrors expandForPresentation: a gallery section yields its ticked slides,
  // plus itself unless it is gallery-only.
  function audit(){
    var chosen = [].slice.call(
      document.querySelectorAll('#builderList .builder-item > input:checked'));
    var total = 0, empties = [];
    chosen.forEach(function(input){
      var block = document.getElementById(input.value);
      if (!block) return;
      if (block.dataset.gallery === 'true'){
        var slides = [].slice.call(block.querySelectorAll('.ppt-slide-card'))
                       .filter(function(card){ return card.id && selected(card.id); }).length;
        var self = block.dataset.galleryOnly === 'true' ? 0 : 1;
        if (slides + self === 0){
          empties.push(block.dataset.title || input.value);
        }
        total += slides + self;
      } else {
        total += 1;
      }
    });
    return {total: total, empties: empties};
  }

  document.addEventListener('click', function(e){
    var btn = e.target.closest && e.target.closest('#launchBtn');
    if (!btn) return;
    var r = audit();
    if (r.total === 0){
      e.stopPropagation();
      e.preventDefault();
      alert('Nothing would be presented.\n\n' +
            (r.empties.length
              ? 'These sections only include the individual slides you tick:\n  • ' +
                r.empties.join('\n  • ') + '\n\n'
              : '') +
            'Expand each one in the checklist above, tick the slides you want, ' +
            'then launch again.');
      return;
    }
    if (r.empties.length){
      var ok = confirm('No slides are ticked in:\n  • ' + r.empties.join('\n  • ') +
                       '\n\nThose sections will not appear in the presentation. Continue anyway?');
      if (!ok){ e.stopPropagation(); e.preventDefault(); }
    }
  }, true);
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()

    html = open(args.input, encoding="utf-8").read()
    if 'id="launchBtn"' not in html:
        sys.exit("no launchBtn in this file")
    if "#builderList .builder-item > input:checked" in html:
        sys.exit("guard already present")

    # jsPDF's own source contains "</body>" inside string literals, so a
    # replace-first would splice this script into the middle of the library and
    # truncate it. Anchor to the document's real closing tag instead.
    cut = html.rfind("</body>")
    if cut == -1:
        sys.exit("no </body> to anchor to")
    html = html[:cut] + SCRIPT + "\n" + html[cut:]
    open(args.output, "w", encoding="utf-8").write(html)
    print(f"guard added -> {len(html)/1e6:.2f}M chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
