# Section Guide — Content Requirements by Document Type

Read this in Step 3 once the document type is confirmed. It defines **which sections to include and what each must contain**. Build the sections using the component snippets and `data-cat` mapping in `html-shell.md`. All universal rules from SKILL.md Step 4A apply to every section: citations on every material fact, tables (never prose) for distributions/trustees/agents/charities/schedules, `[NOT FOUND]` for anything absent, no fabrication, no emoji, and the independent-trustee/self-dealing rule.

Quick Reference is always §1 (a non-collapsible `.quick-ref`); collapsible sections start at §2. Omit any section that does not apply — don't leave numbering gaps.

---

## A. Section orders

### Trust-only guide (single or two-column)
1. Quick Reference — At a Glance
2. Key Differences *(two-column only; include only if material differences exist)*
3. Trust Structure Overview — Flowchart
4. Family Information *(revocable trusts)*
5. Basic Trust Information
6. Trustee Succession
7. Trust Protector *(if present)*
8. Incapacity Provisions *(revocable trusts)*
9. Administration Upon Death / Trust Termination
10. Marital Trust & Family Trust *(if applicable)*
11. Specific Distributions
12. Charitable Distributions *(if applicable)*
13. Tangible Personal Property *(if applicable)*
14. Underage / Incapacitated Beneficiary Distributions *(if applicable)*
15. Retirement Plans & Life Insurance *(if applicable)*
16. Administrative Provisions
17. Protective Provisions
18. Trust Duration & Remote Contingent Distribution
19. Key Definitions

### Will-only guide
1. Quick Reference — At a Glance
2. Will Overview
3. Executor / Personal Representative Succession
4. Guardian Nominations *(if minor children named)*
5. Specific Bequests
6. Tangible Personal Property
7. Residuary Estate
8. Administrative Provisions
9. Key Definitions

### Combined Will + Trust guide
Follow the trust section order for all trust sections, then append: Will Overview; Executor/PR Succession; Guardian Nominations *(if minor children)*; Specific Bequests *(Will-only gifts — exclude anything the trust already covers)*; Residuary Estate / Pour-Over Clause; Will Administrative Provisions *(only if materially different from the trust's)*. Where a pour-over clause exists, add a cross-reference note in the trust's "Administration Upon Death" section pointing to the Will's Residuary Estate section.

### Personal-documents bundle (Will + codicil + POA + HCP + HIPAA)
1. Quick Reference — All Documents at a Glance *(group rows by document with `qr-group` subheaders)*
2. Will Overview *(note the codicil; flag if pour-over)*
3. Tangible Personal Property
4. Residuary Estate (Pour-Over to Trust)
5. Personal Representative Succession
6. Payment of Taxes & Expenses
7. Guardian for Children *(if minor children)*
8. Durable Power of Attorney
9. Health Care Proxy
10. HIPAA Authorization
11. How These Documents Work Together *(scenario table)*

---

## B. `data-cat` by section

| Section | data-cat |
|---|---|
| Trust Structure / Flowchart, Family Information, Basic Info, Will Overview, Guardian Nominations, Quick-Ref context | `overview` |
| Trustee Succession, Trust Protector, Executor/PR Succession, Durable POA | `trustee` |
| Incapacity, Administration Upon Death / Termination, Marital Trust, Health Care Proxy | `lifecycle` |
| All distribution sections, Specific Bequests, Residuary/Pour-Over, Tangible Personal Property, Taxes & Expenses | `distribution` |
| Administrative, Protective, Trust Duration, Key Definitions, HIPAA, "How These Documents Work Together" | `legal` |

---

## C. Trust-type-specific requirements

### Revocable Living Trust (RLT)
Include Family Information, Incapacity, and (if present) Marital/Family Trust sections.
- **Basic Trust Information:** revocability and how it ends; income/principal management during the grantor's life; grantor-trust income-tax status; GST division provisions if present.
- **Trustee Succession:** current and successor trustees in a table; bond waiver; whether a beneficiary/trustee can distribute to themselves (independent-trustee rule); appointment/removal mechanics.
- **Incapacity:** who determines incapacity and by what standard; successor trustee's distribution powers; cross-reference any separate POA/HCP.
- **Administration Upon Death:** what happens at death (becomes irrevocable, splits); estate-tax/debt apportionment; pour-over receipt from the Will.
- **Marital & Family Trust:** funding formula (e.g., marital deduction amount), income/principal standards, powers of appointment, remainder to the Family Trust; if a spouse has predeceased, mark the Marital Trust `na`/`active-now` accordingly.
- **Specific/Children's Distributions:** the distribution schedule as a table (age triggers, fractions); powers of appointment; per stirpes gifts to issue.

### SLAT
Gift-tax structure at creation; the beneficiary spouse's access standard; divorce/incapacity risk (`flag-banner`); reciprocal trust doctrine warning; remainder beneficiaries; independent-trustee distribution requirement.

### ILIT
Policies held and premium funding; **Crummey withdrawal rights** (who holds them, window period, amount) — historical vs. currently active; trustee ownership of policy and any transition rules; distribution at the insured's death; independent-trustee coverage check (`flag-banner` if a beneficiary serves as trustee); insurance provisions section.

### GRAT
Annuity payment amount/rate and the term; hurdle (§7520) rate; remainder beneficiaries; mortality risk if the grantor dies during the term (`flag-banner`).

### CRT / CRUT / CRAT
Payout type and rate; income beneficiaries and term; charitable remainder beneficiary; tax treatment; ordering rules.

### SNT
Beneficiary and disability; government-benefit-preservation language; permissible (supplemental, not supplanting) distributions; trustee discretion standard; Medicaid payback provision (first-party) if present.

### Generic irrevocable
Universal sections only — omit Family Information, Incapacity, and Marital/Family Trust unless the document actually contains them.

---

## D. Will sections — content requirements

### Will Overview *(overview)*
Testator full name; execution date and governing state law; family recitals (spouse, children with ages if stated); whether it is a pour-over Will (flag prominently); prior-Will revocation clause; any codicil and exactly what it changes.

### Executor / Personal Representative Succession *(trustee)*
Table: `Priority | Name | Relationship | Notes`. Primary, successors, any corporate/institutional fallback; bond waiver; incapacity-of-PR standard. If a codicil replaced the succession, show the current chain and note the superseded original (`warning-banner`).

### Guardian Nominations *(overview)*
Named guardian(s) for minor children with succession order; whether guardian of the person and of the property are the same or split; conservator/UTMA custodian authorizations. If no guardian is named and minor children are beneficiaries, flag `[NOT FOUND]`.

### Specific Bequests *(distribution)*
Table: `Beneficiary | Asset / Amount | Condition | §Ref`. All pre-residuary gifts; lapse provisions (what happens if a beneficiary predeceases; mark with `amt-lapse`/`na` where applicable).

### Tangible Personal Property *(distribution)*
Distribution method (written memorandum, executor discretion, equal division); whether a separate memorandum is incorporated by reference; the fallback order; what is excluded (cash/securities pass under the residue).

### Residuary Estate / Pour-Over Clause *(distribution)*
Who receives the residue, or — if pour-over — the receiving trust's name, trustee, and governing article; per stirpes vs. per capita; contingent residuary beneficiaries. If pour-over, add an `info-banner`: "Residuary estate flows into the [Trust Name] — see [Trust guide/section]."

### Payment of Taxes & Expenses *(distribution)*
Source of payment (usually residue, without apportionment); exceptions (marital/charitable-deductible property; GST borne by recipients); any §2207A recovery direction.

### Will Administrative Provisions *(legal)*
Only if the Will contains executor powers, no-contest clauses, or other provisions not duplicated in the trust.

---

## E. Personal directive sections — content requirements

### Durable Power of Attorney *(trustee)*
- Type and activation: **immediate vs. springing**; the incapacity standard (who determines it and how).
- Agents: table of `Role | Name | Acceptance | Contact` (attorney-in-fact + alternates; include acceptance dates/method and contact info when present).
- Scope of powers (banking, real estate, investments, tax, retirement, business, litigation, digital assets, etc.) as a bulleted list with article citations.
- **Gifting authority and limits** (annual-exclusion cap, unlimited tuition/medical, charitable gifts).
- Revocation mechanics and third-party reliance.
- Guardian/conservator nomination if present.
- Flag (`flag-banner`) any agent who is deceased or whose appointment is otherwise void.

### Health Care Proxy *(lifecycle)*
- Agent and alternate (table with status and contact); flag a deceased/void primary agent and note who effectively steps up.
- Activation standard (incapacity determined by the treating physician; special rule for mental illness/developmental disability).
- End-of-life directives verbatim in plain terms (pain management, persistent vegetative state / no-recovery instructions, any explicit exceptions such as a COVID-19 clause).
- Scope of the agent's authority; revocation mechanics; guardian-of-the-person nomination.

### HIPAA Authorization *(legal)*
- Authorized recipients and the purpose for each (agents, successor trustees, estate-planning attorney); table format.
- Duration/expiration (often continues after death until revoked); re-disclosure caveat.
- Note it revokes prior HIPAA authorizations if stated.

### Codicil (when part of a Will/bundle)
Do not give the codicil its own section — fold it into the sections it changes (usually PR succession and/or guardian). In each affected section, state the current controlling provision and note the superseded original with a `warning-banner`.

### How These Documents Work Together *(legal)*
A scenario table mapping life events to the governing document and who acts:

| Scenario | Governing Document | Who Acts |
|---|---|---|
| Principal alive and competent | — | The principal directly |
| Alive but incapacitated (financial) | Durable POA | [primary → alternate] |
| Alive but incapacitated (medical) | Health Care Proxy | [effective agent] |
| Medical records / capacity determination | HIPAA Authorization | [agents / successor trustee / attorney] |
| Death (probate assets) | Will + Codicil | [PR chain] |
| Death (trust assets) | Trust + Will (pour-over) | [trustee chain] |

Close with a short "Action items to consider" `warning-banner` drawn only from what the documents actually show (e.g., a deceased agent to replace, an age to confirm, a stale certificate to update). No generic items.
