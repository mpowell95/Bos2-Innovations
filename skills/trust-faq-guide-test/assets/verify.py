#!/usr/bin/env python3
"""
Verification pass — checks the CONTENT of a built guide, not its formatting.

build.py guarantees the guide is well-formed. It cannot tell whether a name, an
amount, an age or a citation is RIGHT. This does two things about that:

  1. extract  — pulls every decision-driving claim out of the content file into a
                worksheet. You then re-read the document and mark each one.
  2. check    — refuses to pass until every claim is marked, and reports what the
                marks say.

It also runs the cross-field checks that need no document: the interested-trustee
conflict, the NOT FOUND census, and a warning for sections the document type
normally has but this guide omits.

Usage:
    python3 verify.py extract content.json worksheet.md
    python3 verify.py mark  worksheet.md marks.txt      # apply marks, report progress
    python3 verify.py check worksheet.md [marks.txt]    # gate

A long worksheet can be marked over several turns: run "mark" with each batch as you
work through the document -- it applies the marks and tells you how many remain,
without failing -- then run "check" once at the end.

Worksheet marks (edit the box, add a note after '--'):
    [x] confirmed against the document
    [!] WRONG -- note what the document actually says, then fix content.json,
        rebuild with build.py, and re-extract
    [?] cannot be verified from the document -- say why; these are reported to
        the advisor, not silently dropped

A claim you did not actually look up is not [x]. The worksheet is the record that
the guide was checked, and it is delivered alongside it.
"""

import json
import re
import sys
from pathlib import Path

# Reuse build.py's content merging so a split content set is read identically here.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as G  # noqa: E402

# Sections a document type normally contains. Absence is a warning, never a hard
# failure -- a real document can lack any of these, and the guide is right to omit
# a section the document does not have. The point is to make an omission visible
# rather than silent.
EXPECTED = {
    "revocable": ["trustee succession", "incapacity", "administration upon death",
                  "distribution", "administrative", "protective"],
    "irrevocable": ["trustee succession", "distribution", "administrative", "protective"],
    "will": ["executor", "residuary", "specific bequest", "administrative"],
}

CLAIM_RE = re.compile(r"^- \[(.)\]\s+(\S+)\s+\|", re.M)

# A claim is worth verifying if it drives a decision: a name, a number, a date, an
# age, a role, an amount. Generic explanation is not.
SIGNAL = re.compile(
    r"\d|\bage[sd]?\b|\btrustee\b|\bexecutor\b|\bbeneficiar|\bspouse\b|\bchild"
    r"|\bgrantor\b|\bsuccessor\b|\bagent\b|\bper stirpes\b|\boutright\b"
    r"|\bdiscretion\b|\bincome\b|\bprincipal\b|\bNOT FOUND\b", re.I)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", str(s)).strip()


def cites_in(s):
    return re.findall(r'<span class="section-ref">([^<]*)</span>', str(s))


def all_cites(data):
    """Every citation anywhere in the content file.

    Coverage must not be computed from claim lines alone: an answer that is not a
    decision-driving claim (so gets no worksheet line) can still carry a citation,
    and counting only claims reported such a section as "never cited". Found in the
    first real two-column run -- Article XXIV was cited in the guide and listed as
    uncited here. Walks the structure rather than pattern-matching serialised JSON,
    where the escaped quotes made the match unreliable.
    """
    found = set()

    def walk(node, key=None):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)
        elif isinstance(node, str):
            if key == "cite" and node.strip():
                found.add(node.strip())
            for c in re.findall(r'<span class="section-ref">([^<]*)</span>', node):
                if c.strip():
                    found.add(c.strip())

    walk(data)
    return found


def claims(data):
    """Every decision-driving assertion in the content file, with its citations."""
    out = []

    def add(kind, text, cites, loc):
        text = " ".join(strip_tags(text).split())
        if not text:
            return
        seen, uniq = set(), []            # a row's own cite often repeats inside its body
        for c in cites:
            c = str(c).strip()
            if c and c not in seen:
                seen.add(c)
                uniq.append(c)
        out.append({"kind": kind, "text": text[:220], "cites": uniq, "loc": loc})

    for i, r in enumerate(data.get("quick_ref") or []):
        if r.get("not_found"):
            add("NOTFOUND", f'{r.get("k","")}: flagged NOT FOUND', [], f"quick_ref[{i}]")
            continue
        v = r.get("v")
        if r.get("numbered"):
            items = [x.get("text", "") if isinstance(x, dict) else x for x in r["numbered"]]
            v = " -> ".join(str(x) for x in items)
        elif isinstance(v, list):
            v = "; ".join(str(x) for x in v)
        add("QR", f'{r.get("k","")}: {v}',
            ([r["cite"]] if r.get("cite") else []) + cites_in(v), f"quick_ref[{i}]")

    for si, s in enumerate(data.get("sections") or []):
        num = si + 2
        for bi, b in enumerate(s.get("blocks") or []):
            loc = f"sections[{si}].blocks[{bi}]"
            if b.get("type") == "table":
                for ri, row in enumerate(b.get("rows") or []):
                    cells = [strip_tags(c) for c in row]
                    add("TABLE", " | ".join(cells),
                        [c for cell in row for c in cites_in(cell)], f"{loc}.rows[{ri}]")
            elif b.get("type") == "flowchart":
                for sti, st in enumerate(b.get("stages") or []):
                    legs = st.get("branch") or [st]
                    for leg in legs:
                        add("STAGE", f'{leg.get("stage","")}: {leg.get("body","")}',
                            ([leg["cite"]] if leg.get("cite") else [])
                            + cites_in(leg.get("body", "")), f"{loc}.stages[{sti}]")
            elif b.get("type") in ("two_col", "identical"):
                for side in (("g1", "g2") if b.get("type") == "two_col" else ("body",)):
                    part = b.get(side) if side != "body" else {"body": b.get("body")}
                    if part:
                        add("COL", f'{part.get("head","")} {part.get("body","")}',
                            cites_in(part.get("body", "")), f"{loc}.{side}")
        for ii, it in enumerate(s.get("items") or []):
            a = it.get("a", "")
            loc = f"sections[{si}].items[{ii}]"
            if "not-found" in a:
                add("NOTFOUND", f'{it.get("q","")} -> flagged NOT FOUND', cites_in(a), loc)
            elif SIGNAL.search(strip_tags(a)):
                add("ANSWER", f'{it.get("q","")} -> {a}', cites_in(a), loc)
    for i, b in enumerate(data.get("banners") or []):
        add("BANNER", f'{b.get("label","")} {b.get("body","")}',
            cites_in(b.get("body", "")), f"banners[{i}]")
    return out


def cross_checks(data):
    """Checks that need no document, only the content file read against itself."""
    warn = []
    blob = json.dumps(data).lower()

    # Interested-trustee conflict. If a person is named both as a trustee and as a
    # beneficiary, "full discretion" over distributions to themselves is a
    # self-dealing problem -- the skill's highest-liability rule.
    names = set()
    for r in data.get("quick_ref") or []:
        k = str(r.get("k", "")).lower()
        vals = r.get("numbered") or r.get("v")
        if not isinstance(vals, list):
            vals = [vals]
        flat = [strip_tags(x.get("text", "") if isinstance(x, dict) else x) for x in vals]
        if any(w in k for w in ("trustee", "grantor")):
            names |= {("trustee", n) for n in flat if n}
        if any(w in k for w in ("beneficiar", "remainder", "children")):
            names |= {("beneficiary", n) for n in flat if n}
    # Scope: this compares names that appear in Quick Reference rows only. A document
    # that names no beneficiaries there -- e.g. one disposing to "my descendants"
    # generally -- gives it nothing to compare, so silence here is not a clearance.
    trustees = {n for role, n in names if role == "trustee"}
    benes = {n for role, n in names if role == "beneficiary"}
    both = {n for n in trustees & benes if len(n) > 3}
    if both and re.search(r"(full|sole|absolute|complete)\s+discretion", blob):
        warn.append(
            "INTERESTED TRUSTEE: " + ", ".join(sorted(both)) + " appears as both a "
            "trustee and a beneficiary, and the guide says \"full/sole/absolute "
            "discretion\" somewhere. Check whether an independent trustee is required "
            "for distributions to that person. If so, the flowchart and distribution "
            "table must say an independent trustee decides -- a beneficiary-trustee "
            "must never be described as self-directing distributions to themselves.")
    elif both:
        warn.append(
            "INTERESTED TRUSTEE: " + ", ".join(sorted(both)) + " is both trustee and "
            "beneficiary. No \"full discretion\" language found, which is correct, but "
            "confirm the guide states who decides distributions to that person.")

    # Sections the type normally has.
    titles = " ".join(str(s.get("title", "")).lower() for s in data.get("sections") or [])
    dt = str(data.get("doc_type_dates", "")).lower()
    key = ("will" if "will" in dt and "trust" not in dt else
           "revocable" if "revocable" in dt else
           "irrevocable" if "irrevocable" in dt else None)
    if key:
        missing = [e for e in EXPECTED[key] if e not in titles]
        if missing:
            warn.append(f"SECTIONS: a {key} document usually has a section covering "
                        f"{', '.join(missing)}. None found. Confirm the document really "
                        f"lacks these rather than the guide having skipped them.")
    return warn


def do_extract(content_path, out_path, quiet=False):
    """content_path may be one path or a list of them, matching build.py's merge."""
    paths = content_path if isinstance(content_path, (list, tuple)) else [content_path]
    data = G.load_content(paths)
    cl = claims(data)
    warn = cross_checks(data)
    idx = [c.strip() for c in data.get("document_sections") or []]
    used = all_cites(data)
    loose = {u.lstrip("\u00a7").strip() for u in used}
    unused = [c for c in idx
              if c not in used and c.lstrip("\u00a7").strip() not in loose]

    L = [f"# Verification worksheet — {data.get('title','(untitled)')}",
         "",
         "Re-read the document and mark every line. `[x]` confirmed · `[!]` wrong (note what "
         "the document says) · `[?]` not verifiable from the document (say why).",
         "",
         "A line you did not look up is not `[x]`. This worksheet is delivered with the "
         "guide as the record that it was checked.",
         ""]
    L += ["## Check these first", ""]
    if warn:
        for w in warn:
            L += [f"- {w}", ""]
    else:
        L += ["- No automatic cross-check fired. That is not a clearance: the "
              "interested-trustee check compares names in Quick Reference rows, so a "
              "document that names no beneficiaries there (one disposing to \"my "
              "descendants\" generally, say) gives it nothing to compare. Confirm by "
              "reading: is any trustee also a beneficiary, and if so does the guide say "
              "who decides distributions to that person?", ""]
    L += [f"## Claims ({len(cl)})", ""]
    for i, c in enumerate(cl, 1):
        cites = " ".join(c["cites"]) or "(no citation)"
        L.append(f'- [ ] {i:03d} | {c["kind"]} | {cites} | {c["text"]}')
    L += ["",
          "## Citation coverage",
          "",
          f"The document has {len(idx)} sections; the guide cites {len(idx) - len(unused)} "
          f"of them ({len(used)} distinct citations in all).",
          "",
          "Counted across the whole guide, not only the claims listed above."]
    if unused:
        L += ["", "Never cited — confirm none of these belong in the guide:", ""]
        L += [f"- {u}" for u in unused]
    L += ["", "## Sign-off", "",
          "- [ ] Every claim above is marked.",
          "- [ ] Every `[!]` was fixed in content.json and the guide rebuilt.",
          "- [ ] Every `[?]` is listed in the post-output notes for the advisor.",
          ""]
    Path(out_path).write_text("\n".join(L))
    if quiet:
        return {"claims": len(cl), "warnings": warn}
    print(f"OK  wrote {out_path}")
    print(f"    {len(cl)} claims to verify"
          + (f"  |  {len(warn)} cross-check warning(s)" if warn else ""))
    for w in warn:
        print("    ! " + w.split(":")[0])
    print("    Re-read the document, mark every line, then: verify.py check "
          f"{Path(out_path).name}")


MARK_LINE = re.compile(r"^\s*(\d{1,3}|signoff)\s+([x!?])\s*(?:--\s*)?(.*)$", re.I)


def apply_marks(ws_path, marks_path):
    """Apply a compact marks file to the worksheet, in place.

    Writing "001 x" lines costs a fraction of re-emitting a 40-line worksheet, which
    matters when the whole guide has to be produced inside one turn.
    """
    ws = Path(ws_path).read_text()
    applied, unknown = 0, []
    for raw in Path(marks_path).read_text().split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = MARK_LINE.match(raw)
        if not m:
            unknown.append(raw.strip())
            continue
        ident, mark, note = m.group(1).lower(), m.group(2).lower(), m.group(3).strip()
        if ident == "signoff":
            ws = re.sub(r"^- \[ \] (Every )", rf"- [{mark}] \1", ws, flags=re.M)
            applied += 1
            continue
        ident = ident.zfill(3)
        pat = re.compile(rf"^- \[.\] {ident} \|(.*)$", re.M)
        if not pat.search(ws):
            unknown.append(f"{ident} (no such claim in the worksheet)")
            continue
        def sub(mo):
            line = f"- [{mark}] {ident} |{mo.group(1)}"
            return line + (f"  -- {note}" if note else "")
        ws = pat.sub(sub, ws, count=1)
        applied += 1
    if unknown:
        print("MARKS FILE HAS LINES I CANNOT READ - nothing was applied.\n",
              file=sys.stderr)
        for u in unknown:
            print("  * " + u, file=sys.stderr)
        print('\nUse one per line: "<claim number> <x|!|?> [-- note]", or '
              '"signoff x".', file=sys.stderr)
        sys.exit(1)
    Path(ws_path).write_text(ws)
    print(f"    applied {applied} mark(s) to {Path(ws_path).name}")


def do_mark(ws_path, marks_path):
    """Apply a batch of marks and report progress, without gating.

    Verifying 70+ claims against a long document does not fit in one turn. This lets
    the work be done in batches: mark what you have checked so far, come back, mark
    more. Only "check" gates, and it is run once at the end.
    """
    apply_marks(ws_path, marks_path)
    marks = CLAIM_RE.findall(Path(ws_path).read_text())
    left = [i for m, i in marks if m.strip() == ""]
    done = len(marks) - len(left)
    print(f"    {done} of {len(marks)} claims marked, {len(left)} remaining")
    if left:
        print(f"    still unmarked: {', '.join(left[:20])}"
              f"{' ...' if len(left) > 20 else ''}")
        print("    Continue marking, then run: verify.py check " + Path(ws_path).name)
    else:
        print("    All claims marked. Run: verify.py check " + Path(ws_path).name)


def do_check(path, marks=None):
    if marks:
        apply_marks(path, marks)
    text = Path(path).read_text()
    marks = CLAIM_RE.findall(text)
    if not marks:
        print(f"BUILD FAILED - no claim lines found in {path}", file=sys.stderr)
        sys.exit(1)
    unmarked = [i for m, i in marks if m.strip() == ""]
    wrong = [i for m, i in marks if m == "!"]
    unver = [i for m, i in marks if m == "?"]
    good = [i for m, i in marks if m.lower() == "x"]
    bad_mark = [(m, i) for m, i in marks if m.strip() and m.lower() not in "x!?"]

    errs = []
    if unmarked:
        errs.append(f"{len(unmarked)} claim(s) still unmarked: "
                    f"{', '.join(unmarked[:15])}{' ...' if len(unmarked) > 15 else ''}")
    for m, i in bad_mark:
        errs.append(f"claim {i}: '{m}' is not a valid mark (use x, !, or ?)")
    if wrong:
        errs.append(f"{len(wrong)} claim(s) marked WRONG and still present: "
                    f"{', '.join(wrong)}. Fix content.json, rebuild with build.py, "
                    f"re-extract the worksheet, and check again.")
    signoff = re.findall(r"^- \[(.)\] (Every .*)$", text, re.M)
    unsigned = [t for m, t in signoff if m.strip() == ""]
    if unsigned:
        errs.append("sign-off incomplete: " + "; ".join(unsigned))

    if errs:
        print("VERIFICATION FAILED - the guide is not ready to deliver.\n", file=sys.stderr)
        for e in errs:
            print("  * " + e, file=sys.stderr)
        sys.exit(1)

    print(f"OK  verification complete — {len(marks)} claims")
    print(f"    {len(good)} confirmed against the document")
    if unver:
        print(f"    {len(unver)} not verifiable from the document: {', '.join(unver)}")
        print("    List each of these in the post-output notes. Do not present them as "
              "verified.")
    print("    This records that the claims were checked. It does not make the guide "
          "authoritative -")
    print("    the advisor still reads it against the executed document before it "
          "reaches a client.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("extract", "mark", "check"):
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    if sys.argv[1] == "mark":
        if len(sys.argv) != 4:
            print("usage: verify.py mark worksheet.md marks.txt", file=sys.stderr)
            sys.exit(2)
        do_mark(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "extract":
        if len(sys.argv) < 4:
            print("usage: verify.py extract content.json [more.json ...] worksheet.md",
                  file=sys.stderr)
            sys.exit(2)
        do_extract(sys.argv[2:-1], sys.argv[-1])
    else:
        if len(sys.argv) not in (3, 4):
            print("usage: verify.py check worksheet.md [marks.txt]", file=sys.stderr)
            sys.exit(2)
        do_check(sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)


if __name__ == "__main__":
    main()
