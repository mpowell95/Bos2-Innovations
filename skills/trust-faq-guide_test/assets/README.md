# assets/

- `guide-template.html` — the complete HTML shell with `{{...}}` placeholders. The logo is
  embedded inline. Read only by `build.py`, never by a model.
- `build.py` — renders content JSON into the template, validates, writes nothing on failure.
- `content-schema.md` — the content format. This is the file to read before authoring content.

Do not hand-edit `guide-template.html` to change content. Content comes from the JSON.
To change the shell itself, edit the template and then run `build.py` against a test
content file to confirm it still validates.
