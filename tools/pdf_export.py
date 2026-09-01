#!/usr/bin/env python3
"""
Make the presentation's "Print / Save PDF" button produce a real PDF file.

It previously called window.print(), which asks the browser to re-flow the page
into paper. That is why the output looks poor: slides get scaled and split by the
print engine rather than placed as slides.

This builds the PDF directly instead:

  * A page is 10 x 7.5 inches, the 4:3 PowerPoint size, so a slide fills it
    exactly with no margins or re-flow.
  * A slide page is drawn straight from the original 1500x1125 image, never
    screen-scraped, so it is as sharp as the source deck.
  * A text page (title, bios, fee tables, disclosures) is rendered with
    html2canvas and split across pages if it runs long.

Sam's print rules live inside `@media print`, which does not apply to an
off-screen render, so those rules are re-emitted scoped to the export stage and
reused as-is rather than reinvented.

jsPDF and html2canvas are embedded rather than loaded from a CDN. The host's
script-src does allow cdn.jsdelivr.net, but a corporate network that blocks it
would break the button in front of a prospect, which is the one moment it has to
work. Embedding costs about 0.56M characters and removes the dependency. Any
failure still falls back to window.print().

Usage:
    python3 pdf_export.py IN.html OUT.html --lib jspdf.min.js --lib html2canvas.min.js
"""

import argparse
import re
import sys

# Pinned versions, embedded at build time.
LIB_NOTE = ("jsPDF 2.5.2 and html2canvas 1.4.1, embedded so the button does not "
            "depend on a CDN being reachable during a client meeting.")


def print_rules_for_screen(html):
    """Lift the @media print body out and re-scope it to the export stage."""
    i = html.find("@media print")
    if i == -1:
        return ""
    j = html.find("{", i)
    depth, k = 0, j
    while k < len(html):
        if html[k] == "{":
            depth += 1
        elif html[k] == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    body = html[j + 1 : k]
    # This one only makes sense while actually printing.
    body = re.sub(r"body\s*\*\s*\{[^}]*\}", "", body)
    return body.replace("#printContainer", "#pdfStage")


STYLE = """
<style>
/* Sam's own print rules, re-scoped so they apply to the off-screen export
   stage. @media print does not apply to an html2canvas render. */
#pdfStage{position:fixed; left:-12000px; top:0; width:1400px; background:#fff; z-index:-1;}
#pdfStage .print-page{page-break-before:auto; background:#fff;}
__PRINT_RULES__
#pdfBusy{position:fixed; inset:0; z-index:5000; display:none; align-items:center; justify-content:center;
background:rgba(20,26,32,0.82); color:#fff; font:15px/1.5 system-ui,sans-serif;}
#pdfBusy .box{background:#26323f; padding:22px 26px; border-radius:8px; min-width:260px; text-align:center;}
#pdfBusy .bar{height:6px; background:#3c4b5c; border-radius:3px; margin-top:14px; overflow:hidden;}
#pdfBusy .bar i{display:block; height:100%; width:0; background:#5fd6a4; transition:width .2s;}
</style>
"""

SCRIPT = r"""
<script>
// ---------------------------------------------------------------------------
// Save PDF.
//
// window.print() hands the page to the browser's print engine, which re-flows
// it onto paper and is why the result looked poor. This composes the PDF
// directly: slides are placed as full 4:3 pages from their original bitmaps,
// and text sections are rasterised and paginated.
// ---------------------------------------------------------------------------
(function(){
  var btn = document.getElementById('printBtn');
  if (!btn) return;

  var PT_W = 720, PT_H = 540;           // 10 x 7.5in at 72pt/in — 4:3
  var A = window.__IMG_ASSETS__ || [];

  function bytes(b64){
    var s = atob(b64), a = new Uint8Array(s.length);
    for (var i = 0; i < s.length; i++) a[i] = s.charCodeAt(i);
    return a;
  }

  var busy = null;
  function showBusy(){
    if (!busy){
      busy = document.createElement('div');
      busy.id = 'pdfBusy';
      busy.innerHTML = '<div class="box"><div class="msg">Preparing PDF…</div>' +
                       '<div class="bar"><i></i></div></div>';
      document.body.appendChild(busy);
    }
    busy.style.display = 'flex';
  }
  function progress(done, total, label){
    if (!busy) return;
    busy.querySelector('.msg').textContent = label || ('Building page ' + done + ' of ' + total + '…');
    busy.querySelector('.bar i').style.width = Math.round(100 * done / Math.max(1, total)) + '%';
  }
  function hideBusy(){ if (busy) busy.style.display = 'none'; }

  // Full-resolution bitmap for one asset, as a JPEG data URL jsPDF accepts.
  async function assetJpeg(i){
    var a = A[i];
    var bm = await createImageBitmap(new Blob([bytes(a.d)], {type: 'image/' + a.m}));
    var c = document.createElement('canvas');
    c.width = bm.width; c.height = bm.height;
    var ctx = c.getContext('2d');
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(bm, 0, 0);
    if (bm.close) bm.close();
    return {url: c.toDataURL('image/jpeg', 0.92), w: c.width, h: c.height};
  }

  // Paint every cloned canvas on the stage at native size before capture.
  async function paintStage(root){
    var els = [].slice.call(root.querySelectorAll('canvas.cimg'));
    await Promise.all(els.map(async function(el){
      var a = A[+el.dataset.i];
      if (!a) return;
      var bm = await createImageBitmap(new Blob([bytes(a.d)], {type: 'image/' + a.m}));
      el.width = bm.width; el.height = bm.height;
      var ctx = el.getContext('2d');
      ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
      ctx.drawImage(bm, 0, 0);
      if (bm.close) bm.close();
    }));
  }

  // html2canvas rasterises inline SVG through a data: URL, which this host's CSP
  // blocks, so logos silently vanish from the PDF. Chrome also refuses to decode
  // an SVG blob via createImageBitmap. Every SVG here is plain paths and circles
  // with at most one transform, so draw them with Path2D instead — exact, and it
  // adds nothing to the file.
  function svgToCanvas(svg){
    var r = svg.getBoundingClientRect();
    var w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
    var vb = (svg.getAttribute('viewBox') || '').trim().split(/[\s,]+/).map(Number);
    var vbW = vb[2] || w, vbH = vb[3] || h;
    var S = 3;                                   // supersample, then scale down in CSS
    var c = document.createElement('canvas');
    c.width = w * S; c.height = h * S;
    var ctx = c.getContext('2d');
    ctx.scale(c.width / vbW, c.height / vbH);
    ctx.translate(-(vb[0] || 0), -(vb[1] || 0));
    var color = getComputedStyle(svg).color || '#000';

    function xform(t){
      if (!t) return;
      var re = /(translate|scale|rotate|matrix)\(([^)]*)\)/g, m;
      while ((m = re.exec(t))){
        var v = m[2].trim().split(/[\s,]+/).map(Number);
        if (m[1] === 'translate') ctx.translate(v[0] || 0, v[1] || 0);
        else if (m[1] === 'scale') ctx.scale(v[0], v.length > 1 ? v[1] : v[0]);
        else if (m[1] === 'rotate') ctx.rotate((v[0] || 0) * Math.PI / 180);
        else if (m[1] === 'matrix') ctx.transform(v[0], v[1], v[2], v[3], v[4], v[5]);
      }
    }
    function resolve(v){ return v === 'currentColor' ? color : v; }

    function paint(el, fill, stroke, sw){
      fill = el.getAttribute('fill') || fill;
      stroke = el.getAttribute('stroke') || stroke;
      sw = el.getAttribute('stroke-width') || sw;
      var tag = el.tagName.toLowerCase();
      if (tag === 'g'){
        ctx.save(); xform(el.getAttribute('transform'));
        [].forEach.call(el.children, function(k){ paint(k, fill, stroke, sw); });
        ctx.restore(); return;
      }
      var path;
      if (tag === 'path') path = new Path2D(el.getAttribute('d') || '');
      else if (tag === 'circle'){
        path = new Path2D();
        path.arc(+el.getAttribute('cx') || 0, +el.getAttribute('cy') || 0,
                 +el.getAttribute('r') || 0, 0, Math.PI * 2);
      } else if (tag === 'rect'){
        path = new Path2D();
        path.rect(+el.getAttribute('x') || 0, +el.getAttribute('y') || 0,
                  +el.getAttribute('width') || 0, +el.getAttribute('height') || 0);
      } else return;
      ctx.save(); xform(el.getAttribute('transform'));
      if (fill && fill !== 'none'){ ctx.fillStyle = resolve(fill); ctx.fill(path); }
      if (stroke && stroke !== 'none'){
        ctx.strokeStyle = resolve(stroke);
        ctx.lineWidth = parseFloat(sw) || 1;
        ctx.lineCap = svg.getAttribute('stroke-linecap') || 'butt';
        ctx.lineJoin = svg.getAttribute('stroke-linejoin') || 'miter';
        ctx.stroke(path);
      }
      ctx.restore();
    }

    [].forEach.call(svg.children, function(k){
      paint(k, svg.getAttribute('fill'), svg.getAttribute('stroke'), svg.getAttribute('stroke-width'));
    });
    c.style.width = w + 'px'; c.style.height = h + 'px';
    c.style.display = getComputedStyle(svg).display || 'inline-block';
    c.style.verticalAlign = 'middle';
    return c;
  }

  function rasterizeSvgs(root){
    [].slice.call(root.querySelectorAll('svg')).forEach(function(svg){
      try { svg.replaceWith(svgToCanvas(svg)); }
      catch (e){ /* leave it; the page still renders without the mark */ }
    });
  }

  // html2canvas returns the full element box, which often ends in a band of
  // blank page. Trim it so a section does not spill one nearly empty page.
  function trimBottom(cv){
    var w = cv.width, h = cv.height;
    var data = cv.getContext('2d').getImageData(0, 0, w, h).data;
    var step = 4, last = -1;
    for (var y = h - 1; y >= 0; y -= step){
      var row = y * w * 4;
      for (var x = 0; x < w; x += 8){
        var i = row + x * 4;
        if (data[i] < 246 || data[i+1] < 246 || data[i+2] < 246){ last = y; break; }
      }
      if (last >= 0) break;
    }
    if (last < 0) return cv;
    var keep = Math.min(h, last + step * 3);
    if (keep >= h - 8) return cv;
    var c2 = document.createElement('canvas');
    c2.width = w; c2.height = keep;
    var c2x = c2.getContext('2d');
    c2x.fillStyle = '#fff'; c2x.fillRect(0, 0, w, keep);
    c2x.drawImage(cv, 0, 0, w, keep, 0, 0, w, keep);
    return c2;
  }

  function fileName(){
    var c = (document.getElementById('tpfClientName') || {}).value || '';
    var d = (document.getElementById('tpfDate') || {}).value || '';
    var parts = ['Cerity Partners'];
    if (c.trim()) parts.push(c.trim());
    if (d) parts.push(d);
    return parts.join(' - ').replace(/[\\/:*?"<>|]/g, '') + '.pdf';
  }

  // A card that is purely a slide image goes in at native resolution.
  function pureSlideIndex(el){
    if (!el.classList.contains('ppt-slide-card')) return -1;
    if (el.classList.contains('custom-slide-card')) return -1;
    var cs = el.querySelectorAll('canvas.cimg');
    if (cs.length !== 1) return -1;
    return +cs[0].dataset.i;
  }

  async function build(){
    var jsPDF = (window.jspdf || {}).jsPDF;
    if (!jsPDF) throw new Error('jsPDF unavailable');

    var ids = (window.currentSlides || []).slice();
    if (!ids.length) throw new Error('nothing selected');

    var doc = new jsPDF({orientation: 'landscape', unit: 'pt', format: [PT_W, PT_H]});
    var stage = document.getElementById('pdfStage');
    var first = true;

    for (var n = 0; n < ids.length; n++){
      progress(n, ids.length);
      var src = document.getElementById(ids[n]);
      if (!src) continue;

      var idx = pureSlideIndex(src);
      if (idx >= 0){
        var img = await assetJpeg(idx);
        if (!first) doc.addPage([PT_W, PT_H], 'landscape');
        first = false;
        doc.addImage(img.url, 'JPEG', 0, 0, PT_W, PT_H);
        continue;
      }

      // Text section: lay it out the way printing would, then rasterise.
      stage.innerHTML = '';
      var clone = src.cloneNode(true);
      clone.classList.add('presenting');
      var page = document.createElement('div');
      page.className = 'print-page';
      page.appendChild(clone);
      stage.appendChild(page);
      await paintStage(stage);
      rasterizeSvgs(stage);
      await new Promise(function(r){ setTimeout(r, 30); });

      // Record where the page could be cut without splitting a card, measured
      // before capture and scaled to the captured pixels.
      var H2C_SCALE = 2;
      var pageTop = page.getBoundingClientRect().top;
      var breaks = [].slice.call(
            page.querySelectorAll('.bio-card, .content-block > *, table, .materials tr'))
          .map(function(el){
            return Math.round((el.getBoundingClientRect().bottom - pageTop) * H2C_SCALE);
          })
          .filter(function(v){ return v > 0; })
          .sort(function(a, b){ return a - b; });

      var shot = await window.html2canvas(page, {
        scale: H2C_SCALE, backgroundColor: '#ffffff', logging: false,
        windowWidth: 1400, useCORS: true
      });

      shot = trimBottom(shot);
      var slice = Math.round(shot.width * PT_H / PT_W);

      // A section that only just overflows reads far better shrunk onto one
      // page than sliced through the middle of a bio card.
      if (shot.height <= slice * 1.3){
        var sc = Math.min(PT_W / shot.width, PT_H / shot.height);
        var dw = shot.width * sc, dh = shot.height * sc;
        if (!first) doc.addPage([PT_W, PT_H], 'landscape');
        first = false;
        doc.addImage(shot.toDataURL('image/jpeg', 0.92), 'JPEG',
                     (PT_W - dw) / 2, 0, dw, dh);
        stage.innerHTML = '';
        continue;
      }

      // Otherwise fit to width and slice down the page.
      var y = 0;
      while (y < shot.height){
        var h = Math.min(slice, shot.height - y);
        if (y + h < shot.height){
          // Prefer the lowest card boundary that still fits on this page.
          var cut = 0;
          for (var bi = 0; bi < breaks.length; bi++){
            if (breaks[bi] > y + slice) break;
            if (breaks[bi] > y + slice * 0.45) cut = breaks[bi];
          }
          if (cut) h = cut - y;
        }
        var part = document.createElement('canvas');
        part.width = shot.width; part.height = h;
        var pc = part.getContext('2d');
        pc.fillStyle = '#fff'; pc.fillRect(0, 0, part.width, part.height);
        pc.drawImage(shot, 0, y, shot.width, h, 0, 0, shot.width, h);
        if (!first) doc.addPage([PT_W, PT_H], 'landscape');
        first = false;
        doc.addImage(part.toDataURL('image/jpeg', 0.92), 'JPEG',
                     0, 0, PT_W, PT_W * h / shot.width);
        y += h;
      }
      stage.innerHTML = '';
    }

    progress(ids.length, ids.length, 'Saving…');
    doc.save(fileName());
  }

  btn.onclick = async function(){
    showBusy();
    try {
      await build();
      hideBusy();
    } catch (err){
      hideBusy();
      // Anything at all goes wrong and the old behaviour is still there.
      var c = document.getElementById('printContainer');
      c.innerHTML = '';
      (window.currentSlides || []).forEach(function(id){
        var s = document.getElementById(id);
        if (!s) return;
        var cl = s.cloneNode(true);
        cl.classList.add('presenting');
        var p = document.createElement('div');
        p.className = 'print-page';
        p.appendChild(cl);
        c.appendChild(p);
      });
      window.print();
    }
  };
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--lib", action="append", default=[],
                    help="JS library file to embed, in load order")
    args = ap.parse_args()

    html = open(args.input, encoding="utf-8").read()
    before = len(html)

    if 'id="printBtn"' not in html:
        sys.exit("no printBtn in this file")

    rules = print_rules_for_screen(html)
    if not rules.strip():
        sys.exit("could not find the @media print rules to re-scope")

    # currentSlides is a module-level binding in Sam's script; expose it.
    hook = "currentSlides = ['sec-titlepage', ...expandForPresentation(presentationOrder), 'sec-disclosures'];"
    if hook not in html:
        sys.exit("could not find where currentSlides is assigned")
    html = html.replace(hook, hook + "\nwindow.currentSlides = currentSlides;", 1)

    libs = ""
    for path in args.lib:
        src = open(path, encoding="utf-8").read()
        if "</script" in src.lower():
            sys.exit(f"{path} contains a closing script tag; cannot inline safely")
        libs += f"\n<script>/* {path} */\n{src}\n</script>\n"

    block = (STYLE.replace("__PRINT_RULES__", rules)
             + '<div id="pdfStage"></div>'
             + libs
             + SCRIPT)
    html = html.replace("</body>", block + "\n</body>", 1)

    # The button no longer just prints.
    html = html.replace(">Print / Save PDF<", ">Save PDF<", 1)

    open(args.output, "w", encoding="utf-8").write(html)
    print(f"re-scoped print rules: {len(rules)} chars")
    print(f"embedded libraries: {len(args.lib)}  ({LIB_NOTE})")
    print(f"{before/1e6:.2f}M -> {len(html)/1e6:.2f}M chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
