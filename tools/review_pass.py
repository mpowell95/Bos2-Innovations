#!/usr/bin/env python3
"""
Apply Matt's review pass over the built toolkit.

Two kinds of change, both driven by the same review:

1. Copy. The Library and the builder had accumulated a running commentary —
   notes explaining that optional things are optional, that a slide library is
   a slide library, that the Title Page is always included. None of it told a
   reader something they could not see on screen, and all of it competed with
   the content for attention. Those lines come out.

2. Behaviour. Two real defects:
   - buildChecklist() rebuilt the section rows from scratch on every visit to
     the Build tab and restored only the slide checkboxes, so the sections
     themselves silently unchecked and presentationOrder was recomputed from an
     empty set. A loaded template looked applied (slides checked) but produced
     an empty deck. Section state is now restored the same way slide state is.
   - "Questions to Ask When Choosing an Advisor" is advisor prep — the Library
     page says to think about the questions, not present them — but it sat in
     the builder with nothing saying so. It now carries a tag.

Usage:
    python3 review_pass.py IN.html OUT.html
"""

import argparse
import sys

# (label, old, new). Every old must appear exactly once: these strings are
# hand-picked out of a 13M-char file, and a silent miss or a stray second hit
# is how a build quietly keeps the thing it was meant to drop.
EDITS = []


def cut(label, text):
    EDITS.append((label, text, ""))


def sub(label, old, new):
    EDITS.append((label, old, new))


# --- Page title -----------------------------------------------------------

# The browser tab and any bookmark. Leads with what it is, since the tab strip
# truncates from the right.
sub("retitle the page",
    "<title>Cerity Partners — Prospect Meeting Toolkit</title>",
    "<title>Prospect Meeting Toolkit - CP Bos2</title>")

# --- Templates bar --------------------------------------------------------

# The built-in is just "Wealth Management Template"; tagging it as built-in
# raises a distinction the advisor has no use for.
sub("drop the (built-in) dropdown tag",
    "built.map(function(n){ return opt(n, '(built-in)'); }).join('')",
    "built.map(function(n){ return opt(n, ''); }).join('')")

# Applying the shared default needs no announcement — the checkboxes filling in
# is the feedback. A template the advisor set themselves still confirms, since
# there it tells them their own setting took effect.
sub("stop announcing the built-in template",
    """    say(store.def === name ? 'Applied your default template, "' + name + '".'
                           : 'Started from the ' + name + '.');""",
    """    if (store.def === name) say('Applied your default template, "' + name + '".');
    else if (!note.classList.contains('warn')) say('');""")

sub("shorten the templates help popover",
    """<div class="tpl-help-pop" id="tplHelpPop" hidden>
The Wealth Management Template is built into this tool and available to everyone.
It loads automatically, and you can change anything after it does.
<br><br>
Templates you save yourself are stored on this browser only — they are not shared
with other advisors, and will not follow you to another computer.
</div>""",
    """<div class="tpl-help-pop" id="tplHelpPop" hidden>
Custom templates exist <strong>only</strong> on this browser.
</div>""")

# Four bare underlined links reading as one undifferentiated run. Same actions,
# given shape: Apply is the one you press, Delete is the one to be careful with.
sub("give the template actions real buttons",
    """<button type="button" class="linklike" id="tplApply">Apply</button>
<button type="button" class="linklike" id="tplSave">Save current…</button>
<button type="button" class="linklike" id="tplDefault">Set as default</button>
<button type="button" class="linklike" id="tplDelete">Delete</button>""",
    """<div class="tpl-actions">
<button type="button" class="tplbtn primary" id="tplApply">Apply</button>
<button type="button" class="tplbtn" id="tplSave">Save current…</button>
<button type="button" class="tplbtn" id="tplDefault">Set as default</button>
<button type="button" class="tplbtn danger" id="tplDelete">Delete</button>
</div>""")

# --- Builder copy ---------------------------------------------------------

cut("drop the builder intro",
    """<p class="builder-intro">Check the sections you want available for this meeting, then launch a clean full-screen walkthrough. You can jump between sections live, or click through in order — nothing outside your selection will show.</p>
""")

cut("drop the title-page styling note",
    """<p class="tpf-hint">Styled after the official Cerity Partners cover design. This is always shown first when you launch, ahead of whatever sections you select below.</p>
""")

# The deck total directly below already says the Title Page and Disclosure are
# always added, and says it against a number the advisor can check.
cut("drop the duplicate title-page/disclosure note",
    """<p class="order-hint" style="margin-top:16px;">Every presentation automatically opens with the Title Page and closes with Disclosure — neither appears above since they're not optional.</p>

""")

# --- Library copy ---------------------------------------------------------

cut("drop the slide-library attribution",
    """ <span style="font-weight:400; font-size:13px; color:var(--clay);">(from the Cerity Partners Overview Slide Library)</span>""")

cut("drop the Why Cerity optional note",
    """<p class="section-sub advisor-note">Everything in this section — Who We Are, Why Clients Choose Us, and 14 additional slides — is optional. Go to Build a Presentation to choose which ones to include; none are selected by default.</p>
""")

for n in (32, 8, 4, 23):
    cut(f"drop the '{n} slides available' note",
        f"""<p class="section-sub advisor-note">{n} slides available from the Cerity Partners Overview Slide Library. Go to Build a Presentation to choose which ones to include — none are selected by default — check the ones you want to include.</p>
""")

cut("drop the onboarding three-documents note",
    """<p class="section-sub advisor-note">Three documents make up the onboarding process — Welcome &amp; Onboarding Steps, Client's First Year, and the Planning Checklist. All are optional; go to Build a Presentation to choose which ones to include.</p>

""")

cut("drop the team roster note",
    """<p class="section-sub team-picker-note">The Boston 2 team, for reference. To feature specific colleagues in a presentation, select them from the "Meet Your Team" row in Build a Presentation.</p>

""")

cut("drop the reference-documents note",
    """<p class="section-sub advisor-note">Full one-pagers and reference documents built directly into the toolkit — no external link needed. Each is optional and individually selectable in Build a Presentation, the same way the onboarding documents work.</p>
""")

# The three orange flags. The fee note restates that a published schedule is a
# published schedule; the other two are notes-to-self from building the toolkit
# that were never meant for the advisor reading it.
cut("drop the fee-schedule flag",
    """<div class="flag"><span class="label">Confirm before external use</span>Cross-check against the current Form ADV Part 2A, Item 5 and with Compliance before quoting to a prospect, since fees are negotiable and may vary by engagement.</div>
""")

cut("drop the data-gap flag",
    """<div class="flag" style="margin-top:16px;"><span class="label">Data gap</span>Full biographies and confirmed headshots are now in place for all 24 Boston 2 colleagues, sourced directly from ceritypartners.com.</div>
""")

cut("drop the source-note flag",
    """<div class="flag"><span class="label">Source note</span>Bios compiled from ceritypartners.com/team profile pages and the internal Boston 2 Team roster. Confirm a bio is current before a meeting — advisor bios are updated periodically on the website.</div>
""")

# --- Layout ---------------------------------------------------------------

# Everything else on the page runs the full content column. This one rule made
# roughly one paragraph in seven stop two thirds of the way across, which reads
# as a mistake rather than as a measure.
sub("let intro paragraphs use the content column",
    ".section-sub{ font-size:13.5px; color:var(--clay); max-width:640px; margin:-14px 0 24px; }",
    ".section-sub{ font-size:13.5px; color:var(--clay); margin:-14px 0 24px; }")

# The resources tables had one 30% column and two that fought over the rest, so
# a long "Best Use" squeezed "Open document" into a two-line stack. Fixed layout
# with a reserved link column instead: the link never wraps, the description
# takes whatever is left, and the rows breathe.
sub("re-space the resources tables",
    """.materials td{ padding:12px 10px; border-bottom:1px solid var(--rule); color:#3d4a56; vertical-align:top; }
.materials td.doc{ font-weight:600; color:var(--cobalt); width:30%; }""",
    """.materials td{ padding:14px 16px; border-bottom:1px solid var(--rule); color:#3d4a56;
vertical-align:top; line-height:1.55; }
.materials td.doc{ font-weight:600; color:var(--cobalt); }
.materials{ table-layout:fixed; }
.materials th:first-child, .materials td:first-child{ width:26%; padding-left:0; }
.materials th:last-child, .materials td:last-child{ width:150px; padding-right:0; white-space:nowrap; }""")

CSS = """
/* Template actions: shaped buttons rather than a run of underlined links. */
.tpl-row{ padding-right:26px; }
.tpl-actions{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.tplbtn{
appearance:none; cursor:pointer; white-space:nowrap;
font-family:'Helvetica Neue', Arial, sans-serif; font-size:12px; letter-spacing:.02em; line-height:1;
padding:8px 14px; border-radius:20px;
border:1px solid var(--rule); background:#fff; color:var(--fiord);
transition:background .12s ease, color .12s ease, border-color .12s ease;
}
.tplbtn:hover{ border-color:var(--fiord-light); background:var(--vellum); }
.tplbtn.primary{ background:var(--fiord); border-color:var(--fiord); color:#fff; }
.tplbtn.primary:hover{ background:var(--cobalt); border-color:var(--cobalt); }
.tplbtn.danger:hover{ background:#fdf5ef; border-color:#e3b48b; color:#a5471a; }
.tplbtn:focus-visible{ outline:2px solid var(--tradewind); outline-offset:2px; }

/* Advisor-prep sections carry the same weight, and sit in the same place, as
   the dense-content ones. */
.builder-item .tag.prep{ margin-left:auto; background:rgba(107,77,89,0.13); color:var(--plum);
font-size:10px; padding:3px 9px; border-radius:20px; font-family:'Helvetica Neue', Arial, sans-serif; }
.builder-item .tag.prep + .row-badge{ margin-left:8px; }

/* A wrapped tag should sit flush under the title, not indented by the gap that
   separates it from the title when they share a line. */
.materials td.doc .tag{ margin-left:0; margin-right:6px; }
"""

# --- Behaviour ------------------------------------------------------------

# The Library page tells the advisor to think about these questions rather than
# present them; the builder should not silently offer them as a section.
sub("tag Questions to Ask as advisor prep",
    '<section class="content-block" id="sec-advisorquestions" data-title="Questions to Ask When Choosing an Advisor" data-category="Firm &amp; Prospecting">',
    '<section class="content-block" id="sec-advisorquestions" data-title="Questions to Ask When Choosing an Advisor" data-category="Firm &amp; Prospecting" data-buildtag="Advisor prep — not for presenting">')

sub("render the per-section builder tag",
    """const id=b.id, title=b.dataset.title, isDense = b.dataset.default==='off';
const row=document.createElement('label');
row.className='builder-item';
row.innerHTML = '<input type="checkbox" value="'+id+'"><span>'+title+'</span>'+
(isDense ? '<span class="tag stale">Dense — screen not recommended</span>' : '');""",
    """const id=b.id, title=b.dataset.title, isDense = b.dataset.default==='off';
// A section can name its own caveat; otherwise the dense-content one applies.
const tag = b.dataset.buildtag
? '<span class="tag prep">'+b.dataset.buildtag+'</span>'
: (isDense ? '<span class="tag stale">Dense — screen not recommended</span>' : '');
// Rebuilt on every visit to the Build tab, so the section's own checkbox has to
// be restored from the order the same way its slides are restored from
// selectedGallerySlides. Without this the sections silently unchecked and a
// loaded template produced an empty deck.
const wasChosen = presentationOrder.indexOf(id) !== -1 ? ' checked' : '';
const row=document.createElement('label');
row.className='builder-item';
row.innerHTML = '<input type="checkbox" value="'+id+'"'+wasChosen+'><span>'+title+'</span>'+tag;""")

# Rebuilding must not reorder or drop a deck the advisor already arranged: keep
# the existing order, and only append sections that are newly checked.
sub("preserve the deck across rebuilds",
    """// initialize order from whatever is checked by default (section-level checkboxes only)
presentationOrder = Array.from(container.querySelectorAll('.builder-item > input:checked')).map(i=>i.value);""",
    """// Keep the order the advisor arranged; only append sections checked by default
// that are not already in it (section-level checkboxes only).
const checkedNow = Array.from(container.querySelectorAll('.builder-item > input:checked')).map(i=>i.value);
presentationOrder = presentationOrder.filter(id=>checkedNow.includes(id))
.concat(checkedNow.filter(id=>!presentationOrder.includes(id)));""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()

    html = open(args.input, encoding="utf-8").read()
    before = len(html)

    for label, old, new in EDITS:
        n = html.count(old)
        if n != 1:
            sys.exit(f"[{label}] expected 1 match, found {n}")
        html = html.replace(old, new, 1)
        print(f"  ok  {label}")

    cutpt = html.find("</style>")
    if cutpt == -1:
        sys.exit("no </style> to extend")
    html = html[:cutpt] + CSS + html[cutpt:]

    open(args.output, "w", encoding="utf-8").write(html)
    print(f"review pass applied -> {before/1e6:.2f}M -> {len(html)/1e6:.2f}M chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
