#!/usr/bin/env python3
"""p4_crosscheck.py — Phase 4 cross-check: the analytics library is complete, honest about n, and reproducible.

Checks:
    C01 Every technique file is complete and every XPath it names exists in the XSD (p4_check_xpaths.py)
    C02 The catalog lists every technique and is current
    C03 Every technique's script and every declared output exist; nothing undeclared in outputs/
    C04 n = 25 is never breached in a comparison (every cohort and base entering T04's spreads, T05's ranks,
        and T07–T09 is ≥ 25; All respondents never enters a cross-cohort comparison)
    C05 Ecological caveat: every technique that compares across cohorts (T04, T07, T08, T09) says so in its
        file, and T07's output carries it on every row
    C06 Measures reproduce the schema: T02 values recomputed directly from full_study.xml Result shares
    C07 Every technique script re-runs byte-identical (all outputs)
    C08 Every third-party package imported by a Phase 4 script is listed in requirements.txt
    C09 Source files match the integrity manifest
Output: 04_analytics_library/crosscheck_report.md. Exit 1 if any check fails.

Usage: python3 -I scripts/p4_crosscheck.py
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402

import p4_lib as L  # noqa: E402
from p4_check_xpaths import front_matter  # noqa: E402

LIB = Path("04_analytics_library")
results = []


def check(cid, name, ok, detail):
    results.append((cid, name, "PASS" if ok else "FAIL", detail))
    print(f"{cid} {'PASS' if ok else 'FAIL'} — {name} | {detail}")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main() -> int:
    tech = sorted(LIB.glob("T[0-9][0-9]-*.md"))
    fms = {f.name: front_matter(f.read_text(encoding="utf-8")) for f in tech}

    # C01
    p = subprocess.run([sys.executable, "-I", "scripts/p4_check_xpaths.py"], capture_output=True, text=True)
    last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr.strip()
    check("C01", "Technique files complete; every XPath exists in the XSD (with self-test)", p.returncode == 0,
          f"{last}; self-test: {'PASS' if 'selftest PASS' in p.stdout else 'FAIL'}")

    # C02
    before = sha(LIB / "catalog.md")
    subprocess.run([sys.executable, "-I", "scripts/p4_build_catalog.py"], capture_output=True)
    cat = (LIB / "catalog.md").read_text(encoding="utf-8")
    listed = [fm["id"] for fm in fms.values() if f"[{fm['id']}]" in cat]
    check("C02", "Catalog lists every technique and is current", len(listed) == len(tech) == 9 and sha(LIB / "catalog.md") == before,
          f"{len(tech)} technique files; {len(listed)} listed; catalog unchanged by regeneration: {sha(LIB / 'catalog.md') == before}")

    # C03
    missing, declared = [], set()
    for name, fm in fms.items():
        if not Path(fm["script"]).exists():
            missing.append(fm["script"])
        for o in fm["outputs"]:
            declared.add(o)
            if not Path(o).exists():
                missing.append(o)
    actual = {str(x) for x in (LIB / "outputs").rglob("*") if x.is_file()}
    undeclared = sorted(actual - declared)
    check("C03", "Scripts and declared outputs exist; no undeclared outputs", not missing and not undeclared,
          f"{len(declared)} declared outputs; missing {missing or 'none'}; undeclared {undeclared or 'none'}")

    # C04 — n = 25 in comparisons
    co = L.cohorts(L.load()).set_index("cohort")
    breaches = []
    t4 = pd.read_csv(LIB / "outputs/T04/value_vs_experience.csv")
    u4 = t4[t4.usable]
    if ((u4.a_base < 25) | (u4.b_base < 25) | (u4.cohort.map(co.n) < 25)).any():
        breaches.append("T04 usable rows below 25")
    t5 = pd.read_csv(LIB / "outputs/T05/reasons_by_cohort.csv")
    if (t5[t5.usable].base < 25).any() or (t5[t5.usable].n < 25).any():
        breaches.append("T05 usable rows below 25")
    wide, h = L.cohort_matrix()
    hu = h[h.usable]
    if (hu.base < 25).any() or (hu.n < 25).any():
        breaches.append("headline matrix below 25")
    for t, f, col in (("T08", "outputs/T08/cohort_clusters.csv", "cohort"), ("T09", "outputs/T09/cohort_coordinates.csv", "cohort")):
        cs = pd.read_csv(LIB / f)[col]
        if (cs.map(co.n) < 25).any() or (cs == "C-L-ALL-RESPONDENTS").any():
            breaches.append(f"{t}: cohort below 25 or All respondents")
        if set(cs) != set(wide.index):
            breaches.append(f"{t}: cohorts differ from the usable matrix")
    t7 = pd.read_csv(LIB / "outputs/T07/measure_correlations.csv")
    if (t7.cohorts < 20).any():
        breaches.append("T07 pair with < 20 cohorts")
    excluded = int((~h.usable).sum())
    check("C04", "n = 25 never breached in a comparison", not breaches,
          f"breaches {breaches or 'none'}; T04 usable rows {len(u4)} of {len(t4)}; T05 usable rows {int(t5.usable.sum())} of {len(t5)}; "
          f"T07–T09 matrix {wide.shape[0]} cohorts × {wide.shape[1]} measures; headline values excluded as below 25: {excluded}")

    # C05 — ecological caveat
    cross = [n for n, fm in fms.items() if fm["id"] in ("T04", "T07", "T08", "T09")]
    no_cav = [n for n in cross if fms[n]["ecological_caveat"] != "yes" or
              "## Ecological caveat" not in (LIB / n).read_text(encoding="utf-8")]
    t7_ok = (t7.caveat.str.startswith("ecological")).all()
    check("C05", "Ecological caveat stated wherever cohorts are compared statistically", not no_cav and t7_ok,
          f"techniques with caveat: {', '.join(fms[n]['id'] for n in cross)}; missing: {no_cav or 'none'}; T07 rows carrying it: {bool(t7_ok)}")

    # C06 — T02 recomputed straight from the instance
    from lxml import etree
    ns = {"d": L.NS["d"]}
    doc = etree.parse(str(L.FULL))
    opts = {s.get("id"): [o.text for o in s.findall(f"{{{ns['d']}}}Option")] for s in doc.xpath("//d:Scale", namespaces=ns)}
    share = {(r.getparent().get("item"), r.get("cohort"), r.get("option")): float(r.get("share"))
             for r in doc.xpath("//d:Result[@share]", namespaces=ns)}
    t2 = pd.read_csv(LIB / "outputs/T02/summary_measures.csv")
    bad = 0
    for x in t2.itertuples():
        item, suffix = x.measure.split("__")
        scale = doc.xpath(f"//d:Variable[@id='{x.measure}']/@scale", namespaces=ns)[0]
        spec = L.SUMMARY_OPTIONS[(scale, suffix)]
        seqs = [o if isinstance(o, int) else opts[scale].index(o) + 1 for o in spec]
        v = sum(share[(item, x.cohort, str(s))] for s in seqs)
        if abs(v - x.value) > 1e-4:
            bad += 1
    check("C06", "T02 summary measures equal a direct recomputation from the instance", bad == 0,
          f"{len(t2)} values recomputed from Result shares; mismatches {bad}")

    # C07 — reproducibility
    outs = sorted({o for fm in fms.values() for o in fm["outputs"]})
    before = {o: sha(o) for o in outs}
    codes = [subprocess.run([sys.executable, "-I", fm["script"]], capture_output=True).returncode for fm in fms.values()]
    changed = [o for o in outs if sha(o) != before[o]]
    check("C07", "Every technique script re-runs byte-identical", all(c == 0 for c in codes) and not changed,
          f"{len(codes)} scripts, {len(outs)} outputs; exit codes {sorted(set(codes))}; changed {changed or 'none'}")

    # C08 — dependencies listed
    req = {re.split(r"[<>=]", l.strip())[0].lower() for l in Path("requirements.txt").read_text().splitlines() if l.strip()}
    stdlib = set(sys.stdlib_module_names) | {"p4_lib", "p4_check_xpaths"}
    used = set()
    for s in sorted(Path("scripts").glob("p4_*.py")):
        for m in re.findall(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", s.read_text(encoding="utf-8"), re.M):
            if m not in stdlib and m != "__future__":
                used.add(m.lower())
    unlisted = sorted(used - req)
    check("C08", "Every third-party package used by Phase 4 is in requirements.txt", not unlisted,
          f"used {sorted(used)}; unlisted {unlisted or 'none'}")

    # C09
    p = subprocess.run(["sha256sum", "-c", "00_source/MANIFEST.sha256"], capture_output=True, text=True)
    check("C09", "Source files match the integrity manifest", p.returncode == 0, p.stdout.strip().replace("\n", "; "))

    fails = [r for r in results if r[2] == "FAIL"]
    Lr = ["# Phase 4 Cross-check", "", "Generated by `scripts/p4_crosscheck.py`. Do not edit by hand.", "",
          f"**Result: {'ALL PASS' if not fails else 'FAILURES'}** — {len(results) - len(fails)} of {len(results)} checks.", "",
          "| # | Check | Result | Evidence |", "|---|---|---|---|"]
    for cid, name, res_, det in results:
        Lr.append(f"| {cid} | {name} | {res_} | {det.replace('|', '/')} |")
    Lr.append("")
    (LIB / "crosscheck_report.md").write_text("\n".join(Lr), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
