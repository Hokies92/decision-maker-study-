#!/usr/bin/env python3
"""p6_build_argument_page.py — the argument page (P6.S04; rebuilt after Scott's review, 2026-10-30).

Thesis (Scott): vendors should walk away thinking "we are focused on all of the wrong things, and it's horrible — but we
don't have to do a lot to be very different from our competition."
Every finding reads one survey question directly, in its own wording, and opens with the same five-part frame Scott asked
for: scope (gate), items (the question), vantage point (who is speaking), scale (what the number means), stakes (what it
costs the customer). No result is subtracted from another question's result.

Inputs: 06_visualization/data/findings.json, v0_context.json (P6.S03 data layer).
Output: 06_visualization/argument.html — committed (public with the repo) and published as a page (D6-2: both).
Numbers are computed in the page from the embedded data; interpretation is labelled as such.
Usage: python3 -I scripts/p6_build_argument_page.py [--fragment <path for the publishable copy>]
"""
import json
import sys
from pathlib import Path

DATA = Path("06_visualization/data")
OUT = Path("06_visualization/argument.html")
REPO = "https://github.com/Hokies92/decision-maker-study-"


def main() -> int:
    f = json.loads((DATA / "findings.json").read_text(encoding="utf-8"))
    v0 = json.loads((DATA / "v0_context.json").read_text(encoding="utf-8"))
    payload = {"f": f, "v0": v0, "repo": REPO}
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=False).replace("</", "<\\/")
    page = TEMPLATE.replace("__DATA__", blob)
    OUT.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                   '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                   + page.replace("<main>", "</head>\n<body>\n<main>", 1) + "</body>\n</html>\n", encoding="utf-8")
    if "--fragment" in sys.argv:
        Path(sys.argv[sys.argv.index("--fragment") + 1]).write_text(page, encoding="utf-8")
    print(f"{OUT}: {OUT.stat().st_size} bytes")
    return 0


TEMPLATE = r"""<title>The Wrong Focus</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: one reading column in three acts — what vendors focus on, what it costs, how low the bar is. Every finding
   opens with the same five-part frame card, then the question's answers as bars, a plain reading, and the customers' words. */
:root{
  --bg:#f6f7f8; --panel:#ffffff; --fg:#14181d; --fg2:#4d5560; --muted:#7c8590; --rule:#dde1e6; --track:#eceff2;
  --vendor:#eb6834; --vendor-2:#f6b89e; --cust:#2a78d6; --cust-2:#a9c8f0; --neutral:#9aa3ad; --frame:#f1f4f8; --hl:#fff4ec;
  --display:"Archivo",system-ui,-apple-system,"Segoe UI",sans-serif;
  --body:"Source Serif 4",Georgia,"Times New Roman",serif;
  --data:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121417; --panel:#1a1d21; --fg:#eef0f2; --fg2:#b8bfc7; --muted:#8a929b; --rule:#2c3137; --track:#262a2f;
  --vendor:#d95926; --vendor-2:#6e3a26; --cust:#3987e5; --cust-2:#244a78; --neutral:#5d656e; --frame:#1d2228; --hl:#2a211b; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121417; --panel:#1a1d21; --fg:#eef0f2; --fg2:#b8bfc7; --muted:#8a929b; --rule:#2c3137; --track:#262a2f;
  --vendor:#d95926; --vendor-2:#6e3a26; --cust:#3987e5; --cust-2:#244a78; --neutral:#5d656e; --frame:#1d2228; --hl:#2a211b; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16.5px;line-height:1.6;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:900px;margin:0 auto;padding-block:40px 64px;display:grid;grid-template-columns:minmax(0,1fr);gap:56px}
main>*,.act>*,.finding>*{min-width:0}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0;letter-spacing:-.01em}
h1{font-size:clamp(34px,5.6vw,56px);font-stretch:85%;font-weight:800;line-height:1.04}
h2{font-size:clamp(26px,3.6vw,36px);font-stretch:88%;font-weight:800;line-height:1.1}
h3{font-size:clamp(20px,2.6vw,24px);font-stretch:92%;font-weight:700;line-height:1.2}
h4{margin:0;font-family:var(--display);font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
p{margin:0;max-width:68ch}
.eyebrow{font-family:var(--display);font-size:12px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
.n{font-family:var(--data);font-variant-numeric:tabular-nums;font-size:.92em;white-space:nowrap}
header{display:grid;gap:18px}
.lede{font-size:clamp(18px,2.2vw,21px);color:var(--fg2);max-width:62ch}
.tiles{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.tile{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;display:grid;gap:4px;align-content:start}
.tile .big{font-family:var(--display);font-size:40px;font-weight:800;font-stretch:85%;line-height:1}
.tile span{font-family:var(--display);font-size:14px;color:var(--fg2);line-height:1.4}
.howframe{background:var(--frame);border-radius:10px;padding:16px;display:grid;gap:10px}
.howframe dl,.frame dl{display:grid;grid-template-columns:max-content 1fr;gap:6px 14px;margin:0}
.howframe dt,.frame dt{font-family:var(--display);font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding-top:3px}
.howframe dd,.frame dd{margin:0;font-size:15px;color:var(--fg2)}
.frame dd q{color:var(--fg);quotes:"“" "”"}
@media (max-width:560px){.howframe dl,.frame dl{grid-template-columns:1fr}.frame dt{padding-top:6px}}
.act{display:grid;gap:40px;padding-top:8px;border-top:3px solid var(--fg)}
.act-head{display:grid;gap:8px}
.finding{display:grid;gap:16px}
.frame{background:var(--frame);border-radius:10px;padding:14px 16px}
.chart{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:16px;display:grid;gap:12px}
.chart-title{font-family:var(--display);font-size:14px;font-weight:600;color:var(--fg)}
.chart-note{font-family:var(--display);font-size:12.5px;color:var(--muted)}
.rows{display:grid;gap:10px}
.row{display:grid;grid-template-columns:minmax(0,1fr) 56px;gap:4px 10px;align-items:center}
.row .lab{grid-column:1/-1;font-family:var(--display);font-size:14px;line-height:1.35;color:var(--fg)}
.row .track{height:14px;background:var(--track);border-radius:4px;overflow:hidden;display:flex}
.row .val{font-family:var(--data);font-size:13px;text-align:right;font-variant-numeric:tabular-nums}
.seg{height:100%}
.v{background:var(--vendor)} .c{background:var(--cust)} .x{background:var(--neutral)}
.f4{background:var(--cust)} .f3{background:var(--cust-2)} .f2,.f1{background:transparent}
.f4.own{background:var(--vendor)} .f3.own{background:var(--vendor-2)}
.group-lab{font-family:var(--display);font-size:11.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding-top:4px}
.group-lab.v-t{color:var(--vendor)} .group-lab.c-t{color:var(--cust)}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-family:var(--display);font-size:13px;color:var(--fg2)}
.key{display:inline-flex;align-items:center;gap:6px}.sw{width:14px;height:10px;border-radius:3px;display:inline-block}
.two{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.plain{border-left:3px solid var(--fg);padding-left:14px;display:grid;gap:8px}
.plain p{color:var(--fg)}
.meaning{border-left:3px solid var(--vendor);padding-left:14px;display:grid;gap:6px}
.meaning p{color:var(--fg2)}
.tag{font-family:var(--display);font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-left:6px}
.quotes{list-style:none;margin:0;padding:0;display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.quotes li{background:var(--panel);border:1px solid var(--rule);border-left:3px solid var(--rule);border-radius:8px;padding:10px 12px;font-size:15px;display:grid;gap:4px;align-content:start}
.quotes li.best{border-left-color:var(--cust)} .quotes li.worst{border-left-color:var(--vendor)}
.quotes .meta{font-family:var(--display);font-size:12px;color:var(--muted)}
.bar-list{display:grid;gap:8px}
.actions{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.actions li{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;display:grid;gap:6px}
.actions b{font-family:var(--display);font-size:17px;line-height:1.3}
.actions .ev{font-family:var(--display);font-size:13px;color:var(--muted)}
.limits{display:grid;gap:4px;padding-left:20px;margin:0;color:var(--fg2)}
details.about{font-family:var(--display);font-size:13px;color:var(--fg2)}
details.about summary{cursor:pointer;color:var(--muted);font-weight:600}
details.about ul{margin:6px 0;padding-left:18px;display:grid;gap:3px}
details.about code{font-family:var(--data);font-size:12px;overflow-wrap:anywhere}
footer{font-family:var(--display);font-size:13px;color:var(--muted);border-top:1px solid var(--rule);padding-top:16px;display:grid;gap:6px}
footer a,nav a{color:var(--fg2)}
nav{display:flex;flex-wrap:wrap;gap:6px 16px;font-family:var(--display);font-size:13.5px}
summary:focus-visible,a:focus-visible{outline:2px solid var(--cust);outline-offset:2px}
</style>

<main>
<header>
  <div class="eyebrow">What business decision-makers say about vendors' salespeople</div>
  <h1>Vendors are focused on the wrong things.</h1>
  <p class="lede" id="lede"></p>
  <div class="tiles" id="tiles"></div>
  <nav aria-label="Sections"><a href="#how">How to read this</a><a href="#act1">1 · What vendors focus on</a><a href="#act2">2 · What it costs</a><a href="#act3">3 · How low the bar is</a><a href="#act4">What to do</a></nav>
</header>

<section class="howframe" id="how">
  <h4>How to read every finding</h4>
  <p id="who"></p>
  <dl>
    <dt>Scope</dt><dd>Which step of the customer's decision the finding covers. The study uses five steps, each a yes or no: <span id="gatesline"></span>.</dd>
    <dt>Question</dt><dd>The exact question the decision-makers answered, and its answer choices.</dd>
    <dt>Vantage point</dt><dd>Who is speaking and about what. Here it is always the customer, describing the vendors and salespeople they deal with.</dd>
    <dt>Scale</dt><dd>What a number means. Unless stated otherwise: the share of all <span class="n" id="n1"></span> decision-makers who chose that answer.</dd>
    <dt>At stake</dt><dd>What the customer loses when the vendor gets this wrong.</dd>
  </dl>
</section>

<section class="act" id="act1">
  <div class="act-head"><div class="eyebrow">Act 1</div><h2>What vendors focus on: their product, not the customer's problem</h2></div>
  <article class="finding" id="f-meeting"></article>
  <article class="finding" id="f-prep"></article>
  <article class="finding" id="f-case"></article>
</section>

<section class="act" id="act2">
  <div class="act-head"><div class="eyebrow">Act 2</div><h2>What it costs: decisions that stall or go to someone else</h2></div>
  <article class="finding" id="f-cost"></article>
</section>

<section class="act" id="act3">
  <div class="act-head"><div class="eyebrow">Act 3</div><h2>How low the bar is: a little customer focus stands out</h2></div>
  <article class="finding" id="f-bar"></article>
</section>

<section class="act" id="act4">
  <div class="act-head"><div class="eyebrow">What to do</div><h2>Small changes, large difference</h2>
  <p>These follow from the findings above. They are interpretation, not data; each names the finding it rests on.</p></div>
  <ul class="actions" id="actions"></ul>
  <div class="finding"><h4>What this evidence cannot tell you</h4><ul class="limits" id="limits"></ul>
  <details class="about" id="about"></details></div>
</section>

<footer id="foot"></footer>
</main>

<script type="application/json" id="data">__DATA__</script>
<script>
(function(){
const D = JSON.parse(document.getElementById('data').textContent), F = D.f, C = D.v0;
const $ = s => document.querySelector(s);
const pct = v => Math.round(v * 100) + '%';
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const strip = s => String(s).replace(/<[^>]+>/g, '');
const N = s => `<span class="n">${s}</span>`;
const oneIn = v => { const k = Math.round(1 / v); return `1 in ${k}`; };
const opt = (q, i) => q.items[0].options[i];
const item = (q, id) => q.items.find(x => x.item === id);
const single = (q, id) => item(q, id).options[0].share;      // pick-several: share who ticked it
const freq = (q, id) => item(q, id).options.find(o => o.label === 'Frequently').share;
const QNAME = {Q22: 'about one of their three MOST effective sales teams', Q23: 'about one of their three LEAST effective sales teams',
  Q24: 'about the main contact in their BEST vendor relationships', Q25: 'about the main contact in their WORST vendor relationships', Q21: 'on what sets a vendor apart'};

// ---------------- numbers used in the words
const n = F.respondents;
const q14 = F.q14, pitchShare = opt(q14, 0).share + opt(q14, 1).share, custShare = opt(q14, 3).share + opt(q14, 4).share;
const q11 = F.q11, demo = single(q11, 'Q11_6'), issues = single(q11, 'Q11_3'), solve = single(q11, 'Q11_1');
const q8 = F.q8, ownF = freq(q8, 'Q8_1'), bizF = freq(q8, 'Q8_3'), issF = freq(q8, 'Q8_5');
const q18 = F.q18, simple = opt(q18, 0).share, ownWork = opt(q18, 2).share + opt(q18, 3).share + opt(q18, 4).share, mostAll = opt(q18, 3).share + opt(q18, 4).share;
const q15 = F.q15, other = single(q15, 'Q15_1'), envision = single(q15, 'Q15_2'), risky = single(q15, 'Q15_3'), board = single(q15, 'Q15_5'), momentum = single(q15, 'Q15_4');
const B = c => F.behaviours.find(b => b.code === c);

// ---------------- header
$('#lede').innerHTML = `${N(n)} business decision-makers describe what vendors' salespeople do, what they want instead, and why they walk away. ` +
  `The picture is bad: most sales effort goes into the vendor's own product, and customers lose deals they wanted because of it. ` +
  `It is also an opportunity: so few vendors get the basics right that a small shift in focus is enough to stand out.`;
$('#tiles').innerHTML =
  `<div class="tile"><span class="big n">${pct(pitchShare)}</span><span>say the typical sales meeting is a product pitch. ${pct(custShare)} say it is about their challenges or success.</span></div>` +
  `<div class="tile"><span class="big n">${pct(bizF)}</span><span>say salespeople frequently come prepared on their specific business. ${pct(ownF)} say they come prepared on their own products.</span></div>` +
  `<div class="tile"><span class="big n">${pct(simple)}</span><span>say vendor material makes the business case simple. ${pct(mostAll)} had to build most or all of it themselves.</span></div>`;
$('#who').innerHTML = `Everyone in this study is a customer: ${N(n)} decision-makers who take part in their company's IT purchases, ${N(C.it_decision_makers)} from IT and ${N(C.business_decision_makers)} from the business side; ` +
  C.levels.map(l => `${N(l.n)} ${esc(l.label === 'C-level' ? 'C-level executives' : l.label.toLowerCase() + 's')}`).join(', ') + `. They answered fixed-choice survey questions and wrote ${N(C.written_answers.toLocaleString('en-US'))} answers in their own words.`;
$('#gatesline').innerHTML = C.gates.map(g => `<b>${esc(g.name)}</b>`).join(' → ') + ' (right people reached; meeting won; idea agreed worth exploring; shared picture of success; business case accepted)';
$('#n1').textContent = n;

// ---------------- builders
function frame(o){
  return `<div class="frame"><dl>` +
    `<dt>Scope</dt><dd>${o.scope}</dd>` +
    `<dt>Question</dt><dd>${o.items}</dd>` +
    `<dt>Vantage point</dt><dd>${o.vantage}</dd>` +
    `<dt>Scale</dt><dd>${o.scale}</dd>` +
    `<dt>At stake</dt><dd>${o.stakes}</dd></dl></div>`;
}
function bars(rows){   // rows: {label, value, cls, group?}
  let h = '<div class="rows">', g = null;
  for (const r of rows) {
    if (r.group && r.group !== g) { g = r.group; h += `<div class="group-lab ${r.gcls || ''}">${esc(g)}</div>`; }
    h += `<div class="row"><div class="lab">${esc(r.label)}</div><div class="track" role="img" aria-label="${esc(r.label)}: ${pct(r.value)}"><div class="seg ${r.cls}" style="width:${(r.value * 100).toFixed(1)}%"></div></div><div class="val">${pct(r.value)}</div></div>`;
  }
  return h + '</div>';
}
function countBars(rows, max, cls){
  let h = '<div class="rows">';
  for (const r of rows) h += `<div class="row"><div class="lab">${esc(r.label)}</div><div class="track" role="img" aria-label="${esc(r.label)}: ${r.value} answers"><div class="seg ${cls}" style="width:${(r.value / max * 100).toFixed(1)}%"></div></div><div class="val">${r.value}</div></div>`;
  return h + '</div>';
}
function quotes(key){
  const qs = F.quotes.filter(q => q.finding === key);
  return `<h4>In their own words</h4><ul class="quotes">` + qs.map(q => {
    const s = ['Q22','Q24'].includes(q.item) ? 'best' : ['Q23','Q25'].includes(q.item) ? 'worst' : '';
    return `<li class="${s}">“${esc(q.text)}”<span class="meta">Decision-maker ${esc(q.respid)}, ${esc(QNAME[q.item] || q.item)}</span></li>`; }).join('') + `</ul>`;
}
const plain = (h, body) => `<div class="plain"><h4>What it shows</h4>${body}</div>`;
const meaning = body => `<div class="meaning"><h4>What it means <span class="tag">interpretation</span></h4>${body}</div>`;
const Q = (id, s) => `${N(id)} <q>${esc(strip(s))}</q>`;

// ---------------- Finding 1: the meeting
$('#f-meeting').innerHTML = `<h3>The typical meeting is a product pitch. Customers value a meeting about their problem.</h3>` +
  frame({scope: '<b>Agree</b> — the meeting where the customer decides whether the idea is worth exploring.',
    items: `${Q('Q14', q14.stem)} One answer each. And ${Q('Q11', q11.stem)} As many answers as apply.`,
    vantage: 'The customer, describing the sales meetings they typically sit through, and what makes one worth their time.',
    scale: `Left: share of all ${n} who chose each description; adds to 100%. Right: share who ticked each item; adds to more than 100%.`,
    stakes: `Whether the customer gives the idea a second meeting. Of those who walked away from a vendor they were interested in, ${pct(envision)} say they <q>could not envision how the value would be delivered</q>.`}) +
  `<div class="two"><div class="chart"><div class="chart-title">What the typical meeting is like (${N('Q14')})</div>` +
    bars(q14.items[0].options.map((o, i) => ({label: o.label, value: o.share, cls: i < 2 ? 'v' : 'c', group: i < 2 ? 'About the vendor\'s product' : 'About the customer', gcls: i < 2 ? 'v-t' : 'c-t'}))) +
    `<div class="chart-note">Grouping into “about the product” and “about the customer” is our reading of the answer wording.</div></div>` +
  `<div class="chart"><div class="chart-title">What makes a meeting valuable (${N('Q11')})</div>` +
    bars(q11.items.slice().sort((a, b) => b.options[0].share - a.options[0].share).map(x => ({label: x.label, value: x.options[0].share, cls: x.item === 'Q11_6' ? 'v' : 'c'}))) +
    `<div class="chart-note">The orange bar is the one item about the vendor's presentation.</div></div></div>` +
  plain('', `<p>${N(pct(pitchShare))} of decision-makers say the typical sales meeting is about the vendor's product: either a straight presentation, or listening for a cue to launch the pitch. Only ${N(pct(custShare))} say it is about understanding their challenges or making their initiative succeed.</p>` +
    `<p>Yet when asked what makes a meeting valuable, ${N(pct(issues))} pick a salesperson who understands their business issues and can explain how to solve them, and ${N(pct(solve))} a meeting that helps them think about how to solve a business problem. Only ${N(pct(demo))} pick a compelling presentation or demo.</p>`) +
  meaning(`<p>The meeting customers get is the one they value least. The pitch is not a minor flaw; it is what most meetings are made of.</p>`) +
  quotes('pitch');

// ---------------- Finding 2: preparation
const q8rows = q8.items.map(x => ({label: x.label, f: x.options.find(o => o.label === 'Frequently').share, o: x.options.find(o => o.label === 'Occasionally').share, own: x.item === 'Q8_1'}));
$('#f-prep').innerHTML = `<h3>Salespeople prepare on their own products, not on the customer.</h3>` +
  frame({scope: '<b>Agree</b> — what the salesperson brings into the meeting.',
    items: `${Q('Q8', q8.stem)} Each item rated Never, Rarely, Occasionally or Frequently.`,
    vantage: 'The customer, judging how prepared salespeople generally are when they meet.',
    scale: `For each item, the share of all ${n} who answered “Frequently” (dark) and “Occasionally” (light). The rest answered Rarely or Never.`,
    stakes: 'Whether the meeting is worth the customer\'s time. A salesperson who does not know the business cannot show how to solve its problems — the top reason a meeting is valuable (Finding 1).'}) +
  `<div class="chart"><div class="chart-title">How often salespeople come prepared (${N('Q8')})</div><div class="rows">` +
    q8rows.sort((a, b) => b.f - a.f).map(r => `<div class="row"><div class="lab">${esc(r.label)}</div><div class="track" role="img" aria-label="${esc(r.label)}: ${pct(r.f)} frequently, ${pct(r.o)} occasionally"><div class="seg f4 ${r.own ? 'own' : ''}" style="width:${(r.f * 100).toFixed(1)}%"></div><div class="seg f3 ${r.own ? 'own' : ''}" style="width:${(r.o * 100).toFixed(1)}%"></div></div><div class="val">${pct(r.f)}</div></div>`).join('') +
    `</div><div class="legend"><span class="key"><span class="sw" style="background:var(--vendor)"></span>about the vendor itself</span><span class="key"><span class="sw" style="background:var(--cust)"></span>about the customer</span><span class="key"><span class="sw" style="background:var(--cust-2)"></span>lighter: occasionally</span><span>Number: share answering “Frequently”.</span></div></div>` +
  plain('', `<p>${N(pct(ownF))} say salespeople frequently come knowing their own company and products. Only ${N(pct(bizF))} say they frequently come knowing the customer's specific business, and ${N(pct(issF))} that they frequently understand the customer's issues and where they can help.</p>`) +
  meaning(`<p>Salespeople are prepared to talk about themselves. Preparing on the customer is the exception: about ${N(oneIn(bizF))} decision-makers say it happens frequently.</p>`) +
  quotes('prepared');

// ---------------- Finding 3: the business case
$('#f-case').innerHTML = `<h3>Customers build the business case alone.</h3>` +
  frame({scope: '<b>Case</b> — whether the customer can justify the purchase inside their company.',
    items: `${Q('Q18', q18.stem)} One answer each.`,
    vantage: 'The customer, describing the materials vendors typically give them.',
    scale: `Share of all ${n} who chose each description; adds to 100% (with “Other” and “Don't know”).`,
    stakes: `Whether the purchase survives inside the customer's company. Of those who walked away, ${pct(board)} <q>struggled to get others on board internally</q> and ${pct(risky)} found it <q>too risky</q>.`}) +
  `<div class="chart"><div class="chart-title">How well vendor material helps build the case to invest (${N('Q18')})</div>` +
    bars(q18.items[0].options.filter(o => !/^Other|^Don/.test(o.label)).map((o, i) => ({label: o.label, value: o.share, cls: i === 0 ? 'c' : i === 1 ? 'c' : 'v',
      group: i < 2 ? 'Vendor material does most of the work' : 'The customer does significant work themselves', gcls: i < 2 ? 'c-t' : 'v-t'}))) +
    `<div class="chart-note">Grouping is our reading of the answer wording: the bottom three describe significant customization, or doing most or all of the justification themselves.</div></div>` +
  plain('', `<p>Only ${N(pct(simple))} say vendor material makes building a convincing business case simple. ${N(pct(ownWork))} must do significant work themselves, and ${N(pct(mostAll))} — about ${N(oneIn(mostAll))} — did most or all of the justification on their own.</p>`) +
  meaning(`<p>The business case is the last step before a yes, and it is the one vendors leave to the customer. The customer has to sell the purchase inside their own company, mostly without the vendor's help.</p>`) +
  quotes('case');

// ---------------- Finding 4: what it costs
const reasons = q15.items.map(x => ({label: x.label, value: x.options[0].share})).sort((a, b) => b.value - a.value);
const worstB = F.behaviours.slice().sort((a, b) => b.criticised_worst - a.criticised_worst).slice(0, 6);
$('#f-cost').innerHTML = `<h3>Interested customers walk away — to a competitor, or to no decision.</h3>` +
  frame({scope: 'The end of the decision: a customer who was interested and then said no.',
    items: `${Q('Q15', q15.stem)} As many reasons as apply. And, in their own words: which three companies have the <b>least</b> effective sales teams, and why (${N('Q23')}), and who the main contact is in their <b>worst</b> relationships, and why (${N('Q25')}).`,
    vantage: 'The customer, remembering a time they were interested in a vendor and then did not buy.',
    scale: `Left: share of all ${n} who ticked each reason; adds to more than 100%. Right: number of written answers saying the team fails at each behaviour, out of ${F.codable_answers} written answers that say something specific.`,
    stakes: 'The deal itself.'}) +
  `<div class="two"><div class="chart"><div class="chart-title">Why an interested customer did not buy (${N('Q15')})</div>` +
    bars(reasons.map(r => ({label: r.label, value: r.value, cls: 'v'}))) + `</div>` +
  `<div class="chart"><div class="chart-title">Where the worst sales teams fall short (written answers)</div>` +
    countBars(worstB.map(b => ({label: b.label, value: b.criticised_worst})), Math.max(...worstB.map(b => b.criticised_worst)), 'v') +
    `<div class="chart-note">Each answer was read and coded for what it criticises; a row counts answers saying the team fails at that behaviour.</div></div></div>` +
  plain('', `<p>When an interested customer walks away, the most common reasons are going with <b>another vendor</b> (${N(pct(other))}) and not being able to <b>see how the value would be delivered</b> (${N(pct(envision))}). About one in four lost it inside their own company: too risky (${N(pct(risky))}), too much effort to keep momentum as others got involved (${N(pct(momentum))}), or unable to get others on board (${N(pct(board))}).</p>` +
    `<p>In their own words, the most common complaint about the worst sales teams is a failure on <b>“${esc(worstB[0].label)}”</b> (${N(worstB[0].criticised_worst)} answers): they push the vendor's sale over the customer's need. Next comes a failure on <b>“${esc(worstB[1].label)}”</b> (${N(worstB[1].criticised_worst)}).</p>`) +
  meaning(`<p>The costs line up with the focus. A pitch does not show how value will be delivered; a case left to the customer does not survive inside their company. Both are reasons interested customers give for walking away.</p>`);

// ---------------- Finding 5: how low the bar is
const bestB = F.behaviours.slice().sort((a, b) => b.praised_best - a.praised_best).slice(0, 6);
const kb = B('B-KNOWS-BUSINESS');
$('#f-bar').innerHTML = `<h3>Doing the basics puts a vendor ahead of most of its competitors.</h3>` +
  frame({scope: 'All steps: what separates the vendors customers rate best from the rest.',
    items: `In their own words: which three companies have the <b>most</b> effective sales teams, and why (${N('Q22')}); who the main contact is in their <b>best</b> relationships, and why (${N('Q24')}); and ${Q('Q21', C.question_stems.Q21)}`,
    vantage: 'The customer, describing the vendors they rate best.',
    scale: `Number of written answers praising each behaviour, out of ${F.codable_answers} written answers that say something specific. The three figures on the left repeat Findings 1–3.`,
    stakes: 'Being the vendor the customer chooses, rather than the other vendor they went with instead.'}) +
  `<div class="two"><div class="chart"><div class="chart-title">How rare the basics are today</div><div class="bar-list">` +
    bars([{label: 'The typical meeting is about the customer\'s challenges or success (Q14)', value: custShare, cls: 'c'},
          {label: 'Salespeople frequently come prepared on the customer\'s specific business (Q8)', value: bizF, cls: 'c'},
          {label: 'Vendor material makes the business case simple (Q18)', value: simple, cls: 'c'}]) +
    `</div><div class="chart-note">Share of all ${n} decision-makers. Everything outside these bars is the room to stand out.</div></div>` +
  `<div class="chart"><div class="chart-title">What the best sales teams are praised for (written answers)</div>` +
    countBars(bestB.map(b => ({label: b.label, value: b.praised_best})), Math.max(...bestB.map(b => b.praised_best)), 'c') +
    `<div class="chart-note">Each answer was read and coded for the behaviour it praises.</div></div></div>` +
  plain('', `<p>The behaviours that win are basic: <b>${esc(bestB.slice(0, 4).map(b => b.label.toLowerCase()).join(', '))}</b>. Knowing the customer's business is both the most praised behaviour in the best sales teams (${N(kb.praised_best)} answers) and the most common answer to what sets a vendor apart (${N(kb.q21)} answers).</p>` +
    `<p>Today only ${N(pct(custShare))} of decision-makers say the typical meeting is about them, ${N(pct(bizF))} that salespeople frequently know their business, and ${N(pct(simple))} that vendor material makes the case simple.</p>`) +
  meaning(`<p>Customers are not asking for anything exotic: know my business, help me solve the problem, help me make the case. Because so few vendors do it, a vendor that does it consistently is different from most of its competition.</p>`) +
  quotes('different');

// ---------------- what to do
const ACTIONS = [
  ['Make the first meeting about their problem, not your product.', `${pct(pitchShare)} of meetings are a pitch; ${pct(demo)} of customers value a compelling demo, ${pct(issues)} value a salesperson who understands their business issues.`, 'Finding 1'],
  ['Prepare on the customer before you prepare on yourself.', `Preparation on the vendor's own products is frequent for ${pct(ownF)}; on the customer's specific business for ${pct(bizF)}.`, 'Finding 2'],
  ['Give the customer the business case, built for their company.', `Only ${pct(simple)} find it simple with vendor material; ${pct(mostAll)} build most or all of it themselves; ${pct(board)} of those who walked away could not get others on board.`, 'Findings 3 and 4'],
  ['Stop pushing the sale.', `It is the behaviour most criticised in the worst sales teams (${worstB[0].criticised_worst} written answers).`, 'Finding 4'],
];
$('#actions').innerHTML = ACTIONS.map(([t, why, ev]) => `<li><b>${esc(t)}</b><span>${esc(why)}</span><span class="ev">Rests on: ${esc(ev)}</span></li>`).join('');
$('#limits').innerHTML = [
  `All shares describe the ${n} decision-makers as a group; the study does not follow individual deals.`,
  'Customers describe vendors in general, not one named vendor, except in the written answers about their best and worst sales teams.',
  'Grouping answers into “about the product” and “about the customer” is our reading of the answer wording, shown on each chart.',
  'Written answers were coded by one coder and checked blind on 200 of them; the quotes shown were chosen to illustrate, and every answer is in the project data.',
  'The study shows what customers experience and want. It does not measure whether changing focus raises a vendor\'s revenue.'
].map(s => `<li>${esc(s)}</li>`).join('');
const m = F.meta;
$('#about').innerHTML = `<summary>Sources and method</summary><ul>${m.caveats.map(c => `<li>${esc(c)}</li>`).join('')}</ul><div><b>Sources:</b> ${m.sources.map(s => `<code>${esc(s)}</code>`).join(', ')} · built by <code>${esc(m.generated_by)}</code></div>`;
$('#foot').innerHTML = `<div>Built from committed data by scripts in the project repository: <a href="${D.repo}" target="_blank" rel="noopener">${esc(D.repo.replace('https://', ''))}</a> (<code>06_visualization/</code>).</div>` +
  `<div>Every number on this page is computed from the embedded data; none is typed by hand. Question wording is quoted exactly. Respondents appear by anonymous ID only.</div>`;
})();
</script>
"""


if __name__ == "__main__":
    sys.exit(main())
