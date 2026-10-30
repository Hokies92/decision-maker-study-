#!/usr/bin/env python3
"""p5_precode.py — rule-assisted not-codable codes, and the work list for hand coding (P5.S05).

Assigns an N- code by rule where the answer has nothing else to code (coder 'claude-rule', INFERRED):
    N-NONANSWER       corpus non_answer, or a refusal phrase
    N-UNINTELLIGIBLE  '[unintelligible]' or keyboard noise (corpus refusal flag, noise branch)
    N-VALUE           Q20_2_text amounts (digits only)
    N-NAMES-ONLY      the text is only vendor names from the gazetteer, separators and filler words
    N-ROLE-ONLY       Q24/Q25 text is only a contact-role phrase, separators and filler words
    N-REFERENCE       'same', 'same answer', 'see previous', 'as above', 'ditto'
Refusals longer than 80 characters go to hand coding (they may give a reason). Answers already coded in the
P5.S03 sample keep those codes. Everything else goes to the work list.
Outputs: 05_open_ended/coding/precoded.psv, worklist.csv
Usage: python3 -I scripts/p5_precode.py
"""
import csv
import re
import sys
from pathlib import Path

import pandas as pd

D = Path("05_open_ended")
NOISE = re.compile(r"\[unintelligible\]|^\s*\W+\s*$|^\s*[a-z]\s*$|^\s*(?-i:[b-df-hj-np-tv-z]{4,})\s*$|^\s*(\w{1,3})\1+\s*$", re.I)
REFERENCE = re.compile(r"^\W*(same( answer)?( as (above|before|previous( question)?))?|see previous( response| answer)?|as above|"
                       r"ditto( on the last question)?|again|this as well|same as previous( question)?|as previous|"
                       r"same answer as above|i.ve said everything about this as well)\W*$", re.I)
FILLER = r"(?:and|und|et|or|the|their|for|just|1|all|a|an|of|at)"
ROLE = (r"(?:sr\.?\s*)?(?:key\s+)?(?:account|acct|acc|accoutn)\.?\s*(?:manager|manger|mgr|exec(?:utive)?|rep|director|strategist|management)s?|"
        r"consultants?|product\s+specialists?|specialists?|product\s+managers?|executives?|exeutives|ceo|director|sales\s*(?:rep(?:resentative)?s?|"
        r"person|people|man|manager|director|engineer|consultant)?|salesm[ae]n|salesperson|customer\s+service\s+(?:representative|associate)|"
        r"technical\s+(?:account\s+management|specialist|chief|director|consultants?)|it\s+specialist|technician|kam|manager|partner|"
        r"vendor|e-mail|project manager|accountant|regional manager|development manager|sales director|client sales executive|"
        r"technical field engineer|product|account group vp|sr\.? vp|vp|business relationship manager|national business manager|"
        r"engineering team|staff|people|it staff|telesales|clerk")


def main() -> int:
    c = pd.read_csv(D / "corpus.csv", dtype=str, keep_default_na=False)
    vend = [re.compile(r["pattern"], 0 if r["case_sensitive"] == "yes" else re.I)
            for r in csv.DictReader((D / "gazetteer/vendors.csv").open(encoding="utf-8"))]
    sample = {l.split("|")[0] for l in (D / "coding/codes_sample_s03_compact.psv").read_text(encoding="utf-8").splitlines()[1:]}
    role_rx = re.compile(rf"^\W*(?:(?:{ROLE})(?:\s*(?:/|,|&|\+|-|–|and|or|with|and/or)\s*)?)+\W*$", re.I)
    rows, work = [], []
    for a in c.itertuples():
        if a.answer_id in sample:
            continue
        t = a.text.strip()
        code = ""
        if a.item == "Q20_2_text" and re.fullmatch(r"\d+", t):
            code = "N-VALUE"
        elif a.non_answer == "True":
            code = "N-NONANSWER"
        elif a.refusal == "True" and len(t) <= 80:
            code = "N-UNINTELLIGIBLE" if NOISE.search(t) else "N-NONANSWER"
        elif REFERENCE.match(t):
            code = "N-REFERENCE"
        else:
            rest, hits = t, 0
            for rx in vend:
                rest, n = rx.subn(" ", rest)
                hits += n
            rest = re.sub(rf"\b{FILLER}\b", " ", rest, flags=re.I)
            if hits and re.fullmatch(r"[\W\d_]*", rest):
                code = "N-NAMES-ONLY"
            elif a.item in ("Q24", "Q25") and role_rx.match(t) and len(t) <= 60:
                code = "N-ROLE-ONLY"
        if code:
            rows.append(f"{a.answer_id}|{code}|||||||")
        else:
            work.append({"answer_id": a.answer_id, "item": a.item, "frame": a.frame, "text": a.text})
    (D / "coding/precoded.psv").write_text("answer_id|nc|gate|behaviour|servqual|meansend|attribution|valence|lexicon\n" +
                                           "\n".join(rows) + "\n", encoding="utf-8")
    pd.DataFrame(work).to_csv(D / "coding/worklist.csv", index=False, lineterminator="\n")
    from collections import Counter
    print(f"sample={len(sample)} precoded={len(rows)} worklist={len(work)}", dict(Counter(r.split('|')[1] for r in rows)),
          pd.DataFrame(work).item.value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
