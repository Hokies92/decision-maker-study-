#!/usr/bin/env python3
"""p2_crosscheck.py — Phase 2 cross-check and provenance count.

    C01 result cells = Σ over blocks (options × cohort columns on the block's sheet)
    C02 every result maps to a question item and a tabulated cohort
    C03 every tabulated question item has results; no text item does
    C04 significance flags complete: every block × banner on tested sheets has exactly one flag
    C05 variable dictionary covers every question item; every derivable variable has a rule
    C06 data quality: zero failures
    C07 coverage matrix = distinct cohort × item pairs with values; flags follow n = 25
    C08 open-ended: 319 respondents per sheet; all-five count matches the linkage inventory
    C09 every Phase 2 generator re-runs to identical output
    C10 source files match the integrity manifest
Output: 02_data_inventory/crosscheck_report.md

Usage: python3 -I scripts/p2_crosscheck.py
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RD, OD = Path("01_instrument_reconstruction"), Path("02_data_inventory")
OUT = OD / "crosscheck_report.md"
SHEETS = ["Main Page", "Industry 7", "Company Size & Revenue", "Sales Engagement", "Decision Making Stages"]
TESTED = {"Main Page", "Industry 7", "Company Size & Revenue", "Sales Engagement"}
GENERATORS = [
    ("scripts/p2_extract_results.py", ["results.csv"]),
    ("scripts/p2_extract_significance.py", ["significance.csv"]),
    ("scripts/p2_build_variable_dictionary.py", ["variable_dictionary.csv", "variable_dictionary.md"]),
    ("scripts/p2_check_data_quality.py", ["data_quality.csv", "data_quality.md"]),
    ("scripts/p2_build_coverage_matrix.py", ["coverage_matrix.csv", "coverage_matrix.md"]),
    ("scripts/p2_inventory_open_ended.py", ["open_ended_inventory.csv", "open_ended_inventory.md"]),
]


def read(path):
    return list(csv.DictReader(Path(path).open(encoding="utf-8")))


def main() -> int:
    res = read(OD / "results.csv")
    blocks = read(RD / "derived/table_blocks.csv")
    cohorts = read(RD / "cohorts.csv")
    qmap = read(RD / "question_map.csv")
    out = []

    def check(cid, title, ok, detail):
        out.append((cid, title, "PASS" if ok else "FAIL", detail))

    ncols = Counter({s: 1 for s in SHEETS})                    # All-respondents column on every sheet
    for c in cohorts:
        if c["status"] == "tabulated" and c["dimension_id"] != "ALL":
            ncols[c["sheet"]] += 1
    expected = sum(int(b["n_options"]) * ncols[b["sheet"]] for b in blocks)
    check("C01", "Result cells = options × cohort columns", len(res) == expected, f"{len(res)} extracted; {expected} expected")

    items = {q["item_id"] for q in qmap}
    tab_cohorts = {c["cohort_id"] for c in cohorts if c["status"] == "tabulated"}
    bad = [r for r in res if r["item_id"] not in items or r["cohort_id"] not in tab_cohorts]
    check("C02", "Every result maps to an item and a tabulated cohort", not bad, f"unmapped: {len(bad)}")

    with_res = {r["item_id"] for r in res}
    tab_items = {q["item_id"] for q in qmap if q["question_type"] not in ("open_text", "open_text_specify")}
    check("C03", "Every tabulated item has results; text items have none", with_res == tab_items,
          f"{len(with_res)} items with results; {len(tab_items)} tabulated items")

    sig = read(OD / "significance.csv")
    banners = Counter()
    for c in cohorts:
        if c["status"] == "tabulated" and c["sheet"] in TESTED and c["dimension_id"] != "ALL":
            banners[(c["sheet"], c["dimension_id"])] = 1
    per_sheet = Counter(s for s, _ in banners)
    exp_flags = sum((per_sheet[b["sheet"]] + 1) for b in blocks if b["sheet"] in TESTED)
    dup = [k for k, v in Counter((s["sheet"], s["cell"]) for s in sig).items() if v > 1]
    check("C04", "Significance flags complete (block × banner)", len(sig) == exp_flags and not dup,
          f"{len(sig)} flags; {exp_flags} expected (blocks × (banners + All) on tested sheets); duplicates {len(dup)}")

    vd = read(OD / "variable_dictionary.csv")
    vitems = {v["variable"] for v in vd if v["kind"] == "item"}
    norule = [v["variable"] for v in vd if v["status"] == "derivable" and not v["derivation_rule"]]
    check("C05", "Variable dictionary complete; every derivable has a rule", vitems == items and not norule,
          f"{len(vitems)} of {len(items)} items; derivable without rule: {norule or 'none'}")

    dq = read(OD / "data_quality.csv")
    fails = sum(int(r["out_of_range"]) + int(r["sum_failures"]) + int(r["base_over_cohort"]) +
                (r["all_sheets_agree"] != "yes") for r in dq)
    check("C06", "Data quality: zero failures", fails == 0, f"{fails} failures over {len(dq)} items")

    cov = read(OD / "coverage_matrix.csv")
    pairs = {(r["cohort_id"], r["item_id"]) for r in res if r["value_status"] == "value"}
    flag_ok = all((r["flag"] == "ok") == (int(r["base_n"]) >= 25) for r in cov)
    check("C07", "Coverage matrix matches results; flags follow n = 25",
          len(cov) == len(pairs) and flag_ok, f"{len(cov)} cells; {len(pairs)} cohort × item pairs")

    oe = read(OD / "open_ended_inventory.csv")
    import pandas as pd
    sheets = pd.read_excel("00_source/data/open_ended.xlsx", sheet_name=None, dtype=str)
    answered = {}
    for q, d in sheets.items():
        d = d[d["respid"].notna()]
        t = d.iloc[:, 2].fillna("").astype(str).str.strip()
        answered[f"T-Q{int(q[1:]):02d}"] = set(d.loc[t != "", "respid"])
    links = read(RD / "linkages.csv")
    mism = []
    for l in links:
        if l["link_type"] == "same_respondents" and l["source"] in answered and l["target"] in answered:
            true_n = len(answered[l["source"]] & answered[l["target"]])
            if int(l["weight"]) != true_n:
                mism.append(f"{l['source'][2:]}∩{l['target'][2:]}: linkage {l['weight']} vs source {true_n}")
    check("C08", "Open-ended: 319 per sheet; respondent overlaps in linkages equal a fresh count",
          all(int(r["respondents"]) == 319 for r in oe) and not mism,
          f"respondents {[r['respondents'] for r in oe]}; mismatches {len(mism)}: {mism or 'none'}")

    before = {o: hashlib.sha256((OD / o).read_bytes()).hexdigest() for _, outs in GENERATORS for o in outs}
    gen_fail = [s for s, _ in GENERATORS if subprocess.run([sys.executable, "-I", s], capture_output=True).returncode != 0]
    after = {o: hashlib.sha256((OD / o).read_bytes()).hexdigest() for _, outs in GENERATORS for o in outs}
    changed = [o for o in before if before[o] != after[o]]
    check("C09", "Every Phase 2 generator re-runs to identical output", not gen_fail and not changed,
          f"{len(GENERATORS)} scripts, {len(before)} outputs; failures {gen_fail or 'none'}; changed {changed or 'none'}")

    r = subprocess.run(["sha256sum", "-c", "00_source/MANIFEST.sha256"], capture_output=True, text=True)
    check("C10", "Source files match the integrity manifest", r.returncode == 0, r.stdout.strip().replace("\n", "; "))

    prov = Counter()
    for v in vd:
        prov[v["provenance"].split(" ")[0]] += 1
    ok = all(x[2] == "PASS" for x in out)
    L = ["# Phase 2 Cross-check", "", "Generated by `scripts/p2_crosscheck.py`.", "",
         f"**Result: {'ALL PASS' if ok else 'FAILURES'}** — {sum(x[2] == 'PASS' for x in out)} of {len(out)} checks.", "",
         "| Check | What | Result | Detail |", "|---|---|---|---|"]
    for cid, t, res_, d in out:
        L.append(f"| {cid} | {t} | {res_} | {str(d).replace('|', '/')} |")
    L += ["", "## Provenance (variable dictionary)", "", "| Tag | Variables |", "|---|---|"]
    for k, n in sorted(prov.items()):
        L.append(f"| {k} | {n} |")
    L += ["", f"Results ({len(res)} cells), significance flags ({len(sig)}), and coverage cells ({len(cov)}) are all "
          "`RECON_DATA`: read directly from the source tables and comments.", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    for x in out:
        print(x[0], x[2], "—", x[1], "|", x[3][:110])
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
