#!/usr/bin/env python3
"""p2_check_data_quality.py — data quality for every tabulated variable.

Inputs (read-only): 02_data_inventory/results.csv, 02_data_inventory/variable_dictionary.csv,
01_instrument_reconstruction/cohorts.csv, 01_instrument_reconstruction/anomalies.csv
Outputs: 02_data_inventory/data_quality.csv (one row per item) and data_quality.md

Checks per item:
    base_all            base among all respondents
    nonsubstantive      share choosing don't know / not applicable / other (all respondents)
    out_of_range        values outside 0–1 (any cohort)
    sum_failures        single-choice and grid rows: cohorts whose option shares do not sum to 1 (±0.002)
    base_over_cohort    cohorts where the item base exceeds the cohort's size
    not_asked_cells     cells marked '-' (asked of a subset only)
    zero_base_cells     cohorts with base 0 (nothing to report)
    all_sheets_agree    All-respondents shares identical on every sheet carrying the item
Every check is computed here; nothing is typed by hand.

Usage: python3 -I scripts/p2_check_data_quality.py
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

OD, RD = Path("02_data_inventory"), Path("01_instrument_reconstruction")
OUT_CSV, OUT_MD = OD / "data_quality.csv", OD / "data_quality.md"
NON_SUB = re.compile(r"don.?t\s+know|dont\s+know|not\s+applicable|^\s*other\b|please\s+specify", re.I)
TOL = 0.002
FIELDS = ["item_id", "type", "base_all", "nonsubstantive", "out_of_range", "sum_failures", "sum_checked",
          "base_over_cohort", "not_asked_cells", "zero_base_cells", "all_sheets_agree", "anomalies", "flags"]


def main() -> int:
    res = list(csv.DictReader((OD / "results.csv").open(encoding="utf-8")))
    vd = {v["variable"]: v for v in csv.DictReader((OD / "variable_dictionary.csv").open(encoding="utf-8")) if v["kind"] == "item"}
    cohorts = {c["cohort_id"]: c for c in csv.DictReader((RD / "cohorts.csv").open(encoding="utf-8"))}
    all_id = next(k for k, c in cohorts.items() if c["dimension_id"] == "ALL")

    by_item = defaultdict(list)
    for r in res:
        by_item[r["item_id"]].append(r)
    out, total_fail = [], 0
    for item, rows in by_item.items():
        t = vd[item]["type"]
        vals = [r for r in rows if r["value_status"] == "value"]
        oor = sum(1 for r in vals if not 0 <= float(r["value"]) <= 1)
        canon_all = [r for r in vals if r["cohort_id"] == all_id and r["sheet"] in ("Industry 7",)] or \
                    [r for r in vals if r["cohort_id"] == all_id]
        base_all = canon_all[0]["base_n"] if canon_all else ""
        seen, nonsub = set(), 0.0
        for r in canon_all:
            key = r["option_seq"]
            if key in seen:
                continue
            seen.add(key)
            if NON_SUB.search(r["option_label"]) or (t == "multi_select_option" and NON_SUB.search(vd[item]["label"])):
                nonsub += float(r["value"])
        sums = defaultdict(float)
        for r in vals:
            sums[(r["sheet"], r["cohort_id"])] += float(r["value"])
        fails, checked = 0, 0
        if t in ("single_select", "grid_row"):
            for (sh, cid), s in sums.items():
                base = next((r["base_n"] for r in vals if r["sheet"] == sh and r["cohort_id"] == cid), "")
                if base in ("", "0"):
                    continue
                checked += 1
                if abs(s - 1) > TOL:
                    fails += 1
        over = sum(1 for (sh, cid) in sums if any(r["base_n"] and int(r["base_n"]) > int(cohorts[cid]["n"])
                                                    for r in vals if r["sheet"] == sh and r["cohort_id"] == cid))
        not_asked = sum(1 for r in rows if r["value_status"] == "not_asked")
        zero = len({(r["sheet"], r["cohort_id"]) for r in vals if r["base_n"] == "0"})
        allvals = defaultdict(set)
        for r in vals:
            if r["cohort_id"] == all_id:
                allvals[r["option_seq"]].add(round(float(r["value"]), 12))
        agree = all(len(v) == 1 for v in allvals.values())
        flags = []
        if oor: flags.append("out of range")
        if fails: flags.append(f"{fails} sum failures")
        if over: flags.append("base exceeds cohort")
        if not agree: flags.append("sheets disagree")
        if nonsub >= 0.10: flags.append(f"non-substantive {nonsub:.0%}")
        if vd[item]["anomalies"]: flags.append(f"anomalies {vd[item]['anomalies']}")
        total_fail += oor + fails + over + (0 if agree else 1)
        out.append({"item_id": item, "type": t, "base_all": base_all, "nonsubstantive": f"{nonsub:.4f}",
                    "out_of_range": oor, "sum_failures": fails, "sum_checked": checked, "base_over_cohort": over,
                    "not_asked_cells": not_asked, "zero_base_cells": zero, "all_sheets_agree": "yes" if agree else "no",
                    "anomalies": vd[item]["anomalies"], "flags": "; ".join(flags)})

    order = list(vd)
    out.sort(key=lambda r: order.index(r["item_id"]))
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader(); w.writerows(out)

    checked = sum(r["sum_checked"] for r in out)
    hi_ns = [r for r in out if float(r["nonsubstantive"]) >= 0.10]
    L = ["# Data Quality", "", "Generated by `scripts/p2_check_data_quality.py`. Per-item detail: `data_quality.csv`.", "",
         f"**Items checked:** {len(out)} tabulated items, {sum(len(v) for v in by_item.values())} result cells.", "",
         "| Check | Result |", "|---|---|",
         f"| Values outside 0–1 | {sum(r['out_of_range'] for r in out)} |",
         f"| Single-choice / grid sums ≠ 1 (±{TOL}) | {sum(r['sum_failures'] for r in out)} of {checked} cohort-tables |",
         f"| Item base larger than cohort size | {sum(r['base_over_cohort'] for r in out)} |",
         f"| All-respondents shares disagree across sheets | {sum(1 for r in out if r['all_sheets_agree'] == 'no')} items |",
         f"| Cells not asked ('-'), by design | {sum(r['not_asked_cells'] for r in out)} |",
         f"| Cohort-tables with base 0 | {sum(r['zero_base_cells'] for r in out)} |",
         f"| Items with ≥10% non-substantive answers | {len(hi_ns)} |", "",
         "## Items with ≥10% don't know / not applicable / other", "", "| Item | Share | Base |", "|---|---|---|"]
    for r in sorted(hi_ns, key=lambda r: -float(r["nonsubstantive"])):
        L.append(f"| {r['item_id']} | {float(r['nonsubstantive']):.1%} | {r['base_all']} |")
    L += ["", "## Carried anomalies", "",
          "- A04 Q6 bucket '1-5' holds 0–5 — read as 0–5 in derived data.",
          "- A05 Q6 has one answer of 80 appointments a week — use medians or buckets, not means.",
          "- A07 S5 wording unknown — caution when comparing S5 across IT and business respondents.",
          "- Minimum n = 25 applies to all cohort comparisons (see `coverage_matrix.md`).", ""]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"items={len(out)} failures={total_fail} sum_checked={checked} high_nonsub={len(hi_ns)}")
    return 0 if total_fail == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
