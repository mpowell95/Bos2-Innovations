# assets/

Templates and the builders. A model never reads a template — only its builder does.

- `guide-template.html` — the complete HTML shell for a guide, `{{...}}` placeholders, logo inline.
- `build.py` — renders guide content JSON. Enforces shell fidelity, logo census, class coverage,
  open/closed defaults, CSP rules, citations, guide size, and confirms every quote word-for-word
  against the document text the model saved. Writes nothing on failure.
- `binder-template.html` / `build_binder.py` — the Family Estate Plan Binder index (static).
- `content-schema.md` — the guide content format. Binder format: `references/binder-guide.md`.

There is no separate verification pass. Verification is the quote check inside `build.py`: a
citation without the document's own words behind it does not build. A hand-marked worksheet was
tried and removed in v3.1 — see CHANGELOG.md.

To change a shell: edit the template, then run the builders against test content to confirm they
still validate. Never hand-edit a template to change content.
