#!/usr/bin/env python3
"""p5_crosscheck.py — Phase 5 cross-check: verbatims intact, codes complete and defined, links sound, nothing inferred
about respondents, numbers traceable, everything reproducible.

Checks:
    C01 Verbatims unchanged: corpus.csv text = the source cell it cites (SRC-002 / SRC-003, read with openpyxl)
        = the TextAnswer in respondents_open_ended.xml = the TextAnswer in respondents_coded.xml
    C02 Every code used (main and blind re-code) has an entry in the coding frame; every code has an exclude rule and an
        example; every example occurs verbatim in the answer or instrument item it cites
    C03 Every answer is covered exactly once (one not-codable code, or coded), and every coded row links
        answer → respid → item → thread exactly as the corpus does
    C04 Coding rules hold: not-codable answers carry nothing else; every codable answer has a gate and a valence;
        polarity on behaviour codes and only there; exactly one primary per answer and layer
    C05 No level or stakeholder type on any respondent: no Attributes in any respondent layer; no level, stakeholder,
        function or seniority column in any P5 table; respondent-level views keyed by respid only
    C06 The coded instance (schema 1.2.0) validates, carries the frame and every code row, and every 1.1.0 example
        still validates against 1.2.0
    C07 Every number in findings.md appears in a generated file
    C08 Every P5 script re-runs byte-identical (all outputs, run in dependency order)
    C09 Every third-party package imported by a Phase 5 script is listed in requirements.txt
    C10 Source files match the integrity manifest
Output: 05_open_ended/crosscheck_report.md. Exit 1 if any check fails.
Usage: python3 -I scripts/p5_crosscheck.py
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402
from lxml import etree  # noqa: E402

from p5_build_coding_frame import rows as frame_rows  # noqa: E402

D = Path("05_open_ended")
EX = Path("03_schema/examples")
XSD = Path("03_schema/decision-maker-study.xsd")
NS = {"d": "https://growthenablement.com/ns/dms/v1"}
SRC = {"SRC-002": Path("00_source/data/survey.xlsx"), "SRC-003": Path("00_source/data/open_ended.xlsx")}
results = []
# Scripts in dependency order, with the files each writes (C08).
RUNS = [
    (["scripts/p5_build_corpus.py"], ["05_open_ended/corpus.csv"]),
    (["scripts/p5_build_coding_frame.py", "--require-examples"], ["05_open_ended/coding_frame.md"]),
    (["scripts/p5_build_index.py"], sorted(str(p) for p in (D / "index").glob("*"))),
    (["scripts/p5_build_text_views.py"], sorted(str(p) for p in (D / "views").glob("*") if p.is_file())),
    (["scripts/p5_draw_sample.py"], ["05_open_ended/coding/sample_s03.csv"]),
    (["scripts/p5_expand_codes.py", "05_open_ended/coding/codes_sample_s03_compact.psv", "05_open_ended/coding/codes_sample_s03.csv", "claude-s03"],
     ["05_open_ended/coding/codes_sample_s03.csv"]),
    (["scripts/p5_summarize_codes.py", "05_open_ended/coding/codes_sample_s03.csv", "05_open_ended/coding/sample_s03_summary.md", "Inductive pass — sample code counts (P5.S03)"],
     ["05_open_ended/coding/sample_s03_summary.md"]),
    (["scripts/p5_precode.py"], sorted(str(p) for p in (D / "coding").glob("precoded*")) + sorted(str(p) for p in (D / "coding").glob("worklist*"))),
    (["scripts/p5_assemble_codes.py"], ["05_open_ended/codes.csv"]),
    (["scripts/p5_draw_recode_sample.py"], ["05_open_ended/coding/recode_sample.csv"]),
    (["scripts/p5_expand_codes.py", "05_open_ended/coding/recode_compact.psv", "05_open_ended/coding/recode.csv", "claude-recode"],
     ["05_open_ended/coding/recode.csv"]),
    (["scripts/p5_agreement.py"], ["05_open_ended/consistency_report.md", "05_open_ended/coding/agreement.csv", "05_open_ended/coding/disagreements.csv"]),
    (["scripts/p5_build_coded_views.py"], sorted(str(p) for p in (D / "views/coded").glob("*"))),
    (["scripts/p5_build_coded_instance.py"], ["03_schema/examples/respondents_coded.xml", "03_schema/schema_mapping_coding.csv"]),
]


def r_example(frame, code):
    return next(r["example"] for r in frame if r["code"] == code)


def check(cid, name, ok, detail):
    results.append((cid, name, "PASS" if ok else "FAIL", detail))
    print(f"{cid} {'PASS' if ok else 'FAIL'} — {name} | {detail}")


def sha(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def xmllint(f):
    p = subprocess.run(["xmllint", "--noout", "--schema", str(XSD), str(f)], capture_output=True, text=True)
    return p.returncode == 0


def main() -> int:
    rd = lambda p: pd.read_csv(p, dtype=str, keep_default_na=False)
    corpus = rd(D / "corpus.csv")
    codes = rd(D / "codes.csv")
    recode = rd(D / "coding/recode.csv")
    frame = frame_rows()
    fcodes = {r["code"]: r for r in frame}

    # C01 — verbatims
    from openpyxl import load_workbook
    wbs = {k: load_workbook(v, read_only=False, data_only=True) for k, v in SRC.items()}
    src_mism = []
    for r in corpus.itertuples(index=False):
        m = re.match(r"^(SRC-00[23]) (.+)!([A-Z]+\d+)$", r.cite)
        val = wbs[m.group(1)][m.group(2)][m.group(3)].value
        if str(val) != r.text:
            src_mism.append(r.answer_id)
    def texts(f):
        out = {}
        for a in etree.parse(str(f)).xpath("//d:TextAnswer", namespaces=NS):
            m = re.search(r"!([A-Z]+)(\d+)$", a.get("cite"))
            out[f"{a.get('item')}-R{int(m.group(2)):03d}"] = a.text
        return out
    t_open, t_coded = texts(EX / "respondents_open_ended.xml"), texts(EX / "respondents_coded.xml")
    cmap = dict(zip(corpus.answer_id, corpus.text))
    inst_mism = [a for a in cmap if t_open.get(a) != cmap[a] or t_coded.get(a) != cmap[a]]
    check("C01", "Verbatims unchanged: source cell = corpus = 1.1.0 instance = coded instance",
          not src_mism and not inst_mism and len(t_open) == len(t_coded) == len(cmap),
          f"{len(cmap)} answers; source mismatches {len(src_mism)}; instance mismatches {len(inst_mism)}; "
          f"answers in instances {len(t_open)} / {len(t_coded)}")

    # C02 — codes defined; frame examples verbatim
    used = set(codes.code) | set(recode.code)
    undefined = sorted(used - set(fcodes))
    bad_ex = []
    for r in frame:
        m = re.search(r"example ([A-Z][\w]+-R\d{3})", r.get("source", ""))
        if r.get("example") and m:
            if r["example"].strip() not in cmap.get(m.group(1), ""):
                bad_ex.append(r["code"])
    n_ex = sum(1 for r in frame if r.get("example") and re.search(r"example ([A-Z][\w]+-R\d{3})", r.get("source", "")))
    qm = rd(Path("01_instrument_reconstruction/question_map.csv")).set_index("item_id")
    inst = [(r["code"], re.search(r"example instrument (\S+) (stem|item_label)", r["source"])) for r in frame
            if "example instrument" in r.get("source", "")]
    bad_ex += [c for c, m in inst if not m or r_example(frame, c) not in qm.loc[m.group(1), m.group(2)]]
    no_ex = [r["code"] for r in frame if not r.get("example") or not r.get("exclude")]
    n_ex += len(inst)
    check("C02", "Every code used is defined; every code has an exclude rule and an example; every example verbatim at its citation",
          not undefined and not bad_ex and not no_ex,
          f"{len(used)} codes used (main + re-code) of {len(fcodes)} defined; undefined {undefined or 'none'}; "
          f"{n_ex} cited examples ({len(inst)} from the instrument, for codes no answer carries), not found {bad_ex or 'none'}; "
          f"codes without an example or exclude rule: {no_ex or 'none'}")

    # C03 — coverage and links
    per = codes.groupby("answer_id")
    nc = codes[codes.layer == "notcodable"].answer_id
    va = codes[codes.layer == "valence"].answer_id.unique()
    covered = set(nc) | set(va)
    both = set(nc) & set(va)
    missing = sorted(set(corpus.answer_id) - covered)
    extra = sorted(set(codes.answer_id) - set(corpus.answer_id))
    key = corpus.set_index("answer_id")[["respid", "item", "thread", "frame"]]
    j = codes.join(key, on="answer_id", rsuffix="_c")
    badlink = j[(j.respid != j.respid_c) | (j.item != j.item_c) | (j.thread != j.thread_c) | (j.frame != j.frame_c)]
    check("C03", "Every answer covered exactly once; every code row links answer → respid → item → thread as the corpus does",
          not missing and not extra and not both and nc.duplicated().sum() == 0 and badlink.empty,
          f"{len(corpus)} answers: not codable {nc.nunique()}, coded {len(va)}; missing {len(missing)}; unknown {len(extra)}; "
          f"both {len(both)}; duplicate N- {int(nc.duplicated().sum())}; rows {len(codes)}, link mismatches {len(badlink)}")

    # C04 — coding rules
    v = []
    ncset = set(nc)
    v += [f"{a}: N- with other codes" for a, g in per if a in ncset and len(g) > 1]
    for a, g in per:
        if a in ncset:
            continue
        ls = set(g.layer)
        if not {"gate", "valence"} <= ls:
            v.append(f"{a}: no gate or valence")
    pol = codes[(codes.polarity != "") != (codes.layer == "behaviour")]
    v += [f"{r.answer_id}: polarity rule ({r.code})" for r in pol.itertuples()]
    prim = codes.groupby(["answer_id", "layer"]).primary.apply(lambda s: (s == "True").sum())
    v += [f"{a}/{l}: {n} primaries" for (a, l), n in prim.items() if n != 1]
    rprim = recode.groupby(["answer_id", "layer"]).primary.apply(lambda s: (s == "True").sum())
    v += [f"recode {a}/{l}: {n} primaries" for (a, l), n in rprim.items() if n != 1]
    check("C04", "Coding rules: N- exclusive; gate and valence on every codable answer; polarity on behaviour only; one primary per answer and layer",
          not v, f"violations {len(v)}: {v[:5] or 'none'} (main {len(codes)} rows, re-code {len(recode)} rows)")

    # C05 — nothing about level or stakeholder
    attrs = sum(len(etree.parse(str(f)).xpath("//d:Respondent/d:Attributes", namespaces=NS)) for f in EX.glob("*.xml"))
    pat = re.compile(r"^(role_?level|level|stakeholder(_?type)?|function|seniority|job_?title|title)$", re.I)
    cols = []
    for f in sorted(D.rglob("*.csv")):
        hdr = pd.read_csv(f, nrows=0).columns
        cols += [f"{f.relative_to(D)}:{c}" for c in hdr if pat.search(c)]
    fm = pd.read_csv(D / "views/coded/framework_matrix.csv", nrows=0).columns[0]
    ty = pd.read_csv(D / "views/coded/typology.csv", nrows=0).columns.tolist()
    check("C05", "No level or stakeholder type on any respondent; respondent views keyed by respid only",
          attrs == 0 and not cols and fm == "respid" and ty == ["respid", "type"],
          f"Respondent/Attributes in examples: {attrs}; P5 columns naming level, stakeholder, function, seniority or title: {cols or 'none'}; "
          f"framework matrix key '{fm}'; typology columns {ty}")

    # C06 — coded instance
    doc = etree.parse(str(EX / "respondents_coded.xml"))
    n_def = int(doc.xpath("count(//d:Coding/d:CodeDef)", namespaces=NS))
    n_app = int(doc.xpath("count(//d:Coding/d:Applied)", namespaces=NS))
    ver = {f.name: etree.parse(str(f)).getroot().get("schemaVersion") for f in sorted(EX.glob("*.xml"))}
    valid = {f.name: xmllint(f) for f in sorted(EX.glob("*.xml"))}
    xsd_v = etree.parse(str(XSD)).getroot().get("version")
    check("C06", "Coded instance validates and carries the frame and every code; 1.1.0 examples still validate",
          all(valid.values()) and n_def == len(frame) and n_app == len(codes) and ver["respondents_coded.xml"] == xsd_v,
          f"schema {xsd_v}; versions {ver}; valid {valid}; CodeDef {n_def} / frame {len(frame)}; Applied {n_app} / code rows {len(codes)}")

    # C07 — findings numbers traceable
    gen = [D / "views/coded/summary.md", D / "consistency_report.md", D / "views/summary.md",
           Path("04_analytics_library/outputs/T04/summary.md"), Path("04_analytics_library/outputs/T09/summary.md"),
           Path("02_data_inventory/open_ended_inventory.md")]
    gen += sorted((D / "views/coded").glob("*.csv")) + [D / "coding/agreement.csv"]
    norm = lambda s: s.replace("−", "-").replace(",", "")
    hay = norm(" ".join(p.read_text(encoding="utf-8") for p in gen if p.exists()))
    hay_nums = set(re.findall(r"\d+(?:\.\d+)?", hay))
    text = re.sub(r"`[^`]*`", " ", (D / "findings.md").read_text(encoding="utf-8"))
    text = re.sub(r"\b(P|C|Q|L|T|S|D|M)\d+\w*", " ", text)    # IDs (P05, Q22, L28, …) are names, not numbers
    nums = re.findall(r"\d+(?:\.\d+)?", norm(text))
    absent = sorted({n for n in nums if n not in hay_nums and n not in {"1", "2", "3", "4"}}, key=float)
    check("C07", "Every number in findings.md appears in a generated file", not absent,
          f"{len(nums)} numbers checked against {sum(p.exists() for p in gen)} generated files; not found {absent or 'none'}")

    # C08 — reproducibility
    outs = sorted({o for _, os_ in RUNS for o in os_})
    before = {o: sha(o) for o in outs}
    rc = []
    for cmd, _ in RUNS:
        p = subprocess.run([sys.executable, "-I"] + cmd, capture_output=True, text=True)
        rc.append(p.returncode)
    changed = [o for o in outs if sha(o) != before[o]]
    check("C08", "Every P5 script re-runs byte-identical", all(c == 0 for c in rc) and not changed,
          f"{len(RUNS)} runs, {len(outs)} outputs; exit codes {sorted(set(rc))}; changed {changed or 'none'}")

    # C09 — dependencies
    req = {re.split(r"[<>=]", l.strip())[0].lower() for l in Path("requirements.txt").read_text().splitlines() if l.strip()}
    alias = {"sklearn": "scikit-learn", "vadersentiment": "vadersentiment", "openpyxl": "openpyxl"}
    local = {p.stem for p in Path("scripts").glob("p*.py")}
    used_p = set()
    for s in sorted(Path("scripts").glob("p5_*.py")):
        for m in re.findall(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", s.read_text(encoding="utf-8"), re.M):
            if m not in sys.stdlib_module_names and m not in local:
                used_p.add(alias.get(m.lower(), m.lower()))
    unlisted = sorted(used_p - req)
    check("C09", "Every third-party package used by Phase 5 is in requirements.txt", not unlisted,
          f"used {sorted(used_p)}; unlisted {unlisted or 'none'}")

    # C10
    p = subprocess.run(["sha256sum", "-c", "00_source/MANIFEST.sha256"], capture_output=True, text=True)
    check("C10", "Source files match the integrity manifest", p.returncode == 0, p.stdout.strip().replace("\n", "; "))

    fails = [r for r in results if r[2] == "FAIL"]
    L = ["# Phase 5 Cross-check", "", "Generated by `scripts/p5_crosscheck.py`. Do not edit by hand.", "",
         f"**Result: {'ALL PASS' if not fails else 'FAILURES'}** — {len(results) - len(fails)} of {len(results)} checks.", "",
         "| # | Check | Result | Evidence |", "|---|---|---|---|"]
    for cid, name, r_, det in results:
        L.append(f"| {cid} | {name} | {r_} | {det.replace('|', '/')} |")
    L.append("")
    (D / "crosscheck_report.md").write_text("\n".join(L), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
