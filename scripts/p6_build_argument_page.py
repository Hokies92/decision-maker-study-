#!/usr/bin/env python3
"""p6_build_argument_page.py — the argument page: V1 two-sided ledger, V3 silent gap, V4 what wins / what loses, V5 two
vocabularies (P6.S04). One self-contained HTML file, data embedded from the Phase 6 data layer.

Inputs: 06_visualization/data/v1_ledger.json, v3_silent_gap.json, v4_wins_loses.json, v5_vocabularies.json (P6.S03).
Output: 06_visualization/argument.html — committed (public with the repo) and published as a page (D6-2: both).
Every number on the page is computed in the page from the embedded data; the page types none by hand. The question, unit,
sources and caveats of each view are read from each file's meta.
Usage: python3 -I scripts/p6_build_argument_page.py [--fragment <path for the publishable copy>]
"""
import json
import sys
from pathlib import Path

DATA = Path("06_visualization/data")
OUT = Path("06_visualization/argument.html")
REPO = "https://github.com/Hokies92/decision-maker-study-"


def main() -> int:
    v1, v3, v4, v5 = (json.loads((DATA / f).read_text(encoding="utf-8")) for f in
                      ("v1_ledger.json", "v3_silent_gap.json", "v4_wins_loses.json", "v5_vocabularies.json"))
    answers = dict(v3.pop("answers"))
    answers.update(v4.pop("answers"))
    payload = {"v1": v1, "v3": v3, "v4": v4, "v5": v5, "answers": dict(sorted(answers.items())), "repo": REPO}
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=False).replace("</", "<\\/")
    page = TEMPLATE.replace("__DATA__", blob)
    # The committed file is a full document (opens on its own, standards mode). --fragment writes the same page without
    # the document wrapper, which is the form the publishing host expects (it adds its own).
    OUT.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                   '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                   + page.replace("<main>", "</head>\n<body>\n<main>", 1) + "</body>\n</html>\n", encoding="utf-8")
    if "--fragment" in sys.argv:
        Path(sys.argv[sys.argv.index("--fragment") + 1]).write_text(page, encoding="utf-8")
    print(f"{OUT}: {OUT.stat().st_size} bytes; answers embedded {len(answers)}")
    return 0


TEMPLATE = r"""<title>The Silent Gap</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: one reading column; each view is a band — question, chart, then its sources and caveats. Charts use the validated data palette. */
:root{
  --bg:#f6f7f8; --panel:#ffffff; --fg:#14181d; --fg2:#4d5560; --muted:#7c8590; --rule:#dde1e6; --axis:#b9c0c8;
  --valued:#2a78d6; --received:#eb6834; --lose:#e34948; --win:#2a78d6; --mark:#14181d; --ring:#ffffff; --hl:#eef3fb;
  --display:"Archivo",system-ui,-apple-system,"Segoe UI",sans-serif;
  --body:"Source Serif 4",Georgia,"Times New Roman",serif;
  --data:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121417; --panel:#1a1d21; --fg:#eef0f2; --fg2:#b8bfc7; --muted:#8a929b; --rule:#2c3137; --axis:#3d434a;
  --valued:#3987e5; --received:#d95926; --lose:#e66767; --win:#3987e5; --mark:#eef0f2; --ring:#1a1d21; --hl:#1d2733; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121417; --panel:#1a1d21; --fg:#eef0f2; --fg2:#b8bfc7; --muted:#8a929b; --rule:#2c3137; --axis:#3d434a;
  --valued:#3987e5; --received:#d95926; --lose:#e66767; --win:#3987e5; --mark:#eef0f2; --ring:#1a1d21; --hl:#1d2733; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.55;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:980px;margin:0 auto;padding-block:40px 64px;display:grid;grid-template-columns:minmax(0,1fr);gap:56px}
.sec>*,header>*{min-width:0}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0;letter-spacing:-.01em}
h1{font-size:clamp(34px,6vw,58px);font-stretch:85%;font-weight:800;line-height:1.02}
h2{font-size:clamp(22px,3.2vw,30px);font-stretch:90%;font-weight:700;line-height:1.15}
h3{font-size:15px;font-weight:700}
p{margin:0;max-width:66ch}
.eyebrow{font-family:var(--display);font-size:12px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
header{display:grid;gap:18px}
.lede{font-size:clamp(17px,2.1vw,20px);color:var(--fg2)}
.lede b{color:var(--fg);font-weight:600}
.n{font-family:var(--data);font-variant-numeric:tabular-nums;font-size:.92em}
.sec{display:grid;gap:16px;scroll-margin-top:16px}
.q{font-family:var(--display);font-size:17px;font-weight:500;color:var(--fg2);font-stretch:95%}
.chart{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:16px;min-width:0;overflow-x:auto}
.chart svg{display:block;width:100%;height:auto;overflow:visible}
.controls{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;font-family:var(--display);font-size:14px}
select{max-width:100%}
select,button{font-family:var(--display);font-size:14px;color:var(--fg);background:var(--panel);border:1px solid var(--axis);border-radius:6px;padding:6px 10px}
button{cursor:pointer}
select:focus-visible,button:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--valued);outline-offset:2px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-family:var(--display);font-size:13px;color:var(--fg2)}
.key{display:inline-flex;align-items:center;gap:6px}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block}
.bar{width:16px;height:10px;border-radius:3px;display:inline-block}
.about{font-family:var(--display);font-size:13px;color:var(--fg2);border-top:1px solid var(--rule);padding-top:12px;display:grid;gap:6px}
.about ul{margin:0;padding-left:18px;display:grid;gap:3px}
.about code{font-family:var(--data);font-size:12px;overflow-wrap:anywhere}
.reader{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:16px;display:grid;gap:12px;min-width:0}
.reader[hidden]{display:none}
.reader-head{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline;justify-content:space-between}
.tabs{display:flex;flex-wrap:wrap;gap:6px}
.tabs button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.quotes{list-style:none;margin:0;padding:0;display:grid;gap:10px;max-height:420px;overflow-y:auto}
.quotes li{border-left:3px solid var(--rule);padding:2px 0 2px 12px}
.quotes li.best{border-left-color:var(--win)} .quotes li.worst{border-left-color:var(--lose)}
.quotes .meta{font-family:var(--data);font-size:11.5px;color:var(--muted);margin-top:2px}
.tbl{overflow-x:auto;min-width:0;background:var(--panel);border:1px solid var(--rule);border-radius:10px}
table{border-collapse:collapse;width:100%;font-family:var(--display);font-size:13.5px;min-width:720px}
th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--rule)}
th{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600}
td.gap{color:var(--lose);font-weight:600}
tr.gaprow{background:var(--hl)}
td.num{font-family:var(--data);font-variant-numeric:tabular-nums;text-align:right}
.tip{position:fixed;z-index:20;pointer-events:none;max-width:320px;background:var(--fg);color:var(--bg);font-family:var(--display);
  font-size:12.5px;line-height:1.4;padding:8px 10px;border-radius:6px;opacity:0;transition:opacity .08s}
.tip.on{opacity:1}
svg text{font-family:var(--display)}
.ax{stroke:var(--axis);stroke-width:1} .gr{stroke:var(--rule);stroke-width:1}
.lab{fill:var(--fg);font-size:13px} .sub{fill:var(--muted);font-size:11px} .val{fill:var(--fg2);font-size:12px;font-family:var(--data)}
.hit{fill:transparent;cursor:pointer} .hit:hover+g .row-bg, .sel .row-bg{fill:var(--hl)}
.row-bg{fill:transparent}
footer{font-family:var(--display);font-size:13px;color:var(--muted);border-top:1px solid var(--rule);padding-top:16px;display:grid;gap:6px}
footer a{color:var(--fg2)}
@media (prefers-reduced-motion: reduce){.tip{transition:none}}
</style>

<main>
<header>
  <div class="eyebrow">Decision-maker study · Phase 6</div>
  <h1>The Silent Gap</h1>
  <p class="lede" id="lede"></p>
  <nav class="legend" aria-label="Sections">
    <a href="#ledger">1 · Valued vs received</a><a href="#silent">2 · Felt but not said</a><a href="#wins">3 · What wins, what loses</a><a href="#words">4 · Two vocabularies</a>
  </nav>
</header>

<section class="sec" id="ledger">
  <div class="eyebrow">View 1 · The two-sided ledger</div>
  <h2>Customers get the pitch. They miss the case.</h2>
  <p class="q" data-q="v1"></p>
  <div class="controls">
    <label for="cohort">Cohort</label>
    <select id="cohort"></select>
    <span class="legend" id="v1legend"></span>
  </div>
  <div class="chart" id="v1chart"></div>
  <div class="about" data-about="v1"></div>
</section>

<section class="sec" id="silent">
  <div class="eyebrow">View 2 · The silent gap</div>
  <h2>The largest gap is the one customers do not put into words.</h2>
  <p class="q" data-q="v3"></p>
  <div class="chart" id="v3chart"></div>
  <p class="legend">Select a point to read the answers behind it.</p>
  <div class="reader" id="v3reader" hidden></div>
  <div class="about" data-about="v3"></div>
</section>

<section class="sec" id="wins">
  <div class="eyebrow">View 3 · What wins, what loses</div>
  <h2>Knowledge wins accounts. Conduct loses them.</h2>
  <p class="q" data-q="v4"></p>
  <div class="controls"><span class="legend"><span class="key"><span class="bar" style="background:var(--lose)"></span>ineffective, in worst accounts</span><span class="key"><span class="bar" style="background:var(--win)"></span>effective, in best accounts</span></span></div>
  <div class="chart" id="v4chart"></div>
  <p class="legend">Select a behaviour to read what decision-makers said.</p>
  <div class="reader" id="v4reader" hidden></div>
  <div class="about" data-about="v4"></div>
</section>

<section class="sec" id="words">
  <div class="eyebrow">View 4 · Two vocabularies</div>
  <h2>Where the vendor has a word and the customer has none.</h2>
  <p class="q" data-q="v5"></p>
  <div class="tbl" id="v5table"></div>
  <div class="about" data-about="v5"></div>
</section>

<footer id="foot"></footer>
</main>
<div class="tip" id="tip" role="tooltip"></div>

<script type="application/json" id="data">__DATA__</script>
<script>
(function(){
const D = JSON.parse(document.getElementById('data').textContent);
const NS = 'http://www.w3.org/2000/svg';
const $ = s => document.querySelector(s);
const fmtPct = v => (v*100).toFixed(0) + '%';
const fmtGap = v => (v>0?'+':v<0?'−':'') + Math.abs(v).toFixed(2);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const QNAME = {Q21:'What differentiates a vendor', Q22:'Most effective sales teams', Q23:'Least effective sales teams', Q24:'Contact in best relationships', Q25:'Contact in worst relationships'};
function el(tag, attrs, parent){ const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function text(parent, x, y, s, cls, anchor){ const t = el('text', {x, y, class: cls || 'lab', 'text-anchor': anchor || 'start'}, parent); t.textContent = s; return t; }
const tip = $('#tip');
function showTip(evt, html){ tip.innerHTML = html; tip.classList.add('on'); const r = tip.getBoundingClientRect();
  let x = evt.clientX + 14, y = evt.clientY + 14; if (x + r.width > innerWidth - 8) x = evt.clientX - r.width - 14; if (y + r.height > innerHeight - 8) y = evt.clientY - r.height - 14;
  tip.style.left = Math.max(8, x) + 'px'; tip.style.top = Math.max(8, y) + 'px'; }
function hideTip(){ tip.classList.remove('on'); }

// meta: question and "about" blocks
for (const k of ['v1','v3','v4','v5']) {
  const m = D[k].meta;
  document.querySelector(`[data-q="${k}"]`).textContent = m.question;
  document.querySelector(`[data-about="${k}"]`).innerHTML =
    `<h3>About this view</h3><div><b>Unit:</b> ${esc(m.unit)} · <b>Provenance:</b> ${esc(m.provenance)}</div>` +
    `<ul>${m.caveats.map(c => `<li>${esc(c)}</li>`).join('')}</ul>` +
    `<div><b>Sources:</b> ${m.sources.map(s => `<code>${esc(s)}</code>`).join(', ')} · built by <code>${esc(m.generated_by)}</code></div>`;
}

// lede: computed from the data
const allRow = p => p.cohorts.find(c => c.cohort === 'C-L-ALL-RESPONDENTS');
const vxe = D.v1.pairs.filter(p => p.type === 'value_vs_experience').map(p => ({p, r: allRow(p)}));
const most = vxe.reduce((a,b) => b.r.gap < a.r.gap ? b : a), over = vxe.reduce((a,b) => b.r.gap > a.r.gap ? b : a);
const pt = id => D.v3.points.find(x => x.pair === id);
$('#lede').innerHTML = `Across ${allRow(vxe[0].p).n} decision-makers, the one thing salespeople deliver more than it is valued is <b>${esc(over.p.concept.toLowerCase())}</b> (<span class="n">${fmtGap(over.r.gap)}</span>). ` +
  `The largest shortfall is <b>${esc(most.p.concept.toLowerCase())}</b> (<span class="n">${fmtGap(most.r.gap)}</span>), and only <span class="n">${pt(most.p.pair).answers}</span> of their written answers touch it.`;

// ---------------- V1 ledger
const sel = $('#cohort');
const cohorts = D.v1.pairs[0].cohorts;
const groups = {};
cohorts.forEach(c => (groups[c.dimension] = groups[c.dimension] || []).push(c));
for (const dim of Object.keys(groups)) {
  const og = document.createElement(dim === 'All' ? 'div' : 'optgroup');
  if (dim !== 'All') og.label = dim;
  for (const c of groups[dim]) { const o = document.createElement('option'); o.value = c.cohort; o.disabled = !c.usable;
    o.textContent = `${c.label} (n = ${c.n})${c.usable ? '' : ' — below 25, not shown'}`; (dim === 'All' ? sel : og).appendChild(o); }
  if (dim !== 'All') sel.appendChild(og);
}
sel.value = 'C-L-ALL-RESPONDENTS';
$('#v1legend').innerHTML = `<span class="key"><span class="dot" style="background:var(--valued)"></span>valued / about them</span>` +
  `<span class="key"><span class="dot" style="background:var(--received)"></span>received / about me</span>` +
  `<span class="key"><span class="dot" style="border:1.5px solid var(--muted)"></span>All respondents, for reference</span>`;
function drawV1(){
  const host = $('#v1chart'); host.innerHTML = '';
  const W = Math.max(320, host.clientWidth - 32), narrow = W < 620;
  const L = narrow ? 8 : Math.min(300, W * 0.36), R = W - 56, rh = narrow ? 64 : 46, top = 34;
  const order = D.v1.pairs.slice().sort((a,b) => (a.type === b.type ? allRow(a).gap - allRow(b).gap : a.type === 'value_vs_experience' ? -1 : 1));
  const H = top + rh * order.length + 34 + 26;
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Valued against received, by concept'}, host);
  const x = v => L + v * (R - L);
  for (const v of [0, .25, .5, .75, 1]) { el('line', {x1: x(v), x2: x(v), y1: top - 10, y2: top + rh * order.length + 22, class: 'gr'}, svg); text(svg, x(v), top - 16, fmtPct(v), 'sub', 'middle'); }
  const cid = sel.value;
  let y0 = top, lastType = null;
  order.forEach((p, i) => {
    if (p.type !== lastType) { if (lastType) y0 += 22; text(svg, narrow ? 8 : 8, y0 + 4, p.type === 'value_vs_experience' ? 'VALUED vs RECEIVED' : (narrow ? 'SALESPEOPLE KNOW: THEMSELVES vs ME' : 'WHAT SALESPEOPLE KNOW: ABOUT THEMSELVES vs ABOUT ME'), 'sub'); y0 += 12; lastType = p.type; }
    const c = p.cohorts.find(z => z.cohort === cid), a0 = allRow(p);
    const yy = y0 + (narrow ? 40 : rh / 2);
    const g = el('g', {}, svg);
    el('rect', {x: 0, y: y0, width: W, height: rh, class: 'row-bg'}, g);
    text(g, narrow ? 8 : L - 14, narrow ? y0 + 16 : yy + 1, p.concept, 'lab', narrow ? 'start' : 'end');
    text(g, narrow ? 8 : L - 14, narrow ? y0 + 30 : yy + 15, `${p.pair} · ${p.gate.charAt(0) + p.gate.slice(1).toLowerCase()}`, 'sub', narrow ? 'start' : 'end');
    if (cid !== 'C-L-ALL-RESPONDENTS') { el('circle', {cx: x(a0.a), cy: yy, r: 5, fill: 'none', stroke: 'var(--muted)', 'stroke-width': 1.5}, g); el('circle', {cx: x(a0.b), cy: yy, r: 5, fill: 'none', stroke: 'var(--muted)', 'stroke-width': 1.5}, g); }
    el('line', {x1: x(c.a), x2: x(c.b), y1: yy, y2: yy, stroke: 'var(--fg2)', 'stroke-width': 2}, g);
    el('circle', {cx: x(c.a), cy: yy, r: 7, fill: 'var(--valued)', stroke: 'var(--ring)', 'stroke-width': 2}, g);
    el('circle', {cx: x(c.b), cy: yy, r: 7, fill: 'var(--received)', stroke: 'var(--ring)', 'stroke-width': 2}, g);
    text(g, Math.max(x(c.a), x(c.b)) + 12, yy + 4, fmtGap(c.gap), 'val');
    const hit = el('rect', {x: 0, y: y0, width: W, height: rh, class: 'hit', tabindex: 0, 'aria-label': `${p.concept}: ${fmtPct(c.a)} and ${fmtPct(c.b)}`}, svg);
    const html = `<b>${esc(p.concept)}</b><br>${esc(p.a_label)}: <b>${fmtPct(c.a)}</b> (base ${c.a_base})<br>${esc(p.b_label)}: <b>${fmtPct(c.b)}</b> (base ${c.b_base})<br>Gap ${fmtGap(c.gap)} · ${esc(c.label)}` +
      (cid !== 'C-L-ALL-RESPONDENTS' ? `<br>All respondents: gap ${fmtGap(a0.gap)}` : '');
    hit.addEventListener('mousemove', e => showTip(e, html)); hit.addEventListener('mouseleave', hideTip);
    hit.addEventListener('focus', () => { const b = hit.getBoundingClientRect(); showTip({clientX: b.left + b.width / 2, clientY: b.top + b.height}, html); }); hit.addEventListener('blur', hideTip);
    y0 += rh;
  });
}
sel.addEventListener('change', drawV1);

// ---------------- reader (verbatims)
function reader(host, title, groupsDef){
  host.hidden = false;
  let cur = groupsDef.find(g => g.ids.length) ? groupsDef.find(g => g.ids.length).key : groupsDef[0].key;
  function render(){
    const g = groupsDef.find(z => z.key === cur);
    host.innerHTML = `<div class="reader-head"><h3>${esc(title)}</h3><div class="tabs">` +
      groupsDef.map(z => `<button type="button" aria-pressed="${z.key === cur}" data-k="${z.key}">${esc(z.label)} <span class="n">${z.ids.length}</span></button>`).join('') +
      `</div></div><ul class="quotes">` + (g.ids.length ? g.ids.map(id => { const a = D.answers[id];
        const side = ['Q22','Q24'].includes(a.item) ? 'best' : ['Q23','Q25'].includes(a.item) ? 'worst' : '';
        return `<li class="${side}">${esc(a.text)}<div class="meta">${esc(a.item)}${QNAME[a.item] ? ' · ' + esc(QNAME[a.item]) : ''} · respondent ${esc(a.respid)} · ${esc(a.id)}</div></li>`; }).join('')
        : '<li>No answers in this group.</li>') + '</ul>';
    host.querySelectorAll('button[data-k]').forEach(b => b.addEventListener('click', () => { cur = b.dataset.k; render(); }));
  }
  render();
}
const side = id => { const it = D.answers[id].item; return ['Q22','Q24'].includes(it) ? 'best' : ['Q23','Q25'].includes(it) ? 'worst' : it === 'Q21' ? 'q21' : 'other'; };

// ---------------- V3 silent gap
let v3sel = null;
function drawV3(){
  const host = $('#v3chart'); host.innerHTML = '';
  const W = Math.max(320, host.clientWidth - 32), H = Math.round(Math.min(460, Math.max(320, W * 0.55)));
  const L = 52, R = W - 20, T = 20, B = H - 48;
  const pts = D.v3.points, ymax = Math.ceil(Math.max(...pts.map(p => p.answers)) / 50) * 50;
  const x = v => L + (v + 0.6) / 1.2 * (R - L), y = v => B - v / ymax * (B - T);
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Structured gap against number of written answers'}, host);
  for (let v = 0; v <= ymax; v += 50) { el('line', {x1: L, x2: R, y1: y(v), y2: y(v), class: 'gr'}, svg); text(svg, L - 8, y(v) + 4, v, 'sub', 'end'); }
  for (const v of [-0.6, -0.3, 0, 0.3, 0.6]) { el('line', {x1: x(v), x2: x(v), y1: T, y2: B, class: v === 0 ? 'ax' : 'gr'}, svg); text(svg, x(v), B + 16, v === 0 ? '0' : fmtGap(v), 'sub', 'middle'); }
  const nar = W < 560;
  text(svg, (L + R) / 2, B + 36, nar ? 'gap: received − valued' : 'gap between what is received and what is valued (survey, all respondents)', 'sub', 'middle');
  text(svg, R - 4, T + 12, '↑ more written answers raise it', 'sub', 'end');
  if (!nar) { text(svg, x(-0.6) + 4, B - 8, '← customers get less than they value', 'sub');
    text(svg, x(0.6) - 4, B - 8, 'more than they value →', 'sub', 'end'); }
  const placed = [];
  pts.slice().sort((a, b) => a.answers - b.answers).forEach(p => {
    const cx = x(p.gap), cy = y(p.answers), key = p.pair === 'P07' || p.pair === 'P05';
    const g = el('g', {class: v3sel === p.pair ? 'sel' : ''}, svg);
    el('circle', {cx, cy, r: key ? 9 : 7, fill: key ? 'var(--received)' : 'var(--valued)', stroke: v3sel === p.pair ? 'var(--fg)' : 'var(--ring)', 'stroke-width': 2}, g);
    // Fixed sides for the crowded business-knowledge cluster; others sit above their point.
    const SIDE = {C01: 'end', P01: 'end', P03: 'end', C02: 'start'};
    let ly = cy - 13, anchor = 'middle', lx = cx;
    if (SIDE[p.pair]) { ly = cy + 4; anchor = SIDE[p.pair]; lx = cx + (anchor === 'end' ? -13 : 13); }
    placed.push({x: lx, y: ly});
    text(g, lx, ly, key ? `${p.concept}` : p.pair, key ? 'lab' : 'sub', anchor);
    const hit = el('circle', {cx, cy, r: 16, class: 'hit', tabindex: 0, role: 'button', 'aria-label': `${p.concept}: gap ${fmtGap(p.gap)}, ${p.answers} answers`}, svg);
    const html = `<b>${esc(p.pair)} · ${esc(p.concept)}</b><br>Gap ${fmtGap(p.gap)} · ${p.answers} written answers<br>In best accounts (+) ${p.best_pos} · in worst accounts (−) ${p.worst_neg} · as a criterion ${p.q21}<br>Codes: ${esc(p.code_labels.join('; '))}`;
    hit.addEventListener('mousemove', e => showTip(e, html)); hit.addEventListener('mouseleave', hideTip);
    const open = () => { v3sel = p.pair; hideTip(); drawV3();
      reader($('#v3reader'), `${p.pair} · ${p.concept} — answers carrying ${p.code_labels.join(', ')}`, [
        {key: 'best', label: 'Best accounts', ids: p.answer_ids.filter(i => side(i) === 'best')},
        {key: 'worst', label: 'Worst accounts', ids: p.answer_ids.filter(i => side(i) === 'worst')},
        {key: 'q21', label: 'As a criterion (Q21)', ids: p.answer_ids.filter(i => side(i) === 'q21')},
        {key: 'other', label: 'Other answers', ids: p.answer_ids.filter(i => side(i) === 'other')}]); };
    hit.addEventListener('click', open); hit.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
  });
}

// ---------------- V4 wins / loses
let v4sel = null;
function drawV4(){
  const host = $('#v4chart'); host.innerHTML = '';
  const rows = D.v4.behaviours.filter(b => b.class !== 'too few').sort((a, b) => b.experiential - a.experiential || a.code.localeCompare(b.code));
  const W = Math.max(320, host.clientWidth - 32), narrow = W < 620;
  const labW = narrow ? 0 : 250, rh = narrow ? 40 : 24, top = 10;
  const C = labW + (W - labW) / 2, half = (W - labW) / 2 - 34;
  const mx = Math.max(...rows.map(r => Math.max(r.effective, r.ineffective)));
  const sc = v => v / mx * half;
  const H = top + rh * rows.length + 8;
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Behaviours by mentions in worst and best accounts'}, host);
  el('line', {x1: C, x2: C, y1: top - 4, y2: H - 4, class: 'ax'}, svg);
  rows.forEach((r, i) => {
    const y = top + rh * i, by = narrow ? y + 20 : y + 4, bh = narrow ? 14 : 16;
    const g = el('g', {class: v4sel === r.code ? 'sel' : ''}, svg);
    el('rect', {x: 0, y, width: W, height: rh, class: 'row-bg'}, g);
    text(g, narrow ? 4 : 0, narrow ? y + 13 : y + 16, r.label, 'lab');
    text(g, narrow ? W - 4 : 196, narrow ? y + 13 : y + 16, r.class, 'sub', narrow ? 'end' : 'start');
    if (r.ineffective) el('rect', {x: C - sc(r.ineffective), y: by, width: sc(r.ineffective), height: bh, rx: 3, fill: 'var(--lose)'}, g);
    if (r.effective) el('rect', {x: C, y: by, width: sc(r.effective), height: bh, rx: 3, fill: 'var(--win)'}, g);
    text(g, C - sc(r.ineffective) - 6, by + bh - 3, r.ineffective, 'val', 'end');
    text(g, C + sc(r.effective) + 6, by + bh - 3, r.effective, 'val');
    const hit = el('rect', {x: 0, y, width: W, height: rh, class: 'hit', tabindex: 0, role: 'button', 'aria-label': `${r.label}: ${r.ineffective} ineffective, ${r.effective} effective, ${r.class}`}, svg);
    const html = `<b>${esc(r.label)}</b> · ${esc(r.class)}<br>${esc(r.definition)}<br>Ineffective in worst accounts: <b>${r.ineffective}</b> · effective in best: <b>${r.effective}</b><br>Named as a criterion (Q21): ${r.q21}`;
    hit.addEventListener('mousemove', e => showTip(e, html)); hit.addEventListener('mouseleave', hideTip);
    const open = () => { v4sel = r.code; hideTip(); drawV4();
      reader($('#v4reader'), `${r.label} — ${r.class}`, [
        {key: 'worst', label: 'Ineffective, worst accounts', ids: r.worst_ids}, {key: 'best', label: 'Effective, best accounts', ids: r.best_ids}]); };
    hit.addEventListener('click', open); hit.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
  });
  const few = D.v4.behaviours.filter(b => b.class === 'too few').map(b => b.label);
  const note = document.createElement('p'); note.className = 'legend'; note.textContent = `Fewer than 10 mentions, left out: ${few.join(', ')}.`; host.appendChild(note);
}

// ---------------- V5 table
(function(){
  const rows = D.v5.rows;
  const gaps = rows.filter(r => r.gap).length;
  let h = `<table><thead><tr><th>Gate</th><th>Concept</th><th>Vendor's word</th><th>Customer's word in the survey</th><th>Decision-makers' own words</th><th class="num">Answers</th></tr></thead><tbody>`;
  for (const r of rows) {
    const cust = r.gap ? `<td class="gap">No word · ${esc(r.gap)}</td>` : `<td>${esc(r.customer_term.split(' | ')[0])}</td>`;
    h += `<tr class="${r.gap ? 'gaprow' : ''}"><td>${esc(r.gate)}</td><td>${esc(r.concept)}</td><td>${esc(r.vendor_term)}</td>${cust}<td>${esc(r.top_words.slice(0, 5).join(', ') || '—')}</td><td class="num">${r.answers}</td></tr>`;
  }
  $('#v5table').innerHTML = h + `</tbody></table>`;
  const q = document.querySelector('[data-q="v5"]'); q.textContent += ` ${gaps} of ${rows.length} concepts have no customer-side word.`;
})();

$('#foot').innerHTML = `<div>Built from committed data by scripts in the project repository: <a href="${D.repo}" target="_blank" rel="noopener">${esc(D.repo.replace('https://', ''))}</a> (<code>06_visualization/</code>).</div>` +
  `<div>Every number on this page is computed from the embedded data files; none is typed by hand. Respondents appear by anonymous ID only, with no level or stakeholder type.</div>`;

function drawAll(){ drawV1(); drawV3(); drawV4(); }
drawAll();
let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(drawAll, 120); });
})();
</script>
"""


if __name__ == "__main__":
    sys.exit(main())
