# assets/

- `guide-template.html` — the complete HTML shell for a guide, with `{{...}}` placeholders.
  Logo embedded inline. Read only by `build.py`, never by a model.
- `build.py` — renders guide content JSON into that template, validates, writes nothing on failure.
- `binder-template.html` — the shell for the Family Estate Plan Binder index (static, no script).
- `build_binder.py` — renders binder JSON. Reuses build.py's validators, so both outputs are
  held to one standard.
- `content-schema.md` — the guide content format. Read this before authoring guide content.
  The binder format is in `references/binder-guide.md`.

Do not hand-edit a template to change content — content comes from the JSON. To change a shell,
edit the template, then run both builders against test content to confirm they still validate.
