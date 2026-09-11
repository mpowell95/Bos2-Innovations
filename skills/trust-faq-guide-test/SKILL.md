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
v3.0 TEST COPY — named trust-faq-guide-test so it sits alongside the live trust-faq-guide
rather than replacing it. If the wrong one fires, ask for "the trust-faq-guide-test skill"
by name.

Claude writes only the facts (a content JSON), each citation carrying a verbatim quote;
assets/build.py renders them into a locked template, confirms every quote against the
document text, and refuses to write if anything is wrong.

TO PROMOTE: change the frontmatter `name:` and the folder name to trust-faq-guide. Nothing
else — the builders resolve their own paths.

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

Branch: HTML guide -> Step 4. PowerPoint -> Step 5. Family binder -> Step 6.

---

## Step 4 — Write `content.json` and run the build

Read **`assets/content-schema.md`** for the full field reference — including `document_sections`
(every heading you found, which every citation is checked against), `source_text` (the document
text you saved while reading), and `quote` (the words that confirm each citation). Then write the
content file and run:

```
BUILD=$(find /mnt/skills -path '*trust-faq-guide*/assets/build.py' | head -1)
python3 "$BUILD" content.json /mnt/user-data/outputs/[Name]_Rev_Trust_FAQ_Guide.html
```

### Content rules

- **Every material fact carries a citation** — `"cite": "§4.2"` on a Quick Reference row, or
  `<span class="section-ref">§4.2</span>` inline in an answer. Wills use `Art. Three`; personal
  documents use `POA Art. One`. An answer with no citation and no NOT FOUND flag fails the build,
  as does a citation not in `document_sections`. An answer that is a general explanation rather
  than a provision sets `"cite": false`.
- **Every citation carries a `"quote"`** — a dozen or more characters of the document's own words,
  copied verbatim, for the provision being stated. Save the document text you read to a file and
  list it in `source_text`; the build looks up every quote in it and **fails on any quote it
  cannot find**. This is how verification happens: you are already at §4.2 when you write it, so
  record the words then. Do not paraphrase, and never write a quote you have not copied.
  Tables and flowcharts take one block-level quote each, not one per row.
- **Never cite a section you did not read.** A confirmed quote proves the document contains those
  words; it does not prove they sit at the cited section, or that your summary reads them
  correctly. Padding `document_sections` or quoting the wrong passage defeats the point.
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

## Step 5 — PowerPoint (Client Meeting Summary)

If the user asked for a PowerPoint, slide deck or Client Meeting Summary, read
**`references/pptx-guide.md`** and follow it.

---

## Step 6 — Family Estate Plan Binder

If the user asked for a binder, produce each individual guide via Step 4 first, then read
**`references/binder-guide.md`** and follow it. Same pattern as Step 4: you write a JSON file,
`assets/build_binder.py` renders it. Set `binder` in each guide's content.json so its
back-to-index crumb is generated.

---

## Step 7 — Deliver

1. Present the file(s) with `present_files`.
2. **Offer Box upload:** "Would you like me to upload this to the client's Box folder? If so,
   share the Box folder ID." Given an ID, read the saved file and call `Box:upload_file` with
   `file_name`, `parent_folder_id`, and `file_content`. For a binder, upload the index and every
   linked guide to the same folder so relative links resolve. Confirm with the Box file ID and link.
3. **Post-output notes** — always, in this shape:

```
POST-OUTPUT NOTES

Reference files read:
- [section-guide.md, content-schema.md, ...]

Quotes confirmed: [n] of [n] against the document text
- [anything you could not confirm, and why]
- [every build warning and how it was resolved]

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
citations, and confirms every quote word-for-word against the document text. It must have exited OK.
What neither can check, and you must:

- [ ] Full text of every document read — not previews
- [ ] Nothing fabricated; every statement traceable to the document
- [ ] Succession ladders complete and in the document's order
- [ ] **Independent trustee** — no "full discretion" where a beneficiary is trustee
- [ ] **Cross-document** — pour-over / codicil supersession / agent roles noted
- [ ] **Guardian (Wills)** — minor children addressed or flagged NOT FOUND
- [ ] anything you could not confirm in the document listed in the post-output notes
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
