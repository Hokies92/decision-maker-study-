#!/usr/bin/env python3
"""p1_build_response_scales.py — every answer list, deduplicated, with order and users.

Inputs (read-only):
    01_instrument_reconstruction/question_map.csv
    01_instrument_reconstruction/derived/table_blocks.csv
    01_instrument_reconstruction/scale_annotations.csv   (authored: names, type, order)
Outputs:
    01_instrument_reconstruction/response_scales.csv   one row per scale
    01_instrument_reconstruction/item_scales.csv       one row per item → scale_id
    01_instrument_reconstruction/response_scales.md    readable summary

Grouping (RECON_DATA):
    single-choice and grid items  → grouped by their exact, ordered option labels
    pick-all-that-apply items     → one selection list per question (its choices)
    open text and "please specify"→ SC-OPEN
Labels are VERBATIM. Points marked non-substantive (don't know, not applicable, other /
please specify) are detected by pattern (RECON_DATA). Scale type, order, and family come
from scale_annotations.csv and carry that file's provenance.

Usage: python3 -I scripts/p1_build_response_scales.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

QMAP = Path("01_instrument_reconstruction/question_map.csv")
BLOCKS = Path("01_instrument_reconstruction/derived/table_blocks.csv")
ANNOT = Path("01_instrument_reconstruction/scale_annotations.csv")
OUT_SCALES = Path("01_instrument_reconstruction/response_scales.csv")
OUT_ITEMS = Path("01_instrument_reconstruction/item_scales.csv")
OUT_MD = Path("01_instrument_reconstruction/response_scales.md")
CANON = "Industry 7"

NON_SUBSTANTIVE = re.compile(
    r"don'?t\s+know|dont\s+know|not\s+applicable|^\s*other\b|please\s+specify", re.I)

SCALE_FIELDS = ["scale_id", "scale_type", "direction", "family", "n_points", "n_substantive",
                "labels", "non_substantive_labels", "label_prov", "grouping_prov",
                "annotation_prov", "rationale", "n_items", "used_by_threads", "used_by_items"]


def thread_sort(t: str) -> tuple:
    return (t[2] != "S", int(t[3:]))


def main() -> int:
    items = list(csv.DictReader(QMAP.open(encoding="utf-8")))
    blocks = {(b["sheet"], b["header_row"]): b for b in csv.DictReader(BLOCKS.open(encoding="utf-8"))}
    annots = list(csv.DictReader(ANNOT.open(encoding="utf-8")))
    by_rep = {a["representative_item"]: a for a in annots}

    groups: "OrderedDict[tuple, list]" = OrderedDict()   # signature -> items
    for it in items:
        qt = it["question_type"]
        if qt in ("single_select", "grid_row"):
            b = blocks[(CANON, it["options_ref"].rsplit(" ", 1)[-1])]
            sig = ("options", tuple(json.loads(b["options_json"])))
        elif qt == "multi_select_option":
            sig = ("selection", it["thread_id"])
        elif qt in ("open_text", "open_text_specify"):
            sig = ("open",)
        else:
            print(f"ERROR: unhandled type {qt} for {it['item_id']}", file=sys.stderr)
            return 2
        groups.setdefault(sig, []).append(it)

    scales, item_rows, errors, used_annots = [], [], [], set()
    for sig, its in groups.items():
        ids = [i["item_id"] for i in its]
        annot = next((by_rep[i] for i in ids if i in by_rep), None)
        if annot is None:
            errors.append(f"no annotation for scale used by {ids[:3]}")
            continue
        if annot["representative_item"] in used_annots:
            errors.append(f"annotation {annot['scale_id']} matched two groups")
        used_annots.add(annot["representative_item"])

        if sig[0] == "options":
            labels = list(sig[1])
        elif sig[0] == "selection":
            labels = [i["item_label"] for i in its]
        else:
            labels = []
        non_sub = [l for l in labels if NON_SUBSTANTIVE.search(l)]
        threads = sorted({i["thread_id"] for i in its}, key=thread_sort)
        scales.append({
            "scale_id": annot["scale_id"], "scale_type": annot["scale_type"],
            "direction": annot["direction"], "family": annot["family"],
            "n_points": len(labels), "n_substantive": len(labels) - len(non_sub),
            "labels": json.dumps(labels, ensure_ascii=False),
            "non_substantive_labels": json.dumps(non_sub, ensure_ascii=False),
            "label_prov": "VERBATIM" if labels else "n/a",
            "grouping_prov": "RECON_DATA", "annotation_prov": annot["provenance"],
            "rationale": annot["rationale"], "n_items": len(its),
            "used_by_threads": ";".join(threads), "used_by_items": ";".join(ids),
        })
        for i in its:
            item_rows.append({"thread_id": i["thread_id"], "item_id": i["item_id"],
                              "scale_id": annot["scale_id"]})

    unused = sorted(set(by_rep) - used_annots)
    if unused:
        errors.append(f"annotations matched no scale: {unused}")
    if len(item_rows) != len(items):
        errors.append(f"{len(items)} items but {len(item_rows)} assigned")
    if len({s['scale_id'] for s in scales}) != len(scales):
        errors.append("duplicate scale_id")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    with OUT_SCALES.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SCALE_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(scales)
    with OUT_ITEMS.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["thread_id", "item_id", "scale_id"], lineterminator="\n")
        w.writeheader()
        w.writerows(item_rows)

    # Markdown
    types = defaultdict(int)
    for s in scales:
        types[s["scale_type"]] += 1
    shared = [s for s in scales if len(s["used_by_threads"].split(";")) > 1]
    lines = [
        "# Response Scales",
        "",
        "Generated by `scripts/p1_build_response_scales.py`. Do not edit by hand.",
        "",
        "Labels `VERBATIM`; grouping `RECON_DATA` (identical ordered labels = one scale); "
        "type, order, and family per `scale_annotations.csv` (provenance shown per scale).",
        "",
        f"**{len(scales)} scales** covering {len(item_rows)} items. By type: "
        + ", ".join(f"{k} {v}" for k, v in sorted(types.items())) + ".",
        "",
        "## Scales shared across questions",
        "",
        "| Scale | Items | Questions | Labels |",
        "|---|---|---|---|",
    ]
    for s in shared:
        lab = " / ".join(json.loads(s["labels"])) or "(free text)"
        q = ", ".join(t[2] + str(int(t[3:])) for t in s["used_by_threads"].split(";"))
        lines.append(f"| {s['scale_id']} | {s['n_items']} | {q} | {lab} |")
    fams = defaultdict(list)
    for s in scales:
        fams[s["family"]].append(s["scale_id"])
    lines += ["", "## Scale families (same construct, different wording or length)", "",
              "| Family | Scales |", "|---|---|"]
    for f, ids in fams.items():
        if len(ids) > 1:
            lines.append(f"| {f} | {', '.join(ids)} |")
    lines += ["", "## All scales", "",
              "| Scale | Type | Order | Points (substantive) | Used by | Labels | Order provenance |",
              "|---|---|---|---|---|---|---|"]
    for s in scales:
        labs = json.loads(s["labels"])
        lab = " / ".join(labs) if len(labs) <= 10 else " / ".join(labs[:8]) + f" / … ({len(labs)} total)"
        q = ", ".join(t[2] + str(int(t[3:])) for t in s["used_by_threads"].split(";"))
        lab = lab.replace("|", "\\|") or "(free text)"
        lines.append(f"| {s['scale_id']} | {s['scale_type']} | {s['direction']} | "
                     f"{s['n_points']} ({s['n_substantive']}) | {q} | {lab} | {s['annotation_prov']} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"scales={len(scales)} items={len(item_rows)} shared={len(shared)}")
    print("types:", dict(sorted(types.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
