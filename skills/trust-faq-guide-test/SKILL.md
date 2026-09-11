---
name: trust-faq-guide-test
description: >
  Creates estate planning document guides in two formats: (1) an interactive HTML FAQ with
  citations and collapsible sections, or (2) a simplified client-facing PowerPoint deck (~10
  slides) for client meetings. Use whenever an advisor uploads or references a trust, Will, power
  of attorney, health care proxy, HIPAA authorization, codicil, or other estate planning document
  and asks for a summary, FAQ, guide, trustee reference, meeting prep, PowerPoint, slide deck,
  client summary, or a combined family estate-plan binder. Also trigger on: "make an FAQ for this
  trust", "summarize these documents", "create a trust guide", "analyze this Will", "prep for a
  client estate meeting", "make a slide deck for this trust", "meeting deck", "build a binder for
  this family." Handles revocable living trusts (including mirror/paired), SLATs, ILITs, GRATs,
  CRTs, SNTs, other irrevocable instruments, standalone Wills, Will + Trust packages, and
  personal-document bundles.
---

<!--
v2.3 TEST COPY — named trust-faq-guide-test so it can sit alongside the live
trust-faq-guide. Both are installed during testing; if the wrong one fires, ask for
"the trust-faq-guide-test skill" by name.

TO PROMOTE TO PRODUCTION: change the frontmatter `name:` and the folder name to
trust-faq-guide. Nothing else — the build command resolves its own path.

Version history is in CHANGELOG.md, shipped alongside this file. Do not read it at run time —
it is 38KB and purely historical. It is there for whoever maintains this skill next.

NOTE FROM MATT POWELL: Works well if you upload both a husband and wife's rev trusts and say
"build a FAQ." For a whole family's documents, ask for a "family binder."
-->

# Trust & Estate Document Guide

**Your job is to read and understand the document. Not to build anything.**

The HTML guide is already built. It lives in `assets/guide-template.html` and is rendered by
`assets/build.py`. You produce a JSON file of facts extracted from the estate planning document;
the script turns it into the finished guide. You never write HTML, CSS, JavaScript, or the logo.

This is deliberate. Earlier versions had you assemble the page from a 774-line spec and it drifted
every run — that spec is longer than a file read returns, so its CSS and JS were never in what you
read. Do not reconstruct a page. Fill in facts.

---

## Step 1 — Intake

Default output is the **Detailed FAQ Guide** (interactive HTML). Don't ask which format — proceed
with the HTML guide unless the user already asked for a PowerPoint / slide deck / Client Meeting
Summary, or a Family Estate Plan Binder.

Ask this one question before reading anything, and nothing else:

```
Before I start — what documents are you working with? (One guide per document is the
default. Tell me if any are related so I can cross-link them or build a family binder.)
  - One document only (a single trust, or a single Will) -> single-column guide
  - Two mirror/paired trusts (spouses each with their own revocable living trust)
    -> side-by-side two-column guide
  - Will + Trust for one person (e.g. a pour-over Will alongside a revocable trust)
    -> combined single-column guide
  - A personal-documents bundle for one person (Will, codicil, power of attorney,
    health care proxy, HIPAA authorization) -> single-column guide
  - Several related documents across a family -> one guide per document PLUS a
    Family Estate Plan Binder index linking them
  - Base trust plus amendments: upload all of them together.
```

If the user's opening message already answers it, skip the question.

**Do not ask** about document type (confirmed from the documents in Step 3), whether the PDF is
scanned (just try, then OCR yourself), the filename (pick one), or the footer.

**Preparer name:** the footer names whoever is running this skill. Take their name from your
session context and pass it as `preparer`. Ask only if no name is available to you. The address
is always `Cerity Partners, LLC | 53 State St, 39th Floor, Boston, MA 02109` — build.py supplies
it; don't pass it.

---

## Step 2 — Read the document(s)

**Uploaded to chat** — read with your document-reading tools (use the `pdf` skill for PDFs).

**In Box** — with a file ID, call `Box:get_file_content`. With a filename,
`Box:search_files_keyword` first; if several hits, show them and ask which. If content is empty or
garbled it's a scanned PDF — run OCR yourself via the `pdf` skill (rasterize, then OCR). Only tell
the user the file can't be processed if OCR itself fails.

Read the **full text**. Never rely on previews or first/last pages.

Read **`references/reading-guide.md`** now — the reading order for each document type, and how
to handle a base trust with amendments, a Will alongside a trust, and a codicil.

---

## Step 3 — Document type and layout

**Two-column** is used *only* for two mirror/paired revocable living trusts (spouses each with
their own RLT). "Grantor 1" is whoever is named first in the preamble. Everything else is
single-column — including a single trust of any type, a standalone Will, a Will + Trust package,
a personal-documents bundle, and two irrevocable trusts.


Read **`references/section-guide.md`** now — required, not optional. It holds the document-type
signal table (confirm the type from the document itself, not from what the user called it), the
section order for each type, the `data-cat` mapping, and the per-type content requirements. If
the user stated a type up front and it conflicts with the signals, flag it and ask before
proceeding.

Branch: HTML guide -> Steps 4 and 5. PowerPoint -> Step 6. Family binder -> Step 7.

---

## Step 4 — Write `content.json` and run the build

Read **`assets/content-schema.md`** for the full field reference — including `document_sections`,
the list of every heading you found in the document, which is required and which every citation is
checked against. Then write the content file and run:

```
BUILD=$(find /mnt/skills -path '*trust-faq-guide*/assets/build.py' | head -1)
python3 "$BUILD" content.json /mnt/user-data/outputs/[Name]_Rev_Trust_FAQ_Guide.html
```

Resolve the path with `find`, don't hardcode it — the folder name differs between the test and
production copies, and `build.py` finds its own template relative to itself. If `find` returns
more than one hit, use the one whose folder matches this skill's name. If it returns nothing, say
so rather than guessing a path or writing the HTML yourself.

Pick the filename yourself — `[ClientLastName]_Rev_Trust_FAQ_Guide.html`. Mention it on delivery;
don't ask permission first.

**What build.py generates, so you never write it:** the whole `<head>`, CSS, JavaScript, the
Cerity logo, header, toolbar, footer, disclaimer, section wrappers, `data-cat`, chevrons,
`aria-expanded`/`.open` pairing, open/closed defaults, section numbering, the Quick Reference
table, the flowchart, and two-column view switching.

**What you write:** the facts. Section titles and categories, questions and answers, Quick
Reference rows, flowchart stages, tables, banners.

**Do not open `assets/guide-template.html`.** It is 30KB, so a read returns a truncated middle,
and you have no reason to see it — `build.py` reads it with Python and gets the real bytes.
Reading it can only tempt you into reproducing something. Same for `build.py` and `CHANGELOG.md`.

### Content rules

- **Every material fact carries a citation** — `"cite": "§4.2"` on a Quick Reference row, or
  `<span class="section-ref">§4.2</span>` inline in an answer. Wills use `Art. Three`; personal
  documents use `POA Art. One`. This is enforced: an answer with no citation and no NOT FOUND
  flag fails the build, as does a citation that is not in `document_sections`. An answer that is
  a general explanation rather than a provision sets `"cite": false`.
- **Never cite a section you did not read.** The build confirms a citation *exists* in the
  document; it cannot confirm it is the *right* one. Padding `document_sections` to make a
  citation pass defeats the only mechanical check on citations there is.
- **Never fabricate.** A provision you can't find gets `"not_found": true` (Quick Reference) or
  `<span class="not-found">[NOT FOUND — verify in original document]</span>` inline, and goes in
  the post-output notes.
- **Independent trustee / self-dealing.** If a beneficiary is also a trustee, or could serve as
  one, never describe them as having "full discretion" over income or principal. Check whether an
  independent trustee is required for distributions to that beneficiary; if so, the flowchart
  stage and the distribution table must say an independent trustee makes all distribution
  decisions — the beneficiary cannot direct distributions to themselves. (Per Alexander Gross
  feedback on the Pappalardo guide, 2025-05-19.)

Formatting rules — tables vs. prose, amount/lapse/N-A spans, the permitted class list, and the
Will+Trust and personal-bundle section patterns — are in `assets/content-schema.md`.

### If the build fails

It prints exactly what's wrong and writes nothing. Fix the content file and run again. **Never
work around a failure by writing the HTML yourself** — a failed build means the guide would have
been wrong. If you genuinely cannot get it to pass, tell the user what the validator is rejecting
rather than delivering something unverified.

---

## Step 5 — Verify the content against the document

**Required for every HTML guide. Do not deliver before this passes.**

`build.py` guarantees the guide is well formed. It cannot tell whether a name, amount, age or
citation is *right*. That is this step.

`build.py` already wrote the worksheet next to the guide, named
`[GuideName]_verification.md`. Mark it, then gate on it:

```
V=$(find /mnt/skills -path '*trust-faq-guide*/assets/verify.py' | head -1)
# ... re-read the document and mark every line in [GuideName]_verification.md ...
python3 "$V" check /mnt/user-data/outputs/[GuideName]_verification.md
```

If you had to fix `content.json` and rerun `build.py`, it rewrites the worksheet — mark the new
one. (`verify.py extract content.json out.md` regenerates it by hand if ever needed.)

The worksheet lists every decision-driving claim — names, amounts, ages, succession order,
distribution standards, flowchart stages, table rows, NOT FOUND flags — with its citation. Mark
each by **going back to the document**:

- `[x]` confirmed — the document says this, at this citation
- `[!]` wrong — note what the document actually says, then fix `content.json`, rerun `build.py`,
  re-extract the worksheet, and check again
- `[?]` not verifiable from the document — say why; these go in the post-output notes

A claim you did not actually look up is not `[x]`. Marking everything `[x]` without re-reading
makes the worksheet a lie and is worse than not running it — the advisor will trust it.

The worksheet also opens with "Check these first" — cross-checks that need no document
(interested-trustee conflicts, sections this document type normally has but the guide omits,
document sections never cited). Each explains itself; work them before the claims.

Deliver the worksheet alongside the guide. It is the record that the guide was checked.

---

## Step 6 — PowerPoint (Client Meeting Summary)

If the user asked for a PowerPoint, slide deck or Client Meeting Summary, read
**`references/pptx-guide.md`** and follow it.

---

## Step 7 — Family Estate Plan Binder

If the user asked for a binder, produce each individual guide via Steps 4-5 first, then read
**`references/binder-guide.md`** and follow it. Same pattern as Step 4: you write a JSON file,
`assets/build_binder.py` renders it. Set `binder` in each guide's content.json so its
back-to-index crumb is generated.

---

## Step 8 — Deliver

1. Present the file(s) with `present_files`, including the verification worksheet.
2. **Offer Box upload:** "Would you like me to upload this to the client's Box folder? If so,
   share the Box folder ID." Given an ID, read the saved file and call `Box:upload_file` with
   `file_name`, `parent_folder_id`, and `file_content`. For a binder, upload the index and every
   linked guide to the same folder so relative links resolve. Confirm with the Box file ID and link.
3. **Post-output notes** — always, in this shape:

```
POST-OUTPUT NOTES

Reference files read:
- [section-guide.md, content-schema.md, ...]

Verification (Step 5):
- [n] claims checked against the document; [n] confirmed, [n] not verifiable
- [list every [?] claim and why it could not be verified]
- [list every cross-check warning and how it was resolved]

Provisions flagged [NOT FOUND]:
- [each, with section reference]

OCR corrections made:
- [artifact] -> [corrected] (§X.XX)

Provisions to verify with client/counsel:
- [anything ambiguous or potentially incomplete]

Cross-document connections identified:
- [Will clause -> Trust article; POA -> trustee succession; etc.]
```

4. **Say plainly that the guide is unverified.** The build checks formatting, structure and
   whether each citation exists in the document — not whether any fact or citation is correct.
   Close along these lines: "Please read this against the document before it goes to a client —
   I've cited every provision, but only you can confirm each citation points at the right place.
   Let me know if you'd like changes, or this content in another format (PowerPoint, PDF, etc.)."

---

## Checklist before delivering

`build.py` already enforces the shell, logo, classes, open/closed defaults, CSP rules and
citations, and `verify.py check` gates the claim-by-claim verification. Both must have exited OK.
What neither can check, and you must:

- [ ] Full text of every document read — not previews
- [ ] Nothing fabricated; every statement traceable to the document
- [ ] Succession ladders complete and in the document's order
- [ ] **Independent trustee** — no "full discretion" where a beneficiary is trustee
- [ ] **Cross-document** — pour-over / codicil supersession / agent roles noted
- [ ] **Guardian (Wills)** — minor children addressed or flagged NOT FOUND
- [ ] the verification worksheet delivered with the guide, every `[?]` listed in the notes
- [ ] Post-output notes posted with all six sections

---

## Maintaining this skill

See `assets/README.md`. The shells are `assets/guide-template.html` and
`assets/binder-template.html`, rendered by `build.py` and `build_binder.py`. Edit those.
`references/_html-shell-ARCHIVE.md` is the pre-v2.0 shell spec, kept in the repo for historical
reference only — it is not shipped in the packaged skill and nothing reads it.

**Before writing any changelog entry, verify the change is actually in the file you claim to have
changed.** From v1.6 to v1.18 this skill accumulated five separate entries describing fixes that
were only ever written into the documentation — the shell itself never changed. Treat "the
changelog says X" as a claim to check, not a fact. After any template edit, run build.py against a
test content file and confirm it still passes.
