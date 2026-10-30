#!/usr/bin/env python3
"""p5_build_index.py — names and roles: who and what each answer names, and a searchable answer file.

Inputs: 05_open_ended/corpus.csv; gazetteer/vendors.csv, gazetteer/people.csv (authored, INFERRED).
Outputs (05_open_ended/index/):
    vendor_mentions.csv   one row per vendor named in an answer: vendor, answer_id, respid, item, frame, matched
    vendor_index.csv      per vendor: mentions in best (Q22, Q24), worst (Q23, Q25), other answers; respondents
    people_mentions.csv   one row per person named (names kept — Scott, D5-4)
    contact_roles.csv     Q24 / Q25: primary-contact role(s) named, by pattern (M12)
    answers_search.csv    every answer with its vendors, people, roles — for search by vendor, person or text
    answers_search.json   the same, for a search page
    unmatched_capitals.csv capitalised words in any answer not covered by a gazetteer or a stop list — reviewed by hand
Usage: python3 -I scripts/p5_build_index.py
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

D = Path("05_open_ended")
OUT = D / "index"
ROLES = [  # (role, pattern) — order matters only for display
    ("account_manager", r"\bacc(oun|out)?n?t?\.?\s*(manager|manger|mgr|exec\w*|rep\w*|director|strategist|group vp)\b|\bacct\.?\s*m(gr|anager)\b|\bacc manager\b|\bkam\b|\bkey account\b|business relationship manager|client executive"),
    ("consultant", r"\bconsultant|\blead partner\b|^\s*partner\s*$"),
    ("product_specialist", r"\bproduct\s*(specialist|manager|person|“?consultant)|^\s*specialist\s*$|^\s*product\s*$"),
    ("executive", r"\bexecutive\b(?!\s*management)|\bexeutives\b|\bexuecutibes\b|\bceo\b|\b(sr\.? )?vp\b|\bvp level\b|\bmanaging director\b|\btop management\b|\bleadership\b|\bhead honcho\b|\boperating officer\b|\bsupplier executive\b|^\s*director\b|\bdirector whom\b|\bdirectors\b|\bthe director\b|\baccount director\b|\bregional director\b|\bcompany owner\b"),
    ("sales_rep", r"\bsales\s*(rep\w*|person|people|man|men|guy|manager\w*|director|engineer|specialist|consultant|team)\b|\bsales(wo)?man\b|\bsalesmen\b|\bsalesperson\b|^\s*sales\s*$|\btelesales\b|\bphone sales\b|\bcold calling\b|\bcommission based sales\b|\bregional sales manager\b|\bregional manager\b|\bnational business manager\b"),
    ("technical", r"\bengineer|\btechnical|\btechnician|\bit specialist\b|\bspecialists?\b(?=.*\btechnical)|\bengineering team\b|\btechnocrats\b|\bdedicated engineers\b"),
    ("customer_service", r"\bcustomer service|\bcustomer represent|\bclerk\b|\bgeneral line\b"),
    ("other_role", r"\boperations person\b|\bunderwriting management\b|\brecruiter\b|\bplacement specialist\b|\bproject manager\b|"
                   r"\bdevelopment manager\b|\bassistant manager\b|\bit staff\b|\bbuyer\b|\baccountant\b|^\s*manager\s*$|^\s*staff\s*$|"
                   r"\bproduction support\b|\boperational and implementation contact\b|^\s*people\s*$|\bwhizz kid\b|\bescalation manager\b"),
]
STOP = set("""I A The They Their We It My Not No None NA Na N Don't I'm I'd I've I'll Can Do Too An Always Best One All Can't He His She Me Most
Many Some Several Usually Often Typically Generally Again Ditto Same Sorry This That These Those When While If Or And For By On To Of With Then There
Very Good Great Poor Lack Lots Only Never Account Manager Product Specialist Specialists Executive Executives Consultant Consultants Sales Rep Customer
Service Director Technical Partner Leadership Unknown Unspecified Unsure Prefer Rather Difficult Commercially Non Disclosure Key Managers Mgr Exec""".split())


def load_gaz(path):
    out = []
    for r in csv.DictReader(path.open(encoding="utf-8")):
        flags = 0 if r["case_sensitive"] == "yes" else re.I
        out.append((list(r.values())[0], re.compile(r["pattern"], flags)))
    return out


def main() -> int:
    c = pd.read_csv(D / "corpus.csv", dtype=str, keep_default_na=False)
    vendors, people = load_gaz(D / "gazetteer/vendors.csv"), load_gaz(D / "gazetteer/people.csv")
    roles = [(n, re.compile(p, re.I)) for n, p in ROLES]
    vm, pm, rm, search = [], [], [], []
    for a in c.itertuples():
        found_v, found_p, found_r, spans = [], [], [], []
        for name, rx in vendors:
            for m in rx.finditer(a.text):
                if name not in found_v:
                    found_v.append(name)
                    vm.append({"vendor": name, "answer_id": a.answer_id, "respid": a.respid, "item": a.item,
                               "frame": a.frame, "matched": m.group(0), "provenance": "INFERRED"})
                spans.append(m.span())
        for name, rx in people:
            for m in rx.finditer(a.text):
                if name not in found_p:
                    found_p.append(name)
                    pm.append({"person": name, "answer_id": a.answer_id, "respid": a.respid, "item": a.item,
                               "frame": a.frame, "matched": m.group(0), "provenance": "INFERRED"})
                spans.append(m.span())
        if a.item in ("Q24", "Q25"):
            for name, rx in roles:
                if rx.search(a.text):
                    found_r.append(name)
                    rm.append({"answer_id": a.answer_id, "respid": a.respid, "item": a.item, "frame": a.frame,
                               "role": name, "provenance": "INFERRED"})
        search.append({"answer_id": a.answer_id, "respid": a.respid, "item": a.item, "frame": a.frame,
                       "vendors": "; ".join(found_v), "people": "; ".join(found_p), "roles": "; ".join(found_r),
                       "non_answer": a.non_answer, "text": a.text})
    OUT.mkdir(parents=True, exist_ok=True)
    vmd = pd.DataFrame(vm)
    vmd.to_csv(OUT / "vendor_mentions.csv", index=False, lineterminator="\n")
    pd.DataFrame(pm).to_csv(OUT / "people_mentions.csv", index=False, lineterminator="\n")
    pd.DataFrame(rm).to_csv(OUT / "contact_roles.csv", index=False, lineterminator="\n")
    s = pd.DataFrame(search)
    s.to_csv(OUT / "answers_search.csv", index=False, lineterminator="\n")
    (OUT / "answers_search.json").write_text(json.dumps(search, ensure_ascii=False, indent=0), encoding="utf-8")
    idx = vmd.assign(best=vmd.frame.eq("best"), worst=vmd.frame.eq("worst")).groupby("vendor").agg(
        mentions=("answer_id", "size"), best=("best", "sum"), worst=("worst", "sum"), respondents=("respid", "nunique"),
        in_q22=("item", lambda x: int((x == "Q22").sum())), in_q23=("item", lambda x: int((x == "Q23").sum())),
        in_q24=("item", lambda x: int((x == "Q24").sum())), in_q25=("item", lambda x: int((x == "Q25").sum())))
    idx["other"] = idx.mentions - idx.best - idx.worst
    idx = idx.reset_index().sort_values(["mentions", "vendor"], ascending=[False, True], kind="stable")
    idx.to_csv(OUT / "vendor_index.csv", index=False, lineterminator="\n")
    # review aid: capitalised words in Q22–Q25 not inside a gazetteer match and not on the stop list
    un = Counter()
    for a in c.itertuples():
        txt = a.text
        for name, rx in vendors + people:
            txt = rx.sub(" ", txt)
        for w in re.findall(r"\b[A-Z][A-Za-z&\.\-']+", txt):
            if w.strip(".") not in STOP:
                un[w.strip(".")] += 1
    pd.DataFrame(sorted(un.items(), key=lambda kv: (-kv[1], kv[0])), columns=["word", "count"]).to_csv(
        OUT / "unmatched_capitals.csv", index=False, lineterminator="\n")
    print(f"vendor_mentions={len(vmd)} vendors={vmd.vendor.nunique()} people_mentions={len(pm)} role_rows={len(rm)} "
          f"q24q25_with_role={len({r['answer_id'] for r in rm})} unmatched_capitals={len(un)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
