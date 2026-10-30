#!/usr/bin/env python3
"""p5_draw_recode_sample.py — the blind re-code sample for the consistency check (P5.S06, M17).

200 answers drawn from all 1,697 (including rule-coded ones), stratified by question: 36 each from Q21–Q25 and
20 'please specify'. Seed differs from the S03 sample. The file given to the second coder holds no codes:
answer_id, item, question wording, frame, text.
Output: 05_open_ended/coding/recode_sample.csv
Usage: python3 -I scripts/p5_draw_recode_sample.py
"""
import sys
from pathlib import Path

import pandas as pd
from lxml import etree

SEED = 1954          # Flanagan (1954)
OUT = Path("05_open_ended/coding/recode_sample.csv")
NS = {"d": "https://growthenablement.com/ns/dms/v1"}


def main() -> int:
    c = pd.read_csv("05_open_ended/corpus.csv", dtype=str, keep_default_na=False)
    doc = etree.parse("03_schema/examples/respondents_open_ended.xml")
    wording = {}
    for i in doc.xpath("//d:Item", namespaces=NS):
        stem = i.findtext(f"{{{NS['d']}}}Stem") or ""
        label = i.findtext(f"{{{NS['d']}}}Label") or ""
        wording[i.get("id")] = (label + " — " if label and label != stem else "") + stem
    parts = [c[c.item == q].sample(36, random_state=SEED) for q in ["Q21", "Q22", "Q23", "Q24", "Q25"]]
    parts.append(c[c.frame == "specify"].sample(20, random_state=SEED))
    s = pd.concat(parts)
    s = s.assign(question=s["item"].map(wording))[["answer_id", "item", "question", "frame", "text"]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    s.to_csv(OUT, index=False, lineterminator="\n")
    print(f"recode_sample={len(s)}", s["item"].value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
