#!/usr/bin/env python3
"""p3_build_instances.py — generate the schema instance documents from Phase 1 and Phase 2 outputs.

Inputs (read-only):
    01_instrument_reconstruction/  question_map, thread_annotations, item_scales, response_scales,
                                   routing, cohort_dimensions, cohorts, scott_grouping, linkages,
                                   review_decisions
    02_data_inventory/             results, significance, variable_dictionary
    00_source/data/                open_ended.xlsx (SRC-003), survey.xlsx "Other" sheet (SRC-002)
Outputs:
    03_schema/examples/full_study.xml            every entity; no respondent layer
    03_schema/examples/thread_q15.xml            one thread (Q15) and everything it references
    03_schema/examples/respondents_open_ended.xml  respondents and their text answers, unchanged
    03_schema/tests/synthetic_decision_path.xml  one invented decision path (SYNTHETIC; not data)

Design: 03_schema/design_brief.md and decisions/ADR-001…013. Every value is copied from its
input file; nothing is recomputed. Output is byte-identical on every run.

Usage: python3 -I scripts/p3_build_instances.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import pandas as pd
from lxml import etree

R1, R2, S = Path("01_instrument_reconstruction"), Path("02_data_inventory"), Path("03_schema")
SRC2, SRC3 = Path("00_source/data/survey.xlsx"), Path("00_source/data/open_ended.xlsx")
NS_D, NS_G = "https://growthenablement.com/ns/dms/v1", "https://growthenablement.com/ns/gates/v1"
D, G = f"{{{NS_D}}}", f"{{{NS_G}}}"
NSMAP = {None: NS_D, "g": NS_G}
SCHEMA_VERSION = "1.0.0"
CANON_SHEET = "Industry 7"           # canonical sheet for the All-respondents column (as in Phase 1)
SHEETS = ["Main Page", "Industry 7", "Company Size & Revenue", "Sales Engagement", "Decision Making Stages"]
ALL_COHORT = "C-L-ALL-RESPONDENTS"
MIN_N = 25

FACET = {"D-FUNCTION": "stakeholderType", "D-LEVEL-IT": "roleLevel", "D-LEVEL-BUS": "roleLevel",
         "D-DEPT": "department", "D-ITROLE": "itRole", "D-STAGE": "purchaseRole", "D-STAGE-BUS": "purchaseRole"}
DIRECTED = {"routes_to", "derived_from", "specify_of", "breakout_of", "in_group"}
GROUP_IDS = OrderedDict([
    ("Screener metadata", ("G-SCREENER", "input", "TARGET")),
    ("Baseline", ("G-BASELINE", "baseline", None)),
    ("Access", ("G-ACCESS", "gate", "ACCESS")),
    ("Successful meeting (I call it agree to explore now)", ("G-AGREE", "gate", "AGREE")),
    ("Shared Vision", ("G-VISION", "gate", "VISION")),
    ("Business Case", ("G-CASE", "gate", "CASE")),
    ("Relationship accounts (open-ended)", ("G-RELATIONSHIP", "crossGate", None)),
])
MISSING_TARGET = {"S8 (raw, not tabulated)": "S8_raw"}
SIG_STATE = {"significant": "significant", "not_significant": "notSignificant", "not_tested": "notTested"}

# Scott's gate questions, quoted (design_intent.md §2.2.2) — RECALL_DESIGNER
GATES = [
    ("TARGET", 1, "Target", "Did the vendor and then the salesperson target the right message to the right people (Target 1 or 0)"),
    ("ACCESS", 2, "Access", "Did the vendor and then the salesperson gain access to the right people (Access 1 or 0)"),
    ("AGREE", 3, "Agree", "Did the vendor and then the salesperson gain agreement with the right people to explore the idea further (Agree 1 or 0)"),
    ("VISION", 4, "Vision", "Did the vendor and then the salesperson gain a shared vision of success with the right people (Vision 1 or 0)"),
    ("CASE", 5, "Case", "Did the vendor and then the salesperson provide a business case for the idea the client accepts (case 1 or 0)"),
]
GATE_DEFINITION = ("My NEW version of this a series of binary gates that are designed to track choices "
                   "(which is the foundational source of reality) and to measure state change")
TITLE = ("The Receiving End of Go-to-Market: What Decision Makers Experience with Vendors, "
         "from First Contact to Signed Contract")


def rd(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def sub(_parent, _tag, _text=None, **attrs):
    el = etree.SubElement(_parent, D + _tag, {k: v for k, v in attrs.items() if v not in (None, "")})
    if _text not in (None, ""):
        el.text = _text
    return el


def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def clean_xml_text(t):
    """XML 1.0 cannot hold most control characters; report any instead of altering text."""
    bad = [c for c in t if ord(c) < 32 and c not in "\t\n\r"]
    return bad


class Data:
    def __init__(self):
        self.qmap = rd(R1 / "question_map.csv")
        self.ann = rd(R1 / "thread_annotations.csv").set_index("thread_id")
        self.item_scale = dict(rd(R1 / "item_scales.csv")[["item_id", "scale_id"]].values)
        self.scales = rd(R1 / "response_scales.csv")
        self.routing = rd(R1 / "routing.csv")
        self.dims = rd(R1 / "cohort_dimensions.csv")
        self.cohorts = rd(R1 / "cohorts.csv")
        self.grouping = rd(R1 / "scott_grouping.csv")
        self.links = rd(R1 / "linkages.csv")
        rev = rd(R1 / "review_decisions.csv")
        self.reviewed = {(r.file, r.id) for r in rev.itertuples() if r.decision == "approved"}
        self.results = rd(R2 / "results.csv")
        self.sig = rd(R2 / "significance.csv")
        self.vars = rd(R2 / "variable_dictionary.csv")
        self.thread_order = list(OrderedDict.fromkeys(self.qmap.thread_id))
        self.items = {r.item_id: r for r in self.qmap.itertuples()}
        self.item_thread = dict(self.qmap[["item_id", "thread_id"]].values)
        self.cohort_by_id = {c.cohort_id: c for c in self.cohorts.itertuples()}
        self.group_of = {r.thread_id: GROUP_IDS[r.scott_group][0] for r in self.grouping.itertuples()}
        # stakeholder nodes: one per person cohort; combined level cohorts carry both function nodes
        self.nodes, self.carries = OrderedDict(), defaultdict(list)
        for c in self.cohorts.itertuples():
            if c.dimension_id in FACET:
                nid = "N-" + c.cohort_id[2:]
                parent = "N-" + c.parent_cohort[2:] if c.parent_cohort in self.cohort_by_id and \
                    self.cohort_by_id[c.parent_cohort].dimension_id in FACET else ""
                self.nodes[nid] = (FACET[c.dimension_id], c.label, parent, c.label_prov)
                self.carries[c.cohort_id].append(nid)
        for c in self.cohorts.itertuples():
            if c.dimension_id == "D-LEVEL":
                for dim in ("D-LEVEL-IT", "D-LEVEL-BUS"):
                    for o in self.cohorts.itertuples():
                        if o.dimension_id == dim and o.label == c.label:
                            self.carries[c.cohort_id].append("N-" + o.cohort_id[2:])

    # ---------- link endpoints ----------
    def endpoints(self, row):
        a = {}
        if row.source in self.ann.index:
            a["fromThread"] = row.source
        elif row.source in self.items:
            a["fromItem"] = row.source
        if row.target in self.ann.index:
            a["toThread"] = row.target
        elif row.target in self.items:
            a["toItem"] = row.target
        elif row.target.startswith("G:"):
            a["toGroup"] = GROUP_IDS[row.target[2:]][0]
        elif row.target in MISSING_TARGET:
            a["toVariable"] = MISSING_TARGET[row.target]
        return a


def build_study(dd: Data, sid, threads, result_items, link_filter, note, with_flags=True, with_vars=True):
    """Build one self-contained Study. `threads`: threads to include (with all their items)."""
    root = etree.Element(D + "Study", nsmap=NSMAP, id=sid, schemaVersion=SCHEMA_VERSION,
                         recordKind="source", sampleN="319", confidenceLevel="0.95", provenance="RECON_DATA")
    sub(root, "Title", TITLE)
    sub(root, "Note", note)
    src = sub(root, "Sources")
    sub(src, "Source", "Structured results: tabulated report, N=319, five table sheets and an 'Other' text sheet",
        id="SRC-002", path=str(SRC2), provenance="RECON_DATA")
    sub(src, "Source", "Open-ended responses, respondent-level, one sheet per question Q21–Q25",
        id="SRC-003", path=str(SRC3), provenance="RECON_DATA")
    gate_model(root)

    items_in = [i for i in dd.qmap.item_id if dd.item_thread[i] in threads]
    scales_in = {dd.item_scale[i] for i in items_in}

    # results and flags
    res = dd.results[dd.results.item_id.isin(result_items)]
    cohorts_in = set(res.cohort_id)
    flag_threads = {dd.item_thread[i] for i in result_items}
    flags = dd.sig[dd.sig.thread_id.isin(flag_threads)] if with_flags else dd.sig.iloc[0:0]
    dims_in = set(flags.dimension_id)

    # variables
    var = dd.vars[dd.vars.thread_id.isin(threads) | (dd.vars.kind == "missing" if sid == "DMS-FULL" else False)] \
        if with_vars else dd.vars.iloc[0:0]

    # links (both ends inside the slice, groups and variables pulled in as needed)
    lk = [r for r in dd.links.itertuples() if link_filter(r)]
    var_ids = set(var.variable)
    for r in lk:
        e = dd.endpoints(r)
        if "toVariable" in e and e["toVariable"] not in var_ids:
            var = pd.concat([var, dd.vars[dd.vars.variable == e["toVariable"]]])
            var_ids.add(e["toVariable"])

    # cohorts → parents, dimensions, nodes
    if sid == "DMS-FULL":
        cohorts_in = set(dd.cohorts.cohort_id)
    frontier = list(cohorts_in)
    while frontier:
        c = dd.cohort_by_id[frontier.pop()]
        if c.parent_cohort in dd.cohort_by_id and c.parent_cohort not in cohorts_in:
            cohorts_in.add(c.parent_cohort)
            frontier.append(c.parent_cohort)
    dims_in |= {dd.cohort_by_id[c].dimension_id for c in cohorts_in}
    dimrow = {d.dimension_id: d for d in dd.dims.itertuples()}
    frontier = [d for d in dims_in if d in dimrow]
    while frontier:
        p = dimrow[frontier.pop()].parent_dimension
        if p and p not in dims_in:
            dims_in.add(p)
            frontier.append(p)
    nodes_in = set()
    for c in cohorts_in:
        for n in dd.carries.get(c, []):
            while n:
                nodes_in.add(n)
                n = dd.nodes[n][2]

    # ----- Instrument -----
    ins = sub(root, "Instrument")
    sc_el = sub(ins, "Scales")
    for s in dd.scales.itertuples():
        if s.scale_id not in scales_in:
            continue
        el = sub(sc_el, "Scale", id=s.scale_id, type=s.scale_type, direction=s.direction, family=s.family,
                 labelProvenance=s.label_prov if s.label_prov != "n/a" else None, provenance=s.annotation_prov,
                 reviewed="confirmedByScott" if ("scale_annotations.csv", s.scale_id) in dd.reviewed else None)
        sub(el, "Rationale", s.rationale)
        nonsub = set(json.loads(s.non_substantive_labels))
        for k, lab in enumerate(json.loads(s.labels), 1):
            sub(el, "Option", lab, scale=s.scale_id, seq=str(k), substantive="false" if lab in nonsub else "true")
    th_el = sub(ins, "Threads")
    for t in dd.thread_order:
        if t not in threads:
            continue
        a = dd.ann.loc[t]
        tel = sub(th_el, "Thread", id=t, question=a.base_question, construct=a.construct, section=a.section,
                  constructProvenance=a.provenance,
                  reviewed="confirmedByScott" if ("thread_annotations.csv", t) in dd.reviewed else None,
                  provenance="RECON_DATA")
        for q in dd.qmap[dd.qmap.thread_id == t].itertuples():
            iel = sub(tel, "Item", id=q.item_id, seq=q.item_seq, role=q.item_role, type=q.question_type,
                      scale=dd.item_scale[q.item_id], base=q.base_all,
                      stemComplete={"yes": "true", "no": "false"}.get(q.stem_complete),
                      cite=q.source_cite, textProvenance=q.text_prov, typeProvenance=q.type_prov,
                      provenance="RECON_DATA")
            sub(iel, "Stem", q.stem) if q.stem else etree.SubElement(iel, D + "Stem")
            sub(iel, "Label", q.item_label)
            sub(iel, "PipingToken", q.piping_token)
    rules = [r for r in dd.routing.itertuples() if sid == "DMS-FULL"
             or any(tok in items_in for tok in re.findall(r"[A-Z]\d+\w*", r.applies_to))]
    if rules:
        rr = sub(ins, "RoutingRules")
        for r in rules:
            el = sub(rr, "Rule", id=r.rule_id, kind=r.kind, check=r.check, provenance=r.provenance)
            sub(el, "Condition", r.condition)
            sub(el, "Action", r.action)
            sub(el, "AppliesTo", r.applies_to)
            for tok in OrderedDict.fromkeys(re.findall(r"[A-Z]\d+\w*", r.applies_to)):
                if tok in items_in:
                    sub(el, "Target", item=tok)
            sub(el, "Evidence", r.evidence)
            sub(el, "Note", r.note)

    # ----- Population -----
    if not cohorts_in:
        pop = None
    else:
        pop = sub(root, "Population")
    h = sub(pop, "StakeholderHierarchy", id="DMS-SCREENER", provenance="RECALL_DESIGNER") if nodes_in else None
    if h is not None:
        sub(h, "Definition", "Function (IT / business) at the top; level, department, IT role and purchase-process "
                         "role beneath it (Scott, 2026-10-28). Nodes come from the screener answers S1–S6.")
    for nid, (facet, label, parent, lprov) in dd.nodes.items():
        if nid in nodes_in:
            sub(h, "Node", id=nid, facet=facet, label=label, parent=parent, labelProvenance=lprov,
                provenance="RECALL_DESIGNER")
    de = sub(pop, "Dimensions") if dims_in else None
    if "ALL" in dims_in:
        sub(de, "Dimension", id="ALL", name="All respondents", layer="all", membership="all", tabulated="true",
            provenance="RECON_DATA")
    for d in dd.dims.itertuples():
        if d.dimension_id not in dims_in:
            continue
        el = sub(de, "Dimension", id=d.dimension_id, name=d.name, layer=d.layer, parent=d.parent_dimension,
                 membership=d.membership, tabulated="true" if d.tabulated == "yes" else "false",
                 sourceItems=d.source_items, derivedFrom=d.derived_from, definitionProvenance=d.definition_prov,
                 provenance=d.hierarchy_prov or "RECON_DATA")
        sub(el, "Definition", d.definition)
    ce = sub(pop, "Cohorts", minimumN=str(MIN_N)) if cohorts_in else None
    for c in dd.cohorts.itertuples():
        if c.cohort_id not in cohorts_in:
            continue
        el = sub(ce, "Cohort", id=c.cohort_id, dimension=c.dimension_id, label=c.label, n=c.n,
                 status="tabulated" if c.status == "tabulated" else "definable",
                 belowMinimum="false" if c.min_n_flag == "ok" else "true",
                 parent=c.parent_cohort if c.parent_cohort in dd.cohort_by_id else None,
                 sheet=c.sheet, column=c.column, cite=c.source_cite, labelProvenance=c.label_prov,
                 provenance=c.n_prov)
        if dd.carries.get(c.cohort_id):
            ca = sub(el, "Carries")
            for n in dd.carries[c.cohort_id]:
                sub(ca, "NodeRef", node=n)

    # ----- Grouping -----
    grp = sub(root, "Grouping")
    groups_in = {dd.group_of[t] for t in threads}
    for label, (gid, role, gate) in GROUP_IDS.items():
        if gid in groups_in:
            sub(grp, "Group", id=gid, label=label, role=role, gate=gate, provenance="RECALL_DESIGNER")
    aset = sub(grp, "AssignmentSet", id="SCOTT-2026-10-28", author="Scott Santucci", status="current",
               provenance="RECALL_DESIGNER")
    for r in dd.grouping.itertuples():
        if r.thread_id in threads:
            el = sub(aset, "Assignment", thread=r.thread_id, group=dd.group_of[r.thread_id], provenance=r.provenance)
            sub(el, "Note", r.note)

    # ----- Results -----
    rs = sub(root, "Results", source="SRC-002") if result_items else None
    by_item = OrderedDict((i, []) for i in dd.qmap.item_id if i in set(res.item_id))
    for r in res.itertuples():
        by_item[r.item_id].append(r)
    for item, rows in by_item.items():
        multi = dd.items[item].question_type == "multi_select_option"
        ir = sub(rs, "ItemResults", item=item)
        groups = OrderedDict()
        for r in rows:
            groups.setdefault((r.cohort_id, r.option_seq), []).append(r)
        for (cohort, opt), cells in groups.items():
            cells = sorted(cells, key=lambda x: (x.sheet != CANON_SHEET, SHEETS.index(x.sheet)))
            p = cells[0]
            el = sub(ir, "Result", cohort=cohort, option=None if multi else opt,
                     scale=None if multi else dd.item_scale[item],
                     status="value" if p.value_status == "value" else "notAsked",
                     share=p.value if p.value_status == "value" else None, base=p.base_n,
                     cite=f"{p.sheet}!{p.cell}", baseCite=p.base_source, provenance="RECON_DATA")
            for o in cells[1:]:
                sub(el, "AlsoAt", cite=f"{o.sheet}!{o.cell}")
    if len(flags):
        fe = sub(rs, "SignificanceFlags")
        for f in flags.itertuples():
            on_item = f.block_item_id in dd.items
            el = sub(fe, "Flag", item=f.block_item_id if on_item else None, thread=None if on_item else f.thread_id,
                     dimension=f.dimension_id, state=SIG_STATE[f.state],
                     tableSize=f.table_size, cite=f"{f.sheet}!{f.cell}", provenance="RECON_DATA")
            sub(el, "Comment", f.comment)

    # ----- Variables -----
    if len(var):
        ve = sub(root, "Variables")
        for v in var.itertuples():
            item = v.variable if v.variable in dd.items else (v.variable.split("__")[0] if "__" in v.variable
                                                              and v.variable.split("__")[0] in dd.items else None)
            if item and dd.item_thread[item] not in threads:
                item = None
            prov = "INFERRED" if v.provenance.startswith("INFERRED") else v.provenance
            el = sub(ve, "Variable", id=v.variable, kind=v.kind, status=v.status, item=item, type=v.type,
                     scale=v.scale_id if v.scale_id in scales_in else None, provenance=prov)
            sub(el, "Label", v.label)
            sub(el, "ValidValues", v.valid_values)
            sub(el, "Rule", v.derivation_rule)
            sub(el, "Note", v.note)

    # ----- Graph -----
    if lk:
        ge = sub(root, "Graph")
        for r in lk:
            e = dd.endpoints(r)
            ev = r.evidence
            if "toVariable" in e:
                ev += f" [target '{r.target}' recorded as variable {e['toVariable']}]"
            el = sub(ge, "Link", id=f"L{int(r.Index) + 1:04d}", type=r.link_type,
                     directed="true" if r.link_type in DIRECTED else "false", weight=r.weight,
                     reviewed="confirmedByScott" if r.provenance == "INFERRED" else None,
                     provenance=r.provenance, **e)
            sub(el, "Evidence", ev)
    return root


def gate_model(root, prov="RECALL_DESIGNER"):
    gm = etree.SubElement(root, G + "GateModel", id="VCP-GATES", version="1.0.0", author="Scott Santucci",
                          provenance=prov)
    etree.SubElement(gm, G + "Definition").text = GATE_DEFINITION
    for gid, order, label, q in GATES:
        g = etree.SubElement(gm, G + "Gate", id=gid, order=str(order), label=label, provenance=prov)
        etree.SubElement(g, G + "Question").text = q
    return gm


def respondents_doc(dd: Data):
    """Respondent-level text: open-ended Q21–Q25 (SRC-003) and 'please specify' answers (SRC-002)."""
    oe = pd.read_excel(SRC3, sheet_name=None, dtype=str)
    other = pd.read_excel(SRC2, sheet_name='"Other" Text Answers', dtype=str)
    answers = defaultdict(list)          # respid → [(item, text, cite)]
    order = []
    errors = []
    for sheet, d in oe.items():
        item = sheet
        for i, r in d.iterrows():
            rid, txt = r["respid"], r.iloc[2]
            if pd.isna(rid):
                continue
            if rid not in answers:
                order.append(rid)
            answers[rid]
            if pd.isna(txt) or not str(txt).strip():
                continue
            if clean_xml_text(txt):
                errors.append(f"control character in {sheet} row {i + 2}")
            answers[rid].append((item, txt, f"SRC-003 {sheet}!{col_letter(2)}{i + 2}"))
    # 'please specify' columns map to items by the column each item cites (question_map.csv source_cite)
    by_col = {}
    for q in dd.qmap.itertuples():
        m = re.fullmatch(r'SRC-002 "Other" Text Answers!([A-Z]+)1', q.source_cite)
        if m:
            by_col[m.group(1)] = q.item_id
    col_items = []
    for j, c in enumerate(other.columns):
        if j == 0:
            continue
        item = by_col.get(col_letter(j))
        if item is None:
            errors.append(f"'Other' column {col_letter(j)} {c!r} maps to no item")
        col_items.append((j, item))
    for i, r in other.iterrows():
        rid = r.iloc[0]
        if pd.isna(rid):
            continue
        for j, item in col_items:
            txt = r.iloc[j]
            if pd.isna(txt) or not str(txt).strip():
                continue
            if rid not in answers:
                order.append(rid)
            answers[rid].append((item, txt, f'SRC-002 "Other" Text Answers!{col_letter(j)}{i + 2}'))
    used = {it for v in answers.values() for it, _, _ in v}
    threads = {dd.item_thread[i] for i in used}
    root = build_study(dd, "DMS-RESPONDENTS", threads, result_items=set(), link_filter=lambda r: False,
                       note="Respondent layer: every respondent-level text answer in the source, unchanged. "
                            "Respondents carry no function, level, or stakeholder value — none was collected. "
                            "One Q21 answer (SRC-003 Q21 row 6) has a blank respid (a single space) in the source; "
                            "it is stored under that blank key, not attributed. Row 6 holds respid 112 on the "
                            "other four sheets (open question Q-P3a).",
                       with_flags=False, with_vars=False)
    re_el = sub(root, "Respondents", source="SRC-003; SRC-002 \"Other\" Text Answers")
    for rid in order:
        rel = sub(re_el, "Respondent", respid=rid, provenance="RECON_DATA")
        for item, txt, cite in answers[rid]:
            sub(rel, "TextAnswer", txt, item=item, cite=cite, provenance="VERBATIM")
    return root, errors


def synthetic_doc(dd: Data):
    """One invented decision-maker path. Not data (ADR-013)."""
    threads = {"T-Q15", "T-Q18"}
    root = etree.Element(D + "Study", nsmap=NSMAP, id="DMS-SYNTHETIC-TEST", schemaVersion=SCHEMA_VERSION,
                         recordKind="syntheticTest", provenance="SYNTHETIC")
    sub(root, "Title", "Synthetic test record — not data")
    sub(root, "Note", "One invented decision-maker's path through the five gates, used only to prove the "
                      "decision-path layer validates (ADR-013). Excluded from every count and analysis. "
                      "The instrument elements are copied from the study so reasons can point to real questions.")
    gate_model(root)
    full = build_study(dd, "TMP", threads, set(), lambda r: False, "", with_flags=False, with_vars=False)
    root.append(full.find(D + "Instrument"))
    rs = sub(root, "Respondents", source="synthetic")
    r = sub(rs, "Respondent", respid="SYN-0001", provenance="SYNTHETIC")
    sub(r, "Answer", item="Q15_2", provenance="SYNTHETIC")            # multi-select: selected
    sub(r, "Answer", item="Q18", scale=dd.item_scale["Q18"], option="4", provenance="SYNTHETIC")
    p = sub(r, "DecisionPath", id="SYN-PATH-1", provenance="SYNTHETIC")
    sub(p, "Context", "Invented opportunity used to exercise every rule: all five gates, a not-yes with reasons, "
                      "recovery at the same gate, one event with clock time and the rest without.")
    events = [
        (1, "TARGET", "1", "vendor", None, []),
        (2, "ACCESS", "1", "salesperson", "2000-01-03T09:00:00", []),
        (3, "AGREE", "1", "salesperson", None, []),
        (4, "VISION", "0", "decisionMaker", None, [("T-Q15", "Q15_2", None), ("T-Q15", "Q15_4", None)]),
        (5, "VISION", "1", "salesperson", None, []),
        (6, "CASE", "0", "decisionMaker", None, [("T-Q18", "Q18", "4")]),
        (7, "CASE", "1", "decisionMaker", None, []),
    ]
    for seq, gate, state, actor, at, reasons in events:
        e = sub(p, "GateEvent", seq=str(seq), gate=gate, state=state, observedAt=at, actor=actor, provenance="SYNTHETIC")
        for th, it, opt in reasons:
            sub(e, "Reason", thread=th, item=it, option=opt, provenance="SYNTHETIC")
    return root


def write(root, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
    path.write_bytes(data)
    return len(data)


def main() -> int:
    dd = Data()
    all_threads = set(dd.thread_order)
    result_items = set(dd.results.item_id)
    full = build_study(dd, "DMS-FULL", all_threads, result_items, lambda r: True,
                       "Full study: every thread, item, scale, routing rule, cohort, result, significance flag, "
                       "variable and link in Phases 1–2. Respondent layer omitted (see respondents_open_ended.xml).")
    # Q15 slice: the thread, every link touching it, and the threads those links reach
    touch = lambda r: "T-Q15" in (r.source, r.target) or dd.item_thread.get(r.source) == "T-Q15" \
        or dd.item_thread.get(r.target) == "T-Q15"
    nb = {"T-Q15"}
    for r in dd.links.itertuples():
        if touch(r):
            for end in (r.source, r.target):
                if end in dd.ann.index:
                    nb.add(end)
                elif end in dd.items:
                    nb.add(dd.item_thread[end])
    q15_items = {i for i in result_items if dd.item_thread[i] == "T-Q15"}
    q15 = build_study(dd, "DMS-Q15", nb, q15_items, touch,
                      "Slice: thread Q15 ('pulled back') with its items, scale, every cohort that reports it, its "
                      "results, significance flags, variables and links; neighbouring threads are included so "
                      "every link endpoint resolves. Results are for Q15 only.")
    resp, errors = respondents_doc(dd)
    syn = synthetic_doc(dd)
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    out = {S / "examples/full_study.xml": full, S / "examples/thread_q15.xml": q15,
           S / "examples/respondents_open_ended.xml": resp, S / "tests/synthetic_decision_path.xml": syn}
    for p, root in out.items():
        n = write(root, p)
        print(f"{p}: {n} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
