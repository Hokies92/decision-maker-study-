#!/usr/bin/env python3
"""p5_build_corpus.py — one corpus file of every respondent-level text answer, read from the schema instance.

Input: 03_schema/examples/respondents_open_ended.xml (text identical to SRC-002 / SRC-003; P3 C08).
Output: 05_open_ended/corpus.csv — answer_id, respid, item, thread, frame, text (exact), n_chars, n_words,
non_answer (P2.S06 pattern), refusal (declines, '[unintelligible]', keyboard noise — scripted, P5.S02), cite,
key_provenance. answer_id is stable: the item plus the source row.
frame: differentiator (Q21), best (Q22, Q24), worst (Q23, Q25), specify ('please specify' fields).
Usage: python3 -I scripts/p5_build_corpus.py
"""
import re
import sys
from pathlib import Path

import pandas as pd
from lxml import etree

SRC = Path("03_schema/examples/respondents_open_ended.xml")
OUT = Path("05_open_ended/corpus.csv")
NS = {"d": "https://growthenablement.com/ns/dms/v1"}
FRAME = {"Q21": "differentiator", "Q22": "best", "Q23": "worst", "Q24": "best", "Q25": "worst"}
NON_ANSWER = re.compile(r"^\s*(n/?a|none|no|nothing|nil|na|not applicable|don'?t know|dont know|dk|no idea|not sure|unknown|"
                        r"no comment|-+|\.+|\?+|x+)\s*\.?\s*$", re.I)   # same pattern as P2.S06
REFUSAL = re.compile(r"\[unintelligible\]|^\W*(i\s*)?(would\s*|'d\s*)?(still\s*)?(prefer|rather|wish) not\b|"
                     r"\bnot (willing|prepared|possible) to (say|share|answer|name|respond)|"
                     r"^\W*(i\s*)?(can ?not|can't|cant|am unable to|do not want to|do not wish to) (share|say|answer|provide|disclose|respond)|"
                     r"^\s*decline|^\s*no comment|^\s*non disclosure|^\s*commercially sensitive|"
                     r"^\s*\W+\s*$|^\s*[a-z]\s*$|^\s*(?-i:[b-df-hj-np-tv-z]{4,})\s*$|^\s*(\w{1,3})\1+\s*$|^\s*(not sure|unsure|no idea|don.?t know)\W*$", re.I)


def main() -> int:
    doc = etree.parse(str(SRC))
    thread = {i.get("id"): i.getparent().get("id") for i in doc.xpath("//d:Item", namespaces=NS)}
    rows = []
    for a in doc.xpath("//d:TextAnswer", namespaces=NS):
        item, cite, text = a.get("item"), a.get("cite"), a.text
        m = re.search(r"!([A-Z]+)(\d+)$", cite)
        rows.append({"answer_id": f"{item}-R{int(m.group(2)):03d}", "respid": a.getparent().get("respid"), "item": item,
                     "thread": thread[item], "frame": FRAME.get(item, "specify"), "text": text,
                     "n_chars": len(text.strip()), "n_words": len(text.split()),
                     "non_answer": bool(NON_ANSWER.match(text.strip())),
                     "refusal": bool(REFUSAL.search(text.strip())) and not NON_ANSWER.match(text.strip()), "cite": cite,
                     "key_provenance": a.get("keyProvenance") or ""})
    df = pd.DataFrame(rows)
    order = {k: i for i, k in enumerate(["Q21", "Q22", "Q23", "Q24", "Q25"])}
    df["_o"] = df.item.map(lambda i: order.get(i, 9))
    df = df.sort_values(["_o", "item", "answer_id"], kind="stable").drop(columns="_o")
    if df.answer_id.duplicated().any():
        print("ERROR: duplicate answer_id", file=sys.stderr)
        return 2
    df.to_csv(OUT, index=False, lineterminator="\n")
    print(f"answers={len(df)} respondents={df.respid.nunique()} non_answers={int(df.non_answer.sum())} refusals={int(df.refusal.sum())}",
          df.frame.value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
