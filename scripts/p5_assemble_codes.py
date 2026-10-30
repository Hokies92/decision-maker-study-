#!/usr/bin/env python3
"""p5_assemble_codes.py — assemble the full code table from its authored parts (P5.S05).

Parts (compact, INFERRED), each with its coder label:
    coding/codes_sample_s03_compact.psv   claude-s03   the S03 inductive sample (220)
    coding/precoded.psv                   claude-rule  rule-assisted not-codable codes (p5_precode.py)
    coding/codes_{A,B,C,D}_compact.psv    claude-s05   hand coding of the work list, by question block
Each part is expanded and validated by p5_expand_codes.py; together they must cover all 1,697 answers exactly once.
Output: 05_open_ended/codes.csv (long: answer_id, respid, item, thread, frame, layer, code, polarity, primary, coder, provenance)
Usage: python3 -I scripts/p5_assemble_codes.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

D = Path("05_open_ended")
PARTS = [("coding/codes_sample_s03_compact.psv", "claude-s03"), ("coding/precoded.psv", "claude-rule")] + \
        [(f"coding/codes_{k}_compact.psv", "claude-s05") for k in "ABCD"]


def main() -> int:
    frames = []
    with tempfile.TemporaryDirectory() as td:
        for rel, coder in PARTS:
            out = Path(td) / (Path(rel).stem + ".csv")
            p = subprocess.run([sys.executable, "-I", "scripts/p5_expand_codes.py", str(D / rel), str(out), coder],
                               capture_output=True, text=True)
            if p.returncode != 0:
                print(f"ERROR in {rel}:\n{p.stderr}", file=sys.stderr)
                return 2
            frames.append(pd.read_csv(out, dtype=str, keep_default_na=False))
    codes = pd.concat(frames, ignore_index=True)
    corpus = pd.read_csv(D / "corpus.csv", dtype=str, keep_default_na=False)
    per = codes.groupby("answer_id").coder.nunique()
    dup = per[per > 1].index.tolist()
    missing = sorted(set(corpus.answer_id) - set(codes.answer_id))
    extra = sorted(set(codes.answer_id) - set(corpus.answer_id))
    if dup or missing or extra:
        print(f"ERROR: coded by more than one part {dup[:5]}; missing {missing[:5]} ({len(missing)}); extra {extra[:5]}",
              file=sys.stderr)
        return 2
    order = {a: i for i, a in enumerate(corpus.answer_id)}
    layer_order = {k: i for i, k in enumerate(["notcodable", "gate", "behaviour", "servqual", "meansend", "attribution",
                                               "valence", "lexicon"])}
    codes["_a"] = codes.answer_id.map(order)
    codes["_l"] = codes.layer.map(layer_order)
    codes["_k"] = range(len(codes))
    codes = codes.sort_values(["_a", "_l", "_k"], kind="stable").drop(columns=["_a", "_l", "_k"])
    codes.to_csv(D / "codes.csv", index=False, lineterminator="\n")
    nc = codes[codes.layer == "notcodable"].answer_id.nunique()
    print(f"answers={codes.answer_id.nunique()} code_rows={len(codes)} not_codable={nc} coded={codes.answer_id.nunique() - nc}",
          codes.drop_duplicates("answer_id").coder.value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
