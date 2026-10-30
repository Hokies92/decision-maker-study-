#!/usr/bin/env python3
"""p5_draw_sample.py — the stratified random sample for the inductive coding pass (P5.S03).

From corpus.csv: per question Q21–Q25, 36 substantive answers + 4 non-answers or refusals; 20 'please specify'
answers — 220 in all. Fixed seed. Output: 05_open_ended/coding/sample_s03.csv (answer_id, item, frame, stratum, text).
Usage: python3 -I scripts/p5_draw_sample.py
"""
import sys
from pathlib import Path

import pandas as pd

SEED = 20261029
OUT = Path("05_open_ended/coding/sample_s03.csv")


def main() -> int:
    c = pd.read_csv("05_open_ended/corpus.csv", dtype=str, keep_default_na=False)
    c["blank"] = (c.non_answer == "True") | (c.refusal == "True")
    parts = []
    for q in ["Q21", "Q22", "Q23", "Q24", "Q25"]:
        g = c[c.item == q]
        parts.append(g[~g.blank].sample(36, random_state=SEED).assign(stratum=f"{q} substantive"))
        parts.append(g[g.blank].sample(4, random_state=SEED).assign(stratum=f"{q} empty"))
    sp = c[c.frame == "specify"]
    parts.append(sp.sample(20, random_state=SEED).assign(stratum="specify"))
    s = pd.concat(parts)[["answer_id", "item", "frame", "stratum", "text"]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    s.to_csv(OUT, index=False, lineterminator="\n")
    print(f"sample={len(s)}", s.stratum.value_counts().sort_index().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
