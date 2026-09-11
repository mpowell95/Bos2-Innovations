# Changelog — trust-faq-guide

Moved out of SKILL.md in v2.0. SKILL.md is loaded on every run, so keeping ~200
lines of history in it cost context on every invocation — and pushed the file past
the ~16,000-character read limit, meaning SKILL.md itself truncated when viewed.

**Read this file in line ranges, not whole.** It is long by design.

---

## v2.9 — 2026-09 — Production

Promoted after a complete, clean real run on the hardest case: the Krasker mirror pair, two
47-page trusts pulled from Box, built and verified across two turns.

The guide: `<style>`, `<script>` and logo byte-identical to the template; 15 sections, all with
correct open/closed defaults; 46 questions with zero aria/.open mismatches and exactly one open
answer; no undefined classes; 94 citations covering all 28 articles; correct two-column layout
labelled with the grantors' names.

The verification pass did its job rather than rubber-stamping it. Of 72 claims, 69 confirmed and
**three marked `[?]`** with substantive reasons: neither trust names any child (both dispose to
"my descendants" generically), neither cross-references a POA or health care proxy, and Article IV
implies a companion pour-over Will that was never provided. Those are precisely the honest
"cannot confirm from this document" answers the worksheet exists to capture, and no automated check
could have produced them.

It also answered the interested-trustee cross-check with real analysis of the fact pattern:
Steven's trust requires a Disinterested Co-Trustee at all times, so an interested Julie never
decides distributions to herself alone; Julie's trust requires one only for the Descendants'
Separate Trusts, so Steven could decide principal distributions to himself — but under the
ascertainable HEMS standard that applies whenever no Disinterested Trustee serves, not "for any
purpose." That is the v1.1 self-dealing rule, prose-only for eight versions, applied correctly to
a live document.

And the coverage report earned its place: Articles IX, XVI, XX and XXVII were uncited in the first
build. The run went back and worked them in. All 28 are now cited.

Renamed from trust-faq-guide-test: frontmatter `name:` and the folder. Nothing else — the builders
resolve their own paths, verified under the production name.

### What this version does not do

It does not verify that a fact is correct, only that the guide was checked against the document
and that every citation exists in it. A `[x]` is a person or a model saying they looked; nothing
can force an honest look. The advisor reads the guide against the executed document before it
reaches a client, and Step 8 requires saying so on delivery.

PPTX mode is unchanged from v1.18 — the `pptx` skill owns file generation there, so there is no
shell to drift. The family binder is templated and tested, but has not yet run on real documents.

---

## v2.8 — 2026-09 — Multi-turn work, planned for rather than discovered

A real mirror-pair run (Krasker, two 47-page trusts from Box) did the right thing and still could
not finish: it read both documents, diffed them for genuine differences rather than name swaps,
wrote content.json, built a clean 78KB guide with a 71-claim worksheet, then ran out of tool calls
and reported "built but not yet verified — I'd rather flag this now than hand you an unverified
guide labeled as done." That is exactly the intended behaviour at a turn boundary. The gap was
that nothing in the skill planned for it.

**`verify.py mark <worksheet> <marks.txt>`** applies a batch of marks and reports how many claims
remain, exiting 0. Previously the only way to apply marks was `check`, which gates — so a partial
pass ended in a failure message, which reads like something went wrong when the work is simply
unfinished. Verifying 71 claims against two long documents does not fit in one turn; now it can be
done in passes, with `check` run once at the end.

**`references/large-guides.md` now opens with staging guidance**: the four stages (read and write
content, build, verify, deliver), the fact that everything persists on disk between turns so a
follow-up resumes from the content files rather than re-reading the documents, and the instruction
to stop at a stage boundary with a one-line status when a turn is running out. Explicitly: do not
compress verification to fit a turn, and never present an unverified guide as finished. SKILL.md
now points there before Step 4 rather than only when the content file looks large.

Also fixed: two edits in v2.6 silently did nothing, because the text they targeted had moved from
SKILL.md into large-guides.md in that same version. Step 5 now really does describe batch marking.

Verified from the shipped package: split build, batch mark then check, five build modes, binder,
14 build negatives, 6 gate behaviours, and a malformed marks file still refusing under `mark`.

---

## v2.7 — 2026-09 — Two worksheet bugs, one of them reported by the skill itself

From the first real two-column run (Krasker, 15 sections, 39 questions, 74 claims). The shipped
guide was clean — `<style>`, `<script>` and logo byte-identical to the template, 0 aria/.open
mismatches, no undefined classes, 79 citations, correct two-column layout.

**Coverage was computed from claim lines only.** An answer that is not a decision-driving claim
gets no worksheet line, but can still carry a citation — so its section was reported as "never
cited". The run caught this itself: Article XXIV appeared on the never-cited list while the
S-corporation answer cited it in the shipped HTML, and the worksheet was annotated saying so and
flagging it for the maintainer. Confirmed by grep. Coverage now walks the whole content structure
and counts every citation. (The first fix attempt pattern-matched serialised JSON and silently
matched nothing, because `json.dumps` escapes the quotes in the embedded HTML; it walks the
structure now.)

**Citations were shown doubled** on rows whose own `cite` also appeared inside their body —
"Article XXI Article XXI". Deduped, order preserved.

**"Check these first" now always appears**, even with nothing to report, saying explicitly that
silence is not a clearance: the interested-trustee check compares names in Quick Reference rows,
so a document naming no beneficiaries there — one disposing to "my descendants" generally, as
this one does — gives it nothing to compare. Previously the section was simply absent, which
reads like a pass.

On whether the run rubber-stamped: all 74 claims came back `[x]` with no `[!]` or `[?]`, which is
the pattern to be suspicious of. Three things argue against it here — it added a substantive
cross-reference note on one claim, it annotated the never-cited list as "confirmed by direct read
to be pure boilerplate", and it caught a bug in the worksheet generator by grepping the output.
None of that is what a rubber stamp does. It cannot be proven from the file, and that limit stands.

---

## v2.6 — 2026-09 — Fit the work inside one turn

Reported from real use: running the skill exhausts the turn and needs a Continue click. The cause
is output volume, not reading volume — a 15-section trust's `content.json` is 30KB+ that the model
must emit in one go, and then marking a 40-line worksheet means re-emitting the whole file.

**`build.py` and `verify.py extract` now accept the content split across several files.** The
output is the last argument; any number of content files precede it. List keys (`sections`,
`quick_ref`, `banners`, `document_sections`) concatenate in order, so the result is byte-identical
to one combined file — verified. A long guide can now be written a few sections per file, across
turns, instead of racing to finish one enormous write that may truncate.

**`verify.py check` accepts a compact marks file.** `001 x` / `020 ? -- reason` / `signoff x`, one
line per claim, applied into the worksheet before gating so the worksheet stays the delivered
record. In testing, 217 bytes of marks replaced re-emitting a 3,533-byte worksheet. A marks file
with any unparseable line applies nothing and says which line, so it can never half-mark.

Both are documented in `references/large-guides.md`, pointed to from Step 4 — which also brought
SKILL.md down to 13,762 characters, its most headroom yet (~2,300).

Caught while building this: `verify.py` used `G.load_content` without importing `build`. The
`import build as G` line existed in `build_binder.py`, not `verify.py`. It surfaced as build.py
reporting "could not write the verification worksheet: name 'G' is not defined" and falling back
to telling the model to extract manually — the guide was never at risk, which is what that
try/except is for.

Verified from the shipped package: split content, auto-written worksheet, marks file apply and
gate, plus the full regression — five build modes, binder, 14 build negatives, 6 gate behaviours,
3 marks-file negatives.

---

## v2.5 — 2026-09 — Step 5 can no longer be skipped by forgetting

Two fixes aimed at the one thing still untested: whether a model actually follows the new
instructions.

**The worksheet is now written by `build.py` itself**, next to the guide as
`[GuideName]_verification.md`. Verification was a separate command to remember, and a required
step a model can forget is a step that will sometimes not happen. Now it always exists, and the
build ends with:

```
NOT DELIVERABLE YET - the content is unverified.
Wrote Krasker_Rev_Trust_FAQ_Guide_verification.md: 22 claims to check against the document.
  ! INTERESTED TRUSTEE - see the top of the worksheet
Mark every line, then run:
  verify.py check .../Krasker_Rev_Trust_FAQ_Guide_verification.md
```

Skipping Step 5 now takes a deliberate decision to ignore that, rather than simply not thinking
of it. A rebuild rewrites the worksheet, so marks always correspond to the guide as it stands.

**An instruction walkthrough** — reading SKILL.md as a model would and following it literally —
caught a contradiction introduced by that very change: Step 5 still said to run
`verify.py extract content.json verification.md`, which would have produced a second worksheet
under a different name while the real one sat beside the guide. Step 5 now says the worksheet
already exists and only needs marking and gating, with manual re-extraction noted as the
exception. Step 4 also now names `document_sections` in its own text rather than only in
content-schema.md, since it is the newest required key.

Verified end to end as the instructions read: build writes the guide and the worksheet; the gate
blocks it unmarked; marking it passes; a rebuild resets it to unmarked. Plus the full regression —
five build modes, 14 build negatives, 6 gate behaviours — from the shipped package.

---

## v2.4 — 2026-09 — Package hygiene audit before replacing the live skill

A consistency audit of the whole package before promotion, which found one live trap and two
files that had no business being in an installed skill.

- **`section-guide.md` still told the model to build sections from "the component snippets and
  `data-cat` mapping in `html-shell.md`", and cited "SKILL.md Step 4A".** A stale pointer, from
  v1.x, aimed straight back at the 50KB file whose truncation caused every drift bug — and at a
  step that no longer exists. Rewritten to point at `content-schema.md` and Step 4. This is the
  clearest illustration of why the audit was worth doing: the disease was cured everywhere except
  in a sentence telling the model where to go.
- **`_html-shell-ARCHIVE.md` (52KB) removed from the shipped package.** Nothing reads it once the
  pointer above is fixed. It stays in the source repo for historical reference. Leaving a 52KB
  truncating markdown file inside an installed skill is an invitation, however many warnings its
  header carries.
- **`CHANGELOG.md` stays in the shipped package.** It was briefly removed on the same reasoning
  and that was wrong: size was never the hazard. `html-shell.md` was dangerous because it held
  copyable CSS and instructions *and* something pointed at it. A changelog is history — nothing
  points to it, nothing in it can be copied into an output, and an unread file costs no context.
  It also has real value in the package, since anyone installing the skill does not have this
  repo. SKILL.md says not to read it at run time and leaves it at that.

Result: every file a model can read in the installed skill is under the ~16,000-character read
limit — the largest is SKILL.md at 14,758. The five files above the limit are templates and
scripts that only Python opens.

Verified from the shipped package after removal: all five build modes, verify extract and check,
build.py 14/14 negative tests, build_binder.py 8/8, verify.py 6/6 gate behaviours.

---

## v2.3 — 2026-09 — Verification pass: the content gets checked, not just the formatting

Everything before this made the guide reliably well-formed. None of it touched the risk that
actually matters: a guide can be 100% valid and 100% wrong, because no script can tell whether
"ages 25 / 30 / 35" is what the trust says.

`assets/verify.py` does two things about that.

**`extract`** pulls every decision-driving claim out of the content file into a worksheet —
Quick Reference rows, table rows, flowchart stages, two-column blocks, banners, NOT FOUND flags,
and any answer containing a number, date, age, role or discretion term. Generic explanation is
skipped; this is about claims that drive decisions. Each line carries its citation.

**`check`** refuses to pass until every line is marked: `[x]` confirmed against the document,
`[!]` wrong (fix content.json, rebuild, re-extract), `[?]` not verifiable (reported to the
advisor, never silently dropped). It also blocks an invalid mark, a `[!]` still present, and an
incomplete sign-off. The worksheet is delivered with the guide as the record that it was checked.

It cannot force an honest read — marking everything `[x]` without looking would pass. SKILL.md
says so bluntly: a claim you did not look up is not `[x]`, and a false worksheet is worse than
none because the advisor will trust it. That is a limit of the approach, not an oversight.

**Cross-checks needing no document**, printed at the top of the worksheet:

- **Interested trustee** — if a person appears as both trustee and beneficiary and the guide says
  "full/sole/absolute discretion" anywhere, the worksheet demands it be resolved. This is the
  skill's highest-liability rule (added v1.1 from counsel feedback) and had been prose-only for
  every version since.
- **Missing sections** — sections a document type normally carries that the guide omits. A
  warning, not a failure: a real document can lack any of them, but the omission is now visible.
- **Uncited sections** — headings in `document_sections` the guide never cites.

SKILL.md restructured to fit under the read limit with real headroom (14,426 chars, ~1,600 spare):
the PowerPoint step moved to `references/pptx-guide.md`, the per-type reading order to
`references/reading-guide.md`, the document-type signal table to `section-guide.md`, and the
delivery checklist cut to only what the builders cannot enforce.

Verified: 6 gate behaviours; extract works across all five content shapes; the interested-trustee
check fires correctly; build.py's 14 negative tests and build_binder.py's 8 all still refuse.

---

## v2.2 — 2026-09 — Citations enforced, not just requested

"Every material fact carries a citation" had been written in SKILL.md since v1.x and was never
checked. Demonstrated by replacing every answer in a test file with "The trust says whatever I
feel like. No citation at all" and stripping every Quick Reference citation: the build printed
OK and wrote the file. The rule had exactly the status "copy the style block verbatim" had for
eight versions — true, important, in two places, and silently violable.

Three checks added:

- **Presence.** An answer with no `section-ref` and no `not-found` flag fails the build, named
  by section and question. An answer that is a general explanation rather than a provision sets
  `"cite": false`, making the exception deliberate and visible. Quick Reference is a proportion
  check (most substantive rows must cite) since some rows characterise rather than quote.
- **Shape.** A citation must look like a reference — `§4.2`, `§4.2(a)(iii)`, `Art. Three`,
  `Article IV`, `Part 6`, `POA Art. One`, `Schedule A`. Prose like "somewhere in the trust"
  fails.
- **Existence.** New required key `document_sections`: the flat list of every section/article
  heading found in the document, which Step 2 already required capturing. Every citation
  anywhere in the guide — answers, Quick Reference, table cells, flowchart stages — must match
  an entry. A `§9.4` in a trust with eight articles cannot ship.

The build also now reports coverage — how many of the document's sections the guide cites, and
names the ones it never cites — which is a completeness signal the skill never had.

**Stated limit.** None of this checks whether a citation is *correct*. `§4.2` can exist and
still be the wrong reference for the sentence it sits on; only reading the document establishes
that. The build says so on every run, and Step 7 now requires telling the advisor the guide is
unverified until they have read it against the document. Padding `document_sections` to make a
citation pass defeats the only mechanical check on citations there is, and SKILL.md says so.

Also moved: the document-type signal table from SKILL.md into section-guide.md, which Step 3
reads at the same moment, keeping SKILL.md under the read limit with real headroom.

Verified: 14 negative tests each refuse; full regression across all five modes.

---

## v2.1 — 2026-09 — Binder templated; nothing reads the archive at run time

The Family Estate Plan Binder was the last path where a model still copied a shell — Step 6
told it to read `_html-shell-ARCHIVE.md` Part 6 in an explicit line range, which worked but
left the original failure mode one mistake away.

- `assets/binder-template.html` — the binder shell as a real file, logo inline, `{{...}}`
  placeholders. Part 6's stylesheet extracted verbatim, not retyped.
- `assets/build_binder.py` — renders binder JSON. Imports build.py's validators, so the guide
  and the binder are held to one standard rather than two drifting ones.
- `references/binder-guide.md` rewritten: a JSON schema, no HTML.
- **No file in this skill is read at run time above the ~16,000-character view limit.**

Binder-specific validation: status pills restricted to the four defined classes; every guide
link must be a bare relative `.html` filename; and **every cross-link must match a document
listed in the inventory** — a link to a guide that was never delivered fails the build, which
is the binder's own characteristic failure (broken relative links in a folder uploaded to Box).

Caught while building it: `build_binder.py` initially used `<span class="na">` for a document
with no guide. `.na` is defined in the guide stylesheet but not the binder's smaller one, so
the class-coverage check refused the build. Exactly the bug class that shipped unnoticed four
times in v1.x, caught here before a single file was written.

Verified: the binder builds; its `<style>` and logo are byte-identical to the template; no
`<script>`; all four panels, all four pill types, done-stage check icons and the deceased
marker render; eight negative tests each refuse. Full regression across all five modes —
guide single, guide two-column, guide with a flowchart-only overview section, guide with a
binder crumb, and the binder index.

### Real-document verification of v2.0

Two live runs before this entry, both with the shell byte-identical to the template:
a single-column revocable trust (11 sections, 31 questions, 41 citations) and a mirror/paired
two-column pair (15 sections, 37 questions, 65 citations, 4 two-col and 6 identical-row blocks).
Zero drift, zero aria/.open mismatches, zero undefined classes in either.

One bug surfaced by the first run and fixed: the first-question-open default was implemented
literally as "section 2, item 0", but section 2 is normally the flowchart-only Trust Structure
Overview, so no question opened anywhere. Now opens the first question of the earliest open
section that has questions. Worth noting the v1.18 output got this right from prose — rigid
generation removes drift but can encode a rule more narrowly than it was meant.

---

## v2.0 — 2026-09 — Template + builder; the model no longer writes the shell

### Root cause found for the entire v1.4–v1.18 drift history

`references/html-shell.md` is 50,866 bytes / 774 lines. The environment's file-view
tool truncates at roughly 16,000 characters. Reading html-shell.md without an explicit
line range returns lines 1–136 and 639–774 and **silently drops lines 137–638** — which
contains the last 60% of the `<style>` block, the ENTIRE `<script>` block, all of Part 4
(every component snippet), all of Part 5 (assembly rules, data-cat mapping, open/closed
defaults), and the entire Part 6 binder stylesheet.

So the instruction "read html-shell.md and copy its `<style>` and `<script>` blocks
verbatim" was, for any normal read, **impossible to comply with** — the blocks were not
in what came back. Whatever got written came from the visible fragment plus recall. That
is the mechanism behind every "the changelog said it was fixed but the shell never
changed" entry below. It was never carelessness; it was an unreadable source of truth.

Verified empirically in the live environment: `cerity-logo.svg` (8,949 bytes) reads
whole; `html-shell.md` (50,866 bytes) reports `< truncated lines 137-638 >`.

### What changed

- `assets/guide-template.html` — the complete shell as a real HTML file with `{{...}}`
  placeholders. Logo embedded inline. Assembled by extracting the verbatim `<style>`,
  `<script>` and logo bytes from the v1.18 sources, not retyped.
- `assets/build.py` — reads the template with `open().read()` (Python is not subject to
  the view-tool truncation, verified), renders content into it, validates, and writes
  nothing on any failure.
- The model now authors `content.json` — extracted facts only. It never writes the
  `<head>`, CSS, JS, logo, header, toolbar, footer, disclaimer, or any generated
  structure (section wrappers, data-cat, chevrons, aria-expanded/.open pairing,
  open/closed defaults, the Quick Reference table, the flowchart, two-column mode).
- `references/html-shell.md` → `references/_html-shell-ARCHIVE.md`. No longer read at
  run time. Maintainer reference only.
- SKILL.md cut from 53,117 to under 16,000 characters so it can never be partially read.

### Bugs found and fixed while building this

- **`.flow-stage.family-trust` and `.flow-stage.children`** — used by the Part 4.G
  flowchart snippets since v1.4, with no CSS rule ever written. Marital/family/children
  branches rendered identically to a plain stage. Real rules added.
- **`.view-btn`** — used by the Part 4.J two-column toolbar, no CSS rule anywhere. It is
  genuinely a JS selector hook, so it is now declared as one (`JS_HOOK_CLASSES` in
  build.py) rather than given invented styling.
- **Step 1 intake numbering** — the block started at "2." because v1.15 removed questions
  1 and 3, and two lines still referenced the removed numbers ("If the user answered
  Question 3", "answer to Question 2"). Renumbered.
- **Footer attribution split** — the visible footer credited the tool's author on a
  client-facing estate document regardless of who actually prepared it. The preparer line
  now takes the running user's name; tool authorship moved to the `<head>` comment and
  `<meta author>`. The `.attrib` line reads "Generated with the CP Trust & Estate Guide".

### Validation the build now enforces (writes nothing on failure)

Logo census (16 `<path>`, 1 `<use>`, head and tail sentinels — the tail sentinel exists
only at the end of the asset, so a truncated or reconstructed logo cannot satisfy it);
every class used in markup has a rule in the template's own stylesheet; all six JS
functions present; no `<img>`, `data:`, `url(data:)`, `mask:`, external font link, or
emoji; no unfilled placeholders; aria-expanded matches `.open` everywhere; unknown JSON
keys rejected; flowchart stage titles must name an event, not "Stage 1"; at most 3
Quick Reference highlights.

### Verified before release

Single-column and two-column both build. Nine negative tests each correctly refuse.
The original v1.6–v1.14 logo bug was reproduced byte-for-byte inside the template
(1 real path plus the fabricated `matrix(387.499,...)` `<use>`) and the build refused,
writing nothing.

---

## Prior history (v1.1 – v1.18)

Kept verbatim. Note the recurring pattern documented from v1.15 onward — a changelog
entry describing a shell fix that never reached the shell. The root cause is now known
and is recorded at the top of this file.

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
