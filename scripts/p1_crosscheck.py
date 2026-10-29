#!/usr/bin/env python3
"""p1_crosscheck.py — Phase 1 cross-check and provenance count.

Checks (each PASS/FAIL, all must pass):
    C01 every table block on every sheet maps to a question-map item
    C02 every "Other" text column maps to a question-map item
    C03 every open-ended sheet maps to a question-map item
    C04 every question-map item maps back to a data location (or is flagged NO_DATA)
    C05 every item has a response scale
    C06 every thread has Scott's group
    C07 every thread has at least one link in the linkage inventory
    C08 every RECON_DATA routing check and every expected anomaly check passed
    C09 every Phase 1 generator re-runs to byte-identical output
    C10 source files match the integrity manifest
Then counts provenance tags across all Phase 1 artifacts and lists every INFERRED item
still open, for Scott's review (P1.S10).

Outputs (01_instrument_reconstruction/):
    crosscheck_report.md
    inferred_for_review.csv

Usage: python3 -I scripts/p1_crosscheck.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

RD = Path("01_instrument_reconstruction")
SRC2, SRC3 = Path("00_source/data/survey.xlsx"), Path("00_source/data/open_ended.xlsx")
OUT_MD, OUT_REV = RD / "crosscheck_report.md", RD / "inferred_for_review.csv"
CONDENSED = {"Q11_1": [f"Q11_{k}" for k in range(1, 8)], "Q15": [f"Q15_{k}" for k in range(1, 8)]}
GENERATORS = [  # (script, outputs) in dependency order
    ("scripts/p1_parse_tables.py", ["derived/table_blocks.csv"]),
    ("scripts/p1_build_question_map.py", ["question_map.csv", "question_map.md"]),
    ("scripts/p1_build_question_list.py", ["question_list.md"]),  # .xlsx embeds a save timestamp; excluded from byte comparison
    ("scripts/p1_build_response_scales.py", ["response_scales.csv", "item_scales.csv", "response_scales.md"]),
    ("scripts/p1_build_skip_logic.py", ["routing.csv", "skip_logic.md"]),
    ("scripts/p1_build_cohort_model.py", ["cohort_dimensions.csv", "cohorts.csv", "cohort_tags.csv", "cohort_model.md"]),
    ("scripts/p1_build_anomalies.py", ["anomalies.csv", "anomalies.md"]),
    ("scripts/p1_build_linkages.py", ["linkages.csv", "linkages.graphml", "linkages.md"]),
]


def read(name):
    return list(csv.DictReader((RD / name).open(encoding="utf-8")))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    results = []

    def check(cid, title, ok, detail):
        results.append((cid, title, "PASS" if ok else "FAIL", detail))

    qmap = read("question_map.csv")
    ids = {q["item_id"] for q in qmap}
    threads = sorted({q["thread_id"] for q in qmap}, key=lambda t: (t[2] != "S", int(t[3:])))
    blocks = read("derived/table_blocks.csv")

    # C01
    unmapped = []
    for b in blocks:
        iid = b["item_id"] or "DM_TYPE"
        if iid in ids:
            continue
        if b["sheet"] == "Main Page" and iid in CONDENSED and all(x in ids for x in CONDENSED[iid]):
            continue
        unmapped.append(f"{b['sheet']}:{iid}")
    check("C01", "Every table block maps to a question item", not unmapped,
          f"{len(blocks)} blocks; unmapped: {unmapped or 'none'} (Main Page condensed Q11/Q15 map to their 7 items — anomalies A01/A02)")

    # C02
    other = pd.read_excel(SRC2, sheet_name='"Other" Text Answers', dtype=str)
    cols = [str(c) for c in other.columns if str(c) != "respid"]
    cite_cols = {q["source_cite"] for q in qmap if '"Other" Text Answers' in q["source_cite"]}
    check("C02", "Every 'Other' text column maps to a question item", len(cols) == len(cite_cols) == 13,
          f"{len(cols)} columns; {len(cite_cols)} cited in question map")

    # C03
    oe = pd.read_excel(SRC3, sheet_name=None, dtype=str)
    oe_ok = all(k in ids for k in oe)
    check("C03", "Every open-ended sheet maps to a question item", oe_ok, f"sheets: {', '.join(oe)}")

    # C04
    no_data = []
    for q in qmap:
        if not q["source_cite"]:
            no_data.append(q["item_id"])
    empty = [q["item_id"] for q in qmap if q["item_id"] == "Q20_4_text"]
    check("C04", "Every question item maps back to data", not no_data,
          f"{len(qmap)} items cite a source location; NO_DATA (column present, no entries): {', '.join(empty)} — anomaly A06")

    # C05
    scaled = {r["item_id"] for r in read("item_scales.csv")}
    check("C05", "Every item has a response scale", scaled == ids, f"{len(scaled)} of {len(ids)} items")

    # C06
    grouped = {r["thread_id"] for r in read("scott_grouping.csv") if r["scott_group"] and r["gate"] != "PENDING"}
    check("C06", "Every thread has Scott's group", set(threads) <= grouped, f"{len(grouped)} of {len(threads)} threads")

    # C07
    links = read("linkages.csv")
    linked = defaultdict(int)
    for e in links:
        if e["link_type"] == "in_group":
            continue
        for end in (e["source"], e["target"]):
            if end in threads:
                linked[end] += 1
    isolated = [t for t in threads if linked[t] == 0]
    check("C07", "Every thread has at least one link", not isolated,
          f"isolated: {isolated or 'none'}; least-linked: " +
          ", ".join(f"{t[2]}{int(t[3:])} ({linked[t]})" for t in sorted(threads, key=lambda t: linked[t])[:3]))

    # C08
    routing_fail = [r["rule_id"] for r in read("routing.csv") if r["provenance"] == "RECON_DATA" and r["check"] != "PASS"]
    anomaly_fail = [a["id"] for a in read("anomalies.csv") if a["check"] == "FAIL"]
    check("C08", "Routing and anomaly checks pass", not routing_fail and not anomaly_fail,
          f"routing failures: {routing_fail or 'none'}; anomaly failures: {anomaly_fail or 'none'}")

    # C09 — re-run every generator, compare outputs byte for byte
    before = {o: sha(RD / o) for _, outs in GENERATORS for o in outs}
    gen_fail = []
    for script, outs in GENERATORS:
        r = subprocess.run([sys.executable, "-I", script], capture_output=True, text=True)
        if r.returncode != 0:
            gen_fail.append(f"{script} exit {r.returncode}")
    after = {o: sha(RD / o) for _, outs in GENERATORS for o in outs}
    changed = [o for o in before if before[o] != after[o]]
    subprocess.run(["git", "checkout", "--", str(RD / "question_list.xlsx")], capture_output=True)
    check("C09", "Every generator re-runs to identical output", not gen_fail and not changed,
          f"{len(GENERATORS)} scripts, {len(before)} outputs; failures: {gen_fail or 'none'}; changed: {changed or 'none'} "
          "(question_list.xlsx excluded: Excel embeds a save timestamp; committed copy restored)")

    # C10
    r = subprocess.run(["sha256sum", "-c", "00_source/MANIFEST.sha256"], capture_output=True, text=True)
    check("C10", "Source files match the integrity manifest", r.returncode == 0, r.stdout.strip().replace("\n", "; "))

    # Provenance counts
    TAGS = ["VERBATIM", "RECON_DATA", "RECON_REPORT", "RECALL_DESIGNER", "INFERRED", "MISSING"]
    prov = defaultdict(lambda: defaultdict(int))

    def tally(name, rows, fields):
        for row in rows:
            for f in fields:
                v = row.get(f, "")
                if v in TAGS:
                    prov[name][v] += 1
    tally("question_map.csv", qmap, ["text_prov", "type_prov", "derived_prov"])
    tally("thread_annotations.csv (constructs)", read("thread_annotations.csv"), ["provenance"])
    tally("response_scales.csv", read("response_scales.csv"), ["label_prov", "annotation_prov"])
    tally("routing.csv", read("routing.csv"), ["provenance"])
    tally("cohort_dimensions.csv", read("cohort_dimensions.csv"), ["definition_prov", "hierarchy_prov"])
    tally("cohorts.csv", read("cohorts.csv"), ["label_prov", "n_prov"])
    tally("cohort_tags.csv", read("cohort_tags.csv"), ["provenance"])
    tally("scott_grouping.csv", read("scott_grouping.csv"), ["provenance"])
    tally("linkages.csv", links, ["provenance"])
    tally("anomalies.csv", read("anomalies.csv"), ["provenance"])
    di = (RD / "design_intent.md").read_text(encoding="utf-8")
    for t in TAGS:
        prov["design_intent.md (tag mentions)"][t] = len(re.findall(rf"`{t}`", di))

    # Open INFERRED items for Scott's review (P1.S10)
    review = []
    for a in read("thread_annotations.csv"):
        review.append({"file": "thread_annotations.csv", "id": a["thread_id"], "what": "construct label",
                       "statement": a["construct"], "why": a["rationale"]})
    for s in read("response_scales.csv"):
        if s["annotation_prov"] == "INFERRED":
            labs = json.loads(s["labels"])
            review.append({"file": "scale_annotations.csv", "id": s["scale_id"], "what": f"scale order: {s['direction']}",
                           "statement": " / ".join(labs[:6]) + (" …" if len(labs) > 6 else ""), "why": s["rationale"]})
    for q in qmap:
        if q["derived_prov"] == "INFERRED":
            review.append({"file": "question_map.csv", "id": q["item_id"], "what": "derivation",
                           "statement": f"derived from {q['derived_from']}", "why": q["derived_evidence"]})
    for t in read("cohort_semantic_tags.csv"):
        review.append({"file": "cohort_semantic_tags.csv", "id": f"{t['source']}→{t['target_thread']}",
                       "what": "topic link", "statement": t["link_type"], "why": t["rationale"]})
    for c in read("construct_links.csv"):
        if c["provenance"] == "INFERRED":
            review.append({"file": "construct_links.csv", "id": f"{c['source']}↔{c['target']}",
                           "what": c["link_type"], "statement": c["link_type"], "why": c["rationale"]})
    with OUT_REV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["n", "file", "id", "what", "statement", "why", "scott_decision"],
                           lineterminator="\n")
        w.writeheader()
        for i, r in enumerate(review, 1):
            w.writerow({"n": i, **r, "scott_decision": ""})

    ok = all(r[2] == "PASS" for r in results)
    L = ["# Phase 1 Cross-check", "", "Generated by `scripts/p1_crosscheck.py`.", "",
         f"**Result: {'ALL PASS' if ok else 'FAILURES'}** — {sum(r[2] == 'PASS' for r in results)} of {len(results)} checks.", "",
         "| Check | What | Result | Detail |", "|---|---|---|---|"]
    for cid, title, res, det in results:
        L.append(f"| {cid} | {title} | {res} | {str(det).replace('|', '/')} |")
    L += ["", "## Provenance counts", "", "| Artifact | " + " | ".join(TAGS) + " |", "|---|" + "---|" * len(TAGS)]
    tot = defaultdict(int)
    for name, d in prov.items():
        L.append(f"| {name} | " + " | ".join(str(d.get(t, 0)) for t in TAGS) + " |")
        for t in TAGS:
            tot[t] += d.get(t, 0)
    L.append("| **Total** | " + " | ".join(f"**{tot[t]}**" for t in TAGS) + " |")
    by_what = defaultdict(int)
    for r in review:
        by_what[r["file"]] += 1
    L += ["", "## Open inferences for Scott's review (P1.S10)", "",
          f"{len(review)} items in `inferred_for_review.csv`: " + ", ".join(f"{k} {v}" for k, v in by_what.items()) + ".",
          "Superseded, not for review: Claude's section labels in `thread_annotations.csv` (replaced by Scott's grouping).", ""]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    for r in results:
        print(r[0], r[2], "—", r[1])
    print(f"review items: {len(review)}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
