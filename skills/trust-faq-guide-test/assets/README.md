# assets/

Templates and builders. A model never reads a template — only its builder does.

- `guide-template.html` — complete HTML shell for a guide, `{{...}}` placeholders, logo inline.
- `build.py` — renders guide content JSON. Enforces shell fidelity, logo census, class coverage,
  open/closed defaults, CSP rules and citations. Writes nothing on failure.
- `verify.py` — the content pass. `extract` builds a worksheet of every decision-driving claim
  for checking against the document; `check` gates delivery until each is marked. Also runs the
  interested-trustee, missing-section and uncited-section cross-checks.
- `binder-template.html` / `build_binder.py` — the Family Estate Plan Binder index (static).
- `content-schema.md` — the guide content format. Binder format: `references/binder-guide.md`.

To change a shell: edit the template, then run both builders against test content to confirm
they still validate. Never hand-edit a template to change content.
