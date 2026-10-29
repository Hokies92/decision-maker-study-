#!/usr/bin/env python3
"""p3_crosscheck.py — Phase 3 cross-check: the schema, its instances, and their agreement with Phases 1–2.

Checks:
    C01 Every example and the test file validate against the XSD (xmllint)
    C02 The gate module stands alone: a GateModel document validates against gates.xsd by itself
    C03 Namespaces carry the major version; schema and instance versions agree
    C04 full_study.xml reconciles to Phase 1–2 outputs (every cell, flag, cohort, item, link, variable)
    C05 Rules XSD 1.0 cannot express (one endpoint per side, scale consistency, one current set, …)
    C06 Every person-cohort result reaches stakeholder type; every level-cohort result reaches role level
    C07 Every result reaches a gate group through the current assignment set
    C08 Respondent layer optional and faithful (full_study has none; text answers equal source cells)
    C09 SYNTHETIC only in tests/; recordKind correct; provenance counted
    C10 Negative tests: broken copies fail validation
    C11 Generators re-run byte-identical
    C12 Source files match the integrity manifest
    C13 No study date in any instance
Output: 03_schema/crosscheck_report.md. Exit 1 if any check fails.

Usage: python3 -I scripts/p3_crosscheck.py
"""

from __future__ import annotations

import copy
import hashlib
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pandas as pd
from lxml import etree
from openpyxl.utils import column_index_from_string

S = Path("03_schema")
XSD, GXSD = S / "decision-maker-study.xsd", S / "gates.xsd"
EXAMPLES = sorted((S / "examples").glob("*.xml"))
TESTS = sorted((S / "tests").glob("*.xml"))
NS_D, NS_G = "https://growthenablement.com/ns/dms/v1", "https://growthenablement.com/ns/gates/v1"
NS = {"d": NS_D, "g": NS_G, "xs": "http://www.w3.org/2001/XMLSchema"}
GENERATED = [S / "examples/full_study.xml", S / "examples/thread_q15.xml", S / "examples/respondents_open_ended.xml",
             S / "tests/synthetic_decision_path.xml", S / "schema_mapping.csv"]
GENERATORS = ["scripts/p3_build_instances.py", "scripts/p3_build_schema_mapping.py"]
results = []


def check(cid, name, ok, detail):
    results.append((cid, name, "PASS" if ok else "FAIL", detail))
    print(f"{cid} {'PASS' if ok else 'FAIL'} — {name} | {detail}")


def xmllint(path, schema=XSD):
    p = subprocess.run(["xmllint", "--noout", "--schema", str(schema), str(path)], capture_output=True, text=True)
    return p.returncode == 0, (p.stderr.strip().splitlines() or [""])[0]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def x(doc, xp):
    return doc.xpath(xp, namespaces=NS)


def main() -> int:
    docs = {p.name: etree.parse(str(p)) for p in EXAMPLES + TESTS}
    full = docs["full_study.xml"]

    # C01
    fails = [f"{p.name}: {xmllint(p)[1]}" for p in EXAMPLES + TESTS if not xmllint(p)[0]]
    check("C01", "Every example and test file validates against the XSD", not fails and len(EXAMPLES) >= 3,
          f"{len(EXAMPLES)} examples + {len(TESTS)} test file; failures: {fails or 'none'}")

    # C02
    gm = copy.deepcopy(x(full, "/d:Study/g:GateModel")[0])
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "gates_only.xml"
        p.write_bytes(etree.tostring(gm, xml_declaration=True, encoding="UTF-8"))
        ok, msg = xmllint(p, GXSD)
    gates = [g.get("id") for g in gm.findall(f"{{{NS_G}}}Gate")]
    check("C02", "Gate module validates on its own (gates.xsd only)", ok and gates == ["TARGET", "ACCESS", "AGREE", "VISION", "CASE"],
          f"gates {gates}; standalone GateModel document {'validates' if ok else 'fails: ' + msg}")

    # C03
    d_ns = etree.parse(str(XSD)).getroot().get("targetNamespace")
    g_ns = etree.parse(str(GXSD)).getroot().get("targetNamespace")
    vers = {etree.parse(str(XSD)).getroot().get("version"), etree.parse(str(GXSD)).getroot().get("version")}
    inst_v = {d.getroot().get("schemaVersion") for d in docs.values()}
    check("C03", "Namespaces end /dms/v1 and /gates/v1; versions agree",
          d_ns.endswith("/dms/v1") and g_ns.endswith("/gates/v1") and vers == {"1.0.0"} and inst_v == {"1.0.0"},
          f"{d_ns}; {g_ns}; schema {sorted(vers)}; instances {sorted(inst_v)}")

    # C04 — reconcile full_study to Phase 1–2
    R1, R2 = Path("01_instrument_reconstruction"), Path("02_data_inventory")
    rd = lambda p: pd.read_csv(p, dtype=str, keep_default_na=False)
    res, sig, qm, coh = rd(R2 / "results.csv"), rd(R2 / "significance.csv"), rd(R1 / "question_map.csv"), rd(R1 / "cohorts.csv")
    lk, var, sc, ro = rd(R1 / "linkages.csv"), rd(R2 / "variable_dictionary.csv"), rd(R1 / "response_scales.csv"), rd(R1 / "routing.csv")
    src_cells = {f"{r.sheet}!{r.cell}": r for r in res.itertuples()}
    cell_errs, seen = [], set()
    for r in x(full, "//d:Result"):
        item = r.getparent().get("item")
        for cite in [r.get("cite")] + [a.get("cite") for a in r.findall(f"{{{NS_D}}}AlsoAt")]:
            seen.add(cite)
            s = src_cells.get(cite)
            if s is None:
                cell_errs.append(f"{cite} not in results.csv"); continue
            want = ("value" if s.value_status == "value" else "notAsked", s.value if s.value_status == "value" else None, s.base_n or None)
            got = (r.get("status"), r.get("share"), r.get("base"))
            if (s.item_id, s.cohort_id) != (item, r.get("cohort")) or want != got:
                cell_errs.append(f"{cite}: {got} vs {want}")
    missing_cells = set(src_cells) - seen
    fl = {(f.get("cite")): (f.get("state"), f.get("dimension")) for f in x(full, "//d:Flag")}
    smap = {"significant": "significant", "not_significant": "notSignificant", "not_tested": "notTested"}
    flag_errs = [r.cell for r in sig.itertuples() if fl.get(f"{r.sheet}!{r.cell}") != (smap[r.state], r.dimension_id)]
    gl = x(full, "//d:Link")
    link_errs = []
    for i, r in enumerate(lk.itertuples()):
        e = gl[i] if i < len(gl) else None
        if e is None or e.get("type") != r.link_type or e.get("weight") != r.weight or e.get("provenance") != r.provenance:
            link_errs.append(i + 1)
    counts = {"cells": len(seen), "flags": len(fl), "cohorts": len(x(full, "//d:Cohort")), "items": len(x(full, "//d:Item")),
              "threads": len(x(full, "//d:Thread")), "links": len(gl), "variables": len(x(full, "//d:Variable")),
              "scales": len(x(full, "//d:Scale")), "rules": len(x(full, "//d:RoutingRules/d:Rule"))}
    want = {"cells": len(res), "flags": len(sig), "cohorts": len(coh), "items": len(qm), "threads": qm.thread_id.nunique(),
            "links": len(lk), "variables": len(var), "scales": len(sc), "rules": len(ro)}
    check("C04", "full_study.xml reconciles to Phases 1–2",
          counts == want and not cell_errs and not missing_cells and not flag_errs and not link_errs,
          f"{counts}; cell mismatches {len(cell_errs)}; cells missing {len(missing_cells)}; flag mismatches {len(flag_errs)}; "
          f"link mismatches {len(link_errs)}; distinct results {len(x(full, '//d:Result'))} + repeat citations {len(x(full, '//d:AlsoAt'))}")

    # C05 — rules XSD 1.0 cannot express (all instances)
    errs = []
    for name, d in docs.items():
        item_scale = {i.get("id"): i.get("scale") for i in x(d, "//d:Item")}
        item_type = {i.get("id"): i.get("type") for i in x(d, "//d:Item")}
        for l in x(d, "//d:Link"):
            if sum(l.get(a) is not None for a in ("fromThread", "fromItem")) != 1 or \
               sum(l.get(a) is not None for a in ("toThread", "toItem", "toGroup", "toVariable")) != 1:
                errs.append(f"{name} link {l.get('id')} endpoints")
        for o in x(d, "//d:Option"):
            if o.get("scale") != o.getparent().get("id"):
                errs.append(f"{name} option scale {o.get('scale')}")
        for r in x(d, "//d:Result"):
            it = r.getparent().get("item")
            multi = item_type[it] == "multi_select_option"
            if multi != (r.get("option") is None) or (not multi and r.get("scale") != item_scale[it]):
                errs.append(f"{name} result {r.get('cite')} option/scale")
            if (r.get("status") == "value") != (r.get("share") is not None):
                errs.append(f"{name} result {r.get('cite')} share/status")
        for a in x(d, "//d:Respondent/d:Answer"):
            if (a.get("option") is not None) and a.get("scale") != item_scale.get(a.get("item")):
                errs.append(f"{name} answer scale")
        for f in x(d, "//d:Flag"):
            if (f.get("item") is None) == (f.get("thread") is None):
                errs.append(f"{name} flag {f.get('cite')} item/thread")
        sets = x(d, "//d:AssignmentSet")
        if sets and sum(s.get("status") == "current" for s in sets) != 1:
            errs.append(f"{name}: current assignment sets ≠ 1")
        for g in x(d, "//d:Group"):
            if g.get("role") == "gate" and not g.get("gate"):
                errs.append(f"{name} group {g.get('id')} has no gate")
        cur = {a.get("thread"): a.get("group") for a in x(d, "//d:AssignmentSet[@status='current']/d:Assignment")}
        for l in x(d, "//d:Link[@type='in_group']"):
            if cur.get(l.get("fromThread")) != l.get("toGroup"):
                errs.append(f"{name} in_group {l.get('id')} disagrees with assignment")
    unassigned = set(i.get("id") for i in x(full, "//d:Thread")) - {a.get("thread") for a in x(full, "//d:Assignment")}
    check("C05", "Rules beyond XSD 1.0 hold in every instance", not errs and not unassigned,
          f"violations {len(errs)}: {errs[:5] or 'none'}; threads without assignment: {sorted(unassigned) or 'none'}")

    # C06 — level and stakeholder reachability
    nodes = {n.get("id"): (n.get("facet"), n.get("parent")) for n in x(full, "//d:Node")}
    def facets(c):
        out = set()
        for ref in c.xpath("d:Carries/d:NodeRef/@node", namespaces=NS):
            n = ref
            while n:
                out.add(nodes[n][0]); n = nodes[n][1]
        return out
    cf = {c.get("id"): (c.get("dimension"), facets(c)) for c in x(full, "//d:Cohort")}
    person_dims = {d.get("id") for d in x(full, "//d:Dimension[@layer='person']")}
    level_dims = {"D-LEVEL", "D-LEVEL-IT", "D-LEVEL-BUS"}
    st_fail = lv_fail = both = 0
    for r in x(full, "//d:Result"):
        dim, f = cf[r.get("cohort")]
        if dim in person_dims and dim not in {"D-LEVEL", "D-STAGE"} and "stakeholderType" not in f:
            st_fail += 1
        if dim in level_dims and "roleLevel" not in f:
            lv_fail += 1
        both += {"stakeholderType", "roleLevel"} <= f
    check("C06", "Results reach stakeholder type and role level through their cohort", st_fail == 0 and lv_fail == 0,
          f"person-cohort results without stakeholder type: {st_fail}; level-cohort results without role level: {lv_fail}; "
          f"results reaching both: {both} (function × level cohorts). Combined-level and S5 decision-stage cohorts span both "
          f"functions, so they reach a level or purchase role, not one stakeholder type")

    # C07 — gate reachability
    item_thread = {i.get("id"): i.getparent().get("id") for i in x(full, "//d:Item")}
    cur = {a.get("thread"): a.get("group") for a in x(full, "//d:AssignmentSet[@status='current']/d:Assignment")}
    grp = {g.get("id"): g.get("gate") or g.get("role") for g in x(full, "//d:Group")}
    per = Counter()
    unreached = 0
    for ir in x(full, "//d:ItemResults"):
        g = cur.get(item_thread[ir.get("item")])
        n = len(ir.findall(f"{{{NS_D}}}Result"))
        if g is None:
            unreached += n
        else:
            per[grp[g]] += n
    check("C07", "Every result reaches a group (and its gate) via the current assignment", unreached == 0,
          f"unreached {unreached}; results per gate/role: {dict(sorted(per.items()))}")

    # C08 — respondent layer
    resp = docs["respondents_open_ended.xml"]
    oe = pd.read_excel("00_source/data/open_ended.xlsx", sheet_name=None, dtype=str)
    other = pd.read_excel("00_source/data/survey.xlsx", sheet_name='"Other" Text Answers', dtype=str)
    mism = 0
    for a in x(resp, "//d:TextAnswer"):
        m = re.fullmatch(r"(SRC-00\d) (.+)!([A-Z]+)(\d+)", a.get("cite"))
        src, sh, col, row = m.groups()
        df = oe[sh] if src == "SRC-003" else other
        i, j = int(row) - 2, column_index_from_string(col) - 1
        if df.iloc[i, j] != a.text or df.iloc[i, 0] != a.getparent().get("respid"):
            mism += 1
    rids = [r.get("respid") for r in x(resp, "//d:Respondent")]
    inferred_attr = sum(len(x(d, "//d:Respondent/d:Attributes[@provenance='INFERRED']")) for d in docs.values())
    no_layer = not x(full, "/d:Study/d:Respondents")
    check("C08", "Respondent layer optional and faithful",
          no_layer and mism == 0 and inferred_attr == 0 and len([r for r in rids if r.strip()]) == 319,
          f"full_study has no Respondents: {no_layer}; text answers {len(x(resp, '//d:TextAnswer'))}, mismatches {mism}; "
          f"respids {len([r for r in rids if r.strip()])} + blank keys {len([r for r in rids if not r.strip()])} (Q-P3a); "
          f"inferred attributes {inferred_attr}")

    # C09 — synthetic containment and provenance counts
    leak = [n for n, d in docs.items() if n in {p.name for p in EXAMPLES} and
            (x(d, "//@provenance[.='SYNTHETIC']") or d.getroot().get("recordKind") != "source")]
    tests_ok = all(d.getroot().get("recordKind") == "syntheticTest" and x(d, "//@provenance[.='SYNTHETIC']")
                   for n, d in docs.items() if n in {p.name for p in TESTS})
    prov = Counter()
    for a in ("provenance", "textProvenance", "typeProvenance", "labelProvenance", "constructProvenance", "definitionProvenance"):
        prov.update(v for v in x(full, f"//@{a}"))
    check("C09", "SYNTHETIC only in tests/; recordKind correct", not leak and tests_ok,
          f"leaks: {leak or 'none'}; full_study provenance tags: {dict(sorted(prov.items()))}")

    # C10 — negative tests
    def mutate(src, fn):
        d = copy.deepcopy(docs[src]); fn(d); return d
    def set_first(xp, attr, val):
        return lambda d: x(d, xp)[0].set(attr, val)
    def dup_seq(d):
        ev = x(d, "//d:GateEvent"); ev[1].set("seq", ev[0].get("seq"))
    def wrong_ns(d):
        raw = etree.tostring(d).replace(NS_D.encode(), NS_D.replace("/v1", "/v2").encode())
        d._setroot(etree.fromstring(raw))
    cases = {
        "result → unknown cohort": ("thread_q15.xml", set_first("//d:Result", "cohort", "C-NOPE")),
        "provenance not a governance tag": ("thread_q15.xml", set_first("//d:Result", "provenance", "GUESS")),
        "wrong namespace (v2)": ("thread_q15.xml", wrong_ns),
        "result option not in its scale": ("full_study.xml", set_first("//d:Result[@option]", "option", "99")),
        "answer option not in its scale": ("synthetic_decision_path.xml", set_first("//d:Answer[@option]", "option", "99")),
        "link → unknown thread": ("thread_q15.xml", set_first("//d:Link[@toThread]", "toThread", "T-Q99")),
        "assignment → unknown group": ("thread_q15.xml", set_first("//d:Assignment", "group", "G-NOPE")),
        "gate not one of the five": ("synthetic_decision_path.xml", set_first("//d:GateEvent", "gate", "CLOSE")),
        "gate state not 1/0": ("synthetic_decision_path.xml", set_first("//d:GateEvent", "state", "0.5")),
        "duplicate event seq in a path": ("synthetic_decision_path.xml", dup_seq),
        "share above 1": ("thread_q15.xml", set_first("//d:Result[@share]", "share", "1.5")),
    }
    caught = []
    with tempfile.TemporaryDirectory() as td:
        for k, (src, fn) in cases.items():
            p = Path(td) / "neg.xml"
            p.write_bytes(etree.tostring(mutate(src, fn), xml_declaration=True, encoding="UTF-8"))
            ok, _ = xmllint(p)
            caught.append((k, not ok))
    missed = [k for k, c in caught if not c]
    check("C10", "Negative tests: broken copies fail validation", not missed,
          f"{sum(c for _, c in caught)} of {len(caught)} rejected; not rejected: {missed or 'none'}")

    # C11 — reproducibility
    before = {str(p): sha(p) for p in GENERATED}
    runs = [subprocess.run([sys.executable, "-I", g], capture_output=True, text=True).returncode for g in GENERATORS]
    changed = [p for p in GENERATED if sha(p) != before[str(p)]]
    check("C11", "Generators re-run byte-identical", runs == [0, 0] and not changed,
          f"{len(GENERATORS)} scripts, {len(GENERATED)} outputs; exit codes {runs}; changed: {changed or 'none'}")

    # C12
    p = subprocess.run(["sha256sum", "-c", "00_source/MANIFEST.sha256"], capture_output=True, text=True)
    check("C12", "Source files match the integrity manifest", p.returncode == 0, p.stdout.strip().replace("\n", "; "))

    # C13 — no study date (ADR-010): no date field; a year may appear only inside verbatim source wording
    date_fields, stray, quoted = [], [], 0
    for n, d in docs.items():
        stems = {i.findtext(f"{{{NS_D}}}Stem") for i in x(d, "//d:Item[@textProvenance='VERBATIM']")}
        for el in d.iter():
            tag = etree.QName(el).localname
            if re.search(r"date|year|field(ed|ing)", tag, re.I):
                date_fields.append(f"{n}: element {tag}")
            for k, v in el.attrib.items():
                if k == "observedAt" and n not in {p.name for p in TESTS}:
                    date_fields.append(f"{n}: observedAt outside tests")
                if re.search(r"date|year|field(ed|ing)", k, re.I):
                    date_fields.append(f"{n}: attribute {k}")
                if k not in ("share", "base", "weight") and re.search(r"(?<!\d)(2012|2013|2014)(?!\d)", v):
                    stray.append(f"{n}: @{k} {v[:50]}")
            t = el.text or ""
            if re.search(r"(?<!\d)(2012|2013|2014)(?!\d)", t):
                if tag in ("Stem", "Label", "Definition") and any(t and (t in st or st in t) for st in stems if st):
                    quoted += 1
                else:
                    stray.append(f"{n}: {tag} {t[:50]}")
    check("C13", "No study date: no date field; a year appears only inside verbatim source wording",
          not date_fields and not stray,
          f"date fields: {date_fields or 'none'}; years outside source wording: {stray[:3] or 'none'}; "
          f"years inside copied source wording (S7 'in calendar year …', kept VERBATIM, not analysed): {quoted}")

    # report
    fails = [r for r in results if r[2] == "FAIL"]
    L = ["# Phase 3 Cross-check", "", "Generated by `scripts/p3_crosscheck.py`. Do not edit by hand.", "",
         f"**Result: {'ALL PASS' if not fails else 'FAILURES'}** — {len(results) - len(fails)} of {len(results)} checks.", "",
         "| # | Check | Result | Evidence |", "|---|---|---|---|"]
    for cid, name, res_, det in results:
        L.append(f"| {cid} | {name} | {res_} | {det.replace('|', '/')} |")
    L += ["", "## Provenance in `full_study.xml` (attribute values)", "", "| Tag | Count |", "|---|---|"]
    for k, v in sorted(prov.items()):
        L.append(f"| {k} | {v} |")
    L.append("")
    (S / "crosscheck_report.md").write_text("\n".join(L), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
