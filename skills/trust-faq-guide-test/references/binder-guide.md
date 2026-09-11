# Family Estate Plan Binder

Read this only when the user asked for a family binder. Build every individual guide first
(Step 4), then the index page.

You do not write any HTML. The binder shell lives in `assets/binder-template.html` and is
rendered by `assets/build_binder.py`. You write a JSON file of facts collated across the
family's documents.

```
BUILD=$(find /mnt/skills -path '*trust-faq-guide*/assets/build_binder.py' | head -1)
python3 "$BUILD" binder.json /mnt/user-data/outputs/[FamilyName]_Estate_Plan_Index.html
```

Save the index in the **same folder** as the guides — every cross-link is a relative filename
so the folder stays portable and can be uploaded to Box together. The build refuses any link
that isn't a bare relative `.html` filename, and refuses a link that doesn't match a document
listed in the inventory.

Set `binder` in each individual guide's content.json so its back-to-index crumb is generated:
`"binder": {"family": "Krasker", "href": "Krasker_Estate_Plan_Index.html"}`

## binder.json

| Key | Required | Notes |
|---|---|---|
| `family` | yes | Family surname. Used in the title, header and footer. |
| `preparer` | yes | The running user's name. The CP address is added for you. |
| `prepared` | yes | e.g. `"September 2026"` |
| `inventory` | yes | Every document in the plan. |
| `whos_who` | yes | Each person and their roles collated across all documents. |
| `timeline` | yes | Which document controls at each life stage. |
| `subtitle` | no | Header right-hand line, e.g. `"Massachusetts · Prepared September 2026"`. Defaults to "Prepared [prepared]". |
| `context` | no | A family-wide status banner at the top, e.g. a spouse's death. |
| `actions` | no | Aggregated warning/flag items from the individual guides. Include it whenever any guide raised a flag. |

### `inventory`
```json
{"owner": "Steven Krasker", "document": "Revocable Living Trust", "type": "RLT",
 "dated": "Restated Apr 2019", "status": ["irrevocable"],
 "guide": "Krasker_Steven_Rev_Trust_FAQ_Guide.html"}
```
`status` is one or more of `active` · `revocable` · `irrevocable` (renders "Now Irrevocable") ·
`super` (renders "Superseded"). Omit `guide` for a document with no guide of its own.

### `whos_who`
```json
{"name": "Julie Krasker", "relation": "Spouse",
 "roles": ["Grantor and trustee — her own trust", "Successor trustee — Steven's trust"]}
```
Add `"deceased": true` to mark someone who has died. Collate every role a person holds across
every document — that is the whole point of the panel. Roles accept a `section-ref` citation.

### `timeline`
```json
{"when": "First death (Mar 2026)", "done": true,
 "what": "Steven's trust became irrevocable. Julie continues as sole trustee.",
 "documents": "Steven's trust"}
```
Cover the full progression: both competent -> one incapacitated -> first death -> second death
-> next generation. `"done": true` marks a stage that has already happened and adds the check
icon. Name which document controls at each stage in `documents`.

### `actions`
```json
{"variant": "warning", "label": "Funding gap.",
 "detail": "The Sample Family LLC interest is not on either Schedule A.",
 "source": "Julie guide §2.1"}
```
`variant` is `flag` (superseded, conflict, critical) · `warning` (action needed) · `info`
(clarifying note). Cite which guide raised it in `source`. Aggregate every flag from every
individual guide — this panel is the reason an advisor opens the binder.

If no guide raised a flag, say so in an `info` item rather than omitting the panel.

## Permitted inline markup

Same as the guides, but the binder has its own smaller stylesheet: `section-ref`, `doc`,
`person`, `role-list`, `pill`. Guide-only classes such as `amt` and `na` are **not** defined
here and will fail the build. When in doubt, write plain text.

## If the build fails

It prints the problem and writes nothing. Fix the JSON and run again. Never write the HTML by
hand instead.
