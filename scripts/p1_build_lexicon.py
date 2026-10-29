#!/usr/bin/env python3
"""p1_build_lexicon.py — the asymmetry lexicon, pass 1 (instrument wording).

For each concept: the vendor's term next to the decision-maker's own words from the
survey, and — where the survey has no customer-side word — a gap for Scott to name.

Inputs (read-only):
    01_instrument_reconstruction/lexicon_entries.csv        (authored)
    01_instrument_reconstruction/question_map.csv           (VERBATIM wording)
    01_instrument_reconstruction/derived/table_blocks.csv   (VERBATIM option labels)
Outputs:
    01_instrument_reconstruction/asymmetry_lexicon.csv
    01_instrument_reconstruction/asymmetry_lexicon.md

Reference forms in decision_maker_refs (';'-separated):
    Q12_6        the item's label (or stem if it has no label)
    Q5:stem      the question's stem
    Q14:opt2     option 2 of the question's answer list
Every reference must resolve, or the script stops (exit 2).

Provenance: decision-maker words VERBATIM (cited); vendor terms INFERRED (Claude, common
trade usage, quoted to expose the vendor side); gaps INFERRED descriptions — names are Scott's.

Usage: python3 -I scripts/p1_build_lexicon.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

RD = Path("01_instrument_reconstruction")
CANON = "Industry 7"
OUT_CSV, OUT_MD = RD / "asymmetry_lexicon.csv", RD / "asymmetry_lexicon.md"
GROUP_ORDER = ["Target", "Baseline", "Access", "Agree", "Vision", "Case", "Not yes", "Relationship"]


def main() -> int:
    entries = list(csv.DictReader((RD / "lexicon_entries.csv").open(encoding="utf-8")))
    qmap = {q["item_id"]: q for q in csv.DictReader((RD / "question_map.csv").open(encoding="utf-8"))}
    blocks = {b["item_id"]: b for b in csv.DictReader((RD / "derived/table_blocks.csv").open(encoding="utf-8"))
              if b["sheet"] == CANON and b["item_id"]}
    first_item = {}
    for q in qmap.values():
        first_item.setdefault(q["thread_id"], q)

    def thread_first(qid):
        return first_item.get(f"T-{qid[0]}{int(qid[1:]):02d}")

    errors, rows = [], []

    def resolve(ref):
        m = re.fullmatch(r"([QS]\d+)(?:_(\w+))?(?::(stem|opt(\d+)))?", ref)
        if not m:
            return None, None
        base, sub, kind, n = m.groups()
        item_id = f"{base}_{sub}" if sub else base
        if kind == "stem":
            q = qmap.get(item_id) or thread_first(base)
            return (q["stem"], q["source_cite"]) if q else (None, None)
        if kind and kind.startswith("opt"):
            b = blocks.get(item_id) or blocks.get(f"{item_id}_PurchaseLimit")
            if not b:
                return None, None
            opts = json.loads(b["options_json"])
            k = int(n) - 1
            if not 0 <= k < len(opts):
                return None, None
            return opts[k], f"SRC-002 {CANON}!A{int(b['first_option_row']) + k}"
        q = qmap.get(item_id)
        if not q:
            return None, None
        return (q["item_label"] or q["stem"]), q["source_cite"]

    for e in entries:
        phrases = []
        for ref in [r.strip() for r in e["decision_maker_refs"].split(";") if r.strip()]:
            text, cite = resolve(ref)
            if text is None:
                errors.append(f"{e['entry_id']}: reference '{ref}' does not resolve")
                continue
            phrases.append({"ref": ref, "text": text, "cite": cite})
        rows.append({**e, "phrases": phrases})

    l23 = next(r for r in rows if r["entry_id"] == "L23")
    if not any("pulled back" in p["text"] for p in l23["phrases"]):
        errors.append("L23: 'pulled back' not found in the cited Q15 wording")
    if errors:
        for x in errors:
            print("ERROR:", x, file=sys.stderr)
        return 2

    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["entry_id", "group", "concept", "vendor_term", "vendor_prov",
                                           "decision_maker_words", "decision_maker_cites", "words_prov",
                                           "gap", "gap_prov", "gap_name_by_scott", "note"], lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({"entry_id": r["entry_id"], "group": r["group"], "concept": r["concept"],
                        "vendor_term": r["vendor_term"], "vendor_prov": "INFERRED",
                        "decision_maker_words": " | ".join(p["text"] for p in r["phrases"]),
                        "decision_maker_cites": " | ".join(f"{p['ref']} ({p['cite']})" for p in r["phrases"]),
                        "words_prov": "VERBATIM", "gap": r["gap"], "gap_prov": "INFERRED" if r["gap"] else "",
                        "gap_name_by_scott": "", "note": r["note"]})

    grouped = OrderedDict((g, []) for g in GROUP_ORDER)
    for r in rows:
        grouped.setdefault(r["group"], []).append(r)
    gaps = [r for r in rows if r["gap"]]
    L = ["# Asymmetry Lexicon — pass 1 (instrument wording)", "",
         "Generated by `scripts/p1_build_lexicon.py` from `lexicon_entries.csv`. Do not edit by hand.", "",
         "The same moment, named from each side of the table. **Vendor terms** are the trade's vocabulary, "
         "quoted to expose the vendor side (Claude, `INFERRED`). **Decision-maker words** are the survey's own "
         "wording, cited (`VERBATIM`). **Gaps** mark experiences the survey measures but has no customer-side "
         "name for — names to be supplied by Scott.", "",
         f"**{len(rows)} concepts**; {len(rows) - len(gaps)} have decision-maker words; **{len(gaps)} gaps** to name.", "",
         "Pass 2 (Phase 5) adds the decision-makers' own words from ~1,600 open-ended answers.", ""]
    for g, rs in grouped.items():
        if not rs:
            continue
        L += [f"## {g}", "", "| Concept | Vendor says | Decision-maker says (survey wording) | Gap |", "|---|---|---|---|"]
        for r in rs:
            words = "<br>".join(f"“{p['text'].rstrip('.')}” ({p['ref']})" for p in r["phrases"])
            gap = f"**GAP:** {r['gap']}" if r["gap"] else ""
            cells = [r["concept"], r["vendor_term"].replace(";", ","), words, gap]
            L.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
        L.append("")
    L += ["## Gaps for Scott to name", "", "| # | Concept | What is unnamed |", "|---|---|---|"]
    for r in gaps:
        L.append(f"| {r['entry_id']} | {r['concept']} | {r['gap']} |")
    L.append("")
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"concepts={len(rows)} gaps={len(gaps)} phrases={sum(len(r['phrases']) for r in rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
