#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Conformance cases for unifold checkers.

Each case is a small project (a mapping of file path to content) and the
findings a checker must report for it, as "SEVERITY RULE file". The cases are
data, so that another implementation can be tested against them:

    python3 tests/conformance.py               run all cases against the reference tool
    python3 tests/conformance.py --write DIR   write every case to DIR/<name>/ with expected.txt
    python3 tests/conformance.py --tool CMD    test another checker; CMD gets: check --json PATH
                                               (and --deps PATH/deps.json if the case has that file)
"""
from __future__ import annotations

import json
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "doc/skills/check-docs/scripts/unifold.py"
MARK = "<!-- unifold:generated - do not edit; run `unifold generate` -->"


def readme(manifest: str, extra: str = "", sidecar: bool = False) -> str:
    name = manifest.split("unit:", 1)[1].split()[0]
    body = f"# {name}\n\nText.\n\n- [Diagram](doc/diagrams/context.md)\n{extra}"
    return body if sidecar else f"---\n{manifest.strip()}\n---\n{body}"


def agents(extra: str = "") -> str:
    return f"# AGENTS.md\n\n## Why\n\nBecause.\n{extra}"


def project(root_manifest: str = "", units: dict | None = None, files: dict | None = None,
            root_extra: str = "", sidecar: bool = False) -> dict:
    """A root unit with the files the standard requires, plus child units."""
    manifest = 'unit: demo\nunifold: "0.1"\nsummary: A demo\nstatus: planned\n' + root_manifest
    out = {
        "README.md": readme(manifest, root_extra, sidecar),
        "AGENTS.md": agents("\n[read-docs](doc/skills/read-docs/SKILL.md)\n"),
        "doc/skills/read-docs/SKILL.md":
            "---\nname: read-docs\ndescription: Read.\n---\n# Read\n\n"
            "[standard](../../references/unifold/index.md)\n",
        "doc/references/unifold/index.md": "# unifold\n",
    }
    if sidecar:
        out["unit.yaml"] = manifest
    for path, child_manifest in (units or {}).items():
        full = f"unit: {path.rsplit('/', 1)[-1]}\nsummary: A part\nstatus: planned\n" + child_manifest
        out[f"{path}/README.md"] = readme(full)
        out[f"{path}/AGENTS.md"] = agents()
    out.update(files or {})
    return {k: v for k, v in out.items() if v is not None}


A_NEEDS_X = "needs:\n  x: {kind: library, summary: Needs x}\n"
B_PROVIDES_X = "provides:\n  x: {kind: library, summary: Offers x}\n"
WIRED = "wiring:\n  a.x: b.x\n"
DECISION = "---\nstatus: {status}\ndate: 2026-10-07\n{more}---\n# A decision\n\nText.\n"

CASES = [
    ("single-unit", project(), []),
    ("root-manifest-in-unit-yaml", project(sidecar=True), []),
    ("two-units-wired", project(WIRED, {"a": A_NEEDS_X, "b": B_PROVIDES_X}), []),
    ("unit-in-plain-folder", project(WIRED, {"parts/a": A_NEEDS_X, "parts/b": B_PROVIDES_X}), []),
    ("need-not-wired", project("", {"a": A_NEEDS_X, "b": B_PROVIDES_X}),
     ["E W2 README.md", "W W3 README.md"]),
    ("optional-need-not-wired",
     project("", {"a": "needs:\n  x: {kind: library, summary: s, optional: true}\n"}), []),
    ("port-not-needed", project("", {"b": B_PROVIDES_X}), ["W W3 README.md"]),
    ("unknown-endpoint", project("wiring:\n  a.x: b.y\n", {"a": A_NEEDS_X, "b": B_PROVIDES_X}),
     ["E W1 README.md", "W W3 README.md"]),
    ("kinds-differ",
     project(WIRED, {"a": A_NEEDS_X, "b": "provides:\n  x: {kind: http, summary: s}\n"}),
     ["W W4 README.md"]),
    ("cycle", project("wiring:\n  a.x: b.x\n  b.y: a.y\n", {
        "a": A_NEEDS_X + "provides:\n  y: {kind: library, summary: s}\n",
        "b": B_PROVIDES_X + "needs:\n  y: {kind: library, summary: s}\n"}),
     ["W W7 README.md"]),
    ("alternatives", project("wiring:\n  a.x: {real: b.x, fake: c.x}\n",
                             {"a": A_NEEDS_X, "b": B_PROVIDES_X, "c": B_PROVIDES_X}), []),
    ("alternatives-as-list", project("wiring:\n  a.x: [b.x, c.x]\n",
                                     {"a": A_NEEDS_X, "b": B_PROVIDES_X, "c": B_PROVIDES_X}),
     ["E M4 README.md", "E W2 README.md", "W W3 README.md", "W W3 README.md"]),
    ("plain-folder-provider", project("wiring:\n  a.x: ./legacy\n", {"a": A_NEEDS_X},
                                      {"legacy/code.txt": "x\n"}), ["I W8 README.md"]),
    ("delegation-and-pass-up", project(
        "provides:\n  p: {kind: http, summary: s}\nneeds:\n  n: {kind: http, summary: s}\n"
        "wiring:\n  p: a.p\n  a.n: n\n",
        {"a": "provides:\n  p: {kind: http, summary: s}\nneeds:\n  n: {kind: http, summary: s}\n"}),
     []),
    ("unknown-key", project("colour: blue\nx-team: red\n"), ["E M5 README.md"]),
    ("manifest-in-two-places", project(files={"unit.yaml": 'unit: demo\nunifold: "0.1"\nsummary: s\n'}),
     ["E M1 unit.yaml", "E S1 ."]),
    ("unsupported-version", {**project(), "README.md": readme(
        'unit: demo\nunifold: "9.9"\nsummary: A demo\nstatus: planned\n')}, ["E S1 README.md"]),
    ("name-differs-from-folder", project("", {"a": ""}, {"a/README.md": readme(
        "unit: other\nsummary: s\nstatus: planned\n")}), ["E S2 a/README.md"]),
    ("no-agents-file", project("", {"a": ""}, {"a/AGENTS.md": None}), ["E S11 a"]),
    ("skill-not-linked", project(files={
        "doc/skills/do-it/SKILL.md": "---\nname: do-it\ndescription: Does it.\n---\n# Do it\n"}),
     ["E S8 AGENTS.md"]),
    ("active-without-verification",
     {**project(), "README.md": readme('unit: demo\nunifold: "0.1"\nsummary: A demo\n'
                                       "provides:\n  p: {kind: cli, summary: s}\n")},
     ["W M8 README.md"]),
    ("link-up-outside-context", project("", {"a": ""}, {"a/README.md": readme(
        "unit: a\nsummary: s\nstatus: planned\n", "[up](../README.md)\n")}),
     ["E L3 a/README.md"]),
    ("link-sideways", project("", {"a": "", "b": ""}, {"a/README.md": readme(
        "unit: a\nsummary: s\nstatus: planned\n", "[b](../b/README.md)\n")}),
     ["E L4 a/README.md"]),
    ("link-into-child", project(root_extra="[a](a/AGENTS.md)\n", units={"a": ""}),
     ["E L2 README.md"]),
    ("link-to-child-readme", project(root_extra="[a](a/README.md)\n", units={"a": ""}), []),
    ("sibling-named-in-code-font", project("", {"a": "", "b": ""}, {"a/README.md": readme(
        "unit: a\nsummary: s\nstatus: planned\n", "It talks to `b`.\n")}),
     ["W L6 a/README.md"]),
    ("context-cites-ancestor", project("", {"a": ""}, {
        "doc/decisions/0001-x.md": DECISION.format(status="proposed", more=""),
        "AGENTS.md": agents("\n[read-docs](doc/skills/read-docs/SKILL.md)\n"
                            "[decisions](doc/decisions/index.md)\n"),
        "a/AGENTS.md": agents("\n[context](doc/context.md)\n"),
        "a/doc/context.md": "# Context of a\n\n### [demo/0001](../../doc/decisions/0001-x.md)\n\n"
                            "Says: x.\n\nHere: y.\n"}), []),
    ("context-cites-superseded-decision", project("", {"a": ""}, {
        "doc/decisions/0001-x.md": DECISION.format(status="superseded by 0002", more=""),
        "AGENTS.md": agents("\n[read-docs](doc/skills/read-docs/SKILL.md)\n"
                            "[decisions](doc/decisions/index.md)\n"),
        "a/AGENTS.md": agents("\n[context](doc/context.md)\n"),
        "a/doc/context.md": "# Context of a\n\n### [demo/0001](../../doc/decisions/0001-x.md)\n\n"
                            "Says: x.\n\nHere: y.\n"}),
     ["W L7 a/doc/context.md"]),
    ("context-item-without-restatement", project("", {"a": ""}, {
        "doc/decisions/0001-x.md": DECISION.format(status="proposed", more=""),
        "AGENTS.md": agents("\n[read-docs](doc/skills/read-docs/SKILL.md)\n"
                            "[decisions](doc/decisions/index.md)\n"),
        "a/AGENTS.md": agents("\n[context](doc/context.md)\n"),
        "a/doc/context.md": "# Context of a\n\n### [demo/0001](../../doc/decisions/0001-x.md)\n\n"
                            "Here: y.\n"}),
     ["W L9 a/doc/context.md"]),
    ("conforms-to-unknown-need",
     project("", {"b": "provides:\n  x: {kind: library, summary: s, conforms-to: spec}\n"}),
     ["E M9 b/README.md", "W W3 README.md"]),
    ("conforms-to-own-need", project(
        "wiring:\n  b.spec: c.x\n  a.x: b.x\n",
        {"a": A_NEEDS_X,
         "b": "provides:\n  x: {kind: library, summary: s, conforms-to: spec}\n"
              "needs:\n  spec: {kind: library, summary: s}\n",
         "c": B_PROVIDES_X}), []),
    ("accepted-without-decision-makers", project(files={
        "doc/decisions/0001-x.md": DECISION.format(status="accepted", more=""),
        "AGENTS.md": agents("\n[read-docs](doc/skills/read-docs/SKILL.md)\n"
                            "[decisions](doc/decisions/index.md)\n")}),
     ["E S10 doc/decisions/0001-x.md"]),
    ("accepted-with-decision-makers", project(files={
        "doc/decisions/0001-x.md": DECISION.format(status="accepted",
                                                   more="decision-makers: [Ada]\n"),
        "AGENTS.md": agents("\n[read-docs](doc/skills/read-docs/SKILL.md)\n"
                            "[decisions](doc/decisions/index.md)\n")}), []),
    ("file-too-long", project(files={"doc/architecture.md": "# Long\n" + "line\n" * 200},
                              root_extra="[arch](doc/architecture.md)\n"),
     ["E T1 doc/architecture.md"]),
    ("line-too-long", project(files={"doc/architecture.md": "# Wide\n\n" + "word " * 100 + "\n"},
                              root_extra="[arch](doc/architecture.md)\n"),
     ["W T3 doc/architecture.md"]),
    ("file-not-reachable", project(files={"doc/references/lost.md": "# Lost\n"}),
     ["E L5 doc/references/lost.md"]),
    ("hand-written-file-among-diagrams", project(files={"doc/diagrams/mine.md": "# Mine\n"}),
     ["E G2 doc/diagrams/mine.md", "E L5 doc/diagrams/mine.md"]),
    ("core-level-needs-no-agents-file-and-no-copy", {
        "unit.yaml": 'unit: demo\nunifold: "0.1"\nlevel: core\nsummary: A demo\n'
                     "status: planned\nwiring:\n  a.x: b.x\n",
        "README.md": "# demo\n",
        "a/unit.yaml": "unit: a\nsummary: s\nstatus: planned\n" + A_NEEDS_X,
        "a/README.md": "# a\n",
        "b/unit.yaml": "unit: b\nsummary: s\nstatus: planned\n" + B_PROVIDES_X,
        "b/README.md": "# b\n"}, []),
    ("core-level-still-checks-wiring", {
        "unit.yaml": 'unit: demo\nunifold: "0.1"\nlevel: core\nsummary: A demo\n'
                     "status: planned\n",
        "README.md": "# demo\n",
        "a/unit.yaml": "unit: a\nsummary: s\nstatus: planned\n" + A_NEEDS_X,
        "a/README.md": "# a\n"}, ["E W2 unit.yaml"]),
    ("wildcard-wiring", project('wiring:\n  "*.x": c.x\n',
                                {"a": A_NEEDS_X, "b": A_NEEDS_X, "c": B_PROVIDES_X}), []),
    ("wildcard-matches-nothing", project('wiring:\n  "*.y": c.x\n', {"c": B_PROVIDES_X}),
     ["E W1 README.md", "W W3 README.md"]),
    ("optional-must-be-a-boolean",
     project("", {"a": 'needs:\n  x: {kind: library, summary: s, optional: "false"}\n'}),
     ["E M4 a/README.md", "E W2 README.md"]),
    ("active-unit-needs-planned-provider", project(WIRED, {"a": A_NEEDS_X, "b": B_PROVIDES_X}, {
        "a/README.md": readme("unit: a\nsummary: s\nstatus: active\n" + A_NEEDS_X)}),
     ["W W9 README.md"]),
    ("alternatives-conform-to-different-definitions", project(
        "wiring:\n  a.x: {real: b.x, fake: c.x}\n  b.spec: d.one\n  c.spec: d.two\n",
        {"a": A_NEEDS_X,
         "b": "provides:\n  x: {kind: library, summary: s, conforms-to: spec}\n"
              "needs:\n  spec: {kind: specification, summary: s}\n",
         "c": "provides:\n  x: {kind: library, summary: s, conforms-to: spec}\n"
              "needs:\n  spec: {kind: specification, summary: s}\n",
         "d": "provides:\n  one: {kind: specification, summary: s}\n"
              "  two: {kind: specification, summary: s}\n"}),
     ["W W10 README.md"]),
    ("readme-heading-not-in-manifest", project("", {"b": B_PROVIDES_X}, {
        "b/README.md": readme("unit: b\nsummary: s\nstatus: planned\n" + B_PROVIDES_X,
                              "\n## Provides\n\n### `x`\n\nText.\n\n### `gone`\n\nText.\n")}),
     ["W T5 b/README.md", "W W3 README.md"]),
    ("readme-title-is-not-the-unit-name", project("", {"a": ""}, {
        "a/README.md": "---\nunit: a\nsummary: s\nstatus: planned\n---\n# other\n\n"
                       "[d](doc/diagrams/context.md)\n"}), ["W T6 a/README.md"]),
    ("duplicate-decision-number", project(files={
        "doc/decisions/0001-x.md": DECISION.format(status="proposed", more=""),
        "doc/decisions/0001-y.md": DECISION.format(status="proposed", more=""),
        "AGENTS.md": agents("\n[read-docs](doc/skills/read-docs/SKILL.md)\n"
                            "[decisions](doc/decisions/index.md)\n")}),
     ["E S9 doc/decisions/0001-y.md"]),
    ("undeclared-dependency-in-code", project("", {"a": "", "b": ""}, {
        "a/src/main.c": "x\n", "b/src/lib.c": "x\n",
        "deps.json": '[{"from": "a/src/main.c", "to": "b/src/lib.c"}]\n'}),
     ["E D1 README.md"]),
    ("declared-dependency-in-code", project(WIRED, {"a": A_NEEDS_X, "b": B_PROVIDES_X}, {
        "a/src/main.c": "x\n", "b/src/lib.c": "x\n",
        "deps.json": '[{"from": "a/src/main.c", "to": "b/src/lib.c"}]\n'}), []),
    ("wired-but-no-dependency-observed", project(WIRED, {"a": A_NEEDS_X, "b": B_PROVIDES_X}, {
        "deps.json": "[]\n"}), ["I D2 README.md"]),
    ("ignored-folder", project("ignore: [./vendor]\n", files={
        "vendor/dep/README.md": "---\nunit: wrong-name\nsummary: s\n---\n# dep\n"}), []),
]


def run_tool(tool: list[str], *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([*tool, *args], capture_output=True, text=True)


def write_case(folder: Path, files: dict) -> None:
    for path, content in files.items():
        target = folder / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main() -> int:
    args = sys.argv[1:]
    if args[:1] == ["--write"]:
        for name, files, expected in CASES:
            folder = Path(args[1]) / name
            write_case(folder, files)
            (folder / "expected.txt").write_text("\n".join(expected) + "\n")
        print(f"wrote {len(CASES)} cases to {args[1]}")
        return 0
    tool = shlex.split(args[1]) if args[:1] == ["--tool"] else [sys.executable, str(TOOL)]
    reference = [sys.executable, str(TOOL)]
    failed = 0
    for name, files, expected in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp).resolve() / "demo"
            write_case(folder, files)
            run_tool(reference, "generate", str(folder))
            deps = ["--deps", str(folder / "deps.json")] if "deps.json" in files else []
            result = run_tool(tool, "check", "--json", *deps, str(folder))
            try:
                found = sorted(f"{f['severity']} {f['rule']} {f['file']}"
                               for f in json.loads(result.stdout))
            except json.JSONDecodeError:
                found = ["no JSON: " + (result.stdout + result.stderr).strip()[:200]]
            ok = found == sorted(expected)
            failed += not ok
            print(("ok   " if ok else "FAIL ") + name)
            if not ok:
                print("     expected:", sorted(expected))
                print("     found:   ", found)
    print(f"{len(CASES) - failed} of {len(CASES)} cases pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
