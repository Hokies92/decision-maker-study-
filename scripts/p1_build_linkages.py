#!/usr/bin/env python3
"""p1_build_linkages.py — every link between question threads that the instrument defines.

Inputs (read-only, all Phase 1 outputs or source):
    question_map.csv, item_scales.csv, routing.csv, cohort_dimensions.csv, cohort_tags.csv,
    scott_grouping.csv, construct_links.csv (authored), and SRC-002 / SRC-003 for respid overlap
Outputs (01_instrument_reconstruction/):
    linkages.csv       edge list: source, target, level, link_type, weight, evidence, provenance
    linkages.graphml   the same graph for network tools (nodes = threads + Scott's groups)
    linkages.md        link types, counts, per-thread degree, group-level summary

Link types:
    shared_scale       two threads use the same closed answer scale                RECON_DATA
    routes_to          one answer decides who is asked another question           RECON_DATA
    breakout_of        a screener thread splits another thread's results           RECON_DATA
    derived_from       an item is computed from another item                       RECON_DATA / INFERRED
    specify_of         a "please specify" text item belongs to its parent item     RECON_DATA
    same_respondents   two text threads answered by the same respids (weight = n)  RECON_DATA
    mirror             paired wording (most/least, best/worst)                     RECON_DATA
    same_construct     threads measuring the same idea                             INFERRED
    topic              open-ended thread bears on a structured thread              INFERRED
    relates_to         screener dimension bears on a thread (from cohort model)    INFERRED
    in_group           thread → Scott's group                                      RECALL_DESIGNER

Usage: python3 -I scripts/p1_build_linkages.py
"""

from __future__ import annotations

import csv
import itertools
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd

RD = Path("01_instrument_reconstruction")
SRC2, SRC3 = Path("00_source/data/survey.xlsx"), Path("00_source/data/open_ended.xlsx")
OUT_CSV, OUT_GML, OUT_MD = RD / "linkages.csv", RD / "linkages.graphml", RD / "linkages.md"
FIELDS = ["source", "target", "level", "link_type", "weight", "evidence", "provenance"]


def read(name):
    return list(csv.DictReader((RD / name).open(encoding="utf-8")))


def qid(t):
    return f"{t[2]}{int(t[3:])}"


def main() -> int:
    qmap = read("question_map.csv")
    item_thread = {q["item_id"]: q["thread_id"] for q in qmap}
    threads = sorted({q["thread_id"] for q in qmap}, key=lambda t: (t[2] != "S", int(t[3:])))
    groups = {r["thread_id"]: r["scott_group"] for r in read("scott_grouping.csv")}
    edges, errors = [], []

    def edge(src, tgt, level, lt, weight, ev, prov):
        edges.append({"source": src, "target": tgt, "level": level, "link_type": lt,
                      "weight": weight, "evidence": ev, "provenance": prov})

    # shared_scale (closed scales used by more than one thread)
    by_scale = defaultdict(set)
    for r in read("item_scales.csv"):
        if r["scale_id"] != "SC-OPEN":
            by_scale[r["scale_id"]].add(r["thread_id"])
    for sc, ts in by_scale.items():
        for a, b in itertools.combinations(sorted(ts, key=threads.index), 2):
            edge(a, b, "thread", "shared_scale", 1, f"both use {sc}", "RECON_DATA")

    # routes_to and specify_of (from routing.csv)
    for r in read("routing.csv"):
        rid, applies = r["rule_id"], r["applies_to"]
        if rid in ("R01", "R02"):
            for tgt in re.findall(r"S\d+", applies):
                edge("T-S01", f"T-S{int(tgt[1:]):02d}", "thread", "routes_to", 1,
                     f"skip_logic {rid}: {r['condition']} → {r['action']}", r["provenance"])
        elif rid == "R11":
            edge("Q20_PurchaseLimit", "Q20_2", "item", "routes_to", 1, f"skip_logic {rid}", r["provenance"])
        elif rid.startswith("R13") or rid.startswith("R14"):
            child = applies.strip()
            parent_thread = item_thread.get(child) or item_thread.get(f"{child}_text")
            edge(child, parent_thread, "item→thread", "specify_of", 1, f"skip_logic {rid}: {r['evidence']}",
                 r["provenance"])

    # derived_from (from question_map)
    for q in qmap:
        if q["derived_from"]:
            for src in re.split(r";\s*", q["derived_from"]):
                edge(q["item_id"], src, "item", "derived_from", 1, q["derived_evidence"], q["derived_prov"])

    # breakout_of (cohort tags → screener threads)
    dims = {d["dimension_id"]: d["source_items"] for d in read("cohort_dimensions.csv")}
    seen = set()
    for t in read("cohort_tags.csv"):
        if t["link_type"] != "breakout_of":
            continue
        for s in dims[t["source"]].split(";"):
            key = (f"T-S{int(s[1:]):02d}", t["target_thread"])
            if key in seen:
                continue
            seen.add(key)
            edge(key[0], key[1], "thread", "breakout_of", 1, f"via {t['source']}: {t['rationale']}", "RECON_DATA")
        if t["link_type"] == "relates_to":
            pass
    for t in read("cohort_tags.csv"):
        if t["link_type"] == "relates_to":
            src_dim = t["source"].split(":")[0]
            s = dims[src_dim].split(";")[0]
            edge(f"T-S{int(s[1:]):02d}", t["target_thread"], "thread", "relates_to", 1,
                 f"{t['source']}: {t['rationale']}", t["provenance"])

    # mirror, same_construct, topic (authored)
    for r in read("construct_links.csv"):
        for t in (r["source"], r["target"]):
            if t not in threads:
                errors.append(f"construct_links: unknown thread {t}")
        edge(r["source"], r["target"], "thread", r["link_type"], 1, r["rationale"], r["provenance"])

    # same_respondents (respid overlap among text answers)
    resp = {}
    oe = pd.read_excel(SRC3, sheet_name=None, dtype=str)
    for k, d in oe.items():
        a = d.iloc[:, 2].astype(str).str.strip()
        resp[f"T-Q{int(k[1:]):02d}"] = set(d.loc[d["respid"].notna() & a.ne("") & a.ne("nan"), "respid"])
    other = pd.read_excel(SRC2, sheet_name='"Other" Text Answers', dtype=str)
    spec = defaultdict(set)
    for c in other.columns[1:]:
        m = re.match(r"((?:Q|S)\d+)", str(c))
        v = other[c].astype(str).str.strip()
        ids = set(other.loc[other["respid"].notna() & other[c].notna() & v.ne(""), "respid"])
        if ids:
            spec[f"T-{m.group(1)[0]}{int(m.group(1)[1:]):02d}"] |= ids
    for a, b in itertools.combinations(sorted(resp), 2):
        n = len(resp[a] & resp[b])
        if n:
            edge(a, b, "thread", "same_respondents", n, f"{n} respondents answered both", "RECON_DATA")
    for s, ids in sorted(spec.items(), key=lambda kv: threads.index(kv[0])):
        for o in sorted(resp):
            n = len(ids & resp[o])
            if n:
                edge(s, o, "thread", "same_respondents", n,
                     f"{n} respondents who wrote a 'please specify' answer in {qid(s)} also answered {qid(o)}", "RECON_DATA")

    # in_group (Scott's grouping)
    for t in threads:
        edge(t, f"G:{groups[t]}", "thread→group", "in_group", 1, "scott_grouping.csv", "RECALL_DESIGNER")

    # integrity
    for e in edges:
        for end in (e["source"], e["target"]):
            if end.startswith("T-") and end not in threads:
                errors.append(f"unknown thread {end} in {e['link_type']}")
    if errors:
        for x in errors:
            print("ERROR:", x, file=sys.stderr)
        return 2

    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader(); w.writerows(edges)

    # GraphML — thread and group nodes, thread-level edges only (item edges stay in the CSV)
    tedges = [e for e in edges if e["level"] in ("thread", "thread→group")]
    gnodes = sorted({e["target"] for e in tedges if e["target"].startswith("G:")})
    g = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
         '  <key id="kind" for="node" attr.name="kind" attr.type="string"/>',
         '  <key id="group" for="node" attr.name="group" attr.type="string"/>',
         '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
         '  <key id="type" for="edge" attr.name="link_type" attr.type="string"/>',
         '  <key id="prov" for="edge" attr.name="provenance" attr.type="string"/>',
         '  <key id="w" for="edge" attr.name="weight" attr.type="double"/>',
         '  <graph id="threads" edgedefault="undirected">']
    for t in threads:
        g.append(f'    <node id="{t}"><data key="kind">thread</data><data key="group">{escape(groups[t])}</data>'
                 f'<data key="label">{qid(t)}</data></node>')
    for n in gnodes:
        g.append(f'    <node id="{escape(n)}"><data key="kind">group</data><data key="label">{escape(n[2:])}</data></node>')
    for i, e in enumerate(tedges):
        g.append(f'    <edge id="e{i}" source="{escape(e["source"])}" target="{escape(e["target"])}">'
                 f'<data key="type">{e["link_type"]}</data><data key="prov">{e["provenance"]}</data>'
                 f'<data key="w">{e["weight"]}</data></edge>')
    g += ["  </graph>", "</graphml>", ""]
    OUT_GML.write_text("\n".join(g), encoding="utf-8")

    # Markdown
    cnt = defaultdict(int)
    for e in edges:
        cnt[(e["link_type"], e["provenance"])] += 1
    deg = defaultdict(lambda: defaultdict(int))
    for e in tedges:
        if e["link_type"] == "in_group":
            continue
        for end in (e["source"], e["target"]):
            if end.startswith("T-"):
                deg[end][e["link_type"]] += 1
    grp_links = defaultdict(int)
    for e in tedges:
        if e["link_type"] in ("in_group", "breakout_of"):
            continue
        a, b = groups.get(e["source"]), groups.get(e["target"])
        if a and b and a != b:
            grp_links[tuple(sorted((a, b)))] += 1
    L = ["# Linkage Inventory", "",
         "Generated by `scripts/p1_build_linkages.py`. Every link the instrument itself defines, as an edge list "
         "(`linkages.csv`) and a graph (`linkages.graphml`, for network tools). Statistical links between results "
         "belong to Phase 4.", "",
         f"**{len(edges)} links** across {len(threads)} threads and {len(gnodes)} groups.", "",
         "## Link types", "", "| Link type | Provenance | Count |", "|---|---|---|"]
    for (lt, pv), n in sorted(cnt.items()):
        L.append(f"| {lt} | {pv} | {n} |")
    L += ["", "## Links between Scott's groups (excluding screener breakouts)", "",
          "| Group A | Group B | Links |", "|---|---|---|"]
    for (a, b), n in sorted(grp_links.items(), key=lambda kv: -kv[1]):
        L.append(f"| {a} | {b} | {n} |")
    types = ["breakout_of", "shared_scale", "routes_to", "same_respondents", "mirror", "same_construct", "topic", "relates_to"]
    L += ["", "## Links per thread", "", "| Thread | Group | " + " | ".join(types) + " | Total |",
          "|---|---|" + "---|" * (len(types) + 1)]
    for t in threads:
        row = [deg[t].get(x, 0) for x in types]
        L.append(f"| {qid(t)} | {groups[t]} | " + " | ".join(str(x) for x in row) + f" | {sum(row)} |")
    L.append("")
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"edges={len(edges)} graph_edges={len(tedges)} types={dict(sorted({k[0]: 0 for k in cnt}.items())).keys()}")
    for (lt, pv), n in sorted(cnt.items()):
        print(f"  {lt:17} {pv:15} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
