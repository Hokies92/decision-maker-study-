#!/usr/bin/env python3
"""p6_build_inventory.py — the validity engine of the analytics inventory (P6.S08).

Pairs every method in the method register with every field, set of fields, pair of fields or group breakdown it could
apply to, tests each combination against the validity rules, and keeps the valid ones. Every rejected combination names
the rule it breaks. Combinations whose answer format the method does not accept are counted as not applicable, not listed.

Inputs: 06_visualization/inventory/data_register.csv (P6.S06), method_register.csv and rules.csv (authored, P6.S07–S08),
        04_analytics_library/pairs.csv (to re-test the retired V1 ledger), 01_instrument_reconstruction/cohort_dimensions.csv.
Outputs: 06_visualization/inventory/valid.csv, rejected.csv, summary.md, methods.md.
Statuses: valid | valid_with_condition (a rule adds a condition the analysis must state) | needs_data | rejected.
Regression test (exit 2 if it fails): every retired V1 ledger pair and the V3 felt-vs-said comparison must be rejected.
Usage: python3 -I scripts/p6_build_inventory.py
"""
import csv
import itertools
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

INV = Path("06_visualization/inventory")
LEVELS = {"nominal": 0, "binary": 1, "ordinal": 2, "binned_numeric": 3, "numeric": 4}
MIN_N = 25


def rd(p):
    return pd.read_csv(p, dtype=str, keep_default_na=False)


def main() -> int:
    reg = rd(INV / "data_register.csv").set_index("field", drop=False)
    methods = list(csv.DictReader((INV / "method_register.csv").open(encoding="utf-8")))
    rules = rd(INV / "rules.csv").set_index("rule_id")
    structured = reg[reg.kind.isin(["item", "measure"]) & (reg.role != "derived_screener")]
    headline = structured[structured.role == "headline"].field.tolist()
    sets = {k: g.field.tolist() for k, g in structured.groupby("comparable_set") if len(g) > 1}
    coded = reg[reg.kind == "coded_layer"].field.tolist()
    written = reg[reg.kind == "text"].field.tolist()
    overlapping_dims = rd(Path("01_instrument_reconstruction/cohort_dimensions.csv"))
    overlapping = sorted(overlapping_dims[overlapping_dims.membership == "overlapping"].name)

    # ---- candidates per arity ------------------------------------------------------------------------------------
    def candidates(m):
        a = m["arity"]
        if a == "one":
            return [[f] for f in structured.field]
        if a == "set":
            return [v for _, v in sorted(sets.items())]
        if a == "pair_same_set":
            return [list(p) for _, v in sorted(sets.items()) for p in itertools.combinations(v, 2)]
        if a == "pair_cross":
            pairs = [list(p) for p in itertools.combinations(headline, 2) if reg.loc[p[0], "comparable_set"] != reg.loc[p[1], "comparable_set"]]
            return pairs + retired_v1
        if a in ("cohort",):
            return [[f] for f in structured.field if (reg.loc[f, "cohorts_with_results"] or "0").isdigit() and int(reg.loc[f, "cohorts_with_results"] or 0) > 1]
        if a == "cohort_matrix":
            out = [v for _, v in sorted(sets.items())]
            out += [[f] for f in structured.field if reg.loc[f, "answer_format"] == "one"]
            return out
        if a == "text":
            return [[f] for f in coded + written]
        if a == "text_survey":
            return [["CODE:behaviour", h] for h in headline] + [["CODE:behaviour", "CODE:lexicon"] + v for v in retired_v3]
        if a == "threads":
            return [["THREAD-GRAPH"]]
        return []

    pairs = rd(Path("04_analytics_library/pairs.csv"))
    retired_v1 = []
    for r in pairs.itertuples():
        a, b = r.a_measures.split(";")[0], r.b_measures.split(";")[0].split("=")[0]
        retired_v1.append(sorted({a if a in reg.index else a.split("__")[0], b if b in reg.index else b.split("__")[0]}))
    retired_v1 = [p for p in retired_v1 if len(p) == 2]
    retired_v3 = [[r.a_measures.split(";")[0]] for r in pairs.itertuples() if r.a_measures.split(";")[0] in reg.index]

    # ---- rules -------------------------------------------------------------------------------------------------------
    def test(m, fields):
        """Return (status, failed_rules, conditions)."""
        failed, cond = [], []
        rows = [reg.loc[f] for f in fields if f in reg.index]
        fmts = m["formats"].split(";")
        if m["arity"] not in ("threads",) and m["formats"] != "any":
            if any(r.answer_format not in fmts for r in rows):
                return "not_applicable", ["R10"], []
        if m.get("gates", "any") != "any" and not any(r.gate.replace(" (input)", "") in m["gates"].split(";") for r in rows):
            return "not_applicable", ["R13"], []
        if m["needs_respondent_level"] == "yes" and any(r.respondent_level != "yes" for r in rows):
            failed.append("R04")
        if m["min_level"] in LEVELS:
            if any(r.level in LEVELS and LEVELS[r.level] < LEVELS[m["min_level"]] for r in rows):
                failed.append("R02")
        if m["needs_partition"] == "yes" and any(r.partition != "yes" for r in rows):
            failed.append("R03")
        if any((r.base_all or "0").isdigit() and int(r.base_all or 0) < MIN_N for r in rows):
            failed.append("R05")
        if m["arity"] == "pair_cross" and m["operation"] in ("difference", "ratio"):
            failed.append("R01")
        if m["arity"] in ("set", "pair_same_set") and len({(r.comparable_set) for r in rows}) > 1:
            failed.append("R11")
        if m["arity"] == "text_survey" and m["operation"] in ("difference", "ratio", "test", "compare"):
            failed.append("R08")
        if failed:
            return "rejected", failed, []
        if m["operation"] == "quantify_money":
            return "needs_data", ["R09"], []
        if m["arity"] in ("cohort", "cohort_matrix") and m["operation"] in ("test",):
            cond.append(f"R06: use non-overlapping groups only (overlapping dimensions: {'; '.join(overlapping)})")
        if m["arity"] in ("cohort_matrix", "pair_cross") and m["operation"] in ("associate", "model"):
            cond.append("R07: describes groups, not individuals (ecological)")
        if m["operation"] == "interpret":
            cond.append("R12: interpretation only; states no quantity of its own")
        if m["arity"] in ("cohort", "cohort_matrix"):
            cond.append("R05: groups below n = 25 shown, not compared")
        return ("valid_with_condition" if cond else "valid"), [], cond

    valid, rejected, na = [], [], Counter()
    for m in methods:
        for fields in candidates(m):
            status, failed, cond = test(m, fields)
            cid = f"{m['method_id']}:{'+'.join(fields)}"
            base = {"combo_id": cid, "method_id": m["method_id"], "discipline": m["discipline"], "method": m["method"],
                    "fields": "+".join(fields), "status": status}
            if status == "not_applicable":
                na[m["method_id"]] += 1
            elif status == "rejected":
                rejected.append({**base, "rules": ";".join(failed), "reason": " | ".join(rules.loc[r, "statement"] for r in failed)})
            else:
                valid.append({**base, "conditions": " | ".join(cond) if cond else (rules.loc["R09", "statement"] if status == "needs_data" else ""),
                              "question": m["question"], "output": m["output"]})
    V, R = pd.DataFrame(valid), pd.DataFrame(rejected)

    # ---- regression test: the two retired analyses must be rejected --------------------------------------------------
    rej = set(R.combo_id)
    v1_ids = [f"DS08:{'+'.join(p)}" for p in retired_v1]
    v3_ids = [f"QL05:{'+'.join(['CODE:behaviour', 'CODE:lexicon'] + v)}" for v in retired_v3]
    missing = [c for c in v1_ids + v3_ids if c not in rej]
    if missing:
        print("ERROR: retired analyses not rejected:", missing[:5], file=sys.stderr)
        return 2

    V.to_csv(INV / "valid.csv", index=False, lineterminator="\n")
    R.to_csv(INV / "rejected.csv", index=False, lineterminator="\n")

    # ---- summary -----------------------------------------------------------------------------------------------------
    disc = sorted({m["discipline"] for m in methods})
    L = ["# Analytics inventory — summary", "", "Generated by `scripts/p6_build_inventory.py` from `data_register.csv`, "
         "`method_register.csv` and `rules.csv`. Do not edit by hand.", "",
         f"**{len(methods)} methods** from {len(disc)} disciplines × **{len(reg)} fields** → **{len(V)} usable combinations** "
         f"({int((V.status == 'valid').sum())} valid, {int((V.status == 'valid_with_condition').sum())} valid with a stated condition, "
         f"{int((V.status == 'needs_data').sum())} need outside data) and **{len(R)} rejected**, each with the rule it breaks. "
         f"{sum(na.values())} pairings were not applicable (the method does not accept the field's answer format) and are counted only.", "",
         "**Regression test passed:** all " + str(len(v1_ids)) + " pairs of the retired V1 ledger are rejected (R01), and the retired "
         "V3 felt-vs-said comparison is rejected (R08).", "",
         "## By discipline", "", "| Discipline | Methods | Usable | Rejected |", "|---|---|---|---|"]
    for d in disc:
        ids = [m["method_id"] for m in methods if m["discipline"] == d]
        L.append(f"| {d} | {len(ids)} | {int(V.method_id.isin(ids).sum())} | {int(R.method_id.isin(ids).sum()) if len(R) else 0} |")
    rc = Counter(r for x in R.rules for r in x.split(";")) if len(R) else Counter()
    L += ["", "## Why combinations are rejected", "", "| Rule | Statement | Combinations |", "|---|---|---|"]
    for rid in rules.index:
        if rid in rc:
            L.append(f"| {rid} | {rules.loc[rid, 'statement']} | {rc[rid]} |")
    blocked = [m for m in methods if not V.method_id.isin([m["method_id"]]).any()]
    L += ["", "## Methods this data cannot support yet", "",
          "No valid combination exists for these methods. The rule that blocks each says what data would unlock it.", "",
          "| Method | Discipline | Blocked by | What would unlock it |", "|---|---|---|---|"]
    unlock = {"R04": "respondent-level answers (the schema already reserves the slot, ADR-009)", "R01": "the same attribute measured twice in one question set",
              "R08": "a written question that asks about the same concept as the survey question", "R03": "a one-answer version of the question",
              "R02": "an interval-scaled version of the question", "R09": "revenue, cost or deal-value data"}
    for m in blocked:
        why = R[R.method_id == m["method_id"]].rules.str.split(";").explode().value_counts().index.tolist() if len(R) else []
        L.append(f"| {m['method_id']} {m['method']} | {m['discipline']} | {', '.join(why) or 'not applicable to any field'} | "
                 f"{'; '.join(unlock.get(w, '') for w in why if unlock.get(w)) or '—'} |")
    needs = V[V.status == "needs_data"]
    L += ["", f"Methods needing outside data: {', '.join(sorted(set(needs.method_id)))} ({len(needs)} combinations).", "",
          "## Usable combinations per method", "", "| Method | Discipline | Usable | Condition |", "|---|---|---|---|"]
    for m in methods:
        g = V[V.method_id == m["method_id"]]
        if len(g):
            c = sorted({x.split(':')[0] for cs in g.conditions if cs for x in cs.split(" | ") if x.startswith("R")})
            L.append(f"| {m['method_id']} {m['method']} | {m['discipline']} | {len(g)} | {', '.join(c) or '—'} |")
    L.append("")
    (INV / "summary.md").write_text("\n".join(L), encoding="utf-8")
    M = ["# Method register", "", "Authored (INFERRED): `method_register.csv`. Rendered by `scripts/p6_build_inventory.py`.", "",
         "| ID | Discipline | Method | Question it answers | Needs | Source | Origin |", "|---|---|---|---|---|---|---|"]
    for m in methods:
        needs_ = f"{m['arity']}; formats {m['formats']}; level ≥ {m['min_level']}" + ("; partition" if m["needs_partition"] == "yes" else "") + \
                 ("; each person's answers" if m["needs_respondent_level"] == "yes" else "")
        M.append(f"| {m['method_id']} | {m['discipline']} | {m['method']} | {m['question']} | {needs_} | {m['citation']} | {m['origin']} |")
    M.append("")
    (INV / "methods.md").write_text("\n".join(M), encoding="utf-8")
    print(f"methods={len(methods)} disciplines={len(disc)} usable={len(V)} rejected={len(R)} not_applicable={sum(na.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
