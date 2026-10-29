#!/usr/bin/env python3
"""p2_build_variable_dictionary.py — every variable: collected, derivable, or missing.

Inputs (read-only): question_map.csv, item_scales.csv, response_scales.csv, anomalies.csv
(01_instrument_reconstruction/), 02_data_inventory/results.csv,
02_data_inventory/variable_review_decisions.csv (authored: Scott's decisions on the INFERRED definitions, P4.S01)
Outputs: 02_data_inventory/variable_dictionary.csv and .md; 02_data_inventory/variable_review.csv
(one row per INFERRED variable with the decision that covers it; the script stops if any is uncovered)

Statuses (GOVERNANCE §5 P2):
    collected  — asked of respondents; results or text exist in the source
    derivable  — computable from collected variables by an explicit rule
    missing    — needed or implied by the instrument but not in the source

Three kinds of rows:
    1. every question-map item (136) — collected, or derivable if the item is itself a recode
    2. summary variables proposed for analysis — derivable, rule stated (definition INFERRED)
    3. missing variables — named, with the reason

Usage: python3 -I scripts/p2_build_variable_dictionary.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RD, OD = Path("01_instrument_reconstruction"), Path("02_data_inventory")
OUT_CSV, OUT_MD = OD / "variable_dictionary.csv", OD / "variable_dictionary.md"
FIELDS = ["variable", "kind", "label", "source_question", "thread_id", "type", "scale_id", "valid_values",
          "status", "derivation_rule", "provenance", "result_cells", "cohorts_with_results", "anomalies", "note",
          "reviewed", "measure_role"]
REVIEW_DEC, REVIEW_OUT = OD / "variable_review_decisions.csv", OD / "variable_review.csv"

# Summary variables: scale_id → (suffix, options counted, meaning)
TOPBOX = {
    "SC-FREQ4": ("top2", ["Occasionally", "Frequently"], "share answering Occasionally or Frequently"),
    "SC-FREQ4/topbox": ("topbox", ["Frequently"], "share answering Frequently"),
    "SC-AGREE4": ("top2", ["Agree", "Strongly agree"], "share answering Agree or Strongly agree"),
    "SC-IMPORT4": ("top2", ["Very important", "Somewhat important"], "share answering Very or Somewhat important"),
    "SC-DIFF3": ("differentiator", ["Important, and a differentiator"], "share rating it a differentiator"),
}
MISSING = [
    ("respondent_level_structured", "All structured answers per respondent", "Only group-level tables exist (Scott: the two files are the only data)."),
    ("respondent_function_level", "Function and level per respondent", "Not in source; never inferred (CLAUDE.md)."),
    ("S8_raw", "Employee count as entered (S8)", "Only the bucketed form is tabulated (A08)."),
    ("S5_piped_text", "Text inserted into S5 wording ('hS5Piping')", "Not in source; Scott does not recall (A07)."),
    ("Q20_4_content", "Purpose and content of the Q20_4 column", "Column present, no entries; trigger unrecoverable (A06, R12)."),
    ("industry_39_to_7_map", "Mapping of the 39 industries to the 7 groups", "Recode exists; its mapping is not in source."),
    ("significance_statistics", "Test statistic and p-value behind each significance flag", "Only the verdict is stored (P2.S02)."),
    ("survey_weights", "Weights, if any were applied", "Not stated in source; tables read as unweighted."),
]


def main() -> int:
    qmap = list(csv.DictReader((RD / "question_map.csv").open(encoding="utf-8")))
    scale_of = {r["item_id"]: r["scale_id"] for r in csv.DictReader((RD / "item_scales.csv").open(encoding="utf-8"))}
    scales = {s["scale_id"]: s for s in csv.DictReader((RD / "response_scales.csv").open(encoding="utf-8"))}
    anomalies = list(csv.DictReader((RD / "anomalies.csv").open(encoding="utf-8")))
    results = list(csv.DictReader((OD / "results.csv").open(encoding="utf-8")))

    cells, cohorts_seen = Counter(), defaultdict(set)
    for r in results:
        if r["value_status"] == "value":
            cells[r["item_id"]] += 1
            cohorts_seen[r["item_id"]].add(r["cohort_id"])

    def anomaly_ids(item):
        base = item.split("_")[0]
        out = []
        for a in anomalies:
            text = f"{a['title']} {a['evidence']}"
            if re.search(rf"\b{re.escape(item)}\b", text) or (re.search(rf"\b{base}\b", text) and a["id"] in ("A01", "A02", "A04", "A05", "A07", "A10")
                                                               and item.startswith(base)):
                out.append(a["id"])
        return ";".join(sorted(set(out)))

    rows, errors = [], []
    for q in qmap:
        sid = scale_of.get(q["item_id"], "")
        labels = json.loads(scales[sid]["labels"]) if sid in scales else []
        derived = q["item_role"] == "derived"
        rule = ""
        if derived:
            rule = f"Recode of {q['derived_from']}: {q['derived_evidence']}"
            if q["item_id"] == "Q6_bucketed":
                rule += " Read the '1-5' band as 0–5 (anomaly A04)."
        tabulated = cells[q["item_id"]] > 0
        text_item = q["question_type"] in ("open_text", "open_text_specify")
        if not (tabulated or text_item):
            errors.append(f"{q['item_id']}: no results and not a text item")
        rows.append({
            "variable": q["item_id"], "kind": "item", "label": q["item_label"] or q["stem"],
            "source_question": f"{q['thread_id'][2]}{int(q['thread_id'][3:])}", "thread_id": q["thread_id"],
            "type": q["question_type"], "scale_id": sid,
            "valid_values": "free text" if text_item else json.dumps(labels, ensure_ascii=False),
            "status": "derivable" if derived else "collected", "derivation_rule": rule,
            "provenance": q["derived_prov"] if derived else "RECON_DATA",
            "result_cells": cells[q["item_id"]], "cohorts_with_results": len(cohorts_seen[q["item_id"]]),
            "anomalies": anomaly_ids(q["item_id"]),
            "note": "attention check — exclude from substantive analysis" if q["item_role"] == "attention_check" else
                    ("text answers keyed by respid" if text_item else ""),
        })

    for q in qmap:
        sid = scale_of.get(q["item_id"], "")
        if q["question_type"] != "grid_row" or sid not in TOPBOX or q["item_role"] == "attention_check":
            continue
        for key in (sid, f"{sid}/topbox"):
            if key not in TOPBOX:
                continue
            suffix, opts, meaning = TOPBOX[key]
            labels = json.loads(scales[sid]["labels"])
            if any(o not in labels for o in opts):
                errors.append(f"{sid}: option missing for summary rule")
            rows.append({"variable": f"{q['item_id']}__{suffix}", "kind": "summary", "label": f"{q['item_label']} — {meaning}",
                         "source_question": f"{q['thread_id'][2]}{int(q['thread_id'][3:])}", "thread_id": q["thread_id"],
                         "type": "share", "scale_id": sid, "valid_values": "0–1", "status": "derivable",
                         "derivation_rule": f"{'share' if len(opts) == 1 else 'sum of shares'} for {' + '.join(opts)} in {q['item_id']}, per cohort",
                         "provenance": "INFERRED (definition)", "result_cells": "", "cohorts_with_results": "",
                         "anomalies": "", "note": ""})
    rows.append({"variable": "Q18__self_built", "kind": "summary",
                 "label": "Share who did most or all of the business justification themselves",
                 "source_question": "Q18", "thread_id": "T-Q18", "type": "share", "scale_id": "SC-MATERIALS7",
                 "valid_values": "0–1", "status": "derivable",
                 "derivation_rule": "sum of shares for options 4 ('…We had to do most of the business justification ourselves') "
                                    "+ 5 ('…We had to do all of the business justification ourselves') in Q18, per cohort",
                 "provenance": "INFERRED (definition)", "result_cells": "", "cohorts_with_results": "", "anomalies": "",
                 "note": "decision-maker wording from the asymmetry lexicon (L20)"})
    for var, label, why in MISSING:
        rows.append({"variable": var, "kind": "missing", "label": label, "source_question": "", "thread_id": "",
                     "type": "", "scale_id": "", "valid_values": "", "status": "missing", "derivation_rule": "",
                     "provenance": "MISSING", "result_cells": "", "cohorts_with_results": "", "anomalies": "", "note": why})

    # Scott's review of the INFERRED definitions (P4.S01): every INFERRED variable must match exactly one decision
    decisions = list(csv.DictReader(REVIEW_DEC.open(encoding="utf-8")))
    review_rows = []
    for r in rows:
        r.setdefault("reviewed", ""); r.setdefault("measure_role", "")
        if not r["provenance"].startswith("INFERRED"):
            continue
        suffix = r["variable"].split("__")[1] if "__" in r["variable"] else ""
        hits = [d for d in decisions if d["match_kind"] == r["kind"] and (
            r["variable"] in d["match_variables"].split(";") if d["match_variables"]
            else (d["match_suffix"] == suffix and d["match_scale"] == r["scale_id"]))]
        if len(hits) != 1:
            errors.append(f"{r['variable']}: matches {len(hits)} review decisions")
            continue
        d = hits[0]
        if d["decision"].startswith(("approved", "added and approved")):
            r["reviewed"] = "confirmedByScott"
        r["measure_role"] = d["role"]
        review_rows.append({"variable": r["variable"], "group": d["group"], "definition": r["derivation_rule"],
                            "decision": d["decision"], "measure_role": d["role"], "decided_by": d["decided_by"],
                            "decided_on": d["decided_on"], "basis": d["basis"]})

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    with REVIEW_OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["variable", "group", "definition", "decision", "measure_role",
                                           "decided_by", "decided_on", "basis"], lineterminator="\n")
        w.writeheader(); w.writerows(review_rows)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    st = Counter((r["kind"], r["status"]) for r in rows)
    L = ["# Variable Dictionary", "", "Generated by `scripts/p2_build_variable_dictionary.py`. Full detail: `variable_dictionary.csv`.", "",
         f"**{len(rows)} variables.**", "", "| Kind | Status | Count |", "|---|---|---|"]
    for (k, s), n in sorted(st.items()):
        L.append(f"| {k} | {s} | {n} |")
    L += ["", "## Derivable items (recodes in the source)", "", "| Variable | Rule | Provenance |", "|---|---|---|"]
    for r in rows:
        if r["kind"] == "item" and r["status"] == "derivable":
            L.append(f"| {r['variable']} | {r['derivation_rule']} | {r['provenance']} |")
    L += ["", "## Summary variables proposed for analysis (derivable)", "",
          "| Scale | Summary | Rule | Count |", "|---|---|---|---|"]
    by_scale = Counter(r["scale_id"] for r in rows if r["kind"] == "summary")
    by_suffix = Counter((r["scale_id"], r["variable"].split("__")[1]) for r in rows if r["kind"] == "summary" and "__" in r["variable"])
    for key, (suffix, opts, meaning) in TOPBOX.items():
        sid = key.split("/")[0]
        L.append(f"| {sid} | `__{suffix}` | {meaning} | {by_suffix[(sid, suffix)]} |")
    L.append("| SC-MATERIALS7 | `Q18__self_built` | did most or all of the business justification themselves (options 4 + 5) | 1 |")
    rc = Counter((v["group"], v["decision"], v["measure_role"]) for v in review_rows)
    L += ["", "## Scott's review of the INFERRED definitions (P4.S01)", "",
          f"All {len(review_rows)} INFERRED variables are covered by a decision in `variable_review_decisions.csv`; "
          "per-variable record in `variable_review.csv`. Approved definitions keep `INFERRED` and carry `reviewed = confirmedByScott`.", "",
          "| Group | Decision | Role | Variables |", "|---|---|---|---|"]
    for (g, dcs, role), n in sorted(rc.items()):
        L.append(f"| {g} | {dcs} | {role or '—'} | {n} |")
    L += ["", "## Missing variables", "", "| Variable | What | Why missing |", "|---|---|---|"]
    for var, label, why in MISSING:
        L.append(f"| {var} | {label} | {why} |")
    L.append("")
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"variables={len(rows)}", dict(st))
    return 0


if __name__ == "__main__":
    sys.exit(main())
