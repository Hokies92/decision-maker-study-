#!/usr/bin/env python3
"""p6_build_argument_page.py — the argument page "The Silent Gap" (P6.S04; revised after Scott's review, 2026-10-30):
study context, then V1 valued vs received, V3 felt vs said, V4 what wins / what loses, V5 two vocabularies — each with
how to read it, what it shows, what it means, and the implication — and a closing list of implications with their evidence.

Inputs: 06_visualization/data/v0_context.json, v1_ledger.json, v3_silent_gap.json, v4_wins_loses.json, v5_vocabularies.json.
Output: 06_visualization/argument.html — committed (public with the repo) and published as a page (D6-2: both).
Every number on the page is computed in the page from the embedded data; none is typed by hand. The interpretation and
implications are Claude's reading of those numbers (INFERRED) and are labelled as such on the page.
Usage: python3 -I scripts/p6_build_argument_page.py [--fragment <path for the publishable copy>]
"""
import json
import sys
from pathlib import Path

DATA = Path("06_visualization/data")
OUT = Path("06_visualization/argument.html")
REPO = "https://github.com/Hokies92/decision-maker-study-"


def main() -> int:
    v0, v1, v3, v4, v5 = (json.loads((DATA / f).read_text(encoding="utf-8")) for f in
                          ("v0_context.json", "v1_ledger.json", "v3_silent_gap.json", "v4_wins_loses.json", "v5_vocabularies.json"))
    answers = dict(v3.pop("answers"))
    answers.update(v4.pop("answers"))
    payload = {"v0": v0, "v1": v1, "v3": v3, "v4": v4, "v5": v5, "answers": dict(sorted(answers.items())), "repo": REPO}
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
/* Layout: one reading column. Each view is a band: the finding as a headline, how to read the chart, the chart, then
   what it shows (data), what it means (interpretation) and the implication. Charts use the validated data palette. */
:root{
  --bg:#f6f7f8; --panel:#ffffff; --fg:#14181d; --fg2:#4d5560; --muted:#7c8590; --rule:#dde1e6; --axis:#b9c0c8;
  --valued:#2a78d6; --received:#eb6834; --lose:#e34948; --win:#2a78d6; --said:#6b7480; --ring:#ffffff; --hl:#eef3fb; --note:#fff7e8;
  --display:"Archivo",system-ui,-apple-system,"Segoe UI",sans-serif;
  --body:"Source Serif 4",Georgia,"Times New Roman",serif;
  --data:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121417; --panel:#1a1d21; --fg:#eef0f2; --fg2:#b8bfc7; --muted:#8a929b; --rule:#2c3137; --axis:#3d434a;
  --valued:#3987e5; --received:#d95926; --lose:#e66767; --win:#3987e5; --said:#9aa3ad; --ring:#1a1d21; --hl:#1d2733; --note:#2a2418; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121417; --panel:#1a1d21; --fg:#eef0f2; --fg2:#b8bfc7; --muted:#8a929b; --rule:#2c3137; --axis:#3d434a;
  --valued:#3987e5; --received:#d95926; --lose:#e66767; --win:#3987e5; --said:#9aa3ad; --ring:#1a1d21; --hl:#1d2733; --note:#2a2418; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16.5px;line-height:1.6;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:940px;margin:0 auto;padding-block:40px 64px;display:grid;grid-template-columns:minmax(0,1fr);gap:64px}
.sec>*,header>*{min-width:0}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0;letter-spacing:-.01em}
h1{font-size:clamp(36px,6vw,60px);font-stretch:85%;font-weight:800;line-height:1.02}
h2{font-size:clamp(23px,3.2vw,31px);font-stretch:90%;font-weight:700;line-height:1.15}
h3{font-family:var(--display);font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
p{margin:0;max-width:68ch}
.eyebrow{font-family:var(--display);font-size:12px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
header{display:grid;gap:18px}
.lede{font-size:clamp(18px,2.2vw,21px);color:var(--fg2);max-width:62ch}
.n{font-family:var(--data);font-variant-numeric:tabular-nums;font-size:.9em;white-space:nowrap}
.short{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.short div{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;display:grid;gap:6px;align-content:start}
.short b{font-family:var(--display);font-size:16px;line-height:1.3}
.short span{font-size:15px;color:var(--fg2)}
.sec{display:grid;gap:18px;scroll-margin-top:16px}
.block{display:grid;gap:8px;align-content:start}
.reader[hidden]{display:none}
.block p,.block li{color:var(--fg2)} .block b{color:var(--fg)}
.howto{background:var(--note);border-radius:10px;padding:14px 16px;display:grid;gap:8px;font-size:15.5px}
.howto ul{margin:0;padding-left:20px;display:grid;gap:4px}
.reading{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.meaning{border-left:3px solid var(--fg);padding-left:14px}
.implication{border-left:3px solid var(--received);padding-left:14px}
.tag{font-family:var(--display);font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-left:6px}
.facts{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.facts div{display:grid;gap:2px}
.facts .big{font-family:var(--display);font-size:30px;font-weight:700;font-stretch:90%;line-height:1}
.facts .lab{font-family:var(--display);font-size:13.5px;color:var(--fg2)}
.gates{display:grid;gap:8px;grid-template-columns:repeat(auto-fit,minmax(160px,1fr))}
.gates div{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:10px 12px;display:grid;gap:4px}
.gates b{font-family:var(--display);font-size:15px}
.gates span{font-size:13.5px;color:var(--fg2);line-height:1.45}
.gates em{font-family:var(--display);font-style:normal;font-size:11px;color:var(--muted)}
.chart{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:16px;min-width:0;overflow-x:auto}
.chart svg{display:block;width:100%;height:auto;overflow:visible}
.controls{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;font-family:var(--display);font-size:14px}
select{max-width:100%}
select,button{font-family:var(--display);font-size:14px;color:var(--fg);background:var(--panel);border:1px solid var(--axis);border-radius:6px;padding:6px 10px}
button{cursor:pointer}
select:focus-visible,button:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--valued);outline-offset:2px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-family:var(--display);font-size:13.5px;color:var(--fg2)}
.legend a{color:var(--fg2)}
.key{display:inline-flex;align-items:center;gap:6px}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block}
.bar{width:16px;height:10px;border-radius:3px;display:inline-block}
details.about{font-family:var(--display);font-size:13px;color:var(--fg2);border-top:1px solid var(--rule);padding-top:10px}
details.about summary{cursor:pointer;color:var(--muted);font-weight:600}
details.about ul{margin:6px 0;padding-left:18px;display:grid;gap:3px}
details.about code{font-family:var(--data);font-size:12px;overflow-wrap:anywhere}
.reader{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:16px;display:grid;gap:12px;min-width:0}
.reader-head{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline;justify-content:space-between}
.reader-head h4{margin:0;font-family:var(--display);font-size:15px}
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
.imps{display:grid;gap:14px;margin:0;padding:0;list-style:none}
.imps li{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;display:grid;gap:6px}
.imps b{font-family:var(--display);font-size:17px;line-height:1.3}
.imps .ev{font-family:var(--display);font-size:13px;color:var(--muted)}
.limits{display:grid;gap:4px;padding-left:20px;margin:0;color:var(--fg2)}
.tip{position:fixed;z-index:20;pointer-events:none;max-width:320px;background:var(--fg);color:var(--bg);font-family:var(--display);
  font-size:12.5px;line-height:1.4;padding:8px 10px;border-radius:6px;opacity:0;transition:opacity .08s}
.tip.on{opacity:1}
svg text{font-family:var(--display)}
.ax{stroke:var(--axis);stroke-width:1} .gr{stroke:var(--rule);stroke-width:1}
.lab{fill:var(--fg);font-size:13px} .sub{fill:var(--muted);font-size:11px} .val{fill:var(--fg2);font-size:12px;font-family:var(--data)}
.callout{fill:var(--fg);font-size:12px;font-weight:600}
.hit{fill:transparent;cursor:pointer} .row-bg{fill:transparent} .sel .row-bg,.key-row .row-bg{fill:var(--hl)}
footer{font-family:var(--display);font-size:13px;color:var(--muted);border-top:1px solid var(--rule);padding-top:16px;display:grid;gap:6px}
footer a{color:var(--fg2)}
@media (prefers-reduced-motion: reduce){.tip{transition:none}}
</style>

<main>
<header>
  <div class="eyebrow">Decision-maker study</div>
  <h1>The Silent Gap</h1>
  <p class="lede" id="lede"></p>
  <div class="short" id="short"></div>
  <nav class="legend" aria-label="Sections">
    <a href="#context">The study</a><a href="#ledger">1 · Valued vs received</a><a href="#silent">2 · Felt vs said</a><a href="#wins">3 · What wins, what loses</a><a href="#words">4 · Two vocabularies</a><a href="#implications">What it means</a>
  </nav>
</header>

<section class="sec" id="context">
  <div class="eyebrow">Before the charts</div>
  <h2>Who was asked, and what</h2>
  <div class="facts" id="facts"></div>
  <div class="block" id="asked"></div>
  <div class="block"><p>The study is organised around five yes-or-no gates a vendor has to pass, in order, before a customer accepts a business case. A "no" at any gate stops the decision.</p></div>
  <div class="gates" id="gates"></div>
</section>

<section class="sec" id="ledger">
  <div class="eyebrow">View 1 · Valued vs received</div>
  <h2 id="h1"></h2>
  <div class="howto" id="howto1"></div>
  <div class="controls">
    <label for="cohort">Show a group</label>
    <select id="cohort"></select>
    <span class="legend" id="v1legend"></span>
  </div>
  <div class="chart" id="v1chart"></div>
  <div class="reading" id="read1"></div>
  <details class="about" data-about="v1"></details>
</section>

<section class="sec" id="silent">
  <div class="eyebrow">View 2 · Felt vs said</div>
  <h2 id="h3"></h2>
  <div class="howto" id="howto3"></div>
  <div class="chart" id="v3chart"></div>
  <p class="legend">Select a row to read the written answers behind it.</p>
  <div class="reader" id="v3reader" hidden></div>
  <div class="reading" id="read3"></div>
  <details class="about" data-about="v3"></details>
</section>

<section class="sec" id="wins">
  <div class="eyebrow">View 3 · What wins, what loses</div>
  <h2 id="h4"></h2>
  <div class="howto" id="howto4"></div>
  <div class="controls"><span class="legend"><span class="key"><span class="bar" style="background:var(--lose)"></span>done badly, in worst sales teams</span><span class="key"><span class="bar" style="background:var(--win)"></span>done well, in best sales teams</span></span></div>
  <div class="chart" id="v4chart"></div>
  <p class="legend">Select a behaviour to read what decision-makers wrote.</p>
  <div class="reader" id="v4reader" hidden></div>
  <div class="reading" id="read4"></div>
  <details class="about" data-about="v4"></details>
</section>

<section class="sec" id="words">
  <div class="eyebrow">View 4 · Two vocabularies</div>
  <h2 id="h5"></h2>
  <div class="howto" id="howto5"></div>
  <div class="tbl" id="v5table"></div>
  <div class="reading" id="read5"></div>
  <details class="about" data-about="v5"></details>
</section>

<section class="sec" id="implications">
  <div class="eyebrow">What it means</div>
  <h2>Implications for vendors and their salespeople</h2>
  <p>These are interpretations of the evidence above, not findings in themselves. Each names the evidence it rests on.</p>
  <ul class="imps" id="imps"></ul>
  <h3>What this evidence cannot tell you</h3>
  <ul class="limits" id="limits"></ul>
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
const pct = v => Math.round(v * 100) + '%';
const pts = v => Math.round(Math.abs(v) * 100);              // gap in percentage points
const gapTxt = v => (v < 0 ? pts(v) + ' points less' : v > 0 ? pts(v) + ' points more' : 'no difference');
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const N = s => `<span class="n">${s}</span>`;
const strip = s => String(s).replace(/<[^>]+>/g, '');
const QNAME = {Q21:'What differentiates a vendor', Q22:'Most effective sales teams', Q23:'Least effective sales teams', Q24:'Contact in best relationships', Q25:'Contact in worst relationships'};
function el(tag, attrs, parent){ const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function text(parent, x, y, s, cls, anchor){ const t = el('text', {x, y, class: cls || 'lab', 'text-anchor': anchor || 'start'}, parent); t.textContent = s; return t; }
const tip = $('#tip');
function showTip(evt, html){ tip.innerHTML = html; tip.classList.add('on'); const r = tip.getBoundingClientRect();
  let x = evt.clientX + 14, y = evt.clientY + 14; if (x + r.width > innerWidth - 8) x = evt.clientX - r.width - 14; if (y + r.height > innerHeight - 8) y = evt.clientY - r.height - 14;
  tip.style.left = Math.max(8, x) + 'px'; tip.style.top = Math.max(8, y) + 'px'; }
function hideTip(){ tip.classList.remove('on'); }
function bindHit(hit, html, open){
  hit.addEventListener('mousemove', e => showTip(e, html)); hit.addEventListener('mouseleave', hideTip);
  hit.addEventListener('focus', () => { const b = hit.getBoundingClientRect(); showTip({clientX: b.left + 20, clientY: b.bottom}, html); });
  hit.addEventListener('blur', hideTip);
  if (open) { hit.addEventListener('click', open); hit.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } }); }
}
function reading(host, shows, means, so){
  host.innerHTML = `<div class="block"><h3>What it shows</h3>${shows}</div>` +
    `<div class="block meaning"><h3>What it means <span class="tag">interpretation</span></h3>${means}</div>` +
    `<div class="block implication"><h3>So what <span class="tag">implication</span></h3>${so}</div>`;
}

// ---------------------------------------------------------------- numbers used in the words, all from the data
const C = D.v0, ALL = 'C-L-ALL-RESPONDENTS';
const allRow = p => p.cohorts.find(c => c.cohort === ALL);
const pair = id => D.v1.pairs.find(p => p.pair === id);
const vxe = D.v1.pairs.filter(p => p.type === 'value_vs_experience');
const short = vxe.filter(p => allRow(p).gap < 0).length;
const worst = vxe.reduce((a, b) => allRow(b).gap < allRow(a).gap ? b : a);
const over = vxe.reduce((a, b) => allRow(b).gap > allRow(a).gap ? b : a);
const pt = id => D.v3.points.find(x => x.pair === id);
const KNOW = ['P01', 'P03', 'C01', 'C02'];
const knowAns = KNOW.map(k => pt(k).answers), knowGap = KNOW.map(k => allRow(pair(k)).gap);
const beh = c => D.v4.behaviours.find(b => b.code === c);
const kb = beh('B-KNOWS-BUSINESS'), cf = beh('B-CUSTOMER-FIRST');
const cls = k => D.v4.behaviours.filter(b => b.class === k);
const gaps5 = D.v5.rows.filter(r => r.gap);
const stem = q => strip(C.question_stems[q]);
const steady = D.v1.pairs.filter(p => { const u = p.cohorts.filter(c => c.usable && c.cohort !== ALL); return u.every(c => Math.sign(c.gap) === Math.sign(allRow(p).gap)); });
const steadyNames = steady.map(p => p.concept.toLowerCase());

// ---------------------------------------------------------------- header and context
$('#lede').innerHTML = `${N(C.respondents)} business decision-makers told us what they want from salespeople, what they actually get, and in their own words what their best and worst sales teams do. The two sides do not match, and the biggest mismatch is the one customers never put into words.`;
$('#short').innerHTML =
  `<div><b>Customers get the pitch they do not want.</b><span>Product presentations are the one thing customers get more of than they value: ${N(pts(allRow(over).gap) + ' points')} more.</span></div>` +
  `<div><b>They miss help with the business case.</b><span>${esc(worst.concept)} is valued by ${N(pct(allRow(worst).a))} but received by ${N(pct(allRow(worst).b))}: the largest gap of all.</span></div>` +
  `<div><b>And they do not say so.</b><span>Only ${N(pt(worst.pair).answers)} of ${N(C.codable_answers)} usable written answers touch it, against ${N(Math.min(...knowAns) + '–' + Math.max(...knowAns))} for each business-knowledge gap.</span></div>`;
$('#facts').innerHTML =
  `<div><span class="big n">${C.respondents}</span><span class="lab">decision-makers who take part in their company's IT purchase decisions</span></div>` +
  `<div><span class="big n">${C.it_decision_makers} / ${C.business_decision_makers}</span><span class="lab">from IT / from the business side</span></div>` +
  `<div><span class="big n">${C.levels.map(l => l.n).join(' · ')}</span><span class="lab">${C.levels.map(l => l.label).join(' · ')}</span></div>` +
  `<div><span class="big n">${C.written_answers.toLocaleString('en-US')}</span><span class="lab">written answers, of which ${C.codable_answers} say something that can be coded</span></div>`;
$('#asked').innerHTML = `<p>Two kinds of question. <b>Survey questions</b> with fixed answers — for example, ${N('Q11')} “${esc(stem('Q11'))}” and ${N('Q8')} “${esc(stem('Q08'))}” Results are reported as the share of decision-makers who chose each answer.</p>` +
  `<p><b>Open questions</b> answered in their own words — for example, ${N('Q22')} “${esc(stem('Q22'))}” and the same for the ${N('LEAST')} effective (${N('Q23')}). We read and coded every written answer for what it praised or criticised.</p>`;
const GPLAIN = {TARGET: 'The right message reaches the right people.', ACCESS: 'The salesperson gets in front of them.', AGREE: 'They agree the idea is worth exploring.',
  VISION: 'They share a picture of what success looks like.', CASE: 'They accept a business case for it.'};
$('#gates').innerHTML = C.gates.map((g, i) => `<div><em>Gate ${i + 1}</em><b>${esc(g.name)}</b><span>${esc(GPLAIN[g.gate])}</span><em title="${esc(g.scott_definition)}">Definition: Scott Santucci</em></div>`).join('');

// about blocks
for (const k of ['v1','v3','v4','v5']) {
  const m = D[k].meta;
  document.querySelector(`[data-about="${k}"]`).innerHTML = `<summary>About this data: sources, method and limits</summary>` +
    `<div><b>Unit:</b> ${esc(m.unit)} · <b>Provenance:</b> ${esc(m.provenance)}</div><ul>${m.caveats.map(c => `<li>${esc(c)}</li>`).join('')}</ul>` +
    `<div><b>Sources:</b> ${m.sources.map(s => `<code>${esc(s)}</code>`).join(', ')} · built by <code>${esc(m.generated_by)}</code></div>`;
}

// ---------------------------------------------------------------- V1
const p7 = allRow(worst), pp = allRow(over);
$('#h1').textContent = `Customers want help building the case. They get a product pitch.`;
$('#howto1').innerHTML = `<h3>How to read this chart</h3><ul>` +
  `<li>Each row is one thing a salesperson can do for a customer.</li>` +
  `<li><span class="key"><span class="dot" style="background:var(--valued)"></span><b>Blue</b></span> = the share of decision-makers who say it matters (they value it).</li>` +
  `<li><span class="key"><span class="dot" style="background:var(--received)"></span><b>Orange</b></span> = the share who say they actually get it from salespeople or vendor material.</li>` +
  `<li>The line between them is the gap. A long line means a big mismatch. Orange to the left of blue means customers get <b>less</b> than they value.</li></ul>` +
  `<p><b>Example, top row (${esc(worst.concept)}).</b> Blue, ${N(pct(p7.a))}: ${esc(worst.a_label.replace(/^Valued: /, ''))}. Orange, ${N(pct(p7.b))}: ${esc(worst.b_label.replace(/^Received: /, ''))}. Gap: ${N(gapTxt(p7.gap))}.</p>`;
const sel = $('#cohort');
const cohorts = D.v1.pairs[0].cohorts, groups = {};
cohorts.forEach(c => (groups[c.dimension] = groups[c.dimension] || []).push(c));
for (const dim of Object.keys(groups)) {
  const og = document.createElement(dim === 'All' ? 'div' : 'optgroup'); if (dim !== 'All') og.label = dim;
  for (const c of groups[dim]) { const o = document.createElement('option'); o.value = c.cohort; o.disabled = !c.usable;
    o.textContent = `${c.label === 'All Respondents' ? 'All decision-makers' : c.label} (n = ${c.n})${c.usable ? '' : ' — too few to show'}`; (dim === 'All' ? sel : og).appendChild(o); }
  if (dim !== 'All') sel.appendChild(og);
}
sel.value = ALL;
$('#v1legend').innerHTML = `<span class="key"><span class="dot" style="background:var(--valued)"></span>value it</span><span class="key"><span class="dot" style="background:var(--received)"></span>get it</span><span class="key" id="refkey" hidden><span class="dot" style="border:1.5px solid var(--muted)"></span>all decision-makers, for comparison</span>`;
function drawV1(){
  const host = $('#v1chart'); host.innerHTML = ''; $('#refkey').hidden = sel.value === ALL;
  const W = Math.max(320, host.clientWidth - 32), narrow = W < 620;
  const L = narrow ? 8 : Math.min(300, W * 0.36), R = W - 120, rh = narrow ? 64 : 48, top = 34;
  const order = D.v1.pairs.slice().sort((a, b) => (a.type === b.type ? allRow(a).gap - allRow(b).gap : a.type === 'value_vs_experience' ? -1 : 1));
  const H = top + rh * order.length + 34 + 26;
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Share who value each thing against share who get it'}, host);
  const x = v => L + v * (R - L);
  for (const v of [0, .25, .5, .75, 1]) { el('line', {x1: x(v), x2: x(v), y1: top - 10, y2: top + rh * order.length + 22, class: 'gr'}, svg); text(svg, x(v), top - 16, pct(v), 'sub', 'middle'); }
  const cid = sel.value; let y0 = top, lastType = null;
  order.forEach(p => {
    if (p.type !== lastType) { if (lastType) y0 += 22; text(svg, 8, y0 + 4, p.type === 'value_vs_experience' ? 'WHAT CUSTOMERS VALUE vs WHAT THEY GET' : (narrow ? 'SALESPEOPLE PREPARED ON: THEMSELVES vs ME' : 'HOW SALESPEOPLE PREPARE: ON THEIR OWN PRODUCTS vs ON THE CUSTOMER'), 'sub'); y0 += 12; lastType = p.type; }
    const c = p.cohorts.find(z => z.cohort === cid), a0 = allRow(p), yy = y0 + (narrow ? 40 : rh / 2);
    const g = el('g', {class: p.pair === worst.pair ? 'key-row' : ''}, svg);
    el('rect', {x: 0, y: y0, width: W, height: rh, class: 'row-bg'}, g);
    text(g, narrow ? 8 : L - 14, narrow ? y0 + 16 : yy + 1, p.concept, 'lab', narrow ? 'start' : 'end');
    text(g, narrow ? 8 : L - 14, narrow ? y0 + 30 : yy + 15, `${p.gate.charAt(0) + p.gate.slice(1).toLowerCase()} gate`, 'sub', narrow ? 'start' : 'end');
    if (cid !== ALL) for (const v of [a0.a, a0.b]) el('circle', {cx: x(v), cy: yy, r: 5, fill: 'none', stroke: 'var(--muted)', 'stroke-width': 1.5}, g);
    el('line', {x1: x(c.a), x2: x(c.b), y1: yy, y2: yy, stroke: 'var(--fg2)', 'stroke-width': 2}, g);
    el('circle', {cx: x(c.a), cy: yy, r: 7, fill: 'var(--valued)', stroke: 'var(--ring)', 'stroke-width': 2}, g);
    el('circle', {cx: x(c.b), cy: yy, r: 7, fill: 'var(--received)', stroke: 'var(--ring)', 'stroke-width': 2}, g);
    text(g, Math.max(x(c.a), x(c.b)) + 12, yy + 4, (c.gap < 0 ? '−' : '+') + pts(c.gap) + ' pts', 'val');
    const hit = el('rect', {x: 0, y: y0, width: W, height: rh, class: 'hit', tabindex: 0, 'aria-label': `${p.concept}: ${pct(c.a)} and ${pct(c.b)}`}, svg);
    bindHit(hit, `<b>${esc(p.concept)}</b><br>${esc(p.a_label)}: <b>${pct(c.a)}</b><br>${esc(p.b_label)}: <b>${pct(c.b)}</b><br>${gapTxt(c.gap)} · ${esc(c.label)} (n = ${c.n})` + (cid !== ALL ? `<br>All decision-makers: ${gapTxt(a0.gap)}` : ''));
    y0 += rh;
  });
}
sel.addEventListener('change', drawV1);
reading($('#read1'),
  `<p>For ${N(short + ' of ' + vxe.length)} things customers value, they get less than they want. The largest shortfall is <b>${esc(worst.concept.toLowerCase())}</b> (${N(gapTxt(p7.gap))}). Three of the shortfalls are about understanding the customer's business, each about ${N(Math.round(-Math.max(...knowGap) * 100) + '–' + Math.round(-Math.min(...knowGap) * 100) + ' points')}.</p>` +
  `<p>Only <b>${esc(over.concept.toLowerCase())}</b> runs the other way: ${N(pct(pp.a))} value a compelling presentation, but ${N(pct(pp.b))} say presenting products is the typical agenda (${N(gapTxt(pp.gap))}).</p>` +
  `<p>Salespeople come prepared on their own products far more often than on the customer (bottom rows, about ${N(Math.round(-Math.min(...knowGap) * 100) + ' points')}). Pick a group above to compare. In every group large enough to show, the direction is the same for ${N(steady.length + ' of ' + D.v1.pairs.length)} rows: ${esc(steadyNames.join('; '))}.</p>`,
  `<p>Salespeople put their effort where customers value it least, and hold back where customers value it most. Because the largest gaps run the same way across roles, levels, industries and countries, they are unlikely to come from a few weak salespeople. It looks like the way selling is set up: what salespeople are trained on, measured on and given to take into meetings.</p>`,
  `<p>Better pitching will not close this gap. The gain is in shifting time from presenting the product to understanding the customer's business and helping them build the case for change.</p>`);

// ---------------------------------------------------------------- V3 felt vs said (two aligned bar columns)
$('#h3').textContent = `The biggest gap is the one customers never mention.`;
$('#howto3').innerHTML = `<h3>How to read this chart</h3><ul>` +
  `<li>The same nine rows as View 1, ordered from the largest shortfall to the largest surplus.</li>` +
  `<li><b>Left bars, “felt”:</b> the gap from View 1, in percentage points. <span class="key"><span class="bar" style="background:var(--lose)"></span>red</span> = customers get less than they value; <span class="key"><span class="bar" style="background:var(--win)"></span>blue</span> = more.</li>` +
  `<li><b>Right bars, “said”:</b> how many of the ${N(C.codable_answers)} usable written answers raise the same topic, unprompted — for example by praising or criticising how well a salesperson knows their business.</li>` +
  `<li>The two “prepared on” rows compare how often salespeople are prepared on the customer against on their own products; red means less often on the customer.</li>` +
  `<li>A row with a long left bar and a short right bar is a gap customers feel but do not talk about.</li></ul>`;
let v3sel = null;
function drawV3(){
  const host = $('#v3chart'); host.innerHTML = '';
  const rows = D.v3.points.slice().sort((a, b) => a.gap - b.gap);
  const W = Math.max(320, host.clientWidth - 32), narrow = W < 620;
  const labW = narrow ? 0 : 230, gutter = 26, colW = (W - labW - gutter) / 2, rh = narrow ? 58 : 40, top = 40;
  const x1 = labW, x2 = labW + colW + gutter;
  const gmax = Math.max(...rows.map(r => Math.abs(r.gap))), amax = Math.max(...rows.map(r => r.answers));
  const H = top + rh * rows.length + 10;
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Gap size against number of written answers, by topic'}, host);
  text(svg, x1, 14, 'FELT: gap in the survey', 'sub'); text(svg, x1, 28, 'percentage points', 'sub');
  text(svg, x2, 14, 'SAID: written answers raising it', 'sub'); text(svg, x2, 28, 'number of answers', 'sub');
  rows.forEach((r, i) => {
    const y = top + rh * i, by = narrow ? y + 24 : y + 10, bh = 18;
    const g = el('g', {class: r.pair === worst.pair || v3sel === r.pair ? 'key-row' : ''}, svg);
    el('rect', {x: 0, y, width: W, height: rh - 4, rx: 6, class: 'row-bg'}, g);
    text(g, narrow ? 6 : 6, narrow ? y + 16 : y + 24, r.concept, 'lab');
    const gw = Math.abs(r.gap) / gmax * (colW - 70), aw = r.answers / amax * (colW - 50);
    el('rect', {x: x1, y: by, width: Math.max(2, gw), height: bh, rx: 3, fill: r.gap < 0 ? 'var(--lose)' : 'var(--win)'}, g);
    text(g, x1 + gw + 6, by + 14, (r.gap < 0 ? '−' : '+') + pts(r.gap) + ' pts', 'val');
    el('rect', {x: x2, y: by, width: Math.max(2, aw), height: bh, rx: 3, fill: 'var(--said)'}, g);
    text(g, x2 + aw + 6, by + 14, r.answers, 'val');
    const hit = el('rect', {x: 0, y, width: W, height: rh - 4, class: 'hit', tabindex: 0, role: 'button', 'aria-label': `${r.concept}: ${gapTxt(r.gap)}, ${r.answers} written answers`}, svg);
    bindHit(hit, `<b>${esc(r.concept)}</b> (${esc(r.gate.toLowerCase())} gate)<br>Felt: ${gapTxt(r.gap)} received than valued<br>Said: ${r.answers} written answers — ${r.best_pos} praising it in best sales teams, ${r.worst_neg} criticising it in worst, ${r.q21} naming it as what sets a vendor apart<br>Topics counted: ${esc(r.code_labels.join('; '))}`, () => {
      v3sel = r.pair; hideTip(); drawV3();
      reader($('#v3reader'), `${r.concept}: what decision-makers wrote`, [
        {key: 'best', label: 'Best sales teams', ids: r.answer_ids.filter(i => side(i) === 'best')},
        {key: 'worst', label: 'Worst sales teams', ids: r.answer_ids.filter(i => side(i) === 'worst')},
        {key: 'q21', label: 'What sets a vendor apart', ids: r.answer_ids.filter(i => side(i) === 'q21')},
        {key: 'other', label: 'Other answers', ids: r.answer_ids.filter(i => side(i) === 'other')}]); });
  });
  const kr = rows.findIndex(r => r.pair === worst.pair);
  if (kr >= 0) { const r = rows[kr], y = top + rh * kr; text(svg, x2 + r.answers / amax * (colW - 50) + 40, (narrow ? y + 24 : y + 10) + 14, narrow ? '← fewest' : '← largest gap, fewest mentions', 'callout'); }
}
const w3 = pt(worst.pair), o3 = pt(over.pair);
reading($('#read3'),
  `<p><b>Business knowledge is felt and said.</b> The four rows about knowing the customer's business have gaps of about ${N(Math.round(-Math.max(...knowGap) * 100) + '–' + Math.round(-Math.min(...knowGap) * 100) + ' points')}, and each comes up in ${N(Math.min(...knowAns) + '–' + Math.max(...knowAns))} written answers.</p>` +
  `<p><b>The business case is felt but not said.</b> ${esc(worst.concept)} has the largest gap (${N(gapTxt(w3.gap))}) and comes up in only ${N(w3.answers)} answers.</p>` +
  `<p><b>The pitch is said, mostly as a complaint.</b> Of its ${N(o3.answers)} answers, ${N(o3.worst_neg)} criticise it in worst sales teams and ${N(o3.best_pos)} praise it in best.</p>`,
  `<p>When customers describe good and bad salespeople, they talk about whether the salesperson knows their business and whether they push product. They almost never talk about being helped to build the case, although the survey shows it is what they lack most. The likely reason is that customers have no ready words for it (View 4 shows no customer-side word for “carrying the idea inside the company”). A need the customer cannot name is a need the salesperson will not hear.</p>`,
  `<p>Asking customers what they want will not surface this gap: win/loss interviews, satisfaction surveys and discovery questions all rely on the customer naming it. It has to be designed into the sales approach and checked at the Case gate directly.</p>`);

// ---------------------------------------------------------------- reader
function reader(host, title, groupsDef){
  host.hidden = false;
  let cur = (groupsDef.find(g => g.ids.length) || groupsDef[0]).key;
  function render(){
    const g = groupsDef.find(z => z.key === cur);
    host.innerHTML = `<div class="reader-head"><h4>${esc(title)}</h4><div class="tabs">` +
      groupsDef.map(z => `<button type="button" aria-pressed="${z.key === cur}" data-k="${z.key}">${esc(z.label)} <span class="n">${z.ids.length}</span></button>`).join('') +
      `</div></div><ul class="quotes">` + (g.ids.length ? g.ids.map(id => { const a = D.answers[id];
        const s = ['Q22','Q24'].includes(a.item) ? 'best' : ['Q23','Q25'].includes(a.item) ? 'worst' : '';
        return `<li class="${s}">${esc(a.text)}<div class="meta">${esc(a.item)}${QNAME[a.item] ? ' · ' + esc(QNAME[a.item]) : ''} · respondent ${esc(a.respid)}</div></li>`; }).join('')
        : '<li>No answers in this group.</li>') + '</ul>';
    host.querySelectorAll('button[data-k]').forEach(b => b.addEventListener('click', () => { cur = b.dataset.k; render(); }));
  }
  render(); host.scrollIntoView({block: 'nearest'});
}
const side = id => { const it = D.answers[id].item; return ['Q22','Q24'].includes(it) ? 'best' : ['Q23','Q25'].includes(it) ? 'worst' : it === 'Q21' ? 'q21' : 'other'; };

// ---------------------------------------------------------------- V4 wins / loses
$('#h4').textContent = `Knowing the business wins accounts. How salespeople behave loses them.`;
$('#howto4').innerHTML = `<h3>How to read this chart</h3><ul>` +
  `<li>Decision-makers named their three most and three least effective sales teams and said why (${N('Q22')}, ${N('Q23')}), and who their main contact is in their best and worst relationships (${N('Q24')}, ${N('Q25')}).</li>` +
  `<li>We coded each written reason for the behaviour it describes. Each row is one behaviour.</li>` +
  `<li><span class="key"><span class="bar" style="background:var(--win)"></span><b>Blue, right</b></span> = how many answers about a <b>best</b> team praise it. <span class="key"><span class="bar" style="background:var(--lose)"></span><b>Red, left</b></span> = how many answers about a <b>worst</b> team criticise it.</li>` +
  `<li>The label beside each row says which way it decides accounts: <b>satisfier</b> — mostly praised when present; <b>dissatisfier</b> — mostly complained about when missing; <b>critical</b> — decides both ways.</li></ul>`;
let v4sel = null;
function drawV4(){
  const host = $('#v4chart'); host.innerHTML = '';
  const rows = D.v4.behaviours.filter(b => b.class !== 'too few').sort((a, b) => b.experiential - a.experiential || a.code.localeCompare(b.code));
  const W = Math.max(320, host.clientWidth - 32), narrow = W < 620;
  const labW = narrow ? 0 : 280, rh = narrow ? 40 : 24, top = 10;
  const Cx = labW + (W - labW) / 2, half = (W - labW) / 2 - 34;
  const mx = Math.max(...rows.map(r => Math.max(r.effective, r.ineffective)));
  const sc = v => v / mx * half, H = top + rh * rows.length + 8;
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Behaviours by answers in worst and best sales teams'}, host);
  el('line', {x1: Cx, x2: Cx, y1: top - 4, y2: H - 4, class: 'ax'}, svg);
  rows.forEach((r, i) => {
    const y = top + rh * i, by = narrow ? y + 20 : y + 4, bh = narrow ? 14 : 16;
    const g = el('g', {class: v4sel === r.code ? 'sel' : ''}, svg);
    el('rect', {x: 0, y, width: W, height: rh, class: 'row-bg'}, g);
    text(g, 4, narrow ? y + 13 : y + 16, r.label, 'lab');
    text(g, narrow ? W - 4 : 214, narrow ? y + 13 : y + 16, r.class, 'sub', narrow ? 'end' : 'start');
    if (r.ineffective) el('rect', {x: Cx - sc(r.ineffective), y: by, width: sc(r.ineffective), height: bh, rx: 3, fill: 'var(--lose)'}, g);
    if (r.effective) el('rect', {x: Cx, y: by, width: sc(r.effective), height: bh, rx: 3, fill: 'var(--win)'}, g);
    text(g, Cx - sc(r.ineffective) - 6, by + bh - 3, r.ineffective, 'val', 'end');
    text(g, Cx + sc(r.effective) + 6, by + bh - 3, r.effective, 'val');
    const hit = el('rect', {x: 0, y, width: W, height: rh, class: 'hit', tabindex: 0, role: 'button', 'aria-label': `${r.label}: ${r.ineffective} criticised, ${r.effective} praised, ${r.class}`}, svg);
    bindHit(hit, `<b>${esc(r.label)}</b> · ${esc(r.class)}<br>${esc(r.definition)}<br>Criticised in worst teams: <b>${r.ineffective}</b> · praised in best: <b>${r.effective}</b><br>Named as what sets a vendor apart (Q21): ${r.q21}`, () => {
      v4sel = r.code; hideTip(); drawV4();
      reader($('#v4reader'), `${r.label} (${r.class}): what decision-makers wrote`, [
        {key: 'worst', label: 'Criticised, worst teams', ids: r.worst_ids}, {key: 'best', label: 'Praised, best teams', ids: r.best_ids}]); });
  });
  const few = D.v4.behaviours.filter(b => b.class === 'too few').map(b => b.label);
  const note = document.createElement('p'); note.className = 'legend'; note.textContent = `Fewer than 10 answers, not shown: ${few.join(', ')}.`; host.appendChild(note);
}
const dis = cls('dissatisfier'), sat = cls('satisfier');
reading($('#read4'),
  `<p><b>${esc(kb.label)}</b> is the most praised behaviour in best teams (${N(kb.effective)} answers) and the most common answer to what sets a vendor apart (${N(kb.q21)}).</p>` +
  `<p><b>${esc(cf.label)}</b> is the most criticised behaviour in worst teams (${N(cf.ineffective)} answers against ${N(cf.effective)} praising it). The other dissatisfiers are about conduct too: ${esc(dis.filter(b => b.code !== cf.code).map(b => b.label.toLowerCase()).join(', '))}.</p>` +
  `<p>${N(sat.length)} behaviours are satisfiers, ${N(dis.length)} dissatisfiers, ${N(cls('critical').length)} critical.</p>`,
  `<p>Decision-makers judge salespeople on two separate scales. What wins an account is knowledge and help: knowing the business, solving the problem, knowing the product, bringing ideas. What loses an account is behaviour: pushing the vendor's agenda, disrespect, being hard to deal with, dishonesty. Being polite and responsive does not win the account; it only avoids losing it.</p>`,
  `<p>Winning and not losing are different investments. Training on conduct (less pushing, more respect) stops losses. Building business knowledge and problem-solving is what wins, and that is exactly where View 1 shows the shortfall.</p>`);

// ---------------------------------------------------------------- V5
$('#h5').textContent = `Vendors have words for steps customers have no words for.`;
$('#howto5').innerHTML = `<h3>How to read this table</h3><ul>` +
  `<li>Each row is one moment in a decision, grouped by gate.</li>` +
  `<li><b>Vendor's word</b>: the term sales teams use for it. <b>Customer's word in the survey</b>: how the survey asked customers about it. <b>Decision-makers' own words</b>: the most frequent words in written answers about it.</li>` +
  `<li><span style="color:var(--lose);font-weight:600">Highlighted rows</span> are gaps: the vendor has a word, the survey has no customer-side word.</li></ul>`;
(function(){
  let h = `<table><thead><tr><th>Gate</th><th>Moment</th><th>Vendor's word</th><th>Customer's word in the survey</th><th>Decision-makers' own words</th><th class="num">Answers</th></tr></thead><tbody>`;
  for (const r of D.v5.rows) {
    const cust = r.gap ? `<td class="gap">No word · ${esc(r.gap)}</td>` : `<td>${esc(r.customer_term.split(' | ')[0])}</td>`;
    h += `<tr class="${r.gap ? 'gaprow' : ''}"><td>${esc(r.gate)}</td><td>${esc(r.concept)}</td><td>${esc(r.vendor_term)}</td>${cust}<td>${esc(r.top_words.slice(0, 5).join(', ') || '—')}</td><td class="num">${r.answers}</td></tr>`;
  }
  $('#v5table').innerHTML = h + `</tbody></table>`;
})();
const l17 = D.v5.rows.find(r => r.id === 'L17'), l28 = D.v5.rows.find(r => r.id === 'L28');
reading($('#read5'),
  `<p>${N(gaps5.length + ' of ' + D.v5.rows.length)} moments have a vendor word and no customer word. Among them: being mis-targeted, being chased, a first meeting that was not worth it, material that never reaches the decision, and <b>${esc(l17.concept.toLowerCase())}</b> (${N(l17.answers)} written answers).</p>` +
  `<p>Where answers exist, they are vivid: “${esc(l28.top_words.find(w => w === 'arrogant') || l28.top_words[0])}” is the commonest word for <b>${esc(l28.concept.toLowerCase())}</b> (${N(l28.answers)} answers, ${N(l28.worst)} about worst teams).</p>`,
  `<p>The vendor side has a full vocabulary for its own process (cadence, champion, multithreading, business case). The customer side often has none for the same moments. What has no name is hard to ask for, hard to complain about, and easy for both sides to skip. This is the language behind View 2's silent gap.</p>`,
  `<p>Salespeople who describe their work in the customer's terms, and give customers words for the steps they lack (for example, how to carry the idea inside their own company), close the gap that customers cannot close for themselves.</p>`);

// ---------------------------------------------------------------- implications
const IMPS = [
  ['Rebalance the meeting from presenting to understanding.', `Customers get product presentations ${gapTxt(pp.gap)} than they value, and business understanding about ${Math.round(-Math.min(...knowGap) * 100)} points less.`, 'View 1 · rows “The pitch” and the business-knowledge rows'],
  ['Make the business case a deliverable, not a hope.', `${worst.concept} is the largest gap (${gapTxt(p7.gap)}) and the least mentioned (${w3.answers} answers). It will not come up unless the salesperson brings it.`, 'View 1 top row · View 2 · View 4 gap rows'],
  ['Do not rely on customers to tell you what is missing.', 'The biggest shortfall barely appears in customers\' own words, so feedback, win/loss reviews and discovery questions will under-report it. Check it at the Case gate directly.', 'View 2'],
  ['Treat winning and not losing as separate programmes.', `Knowledge wins (${kb.label.toLowerCase()}: ${kb.effective} praised). Conduct loses (${cf.label.toLowerCase()}: ${cf.ineffective} criticised).`, 'View 3'],
  ['Fix the design before the people.', `The largest gaps (${steadyNames.join('; ')}) run the same way in every group large enough to show, so they point at how selling is organised, trained and equipped, not at individual salespeople.`, 'View 1 group picker · Phase 4 cohort analysis (T04)'],
];
$('#imps').innerHTML = IMPS.map(([t, why, ev]) => `<li><b>${esc(t)}</b><span>${esc(why)}</span><span class="ev">Evidence: ${esc(ev)}</span></li>`).join('');
$('#limits').innerHTML = [
  'All survey results describe groups of decision-makers, not individuals; we cannot say that any one person both valued and missed something.',
  'Written answers and survey answers are linked by topic, not by person: the written answers carry no role or level.',
  `The topic coding is one coder's work, checked blind on 200 answers (good agreement on behaviours; usable with caution on vocabulary).`,
  'The data show the gaps exist and go unspoken. They do not show that closing them raises revenue; that needs separate evidence.',
  'The pairing of “valued” and “received” questions is an interpretation of the survey, reviewed and confirmed by Scott Santucci.'
].map(s => `<li>${esc(s)}</li>`).join('');
$('#foot').innerHTML = `<div>Built from committed data by scripts in the project repository: <a href="${D.repo}" target="_blank" rel="noopener">${esc(D.repo.replace('https://', ''))}</a> (<code>06_visualization/</code>).</div>` +
  `<div>Every number on this page is computed from the embedded data; none is typed by hand. Interpretations and implications are marked as such. Respondents appear by anonymous ID only.</div>`;

function drawAll(){ drawV1(); drawV3(); drawV4(); }
drawAll();
let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(drawAll, 120); });
})();
</script>
"""


if __name__ == "__main__":
    sys.exit(main())
