"""p4_lib.py — shared reader for Phase 4 techniques. Reads the schema instance, never the source files.

Every technique script imports this module (scripts/ is added to sys.path explicitly, because
techniques run with `python3 -I`). Everything here is a read of 03_schema/examples/full_study.xml.

    study = load()                      # parsed full_study.xml
    results(study)    → DataFrame: item, thread, gate, group, cohort, dimension, option, option_label,
                                   share, base, n, below_min, usable, status, cite
    cohorts(study)    → DataFrame: cohort, dimension, layer, label, n, below_min, stakeholder_type, role_level
    flags(study)      → DataFrame: item, thread, gate, dimension, state, cite
    variables(study)  → DataFrame: id, kind, status, item, scale, role, reviewed, rule, provenance
    links(study)      → DataFrame: id, type, source, target, weight, directed, provenance
    items(study)      → DataFrame: item, thread, type, role, scale, stem, label
    options(study)    → dict scale → [labels in order]

Minimum n (Scott, 2026-10-28): a result is `usable` for comparisons only if its cohort n ≥ 25 and its
item base ≥ 25. Rows below are kept, flagged, never dropped.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from lxml import etree

NS = {"d": "https://growthenablement.com/ns/dms/v1", "g": "https://growthenablement.com/ns/gates/v1"}
FULL = Path("03_schema/examples/full_study.xml")
MIN_N = 25
GATE_ORDER = ["TARGET", "baseline", "ACCESS", "AGREE", "VISION", "CASE", "crossGate"]
OUT = Path("04_analytics_library/outputs")


@lru_cache(maxsize=1)
def load(path: str = str(FULL)):
    return etree.parse(path)


def _x(doc, xp):
    return doc.xpath(xp, namespaces=NS)


def _gate_of_thread(doc):
    cur = {a.get("thread"): a.get("group") for a in _x(doc, "//d:AssignmentSet[@status='current']/d:Assignment")}
    grp = {g.get("id"): (g.get("gate") or g.get("role")) for g in _x(doc, "//d:Group")}
    return {t: grp[g] for t, g in cur.items()}, cur


def items(doc):
    rows = []
    for i in _x(doc, "//d:Item"):
        rows.append({"item": i.get("id"), "thread": i.getparent().get("id"), "type": i.get("type"),
                     "role": i.get("role"), "scale": i.get("scale"),
                     "stem": i.findtext(f"{{{NS['d']}}}Stem"), "label": i.findtext(f"{{{NS['d']}}}Label")})
    return pd.DataFrame(rows)


def options(doc):
    out = {}
    for s in _x(doc, "//d:Scale"):
        out[s.get("id")] = [o.text for o in s.findall(f"{{{NS['d']}}}Option")]
    return out


def cohorts(doc):
    nodes = {n.get("id"): (n.get("facet"), n.get("label"), n.get("parent")) for n in _x(doc, "//d:Node")}
    layer = {d.get("id"): d.get("layer") for d in _x(doc, "//d:Dimension")}
    rows = []
    for c in _x(doc, "//d:Cohort"):
        st, lv = set(), set()
        for ref in c.xpath("d:Carries/d:NodeRef/@node", namespaces=NS):
            n = ref
            while n:
                facet, label, parent = nodes[n]
                if facet == "stakeholderType":
                    st.add(label)
                if facet == "roleLevel":
                    lv.add(label)
                n = parent
        rows.append({"cohort": c.get("id"), "dimension": c.get("dimension"), "layer": layer.get(c.get("dimension")),
                     "label": c.get("label"), "n": int(c.get("n")), "below_min": c.get("belowMinimum") == "true",
                     "status": c.get("status"), "stakeholder_type": ";".join(sorted(st)),
                     "role_level": ";".join(sorted(lv))})
    return pd.DataFrame(rows)


def results(doc):
    gate_of, group_of = _gate_of_thread(doc)
    it = items(doc).set_index("item")
    opts = options(doc)
    co = cohorts(doc).set_index("cohort")
    rows = []
    for ir in _x(doc, "//d:ItemResults"):
        item = ir.get("item")
        thread = it.loc[item, "thread"]
        for r in ir.findall(f"{{{NS['d']}}}Result"):
            opt = r.get("option")
            scale = it.loc[item, "scale"]
            label = opts[scale][int(opt) - 1] if opt else (it.loc[item, "label"] or it.loc[item, "stem"])
            c = co.loc[r.get("cohort")]
            base = int(r.get("base")) if r.get("base") else None
            rows.append({"item": item, "thread": thread, "gate": gate_of[thread], "group": group_of[thread],
                         "cohort": r.get("cohort"), "dimension": c["dimension"], "option": int(opt) if opt else None,
                         "option_label": label, "share": float(r.get("share")) if r.get("share") else None,
                         "base": base, "n": int(c["n"]), "below_min": bool(c["below_min"]),
                         "usable": (c["n"] >= MIN_N) and (base is not None and base >= MIN_N),
                         "status": r.get("status"), "cite": r.get("cite")})
    return pd.DataFrame(rows)


def flags(doc):
    gate_of, _ = _gate_of_thread(doc)
    it = items(doc).set_index("item")
    rows = []
    for f in _x(doc, "//d:Flag"):
        thread = f.get("thread") or it.loc[f.get("item"), "thread"]
        rows.append({"item": f.get("item"), "thread": thread, "gate": gate_of[thread], "dimension": f.get("dimension"),
                     "state": f.get("state"), "cite": f.get("cite")})
    return pd.DataFrame(rows)


def variables(doc):
    rows = []
    for v in _x(doc, "//d:Variable"):
        rows.append({"id": v.get("id"), "kind": v.get("kind"), "status": v.get("status"), "item": v.get("item"),
                     "scale": v.get("scale"), "role": v.get("role"), "reviewed": v.get("reviewed"),
                     "rule": v.findtext(f"{{{NS['d']}}}Rule"), "provenance": v.get("provenance")})
    return pd.DataFrame(rows)


def links(doc):
    rows = []
    for l in _x(doc, "//d:Link"):
        src = l.get("fromThread") or l.get("fromItem")
        tgt = l.get("toThread") or l.get("toItem") or l.get("toGroup") or l.get("toVariable")
        rows.append({"id": l.get("id"), "type": l.get("type"), "source": src, "target": tgt,
                     "weight": float(l.get("weight")), "directed": l.get("directed") == "true",
                     "provenance": l.get("provenance")})
    return pd.DataFrame(rows)


def write_csv(df, path):
    """Deterministic CSV: fixed float format, LF line endings."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n", float_format="%.4f")
    return path
