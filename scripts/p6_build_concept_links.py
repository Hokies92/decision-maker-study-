#!/usr/bin/env python3
"""p6_build_concept_links.py — concept links between survey items and written-answer questions (P6.S11 b).

A concept link joins a survey item to a written-answer question through a code of the coding frame. Links are found by
script, from three routes that the coding frame and its companions already hold; nothing is typed in by hand:

    frame_source   the code's own `source` field in the coding frame names a survey item (e.g. B-KNOWS-BUSINESS: "Q8_3/Q8_5")
    via_lexicon    the code's `source` names a lexicon entry (e.g. "lexicon L11"); that entry's VERBATIM cites name items
    lexicon_cite   the code is a lexicon entry (layer `lexicon`, M11); its own VERBATIM cites in the asymmetry lexicon name items
    t04_pair       the code is linked to a T04 pair (`05_open_ended/t04_concept_links.csv`); the pair's two measures name items
                   (the pairs and their concept map were confirmed by Scott in P6.S02, Q-P4a)

The written side of every link is each written-answer question in which at least one answer carries the code
(`05_open_ended/codes.csv`), with the number of answers. A code with survey links but no coded answer keeps one row with
written_question = none. Joins are by concept (code) only, never by respondent: survey results exist only as group tables
(R04), and no row here holds a respondent.

Polarity: a link is `same` unless listed in OPPOSITE below — a survey item that measures the other pole of a two-sided
behaviour code (INFERRED, with its reason).

Every link is tagged INFERRED until Scott reviews it (P6.S12). Survey references are normalised to the result they stand
for: a rating item to its T02 headline measure (e.g. Q8_5 -> Q8_5__topbox), a several-answer item to itself, a cited option
to item:optN, a T04 option set to item:optN+M, a stem to item:stem (question-level link, no single result).

Inputs: 05_open_ended/coding_frame.csv, codes.csv, t04_concept_links.csv; 01_instrument_reconstruction/asymmetry_lexicon.csv,
        question_map.csv; 04_analytics_library/pairs.csv; 06_visualization/inventory/data_register.csv.
Output: 06_visualization/inventory/concept_links.csv
Usage: python3 -I scripts/p6_build_concept_links.py
"""
import re
import sys
from pathlib import Path

import pandas as pd

OUT = Path("06_visualization/inventory/concept_links.csv")
CONCEPT_LAYERS = ("behaviour", "lexicon")
WRITTEN_ORDER = ["Q21", "Q22", "Q23", "Q24", "Q25"]
# Survey items that measure the other pole of a two-sided behaviour code (INFERRED; Scott reviews in S12).
OPPOSITE = {
    ("B-CUSTOMER-FIRST", "Q11_6"): "the item values a compelling presentation — the pitch, the other pole of putting my needs first (pair P05)",
    ("B-CUSTOMER-FIRST", "Q14:opt1+2"): "the options describe the pitch — the other pole of putting my needs first (pair P05)",
}


def rd(p):
    return pd.read_csv(p, dtype=str, keep_default_na=False)


def main() -> int:
    frame = rd("05_open_ended/coding_frame.csv")
    codes = rd("05_open_ended/codes.csv")
    lex = rd("01_instrument_reconstruction/asymmetry_lexicon.csv").set_index("entry_id")
    t04c = rd("05_open_ended/t04_concept_links.csv")
    pairs = rd("04_analytics_library/pairs.csv").set_index("pair_id")
    reg = rd("06_visualization/inventory/data_register.csv").set_index("field")
    qmap = rd("01_instrument_reconstruction/question_map.csv").drop_duplicates("item_id").set_index("item_id")
    survey_fields = set(reg[reg.kind.isin(["item", "measure"])].index)
    written_fields = set(reg[reg.kind == "text"].index)
    # the register names a summary measure <item>__<rule>; each rated item has one headline measure (T02)
    headline = {f.split("__")[0]: f for f in reg[(reg.kind == "measure") & (reg.role == "headline")].index}

    def norm(tok):
        """Normalise a cited survey reference; None for written questions and unknown tokens."""
        tok = tok.strip()
        m = re.fullmatch(r"([QS]\d+(?:_[A-Za-z0-9]+)?)(?::(stem|opt\d+))?", tok)
        if m:
            item, part = m.group(1), m.group(2)
            if item in written_fields or item in WRITTEN_ORDER:
                return None
            if part == "stem":
                return f"{item}:stem"
            if part:
                return f"{item}:{part}"
            if item in headline:
                return headline[item]
            if item in survey_fields:
                return item
            if any(f.startswith(item + "_") for f in survey_fields):  # a bare question number names the whole question
                return f"{item}:stem"
            return None
        if "__" in tok and tok in survey_fields:
            return tok
        m = re.fullmatch(r"([QS]\d+(?:_\d+)?)=\d+(?:;[QS]\d+(?:_\d+)?=\d+)*", tok)
        if m and len({p.split("=")[0] for p in tok.split(";")}) == 1:
            item = tok.split("=")[0]
            opts = [p.split("=")[1] for p in tok.split(";")]
            return f"{item}:opt{'+'.join(opts)}"
        return None

    links = []  # (code, ref, route, evidence)
    labels = {}
    for f in frame[frame.layer.isin(CONCEPT_LAYERS)].itertuples():
        labels[f.code] = f.label if f.layer == "behaviour" else lex.loc[f.code, "concept"]
        src = re.sub(r"example\s+\S+.*$", "", f.source)
        src = re.sub(r"[A-Za-z0-9_]+-R\d+", "", src)
        if f.layer == "behaviour":
            for tok in re.findall(r"\b([QS]\d+(?:_\d+)?)\b", src.replace("/", " ")):
                ref = norm(tok)
                if ref:
                    links.append((f.code, ref, "frame_source", f"coding_frame.csv {f.code} source names {tok}"))
            for lid in re.findall(r"lexicon (L\d\d)", src):
                for tok in re.findall(r"([QS]\d+(?:_[A-Za-z0-9]+)?(?::(?:stem|opt\d+))?) \(", lex.loc[lid, "decision_maker_cites"]):
                    ref = norm(tok)
                    if ref:
                        links.append((f.code, ref, "via_lexicon", f"coding_frame.csv {f.code} source names lexicon {lid}; "
                                                                   f"asymmetry_lexicon.csv {lid} cites {tok} (VERBATIM)"))
        else:
            for tok in re.findall(r"([QS]\d+(?:_[A-Za-z0-9]+)?(?::(?:stem|opt\d+))?) \(", lex.loc[f.code, "decision_maker_cites"]):
                ref = norm(tok)
                if ref:
                    links.append((f.code, ref, "lexicon_cite", f"asymmetry_lexicon.csv {f.code} cites {tok} (VERBATIM)"))
    own = {}  # items each behaviour code's own frame source names (not through a lexicon entry)
    for code, ref, route, _ in links:
        if route == "frame_source":
            own.setdefault(code, set()).add(ref.split("__")[0].split(":")[0])
    for r in t04c.itertuples():
        p = pairs.loc[r.pair_id]
        for side in ("a_measures", "b_measures"):
            tok = p[side]
            ref = norm(tok) if "=" in tok else norm(tok.split(";")[0])
            if ref is None:
                print(f"ERROR: T04 pair {r.pair_id} {side} '{tok}' not resolved", file=sys.stderr)
                return 2
            item = ref.split("__")[0].split(":")[0]
            for code in r.codes.split(";"):
                # a contrast pair sets two different concepts side by side (own products vs my business): a code joins
                # the side its own frame source names, or both sides when its frame source names the whole question
                if p.pair_type == "self_vs_customer" and not ({item, item.split("_")[0]} & own.get(code, set())):
                    continue
                links.append((code, ref, "t04_pair", f"t04_concept_links.csv {r.pair_id} links {code}; pairs.csv {r.pair_id} "
                                                    f"{side[0]} = {tok} ({p.concept}; pair confirmed by Scott, P6.S02)"))

    L = pd.DataFrame(links, columns=["code", "survey_ref", "route", "evidence"])
    L = L[L.code.isin(labels)]
    unknown = sorted(set(L.code) - set(labels))
    if unknown:
        print("ERROR: codes not in frame:", unknown, file=sys.stderr)
        return 2
    L = (L.groupby(["code", "survey_ref"], sort=True)
          .agg(route=("route", lambda s: ";".join(sorted(set(s)))), evidence=("evidence", lambda s: " | ".join(sorted(set(s)))))
          .reset_index())

    # written side: answers carrying the code, per written-answer question
    cw = codes[codes.code.isin(labels)].groupby(["code", "item"]).answer_id.nunique().reset_index(name="written_answers")
    order = {q: i for i, q in enumerate(WRITTEN_ORDER)}
    cw["o"] = cw["item"].map(lambda q: order.get(q, 99))

    def members(item):
        """The question-map rows of an item, or of every item in a question for a stem."""
        return qmap[(qmap.index == item) | qmap.index.str.startswith(item + "_")]

    def item_text(ref):
        item = ref.split("__")[0].split(":")[0]
        q = members(item)
        if len(q) == 0:
            return ""
        if ref.endswith(":stem") or ":opt" in ref or item not in q.index:
            return q.iloc[0].stem.strip()
        return (q.loc[item, "item_label"] or q.loc[item, "stem"]).strip()

    def gate(item):
        if item in reg.index:
            return reg.loc[item, "gate"]
        sub = [f for f in members(item).index if f in reg.index]
        return reg.loc[sub[0], "gate"] if sub else ""

    rows = []
    for r in L.itertuples():
        survey_item = r.survey_ref.split("__")[0].split(":")[0]
        pol = "opposite" if (r.code, r.survey_ref) in OPPOSITE else "same"
        base = {"code": r.code, "concept": labels[r.code], "layer": "behaviour" if r.code.startswith("B-") else "lexicon",
                "survey_ref": r.survey_ref, "survey_item": survey_item, "survey_text": item_text(r.survey_ref), "gate": gate(survey_item),
                "polarity": pol, "polarity_reason": OPPOSITE.get((r.code, r.survey_ref), ""), "route": r.route, "evidence": r.evidence}
        w = cw[cw.code == r.code].sort_values(["o", "item"])
        if len(w) == 0:
            rows.append({**base, "written_question": "none", "written_answers": 0})
        for x in w.itertuples():
            rows.append({**base, "written_question": x.item, "written_answers": int(x.written_answers)})
    out = pd.DataFrame(rows)
    out.insert(0, "link_id", [f"CL{i + 1:03d}" for i in range(len(out))])
    out["provenance"] = "INFERRED"
    out.to_csv(OUT, index=False, lineterminator="\n")
    print(f"links={len(out)} codes={out.code.nunique()} survey_refs={out.survey_ref.nunique()} "
          f"routes={ {k: int(v) for k, v in pd.Series([x for s in L.route for x in s.split(';')]).value_counts().sort_index().items()} }")
    return 0


if __name__ == "__main__":
    sys.exit(main())
