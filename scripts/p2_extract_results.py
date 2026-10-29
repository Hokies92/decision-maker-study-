#!/usr/bin/env python3
"""p2_extract_results.py — every tabulated result as one row: item × option × cohort.

Inputs (read-only):
    00_source/data/survey.xlsx                              SRC-002
    01_instrument_reconstruction/derived/table_blocks.csv   block positions (P1.S01)
    01_instrument_reconstruction/cohorts.csv                cohort ↔ sheet/column (P1.S06)
    01_instrument_reconstruction/question_map.csv           item ids (P1.S02)
Output:
    02_data_inventory/results.csv

One row per tabulated cell on the five table sheets. Columns:
    sheet, cell, block_item_id, item_id, option_seq, option_label, cohort_id,
    value (share 0–1, blank if not asked), value_status (value | not_asked | blank),
    base_n (cohort base for this item), base_source
Main Page condensed tables (Q11, Q15 — anomalies A01/A02) are split back to their items:
option k of the condensed table → item Q11_k / Q15_k, option "selected".
"Sheet1" is a duplicate (A03) and is not extracted.

Checks (exit 2 on failure): every value in 0–1; every not-asked cell is '-'; the
All-respondents value of every item × option agrees across all sheets that carry it.

Usage: python3 -I scripts/p2_extract_results.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string, get_column_letter

SRC2 = Path("00_source/data/survey.xlsx")
RD = Path("01_instrument_reconstruction")
OUT = Path("02_data_inventory/results.csv")
SHEETS = ["Main Page", "Industry 7", "Company Size & Revenue", "Sales Engagement", "Decision Making Stages"]
CONDENSED = {"Q11_1": "Q11", "Q15": "Q15"}   # Main Page block id → base question
TOL = 1e-9
FIELDS = ["sheet", "cell", "block_item_id", "item_id", "option_seq", "option_label", "cohort_id",
          "value", "value_status", "base_n", "base_source"]


def main() -> int:
    wb = load_workbook(SRC2, data_only=True)
    blocks = list(csv.DictReader((RD / "derived/table_blocks.csv").open(encoding="utf-8")))
    cohorts = list(csv.DictReader((RD / "cohorts.csv").open(encoding="utf-8")))
    qids = {q["item_id"] for q in csv.DictReader((RD / "question_map.csv").open(encoding="utf-8"))}
    all_id = next(c["cohort_id"] for c in cohorts if c["dimension_id"] == "ALL")
    cohort_n = {c["cohort_id"]: int(c["n"]) for c in cohorts}
    cols = defaultdict(list)                     # sheet → [(col_index, cohort_id)]
    for s in SHEETS:
        cols[s].append((2, all_id))
    for c in cohorts:
        if c["status"] == "tabulated" and c["dimension_id"] != "ALL":
            cols[c["sheet"]].append((column_index_from_string(c["column"]), c["cohort_id"]))

    rows, errors = [], []
    for b in blocks:
        sheet = b["sheet"]
        ws = wb[sheet]
        block_id = b["item_id"] or "DM_TYPE"
        opts = json.loads(b["options_json"])
        has_base = b["has_base_row"] == "yes"
        base_row = int(b["header_row"]) + 1 if has_base else None
        for k, label in enumerate(opts):
            r = int(b["first_option_row"]) + k
            if sheet == "Main Page" and block_id in CONDENSED:
                item_id, opt_seq, opt_label = f"{CONDENSED[block_id]}_{k + 1}", 1, label
            else:
                item_id, opt_seq, opt_label = block_id, k + 1, label
            if item_id not in qids:
                errors.append(f"{sheet}!A{r}: item {item_id} not in question map")
                continue
            for ci, cid in sorted(cols[sheet]):
                v = ws.cell(r, ci).value
                coord = f"{get_column_letter(ci)}{r}"
                if isinstance(v, str) and v.strip() == "-":
                    value, status = "", "not_asked"
                elif v is None:
                    value, status = "", "blank"
                elif isinstance(v, (int, float)):
                    if not -TOL <= v <= 1 + TOL:
                        errors.append(f"{sheet}!{coord}: value {v} outside 0–1")
                    value, status = repr(float(v)), "value"
                else:
                    errors.append(f"{sheet}!{coord}: unexpected value {v!r}")
                    continue
                if has_base:
                    bv = ws.cell(base_row, ci).value
                    base = "" if (bv is None or (isinstance(bv, str) and bv.strip() == "-")) else str(int(bv))
                    bsrc = f"{sheet}!{get_column_letter(ci)}{base_row}"
                else:
                    base, bsrc = str(cohort_n[cid]), "cohort size (table has no base row)"
                rows.append({"sheet": sheet, "cell": coord, "block_item_id": block_id, "item_id": item_id,
                             "option_seq": opt_seq, "option_label": opt_label, "cohort_id": cid,
                             "value": value, "value_status": status, "base_n": base, "base_source": bsrc})

    # All-respondents agreement across sheets
    allv = defaultdict(dict)
    for r in rows:
        if r["cohort_id"] == all_id and r["value_status"] == "value":
            allv[(r["item_id"], r["option_seq"])][r["sheet"]] = float(r["value"])
    disagree = [(k, v) for k, v in allv.items() if max(v.values()) - min(v.values()) > 1e-9]
    if disagree:
        errors.append(f"All-respondents values disagree across sheets for {len(disagree)} item-options, e.g. {disagree[:2]}")

    if errors:
        for e in errors[:20]:
            print("ERROR:", e, file=sys.stderr)
        return 2
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    by = defaultdict(int)
    for r in rows:
        by[(r["sheet"], r["value_status"])] += 1
    print(f"results={len(rows)} item-options with All value={len(allv)} (agree across sheets)")
    for k, v in sorted(by.items()):
        print(f"  {k[0]:24} {k[1]:10} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
