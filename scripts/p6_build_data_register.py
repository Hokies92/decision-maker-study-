#!/usr/bin/env python3
"""p6_build_data_register.py — the data register of the analytics inventory (P6.S06).

Every analysable field typed so the validity engine can test any method against it: survey items, summary measures,
coded layers of the written answers, and the written answers themselves.
Inputs: 01_instrument_reconstruction/question_map.csv, item_scales.csv, response_scales.csv, scott_grouping.csv;
        02_data_inventory/variable_dictionary.csv, results.csv, significance.csv; 05_open_ended/codes.csv, corpus.csv.
Output: 06_visualization/inventory/data_register.csv, data_register.md.

Columns:
    field            item / measure / coded-layer id
    kind             item | measure | coded_layer | text
    thread, gate     question thread and Scott's gate (scott_grouping.csv)
    answer_format    one (pick one) | several (pick several; each option a separate yes/no field) | grid (one row of a rating grid)
                     | written (own words) | derived (computed from other fields)
    level            level of measurement (Stevens 1946): nominal | ordinal | binned_numeric | numeric | binary | text
    partition        yes when the field's options are mutually exclusive and exhaustive (shares add to 100%)
    scale_id, scale_family, n_points
    comparable_set   fields that share one question stem, one scale and one base — the only fields whose results may be
                     put on one axis or subtracted (rule R01)
    base_all, asked_of   base for all respondents; 'all' or the routed subset
    unit             group_share (structured: share of a cohort) | answer (written answers)
    respondent_level yes only where a value exists per respondent (written answers); structured results are group tables
    cohorts_with_results, has_sig_flags, source
Usage: python3 -I scripts/p6_build_data_register.py
"""
import sys
from pathlib import Path

import pandas as pd

P1, P2, P5 = Path("01_instrument_reconstruction"), Path("02_data_inventory"), Path("05_open_ended")
OUT = Path("06_visualization/inventory")
LEVEL = {"nominal": "nominal", "ordinal": "ordinal", "numeric_bins": "binned_numeric", "numeric_observed": "numeric",
         "selection_list": "binary", "open_text": "text"}
FORMAT = {"single_select": "one", "multi_select_option": "several", "grid_row": "grid", "open_text": "written",
          "open_text_specify": "written"}


def rd(p):
    return pd.read_csv(p, dtype=str, keep_default_na=False)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    qm, isc, sc = rd(P1 / "question_map.csv"), rd(P1 / "item_scales.csv"), rd(P1 / "response_scales.csv").set_index("scale_id")
    grp = rd(P1 / "scott_grouping.csv").set_index("thread_id")
    vd = rd(P2 / "variable_dictionary.csv").set_index("variable")
    res, sig = rd(P2 / "results.csv"), rd(P2 / "significance.csv")
    scale_of = dict(zip(isc.item_id, isc.scale_id))
    sig_items = set(sig.block_item_id)
    gate = lambda t: grp.loc[t, "gate"] if t in grp.index else ""
    n_text = rd(P5 / "corpus.csv").groupby("item").size().to_dict()   # written answers per item (non-blank)
    rows = []
    for r in qm.itertuples(index=False):
        sid = scale_of.get(r.item_id, "")
        stype = sc.loc[sid, "scale_type"] if sid in sc.index else ("open_text" if r.question_type.startswith("open") else "")
        fmt = "derived" if r.item_role == "derived" else FORMAT.get(r.question_type, "")
        lvl = LEVEL.get(stype, "")
        part = "yes" if fmt in ("one", "grid") or (fmt == "derived" and lvl in ("nominal", "ordinal", "binned_numeric")) else "no"
        base = str(n_text.get(r.item_id, 0)) if fmt == "written" else r.base_all
        rows.append({
            "field": r.item_id, "kind": "text" if fmt == "written" else "item", "thread": r.thread_id, "gate": gate(r.thread_id),
            "answer_format": fmt, "level": lvl, "partition": part if fmt != "written" else "no",
            "scale_id": sid, "scale_family": sc.loc[sid, "family"] if sid in sc.index else "", "n_points": sc.loc[sid, "n_points"] if sid in sc.index else "",
            "comparable_set": f"{r.thread_id}|{sid}|{base}" if fmt in ("several", "grid") else (r.item_id if fmt != "written" else ""),
            "base_all": base, "asked_of": ("written answers given" if fmt == "written" else "all" if base in ("319", "") else f"subset ({base})"),
            "unit": "answer" if fmt == "written" else "group_share", "respondent_level": "yes" if fmt == "written" else "no",
            "cohorts_with_results": vd.loc[r.item_id, "cohorts_with_results"] if r.item_id in vd.index else "",
            "has_sig_flags": "yes" if r.item_id in sig_items else "no",
            "role": r.item_role, "source": "question_map.csv; item_scales.csv; response_scales.csv; variable_dictionary.csv"})
    # summary measures (top box, top two box) — derived binary shares of one grid row or one-answer item
    for v, r in vd[vd.kind == "summary"].iterrows():
        it = r.source_question if r.source_question in set(qm.item_id) else v.split("__")[0]
        base = qm.set_index("item_id").base_all.get(it, "")
        rows.append({
            "field": v, "kind": "measure", "thread": r.thread_id, "gate": gate(r.thread_id), "answer_format": "derived",
            "level": "binary", "partition": "no", "scale_id": r.scale_id, "scale_family": sc.loc[r.scale_id, "family"] if r.scale_id in sc.index else "",
            "n_points": "2", "comparable_set": f"{r.thread_id}|{r.scale_id}|{base}|{v.split('__')[-1]}",
            "base_all": base, "asked_of": "all" if base in ("319", "") else f"subset ({base})", "unit": "group_share",
            "respondent_level": "no", "cohorts_with_results": r.cohorts_with_results, "has_sig_flags": "no",
            "role": r.measure_role or "summary", "source": "variable_dictionary.csv (" + r.derivation_rule.replace(",", ";") + ")"})
    # coded layers of the written answers
    codes, corpus = rd(P5 / "codes.csv"), rd(P5 / "corpus.csv")
    coded = codes[codes.layer == "valence"].answer_id.nunique()
    for layer, g in codes[codes.layer != "notcodable"].groupby("layer"):
        rows.append({
            "field": f"CODE:{layer}", "kind": "coded_layer", "thread": "T-Q21..T-Q25 + specify", "gate": "", "answer_format": "derived",
            "level": "nominal", "partition": "no", "scale_id": "", "scale_family": f"coding frame layer {layer}", "n_points": str(g.code.nunique()),
            "comparable_set": f"CODE:{layer}", "base_all": str(coded), "asked_of": "codable written answers",
            "unit": "answer", "respondent_level": "yes", "cohorts_with_results": "", "has_sig_flags": "no", "role": "multi-code (one primary)",
            "source": "05_open_ended/codes.csv; coding_frame.md"})
    df = pd.DataFrame(rows)
    df = df[df.role != "attention_check"].reset_index(drop=True)
    bad = df[(df.kind != "coded_layer") & ((df.answer_format == "") | (df.level == ""))]
    if not bad.empty:
        print("ERROR: untyped fields:", bad.field.tolist(), file=sys.stderr)
        return 2
    df.to_csv(OUT / "data_register.csv", index=False, lineterminator="\n")
    L = ["# Data register (analytics inventory)", "", "Generated by `scripts/p6_build_data_register.py`. Do not edit by hand.", "",
         f"{len(df)} fields typed for the validity engine. Level of measurement after Stevens (1946). Structured results are group "
         "tables (share of a cohort); only the written answers exist per respondent.", "",
         "| Kind | Answer format | Level | Fields |", "|---|---|---|---|"]
    for (k, f, l), g in df.groupby(["kind", "answer_format", "level"]):
        L.append(f"| {k} | {f} | {l} | {len(g)} |")
    L += ["", f"Comparable sets (one stem, one scale, one base) with more than one field: "
          f"{int((df.groupby('comparable_set').size() > 1).sum())}. Fields asked of a routed subset: {int(df.asked_of.str.startswith('subset').sum())}.", ""]
    (OUT / "data_register.md").write_text("\n".join(L), encoding="utf-8")
    print(f"fields={len(df)}", df.kind.value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
