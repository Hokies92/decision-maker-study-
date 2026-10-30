#!/usr/bin/env python3
"""p5_expand_codes.py — expand a compact hand-coding file into the long code table, validating every code.

Compact input (pipe-separated, authored, INFERRED): answer_id|nc|gate|behaviour|servqual|meansend|attribution|valence|lexicon
    nc         one N- code, or empty; if set, every other field must be empty
    gate       CASE, AGREE, … (prefix G- added); ';'-separated, first = primary
    behaviour  B-CODE:+ or B-CODE:- ; first = primary
    servqual   REL RESP ASSUR EMP TANG NONE; meansend A C V; attribution V S P O N; valence + - ± 0; lexicon L01…
Output: long CSV — answer_id, respid, item, thread, frame, layer, code, polarity, primary, coder, provenance.
Checks: every answer_id in the corpus; every code in coding_frame.md (via the frame builder's rows); polarity on behaviour
codes only; each answer once; not-codable answers carry nothing else. Verbatim examples in the frame must occur in the
answer they cite. Exit 2 on any failure.
Usage: python3 -I scripts/p5_expand_codes.py <compact.psv> <out.csv> <coder>
"""
import csv
import re
import sys
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from p5_build_coding_frame import rows as frame_rows  # noqa: E402

SQ = {"REL": "S-RELIABILITY", "RESP": "S-RESPONSIVENESS", "ASSUR": "S-ASSURANCE", "EMP": "S-EMPATHY", "TANG": "S-TANGIBLES", "NONE": "S-NONE"}
ME = {"A": "M-ATTRIBUTE", "C": "M-CONSEQUENCE", "V": "M-VALUE"}
AT = {"V": "A-VENDOR", "S": "A-SALESPERSON", "P": "A-PRODUCT", "O": "A-OWN", "N": "A-NONE"}
VA = {"+": "V-POS", "-": "V-NEG", "±": "V-MIXED", "0": "V-NEUTRAL"}


def main() -> int:
    src, out, coder = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    frame = {r["code"]: r for r in frame_rows()}
    corpus = pd.read_csv("05_open_ended/corpus.csv", dtype=str, keep_default_na=False).set_index("answer_id")
    errs, rows, seen = [], [], set()
    for line in csv.DictReader(src.open(encoding="utf-8"), delimiter="|"):
        aid = line["answer_id"]
        if aid not in corpus.index:
            errs.append(f"{aid}: not in corpus"); continue
        if aid in seen:
            errs.append(f"{aid}: coded twice"); continue
        seen.add(aid)
        a = corpus.loc[aid]
        base = {"answer_id": aid, "respid": a.respid, "item": a["item"], "thread": a.thread, "frame": a.frame,
                "coder": coder, "provenance": "INFERRED"}
        items = []
        if line["nc"]:
            if any(line[k] for k in ("gate", "behaviour", "servqual", "meansend", "attribution", "valence", "lexicon")):
                errs.append(f"{aid}: not-codable answer carries other codes")
            items.append(("notcodable", line["nc"], "", True))
        else:
            for layer, field, mp in (("gate", "gate", None), ("servqual", "servqual", SQ), ("meansend", "meansend", ME),
                                     ("attribution", "attribution", AT), ("valence", "valence", VA), ("lexicon", "lexicon", None)):
                for k, v in enumerate([x for x in line[field].split(";") if x]):
                    code = ("G-" + v) if layer == "gate" else (mp[v] if mp else v)
                    items.append((layer, code, "", k == 0))
            for k, v in enumerate([x for x in line["behaviour"].split(";") if x]):
                m = re.fullmatch(r"(B-[A-Z\-]+):([+-])", v)
                if not m:
                    errs.append(f"{aid}: behaviour '{v}' needs a polarity"); continue
                items.append(("behaviour", m.group(1), m.group(2), k == 0))
            if not any(i[0] == "gate" for i in items) or not any(i[0] == "valence" for i in items):
                errs.append(f"{aid}: codable answer needs a gate and a valence")
        for layer, code, pol, prim in items:
            f = frame.get(code)
            if f is None or f["layer"] != layer:
                errs.append(f"{aid}: {code} not a {layer} code in the frame"); continue
            rows.append({**base, "layer": layer, "code": code, "polarity": pol, "primary": prim})
    for code, f in frame.items():
        m = re.search(r"example ([A-Za-z0-9_]+-R\d{3})", f["source"])
        if f["example"] and m:
            aid = m.group(1)
            if aid not in corpus.index or f["example"] not in corpus.loc[aid].text:
                errs.append(f"frame example for {code} not found verbatim in {aid}")
    if errs:
        for e in errs:
            print("ERROR:", e, file=sys.stderr)
        return 2
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False, lineterminator="\n")
    print(f"answers={len(seen)} code_rows={len(df)}", df.layer.value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
