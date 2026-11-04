#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""Conformance suite for unifold tools.

Two sorts of tests, both run through the command line only, so that another
implementation can be tested with `--tool`:

- CASES: a small project (file path -> content) and the findings that
  `check --json` must report for it, as "severity rule file". The comparison
  is exact: nothing missing, nothing extra.
- SCENARIOS: a sequence of commands with assertions (init, impact, --fix,
  JSON on failure, idempotent generation, ...).

    uv run tests/conformance.py                  all tests against the reference tool
    uv run tests/conformance.py NAME ...         only tests whose name contains NAME
    uv run tests/conformance.py --tool "CMD"     test another implementation
    uv run tests/conformance.py --write DIR      write every case to DIR/<name>/
    uv run tests/conformance.py --list           names of all tests

How a case runs: the files are written to an empty folder named `demo`; then
`CMD check --fix demo` (unless the case says fix=False: the cases for rule
G1, where the test is what `check` says about files nobody generated); then
`CMD check --json [args] demo`. With `--tool`, the generator under test runs,
never the reference generator.

A meta test compares the rule table in docs/references/rules.md, which the
site build generates from the reference tool, with the tool under test
(`CMD rules --json`) and demands a failing case for every rule.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "docs/skills/unifold/scripts/unifold.py"
RULES_MD = REPO / "docs/references/rules.md"
README_TEMPLATE = REPO / "docs/skills/unifold/assets/README.template.md"
MARK = "<!-- unifold:generated - do not edit; run `unifold check --fix` -->"

ROOT = 'unifold: "0.4"\nresponsibility: A demo\n'
UNIT = "responsibility: A part\n"
COMPOSITE = UNIT + "kind: stateful\n"              # a unit with children states a kind
X = "ref:x"                                       # the contract both sides of x name
NEEDS_X = "needs:\n  x: {summary: Needs x, contract: %s}\n" % X
AT_ROOT_X = NEEDS_X.replace(X, "docs/references/x.md")   # NEEDS_X in a root written by hand
CAPABILITY_X = "capabilities:\n  x: {summary: Offers x, contract: %s}\n" % X
WIRED = "wiring:\n  a.x: b.x\n"
README = "# {name}\n\nWhat it is for.\n\n## Why\n\nBecause.\n"
AGENTS = "# AGENTS.md: {name}\n\nunifold unit; run `unifold show` here.\n\n## Why\n\nBecause.\n"  # hand-written: not allowed
DECISION = "---\nstatus: {status}\ndate: {date}\n{more}---\n# A decision\n\nText.\n"
ITEM = ("# Context of a\n\n### [demo/0001 A decision](../../../docs/decisions/0001-x.md)\n"
        "\nx holds, so a does y.\n")
CONTEXT = "a/docs/explanation/context.md"
WHY = "# {name}\n\nWhat it is for.\n\n## Why\n\n" + "{lines}" + "\n## Commands\n\nNone.\n"
FENCE = "```"


def contract_text(name: str, parts=None) -> str:
    """A contract with a complete body: one query per part (default: one type named after the contract)."""
    out = [f"# {name}", "", f"Contract of `{name}`. Notation: wit.", "Sources: none", "",
           "## Use", "", "Call any part at any time.", "", "## Parts", ""]
    for part in (parts or [(name, "type")]):
        part, kind = part if isinstance(part, tuple) else (part, "query")
        out += [f"### {part}", "", f"Kind: {kind}", "", FENCE + "wit", f"{part}: func() -> u32;" if kind != "type"
                else f"record {part} {{ v: u32 }}", FENCE, ""]
        if kind == "event":
            out += ["When: the work is done.", "Delivery: at least once, in order per key.", ""]
        if kind in ("command", "query", "callback"):
            out += ["Pre: none.", "Result: a number.", "Errors: none.", "Examples:", "",
                    "| Case | Input | Expected |", "|---|---|---|", f"| one | `{part}()` | 1 |", ""]
    out += ["## Fake", "", "Replays the examples.", ""]
    return "\n".join(out)
SKILL = "---\nname: do-it\ndescription: Does it.\n---\n# Do it\n"
AGENTS_FIX = ("AGENTS.md is generated. Move its content into README.md (`## Why`) and "
              "docs/, delete the file, then run `unifold check --fix`.")


def project(root: str = "", units: dict | None = None, files: dict | None = None,
            contracts: dict | None = None) -> dict:
    """A project: a manifest and a README.md per unit. AGENTS.md is generated. A file
    whose value is None is left out. `ref:NAME` in a manifest becomes the path from the
    unit to docs/references/NAME.md of the root, which is written too, with the parts
    `contracts` gives it (default: one type named after it)."""
    names: set = set()

    def refs(text: str, folder: str) -> str:
        def path(match):
            names.add(match.group(1))
            return os.path.relpath(f"docs/references/{match.group(1)}.md", folder)
        return re.sub(r"\bref:([\w-]+)", path, text)

    out = {"unifold.yaml": ROOT + refs(root, "."), "README.md": README.format(name="demo")}
    for path, manifest in (units or {}).items():
        out[f"{path}/unifold.yaml"] = UNIT + refs(manifest, path)
        out[f"{path}/README.md"] = README.format(name=path.rsplit("/", 1)[-1])
    for name in sorted(names):
        out[f"docs/references/{name}.md"] = contract_text(name, (contracts or {}).get(name))
    out.update(files or {})
    return {k: v for k, v in out.items() if v is not None}


def with_decision(status="proposed", more="", date="2026-10-07", name="0001-x.md") -> dict:
    return {f"docs/decisions/{name}": DECISION.format(status=status, more=more, date=date)}


CONTEXT_FILES = {**with_decision(), CONTEXT: ITEM}
DERIVED = "---\nstatus: derived\ndate: 2026-10-07\nderived-from: proto §4\n---\n# A decision\n\n## Source says\n\nText.\n"
# a root capability `api` implemented by a, which needs x from b; the contracts have the parts serve and do
SCENARIO_ROOT = ("capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.x: b.x\n"
                 "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a -> b.do: ok\n    expect: e\n")
SCENARIO_UNITS = {"a": NEEDS_X + "capabilities:\n  api: {summary: s, contract: ref:api}\n", "b": CAPABILITY_X}
SCENARIO_CONTRACTS = {"api": ["serve"], "x": ["do"]}
CONSTANTS = "# Constants\n\n| Name | Value |\n|---|---|\n| `MAX_SIZE` | 3 |\n"
# the contract x with states: closed, then open; `open` may be refused, `send` may lose the line
STATE_ROWS = ["| closed | `open` | ok | open |", "| closed | `open` | `refused` | closed |",
              "| open | `send` | ok | open |", "| open | `send` | `lost` | closed |"]


def stateful_text(rows=None, start="closed", use=True) -> str:
    out = ["# x", "", "Contract of `x`. Notation: wit.", "Sources: none", ""]
    out += ["## Use", "", "Open, then send. When `send` fails with `lost`, open again.", ""] if use else []
    out += ["## States", ""] + ([f"Start: {start}.", ""] if start else [])
    out += ["| State | Part | Result | Next |", "|---|---|---|---|", *(STATE_ROWS if rows is None else rows), ""]
    out += ["## Parts", ""]
    for part, error in (("open", "refused"), ("send", "lost")):
        out += [f"### {part}", "", "Kind: command", "", FENCE + "wit", f"{part}: func();", FENCE, "", "Pre: none.",
                "Result: done.", f"Errors: `{error}` when it fails" + ("; `line gone` when the line is cut." if part == "send"
                                                                       else "."), "Examples:", "", "| Case | Input | Expected |",
                "|---|---|---|", f"| one | `{part}()` | ok |", ""]
    out += ["## Fake", "", "Follows the states.", ""]
    return "\n".join(out)


STATE_HOPS = ("      - api -> a.serve: ok\n      - a -> b.open(): ok\n      - a -> b.send([1]): lost\n"
              "      - a -> b.open(): ok\n      - a -> b.send([1]): ok\n")


def state_project(hops=STATE_HOPS, given="", **contract) -> dict:
    root = ("capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.x: b.x\n"
            "scenarios:\n  s1:\n    summary: s\n" + given + "    hops:\n" + hops + "    expect: e\n")
    return project(root, SCENARIO_UNITS, {"docs/references/x.md": stateful_text(**contract)}, contracts={"api": ["serve"]})


def type_project(*changes, parts=("do", ("thing", "type"))) -> dict:
    """Two wired units whose contract x has these parts; each change is (old text, new text) in the contract."""
    text = contract_text("x", list(parts))
    for old, new in changes:
        assert old in text, old
        text = text.replace(old, new)
    return project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {"docs/references/x.md": text})


TWO_TYPES = ("do", ("thing", "type"), ("other", "type"))
RETURNS_THING = ("do: func() -> u32;", "do: func() -> thing;")
UNUSED_TYPE = ["warn C10 docs/references/x.md"]
FOLDER_INDEX = "# x\n\nContract of x. Notation: wit.\n\n## Use\n\nAny order.\n\n## Parts\n\n- [do](do.md)\n- [thing](thing.md)\n\n## Fake\n\nReplays.\n"
FOLDER_DO = ("# do\n\nKind: query\n\n" + FENCE + "wit\n%s\n" + FENCE + "\n\nPre: none.\nResult: a number.\nErrors: none.\nExamples:\n\n"
             "| Case | Input | Expected |\n|---|---|---|\n| one | `do()` | 1 |\n")
FOLDER_THING = "# thing\n\nKind: type\n\n" + FENCE + "wit\nrecord thing { v: u32 }\n" + FENCE + "\n"


def folder_project(signature: str) -> dict:
    """Two wired units whose contract x is a folder with a query `do` and a type `thing`."""
    return project(WIRED, {"a": "needs:\n  x: {summary: s, contract: ../docs/references/x/index.md}\n",
                           "b": "capabilities:\n  x: {summary: s, contract: ../docs/references/x/index.md}\n"}, {
        "docs/references/x/index.md": FOLDER_INDEX, "docs/references/x/do.md": FOLDER_DO % signature,
        "docs/references/x/thing.md": FOLDER_THING})


# name, files, expected findings, options (fix, args)
CASES = [
    # ---------------------------------------------------------------- clean
    ("clean-single-unit", project(), []),
    ("clean-two-units-wired", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}), []),
    ("clean-shorthand-entries-unwired",
     project("", {"a": "needs:\n  x: {summary: Needs x, optional: true}\n"}), []),
    ("clean-unit-below-plain-folder", project(WIRED, {"parts/a": NEEDS_X, "parts/b": CAPABILITY_X}), []),
    ("clean-pass-up", project(NEEDS_X + "wiring:\n  a.x: x\n", {"a": NEEDS_X}), []),
    ("clean-pass-up-two-levels", project(NEEDS_X + "wiring:\n  a.x: x\n",
                                         {"a": "kind: stateful\n" + NEEDS_X + "wiring:\n  deep.x: x\n", "a/deep": NEEDS_X}), []),
    ("clean-pass-up-to-a-need-of-another-name",
     project("needs:\n  x: One\n  y: {summary: Two, contract: ref:x}\nwiring:\n  a.x: y\n", {"a": NEEDS_X}), []),
    ("clean-path-form-reference", project(
        'wiring:\n  "left/utils.x": right/utils.x\n',
        {"left/utils": NEEDS_X, "right/utils": CAPABILITY_X}), []),
    ("clean-folder-name-with-dots", project(
        "wiring:\n  my.pkg.x: other.lib.x\n", {"my.pkg": NEEDS_X, "other.lib": CAPABILITY_X}), []),
    ("clean-alternatives", project("wiring:\n  a.x: {real: b.x, fake: c.x}\n",
                                {"a": NEEDS_X, "b": CAPABILITY_X, "c": CAPABILITY_X}), []),
    ("clean-two-children-one-provider", project("wiring:\n  a.x: c.x\n  b.x: c.x\n",
                                             {"a": NEEDS_X, "b": NEEDS_X, "c": CAPABILITY_X}), []),
    ("clean-optional-need-unconnected",
     project("", {"a": "needs:\n  x: {summary: s, optional: true}\n"}), []),
    ("clean-capability-implemented-by-child", project(
        "capabilities:\n  p: {summary: s, contract: docs/references/p.md}\n"
        "needs:\n  n: {summary: s, contract: docs/references/n.md}\n"
        "wiring:\n  p: a.p\n  a.n: n\n",
        {"a": "capabilities:\n  p: {summary: s, contract: ../docs/references/p.md}\n"
              "needs:\n  n: {summary: s, contract: ../docs/references/n.md}\n"},
        {"docs/references/p.md": contract_text("p"), "docs/references/n.md": contract_text("n")}), []),
    ("clean-ignored-folder", project("ignore: [vendor]\n", files={
        "vendor/dep/unifold.yaml": "summary: [broken\n"}), []),
    ("clean-nested-project-is-not-checked", project("", files={
        "inner/unifold.yaml": 'unifold: "0.4"\nresponsibility: Inner\nwiring:\n  nobody.x: nothing.y\n'}), []),
    ("clean-units-below-folder-named-target", project(WIRED, {"target/a": NEEDS_X, "target/b": CAPABILITY_X}), []),
    ("clean-contract-in-ancestor", project("capabilities:\n  x: {summary: s, contract: ref:x}\n"
                                           "wiring:\n  x: a.x\n", {
        "a": "capabilities:\n  x:\n    summary: s\n    contract: ref:x\n"}), []),
    ("clean-contract-with-parts", project(WIRED, {
        "a": "needs:\n  x:\n    summary: s\n    contract:\n      path: ref:x\n      parts: [do, thing]\n", "b": CAPABILITY_X},
        contracts={"x": ["do", ("thing", "type")]}), []),
    ("clean-unit-fields", project("", {"a": "kind: logic\nnot:\n  - parsing\n  - sending\n" + NEEDS_X.replace("Needs x,", "Needs x, optional: true,")}), []),
    ("clean-empty-need-passed-up-inherits", project(NEEDS_X + "wiring:\n  a.x: x\n", {"a": "needs:\n  x:\n"}), []),
    ("clean-empty-capability-implemented-by-a-child-inherits", project("capabilities:\n  x:\nwiring:\n  x: b.x\n", {"b": CAPABILITY_X}), []),
    ("clean-empty-need-met-inside-inherits", project("needs:\n  x:\nwiring:\n  x: b.x\n", {"b": CAPABILITY_X}), []),
    ("clean-empty-entries-in-a-chain", project(NEEDS_X + "wiring:\n  a.x: x\n", {"a": "needs:\n  x:\nwiring:\n  deep.x: x\n", "a/deep": "needs:\n  x:\n"}), []),
    ("M2-empty-entry-without-a-wiring-line", project("", {"a": "needs:\n  x:\n"}), ["error M2 a/unifold.yaml", "error W2 unifold.yaml"]),
    ("M2-empty-entry-with-alternatives", project(NEEDS_X + "wiring:\n  a.x: {real: b.x, fake: c.x}\n",
                                                 {"a": "needs:\n  x:\n", "b": CAPABILITY_X, "c": CAPABILITY_X}),
     ["error M2 a/unifold.yaml", "error W11 unifold.yaml"]),
    ("clean-platform-need-of-the-root", project("needs:\n  clock: {summary: s, contract: ref:clock, platform: true}\n"
                                                "wiring:\n  a.clock: clock\n",
                                                {"a": "needs:\n  clock: {summary: s, contract: ref:clock}\n"}), []),
    ("clean-kinds-throughout", project("needs:\n  port: {summary: s, contract: ref:port}\nwiring:\n  s.calc: l.calc\n  s.port: ad.port\n  ad.port: port\n", {
        "s": "kind: stateful\nneeds:\n  calc: {summary: s, contract: ref:calc}\n  port: {summary: s, contract: ref:port}\n",
        "l": "kind: logic\ncapabilities:\n  calc: {summary: s, contract: ref:calc}\n",
        "ad": "kind: adapter\ncapabilities:\n  port: {summary: s, contract: ref:port}\nneeds:\n  port: {summary: s, contract: ref:port}\n"}), []),
    ("clean-scenario", project(SCENARIO_ROOT, SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS), []),
    ("clean-scenario-across-levels", project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.x: b.x\n"
        "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a/inner -> b.do: ok\n      - a -> b.do: ok\n    expect: e\n",
        {"a": "kind: stateful\n" + NEEDS_X + "capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  inner.x: x\n",
         "a/inner": NEEDS_X, "b": CAPABILITY_X}, contracts=SCENARIO_CONTRACTS), []),
    ("clean-scenario-in-a-leaf", project("", {"a": NEEDS_X.replace("Needs x,", "Needs x, optional: true,")
                                                  + "capabilities:\n  api: {summary: s, contract: ref:api}\n"
                                                  "scenarios:\n  s1:\n    summary: s\n    hops: ['api -> x.do': ok]\n    expect: e\n"},
                                         contracts=SCENARIO_CONTRACTS), ["info N4 docs/references/api.md", "warn W3 unifold.yaml"]),
    ("clean-derived-decision", project("", {"a": ""}, {**{"docs/decisions/0001-x.md": DERIVED},
                                                     CONTEXT: ITEM}), []),
    ("clean-constants", project(files={"docs/references/constants.md": CONSTANTS,
                                       "README.md": "# demo\n\nAt most `MAX_SIZE` things; `CRC32` and `GET` are no names.\n\n## Why\n\nBecause.\n"}), []),
    ("clean-contract-folder", project(WIRED, {"a": "needs:\n  x: {summary: s, contract: ../docs/references/x/index.md}\n",
                                              "b": "capabilities:\n  x: {summary: s, contract: ../docs/references/x/index.md}\n"}, {
        "docs/references/x/index.md": "# x\n\nContract of x. Notation: wit.\n\n## Use\n\nAny order.\n\n## Parts\n\n- [do](do.md)\n\n## Fake\n\nReplays.\n",
        "docs/references/x/do.md": "# do\n\nKind: query\n\n```wit\ndo: func() -> u32;\n```\n\nPre: none.\nResult: r.\nErrors: none.\nExamples:\n\n| Case | Input | Expected |\n|---|---|---|\n| one | `do()` | 1 |\n"}), []),
    ("M2-contract-with-a-fragment", project(WIRED, {
        "a": "needs:\n  x: {summary: s, contract: ../docs/references/x.md#part}\n",
        "b": "capabilities:\n  x: {summary: s, contract: ../docs/references/x.md}\n"},
        {"docs/references/x.md": contract_text("x")}), ["error M2 a/unifold.yaml"]),
    ("clean-extension-keys", project("x-team: red\n", {"a": "x-anything: {a: 1}\n"}), []),
    ("clean-diagrams-none", project("diagrams: none\n" + WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}), []),
    ("clean-with-documents", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "README.md": "# demo\n\n[a](a/README.md) and [b](b/)\n\n## Why\n\nBecause.\n",
        "a/README.md": "# a\n\nWhat a is for.\n\n## Needs\n\n### `x`\n\nText. See [the map](docs/explanation/context.md).\n\n## Why\n\nBecause.\n",
        CONTEXT: "# Context of a\n\n### [demo](../../../README.md)\n\nx, so y.\n"}), []),
    ("clean-composite-without-kind", project("", {"a": "", "a/deep": ""}), []),
    ("clean-all-document-kinds", project(files={
        "docs/tutorials/first.md": "# First\n", "docs/references/api/index.md": "# API\n",
        "docs/explanation/risks.md": "# Risks\n", "docs/skills/do-it/SKILL.md": SKILL,
        **with_decision()}), []),
    ("clean-own-need-wired-to-a-child", project(NEEDS_X + "wiring:\n  x: b.x\n", {"b": CAPABILITY_X}), []),
    ("clean-need-met-inside-is-not-wired-above",
     project("", {"a": "kind: stateful\n" + NEEDS_X + "wiring:\n  x: inner.x\n", "a/inner": CAPABILITY_X}), []),
    # ------------------------------------------------------------ S: structure
    ("S1-unsupported-version", {"unifold.yaml": 'unifold: "9.9"\nresponsibility: A demo\n'},
     ["error S1 unifold.yaml"]),
    ("S1-version-0-2-is-not-read", {"unifold.yaml": 'unifold: "0.2"\nsummary: A demo\n'},
     ["error S1 unifold.yaml"]),
    ("S1-version-is-not-a-string", {"unifold.yaml": "unifold: 0.10\nresponsibility: A demo\n"},
     ["error S1 unifold.yaml"]),
    ("S3-root-without-readme", project(files={"README.md": None}), ["error S3 ."]),
    ("S3-child-without-readme", project("", {"a": ""}, {"a/README.md": None}), ["error S3 a"]),
    ("S7-skill-needs-no-link-from-agents-file", project(files={"docs/skills/do-it/SKILL.md": SKILL}), []),
    ("S7-skill-name-differs", project(files={
        "docs/skills/do-it/SKILL.md": "---\nname: other\ndescription: Does it.\n---\n# Do it\n"}),
     ["warn S7 docs/skills/do-it/SKILL.md"]),
    ("S7-skill-without-description", project(files={
        "docs/skills/do-it/SKILL.md": "---\nname: do-it\n---\n# Do it\n"}),
     ["warn S7 docs/skills/do-it/SKILL.md"]),
    ("S9-accepted-without-decision-makers", project(files=with_decision("accepted")),
     ["error S9 docs/decisions/0001-x.md"]),
    ("S9-accepted-with-decision-makers",
     project(files=with_decision("accepted", "decision-makers: [Ada]\n")), []),
    ("S9-status-typo", project(files=with_decision("proposedd")), ["error S9 docs/decisions/0001-x.md"]),
    ("S9-superseded-by-missing-decision", project(files=with_decision("superseded by 0099")),
     ["error S9 docs/decisions/0001-x.md"]),
    ("S9-date-is-not-a-date", project(files=with_decision(date="next sprint")),
     ["error S9 docs/decisions/0001-x.md"]),
    ("S9-duplicate-number", project(files={**with_decision(), **with_decision(name="0001-y.md")}),
     ["error S9 docs/decisions/0001-y.md"]),
    ("S9-file-name", project(files=with_decision(name="first-choice.md")),
     ["error S9 docs/decisions/first-choice.md"]),
    ("S9-derived-without-derived-from", project(files={"docs/decisions/0001-x.md": DERIVED.replace("derived-from: proto §4\n", "")}),
     ["error S9 docs/decisions/0001-x.md"]),
    ("S9-derived-without-source-says", project(files={"docs/decisions/0001-x.md": DERIVED.replace("## Source says", "## Context")}),
     ["error S9 docs/decisions/0001-x.md"]),
    ("S12-entries-of-another-kind-in-docs", project(files={
        "docs/notes.md": "# Notes\n", "docs/site/index.html": "<p>x</p>\n", "docs/.hidden": "x\n"}),
     ["info S12 docs/notes.md", "info S12 docs/site"]),
    ("S12-old-layout-context-and-architecture", project(files={
        "docs/context.md": "# Context\n", "docs/architecture.md": "# Architecture\n"}),
     ["info S12 docs/architecture.md", "info S12 docs/context.md"]),
    # ------------------------------------------------------------- M: manifest
    ("M1-invalid-yaml-in-child-reports-once", project(WIRED, {"a": NEEDS_X, "b": "capabilities: [x\n"}),
     ["error M1 b/unifold.yaml"]),
    ("M1-duplicate-key", project("", {"a": "responsibility: again\n"}), ["error M1 a/unifold.yaml"]),
    ("M1-key-is-a-list", project("", {"a": "[a, b]: c\n"}), ["error M1 a/unifold.yaml"]),
    ("M1-broken-root-manifest", {"unifold.yaml": ROOT + "responsibility: twice\n"}, ["error M1 unifold.yaml"]),
    ("M1-children-of-broken-unit-keep-their-parent", project(
        "", {"a": "wiring: [\n", "a/deep": NEEDS_X}), ["error M1 a/unifold.yaml"]),
    ("M2-summary-on-a-unit", project("", {"a": ""}, {"a/unifold.yaml": "summary: A part\n"}),
     ["error M2 a/unifold.yaml", "error M2 a/unifold.yaml"]),
    ("M2-verified-by-removed", project("capabilities:\n  x: {summary: s, contract: ref:x, verified-by: tests}\n"),
     ["error M2 unifold.yaml"]),
    ("M2-owner-is-no-key", project("owner: the team\n"), ["error M2 unifold.yaml"]),
    ("M2-diagram-links-is-no-key", project("diagram-links: relative\n"), ["error M2 unifold.yaml"]),
    ("M2-diagrams-all", project("diagrams: all\n"), ["error M2 unifold.yaml"]),
    ("M2-kind-on-a-capability", project("capabilities:\n  x: {summary: s, kind: http}\n"), ["error M2 unifold.yaml"]),
    ("M2-platform-on-a-need-of-a-child", project("", {"a": "needs:\n  clock: {summary: s, optional: true, platform: true}\n"}),
     ["error M2 a/unifold.yaml"]),
    ("M2-platform-on-a-capability", project("capabilities:\n  x: {summary: s, platform: true}\n"), ["error M2 unifold.yaml"]),
    ("M2-contract-mapping-with-unknown-key", project("capabilities:\n  x:\n    summary: s\n    contract:\n      path: ref:x\n      verified: yes\n"),
     ["error M2 unifold.yaml"]),
    ("M2-contract-mapping-without-path", project("capabilities:\n  x:\n    summary: s\n    contract:\n      parts: [a]\n"),
     ["error M2 unifold.yaml"]),
    ("M2-scenario-name-with-dot", project("scenarios:\n  v1.open:\n    summary: s\n    hops: ['x -> y.z': ok]\n    expect: e\n"),
     ["error M2 unifold.yaml", "error N1 unifold.yaml"]),
    ("M11-part-not-in-contract", project(WIRED, {
        "a": "needs:\n  x:\n    summary: s\n    contract:\n      path: ref:x\n      parts: [do, gone]\n", "b": CAPABILITY_X},
        contracts={"x": ["do"]}), ["error M11 a/unifold.yaml"]),
    ("M2-unknown-key", project("colour: blue\n"), ["error M2 unifold.yaml"]),
    ("M2-old-key-unit", project("", {"a": "unit: a\n"}), ["error M2 a/unifold.yaml"]),
    ("M2-no-responsibility", {"unifold.yaml": 'unifold: "0.4"\n', "README.md": README}, ["error M2 unifold.yaml"]),
    ("M2-placeholder-responsibility", {"unifold.yaml": 'unifold: "0.4"\nresponsibility: <what the project is, in one line>\n',
                                       "README.md": README}, ["error M2 unifold.yaml"]),
    ("M2-responsibility-over-two-lines", {"unifold.yaml": 'unifold: "0.4"\nresponsibility: |\n  one\n  two\n',
                                          "README.md": README}, ["error M2 unifold.yaml"]),
    ("M2-root-key-in-child", project("", {"a": "ignore: [x]\n"}), ["error M2 a/unifold.yaml"]),
    ("M2-status-as-boolean", project("status: yes\n"), ["error M2 unifold.yaml"]),
    ("M2-level-is-no-key", project("level: full\n"), ["error M2 unifold.yaml"]),
    ("M2-ignore-as-text", project("ignore: vendor\n"), ["error M2 unifold.yaml"]),
    ("M2-ignore-names-a-missing-folder", project("ignore: [nope]\n"), ["error M2 unifold.yaml"]),
    ("M2-ignore-names-an-absolute-path", project("ignore: [/tmp]\n"), ["error M2 unifold.yaml"]),
    ("M2-placeholder-in-kind", project("kind: <kind>\n"), ["error M2 unifold.yaml", "info K1 unifold.yaml"]),
    ("M2-placeholder-in-not", project("not:\n  - <nothing>\n"), ["error M2 unifold.yaml"]),
    ("M2-placeholder-in-expect", project(SCENARIO_ROOT.replace("expect: e", "expect: <expect>"), SCENARIO_UNITS,
                                         contracts=SCENARIO_CONTRACTS), ["error M2 unifold.yaml"]),
    ("M2-max-lines", project("max-lines: none\n"), ["error M2 unifold.yaml"]),
    ("M2-capability-name-with-dot", project("capabilities:\n  v1.api: s\n"), ["error M2 unifold.yaml"]),
    ("M2-capability-name-starts-with-underscore", project("capabilities:\n  _api: s\n"), ["error M2 unifold.yaml"]),
    ("M2-placeholder-summary-of-a-need", project("needs:\n  x: <what is needed>\n"),
     ["error M2 unifold.yaml"]),
    ("M2-capabilities-as-list", project("capabilities: [x]\n"), ["error M2 unifold.yaml"]),
    ("M2-capability-without-summary", project("capabilities:\n  x: {x-note: n}\n"), ["error M2 unifold.yaml"]),
    ("M2-optional-is-not-a-boolean",
     project("", {"a": 'needs:\n  x: {summary: s, optional: "yes"}\n'}),
     ["error M2 a/unifold.yaml", "error W2 unifold.yaml"]),
    ("M2-optional-on-a-capability", project("capabilities:\n  x: {summary: s, optional: true}\n"),
     ["error M2 unifold.yaml"]),
    ("M2-conforms-to-is-not-a-key", project("capabilities:\n  x: {summary: s, conforms-to: spec}\n"),
     ["error M2 unifold.yaml"]),
    ("M2-comma-in-flow-summary", project("capabilities:\n  x: {summary: one, two words}\n"),
     ["error M2 unifold.yaml"]),
    ("M2-alternatives-as-list", project("wiring:\n  a.x: [b.x, c.x]\n",
                                     {"a": NEEDS_X, "b": CAPABILITY_X, "c": CAPABILITY_X}),
     ["error M2 unifold.yaml", "error W2 unifold.yaml", "warn W3 unifold.yaml", "warn W3 unifold.yaml"]),
    ("M2-contract-as-list", project("capabilities:\n  x: {summary: s, contract: [a.md, b.md]}\n"),
     ["error M2 unifold.yaml"]),
    ("M7-contract-missing", project("capabilities:\n  x: {summary: s, contract: docs/api.md}\n"),
     ["error M7 unifold.yaml"]),
    ("M7-contract-outside-project", project("capabilities:\n  x: {summary: s, contract: ../elsewhere.md}\n"),
     ["error M7 unifold.yaml"]),
    ("M7-contract-url", project("capabilities:\n  x: {summary: s, contract: https://example.org/api}\n"),
     ["error M7 unifold.yaml"]),
    ("M7-contract-in-unit-below", project("capabilities:\n  x: {summary: s, contract: a/docs/references/x.md}\n"
                                          "wiring:\n  x: a.x\n",
        {"a": "capabilities:\n  x: {summary: s, contract: docs/references/x.md}\n"},
        {"a/docs/references/x.md": contract_text("x")}),
     ["error M7 unifold.yaml"]),
    ("M7-contract-not-a-reference", project("capabilities:\n  x: {summary: s, contract: openapi.yaml}\n",
                                            files={"openapi.yaml": "openapi: 3.1.0\n"}),
     ["error M7 unifold.yaml"]),
    ("M7-contract-in-sibling-unit", project(WIRED, {
        "a": "needs:\n  x: {summary: s, contract: ../b/docs/references/x.md}\n",
        "b": "capabilities:\n  x: {summary: s, contract: docs/references/x.md}\n"},
        {"b/docs/references/x.md": contract_text("x")}),
     ["error M7 a/unifold.yaml"]),
    ("M10-responsibility-todo", project("", {"a": ""}, {"a/unifold.yaml": "responsibility: TODO\nneeds:\n  x: {summary: TODO, optional: true}\n"}),
     ["warn M10 a/unifold.yaml"]),
    # --------------------------------------------------------------- W: wiring
    ("W1-unknown-capability", project("wiring:\n  a.x: b.y\n", {"a": NEEDS_X, "b": CAPABILITY_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml", "warn W3 unifold.yaml"]),
    ("W1-unknown-child", project("wiring:\n  a.x: nobody.x\n", {"a": NEEDS_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml"]),
    ("W1-wrong-direction", project("wiring:\n  b.x: a.x\n", {"a": NEEDS_X, "b": CAPABILITY_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml", "warn W3 unifold.yaml"]),
    ("W1-reference-to-grandchild", project(
        "wiring:\n  a.x: deep.x\n", {"a": NEEDS_X, "b": "kind: stateful\n", "b/deep": CAPABILITY_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml", "warn W3 b/unifold.yaml"]),
    ("W1-capability-wired-to-own-need", project("capabilities:\n  p: s\nneeds:\n  n: s\nwiring:\n  p: n\n"),
     ["error W1 unifold.yaml"]),
    ("W1-ambiguous-folder-name", project(
        "wiring:\n  utils.x: other.x\n", {"left/utils": NEEDS_X, "right/utils": "", "other": CAPABILITY_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml", "warn W3 unifold.yaml"]),
    ("W1-star-key-not-allowed", project('wiring:\n  "*.x": c.x\n',
                                     {"a": NEEDS_X, "b": NEEDS_X, "c": CAPABILITY_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml", "error W2 unifold.yaml",
      "warn W3 unifold.yaml"]),
    ("W1-star-value-not-allowed", project("wiring:\n  a.x: '*'\n", {"a": NEEDS_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml"]),
    ("W1-unit-provides-for-its-own-need", project(
        "wiring:\n  a.x: a.x\n", {"a": NEEDS_X + CAPABILITY_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml", "warn W3 unifold.yaml"]),
    ("W1-folder-provider", project("wiring:\n  a.x: ./legacy\n", {"a": NEEDS_X}, {"legacy/code.txt": "x\n"}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml"]),
    ("W1-own-code-provider", project("wiring:\n  a.x: ./\n", {"a": NEEDS_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml"]),
    ("W1-own-code-written-as-a-dot", project("wiring:\n  a.x: .\n", {"a": NEEDS_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml"]),
    ("W1-capability-implemented-by-own-code", project("capabilities:\n  p: s\nwiring:\n  p: ./\n"),
     ["error W1 unifold.yaml"]),
    ("W1-key-names-a-capability-and-a-need", project(
        "capabilities:\n  x: {summary: s, contract: ref:x}\n" + NEEDS_X + "wiring:\n  x: b.x\n",
        {"b": CAPABILITY_X}), ["error W1 unifold.yaml", "warn W3 unifold.yaml"]),
    ("W1-own-need-wired-to-own-need", project("needs:\n  x: s\n  y: s\nwiring:\n  x: y\n"),
     ["error W1 unifold.yaml"]),
    ("W1-child-need-passed-up-to-a-need-met-inside", project(
        NEEDS_X + "wiring:\n  x: b.x\n  a.x: x\n", {"a": NEEDS_X, "b": CAPABILITY_X}),
     ["error W1 unifold.yaml", "error W2 unifold.yaml"]),
    ("W1-parent-wires-a-need-its-child-meets-inside", project(
        "wiring:\n  a.x: b.x\n", {"a": "kind: stateful\n" + NEEDS_X + "wiring:\n  x: inner.x\n", "a/inner": CAPABILITY_X,
                                  "b": CAPABILITY_X}),
     ["error W1 unifold.yaml", "warn W3 unifold.yaml"]),
    ("W2-need-without-provider", project("", {"a": NEEDS_X, "b": CAPABILITY_X}),
     ["error W2 unifold.yaml", "warn W3 unifold.yaml"]),
    ("W2-no-pass-up-without-need-of-the-same-name",
     project("needs:\n  other: s\n", {"a": NEEDS_X}), ["error W2 unifold.yaml"]),
    ("W3-capability-not-used", project("", {"b": CAPABILITY_X}), ["warn W3 unifold.yaml"]),
    ("W2-a-need-of-the-same-name-in-the-parent-is-no-connection", project(NEEDS_X, {"a": NEEDS_X}),
     ["error W2 unifold.yaml"]),
    ("W7-cycle", project("wiring:\n  a.x: b.x\n  b.y: a.y\n", {
        "a": NEEDS_X + "capabilities:\n  y: {summary: s, contract: ref:x}\n",
        "b": CAPABILITY_X + "needs:\n  y: {summary: s, contract: ref:x}\n"}),
     ["warn W7 unifold.yaml"]),
    ("W11-need-without-contract", project(WIRED, {"a": "needs:\n  x: Needs x\n", "b": CAPABILITY_X}),
     ["error W11 unifold.yaml"]),
    ("W11-capability-without-contract", project(WIRED, {"a": NEEDS_X, "b": "capabilities:\n  x: Offers x\n"}),
     ["error W11 unifold.yaml"]),
    ("W11-contracts-differ", project(WIRED, {
        "a": "needs:\n  x: {summary: s, contract: ref:a}\n", "b": CAPABILITY_X}),
     ["error W11 unifold.yaml"]),
    ("W11-implemented-by-differs", project(
        "capabilities:\n  x: {summary: s, contract: ref:root}\nwiring:\n  x: b.x\n",
        {"b": CAPABILITY_X}), ["error W11 unifold.yaml"]),
    ("W11-own-need-without-contract", project("needs:\n  x: Needs x\nwiring:\n  x: b.x\n", {"b": CAPABILITY_X}),
     ["error W11 unifold.yaml"]),
    ("W11-own-need-provider-without-contract", project(NEEDS_X + "wiring:\n  x: b.x\n",
                                                       {"b": "capabilities:\n  x: Offers x\n"}),
     ["error W11 unifold.yaml"]),
    ("W11-pass-up-differs", project("needs:\n  x: {summary: s, contract: ref:root}\n"
                                    "wiring:\n  a.x: x\n", {"a": NEEDS_X}), ["error W11 unifold.yaml"]),
    ("W11-pass-up-without-contract", project("needs:\n  x: From outside\nwiring:\n  a.x: x\n", {"a": NEEDS_X}),
     ["error W11 unifold.yaml"]),
    ("W11-reported-once-per-side", project("wiring:\n  a.x: c.x\n  b.x: c.x\n",
                                        {"a": NEEDS_X, "b": NEEDS_X, "c": "capabilities:\n  x: Offers x\n"}),
     ["error W11 unifold.yaml"]),
    ("W9-active-unit-needs-planned-provider", project(
        WIRED, {"a": NEEDS_X, "b": CAPABILITY_X + "status: planned\n"}), ["warn W9 unifold.yaml"]),
    ("W9-active-unit-needs-deprecated-provider", project(
        WIRED, {"a": NEEDS_X, "b": CAPABILITY_X + "status: deprecated\n"}), ["warn W9 unifold.yaml"]),
    ("W9-own-need-from-a-planned-child", project(NEEDS_X + "wiring:\n  x: b.x\n",
                                                 {"b": "status: planned\n" + CAPABILITY_X}),
     ["warn W9 unifold.yaml"]),
    ("W9-not-for-optional-needs", project(WIRED, {
        "a": "needs:\n  x: {summary: s, optional: true, contract: ref:x}\n", "b": CAPABILITY_X + "status: planned\n"}), []),
    # ------------------------------------------------ K: kinds and unit fields
    ("K1-kind-not-well-known", project("", {"a": "kind: library\n"}), ["info K1 a/unifold.yaml"]),
    ("K2-logic-unit-with-a-stateful-child", project("", {"a": "kind: logic\n", "a/deep": "kind: stateful\n"}),
     ["warn K2 a/unifold.yaml"]),
    ("K2-logic-unit-needs-a-stateful-provider", project(WIRED, {"a": "kind: logic\n" + NEEDS_X, "b": "kind: stateful\n" + CAPABILITY_X}),
     ["warn K2 a/unifold.yaml"]),
    ("K2-logic-unit-reaches-a-need-of-the-root", project(NEEDS_X + "wiring:\n  a.x: x\n", {"a": "kind: logic\n" + NEEDS_X}),
     ["warn K2 a/unifold.yaml", "warn K4 unifold.yaml"]),
    ("K3-adapter-needs-an-adapter", project(WIRED, {"a": "kind: adapter\n" + NEEDS_X, "b": "kind: adapter\n" + CAPABILITY_X}),
     ["warn K3 a/unifold.yaml"]),
    ("K4-root-need-reached-by-a-stateful-unit", project(NEEDS_X + "wiring:\n  a.x: x\n", {"a": "kind: stateful\n" + NEEDS_X}),
     ["warn K4 unifold.yaml"]),
    ("K4-silent-for-another-kind", project(NEEDS_X + "wiring:\n  a.x: x\n", {"a": "kind: service\n" + NEEDS_X}),
     ["info K1 a/unifold.yaml"]),
    ("M2-secret-is-gone", project("", {"a": "secret:\n  what: w\n"}), ["error M2 a/unifold.yaml"]),
    ("K6-not-item-mapped-to-a-need", project("", {"a": "not:\n  - parsing: codec\n"}), ["error K6 a/unifold.yaml"]),
    ("K6-not-as-text", project("", {"a": "not: parsing\n"}), ["error K6 a/unifold.yaml"]),
    # ------------------------------------------------ N: scenarios
    ("N1-hop-without-a-connection", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - b -> a.do: ok\n"), SCENARIO_UNITS,
                                            contracts=SCENARIO_CONTRACTS), ["error N1 unifold.yaml"]),
    ("N1-part-not-in-the-contract", project(SCENARIO_ROOT.replace("b.do", "b.undo"), SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS),
     ["error N1 unifold.yaml"]),
    ("N1-unknown-name", project(SCENARIO_ROOT.replace("a -> b.do", "a -> nobody.do"), SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS),
     ["error N1 unifold.yaml"]),
    ("N1-name-is-a-unit-and-a-capability", project(SCENARIO_ROOT.replace("api: a.api", "api: api.api").replace("a.x: b.x", "api.x: b.x"),
                                                   {"api": SCENARIO_UNITS["a"], "b": CAPABILITY_X}, contracts=SCENARIO_CONTRACTS),
     ["error N1 unifold.yaml", "error N1 unifold.yaml"]),
    ("N1-hop-not-in-the-form", project(SCENARIO_ROOT.replace("- a -> b.do", "- a calls b"), SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS),
     ["error N1 unifold.yaml"]),
    ("N1-two-connections-with-the-part", project(
        "wiring:\n  a.x: b.x\n  a.y: b.y\nscenarios:\n  s1:\n    summary: s\n    hops: ['a -> b.do': ok]\n    expect: e\n",
        {"a": NEEDS_X + "  y: {summary: s, contract: ref:y}\n", "b": CAPABILITY_X + "  y: {summary: s, contract: ref:y}\n"},
        contracts={"x": ["do"], "y": ["do"]}), ["error N1 unifold.yaml"]),
    ("N2-scenario-without-expect", project(SCENARIO_ROOT.replace("    expect: e\n", ""), SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS),
     ["error N2 unifold.yaml"]),
    ("N2-scenario-as-text", project("scenarios:\n  s1: a story\n"), ["error N2 unifold.yaml"]),
    ("N3-wiring-line-without-a-hop", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", ""), SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS),
     ["info N4 docs/references/x.md", "warn N3 unifold.yaml"]),
    ("clean-child-scenario-uses-the-lines-of-the-parent",
     project(SCENARIO_ROOT[:SCENARIO_ROOT.index("scenarios:")],
             {**SCENARIO_UNITS, "a": SCENARIO_UNITS["a"] + "scenarios:\n  s:\n    summary: s\n    hops:\n      - api -> x.do: ok\n    expect: e\n"},
             contracts=SCENARIO_CONTRACTS),
     ["info N4 docs/references/api.md"]),
    ("N4-part-without-a-hop", project(SCENARIO_ROOT, SCENARIO_UNITS, contracts={"api": ["serve"], "x": ["do", "undo", ("thing", "type")]}),
     ["info N4 docs/references/x.md", "warn C10 docs/references/x.md"]),
    ("N4-silent-without-a-scenario", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, contracts={"x": ["do", "undo"]}), []),
    ("clean-path-through-states", state_project(), []),
    ("clean-given-sets-the-state", state_project("      - api -> a.serve: ok\n      - a -> b.send([1]): lost\n"
                                                 "      - a -> b.open(): ok\n",
                                                 "    given:\n      - b.x: open\n      - the line is quiet\n"), []),
    ("N2-hop-without-a-result", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.do"), SCENARIO_UNITS,
                                        contracts=SCENARIO_CONTRACTS), ["error N2 unifold.yaml"]),
    ("N2-result-read-as-true", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.do: yes"), SCENARIO_UNITS,
                                       contracts=SCENARIO_CONTRACTS), ["error N2 unifold.yaml"]),
    ("N5-given-names-no-state", state_project(given="    given:\n      - b.x: nowhere\n"), ["error N5 unifold.yaml"]),
    ("N5-given-names-a-contract-without-states", project(SCENARIO_ROOT.replace("    hops:", "    given:\n      - b.x: open\n    hops:"),
                                                         SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS), ["error N5 unifold.yaml"]),
    ("C2-examples-table-with-other-columns", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/references/x.md": contract_text("x", ["do"]).replace("| Case | Input | Expected |", "| Case | Request | Answer |")}),
     ["warn C2 docs/references/x.md"]),
    ("C2-two-rows-with-one-case", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/references/x.md": contract_text("x", ["do"]).replace("| one | `do()` | 1 |", "| one | `do()` | 1 |\n| one | `do(2)` | 2 |")}),
     ["warn C2 docs/references/x.md"]),
    ("clean-examples-with-given", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/references/x.md": contract_text("x", ["do"]).replace("| Case | Input | Expected |\n|---|---|---|\n| one | `do()` | 1 |",
                                                                  "| Case | Given | Input | Expected |\n|---|---|---|---|\n| one | nothing | `do()` | 1 |")}), []),
    ("N1-event-in-the-direction-of-the-dependency", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.done: ok"), SCENARIO_UNITS,
                                                          contracts={"api": ["serve"], "x": ["do", ("done", "event")]}), ["error N1 unifold.yaml"]),
    ("clean-event-raised-by-the-provider", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - a -> b.do: ok\n      - b -> a.done: ok\n"), SCENARIO_UNITS,
                                                   contracts={"api": ["serve"], "x": ["do", ("done", "event")]}), []),
    ("clean-event-without-a-result", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - a -> b.do: ok\n      - b -> a.done\n"), SCENARIO_UNITS,
                                             contracts={"api": ["serve"], "x": ["do", ("done", "event")]}), []),
    ("clean-callback-called-by-the-provider", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - a -> b.do: ok\n      - b -> a.notify(1): ok\n"), SCENARIO_UNITS,
                                                      contracts={"api": ["serve"], "x": ["do", ("notify", "callback")]}), []),
    ("N1-callback-called-by-the-consumer", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.notify(1): ok"), SCENARIO_UNITS,
                                                   contracts={"api": ["serve"], "x": ["do", ("notify", "callback")]}), ["error N1 unifold.yaml"]),
    ("N2-command-without-a-result", project(SCENARIO_ROOT.replace("      - a -> b.do: ok", "      - a -> b.do"), SCENARIO_UNITS,
                                            contracts=SCENARIO_CONTRACTS), ["error N2 unifold.yaml"]),
    ("clean-parallel-hops", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - parallel:\n          - - a -> b.do: ok\n          - - a -> b.ask: ok\n"),
                                    SCENARIO_UNITS, contracts={"api": ["serve"], "x": ["do", "ask"]}), []),
    ("N2-parallel-with-one-branch", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - parallel:\n          - - a -> b.do: ok\n"),
                                            SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS),
     ["error N2 unifold.yaml", "info N4 docs/references/x.md", "warn N3 unifold.yaml"]),
    ("clean-repeated-hops", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - repeat:\n          until: done\n          hops:\n            - a -> b.do: ok\n"),
                                    SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS), []),
    ("N2-repeat-without-until-or-times", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - repeat:\n          hops:\n            - a -> b.do: ok\n"),
                                                 SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS),
     ["error N2 unifold.yaml", "info N4 docs/references/x.md", "warn N3 unifold.yaml"]),
    ("clean-included-scenario", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - a.inner\n"),
                                        {"a": SCENARIO_UNITS["a"] + "scenarios:\n  inner:\n    summary: s\n    hops:\n      - api -> x.do: ok\n    expect: e\n",
                                         "b": SCENARIO_UNITS["b"]}, contracts=SCENARIO_CONTRACTS), []),
    ("clean-included-scenario-names-its-caller", project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nneeds:\n  y: {summary: s, contract: ref:y}\nwiring:\n  api: a.api\n  a.x: b.x\n  c.x: b.x\n  b.y: y\n"
        "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a -> b.do: ok\n      - a -> b.inner\n      - c -> b.do: ok\n    expect: e\n",
        {"a": SCENARIO_UNITS["a"], "c": NEEDS_X,
         "b": SCENARIO_UNITS["b"] + "needs:\n  y: {summary: s, contract: ref:y}\nscenarios:\n  inner:\n    summary: s\n    hops:\n      - x -> y.go: ok\n    expect: e\n"},
        contracts={**SCENARIO_CONTRACTS, "y": ["go"]}), []),
    ("clean-include-two-levels-deep-through-a-passed-up-need", project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nneeds:\n  out: {summary: s, contract: ref:out}\n"
        "wiring:\n  api: a.api\n  a.out: out\nscenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a.mid\n    expect: e\n",
        {"a": "capabilities:\n  api: {summary: s, contract: ref:api}\nneeds:\n  out: {summary: s, contract: ref:out}\n"
              "wiring:\n  api: deep.api\n  deep.out: out\nscenarios:\n  mid:\n    summary: s\n    hops:\n      - api -> deep.serve: ok\n      - deep.inner\n    expect: e\n",
         "a/deep": "capabilities:\n  api: {summary: s, contract: ref:api}\nneeds:\n  out: {summary: s, contract: ref:out}\n"
                   "scenarios:\n  inner:\n    summary: s\n    hops:\n      - api -> out.go: ok\n    expect: e\n"},
        contracts={"api": ["serve"], "out": ["go"]}), []),
    ("N1-included-scenario-with-an-unknown-caller", project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nneeds:\n  y: {summary: s, contract: ref:y}\nwiring:\n  api: a.api\n  a.x: b.x\n  c.x: b.x\n  b.y: y\n"
        "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - z -> b.inner\n      - a -> b.do: ok\n      - c -> b.do: ok\n    expect: e\n",
        {"a": SCENARIO_UNITS["a"], "c": NEEDS_X,
         "b": SCENARIO_UNITS["b"] + "needs:\n  y: {summary: s, contract: ref:y}\nscenarios:\n  inner:\n    summary: s\n    hops:\n      - x -> y.go: ok\n    expect: e\n"},
        contracts={**SCENARIO_CONTRACTS, "y": ["go"]}), ["error N1 unifold.yaml"]),
    ("N1-included-scenario-missing", project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", "      - a.nope\n"), SCENARIO_UNITS,
                                             contracts=SCENARIO_CONTRACTS), ["error N1 unifold.yaml"]),
    ("C8-qualities-table-with-other-columns", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/references/x.md": contract_text("x", ["do"]).replace("## Fake", "## Qualities\n\n| What | How |\n|---|---|\n| latency | 1 ms |\n\n## Fake")}),
     ["warn C8 docs/references/x.md"]),
    ("clean-qualities-table", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/references/x.md": contract_text("x", ["do"]).replace("## Fake", "## Qualities\n\n| Aspect | Guarantee |\n|---|---|\n| latency | 1 ms |\n\n## Fake")}), []),
    ("C9-event-without-when-and-delivery", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/references/x.md": contract_text("x", ["do", ("done", "event")]).replace("When: the work is done.\n", "")}),
     ["warn C9 docs/references/x.md"]),
    ("clean-event-with-when-delivery-and-examples", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/references/x.md": contract_text("x", ["do", ("done", "event")]).replace(
            "Delivery: at least once, in order per key.\n", "Delivery: at least once, in order per key.\nExamples:\n\n"
            "| Case | Action | Emitted |\n|---|---|---|\n| finished | `do()` returns | `done` |\n")}), []),
    ("C9-event-examples-with-other-columns", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/references/x.md": contract_text("x", ["do", ("done", "event")]).replace(
            "Delivery: at least once, in order per key.\n", "Delivery: at least once, in order per key.\nExamples:\n\n"
            "| Case | Input | Expected |\n|---|---|---|\n| finished | `do()` | `done` |\n")}), ["warn C9 docs/references/x.md"]),
    ("M2-runs-as-unknown", project("runs-as: daemon\n"), ["error M2 unifold.yaml"]),
    ("clean-runs-as", project("runs-as: process\n", {"a": "runs-as: library\n"}), []),
    ("clean-carried-contract-uses-the-carrier", project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.x: b.x\n  a.bus: c.bus\n"
        "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a -> b.do: ok\n    expect: e\n",
        {"a": NEEDS_X + "  bus: {summary: s, contract: ref:bus}\ncapabilities:\n  api: {summary: s, contract: ref:api}\n",
         "b": CAPABILITY_X, "c": "capabilities:\n  bus: {summary: s, contract: ref:bus}\n"},
        {"docs/references/x.md": contract_text("x", ["do"]).replace("Sources: none", "Sources: none\nCarried by: [bus](bus.md)")},
        contracts={"api": ["serve"], "bus": ["publish"]}), ["info N4 docs/references/bus.md"]),
    ("N1-hop-to-a-type", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.thing: ok"), SCENARIO_UNITS,
                                contracts={"api": ["serve"], "x": ["do", ("thing", "type")]}), ["error N1 unifold.yaml", "warn C10 docs/references/x.md"]),
    ("N2-result-read-as-a-number", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.do: 1000"), SCENARIO_UNITS,
                                           contracts=SCENARIO_CONTRACTS), ["error N2 unifold.yaml"]),
    ("N7-result-contradicts-the-example", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.do(do()): \"2\""),
                                                  SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS), ["error N7 unifold.yaml"]),
    ("N7-no-such-example", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.do: = two"), SCENARIO_UNITS,
                                   contracts=SCENARIO_CONTRACTS), ["error N7 unifold.yaml"]),
    ("clean-result-from-an-example", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.do: = one"), SCENARIO_UNITS,
                                             contracts=SCENARIO_CONTRACTS), []),
    ("clean-result-equals-the-example", project(SCENARIO_ROOT.replace("a -> b.do: ok", "a -> b.do(do()): \"1\""), SCENARIO_UNITS,
                                                contracts=SCENARIO_CONTRACTS), []),
    ("N8-result-almost-an-error-case", state_project("      - api -> a.serve: ok\n      - a -> b.open(): ok\n      - a -> b.send([1]): Lost\n"),
     ["warn N8 unifold.yaml"]),
    ("N1-two-connections-share-the-part", project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.p1: b.c1\n  a.p2: b.c2\n"
        "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a -> b.do: ok\n    expect: e\n",
        {"a": "capabilities:\n  api: {summary: s, contract: ref:api}\nneeds:\n  p1: {summary: s, contract: ref:x}\n  p2: {summary: s, contract: ref:x}\n",
         "b": "capabilities:\n  c1: {summary: s, contract: ref:x}\n  c2: {summary: s, contract: ref:x}\n"},
        contracts=SCENARIO_CONTRACTS), ["error N1 unifold.yaml"]),
    ("clean-hop-names-the-capability", project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.p1: b.c1\n  a.p2: b.c2\n"
        "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a -> b.c1.do: ok\n      - a -> b.c2.do: ok\n    expect: e\n",
        {"a": "capabilities:\n  api: {summary: s, contract: ref:api}\nneeds:\n  p1: {summary: s, contract: ref:x}\n  p2: {summary: s, contract: ref:x}\n",
         "b": "capabilities:\n  c1: {summary: s, contract: ref:x}\n  c2: {summary: s, contract: ref:x}\n"},
        contracts=SCENARIO_CONTRACTS), []),
    ("N6-path-the-states-forbid", state_project("      - api -> a.serve: ok\n      - a -> b.send([1]): ok\n"),
     ["error N6 unifold.yaml", "info N4 docs/references/x.md"]),
    ("N6-success-that-only-a-failure-row-allows", state_project(rows=STATE_ROWS + ["| open | `open` | `refused` | open |"],
                                                                hops=STATE_HOPS + "      - a -> b.open(): ok\n"),
     ["error N6 unifold.yaml"]),
    # ------------------------------------------------ C: contracts
    ("C1-contract-without-parts", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X},
                                          {"docs/references/x.md": "# x\n\n## Use\n\nAny order.\n\n## Fake\n\nReplays.\n"}), ["warn C1 docs/references/x.md"]),
    ("clean-error-name-with-spaces", state_project(
        "      - api -> a.serve: ok\n      - a -> b.open(): ok\n      - a -> b.send([1]): line gone\n      - a -> b.open(): ok\n",
        rows=STATE_ROWS + ["| open | `send` | `line gone` | closed |"]), []),
    ("C6-contract-without-use", state_project(use=False), ["warn C6 docs/references/x.md"]),
    ("C7-row-of-no-part", state_project(rows=STATE_ROWS + ["| open | `close` | ok | closed |"]), ["error C7 docs/references/x.md"]),
    ("C7-result-that-is-no-error-case", state_project(rows=STATE_ROWS + ["| open | `send` | `busy` | open |"]),
     ["error C7 docs/references/x.md"]),
    ("C7-no-start-state", state_project(start=None), ["error C7 docs/references/x.md"]),
    ("C7-two-rows-for-one-step", state_project(rows=STATE_ROWS + ["| open | `send` | ok | closed |"]),
     ["error C7 docs/references/x.md"]),
    ("C1-part-with-unknown-kind", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X},
                                          {"docs/references/x.md": contract_text("x", [("do", "call")])}), ["warn C1 docs/references/x.md"]),
    ("C2-query-without-examples", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X},
                                          {"docs/references/x.md": contract_text("x", ["do"]).replace("| one | `do()` | 1 |\n", "")}),
     ["warn C2 docs/references/x.md"]),
    ("C2-command-without-pre", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X},
                                       {"docs/references/x.md": contract_text("x", [("do", "command")]).replace("Pre: none.\n", "")}),
     ["warn C2 docs/references/x.md"]),
    ("C3-part-without-a-signature", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X},
                                            {"docs/references/x.md": contract_text("x").replace(FENCE + "wit\nrecord x { v: u32 }\n" + FENCE + "\n", "")}),
     ["warn C3 docs/references/x.md"]),
    ("C4-type-defined-twice-in-a-subtree", project("wiring:\n  a.x: b.x\n  a.y: b.y\n",
                                                   {"a": NEEDS_X + "  y: {summary: s, contract: ref:y}\n", "b": CAPABILITY_X + "  y: {summary: s, contract: ref:y}\n"},
                                                   contracts={"x": [("thing", "type")], "y": [("thing", "type")]}),
     ["warn C4 docs/references/y.md"]),
    ("C4-same-type-in-two-subtrees-is-fine", project("", {
        "a": "kind: stateful\nwiring:\n  p.x: q.x\n", "a/p": "needs:\n  x: {summary: s, contract: ../docs/references/x.md}\n",
        "a/q": "capabilities:\n  x: {summary: s, contract: ../docs/references/x.md}\n",
        "b": "kind: stateful\nwiring:\n  p.x: q.x\n", "b/p": "needs:\n  x: {summary: s, contract: ../docs/references/x.md}\n",
        "b/q": "capabilities:\n  x: {summary: s, contract: ../docs/references/x.md}\n"},
        {"a/docs/references/x.md": contract_text("x", [("thing", "type")]), "b/docs/references/x.md": contract_text("x", [("thing", "type")])}), []),
    ("C10-type-no-part-uses", type_project(), UNUSED_TYPE),
    ("C10-a-word-in-a-sentence-is-no-use", type_project(("Result: a number.", "Result: the thing, as a number.")), UNUSED_TYPE),
    ("C10-part-of-a-longer-name-is-no-use", type_project(("do: func() -> u32;", "do: func(thing-id: u32) -> u32;")), UNUSED_TYPE),
    ("C10-types-that-name-only-each-other", type_project(("record thing { v: u32 }", "record thing { o: other }"),
                                                         ("record other { v: u32 }", "record other { t: thing }"), parts=TWO_TYPES),
     UNUSED_TYPE * 2),
    ("C10-unused-part-of-a-contract-folder", folder_project("do: func() -> u32;"), ["warn C10 docs/references/x/thing.md"]),
    ("C10-clean-named-in-a-signature", type_project(RETURNS_THING), []),
    ("C10-clean-named-by-an-event", type_project(("do: func() -> u32;", "do: func(thing: thing);"), parts=(("do", "event"), ("thing", "type"))), []),
    ("C10-clean-spelled-in-the-notation-of-the-signature", type_project(
        ("do: func() -> u32;", "do() -> exit status, FoundStick, sent_count"),
        parts=("do", ("exit-status", "type"), ("found-stick", "type"), ("sent-count", "type"))), []),
    ("C10-clean-reached-through-another-type", type_project(RETURNS_THING, ("record thing { v: u32 }", "record thing { o: other }"), parts=TWO_TYPES), []),
    ("C10-clean-linked-within-the-contract", type_project(("Result: a number.", "Result: a [thing](#thing).")), []),
    ("C10-clean-linked-from-another-contract", project(
        "wiring:\n  a.x: b.x\n  a.y: b.y\n",
        {"a": NEEDS_X + "  y: {summary: s, contract: ref:y}\n", "b": CAPABILITY_X + "  y: {summary: s, contract: ref:y}\n"},
        {"docs/references/y.md": contract_text("y", ["go"]).replace("Result: a number.", "Result: a [thing](x.md#thing).")},
        contracts={"x": ["do", ("thing", "type")]}), []),
    ("C10-clean-a-contract-of-types-only", type_project(parts=(("thing", "type"), ("other", "type"))), []),
    ("C10-clean-used-in-a-contract-folder", folder_project("do: func() -> thing;"), []),
    ("C5-contract-without-fake", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X},
                                         {"docs/references/x.md": contract_text("x").replace("## Fake\n\nReplays the examples.\n", "")}),
     ["warn C5 docs/references/x.md"]),
    ("C-rules-only-for-named-contracts", project(files={"docs/references/notes.md": "# Notes\n\nNo parts here.\n"}), []),
    # ------------------------------------------------ L, T: documents
    ("L1-broken-link", project(files={"README.md": "# demo\n\n[gone](docs/gone.md)\n\n## Why\n\nBecause.\n"}),
     ["error L1 README.md"]),
    ("L1-broken-link-in-angle-brackets-and-html", project(files={
        "README.md": "# demo\n\n[a\nb](<no such file.md>)\n\n<a href=\"gone.html\">x</a>\n\n## Why\n\nBecause.\n"}),
     ["error L1 README.md", "error L1 README.md"]),
    ("L1-broken-anchor", project(files={
        "README.md": "# demo\n\n[part](docs/explanation/reasoning.md#no-such-part) [ok](docs/explanation/reasoning.md#real-part)\n\n## Why\n\nBecause.\n",
        "docs/explanation/reasoning.md": "# Reasoning\n\n## Real part\n\nText.\n"}), ["error L1 README.md"]),
    ("L1-anchor-of-a-table-row", project(files={
        "README.md": "# demo\n\n[word](docs/references/glossary.md#my-term) [none](docs/references/glossary.md#term)\n\n## Why\n\nBecause.\n",
        "docs/references/glossary.md": "# Glossary\n\n| Term | Meaning |\n|---|---|\n| `My term` | Text |\n"}),
     ["error L1 README.md"]),
    ("L1-links-in-code-are-ignored", project(files={
        "README.md": "# demo\n\n`[x](gone.md)`\n\n````text\n```\n[y](gone.md)\n````\n\n[paren](docs/references/a_(v1).md)\n\n## Why\n\nBecause.\n",
        "docs/references/a_(v1).md": "# A\n"}), []),
    ("L1-broken-link-in-a-tutorial", project(files={"docs/tutorials/x.md": "# X\n\n[gone](nope.md)\n"}),
     ["error L1 docs/tutorials/x.md"]),
    ("L11-upward-link-is-allowed", project("", {"a": ""}, {
        "a/README.md": "# a\n\n[up](../README.md)\n\n## Why\n\nBecause.\n",
        "a/docs/explanation/reasoning.md": "# Why\n\n[up](../../../docs/decisions/0001-x.md)\n", **with_decision()}), []),
    ("L11-upward-link-from-context-is-allowed", project("", {"a": ""}, {
        CONTEXT: "# Context of a\n\n### [demo](../../../README.md)\n\nx, so y.\n"}), []),
    ("L11-sideways-link", project("", {"a": "", "b": ""}, {
        "a/README.md": "# a\n\n[b](../b/README.md)\n\n## Why\n\nBecause.\n"}), ["warn L11 a/README.md"]),
    ("L11-downward-link-is-allowed", project("", {"a": "kind: stateful\n", "a/deep": ""}, {
        "README.md": "# demo\n\n[a](a/unifold.yaml), [deep](a/deep/README.md)\n\n## Why\n\nBecause.\n"}), []),
    ("L11-sideways-link-below-a-sibling", project("", {"a": "", "b": "", "b/deep": ""}, {
        "a/README.md": "# a\n\n[deep](../b/deep/README.md)\n\n## Why\n\nBecause.\n"}), ["warn L11 a/README.md"]),
    ("L2-absolute-link", project(files={"README.md": "# demo\n\n[x](/docs/x.md)\n\n## Why\n\nBecause.\n"}),
     ["error L2 README.md"]),
    ("L2-link-out-of-the-project", project(files={"README.md": "# demo\n\n[up](..) [in](../demo/README.md)\n\n## Why\n\nBecause.\n"}),
     ["error L2 README.md"]),
    ("L2-link-into-a-nested-project", project("", {"a": ""}, {
        "nested/unifold.yaml": 'unifold: "0.4"\nresponsibility: r\n', "nested/README.md": README.format(name="nested"),
        "a/README.md": "# a\n\nSee [nested](../nested/README.md).\n\n## Why\n\nBecause.\n"}),
     ["error L2 a/README.md"]),
    ("T9-readme-without-why", project(files={"README.md": "# demo\n\nWhat it is for.\n"}), ["warn T9 README.md"]),
    ("T9-readme-without-title-first", project(files={"README.md": "Just text, no title.\n\n## Why\n\nBecause.\n"}),
     ["warn T9 README.md"]),
    ("T9-readme-without-paragraph", project(files={"README.md": "# demo\n\n## Why\n\nBecause.\n"}), ["warn T9 README.md"]),
    ("T9-readme-still-the-template", project(files={"README.md": "# demo\n\n<One paragraph.>\n\n## Why\n\n<Why.>\n"}),
     ["warn T9 README.md"]),
    ("L11-generated-marker-gives-no-exemption", project("", {"a": "", "b": ""}, {
        "a/README.md": MARK + "\n# a\n\n[b](../b/README.md)\n\n## Why\n\nBecause.\n"}), ["warn L11 a/README.md"]),
    ("L1-context-cites-a-missing-section", project("", {"a": "status: planned\n"}, {
        CONTEXT: "# Context of a\n\n### [demo](../../../README.md#no-such-section)\n\nx, so y.\n"}),
     [f"error L1 {CONTEXT}"]),
    ("T1-file-too-long", project(files={"docs/explanation/risks.md": "# Risks\n\n" + "word " * 1500 + "\n"}),
     ["warn T1 docs/explanation/risks.md"]),
    ("T1-file-at-the-limit", project(files={"docs/explanation/risks.md": "# Risks\n\n" + "word " * 1499 + "\n"}), []),
    ("T1-pipes-and-dashes-are-no-words", project(files={"docs/explanation/risks.md": "# Risks\n\n" + "| a | - |\n" * 1400}), []),
    ("T4-why-too-long", project(files={"README.md": WHY.format(name="demo", lines="why " * 251 + "\n")}),
     ["warn T4 README.md"]),
    ("T4-why-of-250-words", project(files={"README.md": WHY.format(name="demo", lines="why\n\n" * 250)}), []),
    # ------------------------------------------------------ G: generated files
    ("G1-generated-file-missing", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}),
     ["error G1 AGENTS.md", "error G1 docs/diagrams/component.md"],
     {"fix": False}),
    ("G1-generated-file-out-of-date", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/diagrams/component.md": MARK + "\n# Old\n"}),
     ["error G1 AGENTS.md", "error G1 docs/diagrams/component.md"],
     {"fix": False}),
    ("G1-leftover-generated-file", project(files={"docs/diagrams/component.md": MARK + "\n# Old\n"}),
     ["error G1 AGENTS.md", "error G1 docs/diagrams/component.md"], {"fix": False}),
    ("G1-leftover-in-a-folder-that-is-no-longer-a-unit", project(files={
        "old/AGENTS.md": MARK + "\n# AGENTS.md: old\n", "old/docs/diagrams/context.md": MARK + "\n# Old\n",
        "old/notes/AGENTS.md": "# Hand-written\n"}),
     ["error G1 AGENTS.md", "error G1 old/AGENTS.md", "error G1 old/docs/diagrams/context.md"], {"fix": False}),
    ("G1-hand-written-file-at-generated-path", project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "docs/diagrams/component.md": "# Mine\n"}),
     ["error G1 AGENTS.md", "error G1 docs/diagrams/component.md"],
     {"fix": False}),
    ("G1-hand-written-file-among-diagrams", project(files={"docs/diagrams/mine.md": "# Mine\n"}),
     ["error G1 AGENTS.md", "error G1 docs/diagrams/mine.md"], {"fix": False}),
    ("G1-decision-index-missing", project(files=with_decision()),
     ["error G1 AGENTS.md", "error G1 docs/decisions/index.md"], {"fix": False}),
    ("G1-agents-file-missing", project("", {"a": ""}),
     ["error G1 AGENTS.md", "error G1 docs/diagrams/component.md"],
     {"fix": False}),
    ("G1-leftover-agents-file-of-a-unit", project("", {"a": ""}, {"a/AGENTS.md": MARK + "\n# AGENTS.md: a\n"}),
     ["error G1 AGENTS.md", "error G1 a/AGENTS.md", "error G1 docs/diagrams/component.md"],
     {"fix": False}),
    ("G1-hand-written-agents-file-of-a-unit-is-not-ours", project("", {"a": ""}, {"a/AGENTS.md": AGENTS.format(name="a")}), []),
    ("G1-agents-file-without-marker", project(files={"AGENTS.md": AGENTS.format(name="demo")}),
     ["error G1 AGENTS.md"]),
    ("G1-agents-file-out-of-date", project(files={"AGENTS.md": MARK + "\n# AGENTS.md: old\n"}),
     ["error G1 AGENTS.md"], {"fix": False}),
    ("G1-scenario-diagram-missing", project(SCENARIO_ROOT, SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS),
     ["error G1 AGENTS.md", "error G1 docs/diagrams/component.md"], {"fix": False}),
    ("G1-component-diagrams-only", project("", {"a": "kind: stateful\n", "a/deep": ""}, {
        "a/docs/diagrams/context.md": MARK + "\n# Old\n", "docs/diagrams/architecture.md": MARK + "\n# Old\n"}),
     ["error G1 AGENTS.md", "error G1 a/docs/diagrams/component.md", "error G1 a/docs/diagrams/context.md",
      "error G1 docs/diagrams/architecture.md", "error G1 docs/diagrams/component.md"],
     {"fix": False}),
]


# ------------------------------------------------------------------ running

class Runner:
    def __init__(self, tool: list):
        self.tool = tool

    def run(self, *args: str, cwd=None, stdin=None, env=None) -> subprocess.CompletedProcess:
        return subprocess.run([*self.tool, *args], capture_output=True, text=True, cwd=cwd,
                              input=stdin, env={**os.environ, **(env or {})})

    def json(self, *args: str, cwd=None):
        """Run and parse stdout as JSON. Returns (data, process)."""
        done = self.run(*args, cwd=cwd)
        try:
            return json.loads(done.stdout), done
        except ValueError:
            raise AssertionError(f"`{' '.join(args)}` printed no valid JSON: "
                                 f"{(done.stdout + done.stderr).strip()[:300]}")

    def findings(self, folder, *args) -> list:
        data, _ = self.json("check", "--json", *args, str(folder))
        return sorted(f"{f['severity']} {f['rule']} {f['file']}" for f in data["findings"])


def write_files(folder: Path, files: dict) -> None:
    for path, content in files.items():
        target = folder / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def new_project(tmp: str, files: dict) -> Path:
    folder = Path(tmp).resolve() / "demo"
    write_files(folder, files)
    return folder


def run_case(runner: Runner, case) -> str | None:
    name, files, expected = case[:3]
    options = case[3] if len(case) > 3 else {}
    with tempfile.TemporaryDirectory() as tmp:
        folder = new_project(tmp, files)
        if options.get("fix", True):
            runner.run("check", "--fix", str(folder))
        args = list(options.get("args", []))
        try:
            found = runner.findings(folder, *args)
        except AssertionError as exc:
            return str(exc)
        if found != sorted(expected):
            return f"expected {sorted(expected)}\n     found    {found}"
    return None


# ---------------------------------------------------------------- scenarios

def check(condition, message):
    if not condition:
        raise AssertionError(message)


def check_mermaid(page: str):
    """The sequence diagram of a printed page is well formed: blocks balanced, `and` only in `par`,
    no `end` right before `and`, and every `deactivate` matches an `activate` of the same lifeline."""
    source = re.search(r"```mermaid\n(.*?)\n```", page, re.S)
    check(source is not None, "the page has a mermaid block")
    blocks, active = [], {}
    lines = [l.strip() for l in source.group(1).splitlines()]
    for index, line in enumerate(lines):
        word = line.split(" ")[0] if line else ""
        if word in ("par", "loop", "rect", "opt", "alt", "critical", "break"):
            blocks.append(word)
        elif word == "and":
            check(blocks and blocks[-1] == "par", f"`and` outside a par at line {index}:\n{source.group(1)}")
            check(lines[index - 1] != "end", f"`end` right before `and` at line {index}:\n{source.group(1)}")
        elif word == "end":
            check(blocks, f"`end` without a block at line {index}:\n{source.group(1)}")
            blocks.pop()
        elif word == "activate":
            active[line.split()[1]] = active.get(line.split()[1], 0) + 1
        elif word == "deactivate":
            who = line.split()[1]
            check(active.get(who, 0) > 0, f"deactivate of an idle lifeline {who} at line {index}:\n{source.group(1)}")
            active[who] -= 1
    check(not blocks, f"unclosed blocks {blocks}:\n{source.group(1)}")
    for number in re.findall(r"^\| (\d+) \|", page, re.M):
        check(re.search(rf"(?<![\d↩] ){number} · ", source.group(1)) is not None, f"step {number} of the table is not in the picture:\n{page}")


def scenario_json_on_failure(runner: Runner, tmp: str):
    empty = Path(tmp) / "empty"
    empty.mkdir()
    data, done = runner.json("check", "--json", str(empty))
    check(done.returncode == 2 and data["ok"] is False and data["findings"] == []
          and data["error"]["code"] == "no-project", f"no project: {done.returncode} {data}")
    for command in (["show"], ["tree"], ["capability", str(empty), "x"], ["impact"], ["skills"]):
        args = command if len(command) > 1 else [*command, str(empty)]
        data, done = runner.json(*args[:1], "--json", *args[1:])
        check(done.returncode == 2 and data["ok"] is False and "message" in data["error"],
              f"{command[0]} --json outside a project: {data}")
    data, done = runner.json("check", "--json", str(empty / "missing"))
    check(done.returncode == 2 and data["ok"] is False, "check on a missing path")
    broken = new_project(tmp, {"unifold.yaml": ROOT + "responsibility: twice\n", "a/unifold.yaml": UNIT})
    data, done = runner.json("check", "--json", str(broken / "a"))
    check(done.returncode == 1 and not data["ok"] and data["findings"][0]["rule"] == "M1"
          and data["findings"][0]["file"] == "unifold.yaml" and data["findings"][0]["line"] == 3,
          f"a broken root manifest is still the root: {data}")
    data, done = runner.json("show", "--json", str(broken))
    check(done.returncode == 2 and data["error"]["code"] == "bad-root", "show with a broken root")


def scenario_finding_shape(runner: Runner, tmp: str):
    folder = new_project(tmp, project("wiring:\n  a.x: b.y\n", {"a": NEEDS_X, "b": CAPABILITY_X}))
    runner.run("check", "--fix", str(folder))
    data, done = runner.json("check", "--json", str(folder))
    check(done.returncode == 1 and data["ok"] is False, "exit code 1 with errors")
    check(data["summary"]["error"] == 2 and data["summary"]["warn"] == 1
          and data["summary"]["units"] == 3, f"summary: {data['summary']}")
    for finding in data["findings"]:
        check(set(finding) >= {"rule", "severity", "file", "line", "message", "fix", "url"},
              f"finding keys: {sorted(finding)}")
        check(finding["severity"] in ("error", "warn", "info"), "severity is a word")
    w1 = next(f for f in data["findings"] if f["rule"] == "W1")
    check(w1["line"] == 4 and "it provides: x" in w1["message"], f"W1 line and hint: {w1}")
    text = runner.run("check", str(folder)).stdout
    check("error W1 unifold.yaml:4:" in text and "fix:" in text, f"text output: {text}")
    github = runner.run("check", "--format", "github", str(folder), cwd=str(folder.parent)).stdout
    check("::error file=demo/unifold.yaml,line=4,title=unifold W1::" in github
          and "::warning file=demo/unifold.yaml" in github, f"github output: {github}")
    strict = project("", {"b": CAPABILITY_X})
    folder2 = Path(tmp) / "strict"
    write_files(folder2, strict)
    runner.run("check", "--fix", str(folder2))
    check(runner.run("check", str(folder2)).returncode == 0, "a warning alone: exit 0")
    check(runner.run("check", "--strict", str(folder2)).returncode == 1, "--strict: exit 1")
    only = runner.findings(folder, "--rule", "W3")
    check(only == ["warn W3 unifold.yaml"], f"--rule: {only}")
    data, done = runner.json("check", "--json", "--strict", "--ignore", "W3", str(folder2))
    check(done.returncode == 0 and data["ok"] and data["findings"] == [] and data["summary"]["ignored"] == {"W3": 1}
          and data["summary"]["warn"] == 0, f"--ignore drops the finding and counts it: {data['summary']}")
    text = runner.run("check", "--strict", "--ignore", "W3", str(folder2)).stdout
    check("W3×1 ignored" in text, f"the summary line names the ignored rule: {text}")
    data, done = runner.json("check", "--json", "--ignore", "W1", str(folder))
    check(done.returncode == 1 and data["summary"]["ignored"] == {"W1": 1} and data["summary"]["error"] == 1,
          f"--ignore drops an error too, whatever the severity: {data['summary']}")


def scenario_generate_is_idempotent(runner: Runner, tmp: str):
    files = project(
        NEEDS_X + "  log: {summary: s, contract: ref:log}\n"
        "wiring:\n  a.x: {real: b.x, fake: c.x}\n  a.log: log\n  b.log: log\n  deep.log: log\n",
        {"a": NEEDS_X + "  log: {summary: Logs, contract: ref:log}\n",
         "b": CAPABILITY_X + "needs:\n  log: {summary: Logs, contract: ref:log}\n",
         "c": "kind: stateful\n" + CAPABILITY_X,
         "my plugins/deep": "status: planned\nneeds:\n  log: {summary: Logs, contract: ref:log}\n",
         "c/inner": ""},
        with_decision())
    folder = new_project(tmp, files)
    first = runner.run("check", "--fix", str(folder))
    check(first.returncode == 0, f"check --fix: {first.stdout}{first.stderr}")

    def snapshot():
        return {str(p.relative_to(folder)): p.read_text() for p in sorted(folder.rglob("*.md"))}
    before = snapshot()
    data, _ = runner.json("check", "--fix", "--json", str(folder))
    fixed = data["summary"]["fixed"]
    check(fixed["written"] == [] and fixed["removed"] == [], f"a second check --fix wrote: {fixed}")
    for path in list(folder.rglob("docs/diagrams/*.md")) + list(folder.rglob("AGENTS.md")) \
            + [folder / "docs/decisions/index.md"]:
        path.unlink()
    runner.run("check", "--fix", str(folder), env={"PYTHONHASHSEED": "12345"})
    check(snapshot() == before, "regenerated from nothing: not byte-identical")
    check(runner.findings(folder) == [], f"clean after check --fix: {runner.findings(folder)}")
    component = before["docs/diagrams/component.md"]
    check("Shared connections, not drawn" in component
          and "- need `a.log`, `b.log`, `deep.log` → need `log` of `demo`, passed up" in component
          and "|\"log\"|" not in component,
          f"a need that three children pass up is listed, not drawn: {component}")
    check("my%20plugins/deep" in component, "generated links are URL-encoded")
    check("-.->" in component, "an alternative is a dashed arrow")
    check("**planned**" in component, "status is marked in the unit table")
    check(sorted(p for p in before if "/diagrams/" in p) == ["c/docs/diagrams/component.md", "docs/diagrams/component.md"],
          f"a component diagram for every unit with children, and no other diagram: {sorted(before)}")
    check("proposed" in before["docs/decisions/index.md"], "decision index")
    check(before["AGENTS.md"].startswith(MARK) and "<!-- unifold:end -->" in before["AGENTS.md"]
          and "| a | `a` | A part |" in before["AGENTS.md"], "the root AGENTS.md carries the unit index")
    check(sorted(p for p in before if p.endswith("AGENTS.md")) == ["AGENTS.md"],
          f"AGENTS.md is generated at the root only: {sorted(before)}")


def scenario_show_port_impact(runner: Runner, tmp: str):
    folder = new_project(tmp, project(
        "needs:\n  clock: {summary: A time source, contract: ref:clock}\n"
        "capabilities:\n  api: {summary: s, contract: ref:api}\n"
        "wiring:\n  api: web.api\n  web.store: db.store\n  web.log: db.log\n  web.clock: clock\n",
        {"web": "kind: stateful\ncapabilities:\n  api: {summary: s, contract: ref:api}\n"
                "needs:\n  store: {summary: s, contract: ref:schema}\n"
                "  log: {summary: s, contract: ref:log}\n"
                "  clock: {summary: s, contract: ref:clock}\n"
                "wiring:\n  inner.clock: clock\n  inner.store: store\n",
         "web/inner": "needs:\n  clock: {summary: Needs time, contract: ref:clock}\n"
                      "  store: {summary: s, contract: ref:schema}\n",
         "db": "status: planned\ncapabilities:\n  store: {summary: Keeps things, contract: ref:schema}\n"
               "  log: {summary: s, contract: ref:log}\n"}))
    data, done = runner.json("show", "--json", str(folder / "web" / "inner"))
    check(done.returncode == 0, "show")
    clock = data["needs"]["clock"]["provided-by"][0]
    check(clock.get("outside") and clock["root-need"] == "clock",
          f"a need passed up through two levels in show: {clock}")
    store = data["needs"]["store"]["provided-by"][0]
    check(store["unit"] == "db" and store["status"] == "planned"
          and data["needs"]["store"]["contract"] == "docs/references/schema.md", f"resolved provider with status: {store}")
    text = runner.run("show", str(folder / "web" / "inner")).stdout
    check("[planned" in text, f"show text: {text}")
    data, _ = runner.json("show", "--json", str(folder / "web"))
    log = data["needs"]["log"]["provided-by"][0]
    check(log["unit"] == "db", f"an explicit line in show: {log}")
    data, _ = runner.json("capability", "--json", str(folder / "db"), "store")
    check([e.get("unit") for e in data["ends"]] == ["db", "web/inner"]
          and data["ends"][0]["status"] == "planned", f"capability: {data}")
    done = runner.run("capability", str(folder / "db"), "nothing")
    check(done.returncode == 2 and "store" in done.stderr, "capability with an unknown name")
    data, _ = runner.json("impact", "--json", str(folder / "db"))
    check([d["unit"] for d in data["dependents"]] == ["web", "web/inner"]
          or sorted(d["unit"] for d in data["dependents"]) == ["web", "web/inner"],
          f"impact: {data['dependents']}")
    data, _ = runner.json("impact", "--json", str(folder / "web"), "api")
    check(data["outside"] == ["api"] and data["exposed-as"] == [{"unit": ".", "capability": "api"}],
          f"impact of a capability that the root exposes: {data}")
    data, _ = runner.json("tree", "--json", str(folder))
    check([u["path"] for u in data] == [".", "db", "web", "web/inner"], f"tree: {data}")


def scenario_own_needs(runner: Runner, tmp: str):
    """A unit whose own code uses its children declares needs and wires them to the children.
    Such a need is met inside: it is not a need of the project, and its provider counts it as a
    user. A need of a child is never met by a need of the parent with the same name."""
    files = project(
        "needs:\n  invoices: {summary: Creates invoices, contract: ref:invoices}\n"
        "  clock: {summary: The current time, contract: ref:clock}\n"
        "  mailer: {summary: Sends mail, contract: ref:mailer}\n"
        "wiring:\n  billing.clock: platform.clock\n  billing.mailer: mailer\n"
        "  invoices: billing.invoices\n  clock: platform.clock\n",
        {"billing": "capabilities:\n  invoices: {summary: s, contract: ref:invoices}\n"
                    "needs:\n  clock: {summary: s, contract: ref:clock}\n"
                    "  mailer: {summary: s, contract: ref:mailer}\n",
         "platform": "capabilities:\n  clock: {summary: s, contract: ref:clock}\n"})
    folder = new_project(tmp, files)
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"clean: {runner.findings(folder)}")
    data, _ = runner.json("show", "--json", str(folder))
    clock, mailer = data["needs"]["clock"]["provided-by"], data["needs"]["mailer"]["provided-by"]
    check([e.get("unit") for e in clock] == ["platform"] and not clock[0].get("outside"),
          f"a need met inside is provided by the child: {clock}")
    check(mailer[0].get("outside"), f"a need passed up stays a need of the project: {mailer}")
    data, _ = runner.json("show", "--json", str(folder / "platform"))
    users = sorted(u["unit"] for u in data["capabilities"]["clock"]["used-by"])
    check(users == [".", "billing"], f"the parent is a user of the child: {users}")
    data, _ = runner.json("impact", "--json", str(folder / "platform"))
    check({"unit": ".", "distance": 1} in [{k: d[k] for k in ("unit", "distance")} for d in data["dependents"]],
          f"impact names the parent: {data['dependents']}")
    text = runner.run("show", str(folder / "platform")).stdout
    check("used by the root as need 'clock'" in text, f"show names the root: {text}")
    component = (folder / "docs/diagrams/component.md").read_text()
    check("n_root___clock --> u_platform" in component
          and "| need `clock` of `demo` | `platform.clock` |" in component,
          f"the component diagram draws the need of the parent: {component}")
    manifest = folder / "unifold.yaml"
    manifest.write_text(manifest.read_text().replace("  billing.clock: platform.clock\n", ""))
    check(runner.findings(folder) == ["error G1 docs/diagrams/component.md", "error W2 unifold.yaml"],
          f"the need of the parent does not meet the need of a child: {runner.findings(folder)}")


def scenario_citations(runner: Runner, tmp: str):
    """`impact FILE` lists every link to a file; a link from context.md is marked as such."""
    folder = new_project(tmp, project("", {"a": "status: planned\n"}, CONTEXT_FILES))
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"a context item needs no stamp: {runner.findings(folder)}")
    decision = folder / "docs/decisions/0001-x.md"
    rows = runner.json("impact", "--json", str(decision))[0]["citations"]
    check(rows == [{"file": CONTEXT, "line": 3, "cites": "docs/decisions/0001-x.md", "kind": "context"}],
          f"impact FILE: {rows}")
    done = runner.run("impact", str(decision))
    check(f"{CONTEXT}:3" in done.stdout, f"impact prints file and line: {done.stdout}")
    decision.unlink()
    data, done = runner.json("impact", "--json", str(decision))
    check(done.returncode == 0 and any(r["file"] == CONTEXT for r in data["citations"]),
          f"impact works for a file that was deleted: {data}")
    done = runner.run("stamp", str(folder))
    check(done.returncode == 2, f"there is no command stamp: {done.stdout}{done.stderr}")


GLOSSARY = ("# Glossary\n\n## Words\n\n| Term | Meaning |\n|---|---|\n"
            "| **`capability`** | What a unit provides |\n| other | Text. |\n")
ROW_ITEM = ("# Context of a\n\n### [demo: capability](../../../docs/references/glossary.md#capability)\n"
            "\nA capability is what a unit provides, and a has one.\n")


def scenario_row_anchor(runner: Runner, tmp: str):
    """A fragment may name the first cell of a table row; the header row is no anchor."""
    folder = new_project(tmp, project("", {"a": "status: planned\n"}, {
        "docs/references/glossary.md": GLOSSARY, CONTEXT: ROW_ITEM}))
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"a row is an anchor: {runner.findings(folder)}")
    (folder / CONTEXT).write_text(ROW_ITEM.replace("#capability", "#term"))
    found = runner.findings(folder)
    check(found == [f"error L1 {CONTEXT}"], f"the header row of a table is no anchor: {found}")


def scenario_check_fix(runner: Runner, tmp: str):
    folder = new_project(tmp, project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "a/docs/diagrams/context.md": MARK + "\n# Left over\n"}))
    check(runner.findings(folder) == ["error G1 AGENTS.md", "error G1 a/docs/diagrams/context.md",
                                      "error G1 docs/diagrams/component.md"], "before --fix")
    data, done = runner.json("check", "--fix", "--json", str(folder))
    check(done.returncode == 0 and data["ok"] and sorted(data["summary"]["fixed"]["written"]) ==
          ["AGENTS.md", "docs/diagrams/component.md"]
          and data["summary"]["fixed"]["removed"] == ["a/docs/diagrams/context.md"],
          f"--fix: {data['summary']}")
    (folder / "docs/diagrams/component.md").write_text("# Mine\n")
    done = runner.run("check", "--fix", str(folder))
    check(done.returncode == 1 and (folder / "docs/diagrams/component.md").read_text() == "# Mine\n",
          "check --fix does not overwrite a file without the marker")


EXPECTED_AGENTS_ROOT = (MARK + """
# AGENTS.md: demo

unifold unit; run `unifold show` here. Read [README.md](README.md) first: it says what the unit is for and why it is built this way. Everything else is in `docs/`.

## Documents

| Kind | Files |
|---|---|
| Learn | [first-steps](docs/tutorials/first-steps.md) |
| Look up | [api](docs/references/api/index.md), [events](docs/references/events.md) |
| Understand | [reasoning](docs/explanation/reasoning.md), [runtime](docs/explanation/runtime.md), [risks](docs/explanation/risks.md), [aaa-topic](docs/explanation/aaa-topic.md), [zz-topic](docs/explanation/zz-topic.md), [decisions](docs/decisions/index.md) |

## Skills

| Skill | Description |
|---|---|
| [do-it](docs/skills/do-it/SKILL.md) | Does it. |

<!-- unifold:begin""")


def scenario_agents_generated(runner: Runner, tmp: str):
    """AGENTS.md is generated at the root only: its content, and the refusal to overwrite a
    hand-written one."""
    folder = new_project(tmp, project("", {"a": "", "b": ""}, {
        "docs/tutorials/first-steps.md": "# First steps\n",
        "docs/references/events.md": "# Events\n",
        "docs/references/api/index.md": "# API\n",
        "docs/references/api/calls.md": "# Calls\n",
        "docs/references/notes/draft.md": "# No index: not listed\n",
        "docs/explanation/reasoning.md": "# Reasoning\n", "docs/explanation/zz-topic.md": "# Z\n",
        "docs/explanation/aaa-topic.md": "# A\n", "docs/explanation/risks.md": "# R\n",
        "docs/explanation/runtime.md": "# R\n",
        "docs/decisions/0001-x.md": DECISION.format(status="proposed", date="2026-10-07", more=""),
        "docs/skills/do-it/SKILL.md": SKILL,
        "a/docs/explanation/context.md": "# Context of a\n\n### [demo](../../../README.md)\n\nx, so y.\n",
        "a/docs/decisions/0001-x.md": DECISION.format(status="proposed", date="2026-10-07", more="")}))
    found = runner.findings(folder)
    check(found == ["error G1 AGENTS.md", "error G1 a/docs/decisions/index.md", "error G1 docs/decisions/index.md",
                    "error G1 docs/diagrams/component.md"], f"before --fix: {found}")
    data, done = runner.json("check", "--fix", "--json", str(folder))
    check(done.returncode == 0 and data["ok"] and "AGENTS.md" in data["summary"]["fixed"]["written"]
          and not (folder / "a/AGENTS.md").exists() and not (folder / "b/AGENTS.md").exists(),
          f"--fix writes the root AGENTS.md and no other: {data['summary']}")
    root = (folder / "AGENTS.md").read_text()
    check(root.startswith(EXPECTED_AGENTS_ROOT) and root.endswith("<!-- unifold:end -->\n")
          and "| a | `a` | A part |" in root, f"the root AGENTS.md:\n{root}")
    check("[README.md](../../README.md)" in (folder / "a/docs/decisions/index.md").read_text()
          and "AGENTS.md" not in (folder / "a/docs/decisions/index.md").read_text(),
          "the decision index of a unit below the root links its README.md only")
    data, _ = runner.json("show", "--json", str(folder))
    check(data["documents"]["references"] == ["docs/references/api/index.md", "docs/references/events.md"],
          f"show lists the documents by kind: {data['documents']}")
    for i in range(13):
        (folder / f"docs/tutorials/t{i:02}.md").write_text(f"# {i}\n")
    runner.run("check", "--fix", str(folder))
    check("| Learn | 14 files in docs/tutorials/ |" in (folder / "AGENTS.md").read_text(),
          "more than 12 files of a kind are counted")
    # a hand-written AGENTS.md at the root is reported and never overwritten
    hand = AGENTS.format(name="demo")
    (folder / "AGENTS.md").write_text(hand)
    data, done = runner.json("check", "--fix", "--json", str(folder))
    g1 = [f for f in data["findings"] if f["rule"] == "G1"]
    check(done.returncode == 1 and len(g1) == 1 and g1[0]["file"] == "AGENTS.md"
          and g1[0]["fix"] == AGENTS_FIX and data["summary"]["fixed"]["refused"] == ["AGENTS.md"]
          and (folder / "AGENTS.md").read_text() == hand, f"hand-written AGENTS.md: {data}")
    (folder / "AGENTS.md").write_text(MARK + "\n# AGENTS.md: old\n")
    data, _ = runner.json("check", "--json", str(folder))
    g1 = [f for f in data["findings"] if f["rule"] == "G1"]
    check(len(g1) == 1 and g1[0]["fix"] != AGENTS_FIX and "out of date" in g1[0]["message"],
          f"a stale generated AGENTS.md gets the normal G1 fix: {g1}")


def scenario_init(runner: Runner, tmp: str):
    """`init` writes the root manifest, a README.md from the template and the generated files:
    it reads no build file and drafts no unit."""
    files = {"Cargo.toml": '[workspace]\nmembers = ["crates/core", "crates/cli"]\n',
             "crates/core/Cargo.toml": '[package]\nname = "core"\nversion = "0.1.0"\n',
             "crates/cli/Cargo.toml": '[package]\nname = "cli"\nversion = "0.1.0"\n\n'
                                      '[dependencies]\ncore = { path = "../core" }\n',
             "crates/core/src/lib.rs": "// code\n", "crates/cli/src/main.rs": "fn main() {}\n"}
    folder = new_project(tmp, files)
    data, done = runner.json("init", "--json", str(folder))
    check(done.returncode == 0 and data["ok"] and data["units"] == 1
          and data["written"] == ["unifold.yaml", "README.md", "AGENTS.md"], f"init: {done.stderr} {data}")
    template = README_TEMPLATE.read_text(encoding="utf-8")
    check((folder / "README.md").read_text() == template.replace("<folder-name>", "demo", 1),
          "the README.md that init writes is the template of the skill, with the name filled in")
    check(not (folder / "crates/core/unifold.yaml").exists()
          and not (folder / "crates/cli/unifold.yaml").exists(), "init writes no manifest below the root")
    root = (folder / "unifold.yaml").read_text()
    check('unifold: "0.4"' in root and "\nname: demo\n" in root and "responsibility: TODO" in root
          and "https://unifold.md/0.4/unifold.schema.json" in root,
          f"root manifest: {root}")
    check(runner.findings(folder) == ["warn M10 unifold.yaml", "warn T9 README.md"],
          f"after init: the TODO and the template README are reported: {runner.findings(folder)}")
    (folder / "AGENTS.md").write_text("# Notes\n")
    data, done = runner.json("init", "--json", str(folder))
    check(done.returncode == 0 and (folder / "AGENTS.md").read_text() == "# Notes\n"
          and any("kept the hand-written AGENTS.md" in n for n in data["notes"]),
          f"init without a terminal keeps a hand-written AGENTS.md and says so: {data}")
    (folder / "AGENTS.md").unlink()
    again = runner.run("init", str(folder))
    check(again.returncode == 0 and (folder / "unifold.yaml").read_text() == root
          and "kept" in again.stdout and "unifold-convert" in again.stdout,
          f"init twice keeps the manifest and names the skill: {again.stdout}")
    empty = Path(tmp) / "none"
    data, done = runner.json("init", "--json", str(empty))
    check(done.returncode == 0 and data["units"] == 1
          and data["written"] == ["unifold.yaml", "README.md", "AGENTS.md"]
          and "\nname: none\n" in (empty / "unifold.yaml").read_text(),
          f"init in an empty folder writes the root manifest, README.md and AGENTS.md: {data}")
    check(runner.findings(empty) == ["warn M10 unifold.yaml", "warn T9 README.md"], "the new root manifest says TODO")
    (folder / "crates/core/unifold.yaml").write_text(UNIT)
    done = runner.run("init", str(folder / "crates/core"))
    check(done.returncode == 2 and "no key 'unifold'" in done.stderr,
          f"init on a unit that is not a root: {done.returncode} {done.stderr}")


def scenario_capability_hint(runner: Runner, tmp: str):
    """`capability` prints the summary and the contract of each end, and nothing from README.md."""
    folder = new_project(tmp, project("", {"b": CAPABILITY_X}))
    runner.run("check", "--fix", str(folder))
    done = runner.run("capability", str(folder / "b"), "x")
    check(done.returncode == 0 and "Offers x" in done.stdout and "contract: docs/references/x.md" in done.stdout
          and "README" not in done.stdout, f"capability: {done.stdout}")


def scenario_agents(runner: Runner, tmp: str):
    folder = new_project(tmp, project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "a/docs/skills/release/SKILL.md": "---\nname: release\ndescription: Release a.\n---\n# Release\n",
        "CLAUDE.md": "# Notes\n"}))
    done = runner.run("init", "--agents", str(folder))
    check(done.returncode == 0 and "@AGENTS.md" in done.stdout, f"init --agents: {done.stdout}{done.stderr}")
    check((folder / "docs/skills/unifold/SKILL.md").is_file()
          and (folder / "docs/skills/unifold/scripts/unifold.py").is_file(), "the skill is installed")
    check((folder / "docs/skills/unifold-convert/SKILL.md").is_file(), "the convert skill is installed")
    agents = (folder / "AGENTS.md").read_text()
    check("<!-- unifold:begin" in agents and "<!-- unifold:end -->" in agents
          and "| a | `a` | A part |" in agents and " show " in agents and " check" in agents
          and " capability " in agents and "unifold-convert" in agents, f"AGENTS.md block: {agents}")
    for base in (".agents/skills", ".claude/skills"):
        stub = folder / base / "a-release" / "SKILL.md"
        check(stub.is_file() and "name: a-release" in stub.read_text()
              and "a/docs/skills/release/SKILL.md" in stub.read_text(), f"stub in {base}")
        check((folder / base / "unifold" / "SKILL.md").is_file(), f"stub of the unifold skill in {base}")
        check((folder / base / "unifold-convert" / "SKILL.md").is_file(), f"stub of the convert skill in {base}")
    check(runner.findings(folder) == [], f"clean after init --agents: {runner.findings(folder)}")
    (folder / "c").mkdir()
    (folder / "c/unifold.yaml").write_text(UNIT)
    (folder / "c/README.md").write_text(README.format(name="c"))
    (folder / "a/docs/skills/release/SKILL.md").write_text(
        "---\nname: release\ndescription: Release a, carefully.\n---\n# Release\n")
    found = runner.findings(folder)
    check(found == ["error G1 .agents/skills/a-release/SKILL.md",
                    "error G1 .claude/skills/a-release/SKILL.md", "error G1 AGENTS.md",
                    "error G1 docs/diagrams/component.md"], f"stale stubs and unit index: {found}")
    data, _ = runner.json("check", "--fix", "--json", str(folder))
    check(len([p for p in data["summary"]["fixed"]["written"] if "a-release" in p]) == 2,
          f"check --fix writes the stubs: {data['summary']}")
    check(runner.findings(folder) == [], "clean after check --fix")
    rows, _ = runner.json("skills", "--json", str(folder))
    check({r["name"] for r in rows} == {"unifold", "unifold-convert", "release"}, f"skills: {rows}")


def scenario_stub_names(runner: Runner, tmp: str):
    def skill(name):
        return f"---\nname: {name}\ndescription: Do {name}.\n---\n# {name}\n"
    folder = new_project(tmp, project("", {"a": "", "x/a": "", "b": ""}, {
        "docs/skills/unifold/SKILL.md": skill("unifold"),
        "docs/skills/a-release/SKILL.md": skill("a-release"),
        "a/docs/skills/release/SKILL.md": skill("release"),
        "x/a/docs/skills/release/SKILL.md": skill("release"),
        "b/docs/skills/b-deploy/SKILL.md": skill("b-deploy"),
        "b/docs/skills/test/SKILL.md": skill("test")}))
    for base in (".agents/skills", ".claude/skills"):
        (folder / base).mkdir(parents=True)
    data, done = runner.json("check", "--fix", "--json", str(folder))
    check(done.returncode == 0, f"check --fix writes the stubs where their folders exist: {data}")
    for base in (".agents/skills", ".claude/skills"):
        names = sorted(p.name for p in (folder / base).iterdir())
        check(names == ["a-release", "a-release-2", "b-deploy", "b-test", "unifold", "x-a-release"],
              f"a root skill keeps its name, others are <unit>-<skill>, a clash takes the path: {names}")
        for name in names:
            text = (folder / base / name / "SKILL.md").read_text()
            check(f"name: {name}\n" in text, f"the stub {name} carries its own name: {text}")
        check("x/a/docs/skills/release/SKILL.md" in (folder / base / "x-a-release/SKILL.md").read_text()
              and "(../../../docs/skills/a-release/SKILL.md)" in
              (folder / base / "a-release/SKILL.md").read_text(), "stubs point at their sources")
    check(runner.findings(folder) == [], f"clean after check --fix: {runner.findings(folder)}")


def scenario_explore(runner: Runner, tmp: str):
    folder = new_project(tmp, project("wiring:\n  a.x: b.x\n",
                                   {"a": NEEDS_X, "b": CAPABILITY_X + "status: planned\n"}))
    out = Path(tmp) / "site" / "map.html"
    done = runner.run("explore", "--no-open", str(folder), "-o", str(out))
    check(done.returncode == 0 and out.is_file(), f"explore: {done.stderr}")
    html = out.read_text()
    check('"status": "planned"' in html and '"x"' in html and "cdn.jsdelivr.net" in html,
          "the page holds the model, its connections and status")
    dark = re.findall(r":root(?:\[data-theme=dark\]|:not\(\[data-theme=light\]\))\{(.*?)\}", html, re.S)
    check(len(dark) == 2 and dark[0] == dark[1], "the dark colours are the same for the button and for the system")
    fake = Path(tmp) / "mermaid.min.js"
    fake.write_text("window.mermaid = {initialize(){}, render: async () => ({svg: '<svg></svg>'})};\n")
    done = runner.run("explore", "--no-open", str(folder), "-o", str(out.parent), "--mermaid", str(fake))
    html = (out.parent / "explorer.html").read_text()
    check(done.returncode == 0 and "window.mermaid = {initialize" in html
          and "cdn.jsdelivr.net" not in html, "--mermaid FILE embeds the renderer; -o takes a folder")
    done = runner.run("explore", "--no-open", str(folder), "--mermaid", str(Path(tmp) / "missing.js"))
    check(done.returncode == 2, "--mermaid with a missing file")
    temp = Path(tmp) / "temp"
    temp.mkdir()
    done = runner.run("explore", "--no-open", "--json", str(folder), env={"TMPDIR": str(temp), "TEMP": str(temp), "TMP": str(temp)})
    data = json.loads(done.stdout)
    written = Path(data["written"])
    check(done.returncode == 0 and written.is_file() and data["opened"] is False
          and written.name == "explorer.html" and temp in written.parents and folder not in written.parents,
          f"without -o the explorer is written outside the project, under the temporary folder: {done.stdout}")
    check(not (folder / "unifold.html").exists() and not (folder / "explorer.html").exists(),
          "explore writes nothing into the project")


def scenario_explore_scenarios(runner: Runner, tmp: str):
    # b, outside the open calls, raises done into a, which is busy with serve: the event lands on the bar of serve; a calls b.do
    # (command, nothing inside: no bar, the result on the arrow); a asks b.ask (query); b raises done from inside ask: ask has
    # returned, and so has serve, which waited for it and does nothing more; the event then reaches an idle a and draws no bar,
    # because nothing follows inside it
    hops = "      - b -> a.done: ok\n      - a -> b.do: ok\n      - a -> b.ask: ok\n      - b -> a.done: ok\n"
    folder = new_project(tmp, project(SCENARIO_ROOT.replace("expect: e", "expect: one; two").replace("      - a -> b.do: ok\n", hops),
                                      SCENARIO_UNITS, contracts={"api": ["serve"], "x": [("do", "command"), ("done", "event"), "ask"]}))
    runner.run("check", "--fix", str(folder))
    page = runner.run("scenario", str(folder), "s1").stdout
    check("Expect: one#59; two" in page and "wrap:" in page, "a `;` in a sequence diagram is written #59;")
    check("  papi->>pa: 1 · serve\n  activate pa\n  pb-)pa: 2 · done → ok\n  pa->>pb: 3 · do → ok\n"
          "  pa->>pb: 4 · ask\n  pb-->>pa: ↩ 4 · ok\n  pa-->>papi: ↩ 1 · ok\n  deactivate pa\n"
          "  pb-)pa: 5 · done → ok\n  Note over" in page,
          f"an event from outside lands on the open bar, an event ends the call its raiser handled, a query answers, "
          f"a bare command carries its result, a call with steps inside returns with a dashed arrow:\n{page}")
    check_mermaid(page)
    check("| # | Caller | Target | Call | Kind | Result | State | Contract |" in page
          and "| 2 | `b` | `a` | `done` | event | ok |" in page, "the table has the kind and the result of the part")
    out = Path(tmp) / "map.html"
    done = runner.run("explore", "--no-open", str(folder), "-o", str(out))
    check(done.returncode == 0, f"explore: {done.stderr}")
    model = json.loads(re.search(r"const model = (.*?);\nconst MERMAID", out.read_text(), re.S).group(1))
    scenario = (model.get("scenarios") or [{}])[0]
    lifelines = scenario.get("diagram", {}).get("lifelines", {})
    check(scenario.get("unit") == "." and scenario.get("name") == "s1" and len(scenario.get("hops", [])) == 5
          and "\nsequenceDiagram\n" in "\n" + scenario["diagram"]["source"], "the page holds every scenario")
    check(re.search(r"^  participant \S+ as a$", scenario["diagram"]["source"], re.M) is not None
          and "mirrorActors: false" in scenario["diagram"]["source"], "a lifeline shows its name and kind, once")
    check("| Lifeline | Kind | What it does |" in page and "| `a` |  | A part |" in page, f"the page says what a lifeline does:\n{page}")
    check({"name": "api", "unit": ".", "side": "capability", "entry": "api"} in lifelines.values()
          and {"name": "b", "unit": "b"} in lifelines.values(), "a lifeline names its unit, or the side of the holder")


FRAMES_JS = r"""// the frame frameOf() of the page picks for every scenario of the model, and for the scenarios argv[3] adds: `name<TAB>frame`
const fs = require("node:fs"), html = fs.readFileSync(process.argv[2], "utf8");
const model = JSON.parse(html.match(/\nconst model = (.*?);\nconst MERMAID/s)[1]);
const units = model.units, byPath = Object.fromEntries(units.map(u => [u.path, u]));
const frameOf = new Function("byPath", html.match(/\nfunction frameOf\(s\)\{.*?\n\}\n/s)[0] + "\nreturn frameOf;")(byPath);
for (const s of model.scenarios.concat(JSON.parse(process.argv[3] || "[]"))) console.log(s.name + "\t" + frameOf(s));
"""


def frames_of(tmp: str, page: Path, extra: list | None = None) -> dict:
    """What the explorer picks as the map of each scenario: {name: frame or None}, computed by the page's own frameOf()."""
    node = shutil.which("node")
    check(node is not None, "node is needed: the frame of a scenario is chosen by the script of the page")
    script = Path(tmp) / "frames.js"
    script.write_text(FRAMES_JS)
    done = subprocess.run([node, str(script), str(page), json.dumps(extra or [])], capture_output=True, text=True)
    check(done.returncode == 0, f"frameOf() in the page: {done.stderr}")
    return {name: None if frame == "null" else frame for name, frame in (line.split("\t") for line in done.stdout.splitlines())}


def scenario_explore_frames(runner: Runner, tmp: str):
    """The map tab of a scenario shows the deepest unit whose component diagram holds every unit of its hops, also when the
    folder the units share is plain (`src`, `lib`): a plain folder belongs to the nearest unit above it."""
    contract = lambda name: f"{{summary: s, contract: ref:{name}}}"
    root = ("capabilities:\n  api: " + contract("api") + "\nwiring:\n  api: src/session.api\n  src/session.x: src/runtime.x\n  src/runtime.y: src/serial.y\n"
            "scenarios:\n"
            "  plain:\n    summary: s\n    hops:\n      - api -> src/session.serve: ok\n      - src/session -> src/runtime.do: ok\n      - src/runtime -> src/serial.go: ok\n    expect: e\n"
            "  nested:\n    summary: s\n    hops:\n      - lib/platform/a -> lib/platform/b.run: ok\n    expect: e\n"
            "  root:\n    summary: s\n    hops:\n      - api -> src/session.serve: ok\n    expect: e\n")
    units = {"src/session": "needs:\n  x: " + contract("x") + "\ncapabilities:\n  api: " + contract("api") + "\n",
             "src/runtime": "needs:\n  y: " + contract("y") + "\ncapabilities:\n  x: " + contract("x") + "\n",
             "src/serial": "capabilities:\n  y: " + contract("y") + "\n",
             "lib/platform": "kind: stateful\nwiring:\n  a.z: b.z\nscenarios:\n  inside:\n    summary: s\n    hops:\n      - a -> b.run: ok\n    expect: e\n",
             "lib/platform/a": "needs:\n  z: " + contract("z") + "\n", "lib/platform/b": "capabilities:\n  z: " + contract("z") + "\n"}
    folder = new_project(tmp, project(root, units, contracts={"api": ["serve"], "x": ["do"], "y": ["go"], "z": ["run"]}))
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"the fixture is clean: {runner.findings(folder)}")
    out = Path(tmp) / "map.html"
    done = runner.run("explore", "--no-open", str(folder), "-o", str(out))
    check(done.returncode == 0, f"explore: {done.stderr}")
    model = json.loads(re.search(r"const model = (.*?);\nconst MERMAID", out.read_text(), re.S).group(1))
    paths = {u["path"]: u for u in model["units"]}
    check("src" not in paths and "lib" not in paths and paths["src/serial"]["parent"]["path"] == "."
          and paths["lib/platform/a"]["parent"]["path"] == "lib/platform" and "component" in paths["lib/platform"]["diagrams"],
          f"src and lib are plain folders; the parent is the nearest unit above: {sorted(paths)}")
    frames = frames_of(tmp, out, [{"name": "none", "unit": "src/serial", "hops": []}])
    check(frames == {"plain": ".", "nested": "lib/platform", "root": ".", "inside": "lib/platform", "none": "."},
          f"the frame of a scenario is the deepest unit with a map of every unit in it, plain folders skipped: {frames}")
    lone = new_project(str(Path(tmp) / "lone"), project(""))
    done = runner.run("explore", "--no-open", str(lone), "-o", str(Path(tmp) / "lone.html"))
    check(done.returncode == 0, f"explore: {done.stderr}")
    frames = frames_of(tmp, Path(tmp) / "lone.html", [{"name": "alone", "unit": ".", "hops": []}])
    check(frames == {"alone": None}, f"without a map of children there is no frame, and the sequence view stays: {frames}")


def scenario_explore_documents(runner: Runner, tmp: str):
    notes = "\n".join([
        "# Notes", "", "Text with *em*, **strong**, `a <b> code` and <script>alert(1)</script> <img src=x onerror=alert(1)>.",
        "A [bad](javascript:alert(1)) link, [x](../../b/README.md#why), [up](#table), [file](../../logo.png), "
        "[web](https://example.com/a?b=1&c=2) and [map](../diagrams/component.md).", "",
        "## Table", "", "| A | B \\| C |", "|---|--:|", "| `x` | [x](x.md) |", "",
        "- one", "  - nested", "- [x] done", "", "1. first", "2. second", "",
        "> quoted", "", "---", "", FENCE + "yaml", "a: <b>&</b>", FENCE, "", FENCE + "mermaid", "flowchart LR", "  a --> b", FENCE, "",
        "Kind: query", "Pre: none.", "Result: one.", ""])
    folder = new_project(tmp, project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, files={
        "README.md": "# demo\n\nWhat it is for, see [notes](docs/references/notes.md).\n\nMore.\n\n## Why\n\nBecause *so*.\n\n- one\n\n## Other\n\nRest.\n",
        "b/README.md": "# Not b\n\n- a list first\n\nThe [first](#other) paragraph.\n",
        "docs/references/notes.md": notes,
        "docs/references/api/index.md": "# API\n\n## Parts\n\n- [get](get.md)\n",
        "docs/references/api/get.md": "# get\n\nKind: query\n",
        "docs/skills/do-it/SKILL.md": SKILL + "\nSteps.\n",
        **with_decision("proposed", "decision-makers: [Ann]\n")}))
    runner.run("check", "--fix", str(folder))
    out = Path(tmp) / "map.html"
    done = runner.run("explore", "--no-open", str(folder), "-o", str(out))
    check(done.returncode == 0, f"explore: {done.stderr}")
    model = json.loads(re.search(r"const model = (.*?);\nconst MERMAID", out.read_text(), re.S).group(1))
    docs = model.get("docs") or {}
    root, b, page = docs.get("README.md", {}), docs.get("b/README.md", {}), docs.get("docs/references/notes.md", {})
    check(root.get("kind") == "readme" and root.get("title") == "demo" and "<h1" not in root.get("html", "")
          and root.get("intro") == 'What it is for, see <a href="#.@doc:docs/references/notes.md">notes</a>.'
          and root.get("why") == '<h2 id="md-why">Why</h2>\n<p>Because <em>so</em>.</p>\n<ul><li>one</li></ul>'
          and "Rest." in root.get("html", ""), f"a README: its first paragraph, its Why, and the whole text for its own page: {root}")
    check(b.get("title") == "Not b" and b.get("intro") == 'The <a href="#b@doc:README.md#other">first</a> paragraph.' and "why" not in b,
          f"the first paragraph of a README need not come first; a README without Why has none: {b}")
    source = next(u for u in model["units"] if u["path"] == "b")["diagrams"]["context"]["source"]
    check("<span class='note'>A part</span>" in source, f"a box of the map shows the responsibility of its unit: {source}")
    check("note" not in (folder / "docs" / "diagrams" / "component.md").read_text(), "the generated diagrams do not")
    html = page.get("html", "")
    check(page.get("unit") == "." and page.get("kind") == "references" and page.get("title") == "Notes", f"a document has its unit, kind and title: {page}")
    check("<script" not in html and "<img" not in html and "&lt;script&gt;alert(1)&lt;/script&gt;" in html
          and "<code>a &lt;b&gt; code</code>" in html and "javascript:" not in html and "<em>em</em>" in html
          and "<strong>strong</strong>" in html, "all HTML of a document is escaped; a javascript: link is text")
    check('<a href="#b#why">x</a>' in html and '<a href="#.@doc:docs/references/notes.md#table">up</a>' in html
          and 'logo.png">file</a>' in html and 'href="https://example.com/a?b=1&amp;c=2"' in html
          and '<a href="#.@component">map</a>' in html,
          "links open the unit, the document and its heading, the diagram tab, the file, or the web")
    check('<h2 id="md-table">Table</h2>' in html and '<th class="r">B | C</th>' in html
          and '<td><code>x</code></td>' in html, f"a table, with alignment and an escaped pipe: {html[:2000]}")
    check("<ul><li>one\n<ul><li>nested</li></ul></li><li class=task><input type=\"checkbox\" disabled checked> done</li></ul>" in html
          and "<ol><li>first</li><li>second</li></ol>" in html and "<blockquote><p>quoted</p></blockquote>" in html and "<hr>" in html,
          "lists, nested and with tasks, a quote and a rule")
    check('<pre><code class="language-yaml">a: &lt;b&gt;&amp;&lt;/b&gt;</code></pre>' in html
          and '<pre class="mermaid">flowchart LR\n  a --&gt; b</pre>' in html, "fenced code is escaped; a Mermaid block is kept for drawing")
    check('<p class=field><strong>Kind:</strong> query</p>' in html and '<p class=field><strong>Result:</strong> one.</p>' in html,
          "the fields of a part are one to a line")
    index, part = docs.get("docs/references/api/index.md", {}), docs.get("docs/references/api/get.md", {})
    check(index.get("parts") == ["docs/references/api/get.md"] and part.get("contract") == "docs/references/api/index.md"
          and 'href="#.@doc:docs/references/api/get.md"' in index.get("html", ""), "a folder contract: its index and its parts")
    decision, skill = docs.get("docs/decisions/0001-x.md", {}), docs.get("docs/skills/do-it/SKILL.md", {})
    check(decision.get("kind") == "decisions" and decision.get("status") == "proposed"
          and ["status", '<span class="badge proposed">proposed</span>'] in decision.get("facts", [])
          and ["decision makers", "Ann"] in decision.get("facts", []) and "---" not in decision.get("html", ""),
          f"a decision has its status and its front matter as fields: {decision}")
    check(skill.get("summary") == "Does it." and ["name", "do-it"] in skill.get("facts", []) and skill.get("title") == "Do it",
          f"a skill: its description and its front matter: {skill}")
    check("docs/diagrams/component.md" not in docs and "docs/decisions/index.md" in docs and "AGENTS.md" in docs,
          "generated diagrams are drawn by the page, not shown as documents")
    shown, _ = runner.json("show", "--json", str(folder))
    check("docs" not in shown and "html" not in json.dumps(shown), "`show --json` has no rendered documents")


def scenario_lifeline_order(runner: Runner, tmp: str):
    """A lifeline stands right after the ones introduced through the same partner: d, introduced by b, comes before c."""
    root = ("capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.x: b.x\n  a.y: c.y\n  b.z: d.z\n"
            "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a -> b.do: ok\n      - a -> c.go: ok\n      - b -> d.run: ok\n    expect: e\n")
    units = {"a": "needs:\n  x: {summary: s, contract: ref:x}\n  y: {summary: s, contract: ref:y}\ncapabilities:\n  api: {summary: s, contract: ref:api}\n",
             "b": "needs:\n  z: {summary: s, contract: ref:z}\ncapabilities:\n  x: {summary: s, contract: ref:x}\n",
             "c": "capabilities:\n  y: {summary: s, contract: ref:y}\n", "d": "capabilities:\n  z: {summary: s, contract: ref:z}\n"}
    folder = new_project(tmp, project(root, units, contracts={"api": ["serve"], "x": ["do"], "y": ["go"], "z": ["run"]}))
    runner.run("check", "--fix", str(folder))
    page = runner.run("scenario", str(folder), "s1").stdout
    check_mermaid(page)
    order = re.findall(r"^  participant (\S+)", page, re.M)
    check(order == ["papi", "pa", "pb", "pd", "pc"], f"lifelines by first partner, depth first: {order}")


def scenario_unit_labels(runner: Runner, tmp: str):
    """A box says what a unit states of its kind and runs-as: both, either one, or nothing."""
    root = ("capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.x: b.x\n  a.y: c.y\n  b.z: d.z\n"
            "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a -> b.do: ok\n      - a -> c.go: ok\n      - b -> d.run: ok\n    expect: e\n")
    units = {"a": "kind: stateful\nruns-as: process\nneeds:\n  x: {summary: s, contract: ref:x}\n  y: {summary: s, contract: ref:y}\ncapabilities:\n  api: {summary: s, contract: ref:api}\n",
             "b": "runs-as: job\nneeds:\n  z: {summary: s, contract: ref:z}\ncapabilities:\n  x: {summary: s, contract: ref:x}\n",
             "c": "kind: logic\ncapabilities:\n  y: {summary: s, contract: ref:y}\n", "d": "capabilities:\n  z: {summary: s, contract: ref:z}\n"}
    folder = new_project(tmp, project(root, units, contracts={"api": ["serve"], "x": ["do"], "y": ["go"], "z": ["run"]}))
    runner.run("check", "--fix", str(folder))
    page = runner.run("scenario", str(folder), "s1").stdout
    check_mermaid(page)
    boxes = dict(re.findall(r"^  participant p(\S+) as (.+)$", page, re.M))
    check(boxes == {"api": "api", "a": "a<br/>«stateful, process»", "b": "b<br/>«job»", "c": "c<br/>«logic»", "d": "d"},
          f"the lifelines of a scenario: {boxes}")
    component = (folder / "docs" / "diagrams" / "component.md").read_text(encoding="utf-8")
    for box in ('"a (stateful, process)"', '"b (job)"', '"c (logic)"', '"d"'):
        check(box in component, f"the component diagram has the box {box}")


def scenario_robustness(runner: Runner, tmp: str):
    files = project("wiring:\n" + "".join(f"  u{i}.x: u{(i + 1) % 1200}.x\n" for i in range(1200)),
                    {f"u{i}": NEEDS_X + CAPABILITY_X for i in range(1200)})
    folder = new_project(tmp, files)
    runner.run("check", "--fix", str(folder))
    found = runner.findings(folder)
    check(found == ["warn W7 unifold.yaml"], f"a cycle through 1200 siblings: {found[:5]}")
    deep = Path(tmp) / "deep" / "demo"
    write_files(deep, {"unifold.yaml": ROOT, "README.md": README.format(name="demo"), **{
        "/".join(["d"] * n) + "/unifold.yaml": COMPOSITE if n < 39 else UNIT for n in range(1, 40)}, **{
        "/".join(["d"] * n) + "/README.md": README.format(name="d") for n in range(1, 40)}})
    runner.run("check", "--fix", str(deep))
    check(runner.findings(deep) == [], "39 levels deep")
    odd = Path(tmp) / "odd" / "demo"
    write_files(odd, project(files={"docs/x.md/keep.txt": "a folder named like a file\n",
                                 "docs/references/utf16.md": "x"}))
    (odd / "docs/references/utf16.md").write_bytes("# T\n".encode("utf-16"))
    runner.run("check", "--fix", str(odd))
    done = runner.run("check", "--json", str(odd))
    check(done.returncode in (0, 1) and json.loads(done.stdout), "odd files do not crash check")
    for command in (["show", str(odd / "missing")], ["init", str(odd / "unifold.yaml")],
                    ["rules", "ZZ"], ["capability", str(odd), "nothing"]):
        done = runner.run(*command)
        check(done.returncode == 2 and "Traceback" not in done.stderr and done.stderr.strip(),
              f"{command[0]}: exit {done.returncode}, {done.stderr[:200]}")
    crlf = Path(tmp) / "crlf" / "demo"
    write_files(crlf, {k: v.replace("\n", "\r\n") for k, v in
                       project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}).items()})
    runner.run("check", "--fix", str(crlf))
    check(runner.findings(crlf) == [], "CRLF line ends")
    sub = runner.run("check", "--json", cwd=str(crlf / "a"))
    check(json.loads(sub.stdout)["summary"]["units"] == 3, "run from a folder below the root")


def scenario_gitignore(runner: Runner, tmp: str):
    """What git ignores is not part of the project: no unit, no document."""
    if shutil.which("git") is None:
        return
    folder = new_project(tmp, project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        ".gitignore": "build/\na/docs/references/generated.md\nscratch.md\n",
        "build/x/unifold.yaml": UNIT, "build/x/README.md": README.format(name="x"),
        "a/docs/references/generated.md": "# Generated\n\n[gone](nowhere.md)\n",
        "a/docs/references/kept.md": "# Kept\n",
        "docs/scratch.md": "# Scratch\n"}))
    done = subprocess.run(["git", "init", "-q", str(folder)], capture_output=True, text=True)
    check(done.returncode == 0, f"git init: {done.stderr}")
    runner.run("check", "--fix", str(folder))
    found = runner.findings(folder)
    check(found == [], f"ignored unit and document are not seen: {found}")
    rows, _ = runner.json("tree", "--json", str(folder))
    check([r["path"] for r in rows] == [".", "a", "b"], f"tree without the ignored unit: {rows}")
    data, _ = runner.json("show", "--json", str(folder / "a"))
    check("a/docs/references/kept.md" in data["files"]
          and "a/docs/references/generated.md" not in data["files"], f"show lists only kept files: {data['files']}")
    (folder / ".gitignore").unlink()
    found = runner.findings(folder)
    rows, _ = runner.json("tree", "--json", str(folder))
    check("error L1 a/docs/references/generated.md" in found and "error G1 AGENTS.md" in found
          and "build/x" in [r["path"] for r in rows] and "info S12 docs/scratch.md" in found,
          f"without .gitignore everything is seen: {found} {rows}")
    (folder / ".gitignore").write_text("build/\na/docs/references/generated.md\nscratch.md\ndocs/diagrams/\n")
    runner.run("check", "--fix", str(folder))
    found = runner.findings(folder)
    check(found == ["error G1 docs/diagrams/component.md"], f"an ignored generated file is reported: {found}")


def scenario_states(runner: Runner, tmp: str):
    folder = new_project(tmp, state_project())
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"clean: {runner.findings(folder)}")
    page = runner.run("states", str(folder), "x").stdout
    check(page.startswith("# States: x") and "stateDiagram-v2" in page and "[*] --> sclosed" in page
          and "sopen --> sclosed: send · lost" in page,
          f"a contract with states gets a state diagram:\n{page}")
    check("  sopen --> sclosed: send · lost" in page and "  sclosed: open · refused" in page and "  sopen: send · ok" in page
          and "  sclosed --> sopen: open · ok" in page,
          f"every row of the table is in the diagram: a move on an arrow, a stay in the box of the state:\n{page}")
    scenario = runner.run("scenario", str(folder), "s1").stdout
    check_mermaid(scenario)
    check("  Note over pb: x: closed\n  pa->>pb: 2 · open() → ok" in scenario and "  Note over pb: x: open\n" in scenario
          and "| 3 | `a` | `b` | `send([1])` | command | lost | closed |" in scenario,
          f"a hop shows its call and result, and a note the state:\n{scenario}")
    data, _ = runner.json("model", "--json", str(folder))
    hop = data["units"][0]["scenarios"][0]["hops"][2]
    check(hop["input"] == "[1]" and hop["result"] == "lost" and hop["state-before"] == "open" and hop["state"] == "closed",
          f"the model has input, result and states: {hop}")
    need = next(n for u in data["units"] if u["path"] == "a" for n in u["needs"] if n["name"] == "x")
    check(need["contract-states"]["start"] == "closed" and "contract-scenarios" not in need,
          f"the model has the states of a contract: {need['contract-states']}")
    loop = "      - api -> a.serve: ok\n      - repeat:\n          times: 2\n          hops:\n            - a -> b.open(): ok\n            - a -> b.send([1]): {}\n"
    folder = new_project(tmp, state_project(hops=loop.format("ok")))
    runner.run("check", "--fix", str(folder))
    found = runner.findings(folder)
    check(any(f.startswith("error N6") for f in found) and any("when the repeat runs again" in f for f in runner.run("check", str(folder)).stdout.splitlines()),
          f"the second round of a repeat opens an open line: {found}")
    folder = new_project(tmp, state_project(hops=loop.format("lost")))
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"a round that closes the line can follow itself: {runner.findings(folder)}")


def scenario_brief_and_trace(runner: Runner, tmp: str):
    """`brief` prints what to implement; `trace` finds the example ids in the files below a unit."""
    folder = new_project(tmp, project(WIRED, {"a": NEEDS_X, "b": CAPABILITY_X}, {
        "b/tests/do.txt": "proves x#do/one\n", "b/src/other.txt": "x#do/nine is nobody\n",
        "docs/references/constants.md": "# Constants\n\n| Name | Value |\n|---|---|\n| `MAX` | 3 |\n",
        "a/docs/explanation/context.md": "# Context of a\n\n### [demo](../../../README.md)\n\nx, so y.\n"},
        contracts={"x": ["do"]}))
    runner.run("check", "--fix", str(folder))
    data, done = runner.json("brief", "--json", str(folder / "b"))
    examples = data["capabilities"][0]["contract"]["parts"][0]["examples"]
    check(done.returncode == 0 and examples == [{"id": "x#do/one", "case": "one", "given": None, "input": "`do()`", "expected": "1"}]
          and data["constants"] == [{"name": "MAX", "value": "3", "file": "docs/references/constants.md"}], f"brief: {data}")
    text = runner.run("brief", str(folder / "b")).stdout
    check("implement" in text and "x#do/one" in text and "do: func() -> u32;" in text, f"brief text: {text}")
    data, _ = runner.json("brief", "--json", str(folder / "a"))
    check(data["needs"][0]["contract"]["parts"][0]["name"] == "do" and data["context"][0]["text"] == "x, so y."
          and data["needs"][0]["provided-by"] == [{"unit": "b", "capability": "x"}], f"brief of a consumer: {data}")
    data, done = runner.json("trace", "--json", str(folder / "b"))
    check(done.returncode == 1 and data["summary"] == {"examples": 1, "tested": 1, "untested": 0, "unknown": 1}
          and data["examples"][0]["tests"] == ["b/tests/do.txt"] and data["unknown"][0]["file"] == "b/src/other.txt",
          f"trace: {data}")
    data, done = runner.json("trace", "--json", "--tests", "tests/*", str(folder / "b"))
    check(done.returncode == 0 and data["summary"]["unknown"] == 0, f"trace --tests: {data}")
    (folder / "b/tests/do.txt").write_text("nothing\n")
    data, done = runner.json("trace", "--json", "--tests", "tests/*", str(folder / "b"))
    check(done.returncode == 0 and data["summary"]["untested"] == 1 and data["findings"][0]["rule"] == "X1", f"untested: {data}")
    done = runner.run("trace", "--strict", "--tests", "tests/*", str(folder / "b"))
    check(done.returncode == 1 and "none x#do/one" in done.stdout, f"trace --strict: {done.stdout}")


def scenario_views(runner: Runner, tmp: str):
    """`scenario` folds an included scenario into one step; `--expand` opens it; both are well formed."""
    folder = new_project(tmp, project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.x: b.x\n  a.z: c.z\n"
        "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - a.inner\n      - parallel:\n          - - a -> b.do: ok\n          - - a -> c.go: ok\n    expect: e\n",
        {"a": "needs:\n  x: {summary: s, contract: ref:x}\n  z: {summary: s, contract: ref:z}\ncapabilities:\n  api: {summary: s, contract: ref:api}\n"
              "scenarios:\n  inner:\n    summary: s\n    hops:\n      - api -> x.do: ok\n      - api -> z.go: ok\n    expect: e\n",
         "b": SCENARIO_UNITS["b"], "c": "capabilities:\n  z: {summary: s, contract: ref:z}\n"},
        contracts={**SCENARIO_CONTRACTS, "z": ["go"]}))
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"clean: {runner.findings(folder)}")
    short = runner.run("scenario", str(folder), "s1").stdout
    check_mermaid(short)
    check("  Note over pa: 2 · scenario a.inner (2 steps)\n" in short and "| 2 |  | `a` | scenario `a.inner` | include | 2 steps |" in short
          and "  par\n" in short and "  and\n" in short and short.count("\n  end\n") == 1 and "end\n  and" not in short,
          f"collapsed view: an include without a caller is a note, one end per par:\n{short}")
    full = runner.run("scenario", "--expand", str(folder), "s1").stdout
    check_mermaid(full)
    check("rect rgb" in full and "scenario a.inner" in full and "a -> b.do" not in full and "| 2 | `a` | `b` | `do` |" in full,
          f"expanded view: the included hops as a shaded block:\n{full}")


def scenario_include_inside_the_call(runner: Runner, tmp: str):
    """A collapsed include is an arrow from the caller of its first step, inside the call that is open."""
    folder = new_project(tmp, project(
        "capabilities:\n  api: {summary: s, contract: ref:api}\nwiring:\n  api: a.api\n  a.x: b.x\n"
        "scenarios:\n  s1:\n    summary: s\n    hops:\n      - api -> a.serve: ok\n      - b.inner\n    expect: e\n",
        {"a": SCENARIO_UNITS["a"], "b": "capabilities:\n  x: {summary: s, contract: ref:x}\nwiring:\n  x: c.x\n"
              "scenarios:\n  inner:\n    summary: s\n    hops:\n      - x -> c.do: ok\n    expect: e\n", "b/c": CAPABILITY_X},
        contracts=SCENARIO_CONTRACTS))
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"clean: {runner.findings(folder)}")
    page = runner.run("scenario", str(folder), "s1").stdout
    check_mermaid(page)
    check("  papi->>pa: 1 · serve\n  activate pa\n  pa->>pb: 2 · scenario b.inner (1 step)\n  pa-->>papi: ↩ 1 · ok\n  deactivate pa\n" in page
          and "| 2 | `a` | `b` | scenario `b.inner` | include | 1 step |" in page, f"the include runs inside the call:\n{page}")


def scenario_long_steps_wrap(runner: Runner, tmp: str):
    """A step wider than a line is wrapped at a space, never inside a word with a hyphen."""
    long = "the-first-word and a long text that goes on for a good while"
    folder = new_project(tmp, project(SCENARIO_ROOT.replace("      - a -> b.do: ok\n", f"      - a -> b.do({long}): ok\n"), SCENARIO_UNITS, contracts=SCENARIO_CONTRACTS))
    runner.run("check", "--fix", str(folder))
    page = runner.run("scenario", str(folder), "s1").stdout
    check_mermaid(page)
    drawn = next(line for line in page.splitlines() if "2 · do(" in line and "->>" in line)
    check("<br/>" in drawn and "the-first-word" in drawn and all(len(p) <= 60 for p in drawn.split("<br/>")[1:]), f"wrapped: {drawn}")


def scenario_model(runner: Runner, tmp: str):
    """`model --json` prints the resolved project."""
    files = project("needs:\n  clock: {summary: s, contract: ref:clock, platform: true}\n"
                    + SCENARIO_ROOT.replace("  a.x: b.x\n", "  a.x: b.x\n  a.clock: clock\n")
                                   .replace("      - a -> b.do: ok\n", "      - a -> b.do: ok\n      - a -> clock.now: ok\n"),
                    {"a": NEEDS_X + "  clock: {summary: s, contract: ref:clock}\n"
                          "capabilities:\n  api: {summary: s, contract: ref:api}\n"
                                              "not:\n  - y\nx-maike-group: g\n",
                                              "b": "kind: logic\n" + CAPABILITY_X},
                    {"a/docs/decisions/0001-x.md": DECISION.format(status="proposed", date="2026-10-07", more=""),
                     "docs/decisions/0001-q.md": DECISION.format(status="proposed", date="2026-10-07", more="") + "\n## Answer\n\n"},
                    contracts={**SCENARIO_CONTRACTS, "clock": ["now"]})
    folder = new_project(tmp, files)
    runner.run("check", "--fix", str(folder))
    check(runner.findings(folder) == [], f"clean: {runner.findings(folder)}")
    data, done = runner.json("model", "--json", str(folder))
    check(done.returncode == 0 and data["unifold-model"] == "0.4" and data["project"] == "demo", f"model: {data.keys()}")
    units = {u["path"]: u for u in data["units"]}
    check([u["path"] for u in data["units"]] == [".", "a", "b"], "units in order, the root first")
    a = units["a"]
    check("secret" not in a and a["not"] == ["y"]
          and a["x"] == {"x-maike-group": "g"} and a["kind"] is None, f"unit fields: {a['not']} {a['x']}")
    x = next(n for n in a["needs"] if n["name"] == "x")
    check(x["final-providers"] == [{"unit": "b", "capability": "x", "config": None}]
          and x["contract-parts"] == [{"name": "do", "kind": "query"}] and x["parts"] is None
          and x["fake"] == "described", f"need: {x}")
    clock = next(n for n in a["needs"] if n["name"] == "clock")
    check(clock["final-providers"] == [{"outside": True, "root-need": "clock", "config": None}], f"outside: {clock}")
    api = next(c for c in a["capabilities"] if c["name"] == "api")
    check(api["final-users"] == [{"outside": True, "root-capability": "api", "config": None}], f"users: {api}")
    root = units["."]
    forms = sorted(w["form"] for w in root["wiring"])
    check(forms == ["connection", "implemented-by", "passed-up"], f"wiring forms: {forms}")
    scenario = root["scenarios"][0]
    check(scenario["name"] == "s1" and scenario["hops"][0]["via"] == [{"unit": ".", "key": "api"}]
          and scenario["hops"][1] == {"caller": "a", "target": "b", "part": "do", "input": None, "result": "ok",
                                      "example": None, "direction": "call", "caller-side": "unit", "target-side": "unit",
                                      "part-kind": "query", "contract": "docs/references/x.md", "caller-unit": "a",
                                      "target-unit": "b", "via": [{"unit": ".", "key": "a.x"}],
                                      "state-before": None, "state": None, "groups": []}
          and scenario["given"] == []
          and scenario["hops"][2]["via"] == [{"unit": ".", "key": "a.clock"}], f"hops: {scenario['hops']}")
    check(data["root-needs"] == [{"name": "clock", "platform": True, "reached-by": ["a"]}], f"root needs: {data['root-needs']}")
    question = root["decisions"][0]
    check(question["answer"] == {"empty": True} and question["status"] == "proposed" and question["derived-from"] is None,
          f"decision: {question}")
    check(a["decisions"][0]["answer"] is None, "a decision without an Answer section")
    scenario_md = runner.run("scenario", str(folder), "s1").stdout
    check(scenario_md.startswith("# Scenario: s1") and "sequenceDiagram" in scenario_md and "| 2 | `a` | `b` | `do` |" in scenario_md
          and not (folder / "docs/diagrams/scenario-s1.md").exists(), f"scenario diagram: {scenario_md}")
    done = runner.run("scenario", str(folder), "nope")
    check(done.returncode == 2, "an unknown scenario fails")
    data, _ = runner.json("show", "--json", str(folder / "b"))
    check(data["responsibility"] == "A part" and data["kind"] == "logic" and data["scenarios"] == [
        {"unit": ".", "name": "s1", "summary": "s"}], f"show lists the scenarios through a unit: {data['scenarios']}")
    text = runner.run("show", str(folder / "a")).stdout
    check("secret" not in text and "not       y" in text and "scenario  s1" in text, f"show text: {text}")
    folder2 = new_project(tmp + "/inherit", project(NEEDS_X + "wiring:\n  a.x: x\n", {"a": "needs:\n  x:\n"}))
    runner.run("check", "--fix", str(folder2))
    data, _ = runner.json("show", "--json", str(folder2 / "a"))
    check(data["needs"]["x"]["summary"] == "Needs x" and data["needs"]["x"]["contract"] == "docs/references/x.md"
          and data["needs"]["x"]["inherited-from"] == "..x", f"an empty need takes summary and contract from above: {data['needs']}")
    text = runner.run("show", str(folder2 / "a")).stdout
    check("(from ..x)" in text, f"show marks an inherited entry: {text}")


SCENARIOS = [
    ("scenario-model", scenario_model),
    ("scenario-states", scenario_states),
    ("scenario-lifeline-order", scenario_lifeline_order),
    ("scenario-unit-labels", scenario_unit_labels),
    ("scenario-gitignore", scenario_gitignore),
    ("scenario-json-on-failure", scenario_json_on_failure),
    ("scenario-finding-shape-text-github-strict", scenario_finding_shape),
    ("scenario-generate-is-idempotent", scenario_generate_is_idempotent),
    ("scenario-show-capability-impact-tree", scenario_show_port_impact),
    ("scenario-citations-and-impact", scenario_citations),
    ("scenario-brief-and-trace", scenario_brief_and_trace),
    ("scenario-views", scenario_views),
    ("scenario-include-inside-the-call", scenario_include_inside_the_call),
    ("scenario-long-steps-wrap", scenario_long_steps_wrap),
    ("scenario-row-anchor", scenario_row_anchor),
    ("scenario-check-fix", scenario_check_fix),
    ("scenario-agents-generated", scenario_agents_generated),
    ("scenario-init-root-manifest-only", scenario_init),
    ("scenario-capability-hint", scenario_capability_hint),
    ("scenario-own-needs", scenario_own_needs),
    ("scenario-init-agents-and-skill-stubs", scenario_agents),
    ("scenario-skill-stub-names", scenario_stub_names),
    ("scenario-explore", scenario_explore),
    ("scenario-explore-scenarios", scenario_explore_scenarios),
    ("scenario-explore-frames", scenario_explore_frames),
    ("scenario-explore-documents", scenario_explore_documents),
    ("scenario-robustness", scenario_robustness),
]


def meta_rules(runner: Runner) -> str | None:
    """rules.md, the tool and the cases name the same rules."""
    table = {}
    for line in RULES_MD.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\| (?:<a id=\"[a-z0-9]+\"></a>)?`?([A-Z]\d+)`? \| (error|warn|info) \|", line)
        if match:
            table[match.group(1)] = match.group(2)
    if not table:
        return f"no rule table found in {RULES_MD}"
    try:
        listed, _ = runner.json("rules", "--json")
        tool = {r["id"]: r["severity"] for r in listed}
    except (AssertionError, KeyError, TypeError):
        tool = None                                   # another implementation need not have `rules`
    if tool is not None and tool != table:
        diff = sorted(set(tool.items()) ^ set(table.items()))
        return f"rules.md and `rules --json` differ: {diff}"
    failing = {e.split()[1] for case in CASES for e in case[2]}
    missing = sorted(set(table) - failing)
    if missing:
        return f"no failing case for: {', '.join(missing)}"
    unknown = sorted(failing - set(table))
    if unknown:
        return f"cases expect rules that rules.md does not define: {', '.join(unknown)}"
    wrong = sorted({e for case in CASES for e in case[2]
                    if table.get(e.split()[1], "") != e.split()[0]})
    if wrong:
        return f"cases expect a severity that rules.md does not give: {wrong}"
    return None


def main() -> int:
    args = sys.argv[1:]
    tool = [sys.executable, str(TOOL)]
    if "--tool" in args:
        index = args.index("--tool")
        tool = shlex.split(args[index + 1])
        del args[index:index + 2]
    if args[:1] == ["--list"]:
        print("\n".join([c[0] for c in CASES] + [s[0] for s in SCENARIOS] + ["meta-rules"]))
        return 0
    if args[:1] == ["--write"]:
        for case in CASES:
            name, files, expected = case[:3]
            options = case[3] if len(case) > 3 else {}
            folder = Path(args[1]) / name
            write_files(folder / "demo", files)
            (folder / "expected.txt").write_text("".join(e + "\n" for e in sorted(expected)))
            (folder / "run.json").write_text(json.dumps(
                {"fix": options.get("fix", True),
                 "check": ["check", "--json", *options.get("args", []), "demo"]}) + "\n")
        print(f"wrote {len(CASES)} cases to {args[1]}")
        return 0
    runner = Runner(tool)
    wanted = [a for a in args if not a.startswith("-")]
    tests = [(c[0], lambda c=c: run_case(runner, c)) for c in CASES]
    for name, function in SCENARIOS:
        def scenario(function=function):
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    function(runner, str(Path(tmp).resolve()))
                except AssertionError as exc:
                    return str(exc)
                except (KeyError, IndexError, TypeError, StopIteration, ValueError) as exc:
                    return f"unexpected output ({type(exc).__name__}: {exc})"
            return None
        tests.append((name, scenario))
    tests.append(("meta-rules", lambda: meta_rules(runner)))
    if wanted:
        tests = [t for t in tests if any(w in t[0] for w in wanted)]
    failed = 0
    for name, test in tests:
        problem = test()
        failed += bool(problem)
        if problem or "-v" in args:
            print(("FAIL " if problem else "ok   ") + name)
        if problem:
            print("     " + problem)
    print(f"{len(tests) - failed} of {len(tests)} tests pass "
          f"({len(CASES)} cases, {len(SCENARIOS)} scenarios, 1 meta test)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
