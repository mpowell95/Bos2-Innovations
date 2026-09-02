#!/usr/bin/env python3
"""
Save a slide selection as a reusable template.

Advisors rebuild the same selections meeting after meeting. This stores a named
selection — which sections, which slides within them and in what order, and
which colleagues — and puts it back with one click. One template can be marked
the default and is applied automatically when the tool opens.

Storage is localStorage, which works under the host's CSP and needs no backend.
That makes templates per-browser and per-device: they do not follow an advisor
to another machine and are not shared with the team. Export/import would be the
next step if sharing is wanted.

Applying a template drives the checkboxes and fires their change events rather
than writing to the internal state directly, so every existing handler runs and
there is one code path to keep correct. Explicit orders are restored afterwards,
since check order alone does not preserve a drag-reordered deck.

Slide ids can change when the toolkit is regenerated, so a template applies
whatever still exists and reports what it could not find rather than failing
silently.

Usage:
    python3 save_templates.py IN.html OUT.html
"""

import argparse
import sys

BAR = """
<div class="tpl-bar" id="tplBar">
<div class="tpl-row">
<h3>Templates</h3>
<select id="tplSelect"><option value="">— saved templates —</option></select>
<button type="button" class="linklike" id="tplApply">Apply</button>
<button type="button" class="linklike" id="tplSave">Save current…</button>
<button type="button" class="linklike" id="tplDefault">Set as default</button>
<button type="button" class="linklike" id="tplDelete">Delete</button>
</div>
<p class="tpl-note" id="tplNote">Saved on this browser only.</p>
</div>
"""

CSS = """
/* Saved selection templates */
.tpl-bar{ border:1px solid var(--rule); border-radius:8px; padding:12px 16px; margin:0 0 18px; background:var(--vellum); }
.tpl-row{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.tpl-bar h3{ margin:0; font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--clay); }
.tpl-bar select{ min-width:220px; padding:6px 8px; border:1px solid var(--rule); border-radius:4px;
font-family:inherit; font-size:13px; color:#33404d; background:#fff; }
.tpl-note{ margin:8px 0 0; font-size:12px; color:var(--clay); }
.tpl-note.warn{ color:#a5471a; }
"""

SCRIPT = r"""
<script>
// ---------------------------------------------------------------------------
// Saved selection templates. See save_templates.py.
// ---------------------------------------------------------------------------
(function(){
  var KEY = 'ceritypartners.prospectToolkit.templates.v1';
  var sel  = document.getElementById('tplSelect');
  var note = document.getElementById('tplNote');
  if (!sel) return;

  function say(msg, warn){
    note.textContent = msg;
    note.classList.toggle('warn', !!warn);
  }

  // Private windows and blocked site data throw on access, so never let a
  // storage failure take the builder down with it.
  function read(){
    try {
      var raw = localStorage.getItem(KEY);
      var o = raw ? JSON.parse(raw) : null;
      if (!o || typeof o !== 'object') return {templates:{}, def:''};
      o.templates = o.templates || {};
      return o;
    } catch (e){ return {templates:{}, def:''}; }
  }
  function write(store){
    try { localStorage.setItem(KEY, JSON.stringify(store)); return true; }
    catch (e){ say('This browser will not let the tool save templates.', true); return false; }
  }

  function boxes(value){
    return [].slice.call(
      document.querySelectorAll('input[type="checkbox"][value="' + value + '"]'));
  }
  function set(value, on){
    // Every copy of a checkbox is updated and notified. The handlers add to a
    // Set and guard their pushes, so notifying more than once is harmless.
    boxes(value).forEach(function(cb){
      if (cb.checked !== on){ cb.checked = on; cb.dispatchEvent(new Event('change', {bubbles:true})); }
    });
  }

  function capture(){
    var slides = {};
    presentationOrder.forEach(function(id){
      var block = document.getElementById(id);
      if (block && block.dataset.gallery === 'true'){
        slides[id] = (gallerySlideOrder[id] || []).filter(function(s){
          return selectedGallerySlides.has(s);
        });
      }
    });
    return {
      order: presentationOrder.slice(),
      slides: slides,
      contacts: Array.from(selectedContactIds),
      presentedBy: (document.getElementById('tpfPresentedBy') || {}).value || ''
    };
  }

  function clearAll(){
    [].slice.call(document.querySelectorAll('#builderList .builder-item > input:checked'))
      .forEach(function(cb){ set(cb.value, false); });
    [].slice.call(document.querySelectorAll('.gallery-check-item input:checked'))
      .forEach(function(cb){ set(cb.value, false); });
    [].slice.call(document.querySelectorAll('#contactCheckboxes input:checked'))
      .forEach(function(cb){ set(cb.value, false); });
  }

  function apply(t){
    if (!t) return;
    clearAll();
    var missing = [];

    (t.order || []).forEach(function(id){
      if (!document.getElementById(id)){ missing.push(id); return; }
      set(id, true);
    });
    // Ticking a section builds its nested list, so slides are set afterwards.
    (t.order || []).forEach(function(id){
      ((t.slides || {})[id] || []).forEach(function(sid){
        if (!document.getElementById(sid)){ missing.push(sid); return; }
        set(sid, true);
      });
    });
    (t.contacts || []).forEach(function(cid){
      if (!boxes(cid).length){ missing.push(cid); return; }
      set(cid, true);
    });

    // Check order does not preserve a deck that was dragged into a custom
    // sequence, so restore the recorded orders explicitly.
    presentationOrder = (t.order || []).filter(function(id){ return document.getElementById(id); });
    Object.keys(t.slides || {}).forEach(function(id){
      gallerySlideOrder[id] = (t.slides[id] || []).filter(function(s){ return document.getElementById(s); });
    });
    renderOrderList();

    var pb = document.getElementById('tpfPresentedBy');
    if (pb && t.presentedBy) pb.value = t.presentedBy;

    if (missing.length){
      say('Applied. ' + missing.length + ' item(s) in this template no longer exist in the toolkit and were skipped.', true);
    } else {
      say('Applied.');
    }
  }

  function refresh(keep){
    var store = read();
    var names = Object.keys(store.templates).sort(function(a,b){ return a.localeCompare(b); });
    sel.innerHTML = '<option value="">— saved templates —</option>' +
      names.map(function(n){
        return '<option value="' + n.replace(/"/g,'&quot;') + '">' +
               n + (store.def === n ? '  (default)' : '') + '</option>';
      }).join('');
    if (keep && store.templates[keep]) sel.value = keep;
  }

  document.getElementById('tplSave').addEventListener('click', function(){
    if (!presentationOrder.length){ say('Nothing selected to save yet.', true); return; }
    var name = prompt('Name this template:', sel.value || '');
    if (name === null) return;
    name = name.trim();
    if (!name){ say('Give the template a name.', true); return; }
    var store = read();
    if (store.templates[name] && !confirm('Replace the existing template "' + name + '"?')) return;
    store.templates[name] = capture();
    if (write(store)){ refresh(name); say('Saved "' + name + '" on this browser.'); }
  });

  document.getElementById('tplApply').addEventListener('click', function(){
    var store = read(), name = sel.value;
    if (!name || !store.templates[name]){ say('Choose a template first.', true); return; }
    apply(store.templates[name]);
  });

  document.getElementById('tplDefault').addEventListener('click', function(){
    var store = read(), name = sel.value;
    if (!name || !store.templates[name]){ say('Choose a template first.', true); return; }
    store.def = (store.def === name) ? '' : name;
    if (write(store)){
      refresh(name);
      say(store.def ? '"' + name + '" will be applied when the tool opens.'
                    : 'Default cleared.');
    }
  });

  document.getElementById('tplDelete').addEventListener('click', function(){
    var store = read(), name = sel.value;
    if (!name || !store.templates[name]){ say('Choose a template first.', true); return; }
    if (!confirm('Delete the template "' + name + '"?')) return;
    delete store.templates[name];
    if (store.def === name) store.def = '';
    if (write(store)){ refresh(); say('Deleted "' + name + '".'); }
  });

  refresh();

  // buildChecklist() runs only when the Build a Presentation tab is opened, so
  // there is nothing to apply a default to until then. Apply once, the first
  // time the builder is built, and never again — otherwise it would overwrite
  // whatever the advisor has since selected.
  var appliedDefault = false;
  function applyDefaultOnce(){
    if (appliedDefault) return;
    var store = read();
    if (!store.def || !store.templates[store.def]) { appliedDefault = true; return; }
    if (!document.querySelector('#builderList .builder-item > input')) return;
    appliedDefault = true;
    sel.value = store.def;
    apply(store.templates[store.def]);
    say('Applied your default template, "' + store.def + '".');
  }
  document.addEventListener('click', function(e){
    var btn = e.target.closest && e.target.closest('.modebtn');
    if (btn && btn.dataset.mode === 'builder') setTimeout(applyDefaultOnce, 0);
  });
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()

    html = open(args.input, encoding="utf-8").read()
    before = len(html)

    if 'id="tplBar"' in html:
        sys.exit("templates already present")

    anchor = '<div class="title-page-form">'
    if anchor not in html:
        sys.exit("could not find the builder's title-page form to anchor the bar to")
    html = html.replace(anchor, BAR + anchor, 1)

    cut = html.find("</style>")
    if cut == -1:
        sys.exit("no </style> to extend")
    html = html[:cut] + CSS + html[cut:]

    # Anchor to the document's real closing tag: embedded libraries contain
    # "</body>" inside string literals.
    cut = html.rfind("</body>")
    if cut == -1:
        sys.exit("no </body> to anchor to")
    html = html[:cut] + SCRIPT + "\n" + html[cut:]

    open(args.output, "w", encoding="utf-8").write(html)
    print(f"templates added -> {before/1e6:.2f}M -> {len(html)/1e6:.2f}M chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
