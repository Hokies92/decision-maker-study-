#!/usr/bin/env python3
"""p5_agreement.py — inter-coder agreement between the main coding and the blind re-code (P5.S06, M17).

Inputs: 05_open_ended/codes.csv (main coder), 05_open_ended/coding/recode.csv (second coder, blind),
        05_open_ended/coding/recode_sample.csv (the answers re-coded)
Outputs: 05_open_ended/consistency_report.md, coding/agreement.csv, coding/disagreements.csv

Per layer, on the re-coded answers:
    codability   N- code or CODABLE (all sampled answers)
    primary      the primary code (behaviour: code with polarity), on answers both coders found codable
    presence     pooled yes/no decisions for every code either coder used in the layer (multi-code agreement)
Statistics: Krippendorff's alpha, nominal (Krippendorff 2004, ch. 11; coincidence-matrix form, two coders) and
Cohen's kappa (Cohen 1960). Thresholds (Scott, D5-2): alpha ≥ 0.80 reliable; 0.67–0.80 usable with caution;
< 0.67 revise the definitions and re-check.
Usage: python3 -I scripts/p5_agreement.py
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

D = Path("05_open_ended")
LAYERS = ["gate", "behaviour", "servqual", "meansend", "attribution", "valence", "lexicon"]


def alpha_nominal(pairs):
    """Krippendorff's alpha for two coders, nominal data, no missing values within a pair."""
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    if not pairs:
        return float("nan")
    o = Counter()
    for a, b in pairs:
        o[(a, b)] += 1
        o[(b, a)] += 1
    n_c = Counter()
    for (a, _), v in o.items():
        n_c[a] += v
    n = sum(n_c.values())
    d_o = sum(v for (a, b), v in o.items() if a != b) / n
    d_e = sum(n_c[a] * n_c[b] for a in n_c for b in n_c if a != b) / (n * (n - 1))
    return 1.0 if d_e == 0 else 1 - d_o / d_e


def kappa(pairs):
    from sklearn.metrics import cohen_kappa_score
    a, b = zip(*pairs)
    if len(set(a) | set(b)) < 2:
        return 1.0
    return cohen_kappa_score(a, b)


def verdict(a):
    return "reliable" if a >= 0.80 else ("usable with caution" if a >= 0.667 else "revise")


def main() -> int:
    main_c = pd.read_csv(D / "codes.csv", dtype=str, keep_default_na=False)
    re_c = pd.read_csv(D / "coding/recode.csv", dtype=str, keep_default_na=False)
    sample = pd.read_csv(D / "coding/recode_sample.csv", dtype=str, keep_default_na=False)
    ids = list(sample.answer_id)
    missing = [i for i in ids if i not in set(re_c.answer_id) or i not in set(main_c.answer_id)]
    if missing:
        print("ERROR: answers missing from a coder:", missing[:10], file=sys.stderr)
        return 2
    m, r = main_c[main_c.answer_id.isin(ids)], re_c[re_c.answer_id.isin(ids)]

    def lab(df, aid, layer, primary_only):
        x = df[(df.answer_id == aid) & (df.layer == layer)]
        if primary_only:
            x = x[x.primary == "True"]
        return {(c + (":" + p if p else "")) for c, p in zip(x.code, x.polarity)}

    rows, dis = [], []
    cod = []
    for aid in ids:
        a = next(iter(lab(m, aid, "notcodable", True)), "CODABLE")
        b = next(iter(lab(r, aid, "notcodable", True)), "CODABLE")
        cod.append((a, b))
        if a != b:
            dis.append({"answer_id": aid, "layer": "codability", "main": a, "recode": b})
    rows.append({"layer": "codability", "measure": "N- code or CODABLE", "units": len(cod),
                 "agreement": round(sum(a == b for a, b in cod) / len(cod), 4),
                 "alpha": round(alpha_nominal(cod), 4), "kappa": round(kappa(cod), 4)})
    both = [aid for aid, (a, b) in zip(ids, cod) if a == "CODABLE" and b == "CODABLE"]
    for layer in LAYERS:
        prim = []
        for aid in both:
            pa, pb = lab(m, aid, layer, True), lab(r, aid, layer, True)
            pa, pb = (next(iter(pa)) if pa else "NONE"), (next(iter(pb)) if pb else "NONE")
            prim.append((pa, pb))
            if pa != pb:
                dis.append({"answer_id": aid, "layer": layer + " (primary)", "main": pa, "recode": pb})
        codes = set()
        for aid in both:
            codes |= lab(m, aid, layer, False) | lab(r, aid, layer, False)
        pres = []
        for aid in both:
            sa, sb = lab(m, aid, layer, False), lab(r, aid, layer, False)
            for c in sorted(codes):
                pres.append((c in sa, c in sb))
        for name, pairs in (("primary code", prim), ("presence of each code", pres)):
            if not pairs:
                continue
            al = alpha_nominal(pairs)
            rows.append({"layer": layer, "measure": name, "units": len(pairs),
                         "agreement": round(sum(a == b for a, b in pairs) / len(pairs), 4),
                         "alpha": round(al, 4), "kappa": round(kappa(pairs), 4)})
    # Sensitivity: the second coder applied L26 (judging sales teams) to every codable Q22/Q23 answer, reading the
    # question itself as the concept; the frame states no rule for L26. Shown separately, never replacing the measure.
    pres = []
    for aid in both:
        sa, sb = lab(m, aid, "lexicon", False) - {"L26"}, lab(r, aid, "lexicon", False) - {"L26"}
        for c in sorted({c for x in both for c in lab(m, x, "lexicon", False) | lab(r, x, "lexicon", False)} - {"L26"}):
            pres.append((c in sa, c in sb))
    rows.append({"layer": "lexicon", "measure": "presence, excluding L26 (sensitivity)", "units": len(pres),
                 "agreement": round(sum(a == b for a, b in pres) / len(pres), 4),
                 "alpha": round(alpha_nominal(pres), 4), "kappa": round(kappa(pres), 4)})
    ag = pd.DataFrame(rows)
    ag["verdict"] = ag.alpha.map(verdict)
    ag.to_csv(D / "coding/agreement.csv", index=False, lineterminator="\n")
    pd.DataFrame(dis).to_csv(D / "coding/disagreements.csv", index=False, lineterminator="\n")
    L = ["# Consistency check (M17)", "", "Generated by `scripts/p5_agreement.py`.", "",
         f"**Design.** {len(ids)} answers drawn at random from all 1,697, stratified by question (36 each from Q21–Q25, "
         "20 'please specify'; `scripts/p5_draw_recode_sample.py`, seed 1954). A second coder — a separate agent that had "
         "not seen the main codes — coded them blind from the coding frame v1.1 alone. Agreement is measured on whether "
         f"an answer is codable (all {len(ids)}), then on each layer for the {len(both)} answers both coders found codable: "
         "the primary code, and the presence of each code (multi-code agreement).", "",
         "**Thresholds** (Scott, D5-2; Krippendorff 2004): alpha ≥ 0.80 reliable; 0.67–0.80 usable with caution; "
         "below 0.67 revise the definitions and re-check.", "",
         "| Layer | Measure | Units | % agreement | Krippendorff's alpha | Cohen's kappa | Verdict |", "|---|---|---|---|---|---|---|"]
    for x in ag.itertuples():
        L.append(f"| {x.layer} | {x.measure} | {x.units} | {x.agreement:.0%} | {x.alpha:.2f} | {x.kappa:.2f} | {x.verdict} |")
    L += ["", f"Disagreements: {len(dis)} (`coding/disagreements.csv`). The sensitivity row is not a verdict: it shows how much "
          "of the lexicon disagreement comes from one missing rule (when L26 applies). The second coder's notes on where the frame "
          "was unclear are in `coding/recode_notes.md`.", ""]
    (D / "consistency_report.md").write_text("\n".join(L), encoding="utf-8")
    print(ag.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
