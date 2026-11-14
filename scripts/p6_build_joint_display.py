#!/usr/bin/env python3
"""p6_build_joint_display.py — the joint display of survey and written results, one row per concept (P6.S11 c).

Four methods, as Scott approved them (2026-10-30; method register QL04, QL06–QL08):
    joint display        one row per concept: the survey result, how often written answers raise it, a quote
                         (Fetters, Curry & Creswell 2013)
    following a thread   from a survey item, through the code, into each written-answer question (Moran-Ellis et al. 2006)
    convergence coding   each concept judged agree / expand / disagree / silent (Farmer et al. 2006)
    pillar integration   survey column -> written column -> one shared statement (Johnson, Grove & Clarke 2019)

A concept is a code of the coding frame in the two concept layers: behaviour (what the salesperson or vendor does, coded
+ / -) and lexicon (the asymmetry lexicon's concepts, M11, coded without direction). The survey side of a concept comes
only from its links in `06_visualization/inventory/concept_links.csv`.

Rules kept here:
  * Joined by concept only, never by respondent (R04). Survey results are All respondents (n = 319), group tables only.
  * No arithmetic across sources (R01, R08): survey shares and written-answer counts sit in separate columns. The one sum
    made here adds the options of a single one-answer question (same stem, same base, options add to 100%) where a T04 pair
    names them together (e.g. Q14 options 1 + 2).
  * Each side is first read on its own terms; the judgement compares the two readings, not the numbers.

Readings (INFERRED rules; Scott reviews them in P6.S12):
  survey   valued items (what decision-makers say they want: vendor qualities Q1, appointment reasons Q7, meeting value
           Q11, differentiators Q13, importance Q19) read 'most' when the share is at least MAJORITY, else 'a minority';
           received items (what they say they get: every other question) read 'common' at MAJORITY or more, else 'uncommon'.
           A stem (whole question) has no single result and is not read.
  written  behaviour codes take their class from the P5 satisfier / dissatisfier rule (cit_behaviours.csv: satisfier,
           dissatisfier, critical, neutral, too few); lexicon codes carry no direction.
Judgement per linked item (the item's own reading against the code's written class):
  valued, most                  -> agree     (both say it matters)
  valued, a minority            -> expand    (the written answers add weight the survey does not show)
  received, direction known     -> common + satisfier = agree; common + dissatisfier = disagree;
                                   uncommon + dissatisfier or critical = agree; uncommon + satisfier = expand;
                                   anything else = expand
  received, no direction        -> expand    (lexicon codes, and links that come only through a lexicon entry)
  opposite polarity             -> a received reading is flipped (the pitch common = putting my needs first uncommon);
                                   a valued reading of the other pole is expand
Concept judgement: silent when one side is absent — no survey link (silent: survey), or fewer than MIN_WRITTEN answers
carry the code (silent: written); otherwise disagree if any item disagrees, agree if agreeing items are at least as many
as expanding ones, else expand. A concept linked only to whole questions is expand (question-level link). An option set
of one question counts once (its single options are listed, not counted). A share within NEAR of MAJORITY is flagged.
MAJORITY is 55% (Scott, P6.S12 decision 2, 2026-11-14: "55%, minimum 10"); MIN_WRITTEN stays 10.

Quote: the coding frame's own example answer for the code (chosen in Phase 5), shown verbatim from the corpus.
Every link, judgement and pillar statement is INFERRED until Scott reviews it (P6.S12).

Inputs: 06_visualization/inventory/concept_links.csv, data_register.csv; 05_open_ended/coding_frame.csv, codes.csv,
        corpus.csv, views/coded/cit_behaviours.csv; 01_instrument_reconstruction/asymmetry_lexicon.csv;
        04_analytics_library/outputs/T01/gate_profile.csv, T02/summary_measures.csv.
Outputs: 06_visualization/joint/joint_display.csv, joint_display.md
Usage: python3 -I scripts/p6_build_joint_display.py
"""
import re
import sys
from pathlib import Path

import pandas as pd

OUT = Path("06_visualization/joint")
ALL = "C-L-ALL-RESPONDENTS"
MAJORITY = 0.55  # Scott, P6.S12 decision 2 (2026-11-14): "55%, minimum 10"; was 0.50 in S11
MIN_WRITTEN = 10  # the P5 satisfier / dissatisfier rule's minimum (MIN_KANO); kept by Scott in P6.S12 decision 2
NEAR = 0.05  # a share within 5 points of the MAJORITY line is flagged for Scott: its reading could tip either way
VALUED = {"vendor qualities", "appointment reasons", "meeting value", "importance-differentiation", "importance"}
DIRECTED_ROUTES = {"frame_source", "t04_pair"}  # routes on which the code and the item share a pole
WRITTEN_ORDER = ["Q21", "Q22", "Q23", "Q24", "Q25"]
PHRASE = {"topbox": "frequently", "differentiator": "important, and a differentiator"}
TOP2 = {"agreement": "agree", "importance": "important", "frequency": "occasionally or frequently"}
ORDER = {"disagree": 0, "agree": 1, "expand": 2, "silent: survey": 3, "silent: written": 4, "silent: both": 5}


def rd(p):
    return pd.read_csv(p, dtype=str, keep_default_na=False)


def pct(x):
    return f"{round(x * 100)}%"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    links = rd("06_visualization/inventory/concept_links.csv")
    reg = rd("06_visualization/inventory/data_register.csv").set_index("field")
    frame = rd("05_open_ended/coding_frame.csv")
    codes = rd("05_open_ended/codes.csv")
    corpus = rd("05_open_ended/corpus.csv").set_index("answer_id")
    cit = rd("05_open_ended/views/coded/cit_behaviours.csv").set_index("behaviour")
    lex = rd("01_instrument_reconstruction/asymmetry_lexicon.csv").set_index("entry_id")
    gp = rd("04_analytics_library/outputs/T01/gate_profile.csv")
    gp = gp[gp.cohort == ALL]
    t02 = rd("04_analytics_library/outputs/T02/summary_measures.csv")
    t02 = t02[t02.cohort == ALL].set_index("measure")

    def family(item):
        if item in reg.index:
            return reg.loc[item, "scale_family"]
        sub = [f for f in reg.index if f.startswith(item + "_")]
        return reg.loc[sub[0], "scale_family"] if sub else ""

    def result(ref):
        """(share, n, phrase, cite) for a survey reference, All respondents; share None for a stem."""
        item = ref.split("__")[0].split(":")[0]
        if ref.endswith(":stem"):
            return None, None, "whole question", "question-level link"
        if "__" in ref:
            r = t02.loc[ref]
            rule = ref.split("__")[1]
            phrase = TOP2.get(family(item), "top two") if rule == "top2" else PHRASE.get(rule, rule)
            return float(r.value), int(r.n), phrase, f"T02 summary_measures.csv {ref}"
        g = gp[gp["item"] == item]
        if ":opt" in ref:
            opts = [float(o) for o in ref.split(":opt")[1].split("+")]
            rows = g[pd.to_numeric(g.option, errors="coerce").isin(opts)]
            if len(rows) != len(opts):
                raise SystemExit(f"ERROR: options of {ref} not all in T01")
            return (float(pd.to_numeric(rows.share).sum()), int(rows.n.iloc[0]), "gave this answer",
                    "T01 gate_profile.csv " + "; ".join(rows.cite))
        if len(g) != 1:
            raise SystemExit(f"ERROR: {ref} has {len(g)} rows in T01")
        return float(g.share.iloc[0]), int(g.n.iloc[0]), "chose it", f"T01 gate_profile.csv {g.cite.iloc[0]}"

    def option_labels(ref):
        item = ref.split(":")[0]
        opts = [float(o) for o in ref.split(":opt")[1].split("+")]
        g = gp[(gp["item"] == item) & pd.to_numeric(gp.option, errors="coerce").isin(opts)]
        return " / ".join(x.strip() for x in g.option_label)

    # ---- written side ------------------------------------------------------------------------------------------------
    concept_frame = frame[frame.layer.isin(["behaviour", "lexicon"])]
    rows = []
    for f in concept_frame.itertuples():
        code = f.code
        label = f.label if f.layer == "behaviour" else lex.loc[code, "concept"]
        cw = codes[codes.code == code]
        n_written = int(cw.answer_id.nunique())
        byq = cw.groupby("item").answer_id.nunique()
        main_q = [f"{q} {int(byq[q])}" for q in WRITTEN_ORDER if q in byq.index]
        other = int(byq[[q for q in byq.index if q not in WRITTEN_ORDER]].sum()) if len(byq) else 0
        by_question = "; ".join(main_q + ([f"other-specify {other}"] if other else []))
        if f.layer == "behaviour" and code in cit.index:
            c = cit.loc[code]
            best, worst, cls = int(c["best+"]), int(c["worst-"]), c.kano
        else:
            best, worst, cls = "", "", "no direction" if f.layer == "lexicon" else "not coded"
        ex = re.search(r"example ([A-Za-z0-9_]+-R\d+)", f.source)
        qid = ex.group(1) if ex and ex.group(1) in corpus.index else ""
        quote = corpus.loc[qid, "text"].strip() if qid else ""
        if qid and not ((codes.answer_id == qid) & (codes.code == code)).any():
            print(f"ERROR: example {qid} does not carry {code}", file=sys.stderr)
            return 2

        # ---- survey side and item judgements -------------------------------------------------------------------------
        L = links[links.code == code].drop_duplicates("survey_ref")
        # an option set of one question (T04, e.g. Q14:opt3+4+5) counts once: its single options are listed, not counted
        sets = [r_.split(":opt") for r_ in L.survey_ref if ":opt" in r_ and "+" in r_]
        in_set = {f"{q}:opt{o}" for q, os_ in sets for o in os_.split("+")}
        items, judgements, readings, cites, gates, near = [], [], [], [], [], []
        for lk in L.itertuples():
            share, n, phrase, cite = result(lk.survey_ref)
            item = lk.survey_item
            role = "valued" if family(item) in VALUED else "received"
            text = option_labels(lk.survey_ref) if ":opt" in lk.survey_ref else lk.survey_text
            short = lk.survey_ref.replace("__topbox", "").replace("__top2", "").replace("__differentiator", "")
            if lk.gate:
                gates.append(lk.gate.replace(" (input)", ""))
            cites.append(cite)
            if share is None:
                items.append(f"{short}: whole question (no single result)")
                continue
            items.append(f"{lk.survey_ref} {share:.4f} ({phrase}; {role}; n {n})")
            if lk.survey_ref in in_set:
                items[-1] += " [counted in the option set]"
                continue
            if abs(share - MAJORITY) < NEAR:
                near.append(short)
            directed = f.layer == "behaviour" and bool(set(lk.route.split(";")) & DIRECTED_ROUTES)
            opposite = lk.polarity == "opposite"
            if role == "valued":
                j = "expand" if opposite else ("agree" if share >= MAJORITY else "expand")
                reading = f"{'most' if share >= MAJORITY else 'a minority'} value it"
            else:
                common = share >= MAJORITY
                reading = f"{'common' if common else 'uncommon'}{' (other pole)' if opposite else ''}"
                if opposite:
                    common = not common
                if not directed or cls in ("too few", "neutral", "no direction", "not coded"):
                    j = "expand"
                elif common:
                    j = {"satisfier": "agree", "dissatisfier": "disagree"}.get(cls, "expand")
                else:
                    j = "agree" if cls in ("dissatisfier", "critical") else "expand"
            judgements.append(j)
            readings.append((role, share, f"{short} {pct(share)} {phrase}: {text[:90]}{'…' if len(text) > 90 else ''}"))
            item_j = f"{short} {reading} -> {j}"
            items[-1] += f" [{item_j}]"

        # ---- concept judgement ---------------------------------------------------------------------------------------
        if len(L) == 0 and n_written < MIN_WRITTEN:
            conv, basis = "silent: both", "no survey link and fewer than 10 written answers"
        elif len(L) == 0:
            conv, basis = "silent: survey", "no survey item is linked to this code"
        elif n_written < MIN_WRITTEN:
            conv, basis = "silent: written", f"{n_written} written answers carry the code (fewer than {MIN_WRITTEN})"
        elif not judgements:
            conv, basis = "expand", "question-level link only: the survey asks about it, but no single result stands for it"
        else:
            na, ne, nd = judgements.count("agree"), judgements.count("expand"), judgements.count("disagree")
            conv = "disagree" if nd else ("agree" if na >= ne else "expand")
            basis = f"items: {na} agree, {ne} expand, {nd} disagree"
            if near:
                basis += f"; near the {MAJORITY:.0%} line: {', '.join(near)}"

        # ---- pillar statement ----------------------------------------------------------------------------------------
        if f.layer == "behaviour" and cls not in ("not coded",):
            wr = (f"{n_written} written answers raise it; {best} times as present in a best account, {worst} as missing in a "
                  f"worst account ({cls})")
        else:
            wr = f"{n_written} written answers use these words (no direction coded)"
        # survey column: the most-valued item and the least-received item, side by side within the survey (no arithmetic)
        val = sorted([x for x in readings if x[0] == "valued"], key=lambda x: (-x[1], x[2]))[:1]
        rec = sorted([x for x in readings if x[0] == "received"], key=lambda x: (x[1], x[2]))[:1]
        sv = "; ".join(x[2] for x in val + rec) if readings else ("whole question only" if len(L) else "no survey item")
        together = {"agree": "Both sources point the same way.", "expand": "The two sources add different sides of it.",
                    "disagree": "The two sources point opposite ways; check before using either alone.",
                    "silent: survey": "Only the written answers speak to it.",
                    "silent: written": "Only the survey speaks to it; the written answers barely raise it.",
                    "silent: both": "Neither source says much about it."}[conv]
        pillar = f"Survey: {sv}. Written: {wr}. {together}"
        sources = sorted(set(cites)) + ["concept_links.csv " + ";".join(L.survey_ref)] if len(L) else []
        sources += [f"codes.csv code {code}"] + ([f"cit_behaviours.csv {code}"] if f.layer == "behaviour" else [])
        rows.append({"concept_id": code, "concept": label, "layer": f.layer, "gates": "; ".join(sorted(set(gates))),
                     "survey_links": len(L), "survey_result": " | ".join(items), "written_answers": n_written,
                     "written_by_question": by_question, "best_present": best, "worst_missing": worst, "written_class": cls,
                     "quote_id": qid, "quote": quote, "convergence": conv, "basis": basis, "pillar_statement": pillar,
                     "sources": " | ".join(sources), "provenance": "INFERRED"})
    J = pd.DataFrame(rows)
    J["o"] = J.convergence.map(ORDER)
    J = J.sort_values(["o", "written_answers", "concept_id"], ascending=[True, False, True]).drop(columns="o")
    J.to_csv(OUT / "joint_display.csv", index=False, lineterminator="\n")
    write_md(J, links)
    print("concepts=", len(J), {k: int(v) for k, v in J.convergence.value_counts().sort_index().items()})
    return 0


def write_md(J, links):
    cnt = J.convergence.value_counts()
    M = ["# Joint display — survey and written answers, by concept (P6.S11)", "",
         "Generated by `scripts/p6_build_joint_display.py` from `inventory/concept_links.csv`, the coding frame, the codes, the "
         "corpus, T01 and T02. Do not edit by hand. **Every link, judgement and pillar statement is INFERRED until Scott reviews "
         "it (P6.S12).**", "",
         "Methods: joint display (Fetters, Curry & Creswell 2013), following a thread (Moran-Ellis et al. 2006), convergence "
         "coding (Farmer et al. 2006), pillar integration (Johnson, Grove & Clarke 2019). Method register QL04, QL06–QL08.", "",
         "**Unit and limits.** Survey results are shares of all respondents (n = 319), group tables only. Written results are "
         "counts of answers. The two never share an axis and are never subtracted or divided (R01, R08). Sources join by "
         "concept only, never by respondent (R04): no respondent has a role level or stakeholder type. A concept is a code "
         "in the behaviour or lexicon layer of the coding frame.", "",
         f"**{len(J)} concepts:** " + ", ".join(f"{k} {int(cnt.get(k, 0))}" for k in ORDER if cnt.get(k, 0)) + ".", "",
         "## How each concept is judged", "",
         f"- **Survey reading.** Valued items (Q1, Q7, Q11, Q13, Q19: what decision-makers say they want) read *most* at {MAJORITY:.0%} "
         f"or more, else *a minority*. Received items (every other question: what they say they get) read *common* at {MAJORITY:.0%} or "
         "more, else *uncommon*. The line is Scott's (P6.S12). A whole question has no single result and is not read.",
         f"- **Written reading.** Behaviour codes take their P5 class from best and worst accounts (satisfier, dissatisfier, "
         f"critical, neutral, too few). Lexicon codes carry no direction. Fewer than {MIN_WRITTEN} answers = silent.",
         "- **Per item.** Valued and most → agree; valued and a minority → expand. Received, where the code and the item share "
         "a pole: common + satisfier → agree; common + dissatisfier → disagree; uncommon + dissatisfier or critical → agree; "
         "uncommon + satisfier → expand; otherwise expand. A received item linked to a lexicon code, or only through a lexicon "
         "entry, → expand (no direction to compare); a valued item is read the same way for every code. An item that measures the other pole (the pitch, for *puts my needs first*) has its reading flipped.",
         "- **Per concept.** Disagree if any item disagrees; agree if agreeing items are at least as many as expanding ones; "
         "else expand. Silent when one side is absent. An option set of one question (e.g. Q14 options 3 + 4 + 5) counts "
         f"once; a share within 5 points of the {MAJORITY:.0%} line is flagged in the judgement, because its reading could tip either way.", ""]
    M += ["## The display", "", "| Concept | Survey (all respondents) | Written answers | Quote | Judgement |", "|---|---|---|---|---|"]
    for r in J.itertuples():
        sv = r.survey_result.replace(" | ", "<br>") if r.survey_result else "—"
        sv = re.sub(r"(\S+__\w+|\S+:opt[\d+]+|Q\d+_\d+) (0\.\d{4})", lambda m: f"{m.group(1)} **{pct(float(m.group(2)))}**", sv)
        wr = f"{r.written_answers} answers ({r.written_by_question or 'none'})"
        if r.layer == "behaviour":
            wr += f"; best +{r.best_present}, worst −{r.worst_missing}; {r.written_class}"
        q = r.quote.replace("|", "/") if r.quote else ""
        q = (q[:220] + "…") if len(q) > 220 else q
        quote = f"“{q}” ({r.quote_id})" if q else "—"
        M.append(f"| **{r.concept}** `{r.concept_id}` | {sv} | {wr} | {quote} | **{r.convergence}** — {r.basis} |")
    M += ["", "## Following the threads", "",
          "Each line starts from a survey item and follows it through the code into the written questions that raise it "
          "(answers per question). Q21 = what differentiates a vendor; Q22 / Q24 = best team / relationship; Q23 / Q25 = "
          "worst.", ""]
    both = J[(J.survey_links > 0) & (J.written_answers > 0)]
    for r in both.itertuples():
        refs = links[links.code == r.concept_id].drop_duplicates("survey_ref").survey_ref.tolist()
        M.append(f"- **{r.concept}** — {', '.join(refs)} → `{r.concept_id}` → {r.written_by_question} → *{r.convergence}*")
    M += ["", "## Pillar statements", ""]
    for r in J.itertuples():
        M.append(f"- **{r.concept}** (`{r.concept_id}`, {r.convergence}): {r.pillar_statement}")
    M.append("")
    (OUT / "joint_display.md").write_text("\n".join(M), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
