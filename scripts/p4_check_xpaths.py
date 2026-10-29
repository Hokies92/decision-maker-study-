#!/usr/bin/env python3
"""p4_check_xpaths.py — every technique file is complete, and every XPath it names exists in the XSD.

Reads the front matter of 04_analytics_library/T*.md (and TEMPLATE.md) and checks:
    1. every required field is present and non-empty (GOVERNANCE §5 P4: question, XPaths, assumptions
       — in the body —, minimum n, output form; plus validity and the ecological caveat)
    2. every element name (d:Name, g:Name) and attribute name (@name) in every XPath is declared in
       03_schema/decision-maker-study.xsd or 03_schema/gates.xsd
    3. every XPath outside the respondent layer selects at least one node in full_study.xml
A built-in negative test runs first: a technique naming an element and an attribute that do not exist
must fail. If it does not, the check itself is broken and the script exits 2.

Usage: python3 -I scripts/p4_check_xpaths.py            (exit 0 = all pass, 1 = failures, 2 = self-test failed)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from lxml import etree

LIB = Path("04_analytics_library")
XSDS = {"d": Path("03_schema/decision-maker-study.xsd"), "g": Path("03_schema/gates.xsd")}
FULL = Path("03_schema/examples/full_study.xml")
NS = {"d": "https://growthenablement.com/ns/dms/v1", "g": "https://growthenablement.com/ns/gates/v1"}
XS = "{http://www.w3.org/2001/XMLSchema}"
REQUIRED = ["id", "title", "gates", "question", "required_xpaths", "minimum_n", "validity", "ecological_caveat",
            "output_form", "script", "outputs", "provenance"]
BODY_SECTIONS = ["## Question", "## Method", "## Assumptions", "## Minimum n", "## Validity", "## Output"]


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm, key = {}, None
    for line in m.group(1).splitlines():
        line = re.sub(r"\s+#.*$", "", line)
        if not line.strip():
            continue
        if line.startswith("  - ") and key:
            fm[key].append(line[4:].strip())
        elif ":" in line and not line.startswith(" "):
            key, val = line.split(":", 1)
            key, val = key.strip(), val.strip()
            fm[key] = [] if val == "" else val
    return fm


def declared():
    names = {}
    for p, path in XSDS.items():
        root = etree.parse(str(path)).getroot()
        names[p] = ({e.get("name") for e in root.iter(f"{XS}element") if e.get("name")},
                    {a.get("name") for a in root.iter(f"{XS}attribute") if a.get("name")})
    return names


def xpath_problems(xp, names, full):
    probs = []
    for prefix, name in re.findall(r"\b([dg]):([A-Za-z_][\w]*)", xp):
        if name not in names[prefix][0]:
            probs.append(f"element {prefix}:{name} not in XSD")
    all_attrs = names["d"][1] | names["g"][1]
    for name in re.findall(r"@([A-Za-z_]\w*)", xp):
        if name not in all_attrs:
            probs.append(f"attribute @{name} not in XSD")
    if not probs and "d:Respondents" not in xp:
        try:
            n = len(full.xpath(xp, namespaces=NS))
        except etree.XPathError as e:
            probs.append(f"invalid XPath ({e})")
        else:
            if n == 0:
                probs.append("selects nothing in full_study.xml")
    return probs


def check_file(path, text, names, full):
    errs = []
    fm = front_matter(text)
    if fm is None:
        return [f"{path}: no front matter"]
    for k in REQUIRED:
        if not fm.get(k):
            errs.append(f"{path}: field '{k}' missing or empty")
    for sec in BODY_SECTIONS:
        if sec not in text:
            errs.append(f"{path}: section '{sec}' missing")
    if fm.get("minimum_n") and fm["minimum_n"] != "25":
        errs.append(f"{path}: minimum_n is {fm['minimum_n']}, project minimum is 25")
    if fm.get("ecological_caveat", "").startswith("yes") and "## Ecological caveat" not in text:
        errs.append(f"{path}: ecological_caveat yes but no 'Ecological caveat' section")
    for xp in fm.get("required_xpaths") or []:
        for p in xpath_problems(xp, names, full):
            errs.append(f"{path}: {xp} — {p}")
    return errs


def main() -> int:
    names = declared()
    full = etree.parse(str(FULL))
    template = (LIB / "TEMPLATE.md").read_text(encoding="utf-8")

    # negative self-test: a broken technique must fail
    bad = template.replace("/d:Study/d:Results/d:ItemResults/d:Result/@share",
                           "/d:Study/d:Results/d:Bogus/@nonexistent", 1)
    bad_errs = check_file("SELFTEST", bad, names, full)
    caught = any("d:Bogus" in e for e in bad_errs) and any("@nonexistent" in e for e in bad_errs)
    if not caught:
        print("SELFTEST FAILED: a non-existent element/attribute was not caught", file=sys.stderr)
        return 2
    print("selftest PASS — broken XPath rejected:", "; ".join(e.split(" — ")[1] for e in bad_errs))

    files = [LIB / "TEMPLATE.md"] + sorted(LIB.glob("T[0-9][0-9]-*.md"))
    errs, n_xp = [], 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        n_xp += len((front_matter(text) or {}).get("required_xpaths") or [])
        errs += check_file(str(f), text, names, full)
    for e in errs:
        print("FAIL:", e)
    print(f"files={len(files)} xpaths={n_xp} failures={len(errs)}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
