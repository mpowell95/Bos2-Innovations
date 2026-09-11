# Simplified Client Summary — Slide Content Requirements

Used when the user selects **Client Meeting Summary (PPTX)** at intake.

Output is a Cerity Partners-branded PowerPoint deck of approximately 8–12 slides, designed for client-facing review meetings. No §citations required. Plain language throughout. Short bullets (3–5 per slide). Include ⚠ callout bullets for important compliance or planning cautions.

Read the `cerity-partners-powerpoint-branding` skill before writing a single slide. All branding, color, font, and layout standards come from there.

---

## Slide 1 — Title Slide

- Trust name (full legal name)
- Client name(s)
- Month and Year of review (e.g., "April 2026")
- Tagline: *"Your wealth managed on your terms."*

Use the CP branded title slide layout.

---

## Slide 2 — Trust at a Glance

One-screen summary card. Two-column layout if the tool supports it; otherwise a clean labeled list.

| Field | Content |
|---|---|
| Trust Name | Full legal name |
| Type | e.g., Massachusetts Irrevocable Trust |
| Established | Execution date |
| Amended | Amendment date(s), if any |
| Donor / Grantor | Full name |
| Primary Beneficiary | Full name(s) |
| Governing Law | State |
| GST Status | Exempt / Non-Exempt / Bifurcated / Unknown — extract from document or flag if not stated |
| Spendthrift | Yes / No |
| Duration | e.g., Until trust termination event, 21-year rule, etc. |

If two mirror trusts: include one column per trust.

---

## Slide 3 — Parties & Trustee Structure

- Grantor / Donor (with deceased notation if applicable)
- Current Trustee(s): name, role (interested / disinterested), appointment date if stated
- Successor Trustee(s): list in succession order
- Note any co-trustee requirements (e.g., "disinterested trustee required for all distributions to [beneficiary]")
- ⚠ Flag if no successor is named or if succession chain is incomplete

**Interested vs. Disinterested note:** Include a plain-language one-liner if an interested trustee restriction exists (e.g., "Paul cannot direct distributions to himself — requires disinterested co-trustee").

---

## Slide 4 — Distributions During [Grantor's/Beneficiary's] Lifetime

- Who may receive distributions (beneficiary names)
- Distribution standard: Discretionary / HEMS / Other — in plain language
- Income vs. principal rules (briefly — one bullet each)
- Accumulation of undistributed income rule, if stated
- ⚠ Flag any self-dealing / interested trustee restriction that limits distribution authority

If multiple beneficiary classes: use a small two-column table (Beneficiary | Standard).

---

## Slide 5 — Distributions at Death / Trust Termination

Use a simple decision flowchart in text form (like Sam's decks), e.g.:

```
Is [Spouse] living and still married?
  YES → [describe what happens]
  NO  → [describe what happens]
```

Then list remainder beneficiary waterfall in numbered order:
1. [Primary remainder — describe]
2. [Contingent — describe]
3. [Final fallback — e.g., intestacy or named charity]

Include any testamentary power of appointment held by the primary beneficiary, if present.

---

## Slide 6 — Key Protections & Planning Features

Short bullets only. Include what applies; omit what doesn't.

- **Spendthrift:** [Brief description — creditor/alienation protection]
- **Marital/Separate Property:** [Whether trust assets are separate property]
- **Irrevocability:** [State that trust cannot be revoked; note any limited amendment power if present]
- **Trustee Liability:** [Standard of care stated in document, if any]
- **Independent Administration:** [If stated]
- Any other protective feature (e.g., no-contest, anti-lapse, etc.)

---

## Slide 7 — Special Provisions *(include only if present in document)*

Include this slide only if one or more of the following are present. Use one bullet per item; do not include a section if nothing applies.

- **GST Planning / Bifurcation:** Explain Exempt vs. Non-Exempt trust structure in 1–2 bullets
- **Crummey Rights:** Who holds them, window period, amount, Claire's / other beneficiary's rights
- **Life Insurance:** Whether trust owns policy, any trustee transition rules on policy ownership
- **Grantor Powers (Swap/Substitutor/Selector):** Brief plain-language description
- **Retirement / RMD Conduit:** Whether trust qualifies as conduit trust, RMD rules

---

## Slide 8 — [Beneficiary Name]'s Role as Trustee — Limitations *(include only if beneficiary serves as trustee)*

This slide is specific to situations where the primary beneficiary is also a co-trustee (e.g., a descendant's trust where the beneficiary is an interested trustee).

Use a two-column "CAN / CANNOT" format:

| ✅ [Name] CAN | ❌ [Name] CANNOT |
|---|---|
| [List permitted actions] | [List prohibited actions] |

Extract from trustee powers and distribution articles. Flag the most important restriction (usually: cannot self-direct distributions) as a ⚠ callout.

Only include this slide when this situation applies — omit entirely for trusts where the beneficiary does not serve as trustee.

---

## Slide 9 — Discussion Points & Action Items

This is a checklist of concrete, actionable items drawn from the document itself. Extract these from:
- Incomplete succession chains
- Unconfirmed elections (e.g., GST exempt election status)
- Annual administrative requirements (e.g., Crummey notices, trustee acceptances)
- Documents or records referenced but not confirmed (e.g., Crummey notice log, Schedule A)
- Any ⚠ flags raised earlier in the deck
- Coordination items (e.g., "Confirm this trust is named as beneficiary on retirement accounts")

Format as a numbered list. Keep to 6–10 items. Each item should be a short, actionable sentence.

Do NOT include generic items not supported by the document. Every action item must be traceable to something actually found (or notably absent) in the document.

---

## Slide 10 — Closing

Use the standard Cerity Partners closing slide per the branding skill.

- No additional text needed unless the user specifies otherwise.

---

## Two-Column Variant (Paired Mirror Trusts)

If the user selects two mirror/paired trusts and simplified mode:

- Slides 2–6: Use side-by-side columns (Trust 1 | Trust 2) where provisions differ. Mark identical provisions with a note or visual indicator.
- Slides 8–9: Combine into a single discussion agenda covering both trusts.
- Title slide: List both trust names and both grantor names.

---

## Output Rules

- Tone: Advisory, plain language, forward-looking. No §citations.
- Length per bullet: 1–2 lines max.
- Do not reproduce legal language verbatim — paraphrase in plain English.
- Include ⚠ warnings for: interested trustee restrictions, missing successors, unconfirmed elections, any provision that requires client action.
- File naming: `[ClientLastName]_Trust_Summary.pptx` (or as specified by user at intake).
- After saving, present the file and offer to upload to Box.
- Post-output notes block still required (same format as detailed mode).
