#!/usr/bin/env python3
"""p3_build_schema_mapping.py — map every Phase 2 variable to its place in the schema.

Inputs (read-only):
    02_data_inventory/variable_dictionary.csv
    01_instrument_reconstruction/question_map.csv
    03_schema/examples/full_study.xml, respondents_open_ended.xml, ../tests/synthetic_decision_path.xml
Output:
    03_schema/schema_mapping.csv

One row per variable (189). Columns:
    variable, kind, status, mapping, value_xpath, value_nodes, definition_xpath, definition_nodes,
    checked_in, reason
mapping:
    results          values are cohort results in full_study.xml
    respondent_text  values are respondent text answers (respondents_open_ended.xml)
    rule_only        derivable summary measure: the rule is stored, values are not (ADR-011)
    respondent_slot  reserved respondent-level element; empty in this study; proven by the synthetic test file
    EXCLUDED         not representable from source; reason given
Every XPath is evaluated; the script stops (exit 2) if a mapped XPath that must resolve finds nothing,
or if any variable has no row.

Usage: python3 -I scripts/p3_build_schema_mapping.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd
from lxml import etree

NS = {"d": "https://growthenablement.com/ns/dms/v1", "g": "https://growthenablement.com/ns/gates/v1"}
EX = Path("03_schema/examples")
FILES = {"full_study.xml": EX / "full_study.xml", "respondents_open_ended.xml": EX / "respondents_open_ended.xml",
         "synthetic_decision_path.xml": Path("03_schema/tests/synthetic_decision_path.xml")}
OUT = Path("03_schema/schema_mapping.csv")
FIELDS = ["variable", "kind", "status", "mapping", "value_xpath", "value_nodes", "definition_xpath",
          "definition_nodes", "checked_in", "reason"]

# Missing variables (variable_dictionary.csv status = missing): where the schema reserves room, or why not.
MISSING = {
    "respondent_level_structured": ("respondent_slot", "/d:Study/d:Respondents/d:Respondent/d:Answer",
                                    "Reserved: Respondent/Answer holds one person's structured answers. The source has tables only (SRC-002)."),
    "respondent_function_level": ("respondent_slot", "/d:Study/d:Respondents/d:Respondent/d:Attributes/d:NodeRef",
                                  "Reserved: Respondent/Attributes points to stakeholder nodes. Not collected per respondent; never inferred."),
    "S8_raw": ("EXCLUDED", "", "Raw employee count is not in any source file; only the bucketed S8 is tabulated. "
                               "A future respondent value would go in Respondent/Answer/@value."),
    "S5_piped_text": ("EXCLUDED", "", "The text piped into S5 ('hS5Piping') is not in source (A07); S5 is kept as one question."),
    "Q20_4_content": ("EXCLUDED", "", "The Q20_4 column is present but empty (A06); its purpose is unknown."),
    "industry_39_to_7_map": ("EXCLUDED", "", "The mapping of 39 industries to 7 groups is not in source; the 39 definable "
                                              "cohorts carry no parent cohort."),
    "significance_statistics": ("EXCLUDED", "", "Test statistics and p-values are not in source; only the flag "
                                                 "(significant / not / not tested) is stored (ADR-007)."),
    "survey_weights": ("EXCLUDED", "", "No weights are present or described in source."),
}


def main() -> int:
    v = pd.read_csv("02_data_inventory/variable_dictionary.csv", dtype=str, keep_default_na=False)
    q = pd.read_csv("01_instrument_reconstruction/question_map.csv", dtype=str, keep_default_na=False)
    qtype = dict(q[["item_id", "question_type"]].values)
    docs = {k: etree.parse(str(p)) for k, p in FILES.items()}

    def count(doc, xp):
        return int(docs[doc].xpath(f"count({xp})", namespaces=NS))

    rows, errors = [], []
    for r in v.itertuples():
        dxp = f"/d:Study/d:Variables/d:Variable[@id='{r.variable}']"
        row = {"variable": r.variable, "kind": r.kind, "status": r.status, "definition_xpath": dxp,
               "definition_nodes": count("full_study.xml", dxp), "reason": ""}
        if row["definition_nodes"] != 1:
            errors.append(f"{r.variable}: definition found {row['definition_nodes']} times in full_study.xml")
        if r.kind == "item":
            t = qtype.get(r.variable)
            if t is None:
                errors.append(f"{r.variable}: item not in question_map")
                continue
            if t.startswith("open_text"):
                xp = f"/d:Study/d:Respondents/d:Respondent/d:TextAnswer[@item='{r.variable}']"
                n = count("respondents_open_ended.xml", xp)
                row.update(mapping="respondent_text", value_xpath=xp, value_nodes=n,
                           checked_in="respondents_open_ended.xml",
                           reason="" if n else "Column present in source but no respondent wrote text "
                                               "(0 answers); the slot resolves when answers exist.")
            else:
                xp = f"/d:Study/d:Results/d:ItemResults[@item='{r.variable}']/d:Result"
                n = count("full_study.xml", xp)
                row.update(mapping="results", value_xpath=xp, value_nodes=n, checked_in="full_study.xml")
                if n == 0:
                    errors.append(f"{r.variable}: results XPath finds nothing")
        elif r.kind == "summary":
            row.update(mapping="rule_only", value_xpath=f"{dxp}/d:Rule",
                       value_nodes=count("full_study.xml", f"{dxp}/d:Rule"), checked_in="full_study.xml",
                       reason="Derivable summary measure: the rule is stored; values are computed in Phase 4 (ADR-011). "
                              "Definition INFERRED, pending Scott (Q-P2a).")
            if row["value_nodes"] != 1:
                errors.append(f"{r.variable}: rule not found")
        else:
            if r.variable not in MISSING:
                errors.append(f"{r.variable}: missing variable has no mapping decision")
                continue
            mapping, xp, reason = MISSING[r.variable]
            if mapping == "respondent_slot":
                n = count("synthetic_decision_path.xml", xp)
                row.update(mapping=mapping, value_xpath=xp, value_nodes=n, checked_in="synthetic_decision_path.xml",
                           reason=reason + (" Slot exercised by the synthetic test file." if n else
                                            " Slot defined in the XSD; not exercised by the synthetic file (no attributes are invented)."))
                if xp.endswith("d:Answer") and n == 0:
                    errors.append(f"{r.variable}: Answer slot not exercised by the synthetic file")
            else:
                row.update(mapping="EXCLUDED", value_xpath="", value_nodes="", checked_in="", reason=reason)
        rows.append(row)

    if len(rows) != len(v):
        errors.append(f"{len(rows)} rows for {len(v)} variables")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    counts = pd.Series([r["mapping"] for r in rows]).value_counts().to_dict()
    print(f"variables={len(rows)} " + " ".join(f"{k}={n}" for k, n in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
