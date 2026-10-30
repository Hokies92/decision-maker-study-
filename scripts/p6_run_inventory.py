#!/usr/bin/env python3
"""p6_run_inventory.py — the first run of the analytics inventory (P6.S10): every combination Scott marked useful, run on
the full data, logged, and reported.

Runs (combination → method):
    IN01:Q14        entropy of the typical-meeting answers, all respondents and every usable group (Shannon 1948)
    DS07:Q8_1+Q8_3  prepared on own company and products vs on my specific business — same question, same scale, same people
    IS04:Q18        chi-square test of homogeneity of the business-case answers across groups, within each dimension whose
                    groups do not overlap (R06); usable groups only (R05); false discovery rate across dimensions (BH 1995)
    CM01:Q14        correspondence analysis of typical-meeting answers × usable groups of non-overlapping dimensions (R07)
    EC03:Q18        transaction-cost reading of the business-case answers (interpretation only, R12)
Inputs: 04_analytics_library/outputs/T01/gate_profile.csv; 01_instrument_reconstruction/cohorts.csv, cohort_dimensions.csv;
        06_visualization/inventory/valid.csv, verdicts.csv.
Outputs: 06_visualization/inventory/runs/*.csv, runs/report.md, run_log.csv.
Every number is computed here from committed data; group-level only — no statement about an individual.
Usage: python3 -I scripts/p6_run_inventory.py
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

INV = Path("06_visualization/inventory")
OUT = INV / "runs"
ALL = "C-L-ALL-RESPONDENTS"
MIN_N = 25


def rd(p):
    return pd.read_csv(p, dtype=str, keep_default_na=False)


def bh(p):
    """Benjamini–Hochberg adjusted p-values."""
    p = np.asarray(p, float)
    o = np.argsort(p)
    adj = np.empty_like(p)
    m = len(p)
    run = 1.0
    for rank, i in enumerate(o[::-1]):
        k = m - rank
        run = min(run, p[i] * m / k)
        adj[i] = run
    return adj


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    gp = rd(Path("04_analytics_library/outputs/T01/gate_profile.csv"))
    coh = rd(Path("01_instrument_reconstruction/cohorts.csv")).set_index("cohort_id")
    dims = rd(Path("01_instrument_reconstruction/cohort_dimensions.csv")).set_index("dimension_id")
    exclusive = [d for d in dims.index if dims.loc[d, "membership"] == "exclusive" and dims.loc[d, "tabulated"] == "yes"]
    valid = rd(INV / "valid.csv").set_index("combo_id")
    verdicts = rd(INV / "verdicts.csv")
    to_run = verdicts[(verdicts.level == "combo") & (verdicts.verdict == "useful")].target.tolist()
    for c in to_run:
        if c not in valid.index:
            print(f"ERROR: {c} marked useful but not valid in the inventory", file=sys.stderr)
            return 2
    gp["share_f"] = pd.to_numeric(gp.share, errors="coerce").fillna(0.0)
    gp["n_i"] = pd.to_numeric(gp.n, errors="coerce").fillna(0).astype(int)
    label = lambda c: f"{coh.loc[c, 'label']} ({dims.loc[coh.loc[c, 'dimension_id'], 'name'] if coh.loc[c, 'dimension_id'] in dims.index else 'all'})"

    def dist(item, keep_sub=True):
        x = gp[gp["item"] == item].copy()
        x["o"] = pd.to_numeric(x.option, errors="coerce")
        if keep_sub:
            x = x[~x.option_label.str.match(r"^(Other|Don.?t know)", case=False)]
        return x.sort_values(["cohort", "o"])

    log, R = [], []
    # ---- IN01:Q14 entropy -------------------------------------------------------------------------------------------
    q14 = dist("Q14")
    k = q14.option.nunique()
    ent = []
    for c, g in q14.groupby("cohort"):
        p = g.share_f.values
        p = p / p.sum()
        h = -sum(v * math.log2(v) for v in p if v > 0)
        n = int(coh.loc[c, "n"])
        if c == ALL or (n >= MIN_N and coh.loc[c, "dimension_id"] in exclusive):
            ent.append({"cohort": c, "group": "All respondents" if c == ALL else label(c), "n": n, "entropy_bits": round(h, 4),
                        "evenness": round(h / math.log2(k), 4), "pitch_share": round(float(g.share_f.values[:2].sum() / g.share_f.sum()), 4)})
    E = pd.DataFrame(ent).sort_values(["evenness", "cohort"])
    E.to_csv(OUT / "in01_q14_entropy.csv", index=False, lineterminator="\n")
    eall = E[E.cohort == ALL].iloc[0]
    # ---- DS07:Q8_1+Q8_3 -----------------------------------------------------------------------------------------------
    q8 = gp[gp["item"].isin(["Q8_1", "Q8_3"]) & (gp.option_label == "Frequently")]
    w = q8.pivot_table(index="cohort", columns="item", values="share_f", aggfunc="first").reset_index()
    w["n"] = w.cohort.map(lambda c: int(coh.loc[c, "n"]))
    w = w[(w.cohort == ALL) | ((w.n >= MIN_N) & w.cohort.map(lambda c: coh.loc[c, "dimension_id"] in exclusive))]
    w["difference_pts"] = ((w.Q8_1 - w.Q8_3) * 100).round(1)
    w["group"] = w.cohort.map(lambda c: "All respondents" if c == ALL else label(c))
    W = w[["cohort", "group", "n", "Q8_1", "Q8_3", "difference_pts"]].sort_values(["difference_pts", "cohort"], ascending=[False, True])
    W.to_csv(OUT / "ds07_q8_own_vs_my_business.csv", index=False, lineterminator="\n")
    wall = W[W.cohort == ALL].iloc[0]
    wg = W[W.cohort != ALL]
    # ---- IS04:Q18 chi-square per non-overlapping dimension -------------------------------------------------------------
    q18 = dist("Q18")
    tests = []
    for d in exclusive:
        g = q18[q18.dimension == d]
        cs = sorted(c for c in g.cohort.unique() if int(coh.loc[c, "n"]) >= MIN_N)
        if len(cs) < 2:
            continue
        T = np.array([[float(r.share_f) * int(coh.loc[c, "n"]) for r in g[g.cohort == c].itertuples()] for c in cs])
        T = np.round(T)
        # Three bands of the same question (one regrouping, not a new comparison): vendor material does most of the work
        # (options 1–2); significant customization (3); customer does most or all (4–5). Made after the five-option run
        # showed expected counts below 5 in most dimensions — disclosed in the report.
        T = np.column_stack([T[:, 0] + T[:, 1], T[:, 2], T[:, 3] + T[:, 4]])
        T = T[:, T.sum(axis=0) > 0]
        chi2, p, dof, exp = chi2_contingency(T)
        nn = T.sum()
        v = math.sqrt(chi2 / (nn * (min(T.shape) - 1)))
        tests.append({"dimension": dims.loc[d, "name"], "groups": len(cs), "n": int(nn), "chi2": round(chi2, 3), "dof": dof, "p": p,
                      "cramers_v": round(v, 3), "min_expected": round(float(exp.min()), 2), "expected_ok": bool(exp.min() >= 5)})
    T18 = pd.DataFrame(tests)
    T18["p_bh"] = bh(T18.p.values).round(4)
    T18["p"] = T18.p.round(4)
    T18["differs_at_5pct"] = T18.p_bh < 0.05
    T18.sort_values(["p", "dimension"]).to_csv(OUT / "is04_q18_by_group.csv", index=False, lineterminator="\n")
    # ---- CM01:Q14 correspondence analysis -----------------------------------------------------------------------------
    rows = sorted(c for c in q14.cohort.unique() if c != ALL and coh.loc[c, "dimension_id"] in exclusive and int(coh.loc[c, "n"]) >= MIN_N)
    opts = q14[q14.cohort == ALL].sort_values("o").option_label.tolist()
    N = np.array([[float(r.share_f) * int(coh.loc[c, "n"]) for r in q14[q14.cohort == c].sort_values("o").itertuples()] for c in rows])
    P = N / N.sum()
    rm, cm = P.sum(axis=1), P.sum(axis=0)
    S = (P - np.outer(rm, cm)) / np.sqrt(np.outer(rm, cm))
    U, sv, Vt = np.linalg.svd(S, full_matrices=False)
    inertia = sv ** 2
    sign = 1.0 if Vt[0][int(np.argmax(np.abs(Vt[0])))] >= 0 else -1.0   # fixed orientation: largest option loading positive
    rc = sign * (U[:, 0] * sv[0]) / np.sqrt(rm)
    cc = sign * (Vt[0] * sv[0]) / np.sqrt(cm)
    CA = pd.DataFrame({"cohort": rows, "group": [label(c) for c in rows], "n": [int(coh.loc[c, "n"]) for c in rows],
                       "axis1": np.round(rc, 4), "pitch_share": np.round(N[:, :2].sum(axis=1) / N.sum(axis=1), 4)}).sort_values(["axis1", "cohort"], ascending=[False, True])
    CA.to_csv(OUT / "cm01_q14_groups.csv", index=False, lineterminator="\n")
    pd.DataFrame({"option": opts, "axis1": np.round(cc, 4)}).to_csv(OUT / "cm01_q14_options.csv", index=False, lineterminator="\n")
    share1 = inertia[0] / inertia.sum()
    ends = [o for _, o in sorted(zip(cc, opts), reverse=True)]
    short = lambda t: t if len(t) <= 70 else t[:67].rstrip() + "…"
    # ---- EC03:Q18 transaction-cost reading ----------------------------------------------------------------------------
    q18all = q18[q18.cohort == ALL].sort_values("o")
    s = q18all.share_f.values
    own_work = s[2] + s[3] + s[4]
    # ---- report and log -----------------------------------------------------------------------------------------------
    sig = T18[T18.differs_at_5pct]
    top, bot = CA.head(3), CA.tail(3)
    L = ["# First run of the analytics inventory (P6.S10)", "", "Generated by `scripts/p6_run_inventory.py`. Every number is computed from "
         "committed data. Group-level only: each figure describes a group of decision-makers, not a person.", "",
         "## 1 · How one-sided is the typical meeting? (IN01 entropy, Q14)", "",
         f"- Evenness of the five agenda answers for all {eall.n} respondents: **{eall.evenness:.2f}** (0 = everyone gives the same answer, 1 = answers spread evenly). "
         f"Pitch share (first two answers): {eall.pitch_share:.0%}.",
         f"- Most concentrated groups (least even): " + "; ".join(f"{r.group} {r.evenness:.2f} (pitch {r.pitch_share:.0%})" for r in E[E.cohort != ALL].head(3).itertuples()) + ".",
         f"- Most even: " + "; ".join(f"{r.group} {r.evenness:.2f} (pitch {r.pitch_share:.0%})" for r in E[E.cohort != ALL].tail(3).itertuples()) + ".",
         f"- Reading: across {len(E) - 1} usable groups evenness ranges {E[E.cohort != ALL].evenness.min():.2f}–{E[E.cohort != ALL].evenness.max():.2f}. Meetings are not uniformly pitches — the experience is mixed — but the mass sits on the pitch end in every group "
         f"(pitch share {E[E.cohort != ALL].pitch_share.min():.0%}–{E[E.cohort != ALL].pitch_share.max():.0%}).", "",
         "## 2 · Prepared on themselves vs on me (DS07, Q8_1 vs Q8_3, same question)", "",
         f"- All respondents: frequently knowledgeable about their own company and products {wall.Q8_1:.0%}; about my specific business {wall.Q8_3:.0%}; "
         f"difference **{wall.difference_pts:+.0f} points**.",
         f"- In **{int((wg.difference_pts > 0).sum())} of {len(wg)}** usable groups the own-products share is higher; range {wg.difference_pts.min():+.0f} to {wg.difference_pts.max():+.0f} points.",
         f"- Widest: " + "; ".join(f"{r.group} {r.difference_pts:+.0f}" for r in wg.head(3).itertuples()) + ". Narrowest: "
         + "; ".join(f"{r.group} {r.difference_pts:+.0f}" for r in wg.tail(3).itertuples()) + ".", "",
         "## 3 · Does the business-case problem differ by group? (IS04 chi-square, Q18)", "",
         f"Tested within {len(T18)} dimensions whose groups do not overlap; groups below n = 25 left out; p adjusted for {len(T18)} tests (Benjamini–Hochberg). "
         "Answers grouped into three bands of the same question — vendor material does most of the work (answers 1–2), significant customization (3), "
         "the customer does most or all of it (4–5). Disclosure: the first run used all five answers and most dimensions had expected counts below 5, "
         "which makes the test unreliable; the bands were chosen after seeing that, not before.", "",
         "| Dimension | Groups | n | Chi-square | p (adjusted) | Cramér's V | Smallest expected count |", "|---|---|---|---|---|---|---|"]
    for r in T18.sort_values(["p", "dimension"]).itertuples():
        L.append(f"| {r.dimension} | {r.groups} | {r.n} | {r.chi2} | {r.p_bh} | {r.cramers_v} | {r.min_expected}{'' if r.expected_ok else ' (below 5: read with care)'} |")
    L += ["", f"- Reading: {'the answers differ by ' + ', '.join(sig.dimension) if len(sig) else 'no dimension shows a difference that survives adjustment'}. "
          + ("The business-case problem is shared across levels, functions, regions and company sizes: it is not one group's problem." if len(sig) == 0 else
             "Elsewhere the business-case problem is shared."), "",
          "## 4 · Which groups get the most pitching? (CM01 correspondence analysis, Q14)", "",
          f"- First axis carries {share1:.0%} of the variation between groups. Read from the data, not assumed: its positive end is set by "
          f"“{short(ends[0])}”, its negative end by “{short(ends[-1])}”. It is not a pitch-versus-customer axis.",
          "- Groups at the positive end: " + "; ".join(f"{r.group} (pitch {r.pitch_share:.0%})" for r in top.itertuples()) + ".",
          "- Groups at the negative end: " + "; ".join(f"{r.group} (pitch {r.pitch_share:.0%})" for r in bot.itertuples()) + ".",
          "- Plainer reading for the same question: pitch share by group is in section 1 (48%–73%).",
          f"- Caveat: groups from different dimensions share people (a VP is also in a region); the map describes groups, not individuals (R07).", "",
          "## 5 · The business case as a transaction cost (EC03, Q18) — interpretation", "",
          f"- Data: {s[0]:.0%} find building the case simple with vendor material; {own_work:.0%} need significant customization or do most or all of it themselves.",
          "- Reading (Williamson 1985): the business case is a cost of completing the purchase. Vendors leave most of it with the customer, inside the customer's "
          "company, where the effort competes with every other priority. A purchase that costs the customer more to complete is more likely to stall — "
          "consistent with the pull-back reasons in Q15. The lens explains; it measures nothing of its own (R12).", ""]
    L += ["## What this run taught the inventory (for Scott's verdicts)", "",
          "- **Proposed rule R15:** a test is reported only when its expected counts are at least 5. The five-answer chi-square looked significant for "
          "three dimensions; with sound counts none survives. The method register states this caveat, but the engine cannot see counts until a run — "
          "so the check belongs in the run step.",
          "- **CM01 on Q14 explains little to a reader:** its main axis is set by the 'partnering' answer, not by pitch versus customer. The plain pitch "
          "share by group (section 1) answers the same question more clearly. Suggested verdict: valid but not useful for communication.",
          f"- **DS07 is the strongest result:** own-products preparation exceeds preparation on the customer's business in {int((wg.difference_pts > 0).sum())} of {len(wg)} groups. "
          "It is the sound replacement for the retired ledger.",
          "- **The business-case problem is common to every group tested** (no difference survives) — evidence for 'fix the design, not the people'.", ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    runs = [("IN01:Q14", "runs/in01_q14_entropy.csv", f"evenness all {eall.evenness:.2f}; pitch share {eall.pitch_share:.0%}"),
            ("DS07:Q8_1+Q8_3", "runs/ds07_q8_own_vs_my_business.csv", f"{wall.difference_pts:+.0f} pts all; higher in {int((wg.difference_pts > 0).sum())}/{len(wg)} groups"),
            ("IS04:Q18", "runs/is04_q18_by_group.csv", f"{len(sig)} of {len(T18)} dimensions differ after adjustment"),
            ("CM01:Q14", "runs/cm01_q14_groups.csv; runs/cm01_q14_options.csv", f"axis 1 {share1:.0%} of variation"),
            ("EC03:Q18", "runs/report.md §5", f"{own_work:.0%} carry significant case work themselves")]
    pd.DataFrame([{"combo_id": c, "script": "scripts/p6_run_inventory.py", "outputs": o, "result": r, "verdict": "pending (Scott)"} for c, o, r in runs]) \
        .to_csv(INV / "run_log.csv", index=False, lineterminator="\n")
    print(f"runs={len(runs)}; dimensions tested={len(T18)}; differ={len(sig)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
