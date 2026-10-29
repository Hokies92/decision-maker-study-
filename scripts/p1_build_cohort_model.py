#!/usr/bin/env python3
"""p1_build_cohort_model.py — screener S1–S12 as structured metadata for building cohorts.

Inputs (read-only):
    00_source/data/survey.xlsx                              SRC-002 (banner rows, option shares)
    01_instrument_reconstruction/question_map.csv           wording (VERBATIM)
    01_instrument_reconstruction/derived/table_blocks.csv   option lists and rows
    01_instrument_reconstruction/scott_grouping.csv         Scott's groups (RECALL_DESIGNER)
    01_instrument_reconstruction/cohort_semantic_tags.csv   authored topic links (INFERRED)
Outputs (01_instrument_reconstruction/):
    cohort_dimensions.csv   dimensions, layer, parent, source items, tabulated or not
    cohorts.csv             every cohort: tabulated groups from the banners + definable ones
    cohort_tags.csv         links from dimensions/cohorts to downstream question threads
    cohort_model.md         readable summary

Rules (decided by Scott, 2026-10-28):
    - Screener = demographic metadata; input to Target.
    - Role in purchase is subordinate to IT/business; hierarchies stay configurable —
      the hierarchy lives in data (parent pointers), not in code.
    - Untabulated answers stay available as definable cohorts.
    - Minimum n = 25: cohorts below are flagged, still visible.

Sizes: tabulated cohorts read from the banner "Sample Size" row (RECON_DATA); definable
cohorts computed as option share × question base, rounded (RECON_DATA).

Usage: python3 -I scripts/p1_build_cohort_model.py
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

SRC2 = Path("00_source/data/survey.xlsx")
RD = Path("01_instrument_reconstruction")
QMAP, BLOCKS, GROUPS, SEM = RD / "question_map.csv", RD / "derived/table_blocks.csv", \
    RD / "scott_grouping.csv", RD / "cohort_semantic_tags.csv"
OUT_DIM, OUT_COH, OUT_TAG, OUT_MD = RD / "cohort_dimensions.csv", RD / "cohorts.csv", \
    RD / "cohort_tags.csv", RD / "cohort_model.md"

TABLE_SHEETS = ["Main Page", "Industry 7", "Company Size & Revenue", "Sales Engagement",
                "Decision Making Stages"]
CANON = "Industry 7"
ROW_DIM, ROW_LABEL, ROW_N = 11, 12, 14
MIN_N = 25

# dimension_id: (name, layer, parent_dimension, source_items, derived_from, membership, banner_pattern)
DIMS = {
    "D-FUNCTION":    ("Function (IT vs business)", "person", "", "S1", "S1 (IT or IS department → ITDM)", "exclusive", r"^ITDM or BDM"),
    "D-DEPT":        ("Department", "person", "D-FUNCTION", "S1", "", "exclusive", None),
    "D-LEVEL-IT":    ("Level — IT decision-makers", "person", "D-FUNCTION", "S2", "", "exclusive", r"^S2: IT Decision Maker"),
    "D-LEVEL-BUS":   ("Level — business decision-makers", "person", "D-FUNCTION", "S3", "", "exclusive", r"^S3: Business Decision Maker"),
    "D-LEVEL":       ("Level — combined", "person", "", "S2;S3", "S2 + S3 combined", "exclusive", r"^S2 and S3 combined"),
    "D-ITROLE":      ("IT role", "person", "D-FUNCTION", "S4", "", "exclusive", None),
    "D-STAGE":       ("Decision stages involved in", "person", "D-FUNCTION", "S5", "", "overlapping", r"^S5_"),
    "D-STAGE-BUS":   ("IT decision stages (business decision-makers)", "person", "D-FUNCTION", "S6", "", "overlapping", r"^S6_"),
    "D-REVENUE":     ("Company revenue", "company", "", "S7", "", "exclusive", r"^S7_Revenue"),
    "D-EMPLOYEES":   ("Company employees", "company", "", "S8", "S8 numeric answer, bucketed", "exclusive", r"^S8_Bucketed"),
    "D-COUNTRY":     ("Headquarters country", "company", "D-REGION", "S9", "", "exclusive", r"^S9_Country"),
    "D-REGION":      ("Headquarters region", "company", "", "S9", "S9_Country", "exclusive", r"^S9_Region"),
    "D-CONTACTFREQ": ("Frequency of contact with salespeople", "engagement", "", "S10", "", "exclusive", r"^S10:"),
    "D-SELLSTO":     ("Company's own customers (B2B/B2C)", "company", "", "S11", "", "exclusive", r"^S11:"),
    "D-INDUSTRY39":  ("Industry — 39 categories", "company", "D-INDUSTRY7", "S12", "", "exclusive", None),
    "D-INDUSTRY7":   ("Industry — 7 groups", "company", "", "S12", "S12 (39 → 7)", "exclusive", r"^S12_Industry7"),
}
# Definable (untabulated) dimensions: dimension -> canonical item whose options define cohorts
DEFINABLE = {"D-DEPT": "S1", "D-ITROLE": "S4", "D-INDUSTRY39": "S12"}
COUNTRY_REGION = {"Canada": "North America", "United States": "North America",
                  "France": "Europe", "Germany": "Europe", "United Kingdom": "Europe"}


def slug(text: str) -> str:
    s = re.sub(r"\(.*?\)", "", text)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").upper()
    return s[:28].rstrip("-")


def main() -> int:
    wb = load_workbook(SRC2, data_only=True)
    qmap = {r["item_id"]: r for r in csv.DictReader(QMAP.open(encoding="utf-8"))}
    blocks = {(b["sheet"], b["item_id"]): b for b in csv.DictReader(BLOCKS.open(encoding="utf-8"))}
    groups = {r["thread_id"]: r for r in csv.DictReader(GROUPS.open(encoding="utf-8"))}
    sem = list(csv.DictReader(SEM.open(encoding="utf-8")))
    errors: list[str] = []

    cohorts: list[dict] = []
    ids: set[str] = set()

    def add(dim, label, n, status, sheet="", col="", cite="", parent=""):
        cid = f"C-{dim[2:]}-{slug(label)}"
        k = 2
        while cid in ids:
            cid = f"C-{dim[2:]}-{slug(label)}-{k}"; k += 1
        ids.add(cid)
        cohorts.append({"cohort_id": cid, "dimension_id": dim, "label": label, "n": n,
                        "status": status, "min_n_flag": "ok" if n >= MIN_N else f"below minimum ({MIN_N})",
                        "membership": DIMS[dim][5] if dim in DIMS else "all", "parent_cohort": parent,
                        "sheet": sheet, "column": col, "source_cite": cite,
                        "label_prov": "VERBATIM", "n_prov": "RECON_DATA"})
        return cid

    # 1. All respondents
    ws = wb["Main Page"]
    add("ALL", "All Respondents", int(ws.cell(ROW_N, 2).value), "tabulated", "Main Page", "B",
        "SRC-002 Main Page!B12")
    DIMS["ALL"] = ("All respondents", "all", "", "", "", "all", None)

    # 2. Tabulated cohorts from banner rows on every table sheet
    seen_banner = 0
    for name in TABLE_SHEETS:
        ws = wb[name]
        current = ""
        for c in range(3, ws.max_column + 1):
            head = ws.cell(ROW_DIM, c).value
            if head and str(head).strip():
                current = str(head).strip()
            label = ws.cell(ROW_LABEL, c).value
            if not label or not str(label).strip():
                continue
            label = str(label).strip()
            dim = next((d for d, v in DIMS.items() if v[6] and re.search(v[6], current)), None)
            if dim is None:
                errors.append(f"{name}!{get_column_letter(c)}: banner '{current[:40]}' matches no dimension")
                continue
            n = ws.cell(ROW_N, c).value
            col = get_column_letter(c)
            add(dim, label, int(n), "tabulated", name, col, f"SRC-002 {name}!{col}{ROW_LABEL}")
            seen_banner += 1
    if seen_banner != 57:
        errors.append(f"expected 57 tabulated banner groups, found {seen_banner}")

    # 3. Definable cohorts from untabulated answer lists
    for dim, item in DEFINABLE.items():
        b = blocks[(CANON, item)]
        ws = wb[CANON]
        base = int(b["base_all"])
        for r in range(int(b["first_option_row"]), int(b["last_option_row"]) + 1):
            label = str(ws.cell(r, 1).value).strip()
            n = round((ws.cell(r, 2).value or 0) * base)
            add(dim, label, n, "definable — no tabulated results in source", CANON, "",
                f"SRC-002 {CANON}!A{r}")

    # 4. Parent links (hierarchy as data)
    by_dim_label = {(c["dimension_id"], c["label"]): c["cohort_id"] for c in cohorts}
    itdm = by_dim_label[("D-FUNCTION", "ITDM")]
    bdm = by_dim_label[("D-FUNCTION", "BDM")]
    for c in cohorts:
        d = c["dimension_id"]
        if d in ("D-LEVEL-IT", "D-ITROLE"):
            c["parent_cohort"] = itdm
        elif d in ("D-LEVEL-BUS", "D-STAGE-BUS"):
            c["parent_cohort"] = bdm
        elif d == "D-DEPT":
            c["parent_cohort"] = itdm if c["label"].startswith("IT or IS") else bdm
        elif d == "D-COUNTRY":
            c["parent_cohort"] = by_dim_label[("D-REGION", COUNTRY_REGION[c["label"]])]
        elif d == "D-INDUSTRY39":
            c["parent_cohort"] = "MISSING (39 → 7 mapping not in source)"

    # Integrity checks (RECON_DATA)
    def n_of(dim):
        return sum(c["n"] for c in cohorts if c["dimension_id"] == dim)
    checks = {
        "function sums to 319": n_of("D-FUNCTION") == 319,
        "IT levels sum to ITDM": n_of("D-LEVEL-IT") == by_n(cohorts, itdm),
        "business levels sum to BDM": n_of("D-LEVEL-BUS") == by_n(cohorts, bdm),
        "combined levels sum to 319": n_of("D-LEVEL") == 319,
        "countries sum to 319": n_of("D-COUNTRY") == 319,
        "regions sum to 319": n_of("D-REGION") == 319,
        "countries roll up to regions": all(
            sum(c["n"] for c in cohorts if c["dimension_id"] == "D-COUNTRY" and COUNTRY_REGION[c["label"]] == reg)
            == by_n(cohorts, by_dim_label[("D-REGION", reg)]) for reg in ("North America", "Europe")),
        "departments sum to 319": n_of("D-DEPT") == 319,
        "IT dept equals ITDM": by_n(cohorts, by_dim_label[("D-DEPT", "IT or IS department")]) == by_n(cohorts, itdm),
        "IT roles sum to ITDM": n_of("D-ITROLE") == by_n(cohorts, itdm),
        "industries (39) sum to 319": n_of("D-INDUSTRY39") == 319,
        "revenue sums to 319": n_of("D-REVENUE") == 319,
        "employees sum to 319": n_of("D-EMPLOYEES") == 319,
        "contact frequency sums to 319": n_of("D-CONTACTFREQ") == 319,
        "B2B/B2C sums to 319": n_of("D-SELLSTO") == 319,
    }
    ind7 = n_of("D-INDUSTRY7")
    for k, ok in checks.items():
        if not ok:
            errors.append(f"check failed: {k}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    # 5. Dimensions
    dim_rows = []
    for d, (name, layer, parent, items, derived, memb, pat) in DIMS.items():
        if d == "ALL":
            continue
        first = items.split(";")[0]
        stem = next((q["stem"] for q in qmap.values() if q["thread_id"] == f"T-S{int(first[1:]):02d}"
                     and q["stem"]), "")
        tab = any(c["dimension_id"] == d and c["status"] == "tabulated" for c in cohorts)
        dim_rows.append({"dimension_id": d, "name": name, "layer": layer, "parent_dimension": parent,
                         "source_items": items, "derived_from": derived, "membership": memb,
                         "tabulated": "yes" if tab else "no — definable only",
                         "n_cohorts": sum(1 for c in cohorts if c["dimension_id"] == d),
                         "definition": stem, "definition_prov": "VERBATIM" if stem else "",
                         "hierarchy_prov": "RECALL_DESIGNER" if parent == "D-FUNCTION" else
                                           ("RECON_DATA" if parent else "")})

    # 6. Tags: breakout links (RECON_DATA), routing links, semantic links (INFERRED)
    tags = []
    q_threads = sorted({q["thread_id"] for q in qmap.values() if q["thread_id"].startswith("T-Q")
                        and q["question_type"] not in ("open_text", "open_text_specify")},
                       key=lambda t: int(t[3:]))
    dim_sheets = defaultdict(set)
    for c in cohorts:
        if c["status"] == "tabulated" and c["dimension_id"] != "ALL":
            dim_sheets[c["dimension_id"]].add(c["sheet"])
    for d, sheets in dim_sheets.items():
        for t in q_threads:
            on = [s for s in sheets if any(k[0] == s and qmap.get(k[1], {}).get("thread_id") == t
                                           for k in blocks)]
            if on:
                tags.append({"source": d, "target_thread": t, "target_group": groups[t]["scott_group"],
                             "link_type": "breakout_of", "provenance": "RECON_DATA",
                             "rationale": f"results for {t[2]}{int(t[3:])} are tabulated by this dimension on {', '.join(sorted(on))}"})
    for src, tgt, why in [("D-FUNCTION", "T-S02", "IT path asks S2"), ("D-FUNCTION", "T-S04", "IT path asks S4"),
                          ("D-FUNCTION", "T-S03", "business path asks S3"), ("D-FUNCTION", "T-S06", "business path asks S6")]:
        tags.append({"source": src, "target_thread": tgt, "target_group": groups[tgt]["scott_group"],
                     "link_type": "routes_to", "provenance": "RECON_DATA", "rationale": why + " (skip_logic R01/R02)"})
    for r in sem:
        tags.append({"source": r["source"], "target_thread": r["target_thread"],
                     "target_group": groups[r["target_thread"]]["scott_group"],
                     "link_type": r["link_type"], "provenance": r["provenance"], "rationale": r["rationale"]})

    # Write
    def write(path, rows, fields):
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            w.writeheader(); w.writerows(rows)
    write(OUT_DIM, dim_rows, list(dim_rows[0]))
    write(OUT_COH, cohorts, list(cohorts[0]))
    write(OUT_TAG, tags, list(tags[0]))

    # Markdown
    tab = [c for c in cohorts if c["status"] == "tabulated"]
    dfn = [c for c in cohorts if c["status"] != "tabulated"]
    below = [c for c in cohorts if c["min_n_flag"] != "ok"]
    L = ["# Cohort Model — the screener as metadata", "",
         "Generated by `scripts/p1_build_cohort_model.py`. Do not edit by hand.", "",
         "Screener S1–S12 is demographic metadata and the input to **Target** (Scott, 2026-10-28). "
         "Labels `VERBATIM`; sizes `RECON_DATA`; hierarchy under function `RECALL_DESIGNER`.", "",
         "## Summary", "",
         f"- **{len(tab)} tabulated cohorts** (All respondents + {len(tab) - 1} banner groups): results exist for these.",
         f"- **{len(dfn)} definable cohorts** (departments, IT roles, 39 industries): sizes known, no results tabulated in this source.",
         f"- **Minimum n = {MIN_N}:** {len(below)} cohorts are below it and flagged (still visible).",
         "- **Combining cohorts:** only one intersection is tabulated — function × level (Main Page). "
         "Other combinations need respondent-level data; the model reserves room for it.",
         "- **Overlapping cohorts:** decision-stage cohorts (S5, S6) overlap — one person can be in several.",
         f"- Integrity checks: {len(checks)} passed (every exclusive dimension sums to its base; countries roll up to regions; IT department = ITDM).", "",
         "## Hierarchy", "",
         "```",
         "PERSON",
         "  Function (IT vs business)                [S1 → ITDM/BDM]",
         "    ├─ Department                           [S1]  definable",
         "    ├─ Level — IT        (ITDM only)        [S2]",
         "    ├─ Level — business  (BDM only)         [S3]",
         "    ├─ IT role           (ITDM only)        [S4]  definable",
         "    ├─ Decision stages   (all; overlapping) [S5]",
         "    └─ IT decision stages (BDM; overlapping)[S6]",
         "  Level — combined                         [S2 + S3]",
         "COMPANY",
         "  Revenue [S7] · Employees [S8] · Customers B2B/B2C [S11]",
         "  Region [S9] ← Country [S9]",
         "  Industry 7 groups [S12] ← 39 categories [S12]  definable (39→7 mapping not in source)",
         "ENGAGEMENT",
         "  Frequency of contact with salespeople    [S10]",
         "```", "",
         "The hierarchy is stored as parent pointers in `cohort_dimensions.csv` and `cohorts.csv`, so other role "
         "definitions or hierarchies can be added without changing code (Scott: \"make sure we are flexible\").", "",
         "## Tabulated cohorts", "", "| Cohort | Dimension | n | Flag | Where |", "|---|---|---|---|---|"]
    for c in tab:
        L.append(f"| {c['label']} | {DIMS[c['dimension_id']][0]} | {c['n']} | {c['min_n_flag']} | {c['sheet']} {c['column']} |")
    L += ["", "## Definable cohorts (no tabulated results in this source)", "",
          "| Cohort | Dimension | n | Flag |", "|---|---|---|---|"]
    for c in dfn:
        L.append(f"| {c['label']} | {DIMS[c['dimension_id']][0]} | {c['n']} | {c['min_n_flag']} |")
    by_type = defaultdict(int)
    for t in tags:
        by_type[(t["link_type"], t["provenance"])] += 1
    L += ["", "## Tags to downstream questions", "",
          "| Link type | Provenance | Count | Meaning |", "|---|---|---|---|"]
    meaning = {"breakout_of": "this dimension splits that question's results",
               "routes_to": "this dimension decides who is asked that question",
               "relates_to": "topic link proposed by Claude, for review"}
    for (lt, pv), n in sorted(by_type.items()):
        L.append(f"| {lt} | {pv} | {n} | {meaning.get(lt, '')} |")
    L += ["", "Every tag carries the target question's group from Scott's grouping (`target_group`).", ""]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")

    print(f"dimensions={len(dim_rows)} cohorts={len(cohorts)} (tabulated {len(tab)}, definable {len(dfn)}) "
          f"below_min={len(below)} tags={len(tags)} industry7_sum={ind7}")
    return 0


def by_n(cohorts, cid):
    return next(c["n"] for c in cohorts if c["cohort_id"] == cid)


if __name__ == "__main__":
    sys.exit(main())
