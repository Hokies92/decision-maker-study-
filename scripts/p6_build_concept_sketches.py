#!/usr/bin/env python3
"""p6_build_concept_sketches.py — the Phase 6 concept sheet: one static sketch per candidate view, drawn from committed data.

Inputs (all committed): 04_analytics_library/outputs/T04/value_vs_experience.csv, T02/summary_measures.csv,
    01_instrument_reconstruction/cohorts.csv, asymmetry_lexicon.csv, linkages.csv, 04_analytics_library/outputs/T06/
    thread_metrics.csv, 05_open_ended/views/coded/{t04_link,kano,lexicon_pass2}.csv, 05_open_ended/index/{vendor_index,
    answers_search}.csv, 05_open_ended/codes.csv.
Outputs in 06_visualization/concepts/: V1.svg … V4.svg, V7.svg (themable: light / dark by prefers-color-scheme),
    concepts.html (the whole sheet, self-contained), sketch_numbers.csv (every number a sketch shows, with its source);
    06_visualization/concepts.md (the sheet for GitHub, linking the SVGs). V5 and V6 are tables, drawn in HTML and Markdown.
These are sketches for Scott's review (P6.S02), not the views: no interaction, no layout polish.
Usage: python3 -I scripts/p6_build_concept_sketches.py
"""
import html
import sys
from pathlib import Path

import networkx as nx
import pandas as pd

OUT = Path("06_visualization/concepts")
MD = Path("06_visualization/concepts.md")
A4, P5 = Path("04_analytics_library/outputs"), Path("05_open_ended")
ALL = "C-L-ALL-RESPONDENTS"
GATES = ["TARGET", "ACCESS", "AGREE", "VISION", "CASE"]
NUMS = []
LAB3 = {"C01": (-12, 4, "end"), "P01": (12, 4, "start"), "C02": (-12, 4, "end"), "P03": (-12, 4, "end"), "P02": (0, 20, "middle")}
HIDE7 = {"breakout_of", "in_group", "same_respondents"}          # (view, label, value, source) — every number shown

STYLE = """<style>
.dv{--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--axis:#c3c2b7;
--s1:#2a78d6;--s2:#eb6834;--neg:#e34948;--mid:#f0efec;
--d-3:#184f95;--d-2:#2a78d6;--d-1:#86b6ef;--d0:#f0efec;--d1:#f2a3a2;--d2:#e34948;--d3:#a32b2b;--na:#e1e0d9}
@media (prefers-color-scheme: dark){:root:where(:not([data-theme="light"])) .dv,:root.dv:where(:not([data-theme="light"])){--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;
--muted:#898781;--grid:#2c2c2a;--axis:#383835;--s1:#3987e5;--s2:#d95926;--neg:#e66767;--mid:#383835;
--d-3:#86b6ef;--d-2:#3987e5;--d-1:#1c5cab;--d0:#383835;--d1:#8a3333;--d2:#e66767;--d3:#f2a3a2;--na:#2c2c2a}}
:root[data-theme="dark"] .dv{--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;
--s1:#3987e5;--s2:#d95926;--neg:#e66767;--mid:#383835;--d-3:#86b6ef;--d-2:#3987e5;--d-1:#1c5cab;--d0:#383835;--d1:#8a3333;
--d2:#e66767;--d3:#f2a3a2;--na:#2c2c2a}
.dv{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:12px}
.dv .bg{fill:var(--surface)} .dv .t{fill:var(--ink)} .dv .t2{fill:var(--ink2)} .dv .m{fill:var(--muted)}
.dv .g{stroke:var(--grid);stroke-width:1} .dv .ax{stroke:var(--axis);stroke-width:1}
.dv .s1{fill:var(--s1)} .dv .s2{fill:var(--s2)} .dv .neg{fill:var(--neg)} .dv .ln{stroke:var(--ink2);stroke-width:2}
.dv .ring{stroke:var(--surface);stroke-width:2} .dv .edge{stroke:var(--ink2);stroke-opacity:.18;fill:none}
.dv .b{font-weight:600}
</style>"""


def esc(s):
    return html.escape(str(s), quote=True)


def svg(name, w, h, body, title):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" class="dv" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
         f'aria-label="{esc(title)}">{STYLE}<rect class="bg" width="{w}" height="{h}"/>{body}</svg>')
    (OUT / f"{name}.svg").write_text(s + "\n", encoding="utf-8")
    return s


def txt(x, y, s, cls="t", anchor="start", size=None, extra=""):
    fs = f' font-size="{size}"' if size else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{fs}{extra}>{esc(s)}</text>'


def num(view, label, value, source):
    NUMS.append({"view": view, "label": label, "value": value, "source": source})
    return value


# ---------------------------------------------------------------------------------------------------------- V1
def v1():
    src = "04_analytics_library/outputs/T04/value_vs_experience.csv"
    t = pd.read_csv(src, dtype={"pair_id": str})
    t = t[t.cohort == ALL].sort_values("gap").reset_index(drop=True)
    W, L, R, top, rh = 760, 300, 690, 46, 34
    H = top + rh * len(t) + 40
    x = lambda v: L + v * (R - L)
    b = [txt(16, 22, "Valued vs received, All respondents (T04)", "t b", size=14)]
    b += [f'<circle cx="{L}" cy="34" r="5" class="s1"/>', txt(L + 10, 38, "valued", "t2"),
          f'<circle cx="{L + 80}" cy="34" r="5" class="s2"/>', txt(L + 90, 38, "received", "t2")]
    for v in (0, .25, .5, .75, 1):
        b.append(f'<line x1="{x(v)}" y1="{top - 4}" x2="{x(v)}" y2="{top + rh * len(t)}" class="g"/>')
        b.append(txt(x(v), top + rh * len(t) + 16, f"{v:.0%}", "m", "middle"))
    for i, r in t.iterrows():
        y = top + rh * i + rh / 2
        a, c = float(r.a_value), float(r.b_value)
        num("V1", f"{r.pair_id} valued", a, src); num("V1", f"{r.pair_id} received", c, src); num("V1", f"{r.pair_id} gap", float(r.gap), src)
        b.append(txt(L - 12, y + 4, f"{r.concept}", "t", "end"))
        b.append(txt(L - 12, y + 16, f"{r.pair_id} · {r.gate}", "m", "end", 10))
        b.append(f'<line x1="{x(a)}" y1="{y}" x2="{x(c)}" y2="{y}" class="ln"/>')
        b.append(f'<circle cx="{x(a)}" cy="{y}" r="6" class="s1 ring"/>')
        b.append(f'<circle cx="{x(c)}" cy="{y}" r="6" class="s2 ring"/>')
        b.append(txt(max(x(a), x(c)) + 12, y + 4, f"{float(r.gap):+.2f}", "t2"))
    b.append(txt(16, H - 8, "Gap = received − valued. Negative: customers get less than they value. Source: T04, cohort All (n = 319).", "m", size=10))
    return svg("V1", W, H, "".join(b), "Valued vs received per concept"), t


# ---------------------------------------------------------------------------------------------------------- V2
def v2():
    src = "04_analytics_library/outputs/T02/summary_measures.csv"
    s = pd.read_csv(src)
    s = s[s.role == "headline"]
    coh = pd.read_csv("01_instrument_reconstruction/cohorts.csv").set_index("cohort_id")
    allv = s[s.cohort == ALL].set_index("measure").value
    meas = s[s.cohort == ALL][["measure", "gate", "item"]].drop_duplicates()
    meas["gi"] = meas.gate.map({g: i for i, g in enumerate(GATES)})
    meas = meas.sort_values(["gi", "item", "measure"]).reset_index(drop=True)
    dims = pd.read_csv("01_instrument_reconstruction/cohort_dimensions.csv").set_index("dimension_id")
    cohorts = [c for c in s.cohort.unique() if c != ALL]
    dorder = [d for d in dims.index if d in {coh.loc[c, "dimension_id"] for c in cohorts}]
    order = []                                  # rows: ("dim", id) header or ("coh", id)
    for d in dorder:
        order.append(("dim", d))
        order += [("coh", c) for c in sorted((c for c in cohorts if coh.loc[c, "dimension_id"] == d), key=lambda c: coh.loc[c, "label"])]
    usable = {c: int(coh.loc[c, "n"]) >= 25 for c in cohorts}
    ok = s.set_index(["cohort", "measure"]).usable
    cw, rh, L, top = 13, 12, 290, 70
    W = L + cw * len(meas) + 30
    H = top + rh * len(order) + 56
    bins = [-.15, -.09, -.03, .03, .09, .15]
    def cls(d):
        if d < bins[0]: return "--d-3"
        if d < bins[1]: return "--d-2"
        if d < bins[2]: return "--d-1"
        if d <= bins[3]: return "--d0"
        if d <= bins[4]: return "--d1"
        if d <= bins[5]: return "--d2"
        return "--d3"
    b = [txt(16, 22, "Each cohort against All, headline measure by measure, grouped by gate (T02)", "t b", size=14)]
    for g in GATES:
        cols = meas.index[meas.gate == g]
        if len(cols):
            x0 = L + cw * cols.min()
            b.append(txt(x0, top - 22, g, "t2 b", size=11))
            b.append(f'<line x1="{x0}" y1="{top - 16}" x2="{L + cw * (cols.max() + 1) - 2}" y2="{top - 16}" class="ax"/>')
    val = s.set_index(["cohort", "measure"]).value
    for i, (kind, c) in enumerate(order):
        y = top + rh * i
        if kind == "dim":
            b.append(txt(16, y + 10, dims.loc[c, "name"], "t b", size=10))
            continue
        lab = f"{coh.loc[c, 'label']} (n = {int(coh.loc[c, 'n'])})"
        b.append(txt(L - 8, y + 9, lab, "t2" if usable[c] else "m", "end", 10))
        for j, mrow in meas.iterrows():
            v = val.get((c, mrow.measure))
            if pd.isna(v) or not usable[c] or not bool(ok.get((c, mrow.measure), False)):
                fill = "var(--na)"
            else:
                d = float(v) - float(allv[mrow.measure])
                fill = f"var({cls(d)})"
            if fill == "var(--na)":       # not compared: outline only, so it never reads as "within 3"
                b.append(f'<rect x="{L + cw * j + .5}" y="{y + .5}" width="{cw - 3}" height="{rh - 3}" rx="2" fill="none" stroke="var(--axis)"/>')
            else:
                b.append(f'<rect x="{L + cw * j}" y="{y}" width="{cw - 2}" height="{rh - 2}" rx="2" fill="{fill}"/>')
    num("V2", "cohorts shown", len(cohorts), src); num("V2", "cohorts usable (n ≥ 25)", sum(usable.values()), "01_instrument_reconstruction/cohorts.csv")
    num("V2", "headline measures", len(meas), src)
    ly = H - 34
    keys = [("--d-3", "≥15 below"), ("--d-2", "9–15 below"), ("--d-1", "3–9 below"), ("--d0", "within 3"), ("--d1", "3–9 above"),
            ("--d2", "9–15 above"), ("--d3", "≥15 above"), ("--na", "n < 25 / none")]
    xk = 16
    for k, lab in keys:
        sw = 'fill="none" stroke="var(--axis)"' if k == "--na" else f'fill="var({k})"'
        b.append(f'<rect x="{xk}" y="{ly}" width="12" height="12" rx="2" {sw}/>'); b.append(txt(xk + 16, ly + 10, lab, "t2", size=10))
        xk += 24 + 6 * len(lab)
    b.append(txt(16, H - 8, "Cell = cohort value − All value, in share points. Outlined: cohort or item base below n = 25, or no value — shown, never compared. Group-level only.", "m", size=10))
    return svg("V2", W, H, "".join(b), "Cohort by measure heat grid")


# ---------------------------------------------------------------------------------------------------------- V3
def v3():
    src = "05_open_ended/views/coded/t04_link.csv"
    t = pd.read_csv(src, dtype={"pair_id": str})
    W, H, L, R, T, B = 760, 420, 80, 720, 50, 360
    xmin, xmax, ymax = -0.6, 0.6, 250
    x = lambda v: L + (v - xmin) / (xmax - xmin) * (R - L)
    y = lambda v: B - v / ymax * (B - T)
    b = [txt(16, 22, "Felt vs said: structured gap against how often customers raise it in free text", "t b", size=14)]
    for v in (-0.6, -0.3, 0, 0.3, 0.6):
        b.append(f'<line x1="{x(v)}" y1="{T}" x2="{x(v)}" y2="{B}" class="{"ax" if v == 0 else "g"}"/>')
        b.append(txt(x(v), B + 16, f"{v:+.1f}" if v else "0", "m", "middle"))
    for v in (0, 50, 100, 150, 200, 250):
        b.append(f'<line x1="{L}" y1="{y(v)}" x2="{R}" y2="{y(v)}" class="g"/>'); b.append(txt(L - 8, y(v) + 4, v, "m", "end"))
    b.append(txt((L + R) / 2, B + 34, "gap: received − valued (T04, All)", "t2", "middle"))
    b.append(txt(16, (T + B) / 2, "answers", "t2", extra=f' transform="rotate(-90 26 {(T + B) / 2})"'))
    for r in t.itertuples():
        num("V3", f"{r.pair_id} gap", float(r.gap_all), src); num("V3", f"{r.pair_id} answers", int(r.answers), src)
        cx, cy = x(r.gap_all), y(r.answers)
        b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" class="s1 ring"/>')
        dx, dy, anc = LAB3.get(r.pair_id, (0, -12, "middle"))
        b.append(txt(cx + dx, cy + dy, f"{r.pair_id} {r.concept}" if r.pair_id in ("P05", "P07") else r.pair_id, "t" if r.pair_id in ("P05", "P07") else "t2", anc, 11))
    b.append(txt(16, H - 8, "Answers = open-ended answers carrying the codes linked to the pair (t04_concept_links.csv, INFERRED). Concept-level link, not by person.", "m", size=10))
    return svg("V3", W, H, "".join(b), "Structured gap vs open-ended mentions")


# ---------------------------------------------------------------------------------------------------------- V4
def v4():
    src = "05_open_ended/views/coded/kano.csv"
    k = pd.read_csv(src)
    k = k[k.kano != "too few"].sort_values(["experiential", "behaviour"], ascending=[False, True]).reset_index(drop=True)
    W, C, top, rh, half = 760, 470, 54, 20, 200
    H = top + rh * len(k) + 40
    mx = max(k["best+"].max(), k["worst-"].max())
    sc = lambda v: v / mx * half
    b = [txt(16, 22, "What wins, what loses: behaviour in worst accounts (left) and best accounts (right)", "t b", size=14),
         txt(C - 8, 44, "ineffective (worst, −)", "t2", "end", 11), txt(C + 8, 44, "effective (best, +)", "t2", size=11)]
    b.append(f'<line x1="{C}" y1="{top - 4}" x2="{C}" y2="{top + rh * len(k)}" class="ax"/>')
    for i, r in k.iterrows():
        y = top + rh * i
        lab = r.behaviour.replace("B-", "").replace("-", " ").lower()
        b.append(txt(16, y + 13, lab, "t"))
        b.append(txt(170, y + 13, r.kano, "m", size=10))
        wn, bp = int(r["worst-"]), int(r["best+"])
        num("V4", f"{r.behaviour} worst−", wn, src); num("V4", f"{r.behaviour} best+", bp, src)
        if wn:
            b.append(f'<rect x="{C - sc(wn):.1f}" y="{y + 3}" width="{sc(wn):.1f}" height="{rh - 6}" rx="3" class="neg"/>')
        if bp:
            b.append(f'<rect x="{C:.1f}" y="{y + 3}" width="{sc(bp):.1f}" height="{rh - 6}" rx="3" class="s1"/>')
        b.append(txt(C - sc(wn) - 6, y + 13, wn, "t2", "end", 10)); b.append(txt(C + sc(bp) + 6, y + 13, bp, "t2", size=10))
    b.append(txt(16, H - 8, "Answers coded with the behaviour. Class (Johnston 1995 rule, adapted): satisfier, dissatisfier, critical, neutral. Behaviour layer alpha 0.87.", "m", size=10))
    return svg("V4", W, H, "".join(b), "Behaviours in best vs worst accounts"), k


# ---------------------------------------------------------------------------------------------------------- V5, V6 tables
def v5():
    lex = pd.read_csv("01_instrument_reconstruction/asymmetry_lexicon.csv", dtype=str, keep_default_na=False)
    p2 = pd.read_csv(P5 / "views/coded/lexicon_pass2.csv", dtype=str, keep_default_na=False).set_index("entry_id")
    rows = []
    for r in lex.itertuples():
        words = "; ".join(w.rsplit(" ", 1)[0] for w in p2.loc[r.entry_id, "top_words"].split("; ")[:4]) if p2.loc[r.entry_id, "top_words"] else ""
        cust = "" if r.gap else r.decision_maker_words.split(" | ")[0]
        rows.append({"Gate": r.group, "Concept": r.concept, "Vendor's word": r.vendor_term,
                     "Customer's word (instrument)": cust if cust else "— none —",
                     "Customers' own words (answers)": words or "—", "answers": p2.loc[r.entry_id, "answers"]})
        num("V5", f"{r.entry_id} answers", int(p2.loc[r.entry_id, "answers"]), "05_open_ended/views/coded/lexicon_pass2.csv")
    return pd.DataFrame(rows)


def v6(vendor="IBM"):
    vi = pd.read_csv(P5 / "index/vendor_index.csv").set_index("vendor")
    a = pd.read_csv(P5 / "index/answers_search.csv", dtype=str, keep_default_na=False)
    c = pd.read_csv(P5 / "codes.csv", dtype=str, keep_default_na=False)
    hit = a[a.vendors.str.split(";").apply(lambda v: vendor in v) & a.item.isin(["Q22", "Q23"])]
    beh = c[(c.layer == "behaviour") & c.answer_id.isin(hit.answer_id)]
    tops = {}
    for fr, items in (("best", ["Q22"]), ("worst", ["Q23"])):
        h = hit[hit.item.isin(items)].copy()
        h["len"] = h.text.str.strip().str.len()
        h = h[(h.len >= 25) & (h.len <= 140)].sort_values("answer_id").head(3)
        tops[fr] = [(r.answer_id, r.respid, r.text.strip(), "; ".join(beh[beh.answer_id == r.answer_id].apply(lambda z: f"{z.code}{z.polarity}", axis=1)))
                    for r in h.itertuples()]
    for k in ("mentions", "best", "worst", "in_q22", "in_q23"):
        num("V6", f"{vendor} {k}", int(vi.loc[vendor, k]), "05_open_ended/index/vendor_index.csv")
    return vendor, vi.loc[vendor], tops


# ---------------------------------------------------------------------------------------------------------- V7
def v7():
    src = "01_instrument_reconstruction/linkages.csv"
    tm = pd.read_csv(A4 / "T06/thread_metrics.csv")
    tm = tm[tm.view == "all"]
    gate = dict(zip(tm.thread, tm.gate))
    lk = pd.read_csv(src)
    lk = lk[(lk.level == "thread") & lk.source.isin(gate) & lk.target.isin(gate) & (lk.source != lk.target)]
    hidden = lk[lk.link_type.isin(HIDE7)]
    lk = lk[~lk.link_type.isin(HIDE7)]
    cols = GATES + sorted({g for g in gate.values() if g not in GATES})
    colx = {g: 90 + i * 120 for i, g in enumerate(cols)}
    per = {g: sorted([t for t in gate if gate[t] == g]) for g in cols}
    rows = max(len(v) for v in per.values())
    W, top, rh = 90 + 120 * len(cols), 60, 18
    H = top + rh * rows + 40
    pos = {t: (colx[g], top + rh * i) for g in cols for i, t in enumerate(per[g])}
    G = nx.Graph()
    for r in lk.itertuples():
        G.add_edge(r.source, r.target)
    b = [txt(16, 22, "Thread network: questions in gate columns, instrument-defined links as arcs (P1 linkage inventory)", "t b", size=14)]
    for g in cols:
        b.append(txt(colx[g], top - 18, g.title(), "t2 b", "middle", 11))
    for u, v in sorted(G.edges()):
        (x1, y1), (x2, y2) = pos[u], pos[v]
        mx_ = (x1 + x2) / 2 + (0 if x1 != x2 else 40)
        b.append(f'<path d="M{x1},{y1} Q{mx_},{(y1 + y2) / 2 - (20 if x1 != x2 else 0)} {x2},{y2}" class="edge"/>')
    for t, (px, py) in pos.items():
        deg = G.degree(t) if t in G else 0
        b.append(f'<circle cx="{px}" cy="{py}" r="{3 + min(deg, 30) / 6:.1f}" class="s1 ring"/>')
        b.append(txt(px + 9, py + 4, t.replace("T-", ""), "t2", size=10))
    num("V7", "threads", len(pos), "04_analytics_library/outputs/T06/thread_metrics.csv"); num("V7", "links drawn", G.number_of_edges(), src)
    num("V7", "links hidden (breakout, grouping, same respondents)", len(hidden), src)
    b.append(txt(16, H - 22, f"Content links only ({', '.join(sorted(lk.link_type.unique()))}). Hidden here: {len(hidden)} breakout, grouping and same-respondent links.", "m", size=10))
    b.append(txt(16, H - 8, "Node size = number of linked threads. Statistical (T07) links would be a second, labelled layer: group-level, ecological.", "m", size=10))
    return svg("V7", W, H, "".join(b), "Thread network by gate")


CONCEPTS = [
    ("V1", "The two-sided ledger", "Where do customers get more than they value, and where less?",
     "`04_analytics_library/outputs/T04/value_vs_experience.csv` (cohort All; 50 usable cohorts available)", "pair (concept) × cohort",
     "Pairs are INFERRED (Q-P4a, for Scott's review). Group-level.",
     "The final view adds a cohort picker; the All-respondents line is always visible for reference."),
    ("V2", "Gate × cohort explorer", "At which gate does each cohort's experience differ from everyone's?",
     "`04_analytics_library/outputs/T02/summary_measures.csv` (headline measures); `01_instrument_reconstruction/cohorts.csv`", "cohort × measure",
     "Cohorts below n = 25 shown grey, never compared. Differences are not tested here (T03 has the tests). Target has no headline measures (screener items).",
     "Final view: hover a cell for the item wording, both values and bases; click a cohort for its full profile."),
    ("V3", "The silent gap", "Which gaps do customers feel but not say?",
     "`05_open_ended/views/coded/t04_link.csv` (from T04 and the codes)", "pair; answers",
     "The structured-to-text link is by concept (authored map, INFERRED), never by person.",
     "Final view: click a point to read the answers behind it."),
    ("V4", "What wins, what loses", "Which behaviours win accounts and which lose them?",
     "`05_open_ended/views/coded/kano.csv`", "answer",
     "Codes INFERRED (one coder, blind-checked: behaviour alpha 0.87). Behaviours with < 10 experiential mentions left out.",
     "Final view: click a behaviour for its verbatims, best and worst."),
    ("V5", "Two vocabularies", "Where does the vendor have a word and the customer none?",
     "`01_instrument_reconstruction/asymmetry_lexicon.csv`; `05_open_ended/views/coded/lexicon_pass2.csv`", "lexicon concept",
     "Vendor terms are Claude's (INFERRED); customer instrument wording VERBATIM; answer words are frequency counts. Lexicon alpha 0.72 (usable with caution).",
     "Final view: gate columns side by side, empty cells drawn as gaps; candidate names from the answers beside each gap for Scott."),
    ("V6", "Search the customers' words", "What did decision-makers say about a vendor, a role or a behaviour?",
     "`05_open_ended/index/answers_search.csv`, `vendor_index.csv`; `05_open_ended/codes.csv`", "answer",
     "Verbatims exactly as given, by respid only. Vendor counts are mentions, not ratings. Names shown (D5-4) — audience decision D6-1 applies.",
     "Final view: one search box plus filters (vendor, person, role, code, best / worst, question)."),
    ("V7", "Thread network", "Which questions are linked, and how do the links cross the gates?",
     "`01_instrument_reconstruction/linkages.csv`; `04_analytics_library/outputs/T06/thread_metrics.csv`", "thread",
     "Instrument-defined links only in the sketch. Statistical links (T07) are group-level — ecological caveat.",
     "Final view: hover a thread for its wording and links; toggle link types; T07 links as a separate layer."),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    s1, t1 = v1(); s2 = v2(); s3 = v3(); s4, k4 = v4(); s7 = v7()
    t5 = v5(); vendor, vrow, tops = v6()
    sv = {"V1": s1, "V2": s2, "V3": s3, "V4": s4, "V7": s7}
    t5_md = ["| Gate | Concept | Vendor's word | Customer's word (instrument) | Customers' own words (answers) | Answers |", "|---|---|---|---|---|---|"]
    for r in t5.itertuples(index=False):
        t5_md.append("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
    t6_md = [f"**Query: vendor = {vendor}** — {int(vrow.mentions)} mentions; Q22 best teams {int(vrow.in_q22)}, Q23 worst teams {int(vrow.in_q23)}.", ""]
    for fr in ("best", "worst"):
        t6_md.append(f"*{fr.title()} teams:*")
        for aid, rid, text, codes in tops[fr]:
            t6_md.append(f"- “{text}” — respid {rid} · `{aid}` · {codes or 'no behaviour code'}")
        t6_md.append("")
    # Markdown sheet
    M = ["# Phase 6 concept sheet (P6.S01)", "",
         "Generated by `scripts/p6_build_concept_sketches.py` from committed data. Do not edit by hand. Sketches for Scott's review "
         "(P6.S02) — static, no interaction. Every number shown is listed with its source in `concepts/sketch_numbers.csv`. "
         "Full sheet with light / dark themes: `concepts/concepts.html`.", ""]
    for cid, name, q, data, unit, cav, final in CONCEPTS:
        M += [f"## {cid} — {name}", "", f"**Question.** {q}", "", f"**Data.** {data} · **Unit:** {unit}", "",
              f"**Caveats.** {cav}", "", f"**In the built view.** {final}", ""]
        if cid in sv:
            M += [f"![{name}](concepts/{cid}.svg)", ""]
        elif cid == "V5":
            M += t5_md + [""]
        else:
            M += t6_md
    M += ["## For Scott at P6.S02", "",
          "- Keep, change or drop each of V1–V7.",
          "- **D6-1 audience** (you only, clients, public) — matters most for V6, which names vendors in worst accounts, and the repo is public.",
          "- **D6-2 delivery** — private shareable pages, HTML in the repo, or both.",
          "- **D6-3 scope and order** — recommended first: V1, V3, V4 (pitch over-delivered; case under-delivered and unspoken; knowledge wins, conduct loses).", ""]
    MD.write_text("\n".join(M), encoding="utf-8")
    # HTML sheet
    def table_html(df):
        h = "<table><thead><tr>" + "".join(f"<th>{esc(c)}</th>" for c in df.columns) + "</tr></thead><tbody>"
        for r in df.itertuples(index=False):
            h += "<tr>" + "".join(f"<td{' class=gap' if x == '— none —' else ''}>{esc(x)}</td>" for x in r) + "</tr>"
        return h + "</tbody></table>"
    H = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
         "<title>Phase 6 concept sheet</title>", STYLE.replace(".dv{", ".dv,body{", 1),
         "<style>body{margin:0;background:var(--surface);color:var(--ink)}main{max-width:820px;margin:0 auto;padding:24px 16px}"
         "h1{font-size:22px}h2{font-size:17px;margin-top:40px}p{line-height:1.5;color:var(--ink2)}b{color:var(--ink)}"
         ".fig{overflow-x:auto;border:1px solid var(--grid);border-radius:8px}.fig svg{display:block;max-width:none}"
         "table{border-collapse:collapse;font-size:12px;width:100%}th,td{border-bottom:1px solid var(--grid);padding:5px 6px;text-align:left;vertical-align:top}"
         "th{color:var(--ink2)}td.gap{color:var(--muted);font-style:italic}.q{border-left:3px solid var(--s1);padding-left:10px}</style></head>",
         '<body class="dv"><main><h1>Phase 6 concept sheet</h1><p>Seven candidate views, each sketched from committed data. '
         "Static sketches for review — the built views add interaction. Generated by <code>scripts/p6_build_concept_sketches.py</code>.</p>"]
    for cid, name, q, data, unit, cav, final in CONCEPTS:
        md2h = lambda s: esc(s).replace("`", "")
        H.append(f"<h2>{cid} — {esc(name)}</h2><p class=q><b>{esc(q)}</b></p><p><b>Data.</b> {md2h(data)} · <b>Unit:</b> {esc(unit)}</p>"
                 f"<p><b>Caveats.</b> {esc(cav)}</p><p><b>In the built view.</b> {esc(final)}</p>")
        if cid in sv:
            H.append(f'<div class="fig">{sv[cid].replace(STYLE, "")}</div>')
        elif cid == "V5":
            H.append(f'<div class="fig">{table_html(t5)}</div>')
        else:
            H.append(f"<p><b>Query: vendor = {esc(vendor)}</b> — {int(vrow.mentions)} mentions; Q22 best teams {int(vrow.in_q22)}, Q23 worst teams {int(vrow.in_q23)}.</p>")
            for fr in ("best", "worst"):
                H.append(f"<p><b>{fr.title()} teams</b></p><ul>" + "".join(
                    f"<li>“{esc(t)}” — respid {esc(r)} · {esc(a)} · {esc(c or 'no behaviour code')}</li>" for a, r, t, c in tops[fr]) + "</ul>")
    H.append("<h2>For Scott</h2><p>Keep, change or drop each view. Decide D6-1 audience, D6-2 delivery, D6-3 scope and order. "
             "Recommended first: V1, V3, V4.</p></main></body></html>")
    (OUT / "concepts.html").write_text("\n".join(H) + "\n", encoding="utf-8")
    pd.DataFrame(NUMS).to_csv(OUT / "sketch_numbers.csv", index=False, lineterminator="\n", float_format="%.4f")
    print(f"concepts={len(CONCEPTS)} svgs={len(sv)} numbers={len(NUMS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
