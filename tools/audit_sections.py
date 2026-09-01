#!/usr/bin/env python3
"""
Look for toolkit content that is present in the file but never reaches a
presentation or a PDF.

This exists because the disclosures section shipped as a bare heading: its text
sits inside a closed <details>, which contributes no height, so the capture was
131px tall and the required disclosure language was silently dropped from every
PDF. Nothing failed and nothing logged — the page just came out empty.

For each content block it builds the same clone the exporter builds, then reports:

  chars      text in the section, including anything hidden
  renderH    height that clone actually occupies
  hidden     text sitting in display:none / visibility:hidden subtrees that are
             not on the deliberately-hidden list
  clipped    containers whose scrollHeight exceeds their clientHeight

A section with a lot of text and almost no height is the signature of the
disclosures bug. Deliberate omissions (advisor notes, the bio store, gallery
thumbnails, cards that present individually) are excluded by name, so anything
flagged deserves a look.

Usage:
    python3 tools/cspserve.py &
    python3 tools/audit_sections.py http://127.0.0.1:8899/Toolkit.html

Requires: playwright
"""

import json
import sys

from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Hidden on purpose: reference-only notes, the bio data store, gallery
# thumbnails, and cards that are presented as their own pages.
INTENTIONAL = [
    "advisor-note", "ppt-gallery", "contact-picker", "remove-contact-btn",
    "selected-contacts-label", "team-roster-block", "bio-picker-label",
    "team-picker-note", "overview-detail", "flag", "present-only-line",
    "locked-resource", "custom-slide-card",
]

AUDIT = """(INTENTIONAL)=>{
  const stage=document.getElementById('pdfStage')||document.body.appendChild(
    Object.assign(document.createElement('div'),{id:'pdfStage'}));
  const out=[];
  for(const el of document.querySelectorAll('.content-block')){
    if(!el.id) continue;
    const clone=el.cloneNode(true);
    clone.classList.add('presenting');
    [...clone.querySelectorAll('details')].forEach(d=>d.open=true);
    const page=document.createElement('div');
    page.className='print-page'; page.appendChild(clone);
    stage.innerHTML=''; stage.appendChild(page);

    const chars=(clone.textContent||'').replace(/\\s+/g,' ').trim().length;
    const renderH=Math.round(page.getBoundingClientRect().height);

    let hidden=0; const bits=[];
    clone.querySelectorAll('*').forEach(n=>{
      const cs=getComputedStyle(n);
      if(cs.display!=='none' && cs.visibility!=='hidden') return;
      const t=(n.textContent||'').replace(/\\s+/g,' ').trim();
      if(t.length<40) return;
      const cls=String((n.className&&n.className.baseVal!==undefined)?n.className.baseVal:n.className||'');
      if(INTENTIONAL.some(k=>cls.includes(k))) return;
      if(n.closest('summary')) return;
      if(n.parentElement && getComputedStyle(n.parentElement).display==='none') return;
      hidden+=t.length; bits.push((n.tagName+'.'+cls).slice(0,55)+' ['+t.length+']');
    });

    const clipped=[];
    clone.querySelectorAll('*').forEach(n=>{
      if(!/auto|scroll|hidden/.test(getComputedStyle(n).overflowY)) return;
      if(n.scrollHeight>n.clientHeight+6 && n.clientHeight>0)
        clipped.push((n.tagName+'.'+String(n.className)).slice(0,45)+' '+n.clientHeight+'<'+n.scrollHeight);
    });

    out.push({id:el.id, galleryOnly:el.dataset.galleryOnly==='true',
              chars, renderH, hidden, bits:bits.slice(0,4), clipped:clipped.slice(0,3)});
  }
  stage.innerHTML='';
  return out;
}"""


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: audit_sections.py <url of the served toolkit>")
    url = sys.argv[1]

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(60000)
        page.goto(url)
        page.wait_for_timeout(4500)
        rows = page.evaluate(AUDIT, INTENTIONAL)
        browser.close()

    print(f"{'SECTION':24s} {'chars':>7} {'renderH':>8} {'hidden':>7}  flags")
    findings = 0
    for r in rows:
        flags = []
        if r["hidden"] > 200:
            flags.append("HIDDEN-TEXT")
        if r["clipped"]:
            flags.append("CLIPPED")
        # A gallery-only section is never rendered as its own page, so a short
        # render there is expected rather than a fault.
        if r["chars"] > 400 and r["renderH"] < 260 and not r["galleryOnly"]:
            flags.append("TINY-RENDER")
        if flags:
            findings += 1
        print(f"{r['id']:24s} {r['chars']:7d} {r['renderH']:8d} {r['hidden']:7d}  {' '.join(flags)}")

    for r in rows:
        if r["hidden"] > 200 or r["clipped"]:
            print(f"\n{r['id']}:")
            for x in r["bits"]:
                print("   hidden:", x)
            for x in r["clipped"]:
                print("   clipped:", x)

    json.dump(rows, open("section_audit.json", "w"), indent=1)
    print(f"\n{findings} section(s) flagged; full detail in section_audit.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
