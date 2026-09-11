#!/usr/bin/env python3
"""
Trust & Estate Guide builder.

Reads a content JSON file (the facts extracted from the estate planning document)
and renders it into assets/guide-template.html. The template holds the entire
shell -- head, CSS, JS, logo, header, toolbar, footer, disclaimer -- and is read
here with open().read(), so it reaches the output as exact bytes. Nothing in the
shell is ever retyped by a model.

Usage:
    python3 build.py content.json /mnt/user-data/outputs/Name_Rev_Trust_FAQ_Guide.html

On ANY validation failure this script prints the specific problem and writes
nothing. A partial or unverified guide is never produced.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "guide-template.html"

# ---------------------------------------------------------------- logo identity
# The Cerity wordmark is 16 outlined letterform <path>s plus one <use> for the
# registered-trademark glyph. The tail sentinel exists only at the very end of
# the asset, so its presence proves the whole logo is intact -- a truncated or
# reconstructed logo cannot satisfy it.
LOGO_PATHS = 16
LOGO_USES = 1
LOGO_HEAD_SENTINEL = "M7096.34 3915.85C6981.6 4082.49"
LOGO_TAIL_SENTINEL = 'matrix(100,0,0,-100,1932.16,319.901)'

CATS = ("overview", "trustee", "lifecycle", "distribution", "legal")

# A citation must look like one of these. Deliberately permissive about the label
# itself -- documents number themselves in many ways -- but it must be a reference,
# not prose.
CITE_SHAPE = re.compile(
    r"""^(?:
        \u00a7\s?[\w.()\u2013\-]+                     # sec.4.2, sec.4, sec.4.2(a)(iii)
      | Art(?:icle)?\.?\s+[\w.()\u2013\-]+            # Art. Three, Article IV
      | Part\s+[\w.()\u2013\-]+                        # Part 6
      | (?:POA|HCP|HIPAA|Will|Codicil|Trust)\s+       # POA Art. One
        (?:Art(?:icle)?\.?|Part|\u00a7)\s*[\w.()\u2013\-]+
      | (?:Schedule|Exhibit)\s+[\w.()\u2013\-]+        # Schedule A
      )$""",
    re.X)

# Classes that exist purely as querySelectorAll hooks for the shell's JS and
# deliberately carry no style rule. Everything NOT listed here must have a rule
# in the template stylesheet, or the build fails -- that check is what catches a
# class being referenced in markup while its CSS was never written.
JS_HOOK_CLASSES = {"view-btn"}

# Inline HTML permitted inside authored text (answers, banner bodies, cells).
ALLOWED_TAGS = {"span", "strong", "em", "b", "i", "ul", "ol", "li", "br", "a",
                "code", "sup", "table", "thead", "tbody", "tr", "th", "td",
                "caption", "div", "p"}

# Anything matching these is blocked by the hosting platform's CSP, silently.
CSP_FORBIDDEN = ("<img", "data:image", "data:application", 'url("data', "url('data",
                 "url(data", "mask:", "-webkit-mask:", "fonts.googleapis",
                 "<script", "<iframe", "onerror=", "onload=")

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF️⬀-⯿]"
)

ERRORS = []


def err(msg):
    ERRORS.append(msg)


def die():
    if not ERRORS:
        return
    print("BUILD FAILED - nothing was written.\n", file=sys.stderr)
    for e in ERRORS:
        print("  * " + e, file=sys.stderr)
    print("\nFix the content file (or the template) and run again.", file=sys.stderr)
    sys.exit(1)


# -------------------------------------------------------------------- utilities
def esc(text):
    """Escape a value that must contain no markup at all."""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def defined_classes(template):
    style = re.search(r"<style>(.*?)</style>", template, re.S)
    if not style:
        err("template has no <style> block")
        return set()
    return set(re.findall(r"\.([A-Za-z][\w-]*)", style.group(1)))


def check_inline(html, where, allowed_classes):
    """Validate authored inline markup: tags on the allowlist, classes defined
    in the template's own stylesheet, nothing the CSP will silently eat. Also
    harvests any citations it contains for the document_sections check."""
    scan_cites(html, where)
    if not isinstance(html, str):
        err(f"{where}: expected text, got {type(html).__name__}")
        return
    low = html.lower()
    for bad in CSP_FORBIDDEN:
        if bad in low:
            err(f'{where}: contains "{bad}" - blocked by the hosting CSP, or unsafe')
    if EMOJI.search(html):
        err(f"{where}: contains an emoji - use the shell's SVG icons instead")
    for tag in re.findall(r"</?([a-zA-Z][\w]*)", html):
        if tag.lower() not in ALLOWED_TAGS:
            err(f"{where}: <{tag}> is not an allowed tag")
    for attr in re.findall(r'class="([^"]*)"', html):
        for cls in attr.split():
            if cls not in allowed_classes and cls not in JS_HOOK_CLASSES:
                err(f'{where}: class "{cls}" has no rule in the template stylesheet '
                    f"- it would render unstyled")
    # unbalanced tags are a common truncation symptom
    for tag in ("span", "ul", "ol", "table", "div"):
        o = len(re.findall(rf"<{tag}[\s>]", html))
        c = len(re.findall(rf"</{tag}>", html))
        if o != c:
            err(f"{where}: {o} <{tag}> open vs {c} close - unbalanced")


# Every citation the build emits or finds in authored text, for the index check.
CITES_SEEN = []


def note_cite(ref, where):
    if ref:
        CITES_SEEN.append((str(ref).strip(), where))


def cite(ref, where="content"):
    note_cite(ref, where)
    return f' <span class="section-ref">{esc(ref)}</span>' if ref else ""


def scan_cites(html, where):
    """Pull citations out of authored inline markup so they are checked too."""
    for ref in re.findall(r'<span class="section-ref">([^<]*)</span>', html or ""):
        note_cite(ref, where)


def check_citation_index(index, where_all):
    """Two checks, and it is worth being precise about what each does.

    1. SHAPE -- a citation must look like a reference, not a sentence.
    2. EXISTENCE -- every citation must appear in document_sections, the list of
       headings actually found in the document. This kills the invented-citation
       failure: a sec.9.4 in a trust with eight articles cannot ship.

    What this does NOT do, and no script can: confirm a citation points at the
    RIGHT section. sec.4.2 may exist and still be the wrong reference for the
    sentence it sits on. Only reading the document establishes that.
    """
    norm = {c.strip(): c.strip() for c in index}
    # tolerate a bare "4.2" in the index for a sec.4.2 citation, and vice versa
    loose = {c.strip().lstrip("\u00a7").strip() for c in index}
    for ref, where in CITES_SEEN:
        if not CITE_SHAPE.match(ref):
            err(f'{where}: citation "{ref}" is not shaped like a section reference')
            continue
        if ref in norm:
            continue
        if ref.lstrip("\u00a7").strip() in loose:
            continue
        err(f'{where}: citation "{ref}" is not in document_sections - either the '
            f"section was never found in the document, or the index is incomplete. "
            f"Never cite a section you did not read.")


# ------------------------------------------------------------------- components
ICONS = {
    "warning": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M12 3 22.5 21.5 1.5 21.5Z M12 7 18.9 19 5.1 19Z M11 10h2v5h-2z M11 16.5h2v2h-2z"/></svg>',
    "flag": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M7.5 2H16.5L22 7.5V16.5L16.5 22H7.5L2 16.5V7.5Z M11 6h2v8h-2z M11 16h2v2.4h-2z"/></svg>',
    "info": '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm-1 5h2v2h-2zm0 4h2v6h-2z"/></svg>',
}
PRINTER = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v4H6z"/><path d="M4 8h16a2 2 0 0 1 2 2v6h-4v-3H6v3H2v-6a2 2 0 0 1 2-2zm14 3a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/><path d="M6 14h12v7H6z"/></svg>'

FILTERS = [("all", "All Sections"), ("overview", "Overview"), ("trustee", "Trustee"),
           ("distribution", "Distributions"), ("lifecycle", "Lifecycle"),
           ("legal", "Legal / Admin")]


def render_banner(b, where, cls):
    variant = b.get("variant", "info")
    if variant not in ICONS:
        err(f"{where}: banner variant must be one of {sorted(ICONS)}, got {variant!r}")
        variant = "info"
    label = b.get("label", "")
    body = b.get("body", "")
    check_inline(body, f"{where} body", cls)
    lab = f"<strong>{esc(label)}:</strong> " if label else ""
    return (f'    <div class="banner {variant}-banner">{ICONS[variant]}\n'
            f"      <div>{lab}{body}</div>\n    </div>")


def render_table(t, where, cls, indent="      "):
    headers = t.get("headers") or []
    rows = t.get("rows") or []
    if not headers or not rows:
        err(f"{where}: table needs both headers and rows")
        return ""
    out = [f'{indent}<table class="data-table">']
    if t.get("caption"):
        out.append(f'{indent}  <caption style="caption-side:top; text-align:left; '
                   f"font-size:12px; font-weight:700; color:var(--clay); "
                   f'padding:6px 2px;">{esc(t["caption"])}</caption>')
    out.append(f"{indent}  <tr>" + "".join(f"<th>{esc(h)}</th>" for h in headers) + "</tr>")
    for i, row in enumerate(rows):
        if len(row) != len(headers):
            err(f"{where}: row {i} has {len(row)} cells, headers have {len(headers)}")
        cells = []
        for c in row:
            check_inline(str(c), f"{where} row {i}", cls)
            cells.append(f"<td>{c}</td>")
        out.append(f"{indent}  <tr>" + "".join(cells) + "</tr>")
    out.append(f"{indent}</table>")
    return "\n".join(out)


def render_flowchart(stages, where, cls, indent="        "):
    if not stages:
        err(f"{where}: flowchart has no stages")
        return ""
    out = [f'{indent}<div class="flowchart">']
    for i, st in enumerate(stages):
        if "branch" in st:
            out.append(f'{indent}  <div class="flow-branch">')
            for leg in st["branch"]:
                out.append(f'{indent}    ' + one_stage(leg, f"{where} branch", cls))
            out.append(f"{indent}  </div>")
        else:
            out.append(f"{indent}  " + one_stage(st, where, cls))
        if i < len(stages) - 1:
            out.append(f'{indent}  <div class="flow-arrow" aria-hidden="true"></div>')
    out.append(f"{indent}</div>")
    return "\n".join(out)


def one_stage(st, where, cls):
    label = st.get("stage", "")
    if not label:
        err(f"{where}: a flowchart stage has no title")
    if re.fullmatch(r"(?i)\s*(stage\s*\d+|active now|step\s*\d+)\s*", label or ""):
        err(f'{where}: stage title "{label}" is a category label - name the event '
            f'(e.g. "First Death", "Family Trust")')
    variant = st.get("variant")
    if variant and variant not in ("family-trust", "children"):
        err(f"{where}: stage variant must be family-trust or children, got {variant!r}")
    klass = "flow-stage"
    if st.get("active"):
        klass += " active-now"
    if variant:
        klass += " " + variant
    body = st.get("body", "")
    check_inline(body, f"{where} stage body", cls)
    return (f'<div class="{klass}"><div class="stage-label">{esc(label)}</div>'
            f'<div class="stage-content">{body}{cite(st.get("cite"))}</div></div>')


def render_blocks(blocks, where, cls, indent="        "):
    out = []
    for i, b in enumerate(blocks or []):
        kind = b.get("type")
        w = f"{where} block {i} ({kind})"
        if kind == "table":
            out.append(render_table(b, w, cls, indent))
        elif kind == "flowchart":
            out.append(render_flowchart(b.get("stages"), w, cls, indent))
        elif kind == "banner":
            out.append(render_banner(b, w, cls).replace("    <div", indent + "<div", 1))
        elif kind == "two_col":
            g1, g2 = b.get("g1", {}), b.get("g2", {})
            for side in (g1, g2):
                check_inline(side.get("body", ""), w, cls)
            out.append(
                f'{indent}<div class="two-col">\n'
                f'{indent}  <div class="col col-g1"><div class="col-head">'
                f'{esc(g1.get("head",""))}</div>{g1.get("body","")}</div>\n'
                f'{indent}  <div class="col col-g2"><div class="col-head">'
                f'{esc(g2.get("head",""))}</div>{g2.get("body","")}</div>\n'
                f"{indent}</div>")
        elif kind == "identical":
            check_inline(b.get("body", ""), w, cls)
            out.append(f'{indent}<div class="identical-row">'
                       f'<span class="badge-identical">IDENTICAL</span>'
                       f'<div>{b.get("body","")}</div></div>')
        else:
            err(f"{w}: unknown block type {kind!r} - allowed: table, flowchart, "
                f"banner, two_col, identical")
    return "\n".join(x for x in out if x)


def render_quick_ref(rows, cls):
    """Pack label/value pairs two per row. A 'wide' row spans all four slots."""
    out = ['    <div class="quick-ref">',
           '      <div class="quick-ref-header">&sect;1 &mdash; Key facts</div>',
           '      <table class="qr-table">']
    pending = []

    def value_cell(r, wide=False):
        v = r.get("v")
        if r.get("not_found"):
            inner = '<span class="not-found">[NOT FOUND &mdash; verify in original document]</span>'
        elif r.get("numbered"):
            lis = []
            for n, item in enumerate(r["numbered"], 1):
                if isinstance(item, dict):
                    txt, badge = item.get("text", ""), item.get("badge")
                else:
                    txt, badge = item, None
                check_inline(str(txt), "quick_ref numbered", cls)
                bd = f'<span class="qr-diff-badge">{esc(badge)}</span>' if badge else ""
                lis.append(f'<li><span class="n">{n}</span><span>{txt}</span>{bd}</li>')
            inner = '<ol class="qr-num-list">' + "".join(lis) + "</ol>"
        elif isinstance(v, list):
            # Multi-person values ALWAYS stack one per line.
            for p in v:
                check_inline(str(p), "quick_ref people", cls)
            inner = ('<ul class="qr-people">'
                     + "".join(f"<li>{p}</li>" for p in v) + "</ul>")
        else:
            check_inline(str(v or ""), "quick_ref value", cls)
            inner = str(v or "")
            if r.get("hl"):
                inner = f'<span class="qr-hl">{inner}</span>'
        klass = "qr-v qr-v-wide" if wide else "qr-v"
        span = ' colspan="3"' if wide else ""
        return f'<td class="{klass}"{span}>{inner}{cite(r.get("cite"))}</td>'

    def flush():
        if not pending:
            return
        cells = "".join(f'<td class="qr-k">{esc(p.get("k",""))}</td>' + value_cell(p)
                        for p in pending)
        if len(pending) == 1:
            cells += '<td class="qr-k"></td><td class="qr-v"></td>'
        out.append("        <tr>" + cells + "</tr>")
        pending.clear()

    # Quick Reference rows are mostly provisions, so most should carry a citation.
    # Some legitimately do not (a one-phrase characterisation of the document, a
    # NOT FOUND row), so this is a proportion check rather than a per-row rule.
    substantive = [r for r in rows if not r.get("not_found") and r.get("cite") is not False]
    cited = [r for r in substantive if r.get("cite")]
    if substantive and len(cited) < len(substantive) * 0.6:
        err(f"quick_ref: only {len(cited)} of {len(substantive)} substantive rows carry "
            f'a citation. Cite the provision each fact comes from, or set "cite": false '
            f"on a row that is a characterisation rather than a provision.")

    hl_count = sum(1 for r in rows if r.get("hl"))
    if hl_count > 3:
        err(f"quick_ref: {hl_count} rows are highlighted; at most 3 - past that the "
            f"highlight stops meaning anything")
    for r in rows:
        if r.get("wide") or r.get("numbered"):
            flush()
            out.append('        <tr><td class="qr-k">' + esc(r.get("k", "")) + "</td>"
                       + value_cell(r, wide=True) + "</tr>")
        else:
            pending.append(r)
            if len(pending) == 2:
                flush()
    flush()
    out += ["      </table>", "    </div>"]
    return "\n".join(out)


def render_sections(sections, cls):
    """Section numbering, data-cat, chevrons, and open/closed state are all
    generated here. Defaults come from the shell's rule and cannot be overridden:
    sec.2-4 open, sec.5 onward closed, and exactly ONE question open -- the first
    question of the earliest open section that actually has questions. Anchoring
    it to sec.2 literally would leave no question open at all whenever sec.2 is
    the flowchart-only structure overview, which is the common case."""
    out = []
    first_q_opened = False
    for idx, s in enumerate(sections):
        num = idx + 2
        cat = s.get("cat")
        if cat not in CATS:
            err(f"section {num}: data-cat must be one of {list(CATS)}, got {cat!r}")
            cat = "overview"
        title = s.get("title", "")
        if not title:
            err(f"section {num}: no title")
        sec_open = num <= 4
        badge = (f' <span class="doc-badge">{esc(s["doc_badge"])}</span>'
                 if s.get("doc_badge") else "")
        out.append(f'    <div class="faq-section" data-cat="{cat}">')
        out.append(f'      <button type="button" class="section-title" '
                   f'aria-expanded="{str(sec_open).lower()}" onclick="toggleSection(this)">')
        out.append(f'        <span class="title-text">&sect;{num} &mdash; '
                   f"{esc(title)}{badge}</span>")
        out.append('        <span class="chevron" aria-hidden="true"></span>')
        out.append("      </button>")
        out.append(f'      <div class="section-body{" open" if sec_open else ""}">')

        intro = render_blocks(s.get("blocks"), f"section {num}", cls)
        if intro:
            out.append(intro)

        items = s.get("items") or []
        if not items and not intro:
            err(f"section {num} ({title}): has neither questions nor blocks")
        for i, it in enumerate(items):
            q, a = it.get("q", ""), it.get("a", "")
            if not q or not a:
                err(f"section {num} item {i}: needs both q and a")
            q_open = sec_open and not first_q_opened
            if q_open:
                first_q_opened = True
            check_inline(a, f"section {num} item {i} answer", cls)
            # An answer states what the document says, so it must say where.
            # "cite": false marks a deliberate exception -- a general explanation
            # that is not a provision of this document.
            if it.get("cite") is not False:
                if "section-ref" not in a and "not-found" not in a:
                    err(f'section {num} ("{title}") item {i}: the answer carries no '
                        f"citation and no NOT FOUND flag. Add a "
                        f'<span class="section-ref">...</span> for the provision it '
                        f'states, or set "cite": false if it is a general '
                        f"explanation rather than a provision of this document. "
                        f"Question: {q[:60]}")
            out.append('        <div class="faq-item">')
            out.append(f'          <button type="button" class="faq-q" '
                       f'aria-expanded="{str(q_open).lower()}" onclick="toggleQ(this)">')
            out.append(f"            <span>{esc(q)}</span>"
                       '<span class="chevron" aria-hidden="true"></span>')
            out.append("          </button>")
            out.append(f'          <div class="faq-a{" open" if q_open else ""}">{a}</div>')
            nested = render_blocks(it.get("blocks"), f"section {num} item {i}", cls,
                                   indent="          ")
            if nested:
                out.append(nested)
            out.append("        </div>")
        out += ["      </div>", "    </div>", ""]
    return "\n".join(out)


def render_toolbar(two_col, labels):
    filters = "\n".join(
        f'      <button type="button" class="toolbar-btn{" active" if k=="all" else ""}" '
        f'data-filter aria-pressed="{"true" if k=="all" else "false"}" '
        f"onclick=\"filterSections('{k}', this)\">{lab}</button>"
        for k, lab in FILTERS)
    print_btn = ('      <button type="button" class="toolbar-btn print-btn" '
                 f'onclick="window.print()">\n        {PRINTER}\n        Print / PDF\n'
                 "      </button>")
    show = ('      <span class="label">Show:</span>\n' + filters
            + '\n      <span class="toolbar-sep" aria-hidden="true">|</span>\n'
            '      <button type="button" class="util-btn" onclick="expandAll()">Expand all</button>\n'
            '      <button type="button" class="util-btn" onclick="collapseAll()">Collapse all</button>')
    if not two_col:
        return ('  <div class="toolbar-strip">\n    <div class="toolbar-inner">\n'
                + show + "\n" + print_btn + "\n    </div>\n  </div>")
    g1 = labels[0] if len(labels) > 0 else "Grantor 1"
    g2 = labels[1] if len(labels) > 1 else "Grantor 2"
    views = [("both", "Both"), ("g1", f"{g1}'s Trust"),
             ("g2", f"{g2}'s Trust"), ("same", "Identical Only")]
    vbtns = "\n".join(
        f'      <button type="button" class="toolbar-btn view-btn'
        f'{" active" if m=="both" else ""}" aria-pressed="{"true" if m=="both" else "false"}" '
        f"onclick=\"setView('{m}', this)\">{esc(lab)}</button>"
        for m, lab in views)
    return ('  <div class="toolbar-strip">\n    <div class="toolbar-inner toolbar-row">\n'
            '      <span class="label">View:</span>\n' + vbtns + "\n" + print_btn
            + "\n    </div>\n    <div class=\"toolbar-inner toolbar-row\">\n" + show
            + "\n    </div>\n  </div>")


# ------------------------------------------------------------------ output gate
def verify_output(html, cls):
    m = re.search(r'<svg[^>]*viewBox="0 0 2054\.13 461\.62".*?</svg>', html, re.S)
    if not m:
        err("OUTPUT: the Cerity logo <svg> is missing from the rendered page")
    else:
        logo = m.group(0)
        if logo.count("<path") != LOGO_PATHS:
            err(f"OUTPUT: logo has {logo.count('<path')} <path> elements, expected "
                f"{LOGO_PATHS} - the wordmark is incomplete")
        if logo.count("<use") != LOGO_USES:
            err(f"OUTPUT: logo has {logo.count('<use')} <use> elements, expected {LOGO_USES}")
        if LOGO_HEAD_SENTINEL not in logo:
            err("OUTPUT: logo head sentinel missing")
        if LOGO_TAIL_SENTINEL not in logo:
            err("OUTPUT: logo tail sentinel missing - the logo was truncated or rebuilt")
    left = re.findall(r"\{\{(\w+)\}\}", html)
    if left:
        err(f"OUTPUT: unfilled placeholders remain: {sorted(set(left))}")
    for fn in ("toggleSection", "toggleQ", "filterSections", "setView",
               "expandAll", "collapseAll"):
        if f"function {fn}(" not in html:
            err(f"OUTPUT: <script> is missing {fn}() - the shell was not copied whole")
    # Scan only the authored/rendered region: the body with the shell's own
    # <script> block and HTML comments removed, so the page's legitimate script
    # and the comments that explain these very prohibitions are not flagged.
    body = html[html.index("<body"):]
    scan = re.sub(r"<script>.*?</script>", "", body, flags=re.S)
    scan = re.sub(r"<!--.*?-->", "", scan, flags=re.S)
    for bad in CSP_FORBIDDEN:
        if bad in scan.lower():
            err(f'OUTPUT: "{bad}" appears in the page body - the CSP blocks it silently')
    for attr in re.findall(r'class="([^"]*)"', scan):
        for c in attr.split():
            if c not in cls and c not in JS_HOOK_CLASSES:
                err(f'OUTPUT: class "{c}" is used but has no rule in the stylesheet')
    secs = re.findall(r'aria-expanded="(\w+)"[^>]*>\s*<span class="title-text".*?'
                      r'<div class="section-body([^"]*)"', html, re.S)
    for ae, bodycls in secs:
        if (ae == "true") != ("open" in bodycls):
            err("OUTPUT: a section's aria-expanded does not match its body .open state")
    if EMOJI.search(body):
        err("OUTPUT: an emoji reached the page")


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    content_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])

    if not TEMPLATE.exists():
        print(f"FATAL: template not found at {TEMPLATE}", file=sys.stderr)
        sys.exit(1)
    template = TEMPLATE.read_text()
    cls = defined_classes(template)

    try:
        data = json.loads(content_path.read_text())
    except json.JSONDecodeError as e:
        print(f"BUILD FAILED - content JSON is invalid: {e}", file=sys.stderr)
        sys.exit(1)

    known = {"title", "eyebrow", "doc_type_dates", "layout", "grantor_labels",
             "binder", "preparer", "prepared", "quick_ref", "banners", "sections",
             "document_sections"}
    for k in data:
        if k not in known:
            err(f'unknown top-level key "{k}" - allowed: {sorted(known)}')
    for req in ("title", "doc_type_dates", "preparer", "prepared", "quick_ref",
                "sections", "document_sections"):
        if not data.get(req):
            err(f'required key "{req}" is missing or empty')
    layout = data.get("layout", "single")
    if layout not in ("single", "two-column"):
        err(f'layout must be "single" or "two-column", got {layout!r}')
    two_col = layout == "two-column"
    if two_col and len(data.get("grantor_labels") or []) != 2:
        err('two-column layout needs grantor_labels: ["Name 1", "Name 2"]')

    die()  # stop before rendering if the shape is wrong

    main_html = []
    for i, b in enumerate(data.get("banners") or []):
        main_html.append(render_banner(b, f"top banner {i}", cls))
    main_html.append(render_quick_ref(data["quick_ref"], cls))
    main_html.append(render_sections(data["sections"], cls))

    hdr_bottom = ""
    if data.get("binder"):
        fam = data["binder"].get("family", "")
        href = data["binder"].get("href", "")
        if not href.endswith(".html") or "/" in href:
            err("binder.href must be a relative filename ending in .html")
        hdr_bottom = ('\n      <div class="hdr-bottom">\n'
                      f'        <a class="crumb" href="{esc(href)}">&#8592; '
                      f'{esc(fam)} Family Estate Plan index</a>\n      </div>')

    html = template
    for key, val in {
        "TITLE": esc(data["title"]),
        "EYEBROW": esc(data.get("eyebrow", "Trust & Estate FAQ")),
        "HDR_TITLE": esc(data["title"]),
        "HDR_DATES": esc(data["doc_type_dates"]),
        "HDR_BOTTOM": hdr_bottom,
        "BODY_ATTRS": ' data-view="both"' if two_col else "",
        "TOOLBAR": render_toolbar(two_col, data.get("grantor_labels") or []),
        "MAIN": "\n".join(x for x in main_html if x),
        "PREPARER": esc(data["preparer"]),
        "PREPARED": esc(data["prepared"]),
    }.items():
        html = html.replace("{{" + key + "}}", val)

    check_citation_index(data["document_sections"], "citations")
    verify_output(html, cls)
    die()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)
    logo = re.search(r'<svg[^>]*2054\.13.*?</svg>', html, re.S).group(0)
    print(f"OK  wrote {out_path}  ({len(html):,} bytes)")
    print(f"    layout={layout}  sections={len(data['sections'])}  "
          f"logo={logo.count('<path')} paths / {logo.count('<use')} use")
    idx = [c.strip() for c in data["document_sections"]]
    used = {r for r, _ in CITES_SEEN}
    unused = [c for c in idx if c not in used and c.lstrip("\u00a7").strip() not in
              {u.lstrip("\u00a7").strip() for u in used}]
    print(f"    citations: {len(CITES_SEEN)} references to {len(used)} of "
          f"{len(idx)} sections in the document")
    if unused:
        print(f"    {len(unused)} section(s) in the document are never cited: "
              f"{', '.join(unused[:12])}{' ...' if len(unused) > 12 else ''}")
        print(f"    Check whether any of those belong in the guide.")
    print("    Citations were checked for shape and for existence in "
          "document_sections.")
    print("    They were NOT checked for correctness - only reading the document "
          "confirms a\n    citation points at the right provision.")
    nf = html.count("not-found")
    if nf:
        print(f"    {nf} provision(s) flagged NOT FOUND - list them in the post-output notes")


if __name__ == "__main__":
    main()
