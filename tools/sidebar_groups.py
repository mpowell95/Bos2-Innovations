#!/usr/bin/env python3
"""
Group the presentation's "On Deck" sidebar by section.

buildSidebar() listed every entry in currentSlides as a flat row, so a deck with
a couple of gallery sections produced a sidebar dozens of rows long and the
advisor lost the shape of the meeting.

Entries are now grouped under the section they belong to, derived from the DOM
rather than from expandForPresentation, so nothing about how the deck is built
has to change: a slide card reports the .content-block it sits in, and anything
else is its own group.

Three shapes fall out of that, and all three occur in this deck:

  * A section with no slides of its own — Title Page, Fee Structure, Meet Your
    Team, Disclosure — stays a single plain row.
  * A gallery-only section contributes slides but no page of its own, so its
    header is a label that jumps to the first slide.
  * General Resources is the one section that appears both as its own page and
    as the parent of a slide, so its page becomes the group header.

Only the group holding the current slide is open. Clicking any header navigates
into that group, which opens it, so there is no separate expand state to keep in
step with the deck position.

Usage:
    python3 sidebar_groups.py IN.html OUT.html
"""

import argparse
import sys

OLD = """function buildSidebar(){
const wrap = document.getElementById('overlaySidebar');
wrap.innerHTML = '';
currentSlides.forEach((id,i)=>{
const block = document.getElementById(id);
const item = document.createElement('div');
item.className = 'present-nav-item';
item.dataset.index = i;
item.innerHTML = '<span class="sb-num">'+(i+1)+'</span><span>'+block.dataset.title+'</span>';
item.addEventListener('click', ()=>{ currentIndex = i; renderSlide(); });
wrap.appendChild(item);
});
}

function updateSidebar(){
const items = document.querySelectorAll('#overlaySidebar .present-nav-item');
items.forEach(item=>{
const i = parseInt(item.dataset.index, 10);
item.classList.toggle('active', i===currentIndex);
item.classList.toggle('done', i<currentIndex);
});
const activeItem = document.querySelector('#overlaySidebar .present-nav-item.active');
if(activeItem) activeItem.scrollIntoView({ block:'nearest' });
}"""

NEW = """// Sidebar entries are grouped under the section they belong to. A slide card
// reports the .content-block it sits in; anything else is its own group. Only
// the group holding the current slide is open, and clicking a header navigates
// into that group, so expansion follows the deck position with no separate
// state to keep in step.
function sidebarGroups(){
const groups = [];
currentSlides.forEach((id, i)=>{
const el = document.getElementById(id);
if(!el) return;
const isCard = el.classList.contains('ppt-slide-card');
const owner = isCard ? (el.closest('.content-block') || {}) : el;
const gid = (isCard ? (owner.id || id) : id);
let g = groups[groups.length-1];
if(!g || g.id !== gid){
const block = document.getElementById(gid);
g = { id: gid, title: (block && block.dataset.title) || gid, head: null, items: [] };
groups.push(g);
}
// A section that contributes a page of its own becomes the group's header.
if(!isCard && g.head === null && g.items.length === 0) g.head = i;
else g.items.push({ index: i, title: (el.dataset.title || id) });
});
return groups;
}

function buildSidebar(){
const wrap = document.getElementById('overlaySidebar');
wrap.innerHTML = '';
// Where you are in the deck is what an advisor wants mid-meeting, so state it
// once at the top rather than making them count rows.
const pos = document.createElement('div');
pos.className = 'sb-position';
pos.id = 'sbPosition';
wrap.appendChild(pos);
sidebarGroups().forEach((g, gi)=>{
// Where a group has a page of its own and nothing else, keep the plain row.
if(g.items.length === 0){
const item = document.createElement('div');
item.className = 'present-nav-item';
item.dataset.index = g.head;
item.dataset.group = g.id;
item.innerHTML = '<span class="sb-rail"></span><span class="sb-gtitle">'+g.title+'</span>';
item.addEventListener('click', ()=>{ currentIndex = g.head; renderSlide(); });
wrap.appendChild(item);
return;
}
const box = document.createElement('div');
box.className = 'sb-group';
box.dataset.group = g.id;

const head = document.createElement('div');
head.className = 'present-nav-item sb-head';
// A gallery-only section has no page of its own, so its header goes to the
// first slide in the group instead.
const target = g.head !== null ? g.head : g.items[0].index;
head.dataset.index = target;
head.innerHTML = '<span class="sb-rail"></span><span class="sb-gtitle">'+g.title+'</span>'+
'<span class="sb-count">'+g.items.length+'</span>';
head.addEventListener('click', ()=>{ currentIndex = target; renderSlide(); });
box.appendChild(head);

const kids = document.createElement('div');
kids.className = 'sb-children';
g.items.forEach(it=>{
const row = document.createElement('div');
row.className = 'present-nav-item sb-child';
row.dataset.index = it.index;
row.innerHTML = '<span class="sb-rail"></span><span class="sb-ctitle">'+it.title+'</span>';
row.addEventListener('click', (e)=>{ e.stopPropagation(); currentIndex = it.index; renderSlide(); });
kids.appendChild(row);
});
box.appendChild(kids);
wrap.appendChild(box);
});
}

function updateSidebar(){
document.querySelectorAll('#overlaySidebar .present-nav-item').forEach(item=>{
const i = parseInt(item.dataset.index, 10);
const isHead = item.classList.contains('sb-head');
// A header is only "active" when the deck is on the page it points at; a
// group holding the current slide is marked separately.
item.classList.toggle('active', i === currentIndex && !(isHead && i !== currentIndex));
item.classList.toggle('done', i < currentIndex);
});
document.querySelectorAll('#overlaySidebar .sb-group').forEach(box=>{
const idxs = [].slice.call(box.querySelectorAll('.present-nav-item'))
.map(n=>parseInt(n.dataset.index, 10));
const holds = idxs.indexOf(currentIndex) !== -1;
box.classList.toggle('open', holds);
box.classList.toggle('done', Math.max.apply(null, idxs) < currentIndex);

});
const pos = document.getElementById('sbPosition');
if(pos){
const n = currentSlides.length;
const pct = n > 1 ? Math.round(100 * currentIndex / (n - 1)) : 100;
pos.innerHTML = '<span class="sb-pos-count">'+(currentIndex+1)+' <i>of</i> '+n+'</span>'+
'<span class="sb-progress"><i style="width:'+pct+'%"></i></span>';
}
const activeItem = document.querySelector('#overlaySidebar .present-nav-item.active');
if(activeItem) activeItem.scrollIntoView({ block:'nearest' });
}"""

CSS = """
/* A presenting slide card is position:absolute with inset:0, but .present-stage
   was not a positioned ancestor, so the card resolved against the full-screen
   overlay and covered the sidebar. On Deck was therefore unclickable whenever a
   slide image was on screen. Confining the card to the stage fixes it. */
.present-stage{ position:relative; }

/* ---- On Deck ------------------------------------------------------------
   A progress rail rather than a menu. Numbered circles competed with the
   section names and told an advisor nothing they needed; position in the deck
   is the one fact worth stating, so it is stated once at the top and otherwise
   carried by a continuous rail down the gutter. */
.present-sidebar{ width:258px; padding:16px 0; }

.sb-position{ padding:2px 20px 16px; }
.sb-pos-count{
display:block; font-family:'Helvetica Neue', Arial, sans-serif;
font-size:19px; font-weight:600; color:var(--cobalt); letter-spacing:-.01em;
}
.sb-pos-count i{ font-style:normal; font-weight:400; font-size:13px; color:var(--clay); }
.sb-progress{ display:block; height:3px; margin-top:8px; background:var(--rule); border-radius:2px; overflow:hidden; }
.sb-progress i{ display:block; height:100%; background:var(--tradewind); transition:width .22s ease; }

/* One continuous line through every row, carrying the position marker. */
.present-nav-item{ position:relative; padding:10px 18px 10px 34px; align-items:center; border-left:none; }
.present-nav-item .sb-rail{ position:absolute; left:19px; top:0; bottom:0; width:2px; background:var(--rule); }
.present-nav-item .sb-rail::after{
content:""; position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
width:7px; height:7px; border-radius:50%; background:var(--rule);
box-shadow:0 0 0 3px var(--vellum);
}
.present-nav-item.done .sb-rail, .present-nav-item.done .sb-rail::after{ background:var(--tradewind); }
.present-nav-item.active .sb-rail::after{ width:11px; height:11px; background:var(--cobalt); }

.sb-gtitle{ flex:1; font-size:13.5px; }
.sb-ctitle{ flex:1; }
.present-nav-item.active{ background:#fff; color:var(--cobalt); font-weight:600; }
.sb-group.open > .sb-head{ color:var(--cobalt); font-weight:600; }

.sb-head .sb-count{
flex-shrink:0; font-family:'Helvetica Neue', Arial, sans-serif;
font-size:10px; letter-spacing:.06em; color:var(--clay); font-variant-numeric:tabular-nums;
}
.sb-group.open > .sb-head .sb-count{ color:var(--tradewind); }

.sb-group .sb-children{ display:none; }
.sb-group.open .sb-children{ display:block; }
.present-nav-item.sb-child{ padding-left:46px; font-size:12.5px; color:#5b6875; }
.present-nav-item.sb-child .sb-rail{ left:31px; }
.present-nav-item.sb-child .sb-rail::after{ width:5px; height:5px; }
.present-nav-item.sb-child.active{ color:var(--cobalt); }
.present-nav-item.sb-child.active .sb-rail::after{ width:9px; height:9px; }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()

    html = open(args.input, encoding="utf-8").read()
    before = len(html)

    if "function sidebarGroups()" in html:
        sys.exit("sidebar grouping already applied")
    if OLD not in html:
        sys.exit("could not find buildSidebar/updateSidebar to replace")

    html = html.replace(OLD, NEW, 1)

    cut = html.find("</style>")
    if cut == -1:
        sys.exit("no </style> to extend")
    html = html[:cut] + CSS + html[cut:]

    open(args.output, "w", encoding="utf-8").write(html)
    print(f"sidebar grouped -> {before/1e6:.2f}M -> {len(html)/1e6:.2f}M chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
