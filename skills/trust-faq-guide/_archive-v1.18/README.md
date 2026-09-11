# v1.18 — rollback copy

The skill exactly as it stood before the v2.0 rebuild, unmodified. Keep this until
v2.0 has produced a few real guides successfully.

To roll back: upload this folder's contents (SKILL.md + references/) as the skill,
in place of the v2.0 package.

Known defects in this version, for the record:
- references/html-shell.md is 50,866 bytes; reading it whole silently drops lines
  137-638, which is where the <script> block and most of the <style> block live.
  This is why guides built with it drift.
- .flow-stage.family-trust, .flow-stage.children and .view-btn are used in the
  snippets with no CSS rule.
- Step 1's intake block starts at "2." and two lines reference removed questions.
