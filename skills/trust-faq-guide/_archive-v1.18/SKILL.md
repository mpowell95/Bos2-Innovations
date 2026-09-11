---
name: trust-faq-guide
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
Last Modified: August 19, 2026
Note: Repackaged and re-uploaded on August 19, 2026 (shortened the description to fit the
  1024-character limit). No content changes.
Change: v1.5 — Applied the Cerity Partners brand theme to the locked shell (cobalt masthead with
  the Cerity logo, DM Sans + Cormorant fonts, brand palette, colorblind-safe section colors,
  distinct banner icon shapes, "Built by Matt Powell · BOS2" byline + footer disclaimer). Added
  references/cerity-logo.svg. Built on v1.4, which restored/locked the HTML shell as the single
  source of truth (references/html-shell.md, copied verbatim — earlier versions regenerated it
  from memory and drifted), corrected the shell docs to match reality
  (filterSections/toggleSection/toggleQ/expandAll/collapseAll, inline onclick on <button>s, setView
  for two-column), replaced emojis with SVG icons, formalized personal documents (Durable POA,
  Health Care Proxy, HIPAA, Codicil), added the Family Estate Plan Binder, and rebuilt/tested the
  two-column mirror-trust mode.

NOTE FROM MATT POWELL: Works well if you upload both a husband and wife's rev trusts and say
"build a FAQ." For a whole family's documents, ask for a "family binder."
-->

# Trust & Estate Document Guide

Produces either (A) a polished interactive HTML FAQ guide or (B) a client-facing PowerPoint summary deck from one or more estate planning documents (trusts, Wills, personal directives, or a mix). For a family with several related documents, it can also produce a linked **Family Estate Plan Binder** (an index that ties the individual guides together).

## Reference Files

- `references/html-shell.md` — The locked CSS, JavaScript, component snippets, and HTML structure for the HTML output (Cerity Partners theme). **Read this before writing a single line of HTML, and copy the `<style>`/`<script>` blocks verbatim. (HTML modes only.)**
- `references/cerity-logo.svg` — The Cerity Partners logo as a complete, self-contained inline `<svg class="hdr-logo">` element. Read this file and paste its exact contents in place of the logo in the header markup — do not retype it, and never wrap it in (or replace it with) an `<img>` tag or a `data:` URI: these guides are hosted on a platform whose CSP silently blocks any image loaded from a URL, so a `data:` URI renders as a blank header with no error. (HTML modes only.)
- `references/section-guide.md` — Content requirements by document type (trusts, Wills, POA, health care proxy, HIPAA, codicil). Read once the document type is confirmed in Step 3. (HTML modes only.)
- `references/simplified-sections.md` — Slide-by-slide content requirements for the Client Meeting Summary PPTX. **Read this before building any slides. (Simplified mode only.)**

---

## Step 1 — Intake (Required Before Reading Any Document)

Default output format is the **Detailed FAQ Guide** (interactive HTML). Do not ask which format the user wants — proceed with the interactive HTML guide unless the user's message already states otherwise (e.g., they explicitly ask for a PowerPoint / Client Meeting Summary / slide deck up front, or ask for a Family Estate Plan Binder). If they later want the content in another format, that's handled after delivery (see Step 5 note on offering other formats).

Ask the following before doing anything else. Only question 2 is required up front.

```
Before I start:

2. What documents are you working with? (One guide per document is the default. Tell me if any
   are related so I can cross-link them or build a family binder.)
   - One document only (a single trust, or a single Will) → single-column guide
   - Two mirror/paired trusts (e.g., spouses each with their own revocable living trust)
     → side-by-side two-column guide
   - Will + Trust for one person (e.g., a pour-over Will alongside a revocable trust)
     → combined single-column guide
   - A personal-documents bundle for one person (Will, codicil, power of attorney, health care
     proxy, HIPAA authorization) → single-column "personal legal documents" guide
   - Several related documents across a family (multiple people/trusts/wills) → I can produce one
     guide per document PLUS a Family Estate Plan Binder index that links them together
   - If you have a base trust plus amendments, upload all of them together.
```

Document type (revocable living trust, SLAT, ILIT, Last Will and Testament, durable power of attorney, etc.) is confirmed from the documents themselves in Step 3 — do not ask.

Do not ask whether the documents are text-searchable or scanned image-only. Just attempt to read them (Step 2) — if extraction comes back empty or garbled, that's when you tell the user and handle OCR yourself (see Step 2).

Do not ask what the output file should be named. Choose an appropriate filename yourself and proceed (see Step 5 naming convention below) — mention the filename you chose when you deliver the file, but don't ask permission first.

**Note on footer:** The preparer footer is always Matt Powell | Cerity Partners, LLC | 53 State St, 39th Floor, Boston, MA 02109. Do not ask the user about this.

Do not proceed until you have an answer to question 2 (document relationship). If the user's opening message already answers it (e.g., they uploaded one document and said "build a FAQ for this"), apply that and skip asking.

---

## Step 2 — Locate and Read the Document(s)

### Locating the document

**A. Uploaded directly to chat** — read it using your document-reading capabilities. For PDFs, use the pdf-reading skill if needed.

**B. Stored in Box** — if the user provides a Box file ID, link, or filename:
1. If given a file ID, call `Box:get_file_content` with that ID.
2. If given a filename/description, call `Box:search_files_keyword` first. If more than one result, show the list and ask which file to use before reading.
3. Call `Box:get_file_content` with the confirmed file ID (returns full text in one call).
4. If the content is empty or garbled (common for scanned PDFs), run OCR yourself — see "Scanned / image-only documents" below. Do not stop and hand this back to the user unless OCR itself fails.

### Reading the document

Read the full text of each document. Reading order by type:

- **Trusts:** (1) opening articles — parties, trust name, governing law; (2) distribution articles — specific gifts, charitable residue, withdrawal schedules; (3) trustee succession and powers; (4) administrative and protective provisions.
- **Wills:** (1) opening clause — testator, execution date, governing law, family recitals; (2) specific bequests and tangible personal property; (3) residuary estate and pour-over clause (if any); (4) executor/personal representative succession and powers; (5) guardian nominations; (6) administrative provisions.
- **Durable POA / Health Care Proxy / HIPAA / Codicil:** identify the principal, the agent(s) and successors (with acceptance dates/contacts if present), whether powers are springing or immediate, activation/incapacity standard, scope of powers, gifting limits (POA), end-of-life directives (HCP), authorized recipients (HIPAA), and exactly which prior-document provisions a codicil replaces.

General rules:
- Do not rely on previews or first/last pages alone.
- Capture all party names, all dollar amounts, all section/article headings, withdrawal schedules, named charities, and real property.
- Correct OCR artifacts in the output — watch for mid-word capitalization ("tRustee"), hyphens splitting names, run-together words, punctuation replacing letters. Note every correction so it can be verified.
- If you cannot extract readable text even after OCR (see below), stop and tell the user specifically what failed.

### Scanned / image-only documents

Don't ask the user in advance whether a document is text-searchable — just try to extract text normally first. If extraction is empty, near-empty, or clearly garbled, treat it as a scanned/image-only document and run OCR yourself using the `pdf-reading` skill (rasterize pages, then OCR extraction — see that skill's OCR guidance for the tooling). Only fall back to telling the user the file needs to be reprocessed outside this session if OCR itself fails to produce usable text (e.g., illegible scan quality, corrupted file). When that happens, say plainly what you tried and what didn't work, rather than asking upfront whether the file is scanned.

### Base trust + amendments uploaded together
- Treat the most recent restatement/amendment as controlling for provisions it addresses.
- Note the amendment history (original date, amendment dates) in the Quick Reference.
- Flag any provision where an amendment conflicts with or modifies the original — do not silently merge them.

### Will + Trust, or a codicil, uploaded together
- Identify any pour-over clause (Will language directing the residuary estate into the trust); note it prominently and cross-reference to the trust.
- Treat the documents as an integrated plan; note where provisions interact (e.g., "Residuary estate pours into the [Trust Name] under Article X").
- For a codicil, state exactly which Will articles it replaces or deletes, and treat the codicil as controlling for those.
- Do not fabricate connections that are not expressly stated.

---

## Step 3 — Identify Document Type and Layout

**Layout decision:**
- **Two-column side-by-side** — use exclusively for two mirror/paired revocable living trusts (spouses each with their own RLT). Each grantor gets a column; "Grantor 1" is whoever is named first in the document preamble. Mark matching provisions with an `identical-row` + `badge-identical`; put differing provisions in a `two-col` block. Include a "Key Differences" section only if there are material differences beyond grantor/spouse role reversal.
- **Single-column** — everything else: a single trust of any type, a standalone Will, a combined Will + Trust package, a personal-documents bundle, and irrevocable trusts even when two are provided (two-column is reserved for mirror/paired RLTs).

**Document type detection** — look for these signals:

| Document Type | Key Signals |
|---|---|
| Revocable Living Trust | "revocable," grantor = trustee, amendment/revocation powers reserved, grantor-trust income tax status |
| SLAT | "spousal lifetime access," irrevocable, spouse is beneficiary, gift transfer at creation |
| ILIT | "life insurance," irrevocable, Crummey notices, policy owned by trust |
| GRAT | "grantor retained annuity," fixed annuity back to grantor, defined term |
| CRT / CRUT / CRAT | "charitable remainder," annuity or unitrust percentage, charitable remainder beneficiary |
| SNT | "special needs," "supplemental needs," government benefit preservation language |
| Other irrevocable | No revocation power, no grantor trust status, separate EIN from creation |
| Last Will and Testament | "last will and testament," testator, executor/personal representative, probate, "I give, devise, and bequeath" |
| Pour-Over Will | Will + explicit clause directing residuary estate to a named trust |
| Codicil | "codicil," amends/replaces specific Will articles, re-executes/republishes the Will |
| Durable Power of Attorney | "power of attorney," principal, attorney-in-fact, "durable"/"springing," financial powers |
| Health Care Proxy | "health care proxy"/"agent," medical decisions, activation on incapacity, end-of-life directives |
| HIPAA Authorization | "HIPAA," authorized recipients of protected health information, capacity determination |

If the user answered Question 3, confirm it against these signals; if it conflicts, flag it and ask before proceeding.

**Mode branch after Step 3:**
- **Detailed FAQ mode (HTML)** → read `references/section-guide.md` for the appropriate section list, then proceed to Step 4A.
- **Simplified (PPTX) mode** → read `references/simplified-sections.md`, then proceed to Step 4B.

---

## Step 4A — Build the HTML (Detailed FAQ Mode only)

**Read `references/html-shell.md` first and copy its `<style>` and `<script>` blocks verbatim.** Do not invent, rename, or minify class names or JS functions — use only what the shell defines (`toggleSection`, `toggleQ`, `filterSections`, `setView`, `expandAll`, `collapseAll`). Assemble the page from the component snippets in the shell; your job is to fill them with real facts.

**Section color categories (`data-cat`):** every `.faq-section` needs a `data-cat` (`overview` / `trustee` / `lifecycle` / `distribution` / `legal`) per the mapping table in html-shell.md Part 5. This drives both the header color and the category filter.

**Default open/closed state:** follow the table in html-shell.md Part 5 exactly — §2 open with its first question open; §3–§4 open with questions closed; §5 onward fully closed. A section's `aria-expanded` must always match its body's `.open` (and each question's `aria-expanded` its answer's `.open`).

**Flowchart (Trust Structure Overview):** use the flowchart snippet. Populate each stage with the actual terms; mark the stage in effect right now with `.active-now`. Do not replace the diagram with prose. For two-column guides where both trusts share the flow, wrap it in an `identical-row`.

**Two-column guides:** set `<body data-view="both">` and add the View button group (`setView('both'|'g1'|'g2'|'same', this)`); the four mode strings never change, only the visible button labels (grantor names) do. Use `two-col` for differing provisions and `identical-row` for matching ones.

**Will + Trust combined guides:** add a "Document Overview" `info-banner` near the top identifying both documents. Will sections follow the trust sections unless a pour-over structure makes another order clearer; where a pour-over exists, add a cross-reference note in the trust's "Administration Upon Death" section pointing to the Will's Residuary Estate section.

**Personal-documents bundle:** cover each document as its own section (Will/Codicil, POA, Health Care Proxy, HIPAA), then close with a "How These Documents Work Together" section — a scenario table mapping life events (competent → incapacitated financial → incapacitated medical → death) to the governing document and who acts. Use `doc-badge` to show each document's Box doc id where known.

**Universal rules:**
- Never use emojis. Use the SVG icons and CSS chevrons defined in html-shell.md Part 4.A (warning triangle / flag octagon / info circle / printer / check; `.chevron`, `.flow-arrow`). Each banner type has a distinct icon shape so severity reads without relying on color (colorblind-safe).
- **Cerity theme & branding:** the shell IS the Cerity Partners theme (cobalt masthead, brand palette, DM Sans + Cormorant font stacks with system-font fallback, colorblind-safe section colors). No Google Fonts `<link>` — the hosting CSP blocks it silently, so it's deliberately absent from the shell; the font-family stacks already fall through correctly. Include the `<meta author>`/byline tags from html-shell.md Part 1; insert the logo by reading `references/cerity-logo.svg` and pasting its exact contents (a complete inline `<svg class="hdr-logo">`) into the header — never retype it, and never substitute an `<img>`/`data:` URI. No byline anywhere in the header or toolbar — "Built by Matt Powell · BOS2" only ever appears in the footer's `.attrib`, alongside the disclaimer. Keep the masthead compact — survivor/active-event context goes in a `warning-banner` at the top of `<main>`, not a second header bar.
- All dollar amounts/fractions in `<span class="amt">`; distributions that lapse in `<span class="amt-lapse">`; inapplicable provisions in `<span class="na">`.
- Every material fact carries a `<span class="section-ref">§X.XX</span>` citation (Wills: `Art. Three`; personal docs: `POA Art. One`).
- Tables for distributions, trustees/executors, charities, withdrawal schedules, and agent succession — never prose lists for these.
- No fabrication — if a provision is not found, flag it with `<span class="not-found">[NOT FOUND — verify in original document]</span>` and list it in the post-output notes.
- **Independent trustee / self-dealing rule:** if a beneficiary is also a trustee (or could serve as one), never describe that beneficiary as having "full discretion" over income/principal. Check whether an independent trustee is required to make distributions to that beneficiary; if so, the flowchart box and distribution table must state that an independent trustee makes all distribution decisions — the beneficiary cannot self-direct distributions to themselves. (Rule added 2025-05-19 per Alexander Gross feedback on the Pappalardo trust guide.)

**Section orders** live in `references/section-guide.md` (trust-type-specific, Will, combined Will+Trust, and personal-documents-bundle orders). Always start with §1 Quick Reference (a non-collapsible `.quick-ref`) and number collapsible sections from §2; omit sections that don't apply.

---

## Step 4B — Build the PPTX (Simplified Client Summary Mode only)

Before writing any slides, read **both** in order:
1. `pptx` skill (`/mnt/skills/public/pptx/SKILL.md`)
2. `cerity-partners-powerpoint-branding` skill (`/mnt/skills/user/cerity-partners-powerpoint-branding/SKILL.md`)

Then read `references/simplified-sections.md` for the slide-by-slide requirements.

**Content extraction rules:**
- Extract all party names, dates, distribution standards, trustee succession, and key protections directly from the document — no canned text.
- Action items on the Discussion Points slide must be specific to this document (incomplete succession chains, unconfirmed elections, annual administrative requirements, any warning flags raised during review). No generic filler.
- For two mirror trusts, follow the two-column variant guidance in `references/simplified-sections.md`.
- Plain language throughout. No §citations on slides. Use warning callout bullets for interested-trustee restrictions, missing successors, unconfirmed elections, or items needing client action. (In slides these callouts may use the branding skill's warning styling; the "no emoji" HTML rule applies only to the HTML modes.)

**Output:** Save as `/mnt/user-data/outputs/[filename].pptx`

---

## Step 4C — Build the Family Estate Plan Binder (optional, when several related documents are provided)

When the user asks for a family binder (or confirms it in Step 1), first produce each individual document guide per Step 4A, then build one index page by copying the binder `<style>` block and component snippets from `html-shell.md` **Part 6** verbatim (the binder is a panel-based index and needs no `<script>`):

- **Filename:** `[FamilyName]_Estate_Plan_Index.html`, saved alongside the individual guides (relative links only, so the folder stays portable and can be uploaded to Box together).
- **Header:** family name, as-of date, and a `context-banner` for any family-wide status (e.g., a spouse's death).
- **Document inventory** — a table of every document (owner, document, type, date, status: Active / Revocable / Now Irrevocable / Superseded, and a relative link to its guide).
- **Who's Who** — a table listing each person and their roles collated across every document.
- **How the Plan Works Together** — a family timeline (both competent → one incapacitated → first death → second death → next generation) naming which document controls at each stage.
- **Action Items Across the Plan** — aggregate the warning/flag items surfaced in the individual guides into one list.
- In each individual guide, add the `binder-link` back-to-index banner (html-shell.md Part 4.B) and hyperlink real cross-references (pour-over → trust guide, spouse's trust, related trust) using relative paths.

---

## Step 5 — Output

### Choosing the filename
Don't ask the user what to name the output file. Pick a clear, appropriate name yourself and proceed — e.g. `[ClientLastName]_Rev_Trust_FAQ_Guide.html`, `[FamilyLastName]_Estate_Plan_Index.html` for a binder, or `[ClientLastName]_Trust_Summary.pptx` for a Client Meeting Summary. Use names/relationships identified from the document(s) (e.g. `Krasker_Rev_Trust_FAQ_Guide.html`, `Tse_Trust_FAQ.html`). The exact name isn't critical — just make it identifiable. Mention the filename you used when you present the file; don't ask permission beforehand.

### Detailed FAQ Mode (HTML) and Family Binder
1. Save each file to `/mnt/user-data/outputs/[filename].html`.
2. Present the file(s) with `present_files`.
3. **Offer to upload to Box** — ask: "Would you like me to upload this to the client's Box folder? If so, share the Box folder ID."
   - If given a folder ID: read the saved file(s), then call `Box:upload_file` with `file_name=[filename].html`, `parent_folder_id=[provided ID]`, and `file_content=[full HTML string]`. For a binder, upload the index and all linked guides to the same folder so relative links resolve.
   - Confirm each upload with the resulting Box file ID and a direct link.
4. **Close with an offer to revise or convert.** After presenting the file (and the Box offer/post-output notes), end your response along the lines of: "Let me know if you'd like me to make any changes, or if you'd like this content in another file format (PowerPoint, PDF, etc.)."

### Simplified Summary Mode (PPTX)
1. Save to `/mnt/user-data/outputs/[filename].pptx`.
2. Present with `present_files`.
3. Offer to upload to Box (same as above; `file_name=[filename].pptx`).
4. Close with the same offer as above — changes, or another file format.

### Post-output notes (all modes)
After presenting and uploading, post a structured notes block:

```
POST-OUTPUT NOTES

Provisions flagged [NOT FOUND]:
- [list each, with section reference]

OCR corrections made:
- [original artifact] -> [corrected text] (§X.XX)

Provisions to verify with client/counsel:
- [anything ambiguous or potentially incomplete]

Cross-document connections identified:
- [Will clause -> Trust article; POA -> trustee succession; etc.]
```

---

## Quality Checklist (verify before saving)

### Both Modes
- [ ] All named parties (grantors/testators, trustees/executors, beneficiaries, guardians, agents) confirmed against source document(s)
- [ ] All dollar amounts, percentages, and dates verified against source
- [ ] Trustee/executor/agent succession ladders complete and in correct order
- [ ] No fabricated provisions — every statement traceable to the document
- [ ] **Independent trustee check:** if a beneficiary is also a trustee, output does NOT say "full discretion" — distribution authority correctly attributed to an independent trustee where required
- [ ] **Cross-document check:** pour-over / codicil-supersession / agent-role connections identified and noted
- [ ] **Guardian check (Wills):** if minor children named, guardians addressed or flagged [NOT FOUND]
- [ ] File(s) given an appropriate, identifiable name (chosen by Claude — see Step 5 naming convention)
- [ ] Post-output notes block posted with all four sections

### Detailed FAQ Mode (HTML) only
- [ ] Logo is an inline `<svg class="hdr-logo">` pasted verbatim from `references/cerity-logo.svg` — search the file for `<img` and `data:image`; both must return zero hits
- [ ] No `mask:`/`-webkit-mask:`/`background-image:` rule anywhere in the output references a `url("data:...")` — chevrons and any other icon must be pure CSS (border-triangle, `currentColor` fill on inline `<svg>`) or a real `<svg>` element, never a `data:`-URI image or mask; this CSP blocks those exactly like it blocks `<img src="data:...">`
- [ ] `<style>` and `<script>` copied verbatim from html-shell.md (no drift, no renamed classes/functions)
- [ ] Layout (single vs. two-column) matches the user's answer to Question 2
- [ ] Document type(s) correctly identified; section order follows section-guide.md
- [ ] Quick Reference (§1) uses the paired `.qr-table` layout: two label/value pairs per row, with the "Successor trustees" row spanning full width as a `.qr-num-list` numbered chip list. Multi-person values (Grantors, Remainder beneficiaries, etc.) MUST stack one per line via `<ul class="qr-people">` — never combine names with `·` or `,` on a single line. Highlight 1–2 must-catch facts with `<span class="qr-hl">` (e.g. current amendment date, payout ages). Every value cell that has a citation keeps its `.section-ref`.
- [ ] Flowchart stage titles (`.stage-label`) are real 15px sentence-case headers, not tiny corner labels. Titles name the *event* (e.g. "First Death", "Family Trust") not a category (avoid vague labels like "Stage 1").
- [ ] `--maxw` is `1240px` in both the guide's `:root` and (for a binder) the binder's own `:root` — a binder missing its own `--maxw` definition silently falls back to `max-width: none` (uncapped width), not an error
- [ ] Two-column guides (`data-view="both"`) have the toolbar split into two `.toolbar-inner.toolbar-row` rows (View + Print on row 1, Show/filters + Expand/Collapse on row 2) — never one crowded row, and never Print duplicated on both rows
- [ ] Header carries no byline (it's in the footer's `.attrib` only)
- [ ] Open/closed defaults match Part 5's table exactly — §2–4 open, §5 onward CLOSED (`aria-expanded="false"`, no `.open` class). This is the single biggest lever on whether the guide fits one screen; a section left open past §4 adds real height for no reason.
- [ ] `data-cat` on every `.faq-section`; open/closed defaults follow html-shell.md Part 5
- [ ] Section titles/questions are `<button>` with matching `aria-expanded` and `.open`
- [ ] No emojis anywhere — SVG icons and CSS chevrons only
- [ ] Two-column only: View buttons labeled with grantor names; `setView` mode strings unchanged
- [ ] Binder only: every cross-link is relative and resolves to a delivered file
- [ ] Footer reads: Matt Powell | Cerity Partners, LLC | 53 State St, 39th Floor, Boston, MA 02109

### Simplified Summary Mode (PPTX) only
- [ ] CP branding applied per cerity-partners-powerpoint-branding skill
- [ ] "Trust at a Glance" slide has accurate type, date, parties, governing law, GST status
- [ ] Distributions slide uses decision-flowchart format, not prose
- [ ] CAN/CANNOT table included if a beneficiary also serves as trustee
- [ ] Discussion Points slide has 6–10 document-specific items — no generic filler
- [ ] Warning callouts present for interested-trustee restrictions, missing successors, unconfirmed elections
- [ ] Special Provisions slide omitted if none apply
- [ ] Plain language throughout — no §citations, no verbatim legal language on slides

---

<!--
CHANGELOG

v1.18 — 2026-09 — Two more stale changelog claims: --maxw never widened, two-column toolbar never split
  Fixed: v1.8's changelog (below) claimed `--maxw` was widened from 1040px to 1240px and a 760px
         cap was added to `.faq-a`. Same drift as everything else in this session — html-shell.md's
         actual `:root` still said `1040px` and `.faq-a` had no max-width at all. Now really 1240px,
         and `.faq-a` really has `max-width: 760px`.
  Fixed: v1.8 also claimed fixing the binder template's undefined `--maxw` (referenced twice via
         `var(--maxw)` but never declared in the binder's own `:root`, silently falling back to
         `max-width: none`). The binder's `:root` still had no `--maxw` at all. Added
         `--maxw: 1240px` to match the guide.
  Fixed: v1.7's changelog claimed the two-column toolbar (Part 4.J) was split into two rows via
         `.toolbar-inner.toolbar-row` — View + Print on row 1, Show/filters + Expand/Collapse on
         row 2 — specifically to stop the View group and Show/filter group cramming into one row
         that "wrapped unpredictably." Neither the `.toolbar-row` class nor any two-row structure
         existed anywhere in html-shell.md; Part 4.J still showed the View group being appended
         into the single shared `.toolbar-inner`, exactly the cramped layout v1.7 said was fixed.
         Added the real two-row markup and the `.toolbar-row` divider CSS; Print now appears once
         (row 1) instead of being at risk of ending up on both rows.
  Added: Quality Checklist lines for `--maxw: 1240px` (guide and binder) and the two-column
         toolbar's two-row structure.
  Note: at this point five separate instances of the same failure mode have turned up in one
        sweep (logo, byline, Quick Reference/flowchart, `--maxw`, two-column toolbar) — a
        changelog entry got written and/or SKILL.md got updated to describe a fix, but the actual
        html-shell.md CSS/markup never changed to match. Worth treating "changelog says X" as a
        claim to verify against the real file, not a fact about the file, until this skill's
        update process gets a step that diffs the shell against what the changelog just described.

v1.17 — 2026-09 — Quick Reference & flowchart: SKILL.md said .qr-table, html-shell.md still had .qr-hero
  Fixed: v1.14 (below) added the checklist line and changelog entry for the paired `.qr-table`
         layout and the real flowchart headers — but, same drift pattern as the logo and byline
         bugs, only SKILL.md got updated. html-shell.md's actual Part 2 `<style>` block and Part
         4.D/4.G markup still had the old `.qr-hero`/`.qr-grid` two-tier CSS (v1.13) untouched, so
         every guide since v1.14 kept shipping the v1.13 hero/grid design while SKILL.md's
         checklist described a `.qr-table` that didn't exist anywhere in the actual shell.
  Changed: html-shell.md Part 2 now has the real `.qr-table` CSS (`.qr-k`/`.qr-v`/`.qr-v-wide`,
           `.qr-hl` highlight, `.qr-people` stacked-name list, `.qr-num-list`/`.n`/`.qr-diff-badge`
           numbered successor-trustee chips, 820px mobile stacking breakpoint) in place of the old
           `.qr-hero`/`.qr-grid`/`.qr-fact`/`.qr-label`/`.qr-value` rules. Part 4.D rewritten with
           the paired-table markup and the same fill-in rules SKILL.md's checklist already
           described.
  Changed: html-shell.md's flowchart CSS (`.stage-label`) promoted from the 11px uppercase corner
           label to the real 15px sentence-case title with a colored dot marker, `.stage-content`
           indented beneath it, exactly as v1.14's changelog described. Part 4.G updated to require
           event-based titles ("First Death") over category labels ("Stage 1", "Active Now").

v1.16 — 2026-09 — Header byline regressed back, fixed for real; orphaned onerror leftover cleaned up
  Fixed: v1.11 (below) said the header byline was removed since the footer's `.attrib` already
         carries it, and added a checklist line for it — but v1.15's own edits (this same session,
         earlier) left `.hdr-byline`/`.hdr-bottom` byline markup sitting in both the guide header
         (Part 4.B) and the binder header (Part 6), so every guide kept showing "Built by Matt
         Powell · BOS2" directly under the header, right above the toolbar. Same drift pattern as
         the v1.6/v1.15 logo bug: the checklist said one thing, the live markup said another.
         Removed `.hdr-byline` from both headers for real this time. `.hdr-bottom` in the guide
         header (Part 4.B) now holds only the binder crumb and is omitted entirely for a standalone
         guide (nothing else to right-align there). The binder header (Part 6) dropped `.hdr-bottom`
         entirely — it held nothing but the byline. Removed the now-dead `.hdr-byline` CSS rule from
         both style blocks (Part 2 and the binder's own block) and simplified `.hdr-bottom`'s
         `justify-content` since it no longer needs to split crumb-left/byline-right.
  Fixed: The Part 1 logo comment (`<!-- PASTE inline <svg>… -->`) had a stray orphaned
         `onerror="...">` line dangling after it in Part 4.B — a leftover from the v1.15 edit that
         replaced the old `<img ...>` tag (which spanned two physical lines: the src attribute,
         then a continuation line with onerror closing the tag) but only matched and replaced the
         first line, leaving the second as dead text in the middle of the header markup. Removed.

v1.15 — 2026-09 — Logo bug actually fixed this time; two more CSP-blocked assets found
  Fixed: v1.6 claimed the img/data:-URI logo bug was fixed, but only SKILL.md's reference-file
         description and checklist line were updated to describe inline <svg> — html-shell.md's
         actual Part 1 logo note, Part 4.B header markup, the two-column "Fonts + logo" note, and
         Part 6 all still built `<img class="hdr-logo" src="data:image/png;base64,...">` and still
         pointed at a `references/cerity-logo.txt` data-URI file. So every guide from v1.6 through
         v1.14 shipped with the exact same silently-blank/fallback-text logo v1.6 said it fixed.
         html-shell.md now matches SKILL.md: all four spots paste inline <svg> from
         references/cerity-logo.svg verbatim, with class="hdr-logo" added since the asset's own
         class is "cp-logo". CSS `.hdr-logo` rule updated to also match `.hdr-logo.cp-logo` and a
         bare `<svg>` child so sizing applies regardless of which class ends up on the element.
  Fixed: `.chevron` (the accordion/section-toggle caret) was drawn with `-webkit-mask/mask:
         url("data:image/svg+xml,...")`. Same CSP that blocks `<img src="data:...">` also blocks
         mask/background-image `url(data:...)` — so every expand/collapse chevron in every shipped
         guide was invisible (the element took up space, just rendered nothing). Replaced with a
         pure CSS border-triangle (`border-width` trick, no data: URI, no mask) — same technique
         `.flow-arrow` already used correctly elsewhere in this same file.
  Fixed: The Part 1 `<head>` included a `fonts.googleapis.com` `<link rel="stylesheet">` for DM
         Sans/Cormorant Garamond. Same CSP with no allowance for external stylesheets blocks this
         too, so the fonts never loaded — lower severity than the logo/chevron (the font-family
         stacks already fall through to system-ui/Segoe UI/Arial/serif, so the page still looked
         fine, just not in the literal brand typeface). Removed the dead <link> tags and replaced
         with a comment explaining the fallback is expected, not a bug to keep re-"fixing."
  Added: Quality Checklist line — grep output for `mask:`, `background-image`, and `url("data`
         near `.chevron`/icons, not just near the logo; zero hits required across all three.
  Changed (behavioral, same session): Step 1 no longer asks which output format, whether documents
           are text-searchable, or what to name the file — defaults to Detailed FAQ Guide, attempts
           extraction and self-serves OCR via the pdf-reading skill before telling the user
           anything is wrong, and picks an identifiable filename (e.g. Krasker_Rev_Trust_FAQ_
           Guide.html) without asking. Step 5 now closes every delivery with an offer to revise or
           convert to another format (PowerPoint, PDF, etc.).

v1.14 — 2026-09 — Paired-column QR table, stacked people, real flowchart headers
  Changed: Quick Reference (§1) rebuilt from `.qr-hero` + `.qr-grid` (v1.13) to a single dense
           `.qr-table` — a paired two-column facts table: rows of `label · value | label · value`.
           A reader glances top-to-bottom on either side to hunt for a specific fact, and the
           label sits right next to its value rather than above it. Highlights (`.qr-hl`, a yellow
           marker underline) call out the 1–2 must-catch facts (e.g. current amendment date,
           payout ages). Citations render as small greyish monospaced chips scoped inside the
           table so they don't compete with answers.
  Added: `.qr-people` — multi-person values (Grantors, Remainder beneficiaries) MUST stack one per
         line via `<ul class="qr-people">`. Combining names with `·` or `,` inline in a value cell
         makes both names harder to parse; stacked one-per-line reads instantly.
  Added: `.qr-num-list` + `.qr-diff-badge` — the Successor trustees row spans the full width and
         uses a numbered chip list (1, 2, 3, 4). If exactly one tier differs between mirror
         trusts, `.qr-diff-badge` sits inline on that specific `<li>` as a small yellow
         "ONLY DIFFERENCE" badge so the eye lands on the differing tier immediately.
  Removed: `.qr-hero`, `.qr-hero-fact`, `.qr-hero-label`, `.qr-hero-value`, `.qr-grid`, `.qr-fact`,
           `.qr-label`, `.qr-value` — replaced by `.qr-table` and its child classes. The old
           tier-1/tier-2 vertical split forced a rigid "hero fact" concept that didn't accommodate
           facts that don't naturally headline (payout ages, distribution standard); the paired
           table has no forced hierarchy — highlighting selects the eye-catches instead.
  Changed: Flowchart `.stage-label` promoted from a tiny 11px uppercase corner label to a real
           15px sentence-case title with a small colored dot marker. Body text (`.stage-content`)
           now indents beneath the title so the visual hierarchy is unmistakable. Active-now stage
           inherits the title styling with the mandarin/orange palette. Rationale: a reader
           scanning the flowchart should see the sequence of stages (Now → First Death → Family/
           Marital → Second Death → Children) without reading paragraphs to identify which is
           which. Old labels were the same visual weight as citation refs; new ones are actual
           headers. Part 4.G also updated to require specific event-based titles ("First Death")
           over category labels ("Stage 1", "Active Now").

v1.13 — 2026-09 — Quick Reference two-tier: hero + supporting
  Changed: Quick Reference is now two visually distinct tiers instead of one flat grid of
           same-weight facts. Tier 1 (`.qr-hero`) is a 3–4 fact strip with 22px values —
           WHO the document is for, WHERE (state), WHO the kids are, WHO's in charge if the client
           can't act. These are the questions someone actually asks on a call; they get real
           visual weight so the reader's eye lands on them first. Tier 2 (`.qr-grid`) is the
           previous 3-column aligned grid at normal size, for supporting facts (dates,
           revocability, exact trust names, corporate fallback, full children list with birth
           years).
  Removed: `.qr-group-label` sub-headers (FAMILY, TRUSTEES). The hero/supporting hierarchy handles
           the visual grouping; row labels were adding vertical space without adding scannability.
  Changed: Section-ref citations inside Quick Reference render quieter (no background chip, light
           grey, smaller) so answers aren't visually competing with their own footnotes on a
           glance. Citations elsewhere in the guide are unchanged.
  Rationale: earlier iterations (v1.8–v1.12) kept iterating on chip layout — grid vs flex,
             stretched vs content-sized, one grid vs per-group grids — but never addressed that
             every fact had the same visual weight. "Glance-during-a-call" needs a clear
             information hierarchy, not just alignment tuning.

v1.12 — 2026-09 — Reverted snapshot sentence; real fixes for layout and page height
  Reverted: v1.11's `.qr-snapshot` plain-English sentence. Explicit feedback: the ask was never
            about wording or prose — it was about layout and how information is displayed. Adding
            a sentence didn't address that at all. Removed `.qr-snapshot` from Part 2 and Part 4.D
            entirely; Quick Reference goes straight from the header bar into facts again.
  Changed: Quick Reference is a real aligned grid again — `grid-template-columns: repeat(3, 1fr)`
           (2 columns under 900px, 1 under 560px), one shared grid per Quick Reference with
           `.qr-group-label` spanning the full row to start each group on a fresh row. v1.10's
           content-sized flex chips were reordered/removed: chips don't align into scannable
           columns, which works against "understand it at a glance" even though it solved the
           stretching problem. A fixed small column count means at most the last row of a group
           is partially filled (e.g. a lone fact leaves 2 trailing empty cells) — a normal grid
           ending, not the dangling-cell bug from v1.8/v1.9 where up to 4-5 cells were empty.
  Fixed: The shipped sample had §5, §6, and §7 marked `aria-expanded="true"` with `.section-body
         open` — directly violating Part 5's own rule that only §2–4 default open and §5 onward
         defaults closed. This alone added ~850px of unnecessary height to the sample. Added a
         checklist line specifically for this, since it's the single biggest lever on page height.
  Clarified (not a shell change): a real multi-section reference guide with §2–4 open by default
           (Key Differences/flowchart/Family Info) plus Quick Reference will still exceed a single
           screen's height once you count a flowchart and two open overview sections — that's
           normal for a document this size (like a Word doc or PDF), not a bug. The fix here was
           removing the *unnecessary* height (wrong defaults, unaligned chips), not attempting to
           compress genuine content-driven height out of existence.

v1.11 — 2026-09 — Header byline removed + plain-English snapshot sentence
  Changed: Removed the "Built by Matt Powell · BOS2" byline from the guide header (Part 4.B) —
           it was reported as header clutter, and it's not lost information, since the footer's
           `.attrib` already says "Built by Matt Powell · BOS2 · Prepared [month year]" on every
           guide. Reverted `.hdr-datewrap` back to a plain `.hdr-dates` line for guides (the
           wrapper existed only to stack dates + byline, which no longer applies). Removed the now
           orphaned `.hdr-datewrap`/`.hdr-byline` rules from the guide's Part 2 style block. The
           binder header (Part 6) is untouched — its simple footer never restates the byline
           anywhere else, so removing it there would actually lose the attribution.
  Added: `.qr-snapshot` — a one-sentence, plain-English lead-in at the top of Quick Reference,
         before any fact-chips: what the document actually does, in one sentence a reader can
         understand with zero citations or trust jargon. Addresses "easier to understand at a
         glance" at its root — the guide previously jumped straight into fact fragments (grantor
         names, dates, a governing-law chip) without ever stating in one place what the trust
         actually accomplishes. Documented in Part 4.D as the single highest-leverage sentence in
         the guide; bold the 1–2 things a reader's eye should land on first.

v1.10 — 2026-09 — Quick Reference: chips sized to content, not stretched
  Fixed: v1.9's flexbox fix solved the dangling-empty-cell bug but overcorrected — `flex: 1 1
         230px` stretches every fact to fill its row, so a fact with one short line (e.g.
         "Massachusetts") became a huge mostly-empty box, and a lone leftover fact stretched
         across the *entire* row width alone. Same "wasted space" complaint, just moved inside
         the cell instead of between cells.
  Changed: `.qr-fact` is now `flex: 0 1 auto` with a `min-width: 190px` floor — each fact sizes to
           its own content and wraps naturally, like a row of chips, instead of being forced to
           fill available width. Facts also got individual borders/background (`var(--vellum)`
           chips on the white `.quick-ref` card) instead of the seamless-tile-with-1px-gap trick,
           since that trick is what made uneven fill read as "broken" in the first place — a
           bordered chip that doesn't reach the edge of the row looks intentional; an edge-to-edge
           tile that doesn't reach the edge looks like a bug.

v1.9 — 2026-09 — Fixed ragged Quick Reference grid
  Fixed: v1.8's `.quick-ref-grid` was one continuous CSS Grid spanning every fact across every
         group. Two compounding problems: (1) a short group sitting below a wider group inherited
         that wider group's column count, leaving dangling empty cells; (2) even split into
         separate per-group grids with `auto-fit`, a group whose fact count isn't a clean multiple
         of however many fit per row (e.g. 6 facts, 5 fit per row) still stranded the leftover
         item alone with empty cells beside it — `auto-fit` only collapses tracks that are empty
         *for the whole grid*, it doesn't fix an uneven trailing row. Both produced the same
         ragged, unfinished look reported as "not great."
  Changed: `.quick-ref-grid` is now `display: flex; flex-wrap: wrap` with `.qr-fact { flex: 1 1
           230px; }`, and each group of facts is still its own separate `.quick-ref-grid` (facts
           before the first group label get their own opening grid too). Flexbox's `flex-grow`
           operates per wrapped row, not per-container, so a lone leftover item on a trailing row
           grows to fill it completely — correct regardless of how many facts a group has or how
           unevenly they divide into rows.
  Changed: `.qr-group-label` no longer needs `grid-column: 1 / -1` — it's a plain sibling block
           between grids now, not a spanning item inside a shared one.

v1.8 — 2026-09 — Wider column + scannable Quick Reference
  Changed: `--maxw` widened from 1040px to 1240px — on a normal desktop window the guide was
           floating in a narrow column with large unused margins on both sides. Tables, the
           Quick Reference grid, and two-column comparisons now use the extra width; added a
           760px max-width to `.faq-a` specifically so long-form answer paragraphs don't stretch
           into unreadably long lines just because the container got wider.
  Changed: Quick Reference (§1) rewritten from a `<table>` of full-sentence rows into a
           `.quick-ref-grid` of short label/value fact-cards (`.qr-fact`, `.qr-label`, `.qr-value`),
           wrapping responsively across the wider column. A `.qr-group-label` spans the full grid
           width to introduce a group of facts. Reads as a glanceable dashboard instead of a form.
           Part 4.D now says to keep values a short phrase, not a sentence — anything that needs a
           full sentence to stay accurate belongs in a collapsible section instead.
  Fixed: The binder template (Part 6) referenced `var(--maxw)` twice but never defined `--maxw` in
         its own `:root` — an undefined custom property, so `max-width` silently fell back to
         `none` and the binder's header/main rendered uncapped-width. Added `--maxw: 1240px` to
         match the guide.

v1.7 — 2026-09 — Decluttered header + two-column toolbar
  Changed: The header's dates line and byline now stack together in one `.hdr-datewrap` on the
           right, so a standalone guide (the common case) renders as a single tight row instead of
           a mostly-empty second row that existed only to hold the byline. Applies to both the
           guide header (Part 4.B) and the binder header (Part 6), which never has a crumb and so
           always hit this — every binder index had the wasted row.
  Changed: A guide that IS part of a binder now adds `.hdr-bottom` back only for the crumb — the
           byline no longer needs to live there.
  Changed: Two-column guides (Part 4.J) split the toolbar into two intentional rows — `.toolbar-
           inner.toolbar-row` draws a thin rule between them — instead of cramming the View group
           and the Show/filter group into one row that wrapped unpredictably. View (the primary
           way to navigate a mirror-trust guide) + Print now share row 1; Show/filters +
           Expand/Collapse stay on row 2, matching single-column guides. Print now appears once,
           not duplicated between rows.

v1.6 — 2026-09 — Fixed silently-broken logo
  Fixed: The header logo was an `<img class="hdr-logo" src="data:image/png;base64,…">` — a raster
         PNG wrapped in a data: URI. These guides are hosted on a platform whose CSP has no
         img-src, so every data: URI image is blocked. It failed *silently* (no console error,
         just a blank header) rather than at generation time, so the shell had said "Cerity
         Partners theme" since v1.5 while actually shipping guides with no visible logo.
  Changed: references/cerity-logo.svg now holds a complete, self-contained inline
           <svg class="hdr-logo" fill="currentColor">…</svg> (the same official CP wordmark —
           verified by rendering the old PNG, which was correct artwork, just the wrong delivery
           mechanism). It inherits the header's white text color automatically.
  Changed: html-shell.md Part 4.B and Part 6 header markup, the Part 1 logo note, the two-column
           "Fonts + logo" note, and SKILL.md's reference-file description and branding checklist
           line all now say to paste the file's contents directly as the inline <svg> — never an
           <img> tag or a data: URI — and explain why.
  Removed: The `onerror` text-fallback span. It was a failure-recovery for a broken <img> src;
           inline SVG has no equivalent failure mode (it can't fail to "load" since it's not a
           resource reference), so the fallback no longer applies.
  Added: Quality Checklist line — grep the output for `<img` and `data:image` near the logo;
         both must return zero hits.

v1.5 — 2026-07 — Cerity Partners theme
  Added: Full Cerity brand theme in the locked shell — cobalt masthead with the Cerity logo,
         DM Sans + Cormorant fonts (Google Fonts link + system fallbacks), brand palette, and a
         "Built by Matt Powell · BOS2" byline + footer disclaimer. Matches the CP Portfolio Tool.
  Added: references/cerity-logo.svg (logo data URI, inserted into the header img — not retyped).
  Changed: Section-category colors to a colorblind-safe set (navy/teal/rust/brown/clay — differ in
           hue AND lightness, no red/green reliance) with a colored left bar + label per section.
  Changed: Banners now use distinct icon SHAPES (triangle/octagon/info-circle) so severity reads
           without color. Compacted the masthead (~120px) and moved the binder back-link top-left.

v1.4 — 2026-07 — Locked shell + personal documents + family binder
  Added: references/html-shell.md restored as the single source of truth (copied verbatim).
         Prior packages were missing html-shell.md and section-guide.md, so the shell was
         regenerated from memory each run and drifted (different CSS/JS per output).
  Fixed: SKILL.md shell documentation corrected to the real shell — filterSections/toggleSection/
         toggleQ/expandAll/collapseAll, inline onclick on <button> elements, setView for two-column.
         Removed the obsolete setView-only/addEventListener/"no onclick"/toggle-sections-IDs guidance.
  Changed: Emoji banned; replaced with SVG icons + CSS chevrons.
  Added: Personal document types (Durable POA, Health Care Proxy, HIPAA, Codicil) as first-class,
         a personal-documents-bundle intake option, and Step 4C Family Estate Plan Binder.
  Fixed: Two-column mirror-trust mode rebuilt and tested (setView g1/g2/both/same).
  Accessibility: toggles are keyboard-operable buttons with aria-expanded/aria-pressed.

v1.3 — 2025-05-21 — Added Client Meeting Summary (PPTX) mode + simplified-sections.md.
v1.2 — 2025-05-21 — Added Will support (standalone and combined Will + Trust).
v1.1 — 2025-05-19 — Independent trustee / self-dealing rule (per Alexander Gross, CP).
-->
