#!/usr/bin/env python3
"""p6_build_view_data.py — the Phase 6 data layer: one JSON file per view, built only from committed data (P6.S03).

Outputs: 06_visualization/data/v1_ledger.json … v7_network.json. Every file carries `meta`: the question, the unit, the source
files, the caveats the page must show, and the provenance of what is inferred. Pages read these files and nothing else.
No respondent is given a level or stakeholder type; respondents appear by respid only.
Inputs: Phase 1 (cohorts, dimensions, question map, lexicon, linkages), Phase 2 (variable dictionary), Phase 4 (pairs, T02, T04,
    T06), Phase 5 (corpus, codes, coding frame, index, coded views, concept map, agreement).
Usage: python3 -I scripts/p6_build_view_data.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from p5_build_coding_frame import rows as frame_rows  # noqa: E402

OUT = Path("06_visualization/data")
P1, P2, P4, P5 = Path("01_instrument_reconstruction"), Path("02_data_inventory"), Path("04_analytics_library"), Path("05_open_ended")
ALL = "C-L-ALL-RESPONDENTS"
GATES = ["TARGET", "ACCESS", "AGREE", "VISION", "CASE"]
BEST, WORST = {"Q22", "Q24"}, {"Q23", "Q25"}
SCRIPT = "scripts/p6_build_view_data.py"


def rd(p, **k):
    return pd.read_csv(p, dtype=str, keep_default_na=False, **k)


def f4(x):
    return None if x in ("", None) or pd.isna(x) else round(float(x), 4)


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8")


def meta(view, title, question, unit, sources, caveats, provenance):
    return {"view": view, "title": title, "question": question, "unit": unit, "sources": sources, "caveats": caveats,
            "provenance": provenance, "generated_by": SCRIPT}


def cohort_table():
    coh = rd(P1 / "cohorts.csv").set_index("cohort_id")
    dims = rd(P1 / "cohort_dimensions.csv").set_index("dimension_id")
    return coh, dims


def answers_table():
    corpus = rd(P5 / "corpus.csv").set_index("answer_id")
    idx = rd(P5 / "index/answers_search.csv").set_index("answer_id")
    return corpus, idx


def answer_rec(aid, corpus, idx, codes_by):
    r = corpus.loc[aid]
    return {"id": aid, "respid": r.respid, "item": r["item"], "frame": r.frame, "text": r.text.strip(),
            "vendors": [v for v in idx.loc[aid, "vendors"].split(";") if v], "people": [v for v in idx.loc[aid, "people"].split(";") if v],
            "roles": [v for v in idx.loc[aid, "roles"].split(";") if v], "codes": codes_by.get(aid, [])}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    coh, dims = cohort_table()
    corpus, idx = answers_table()
    codes = rd(P5 / "codes.csv")
    codes_by = {a: [c + p for c, p in zip(g.code, g.polarity)] for a, g in codes.groupby("answer_id", sort=True)}
    frame = {r["code"]: r for r in frame_rows()}
    agree = rd(P5 / "coding/agreement.csv")
    alpha = {(r.layer, r.measure): float(r.alpha) for r in agree.itertuples()}
    pairs = rd(P4 / "pairs.csv").set_index("pair_id")

    # ---- V1 ledger -----------------------------------------------------------------------------------------------
    t4 = rd(P4 / "outputs/T04/value_vs_experience.csv")
    v1 = []
    for pid, g in t4.groupby("pair_id", sort=False):
        p = pairs.loc[pid]
        rows = []
        for r in g.itertuples():
            rows.append({"cohort": r.cohort, "label": coh.loc[r.cohort, "label"], "dimension": dims.loc[r.dimension, "name"] if r.dimension in dims.index else "All",
                         "n": int(coh.loc[r.cohort, "n"]), "a": f4(r.a_value), "b": f4(r.b_value), "gap": f4(r.gap),
                         "a_base": f4(r.a_base), "b_base": f4(r.b_base), "usable": r.usable == "True"})
        v1.append({"pair": pid, "type": p.pair_type, "gate": p.gate, "concept": p.concept, "a_label": p.a_label, "b_label": p.b_label,
                   "a_measures": p.a_measures, "b_measures": p.b_measures, "rationale": p.rationale, "cohorts": rows})
    write("v1_ledger.json", {"meta": meta(
        "V1", "The two-sided ledger", "Where do customers get more than they value, and where less?", "concept pair × cohort",
        ["04_analytics_library/outputs/T04/value_vs_experience.csv", "04_analytics_library/pairs.csv", "01_instrument_reconstruction/cohorts.csv"],
        ["Group-level: each value is the share of a cohort, not of a person.",
         "Cohorts below n = 25 are listed but not compared (usable = false).",
         "Pairs P01–P07 set what decision-makers value against what they receive; C01–C02 set what salespeople know about themselves against what they know about the customer.",
         "Gap = b − a. For value-vs-experience pairs: received − valued."],
        "Pairs are Claude's inference (INFERRED), confirmed by Scott 2026-10-30 (Q-P4a). Values RECON_DATA via T04."), "pairs": v1})

    # ---- V2 cohort grid ----------------------------------------------------------------------------------------------
    s = rd(P4 / "outputs/T02/summary_measures.csv")
    s = s[s.role == "headline"]
    vd = rd(P2 / "variable_dictionary.csv").set_index("variable")
    meas = s[s.cohort == ALL][["measure", "gate", "item", "thread"]].drop_duplicates()
    meas["gi"] = meas.gate.map({g: i for i, g in enumerate(GATES)})
    meas = meas.sort_values(["gi", "item", "measure"])
    mlist = [{"id": m.measure, "gate": m.gate, "item": m["item"], "thread": m.thread,
              "label": vd.loc[m.measure, "label"] if m.measure in vd.index else m.measure,
              "item_wording": vd.loc[m["item"], "label"] if m["item"] in vd.index else ""} for _, m in meas.iterrows()]
    allv = s[s.cohort == ALL].set_index("measure")
    cohorts = [c for c in s.cohort.unique() if c != ALL]
    dorder = [d for d in dims.index if d in {coh.loc[c, "dimension_id"] for c in cohorts}]
    clist = []
    for d in dorder:
        for c in sorted((c for c in cohorts if coh.loc[c, "dimension_id"] == d), key=lambda c: coh.loc[c, "label"]):
            clist.append({"id": c, "label": coh.loc[c, "label"], "dimension": dims.loc[d, "name"], "n": int(coh.loc[c, "n"]),
                          "usable": int(coh.loc[c, "n"]) >= 25})
    sv = s.set_index(["cohort", "measure"])
    cells = []
    for c in clist:
        row = []
        for m in mlist:
            if (c["id"], m["id"]) in sv.index:
                r = sv.loc[(c["id"], m["id"])]
                row.append([f4(r.value), f4(r.base), r.usable == "True"])
            else:
                row.append(None)
        cells.append(row)
    write("v2_cohort_grid.json", {"meta": meta(
        "V2", "Gate × cohort explorer", "At which gate does each cohort's experience differ from everyone's?", "cohort × headline measure",
        ["04_analytics_library/outputs/T02/summary_measures.csv", "02_data_inventory/variable_dictionary.csv",
         "01_instrument_reconstruction/cohorts.csv", "01_instrument_reconstruction/cohort_dimensions.csv"],
        ["Group-level only. A difference shown here is not a significance test (T03 holds the tests).",
         "A cohort or item base below n = 25 is shown but not compared.",
         "Target has no headline measures: its questions are the screeners that define the cohorts."],
        "Values RECON_DATA via T02; headline measures confirmed by Scott (P4.S01)."),
        "all": {m["id"]: f4(allv.loc[m["id"], "value"]) for m in mlist}, "measures": mlist, "cohorts": clist,
        "cell_fields": ["value", "base", "usable"], "cells": cells})

    # ---- V3 silent gap; V4 wins/loses (+ the answers they open) ------------------------------------------------------
    links = rd(P5 / "t04_concept_links.csv").set_index("pair_id")
    tl = rd(P5 / "views/coded/t04_link.csv")
    allc = codes[codes.layer.isin(["behaviour", "lexicon"])]
    used = set()
    v3 = []
    for r in tl.itertuples():
        cs = links.loc[r.pair_id, "codes"].split(";")
        ids = sorted(set(allc[allc.code.isin(cs)].answer_id))
        used |= set(ids)
        v3.append({"pair": r.pair_id, "concept": r.concept, "gate": r.gate, "gap": f4(r.gap_all), "answers": int(r.answers),
                   "q21": int(r.q21_criterion), "best_pos": int(r.best_pos), "worst_neg": int(r.worst_neg),
                   "codes": cs, "code_labels": [frame[c]["label"] for c in cs], "answer_ids": ids})
    k = rd(P5 / "views/coded/kano.csv")
    beh = codes[codes.layer == "behaviour"]
    v4 = []
    for r in k.itertuples():
        g = beh[beh.code == r.behaviour]
        bi = sorted(set(g[g["item"].isin(BEST) & (g.polarity == "+")].answer_id))
        wi = sorted(set(g[g["item"].isin(WORST) & (g.polarity == "-")].answer_id))
        used |= set(bi) | set(wi)
        v4.append({"code": r.behaviour, "label": frame[r.behaviour]["label"], "definition": frame[r.behaviour]["definition"],
                   "class": r.kano, "effective": int(r._2), "ineffective": int(r._3), "experiential": int(r.experiential),
                   "q21": int(r.q21_criterion), "best_ids": bi, "worst_ids": wi})
    sub = {a: answer_rec(a, corpus, idx, codes_by) for a in sorted(used)}
    write("v3_silent_gap.json", {"meta": meta(
        "V3", "The silent gap", "Which gaps do customers feel but not say?", "concept pair; open-ended answer",
        ["05_open_ended/views/coded/t04_link.csv", "05_open_ended/t04_concept_links.csv", "05_open_ended/codes.csv", "05_open_ended/corpus.csv"],
        ["The gap is group-level (T04, All respondents, n = 319).",
         "Answers are linked to a pair by concept, through the codes mapped to it — never by person: the open-ended answers carry no level or stakeholder type.",
         f"Codes are one coder's, checked blind on 200 answers (behaviour alpha {alpha[('behaviour', 'presence of each code')]:.2f}; lexicon {alpha[('lexicon', 'presence of each code')]:.2f}, usable with caution)."],
        "Concept map Claude's (INFERRED), confirmed by Scott 2026-10-30. Answers VERBATIM."), "points": v3, "answers": {a: sub[a] for a in sorted({i for p in v3 for i in p["answer_ids"]})}})
    write("v4_wins_loses.json", {"meta": meta(
        "V4", "What wins, what loses", "Which behaviours win accounts and which lose them?", "open-ended answer",
        ["05_open_ended/views/coded/kano.csv", "05_open_ended/codes.csv", "05_open_ended/coding_frame.md", "05_open_ended/corpus.csv"],
        ["Effective = coded + in a best account (Q22, Q24); ineffective = coded − in a worst account (Q23, Q25).",
         "Class (Johnston 1995 rule, adapted): of ≥ 10 experiential mentions, ≥ 2/3 ineffective = dissatisfier; ≥ 2/3 effective = satisfier; ≥ 1/4 each = critical; else neutral.",
         f"Codes are one coder's, checked blind on 200 answers (behaviour alpha {alpha[('behaviour', 'presence of each code')]:.2f})."],
        "Codes INFERRED. Answers VERBATIM."), "behaviours": v4,
        "answers": {a: sub[a] for a in sorted({i for b in v4 for i in b["best_ids"] + b["worst_ids"]})}})

    # ---- V5 vocabularies ----------------------------------------------------------------------------------------------
    lex = rd(P1 / "asymmetry_lexicon.csv")
    p2 = rd(P5 / "views/coded/lexicon_pass2.csv").set_index("entry_id")
    v5 = []
    for r in lex.itertuples():
        q = p2.loc[r.entry_id]
        v5.append({"id": r.entry_id, "gate": r.group, "concept": r.concept, "vendor_term": r.vendor_term,
                   "customer_term": "" if r.gap else r.decision_maker_words, "customer_cites": r.decision_maker_cites,
                   "gap": r.gap, "gap_name_by_scott": r.gap_name_by_scott, "answers": int(q.answers), "best": int(q.best), "worst": int(q.worst),
                   "top_words": [w.rsplit(" ", 1)[0] for w in q.top_words.split("; ")] if q.top_words else [], "example": q.example})
    write("v5_vocabularies.json", {"meta": meta(
        "V5", "Two vocabularies", "Where does the vendor have a word and the customer none?", "lexicon concept",
        ["01_instrument_reconstruction/asymmetry_lexicon.csv", "05_open_ended/views/coded/lexicon_pass2.csv"],
        ["Vendor terms are Claude's (INFERRED); customer wording is the instrument's (VERBATIM).",
         f"Answer words are the most frequent content words in answers carrying the concept (lexicon alpha {alpha[('lexicon', 'presence of each code')]:.2f}, usable with caution).",
         "A gap is a concept with no customer-side word in the instrument; naming it is Scott's (Q-S10a)."],
        "Mixed, per field as stated."), "rows": v5})

    # ---- V6 search ----------------------------------------------------------------------------------------------------
    allrec = [answer_rec(a, corpus, idx, codes_by) for a in corpus.index]
    write("v6_search.json", {"meta": meta(
        "V6", "Search the customers' words", "What did decision-makers say about a vendor, a person, a role or a behaviour?", "open-ended answer",
        ["05_open_ended/corpus.csv", "05_open_ended/index/answers_search.csv", "05_open_ended/codes.csv", "05_open_ended/coding_frame.md"],
        ["Answers exactly as given; respondents by anonymous respid only, with no level or stakeholder type.",
         "Vendor counts are mentions, not ratings: a large vendor is named more often in both best and worst lists.",
         "Names are kept on Scott's instruction (D5-4); vendor and person matching uses authored lists (INFERRED)."],
        "Answers VERBATIM; vendor, person and role matches INFERRED; codes INFERRED."),
        "code_labels": {c: frame[c]["label"] for c in sorted(frame)}, "answers": allrec})

    # ---- V7 network ---------------------------------------------------------------------------------------------------
    tm = rd(P4 / "outputs/T06/thread_metrics.csv")
    tm = tm[tm.view == "all"].set_index("thread")
    qm = rd(P1 / "question_map.csv")
    stem = qm.groupby("thread_id").stem.first()
    lk = rd(P1 / "linkages.csv")
    lk = lk[(lk.level == "thread") & lk.source.isin(tm.index) & lk.target.isin(tm.index) & (lk.source != lk.target)]
    nodes = [{"id": t, "gate": tm.loc[t, "gate"], "wording": stem.get(t, ""), "neighbours": int(tm.loc[t, "neighbours"]),
              "betweenness": f4(tm.loc[t, "betweenness"])} for t in sorted(tm.index)]
    edges = [{"source": r.source, "target": r.target, "type": r.link_type, "weight": f4(r.weight), "evidence": r.evidence,
              "provenance": r.provenance} for r in lk.itertuples()]
    write("v7_network.json", {"meta": meta(
        "V7", "Thread network", "Which questions are linked, and how do the links cross the gates?", "thread (question)",
        ["01_instrument_reconstruction/linkages.csv", "04_analytics_library/outputs/T06/thread_metrics.csv", "01_instrument_reconstruction/question_map.csv"],
        ["Links are defined by the instrument (P1 linkage inventory), not computed from answers.",
         "Breakout, grouping and same-respondent links describe structure, not content; the view shows them on request.",
         "Statistical links between threads (T07) are group-level — the ecological caveat applies."],
        "Links RECON_DATA or INFERRED per edge (provenance field)."), "nodes": nodes, "edges": edges})

    # ---- V0 context: who was asked what (read by every page) ------------------------------------------------------------
    import re as _re
    di = (P1 / "design_intent.md").read_text(encoding="utf-8")
    gates = []
    for g in ["Target", "Access", "Agree", "Vision", "Case"]:
        m = _re.search(r"\| \*\*" + g + r"\*\* \| \"(.+?)\" \|", di)
        gates.append({"gate": g.upper(), "name": g, "scott_definition": m.group(1) if m else ""})
    def n_of(c):
        return int(coh.loc[c, "n"])
    lev = [c for c in coh.index if coh.loc[c, "dimension_id"] == "D-LEVEL"]
    stems = {}
    for t in ["T-Q08", "T-Q11", "T-Q12", "T-Q13", "T-Q14", "T-Q18", "T-Q19", "T-Q21", "T-Q22", "T-Q23", "T-Q24", "T-Q25"]:
        stems[t.replace("T-", "")] = qm[qm.thread_id == t].stem.iloc[0]
    v0 = {"meta": meta("V0", "Study context", "Who was asked, and what?", "study",
                       ["01_instrument_reconstruction/cohorts.csv", "01_instrument_reconstruction/question_map.csv",
                        "01_instrument_reconstruction/design_intent.md", "05_open_ended/corpus.csv", "05_open_ended/codes.csv"],
                       ["The study date is excluded from analysis by design."],
                       "Counts RECON_DATA; question wording VERBATIM; gate definitions RECALL_DESIGNER (Scott)."),
          "respondents": n_of(ALL), "it_decision_makers": n_of("C-FUNCTION-ITDM"), "business_decision_makers": n_of("C-FUNCTION-BDM"),
          "levels": [{"label": coh.loc[c, "label"], "n": n_of(c)} for c in lev],
          "written_answers": int(len(corpus)), "codable_answers": int(codes[codes.layer == "valence"].answer_id.nunique()),
          "question_stems": stems, "gates": gates}
    write("v0_context.json", v0)

    # ---- Findings for the argument page: single questions read directly (Scott's review, 2026-10-30) -----------------
    gp = rd(P4 / "outputs/T01/gate_profile.csv")
    gp = gp[gp.cohort == ALL]
    qtype = dict(zip(qm.item_id, qm.question_type))
    def question(thread, items, choose, keep=None):
        out = []
        for it in items:
            x = gp[gp["item"] == it].copy()
            x["o"] = pd.to_numeric(x.option, errors="coerce").fillna(0)
            x = x.sort_values("o")
            opts = [{"label": r.option_label, "share": f4(r.share)} for r in x.itertuples() if keep is None or keep(r.option_label)]
            out.append({"item": it, "label": vd.loc[it, "label"] if it in vd.index else it, "gate": x.gate.iloc[0],
                        "base": int(float(x.base.iloc[0])), "type": qtype.get(it, ""), "options": opts})
        return {"thread": thread, "stem": stem.get("T-" + thread, ""), "choose": choose, "items": out}
    q14 = question("Q14", ["Q14"], "one")
    q18 = question("Q18", ["Q18"], "one")
    q11 = question("Q11", [f"Q11_{i}" for i in range(1, 7)], "several", keep=lambda l: True)
    q15 = question("Q15", [f"Q15_{i}" for i in range(1, 7)], "several")
    q8 = question("Q08", [f"Q8_{i}" for i in range(1, 8)], "frequency")
    picks = rd(Path("06_visualization/quote_picks.csv"))
    quotes = [{"finding": r.finding, "why": r.why, **answer_rec(r.answer_id, corpus, idx, codes_by)} for r in picks.itertuples()]
    kk = rd(P5 / "views/coded/kano.csv")
    beh_rank = [{"code": r.behaviour, "label": frame[r.behaviour]["label"], "praised_best": int(r._2), "criticised_worst": int(r._3),
                 "q21": int(r.q21_criterion), "class": r.kano} for r in kk.itertuples()]
    write("findings.json", {"meta": meta(
        "F", "Findings: single questions read directly", "What do decision-makers say vendors focus on, what does it cost, and how low is the bar?",
        "share of all respondents (n = 319) per answer; or number of written answers",
        ["04_analytics_library/outputs/T01/gate_profile.csv", "01_instrument_reconstruction/question_map.csv", "02_data_inventory/variable_dictionary.csv",
         "05_open_ended/views/coded/kano.csv", "06_visualization/quote_picks.csv", "05_open_ended/corpus.csv"],
        ["Each chart reads one question as asked; no result is subtracted from another question's result.",
         "Shares are of all 319 respondents (group-level); one-answer questions add to 100%, pick-several questions do not.",
         "Quotes are verbatim; which quotes to show was chosen by Claude (06_visualization/quote_picks.csv).",
         "Behaviour counts are written answers coded by one coder, checked blind on 200 answers (behaviour alpha 0.87)."],
        "Question wording VERBATIM; shares RECON_DATA; quote selection and behaviour codes INFERRED."),
        "respondents": int(coh.loc[ALL, "n"]), "codable_answers": int(codes[codes.layer == "valence"].answer_id.nunique()),
        "q14": q14, "q11": q11, "q8": q8, "q18": q18, "q15": q15, "behaviours": beh_rank, "quotes": quotes})

    print(f"v1 pairs={len(v1)}; v2 {len(clist)}×{len(mlist)}; v3 points={len(v3)}; v4 behaviours={len(v4)}; answers linked={len(sub)}; "
          f"v5 rows={len(v5)}; v6 answers={len(allrec)}; v7 {len(nodes)} nodes / {len(edges)} edges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
