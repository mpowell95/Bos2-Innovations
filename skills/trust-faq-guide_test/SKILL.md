---
name: trust-faq-guide_test
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
v2.0 TEST COPY — named trust-faq-guide_test so it can sit alongside the live
trust-faq-guide. Both are installed during testing; if the wrong one fires, ask for
"the trust-faq-guide_test skill" by name.

TO PROMOTE TO PRODUCTION: change the frontmatter `name:` and the folder name to
trust-faq-guide. Nothing else — the build command resolves its own path.

v2.0 — see CHANGELOG.md for history. Do not read CHANGELOG.md at run time.

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

Reading order:
- **Trusts:** opening articles (parties, name, governing law) -> distributions (specific gifts,
  charitable residue, withdrawal schedules) -> trustee succession and powers -> administrative
  and protective provisions.
- **Wills:** opening clause (testator, date, governing law, family recitals) -> specific bequests
  and tangible personal property -> residuary estate and pour-over clause -> executor succession
  and powers -> guardian nominations -> administrative provisions.
- **POA / HCP / HIPAA / Codicil:** principal, agents and successors (acceptance dates/contacts if
  present), springing vs. immediate, activation standard, scope of powers, gifting limits (POA),
  end-of-life directives (HCP), authorized recipients (HIPAA), and exactly which prior provisions
  a codicil replaces.

Capture every party name, dollar amount, section/article heading, withdrawal schedule, named
charity, and parcel of real property. Correct OCR artifacts (mid-word capitals like "tRustee",
hyphens splitting names, run-together words, punctuation replacing letters) and note every
correction so it can be verified.

**Base trust + amendments:** the most recent restatement controls for provisions it addresses.
Record the amendment history in the Quick Reference. Flag any provision where an amendment
conflicts with the original — never silently merge them.

**Will + Trust, or a codicil:** identify any pour-over clause and note it prominently, cross-
referencing the trust. Treat the documents as one integrated plan. For a codicil, state exactly
which Will articles it replaces, and treat it as controlling for those. Never invent a connection
the documents don't state.

---

## Step 3 — Document type and layout

**Two-column** is used *only* for two mirror/paired revocable living trusts (spouses each with
their own RLT). "Grantor 1" is whoever is named first in the preamble. Everything else is
single-column — including a single trust of any type, a standalone Will, a Will + Trust package,
a personal-documents bundle, and two irrevocable trusts.

| Type | Key signals |
|---|---|
| Revocable Living Trust | "revocable," grantor = trustee, amendment/revocation reserved |
| SLAT | "spousal lifetime access," irrevocable, spouse is beneficiary, gift at creation |
| ILIT | "life insurance," irrevocable, Crummey notices, policy owned by trust |
| GRAT | "grantor retained annuity," fixed annuity to grantor, defined term |
| CRT / CRUT / CRAT | "charitable remainder," annuity or unitrust percentage |
| SNT | "special needs"/"supplemental needs," benefit preservation language |
| Other irrevocable | No revocation power, no grantor trust status, separate EIN |
| Last Will and Testament | testator, executor, probate, "give, devise, and bequeath" |
| Pour-Over Will | Will + clause directing residue to a named trust |
| Codicil | "codicil," amends specific Will articles, republishes the Will |
| Durable POA | principal, attorney-in-fact, "durable"/"springing" |
| Health Care Proxy | medical decisions, end-of-life directives |
| HIPAA Authorization | authorized recipients of PHI, capacity determination |

If the user stated a document type up front, confirm it against these signals; if it conflicts,
flag it and ask before proceeding.

Then read **`references/section-guide.md`** for the section order and per-type content
requirements. This is required, not optional — it holds the section orders for trusts by type,
Wills, combined Will+Trust, and personal-document bundles, plus the `data-cat` mapping.

Branch: HTML guide -> Step 4. PowerPoint -> Step 5. Family binder -> Step 6.

---

## Step 4 — Write `content.json` and run the build

Read **`assets/content-schema.md`** for the full field reference, then write the content file and
run:

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
  documents use `POA Art. One`.
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

Read in order: the `pptx` skill (`/mnt/skills/public/pptx/SKILL.md`), the
`cerity-partners-powerpoint-branding` skill, then `references/simplified-sections.md` for the
slide-by-slide requirements.

Extract all party names, dates, distribution standards, trustee succession and key protections
from the document — no canned text. Discussion Points must be specific to this document
(incomplete succession chains, unconfirmed elections, annual administrative requirements, any
warning flags found in review) — no generic filler. Plain language, no §citations on slides. Use
warning callouts for interested-trustee restrictions, missing successors, unconfirmed elections,
and client action items. For two mirror trusts, follow the two-column variant in that file.

Save to `/mnt/user-data/outputs/[Name]_Trust_Summary.pptx`.

---

## Step 6 — Family Estate Plan Binder

If the user asked for a binder, produce each individual guide via Step 4 first, then read
**`references/binder-guide.md`** and follow it.

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

Provisions flagged [NOT FOUND]:
- [each, with section reference]

OCR corrections made:
- [artifact] -> [corrected] (§X.XX)

Provisions to verify with client/counsel:
- [anything ambiguous or potentially incomplete]

Cross-document connections identified:
- [Will clause -> Trust article; POA -> trustee succession; etc.]
```

4. Close with: "Let me know if you'd like me to make any changes, or if you'd like this content in
   another file format (PowerPoint, PDF, etc.)."

---

## Checklist before delivering

- [ ] Full text of every document read — not previews
- [ ] All parties, amounts, percentages and dates verified against the source
- [ ] Succession ladders complete and in order
- [ ] Nothing fabricated; every statement traceable to the document
- [ ] **Independent trustee check** — no "full discretion" where a beneficiary is trustee
- [ ] **Cross-document check** — pour-over / codicil supersession / agent roles noted
- [ ] **Guardian check (Wills)** — minor children addressed or flagged NOT FOUND
- [ ] `section-guide.md` read; section order follows it; no numbering gaps
- [ ] `preparer` set to the running user's name
- [ ] build.py exited OK (it enforces the shell, logo, classes, defaults and CSP rules)
- [ ] Post-output notes posted with all five sections

---

## Maintaining this skill

The shell is `assets/guide-template.html`, rendered by `assets/build.py`. Edit those, never the
archive.

**Before writing any changelog entry, verify the change is actually in the file you claim to have
changed.** From v1.6 to v1.18 this skill accumulated five separate entries describing fixes that
were only ever written into the documentation — the shell itself never changed. Treat "the
changelog says X" as a claim to check, not a fact. After any template edit, run build.py against a
test content file and confirm it still passes.
