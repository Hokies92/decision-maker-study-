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


# ---------------------------------------------------------------- measures
# Option labels counted by each approved summary definition (variable_review_decisions.csv, P4.S01).
# measures() checks every label against the Variable/Rule text in the instance and stops on a mismatch.
SUMMARY_OPTIONS = {
    ("SC-FREQ4", "topbox"): ["Frequently"],
    ("SC-FREQ4", "top2"): ["Occasionally", "Frequently"],
    ("SC-AGREE4", "top2"): ["Agree", "Strongly agree"],
    ("SC-IMPORT4", "top2"): ["Very important", "Somewhat important"],
    ("SC-DIFF3", "differentiator"): ["Important, and a differentiator"],
    ("SC-MATERIALS7", "self_built"): [4, 5],          # option seqs; labels quoted in the rule
}


@lru_cache(maxsize=1)
def _measures_cached():
    return _build_measures(load())


def measures(doc=None):
    """Long table of measures per cohort.

    kind = summary    an approved summary variable (role headline / secondary)
           selection  share selecting a multi-select item
           option     share choosing one option of a single-choice item (measure id 'ITEM=seq')
    Columns: measure, kind, role, item, thread, gate, cohort, dimension, value, base, n, usable, label
    A measure is computed only where every result it needs is a value (not 'notAsked').
    """
    return _measures_cached() if doc is None else _build_measures(doc)


def _build_measures(doc):
    r = results(doc)
    it = items(doc).set_index("item")
    opts = options(doc)
    v = variables(doc)
    rows = []
    key = ["item", "cohort"]
    by = {k: g for k, g in r.groupby(key, sort=False)}
    for s in v[v.kind == "summary"].itertuples():
        item, suffix = s.id.split("__")
        spec = SUMMARY_OPTIONS[(s.scale, suffix)]
        labels = [opts[s.scale][o - 1] if isinstance(o, int) else o for o in spec]
        for lab, o in zip(labels, spec):
            probe = f"options {o}" if isinstance(o, int) else lab
            if probe not in s.rule and not (isinstance(o, int) and str(o) in s.rule):
                raise SystemExit(f"{s.id}: rule text does not name {lab!r}")
        seqs = [opts[s.scale].index(l) + 1 for l in labels]
        for (i, c), g in by.items():
            if i != item:
                continue
            g2 = g[g.option.isin(seqs)]
            if len(g2) != len(seqs) or (g2.status != "value").any():
                continue
            rows.append({"measure": s.id, "kind": "summary", "role": s.role, "item": item, "label": s.id,
                         "values": g2.share.sum(), "first": g2.iloc[0]})
    for (i, c), g in by.items():
        t = it.loc[i, "type"]
        if t == "multi_select_option":
            x = g.iloc[0]
            if x.status == "value":
                rows.append({"measure": i, "kind": "selection", "role": "", "item": i, "label": x.option_label,
                             "values": x.share, "first": x})
        elif t == "single_select":
            for x in g.itertuples():
                if x.status == "value":
                    rows.append({"measure": f"{i}={int(x.option)}", "kind": "option", "role": "", "item": i,
                                 "label": x.option_label, "values": x.share, "first": pd.Series(x._asdict())})
    out = []
    for m in rows:
        f = m["first"]
        out.append({"measure": m["measure"], "kind": m["kind"], "role": m["role"], "item": m["item"],
                    "thread": f["thread"], "gate": f["gate"], "cohort": f["cohort"], "dimension": f["dimension"],
                    "value": round(float(m["values"]), 6), "base": f["base"], "n": f["n"], "usable": bool(f["usable"]),
                    "label": m["label"]})
    return pd.DataFrame(out)


# ------------------------------------------------------- headline measures
# One number per substantive question per cohort, for techniques that compare questions across cohorts
# (T07–T09). Rules (INFERRED where noted):
#   grid rows with a summary measure     → the approved headline summary measure
#   multi-select options                 → the share selecting the option
#   Q9, Q10, Q16 (single frequency items)→ share answering "Frequently" (extends the approved headline; INFERRED)
#   Q18                                  → Q18__self_built (approved)
#   Q14                                  → options 3–5, "the typical agenda helps" (INFERRED)
# Excluded: screener threads (they define the cohorts), the attention check, "Other" and "Don't know" rows.
HEADLINE_SINGLE = {"Q9": ["Q9=4"], "Q10": ["Q10=4"], "Q16": ["Q16=4"], "Q14": ["Q14=3", "Q14=4", "Q14=5"]}
EXCLUDE_LABEL = ("Other", "Don’t know", "Don't know")


def headline_measures():
    m = measures()
    it = items(load()).set_index("item")
    keep = []
    for item, g in m.groupby("item", sort=False):
        if it.loc[item, "thread"].startswith("T-S") or it.loc[item, "role"] == "attention_check":
            continue
        label = (it.loc[item, "label"] or "")
        if label.startswith(EXCLUDE_LABEL):
            continue
        h = g[(g.kind == "summary") & (g.role == "headline")]
        if item in HEADLINE_SINGLE:
            parts = g[g.measure.isin(HEADLINE_SINGLE[item])]
            agg = parts.groupby("cohort", sort=False).agg(value=("value", "sum"), k=("value", "size"),
                                                          base=("base", "first"), n=("n", "first"),
                                                          usable=("usable", "all"), dimension=("dimension", "first"),
                                                          thread=("thread", "first"), gate=("gate", "first")).reset_index()
            agg = agg[agg.k == len(HEADLINE_SINGLE[item])].drop(columns="k")
            agg["measure"] = item + ("__help" if item == "Q14" else "__frequently")
            agg["item"] = item
            agg["rule"] = " + ".join(HEADLINE_SINGLE[item])
            agg["provenance"] = "INFERRED"
            keep.append(agg)
        elif not h.empty:
            x = h.copy(); x["rule"] = "approved headline"; x["provenance"] = "INFERRED (confirmed by Scott)"
            keep.append(x)
        elif (g.kind == "selection").any():
            x = g[g.kind == "selection"].copy(); x["rule"] = "share selecting"; x["provenance"] = "RECON_DATA"
            keep.append(x)
    cols = ["measure", "item", "thread", "gate", "cohort", "dimension", "value", "base", "n", "usable", "rule", "provenance"]
    out = pd.concat([k[cols] for k in keep], ignore_index=True)
    out["value"] = out.value.round(6)
    return out


def cohort_matrix(min_cohorts=20):
    """Usable cohorts (excluding All respondents) × headline measures, values only where usable.
    Returns (wide DataFrame cohorts × measures, long headline table)."""
    h = headline_measures()
    u = h[h.usable & (h.cohort != "C-L-ALL-RESPONDENTS")]
    wide = u.pivot(index="cohort", columns="measure", values="value")
    wide = wide.loc[:, wide.notna().sum() >= min_cohorts]
    return wide.sort_index().reindex(sorted(wide.columns), axis=1), h
