# Family Estate Plan Binder

Read this only when the user asked for a family binder.

## Building the index page

Produce each individual guide via Step 4 first, then the index page.

**The binder is not yet templated** (planned next). Until it is, build it from
`references/_html-shell-ARCHIVE.md` **Part 6** — and read that file in the explicit line range
`598-774`, never whole: a full read silently drops lines 137-638. Copy its `<style>` block and
snippets verbatim.

- Filename `[FamilyName]_Estate_Plan_Index.html`, saved beside the guides; relative links only.
- Header: family name, as-of date, and a context banner for family-wide status (e.g. a death).
- **Document inventory** — table of every document: owner, document, type, date, status (Active /
  Revocable / Now Irrevocable / Superseded), relative link to its guide.
- **Who's Who** — each person and their roles collated across every document.
- **How the Plan Works Together** — a timeline (both competent -> one incapacitated -> first
  death -> second death -> next generation) naming which document controls at each stage.
- **Action Items Across the Plan** — the warning/flag items from every individual guide, together.
- In each guide, set `binder` in its content.json so the back-to-index crumb is generated.

---
