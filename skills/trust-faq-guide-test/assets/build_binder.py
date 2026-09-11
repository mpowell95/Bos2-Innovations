#!/usr/bin/env python3
"""
Family Estate Plan Binder builder.

Reads a binder content JSON and renders it into assets/binder-template.html, which
holds the complete shell -- head, CSS, logo, header, footer -- and is read here with
open().read(), so the shell reaches the output as exact bytes.

Usage:
    python3 build_binder.py binder.json /mnt/user-data/outputs/Sample_Estate_Plan_Index.html

The binder is a static index page: no <script>, no collapsible sections. Build the
individual guides first with build.py, then this.

On ANY validation failure this prints the problem and writes nothing.
"""

import json
import re
import sys
from pathlib import Path

# Reuse the guide builder's validators so both outputs are held to one standard.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as G  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "binder-template.html"

PANEL_CATS = ("overview", "trustee", "lifecycle", "flag")
PILLS = {"active": "Active", "revocable": "Revocable",
         "irrevocable": "Now Irrevocable", "super": "Superseded"}
CHECK = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">'
         '<path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>')


def panel(cat, title, inner, flush=False):
    if cat not in PANEL_CATS:
        G.err(f"panel '{title}': header colour must be one of {list(PANEL_CATS)}, got {cat!r}")
    style = ' style="padding:0;"' if flush else ""
    return (f'    <div class="panel">\n'
            f'      <div class="panel-header {cat}">{G.esc(title)}</div>\n'
            f'      <div class="panel-body"{style}>\n{inner}\n      </div>\n    </div>')


def rel_link(href, where):
    """Cross-links must be relative filenames so the folder stays portable."""
    if not href:
        return None
    if "/" in href or ":" in href or href.startswith("#"):
        G.err(f"{where}: guide link must be a bare relative filename, got {href!r}")
    elif not href.endswith(".html"):
        G.err(f"{where}: guide link should end in .html, got {href!r}")
    return href


def render_inventory(docs, cls, delivered):
    rows = []
    for i, d in enumerate(docs):
        w = f"inventory row {i}"
        statuses = d.get("status") or []
        if isinstance(statuses, str):
            statuses = [statuses]
        pills = []
        for s in statuses:
            if s not in PILLS:
                G.err(f"{w}: status must be one of {sorted(PILLS)}, got {s!r}")
            else:
                pills.append(f'<span class="pill pill-{s}">{PILLS[s]}</span>')
        href = rel_link(d.get("guide"), w)
        if href:
            delivered.add(href)
            link = f'<a href="{G.esc(href)}">Open &#8594;</a>'
        else:
            # .na is a guide-stylesheet class and is not defined in the binder's
            # own stylesheet, so this uses an inline style, matching how the binder
            # renders its other muted sub-labels.
            link = '<span style="color:#8a857c;">no guide</span>'
        for f in ("owner", "document", "type", "dated"):
            G.check_inline(str(d.get(f, "")), f"{w} {f}", cls)
        rows.append(
            f'          <tr><td>{d.get("owner","")}</td><td>{d.get("document","")}</td>'
            f'<td>{d.get("type","")}</td><td>{d.get("dated","")}</td>'
            f'<td>{" ".join(pills)}</td><td>{link}</td></tr>')
    if not rows:
        G.err("inventory: no documents listed")
    return ('        <table class="data-table">\n'
            "          <tr><th>Owner</th><th>Document</th><th>Type</th><th>Dated</th>"
            "<th>Status</th><th>Guide</th></tr>\n" + "\n".join(rows) + "\n        </table>")


def render_whos_who(people, cls):
    rows = []
    for i, p in enumerate(people):
        w = f"whos_who row {i}"
        name = p.get("name", "")
        if not name:
            G.err(f"{w}: no name")
        klass = "person deceased" if p.get("deceased") else "person"
        note = ""
        if p.get("relation"):
            note = (f'<br><span style="font-size:12px;color:#8a857c;">'
                    f'{G.esc(p["relation"])}</span>')
        roles = p.get("roles") or []
        if not roles:
            G.err(f"{w} ({name}): no roles listed")
        for r in roles:
            G.check_inline(str(r), w, cls)
        lis = "".join(f"<li>{r}</li>" for r in roles)
        rows.append(f'          <tr><td><span class="{klass}">{G.esc(name)}</span>{note}</td>'
                    f'<td><ul class="role-list">{lis}</ul></td></tr>')
    return ('        <table class="data-table">\n'
            '          <tr><th style="width:210px;">Person</th>'
            "<th>Roles across the plan</th></tr>\n" + "\n".join(rows) + "\n        </table>")


def render_timeline(stages, cls):
    if not stages:
        G.err("timeline: no stages")
    rows = []
    for i, s in enumerate(stages):
        w = f"timeline stage {i}"
        when = s.get("when", "")
        if not when:
            G.err(f"{w}: no 'when' label")
        done = ' done' if s.get("done") else ""
        icon = " " + CHECK if s.get("done") else ""
        G.check_inline(s.get("what", ""), w, cls)
        docs = ""
        if s.get("documents"):
            G.check_inline(str(s["documents"]), f"{w} documents", cls)
            docs = f' <span class="doc">Documents:</span> {s["documents"]}'
        rows.append(f'          <div class="flow-row">'
                    f'<div class="flow-when{done}">{G.esc(when)}{icon}</div>'
                    f'<div class="flow-what">{s.get("what","")}{docs}</div></div>')
    return ('        <div class="flow-timeline">\n' + "\n".join(rows) + "\n        </div>")


def render_actions(items, cls):
    if not items:
        G.err("actions: no items - if the individual guides raised no flags, say so in an "
              "info banner rather than omitting the panel")
    out = []
    for i, a in enumerate(items):
        w = f"action {i}"
        variant = a.get("variant", "warning")
        if variant not in G.ICONS:
            G.err(f"{w}: variant must be one of {sorted(G.ICONS)}, got {variant!r}")
            variant = "warning"
        G.check_inline(a.get("detail", ""), w, cls)
        src = ""
        if a.get("source"):
            src = f' <span class="section-ref">{G.esc(a["source"])}</span>'
        out.append(f'        <div class="banner {variant}-banner">{G.ICONS[variant]}'
                   f'<div><strong>{G.esc(a.get("label",""))}</strong> '
                   f'{a.get("detail","")}{src}</div></div>')
    return "\n".join(out)


def verify_output(html, cls, delivered):
    m = re.search(r'<svg[^>]*viewBox="0 0 2054\.13 461\.62".*?</svg>', html, re.S)
    if not m:
        G.err("OUTPUT: the Cerity logo is missing")
    else:
        logo = m.group(0)
        if logo.count("<path") != G.LOGO_PATHS or logo.count("<use") != G.LOGO_USES:
            G.err(f"OUTPUT: logo census wrong ({logo.count('<path')} paths, "
                  f"{logo.count('<use')} use) - expected {G.LOGO_PATHS}/{G.LOGO_USES}")
        if G.LOGO_TAIL_SENTINEL not in logo:
            G.err("OUTPUT: logo tail sentinel missing - truncated or rebuilt")
    left = re.findall(r"\{\{(\w+)\}\}", html)
    if left:
        G.err(f"OUTPUT: unfilled placeholders remain: {sorted(set(left))}")
    if "<script" in html:
        G.err("OUTPUT: the binder index carries no <script> - remove it")
    body = html[html.index("<body"):]
    scan = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    for bad in G.CSP_FORBIDDEN:
        if bad in scan.lower():
            G.err(f'OUTPUT: "{bad}" appears in the body - the CSP blocks it silently')
    for attr in re.findall(r'class="([^"]*)"', scan):
        for c in attr.split():
            if c not in cls and c not in G.JS_HOOK_CLASSES:
                G.err(f'OUTPUT: class "{c}" has no rule in the stylesheet')
    if G.EMOJI.search(scan):
        G.err("OUTPUT: an emoji reached the page")
    # every link must point at a file named in the inventory
    for href in re.findall(r'<a href="([^"]+)"', body):
        if href not in delivered:
            G.err(f'OUTPUT: link to "{href}" is not one of the documents listed in the '
                  f"inventory - every cross-link must resolve to a delivered guide")


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    content_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    if not TEMPLATE.exists():
        print(f"FATAL: template not found at {TEMPLATE}", file=sys.stderr)
        sys.exit(1)
    template = TEMPLATE.read_text()
    cls = G.defined_classes(template)

    try:
        data = json.loads(content_path.read_text())
    except json.JSONDecodeError as e:
        print(f"BUILD FAILED - binder JSON is invalid: {e}", file=sys.stderr)
        sys.exit(1)

    known = {"family", "subtitle", "preparer", "prepared", "context",
             "inventory", "whos_who", "timeline", "actions"}
    for k in data:
        if k not in known:
            G.err(f'unknown top-level key "{k}" - allowed: {sorted(known)}')
    for req in ("family", "preparer", "prepared", "inventory", "whos_who", "timeline"):
        if not data.get(req):
            G.err(f'required key "{req}" is missing or empty')
    G.die()

    delivered = set()
    parts = [
        panel("overview", "Documents in This Plan",
              render_inventory(data["inventory"], cls, delivered), flush=True),
        panel("trustee", "Who's Who — Roles Across All Documents",
              render_whos_who(data["whos_who"], cls), flush=True),
        panel("lifecycle", "How the Plan Works Together — Family Timeline",
              render_timeline(data["timeline"], cls)),
    ]
    if data.get("actions"):
        parts.append(panel("flag", "Action Items Across the Plan",
                           render_actions(data["actions"], cls)))

    context = ""
    if data.get("context"):
        G.check_inline(data["context"], "context banner", cls)
        context = (f'\n      <div class="context-banner">{G.ICONS["warning"]}'
                   f'{data["context"]}</div>')

    html = template
    for key, val in {
        "FAMILY": G.esc(data["family"]),
        "SUBTITLE": G.esc(data.get("subtitle", f"Prepared {data['prepared']}")),
        "CONTEXT": context,
        "MAIN": "\n".join(parts),
        "PREPARER": G.esc(data["preparer"]),
        "PREPARED": G.esc(data["prepared"]),
    }.items():
        html = html.replace("{{" + key + "}}", val)

    verify_output(html, cls, delivered)
    G.die()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)
    print(f"OK  wrote {out_path}  ({len(html):,} bytes)")
    print(f"    documents={len(data['inventory'])}  people={len(data['whos_who'])}  "
          f"stages={len(data['timeline'])}  actions={len(data.get('actions') or [])}")
    print(f"    guides linked: {', '.join(sorted(delivered)) or 'none'}")
    print("    Confirm every linked guide is delivered to the same folder, or the "
          "relative links will not resolve.")


if __name__ == "__main__":
    main()
