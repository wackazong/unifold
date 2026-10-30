#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""unifold: check, draw and query the architecture map of a repository.

A folder with a `unifold.yaml` is a unit: it says what it provides and what it
needs. The unit above wires needs to providers. This tool checks that the map
is consistent: every need wired, both sides of a connection on one contract, the
documents where they belong, the generated files current.

  init [DIR] [--agents]       start a project: root manifest, generated files; --agents adds the skills
  check [PATH] [--fix]        report findings; --fix first writes the generated files
  generate [PATH]             write diagrams, decision indexes, AGENTS.md, skill stubs
  show [PATH]                 one unit with its resolved neighbours
  capability PATH NAME        both ends of every connection of one entry
  impact PATH [CAPABILITY]    everything that depends on a unit or capability
  tree [PATH]                 the unit tree
  model [PATH]                the resolved project as JSON, with a stable schema
  stamp [PATH]                confirm context items: write and refresh their stamps
  cited-by FILE               context items and links that cite FILE
  skills [sync] [PATH]        list skills, or write stubs where agents look for them
  site [PATH]                 write the HTML explorer
  rules [ID]                  the rules that `check` applies

Documentation: https://unifold.md
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from urllib.parse import quote, unquote

try:
    import yaml
except ImportError:                                   # pragma: no cover
    sys.stderr.write("unifold needs the PyYAML package. Run it with `uvx unifold` or "
                     "`uv run unifold.py`, or install PyYAML (python3 -m pip install pyyaml).\n")
    sys.exit(2)

TOOL_VERSION = "0.3"
SPEC_VERSIONS = ("0.3",)
MODEL_VERSION = "0.3"
SITE_URL = "https://unifold.md"
MANIFEST = "unifold.yaml"
MAX_LINES = 200
MAX_WHY_LINES = 20             # lines that are not blank under `## Why` of a README.md
LIST_LIMIT = 12                # more files of one kind than this are counted, not linked, in AGENTS.md
MAX_DEPTH = 3
SHARED_FROM = 3                # so many children passing one need up are listed, not drawn
INDEX_LIMIT = 40
MARK_PREFIX = "<!-- unifold:generated"
MARK = MARK_PREFIX + " - do not edit; run `unifold generate` -->"
STUB_MARK = MARK_PREFIX + " - do not edit; run `unifold skills sync` -->"
BLOCK_BEGIN = "<!-- unifold:begin - generated block; run `unifold generate` to refresh -->"
BLOCK_BEGIN_PREFIX = "<!-- unifold:begin"
BLOCK_END = "<!-- unifold:end -->"
STAMP = re.compile(r"^<!--\s*unifold:cites\s+sha=([0-9a-f]{8})\s*-->\s*$")
MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"
NEVER_SCANNED = {"node_modules", "__pycache__"}
STUB_DIRS = (".agents/skills", ".claude/skills")
DOC_KINDS = ("tutorials", "skills", "references", "explanation", "decisions", "diagrams")
EXPLANATION_ORDER = ("context", "requirements", "reasoning", "invariants", "runtime", "deployment", "risks")
AGENTS_FIX = ("AGENTS.md is generated. Move its content into README.md (`## Why`) and "
              "docs/, delete the file, then run `unifold check --fix`.")
README_TEMPLATE = """# <folder-name>

<One paragraph: what this unit is, what it is for, and for whom. A reader who knows nothing else about the project must be able to decide from it whether this is the unit they are looking for. Say what the unit does, not how.>

## Why

<Why this unit exists and why it is cut this way: the long form of its secret and its not, the forces that shaped it, the main trade-off, what must stay true. Write the reasons a newcomer cannot guess. At most 20 lines that are not blank; the long form is docs/explanation/reasoning.md. No list of children, capabilities or connections: the manifest holds them and `unifold show` prints them.>

## Capabilities

<One `###` section for each capability whose summary and contract do not say everything. Delete the others, and the whole section if none is left.>

### `<capability-name>`

<Only what the contract does not say: what this unit adds beyond it, each guarantee in a form a test could check, and its own limits. Do not repeat the contract; the manifest names it.>

## Needs

<One `###` section for each need whose summary and contract do not say everything. Delete the others, and the whole section if none is left.>

### `<need-name>`

<Only what the contract does not say: what this unit expects beyond it, never who supplies it. For an optional need: what the unit does without it.>

## Commands

<!-- Optional: the few commands to build, test and run this unit. Delete the section otherwise. -->

## Read next

<!-- Optional: a few links into docs/ whose order matters. Delete the section otherwise. -->
"""   # the same text as the skill asset assets/README.template.md
ROOT_KEYS = ("unifold", "name", "ignore", "diagrams", "diagram-links", "max-lines")
UNIT_KEYS = ("responsibility", "kind", "status", "owner", "secret", "not", "capabilities", "needs", "wiring",
             "scenarios")
CAPABILITY_KEYS = ("summary", "kind", "contract")
NEED_KEYS = ("summary", "kind", "contract", "optional", "platform")
SCENARIO_KEYS = ("summary", "source", "hops", "expect")
STATUSES = ("planned", "active", "deprecated")
WELL_KNOWN_KINDS = ("logic", "stateful", "adapter")
PART_KINDS = ("command", "query", "event", "type")
DIAGRAM_MODES = ("parents", "all", "none")
DECISION_STATUS = re.compile(r"^(proposed|accepted|rejected|deprecated|derived|superseded by (\d{4}))$")
HOP = re.compile(r"^\s*(\S.*?)\s*->\s*(\S.*?)\s*$")
PART_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CONSTANT_PATTERN = r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b"
FIELD_LINE = re.compile(r"^(Kind|Pre|Result|Errors|Examples):\s*(.*?)\s*$")
DECISION_FILE = re.compile(r"^(\d{4})-[a-z0-9][a-z0-9-]*\.md$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ENTRY_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
PLACEHOLDER = re.compile(r"^<[^<>]*>$")
TODO = re.compile(r"^TODO\b", re.I)
INLINE_LINK = re.compile(
    r"\]\(\s*(<[^>\n]*>|(?:[^()\s\\]|\\.|\([^()\s]*\))+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
REF_LINK = re.compile(r"^\s{0,3}\[(?!\^)[^\]]+\]:\s*(<[^>\n]*>|\S+)")
HTML_LINK = re.compile(r"<(?:a|img)\b[^>]*?\b(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
HTML_ANCHOR = re.compile(r"<[a-zA-Z][^>]*?\b(?:id|name)\s*=\s*[\"']([^\"']+)[\"']")
CODE_SPAN = re.compile(r"(`+)(.+?)\1")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
TABLE_RULE = re.compile(r"^\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?$")
ATX = re.compile(r"^ {0,3}(#{1,6})(?:\s+(.*?))?\s*#*\s*$")

# rule id: (severity, what the rule demands, how to fix a finding); the same table as docs/references/rules.md
RULES = {
    "S1": ("error", "The root manifest states `unifold: \"0.3\"`, as a string.",
           "Write `unifold: \"0.3\"` in the root `unifold.yaml`. A 0.2 project is rewritten by hand: `summary` of a unit becomes `responsibility`, `verified-by` goes, a unit with children gets a `kind`."),
    "S3": ("error", "Every unit has a `README.md`.",
           "Write the file (the template is in the `unifold` skill)."),
    "S7": ("error", "Every folder in `docs/skills/` has a `SKILL.md` whose front matter has `name`, equal to the folder name, and `description`.",
           "Correct the front matter."),
    "S9": ("error", "A decision file is named `NNNN-short-title.md` with a number that is unique in the unit; its front matter has an ISO `date` and a `status` that is proposed, accepted, rejected, deprecated, superseded by NNNN, or derived; `accepted` names `decision-makers`; `superseded by NNNN` names an existing decision; `derived` has `derived-from` and a section `## Source says`.",
           "Correct the file name or the front matter; give a derived decision the passage it rests on."),
    "S12": ("info", "Every entry directly in `docs/` is one of `tutorials`, `skills`, `references`, `explanation`, `decisions`, `diagrams`.",
           "Move the file or folder into the folder of its kind: tutorials (learn), skills (do), references (look up), explanation (understand)."),
    "M1": ("error", "A manifest is a YAML mapping without duplicate keys.",
           "Correct the YAML. The unit and its wiring are not checked until it parses."),
    "M2": ("error", "A manifest has a one-line `responsibility` and otherwise only the keys, types and values of the standard; a unit with children below the root states a `kind`; root-only keys are in the root; `platform` stands on a need of the root only; `contract` is a path or a mapping with `path` and `parts`; names of capabilities, needs and scenarios use letters, digits, `-` and `_` and start with a letter or digit; no text is a placeholder (`<...>`).",
           "Correct the key or value named in the message. `summary` of a unit is `responsibility` since 0.3. Project-specific keys start with `x-`."),
    "M7": ("error", "`contract` is a path, relative to the manifest, to a Markdown file that exists in `docs/references/` of this unit or of an ancestor.",
           "Write the contract as `docs/references/<topic>.md` of the unit that wires the connection, and name it from both sides. A schema file is not a contract, and a definition from outside the project is linked from the reference by its URL. Otherwise correct the path, create the file, or remove the key until there is something to point at."),
    "M10": ("warn", "No responsibility or summary is still `TODO`.",
           "Replace `TODO` with one line that says what the unit, capability or need is."),
    "M11": ("error", "Every name under `parts` is a part of the named contract: a `###` heading under `## Parts`, or a file in the contract folder.",
           "Correct the name, or add the part to the contract."),
    "W1": ("error", "Every wiring line has an allowed form and names an existing direct child, capability or need, on the correct side. A bare key names a capability or a need of the unit, not both. A need of a child is passed up only to a need that the unit does not meet inside, and a need that a child meets inside is not wired again. A connection joins two units; a folder is never a provider.",
           "Correct the reference. `unifold show` lists the names; where two children share a folder name, write the path (`a/utils.matcher`). Code that is not a unit gets a folder with a `unifold.yaml`."),
    "W2": ("error", "Every need of every child is connected by a line in the parent's wiring, unless it is `optional` or the child meets it inside.",
           "Add `child.need: provider` to the parent's wiring, for a capability of a sibling, or declare a need in the parent and pass the need up (`child.need: need`). Do not mark a need optional to silence this."),
    "W3": ("warn", "Every capability of a child is used: a wiring line names it as the provider of a need of a sibling or of the parent itself, or a capability of the parent is implemented by it.",
           "Wire the unit that should use it; where code of the parent itself uses it, declare a need in the parent and wire it (`need: child.capability`); or implement a capability of the parent with it (`capability: child.capability`); or remove the capability."),
    "W4": ("warn", "A need and its provider have the same `kind`, if both state one.",
           "Put an adapter unit between the two, or correct the kind that is wrong."),
    "W7": ("warn", "The children of a unit do not need each other in a cycle.",
           "Move what both need into a third unit, or turn one direction around (the other side subscribes)."),
    "W9": ("warn", "An `active` unit does not get a mandatory need from a provider that is `planned` or `deprecated` (default alternative).",
           "Correct the status, or wire a provider that exists."),
    "W11": ("error", "Every side of a connection names a contract, and both sides name the same document.",
           "Write the definition as a reference of this unit, the one that holds the wiring, or of a unit above it, and point both sides at it with `contract`."),
    "K1": ("info", "A unit's `kind` is one of the well-known values `logic`, `stateful` and `adapter`.",
           "Use a well-known kind where one fits; any other value is allowed and carries no rule."),
    "K2": ("warn", "A `logic` unit is logic throughout: every child is a `logic` unit, and the final provider of every need is a `logic` unit, so no need reaches a need of the root.",
           "Move the input, output or state the finding names into a `stateful` or `adapter` unit, or change the kind."),
    "K3": ("warn", "The final provider of no need of an `adapter` is an `adapter`.",
           "Let both talk to a `stateful` or `logic` unit in between, or merge them: one adapter talks to one external system."),
    "K4": ("warn", "A need of the root without `platform: true` is finally reached only by `adapter` units. Silent for a unit that states no `kind`.",
           "Put an adapter between the unit named and the external system, or mark a host service `platform: true`."),
    "K5": ("error", "`secret` is a mapping with `what`, one line, and `decision`, a path relative to the manifest that exists and is a decision of this unit or of an ancestor.",
           "Write the decision that says why this is the secret, and point at it."),
    "K6": ("error", "`not` is a list; an item is a one-line text, or one line mapped to a need of the unit.",
           "Write each item as text, or as `thing: need` where `need` is a need of this unit."),
    "N1": ("error", "Every hop resolves to one connection, its part is in that connection's contract, and no name is ambiguous: a name that is both a descendant and a capability or need of the holding unit, or two connections between the same units whose contracts both have the part.",
           "Wire the connection the hop needs, add the part to the contract, or rename what is ambiguous."),
    "N2": ("error", "A scenario has `summary`, `hops` (a list of `caller -> target.part`) and `expect`; its name follows the rule for names.",
           "Complete the scenario."),
    "N3": ("warn", "Every wiring line of a unit is used by a hop of a scenario that passes through the unit. Silent where no scenario passes through the unit.",
           "Write the scenario that needs the line, or remove the connection."),
    "C1": ("warn", "A contract has `## Parts` with at least one part, each with `Kind:` command, query, event or type.",
           "Write the parts as [writing.md](writing.md#contracts) says."),
    "C2": ("warn", "A command or query has `Pre:`, `Result:`, `Errors:` and an `Examples:` table with at least one row.",
           "Complete the part; the examples are the first tests."),
    "C3": ("warn", "Every part has a fenced code block, its signature.",
           "Write the signature in the notation the header names."),
    "C4": ("warn", "A type is defined once within the subtree of the unit that holds the contract.",
           "Keep one definition and link to it from the other contract."),
    "C5": ("warn", "A contract has `## Fake`.",
           "Say what stands in for the contract in the tests of its consumers."),
    "L1": ("error", "The target of every relative link in a hand-written document exists, including its anchor: a heading, or the first cell of a table row.",
           "Correct the link."),
    "L2": ("error", "A relative link stays inside the project, and no link is an absolute path.",
           "Write the link relative to this file; cite things outside the project by full URL."),
    "L7": ("warn", "`docs/explanation/context.md` cites no decision that is rejected, deprecated or superseded, and an `active` unit cites no decision that is still `proposed`; `derived` binds.",
           "Cite the successor, or have the decision accepted."),
    "L9": ("warn", "Every item of `docs/explanation/context.md` is a `###` heading with a link, followed by a paragraph that starts with `Says` and one that starts with `Here`.",
           "Complete the item."),
    "L10": ("warn", "Every context item carries a stamp, and the cited part (the file, or the section or table row that the fragment of the link names) has not changed since the stamp was written.",
           "Read the cited source again, correct `Says`, then run `unifold stamp`. Only `unifold stamp` writes stamps; `check --fix` never does."),
    "L11": ("warn", "A link stays inside the unit, goes down to a direct child (its folder or its `README.md`), goes up from `docs/explanation/context.md` to an ancestor's `README.md`, decisions or references, or targets a file that the unit's manifest names as `contract`. No other link goes sideways or deeper.",
           "Remove the link. What the unit wants from a sibling is a need in its manifest; what it takes from above is an item in `docs/explanation/context.md`."),
    "T1": ("warn", "A hand-written document has at most `max-lines` lines (default 200).",
           "Split the file: a reference into parts, the long why into `docs/explanation/reasoning.md`, a procedure into a skill."),
    "T4": ("warn", "The `## Why` section of `README.md` has at most 20 lines that are not blank.",
           "Move the long form to `docs/explanation/reasoning.md`."),
    "T5": ("warn", "A `###` heading in code font under `## Capabilities` or `## Needs` of a `README.md` names a capability or need of the manifest.",
           "Rename or remove the section; the manifest is the list of capabilities and needs."),
    "T6": ("warn", "Where the unit or an ancestor has `docs/references/constants.md`, every name in a code span of the unit's hand-written documents that matches the table's name pattern is a row of the nearest such table or of one above it. The table has the columns `Name` and `Value` first; the pattern is `name-pattern` in its front matter, by default capitals in at least two words. Fenced blocks are not read. Silent where no table exists.",
           "Add the row to the constants table, or correct the name."),
    "G1": ("error", "Every generated file exists, is not ignored by git, and equals what the generator writes now, the scenario diagrams included; no leftover generated file remains; `docs/diagrams/` holds only generated files and `AGENTS.md` is generated.",
           "Run `unifold generate` (or `unifold check --fix`). A hand-written `AGENTS.md` is not overwritten: move its content to `README.md` and `docs/`, delete it, then run the command."),
}
SEVERITY_ORDER = {"error": 0, "warn": 1, "info": 2}


class Fail(Exception):
    """A problem that stops the command: bad arguments, no project, unwritable file."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


# ---------------------------------------------------------------- reading

_YamlBase = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


class _Loader(_YamlBase):
    """YAML loader that rejects duplicate and unhashable mapping keys."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            try:
                key = self.construct_object(key_node, deep=True)
                duplicate = key in seen
            except TypeError:
                raise yaml.constructor.ConstructorError(
                    None, None, "a key must be plain text, not a list or a mapping",
                    key_node.start_mark)
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    None, None, f"duplicate key '{key}'", key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)


def _key_lines(node, prefix=(), depth=0, out=None):
    out = {} if out is None else out
    if isinstance(node, yaml.MappingNode) and depth < 3:
        for key, value in node.value:
            if isinstance(key, yaml.ScalarNode):
                path = prefix + (key.value,)
                out.setdefault(path, key.start_mark.line + 1)
                _key_lines(value, path, depth + 1, out)
    return out


def parse_yaml(text: str, offset: int = 0):
    """Return (mapping or None, {key path: line}, error or None, error line or None)."""
    loader = _Loader(text)
    try:
        node = loader.get_single_node()
        data = loader.construct_document(node) if node is not None else {}
        lines = {k: v + offset for k, v in _key_lines(node).items()}
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        problem = getattr(exc, "problem", None) or " ".join(str(exc).split())
        hint = ""
        if "mapping values are not allowed" in problem:
            hint = " (a value that contains ': ' must be quoted)"
        elif "found character '\\t'" in problem:
            hint = " (indent with spaces, not tabs)"
        return None, {}, f"invalid YAML: {problem}{hint}", (mark.line + 1 + offset) if mark else None
    except RecursionError:
        return None, {}, "invalid YAML: nested too deeply", None
    finally:
        loader.dispose()
    if data is None:
        return {}, lines, None, None
    if not isinstance(data, dict):
        return None, {}, "the file must be a YAML mapping (key: value lines)", 1 + offset
    return data, lines, None, None


def read_text(path: str) -> str:
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as handle:
        return handle.read().replace("\r\n", "\n").replace("\r", "\n")


def write_text(path: str, content: str):
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except OSError as exc:
        raise Fail("not-writable", f"cannot write {path}: {exc.strerror or exc}")


def cell(text) -> str:
    """Text made safe for a Markdown table cell."""
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def url_path(path: str) -> str:
    """A relative path as a link target: URL-encoded, with forward slashes."""
    return quote(path.replace(os.sep, "/"), safe="/#")


def show_value(value) -> str:
    """A YAML value as a user wrote it, for messages."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "nothing"
    if isinstance(value, (list, dict)):
        return "a list" if isinstance(value, list) else "a mapping"
    return f"'{value}'"


def heading_slug(text: str) -> str:
    """The anchor that code hosts derive from a heading."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = "".join(c for c in text if c.isalnum() or c in " -_")
    return text.replace(" ", "-")


class Doc:
    """One Markdown file, parsed once: front matter, prose, links, headings."""

    def __init__(self, path: str, text: str):
        self.path, self.text = path, text
        self.lines = text.split("\n")
        if self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.meta, self.meta_error, self.body_start = None, None, 0
        lines = self.lines
        if lines and lines[0].strip() == "---":
            end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
            if end is None:
                self.meta_error = "front matter is not closed with '---'"
            else:
                self.meta, _, self.meta_error, _ = parse_yaml("\n".join(lines[1:end]))
                self.body_start = end + 1
        self._prose = self._links = self._headings = self._rows = None

    @property
    def generated(self) -> bool:
        return any(l.startswith(MARK_PREFIX) for l in self.lines[self.body_start:self.body_start + 2])

    @property
    def prose(self) -> list:
        """(line number, text) outside fenced code blocks; code spans are blanked."""
        if self._prose is None:
            out, fence = [], None
            for number, line in enumerate(self.lines[self.body_start:], self.body_start + 1):
                match = FENCE.match(line)
                if fence:
                    if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
                            and not match.group(2).strip():
                        fence = None
                    continue
                if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                    fence = match.group(1)
                    continue
                out.append((number, line))
            self._prose = out
        return self._prose

    @property
    def links(self) -> list:
        """(line number, target) of every link, image and reference definition."""
        if self._links is None:
            out = []
            for number, line in self.prose:
                if "](" not in line and "]:" not in line and "<" not in line:
                    continue
                bare = CODE_SPAN.sub(lambda m: " " * len(m.group()), line)
                found = [m.group(1) for m in INLINE_LINK.finditer(bare)]
                ref = REF_LINK.match(bare)
                if ref:
                    found.append(ref.group(1))
                found += HTML_LINK.findall(bare)
                for target in found:
                    target = target[1:-1] if target.startswith("<") and target.endswith(">") else target
                    target = re.sub(r"\\(.)", r"\1", target).strip()
                    if target:
                        out.append((number, target))
            self._links = out
        return self._links

    @property
    def headings(self) -> list:
        """(line number, level, text, anchor) of every heading."""
        if self._headings is None:
            out, seen, previous = [], {}, None
            for number, line in self.prose:
                match = ATX.match(line)
                found = None
                if match:
                    found = (number, len(match.group(1)), (match.group(2) or "").strip())
                elif previous and previous[1].strip() and re.match(r"^ {0,3}(=+|-+)\s*$", line) \
                        and not ATX.match(previous[1]) and len(line.strip()) >= 2:
                    found = (previous[0], 1 if "=" in line else 2, previous[1].strip())
                if found:
                    slug = heading_slug(found[2])
                    count = seen.get(slug, 0)
                    seen[slug] = count + 1
                    out.append((*found, slug if not count else f"{slug}-{count}"))
                previous = (number, line)
            self._headings = out
        return self._headings

    @property
    def rows(self) -> dict:
        """{slug of the first cell: line number} of the body rows of every table.

        The first cell is read like a heading (code font and bold do not count), so the
        row `| **stamp** | ... |` is `#stamp`. The first row with a slug wins.
        """
        if self._rows is None:
            out, prose = {}, self.prose
            for index, (number, line) in enumerate(prose):
                text = line.strip()
                if not text.startswith("|") or TABLE_RULE.match(text):
                    continue
                if index + 1 < len(prose) and TABLE_RULE.match(prose[index + 1][1].strip()):
                    continue                          # the header row
                first = re.split(r"(?<!\\)\|", text[1:], maxsplit=1)[0]
                slug = heading_slug(first)
                if slug:
                    out.setdefault(slug, number)
            self._rows = out
        return self._rows

    def anchors(self) -> set:
        return {h[3] for h in self.headings} | set(HTML_ANCHOR.findall(self.text)) | set(self.rows)

    def section(self, anchor: str):
        """Lines of the part with this anchor, or None: the section under a heading, or,
        if no heading has the anchor, the one table row whose first cell has it."""
        for index, (number, level, _, slug) in enumerate(self.headings):
            if slug == anchor:
                end = next((n for n, lvl, _, _ in self.headings[index + 1:] if lvl <= level),
                           len(self.lines) + 1)
                return self.lines[number - 1:end - 1]
        if anchor in self.rows:
            return [self.lines[self.rows[anchor] - 1]]
        return None

    def title(self):
        return next((h[2] for h in self.headings if h[1] == 1), None)


def split_link(link: str):
    """(path part, anchor) of a link target; the path is URL-decoded."""
    path, _, anchor = link.partition("#")
    return unquote(path.split("?", 1)[0]), unquote(anchor)


def content_hash(lines) -> str:
    text = " ".join(" ".join(lines).split())
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


# ------------------------------------------------------------------ model

class Entry:
    """One provider of a connection: a capability of a child or an own need."""
    __slots__ = ("config", "kind", "unit", "capability", "path", "raw")

    def __init__(self, config, kind, raw, unit=None, capability="", path=""):
        self.config, self.kind, self.raw = config, kind, raw
        self.unit, self.capability, self.path = unit, capability, path


class Conn:
    """A need (or an own capability) with its providers."""
    __slots__ = ("key", "entries", "line")

    def __init__(self, key, entries, line):
        self.key, self.entries, self.line = key, entries, line


def _text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


class Unit:
    def __init__(self, project, path: str, manifest: dict, lines: dict, parent, broken=False):
        self.path, self.manifest, self.lines, self.parent = path, manifest, lines, parent
        self.broken = broken
        self.manifest_path = os.path.join(path, MANIFEST)
        self.rel = project.rel(path)
        self.children: list = []
        self.foreign: list = []                 # nested projects below this unit
        self.name = os.path.basename(path)
        if parent is None:
            self.name = _text(manifest.get("name")) or self.name
        self.responsibility = " ".join(_text(manifest.get("responsibility")).split())
        self.kind = _text(manifest.get("kind"))
        secret = manifest.get("secret")
        self.secret = {"what": " ".join(_text(secret.get("what")).split()),
                       "decision": _text(secret.get("decision")) or None} if isinstance(secret, dict) else None
        self.nots: list = []                    # [(text, need or None)]
        for item in (manifest.get("not") if isinstance(manifest.get("not"), list) else []):
            if isinstance(item, str):
                self.nots.append((" ".join(item.split()), None))
            elif isinstance(item, dict) and len(item) == 1:
                text, need = next(iter(item.items()))
                self.nots.append((" ".join(str(text).split()), str(need) if need is not None else ""))
        self.scenarios: dict = {}               # name -> {summary, source, expect, hops: [raw], x: {}}
        raw = manifest.get("scenarios")
        if isinstance(raw, dict):
            for name, spec in raw.items():
                spec = spec if isinstance(spec, dict) else {}
                hops = spec.get("hops")
                self.scenarios[str(name)] = {
                    "summary": " ".join(_text(spec.get("summary")).split()),
                    "source": " ".join(_text(spec.get("source")).split()),
                    "expect": " ".join(_text(spec.get("expect")).split()),
                    "hops": [h for h in hops if isinstance(h, str)] if isinstance(hops, list) else [],
                    "x": {k: v for k, v in spec.items() if isinstance(k, str) and k.startswith("x-")}}
        status = manifest.get("status")
        self.status = status if status in STATUSES else "active"
        self.own_owner = _text(manifest.get("owner"))
        self.capabilities = self._entries("capabilities")
        self.needs = self._entries("needs")
        self.conn: dict = {}                    # (child, need) -> Conn
        self.impl: dict = {}                    # own capability -> Conn (implemented by children)
        self.inner: dict = {}                   # own need -> Conn (met inside, by a child)
        self.need_users: dict = {}              # own need -> [(child, need)]
        self.capability_users: dict = {}        # (child, capability) -> [("need", user, need, config) | ("capability", name)]; the user may be this unit
        self.problems: list = []                # (line, message) for rule W1
        self.schema_problems: list = []         # (line, message) for rule M2
        self._by_name: dict = {}

    def _entries(self, key: str) -> dict:
        raw = self.manifest.get(key)
        out = {}
        if isinstance(raw, dict):
            for name, value in raw.items():
                spec = {"summary": value} if isinstance(value, str) else \
                    value if isinstance(value, dict) else {}
                contract, parts = spec.get("contract"), None
                if isinstance(contract, dict):
                    raw_parts = contract.get("parts")
                    parts = [str(x) for x in raw_parts] if isinstance(raw_parts, list) else None
                    contract = contract.get("path")
                out[str(name)] = {
                    "summary": " ".join(_text(spec.get("summary")).split()),
                    "kind": _text(spec.get("kind")),
                    "contract": _text(contract) or None,
                    "parts": parts,
                    "optional": spec.get("optional") is True,
                    "platform": spec.get("platform") is True,
                    "x": {k: v for k, v in spec.items() if isinstance(k, str) and k.startswith("x-")}}
        return out

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def owner(self) -> str:
        unit = self
        while unit is not None:
            if unit.own_owner:
                return unit.own_owner
            unit = unit.parent
        return ""

    def ancestors(self) -> list:
        out, unit = [], self.parent
        while unit is not None:
            out.append(unit)
            unit = unit.parent
        return out

    def depth_below(self, other):
        """Levels between self and ancestor `other` (0 if same), else None."""
        depth, unit = 0, self
        while unit is not None:
            if unit is other:
                return depth
            unit, depth = unit.parent, depth + 1
        return None

    def ref_in_parent(self) -> str:
        """How the parent's wiring names this unit: the folder name, or the path if it clashes."""
        parent = self.parent
        if parent is None:
            return self.name
        if len(parent._by_name.get(self.name, ())) > 1:
            return os.path.relpath(self.path, parent.path).replace(os.sep, "/")
        return self.name

    def find_child(self, ref: str):
        """Return (child or None, error or None) for a child reference in wiring."""
        ref = ref.strip().strip("/")
        if "/" in ref:
            tail = "/" + ref
            found = [c for c in self.children
                     if ("/" + os.path.relpath(c.path, self.path).replace(os.sep, "/")).endswith(tail)]
        else:
            found = self._by_name.get(ref, [])
        if len(found) == 1:
            return found[0], None
        if found:
            paths = ", ".join(os.path.relpath(c.path, self.path).replace(os.sep, "/") for c in found)
            return None, f"'{ref}' names several children ({paths}); write the path instead"
        names = sorted(self._by_name)
        close = difflib.get_close_matches(ref.split("/")[-1], names, 1) if len(names) < 500 else []
        hint = f"; did you mean '{close[0]}'?" if close else ""
        deeper = "" if "/" in ref or close else \
            " (wiring names direct children only; a child below plain folders is named by its folder name or path)"
        return None, f"no child unit '{ref}'{hint}{deeper}"


def sort_key(rel: str):
    return [(part.casefold(), part) for part in rel.split("/")]


class Project:
    def __init__(self, root: str):
        self.root = root
        self.units: list = []
        self.findings: list = []
        self.foreign: dict = {}                 # nested project path -> owning unit
        self.plain: list = []                   # folders that are not units
        self.by_path: dict = {}
        self.root_unit = None
        self.usable = False                     # False: only `check` can say something
        self.ignore: set = set()                # folders named by `ignore` in the root manifest
        self.git_ignored: set = git_ignored(root)   # files and folders that git ignores
        self.links, self.diagrams, self.max_lines = "none", "parents", MAX_LINES
        self.version = SPEC_VERSIONS[-1]
        self._texts: dict = {}
        self._docs: dict = {}
        self._kinds: dict = {}
        self._owners: dict = {}
        self._rels: dict = {root: "."}
        self._expected = None
        path = os.path.join(root, MANIFEST)
        try:
            data, lines, error, line = parse_yaml(self.text(path))
        except OSError as exc:
            data, lines, error, line = None, {}, f"cannot read the file: {exc.strerror or exc}", None
        if error:
            self.add("M1", path, error, line)
            return
        version = data.get("unifold")
        if not isinstance(version, str) or version not in SPEC_VERSIONS:
            what = f"is {show_value(version)}" + ("" if isinstance(version, str) else ", not a string")
            self.add("S1", path, f"'unifold' {what}; this tool supports "
                                 + ", ".join(f'"{v}"' for v in SPEC_VERSIONS), lines.get(("unifold",)))
            return
        self.usable = True
        self.version = version
        ignore = data.get("ignore")
        if isinstance(ignore, list):
            self.ignore = {os.path.normpath(p).replace(os.sep, "/").strip("/")
                           for p in ignore if isinstance(p, str) and p.strip()}
        links = data.get("diagram-links")
        self.links = links.strip() if isinstance(links, str) and links.strip() else "none"
        if data.get("diagrams") in DIAGRAM_MODES:
            self.diagrams = data["diagrams"]
        limit = data.get("max-lines")
        if isinstance(limit, int) and not isinstance(limit, bool) and limit > 0:
            self.max_lines = limit
        self.root_unit = Unit(self, root, data, lines, None)
        self.units.append(self.root_unit)
        self.by_path[root] = self.root_unit
        self._walk()
        self.units.sort(key=lambda u: sort_key(u.rel) if u.parent else [])
        for unit in self.units:
            unit.children.sort(key=lambda u: sort_key(u.rel))
            for child in unit.children:
                unit._by_name.setdefault(child.name, []).append(child)
        for unit in reversed(self.units):       # children first: a parent must know which
            self._connect(unit)                 # needs its children meet inside

    # ----- files, cached

    def text(self, path: str) -> str:
        found = self._texts.get(path)
        if found is None:
            found = self._texts[path] = read_text(path)
        return found

    def doc(self, path: str) -> Doc:
        found = self._docs.get(path)
        if found is None:
            try:
                text = self.text(path)
            except OSError:
                text = ""
            found = self._docs[path] = Doc(path, text)
        return found

    def kind_of(self, path: str) -> str:
        """'file', 'dir' or '' for a path."""
        found = self._kinds.get(path)
        if found is None:
            found = "file" if os.path.isfile(path) else "dir" if os.path.isdir(path) else ""
            self._kinds[path] = found
        return found

    def forget(self, path: str):
        for cache in (self._texts, self._docs, self._kinds):
            cache.pop(path, None)
        self._kinds.pop(os.path.dirname(path), None)
        self._expected = None

    def expected(self) -> dict:
        """What the generator would write now: {path: content}."""
        if self._expected is None:
            self._expected = generate(self)
        return self._expected

    def rel(self, path: str) -> str:
        found = self._rels.get(path)
        if found is None:
            root = self.root
            if path.startswith(root + os.sep):
                found = path[len(root) + 1:].replace(os.sep, "/")
            else:
                found = path.replace(os.sep, "/")
            self._rels[path] = found
        return found

    def inside(self, path: str) -> bool:
        return path == self.root or path.startswith(self.root + os.sep)

    def add(self, rule: str, path: str, message: str, line=None, fix=None, severity=None):
        self.findings.append({"rule": rule, "severity": severity or RULES[rule][0],
                              "file": self.rel(path), "line": line, "message": message,
                              "fix": fix or RULES[rule][2],
                              "url": f"{SITE_URL}/rules#{rule.lower()}"})

    # ----- the unit tree

    def _walk(self):
        stack = [(self.root, self.root_unit)]
        while stack:
            folder, owner = stack.pop()
            try:
                entries = sorted(os.scandir(folder), key=lambda e: e.name)
            except OSError:
                continue
            for entry in entries:
                name = entry.name
                try:
                    if name.startswith(".") or name in NEVER_SCANNED \
                            or not entry.is_dir(follow_symlinks=False):
                        continue
                except OSError:
                    continue
                path = entry.path
                if name == "docs" and folder == owner.path:
                    continue
                if self.is_ignored(path) or is_build_output(path):
                    continue
                current = owner
                manifest = os.path.join(path, MANIFEST)
                if os.path.isfile(manifest):
                    try:
                        text = self.text(manifest)
                        data, lines, error, line = parse_yaml(text)
                    except OSError as exc:
                        text, data, lines, line = "", None, {}, None
                        error = f"cannot read the file: {exc.strerror or exc}"
                    if (isinstance(data, dict) and "unifold" in data) or \
                            (error and ROOT_LINE.search(text)):
                        owner.foreign.append(path)
                        self.foreign[path] = owner
                        continue
                    if error:
                        self.add("M1", manifest, error, line)
                    current = Unit(self, path, data or {}, lines, owner, broken=bool(error))
                    owner.children.append(current)
                    self.units.append(current)
                    self.by_path[path] = current
                else:
                    self.plain.append(path)
                stack.append((path, current))

    def owner_of(self, path: str):
        """Return ('unit', Unit), ('foreign', path) or (None, None) for any path."""
        if not self.inside(path):
            return None, None
        seen, folder = [], path
        while True:
            found = self._owners.get(folder)
            if found is None:
                if folder in self.foreign:
                    found = ("foreign", folder)
                elif folder in self.by_path:
                    found = ("unit", self.by_path[folder])
            if found is not None or folder == self.root:
                found = found or ("unit", self.root_unit)
                for item in seen:
                    self._owners[item] = found
                return found
            seen.append(folder)
            folder = os.path.dirname(folder)

    def unit_at(self, path: str):
        kind, owner = self.owner_of(path)
        return owner if kind == "unit" else self.root_unit

    def is_ignored(self, path: str) -> bool:
        """Named by `ignore` in the root manifest, or ignored by git: not part of the project."""
        rel = self.rel(path)
        return any(rel == item or rel.startswith(item + "/") for item in self.ignore) \
            or self.git_ignores(path)

    def git_ignores(self, path: str) -> bool:
        rel = self.rel(path)
        return rel in self.git_ignored \
            or any(rel.startswith(item) for item in self.git_ignored if item.endswith("/"))

    def listdir(self, folder: str) -> list:
        """The visible entries of a folder, sorted: no dot files, nothing ignored."""
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            return []
        return [n for n in names if not n.startswith(".")
                and not self.is_ignored(os.path.join(folder, n))]

    # ----- wiring

    def _provider(self, unit, key_side, key_child, config, value, inside=frozenset()):
        """Resolve one provider reference. key_side: 'child' (the key is a need of a child),
        'capability' or 'need' (of this unit). Returns (Entry or None, error or None)."""
        if not isinstance(value, str) or not value.strip():
            return None, f"the provider must be a reference, not {show_value(value)}"
        value = value.strip()
        if value == "." or value.startswith("./"):
            return None, f"'{value}' names a folder; a connection joins two units. Give that " \
                         "code a folder with a unifold.yaml and wire its capability"
        if value.startswith("*"):
            return None, "'*' is not allowed; name the unit"
        if "." in value:
            ref, _, capability = value.rpartition(".")
            child, error = unit.find_child(ref)
            if child is None:
                return None, error
            if capability not in child.capabilities and not child.broken:
                close = difflib.get_close_matches(capability, list(child.capabilities), 1)
                hint = f"; did you mean '{close[0]}'?" if close else \
                    f" (it provides: {', '.join(child.capabilities) or 'nothing'})"
                side = " It is a need there; a provider is a capability." if capability in child.needs else ""
                return None, f"'{child.rel}' does not provide '{capability}'{hint}{side}"
            if child is key_child:
                return None, "a unit cannot provide for its own need"
            return Entry(config, "child", value, unit=child, capability=capability), None
        if key_side == "capability":
            return None, f"a capability cannot be wired to an own need ('{value}'); " \
                         "a capability is implemented by a child (`child.capability`)"
        if key_side == "need":
            return None, f"a need of this unit is met by a capability of a child " \
                         f"(`child.capability`), not by the need '{value}'"
        if value not in unit.needs:
            hint = "; a capability of a child is written 'child." + value + "'" \
                if any(value in c.capabilities for c in unit.children[:500]) else ""
            return None, f"'{value}' is not a need of this unit{hint}"
        if value in inside:
            return None, f"'{value}' is a need that this unit meets inside, for its own code; " \
                         "wire the child's need to a provider of its own"
        return Entry(config, "own", value, capability=value), None

    def _connect(self, unit):
        raw = unit.manifest.get("wiring")
        if not isinstance(raw, dict) or unit.broken:
            raw = {}
        # needs of this unit that a child meets inside: a bare key that names a need and no
        # capability
        inside = {
            str(k).strip() for k in raw if "." not in str(k)
            and str(k).strip() in unit.needs and str(k).strip() not in unit.capabilities}
        for key, value in raw.items():
            key = str(key).strip()
            line = unit.lines.get(("wiring", key))
            if isinstance(value, dict) and value:
                pairs = [(str(k), v) for k, v in value.items()]
            elif isinstance(value, str):
                pairs = [(None, value)]
            else:
                unit.schema_problems.append(
                    (line, f"wiring '{key}': the provider must be one reference or a mapping "
                           f"of named alternatives, not {show_value(value)}"))
                continue
            key_child, need, side = None, None, "child"
            if key.startswith("./") or key.startswith("*"):
                unit.problems.append((line, f"wiring key '{key}': a key is a need of a child "
                                            "(`child.need`), or a capability or need of this unit; "
                                            "every unit is written out"))
                continue
            if "." in key:
                ref, _, need = key.rpartition(".")
                key_child, error = unit.find_child(ref)
                if key_child is None:
                    unit.problems.append((line, f"wiring key '{key}': {error}"))
                    continue
                if need not in key_child.needs and not key_child.broken:
                    close = difflib.get_close_matches(need, list(key_child.needs), 1)
                    hint = f"; did you mean '{close[0]}'?" if close else \
                        f" (it needs: {', '.join(key_child.needs) or 'nothing'})"
                    side_hint = " It is a capability there; write the line as `user.need: " \
                        f"{key}`." if need in key_child.capabilities else ""
                    unit.problems.append((line, f"wiring key '{key}': '{key_child.rel}' has no "
                                                f"need '{need}'{hint}{side_hint}"))
                    continue
                if need in key_child.inner:
                    unit.problems.append((line, f"wiring key '{key}': '{key_child.rel}' meets its "
                                                f"need '{need}' inside, in its own wiring; delete "
                                                "this line"))
                    continue
            else:
                is_cap, is_need = key in unit.capabilities, key in unit.needs
                hint = " (a need of a child is written `child.need`)" \
                    if any(key in c.needs for c in unit.children[:500]) else ""
                if is_cap and is_need:
                    unit.problems.append((line, f"wiring key '{key}': names both a capability and "
                                                "a need of this unit; rename one of them"))
                    continue
                if not is_cap and not is_need:
                    unit.problems.append((line, f"wiring key '{key}': not a capability or need "
                                                f"of this unit{hint}"))
                    continue
                side = "capability" if is_cap else "need"
            entries = []
            for config, target in pairs:
                entry, error = self._provider(unit, side, key_child, config, target, inside)
                if error:
                    shown = target if isinstance(target, str) else show_value(target)
                    unit.problems.append((line, f"wiring '{key}: {shown}': {error}"))
                else:
                    entries.append(entry)
            if not entries:
                continue
            if key_child is not None:
                unit.conn[(key_child, need)] = Conn(key, entries, line)
            elif side == "need":
                unit.inner[key] = Conn(key, entries, line)
            else:
                unit.impl[key] = Conn(key, entries, line)
        for (child, need), conn in unit.conn.items():
            for entry in conn.entries:
                if entry.kind == "own":
                    unit.need_users.setdefault(entry.capability, []).append((child, need))
                elif entry.kind == "child":
                    unit.capability_users.setdefault((entry.unit, entry.capability), []).append(
                        ("need", child, need, entry.config))
        for capability, conn in unit.impl.items():
            for entry in conn.entries:
                unit.capability_users.setdefault((entry.unit, entry.capability), []).append(("capability", capability))
        for need, conn in unit.inner.items():
            for entry in conn.entries:
                unit.capability_users.setdefault((entry.unit, entry.capability), []).append(
                    ("need", unit, need, entry.config))

ROOT_LINE = re.compile(r"^[\"']?unifold[\"']?\s*:", re.M)


def git_ignored(root: str) -> set:
    """Paths under `root` that git ignores, relative to it with `/`: files, and folders with
    a trailing slash. Empty when git is missing or `root` is not in a work tree. Only
    untracked paths are listed: a file that is committed is part of the project even if a
    pattern matches it."""
    try:
        done = subprocess.run(
            ["git", "ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--directory"],
            cwd=root, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return set()
    if done.returncode != 0:
        return set()
    out = set()
    for item in done.stdout.decode("utf-8", "surrogateescape").split("\0"):
        if item and item != "./":
            out.add(item.replace(os.sep, "/"))
    return out


def is_build_output(path: str) -> bool:
    """Cargo's build folder and Python virtual environments never hold units."""
    name = os.path.basename(path)
    if name == "target":
        return os.path.exists(os.path.join(path, "CACHEDIR.TAG")) \
            or os.path.exists(os.path.join(path, ".rustc_info.json"))
    return os.path.exists(os.path.join(path, "pyvenv.cfg")) if name in ("venv", "env") else False


def find_root(start: str):
    """The nearest folder at or above `start` whose unifold.yaml has the key `unifold`."""
    folder = os.path.realpath(start)
    while True:
        path = os.path.join(folder, MANIFEST)
        if os.path.isfile(path):
            try:
                if ROOT_LINE.search(read_text(path)):
                    return folder
            except OSError:
                return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def open_project(path: str, need_usable=True) -> Project:
    """Find the project that contains `path` (which need not exist) and load it."""
    start = os.path.abspath(path)
    while not os.path.isdir(start):
        parent = os.path.dirname(start)
        if parent == start:
            break
        start = parent
    root = find_root(start)
    if root is None:
        raise Fail("no-project", f"no unifold project found: no {MANIFEST} with the key "
                                 f"'unifold' in {os.path.abspath(path)} or above. "
                                 "Run `unifold init` to start one.")
    project = Project(root)
    if need_usable and not project.usable:
        first = project.findings[0]
        where = first["file"] + (f":{first['line']}" if first["line"] else "")
        raise Fail("bad-root", f"the root manifest is not usable: {where}: {first['message']}")
    return project


def real(path: str) -> str:
    """Absolute path with symlinks in the existing part resolved."""
    return os.path.realpath(os.path.abspath(path))


# -------------------------------------------------------------- resolution

def implementers(unit: Unit, capability: str) -> list:
    """Follow a capability down to the units whose own code implements it."""
    found, conn = [], unit.impl.get(capability)
    if conn:
        for entry in conn.entries:
            found += implementers(entry.unit, entry.capability)
    return found or [(unit, capability)]


def final_users(unit: Unit, need: str) -> list:
    """Follow an own need down to the units whose own code uses it."""
    found = []
    for child, name in unit.need_users.get(need, ()):
        found += final_users(child, name)
    return found or [(unit, need)]


def providers_of(unit: Unit, need: str) -> list:
    """Who finally provides for a need of `unit`, resolved through all levels."""
    inside = unit.inner.get(need)
    if inside is not None:                  # met inside: followed down, not up
        return [{"where": "unit", "unit": target, "capability": capability, "config": entry.config}
                for entry in inside.entries
                for target, capability in implementers(entry.unit, entry.capability)]
    parent = unit.parent
    if parent is None:
        return [{"where": "outside", "capability": need, "config": None}]
    conn = parent.conn.get((unit, need))
    if conn is None:
        return []
    out = []
    for entry in conn.entries:
        if entry.kind == "child":
            for target, capability in implementers(entry.unit, entry.capability):
                out.append({"where": "unit", "unit": target, "capability": capability,
                            "config": entry.config})
        else:
            for item in providers_of(parent, entry.capability):
                out.append({**item, "config": item["config"] or entry.config})
    return out


def users_of(unit: Unit, capability: str) -> list:
    """Who finally uses a capability of `unit`, resolved through all levels."""
    parent = unit.parent
    if parent is None:
        return [{"where": "outside", "need": capability, "config": None}]
    out = []
    for use in parent.capability_users.get((unit, capability), ()):
        if use[0] == "need":
            for user, need in final_users(use[1], use[2]):
                out.append({"where": "unit", "unit": user, "need": need, "config": use[3]})
        else:
            out += users_of(parent, use[1])
    return out


def find_cycles(graph: dict) -> list:
    """One cycle per group of nodes that can reach each other. No recursion."""
    index, low, on_stack, stack, groups = {}, {}, set(), [], []
    for start in sorted(graph):
        if start in index:
            continue
        work = [(start, iter(sorted(graph.get(start, ()))))]
        index[start] = low[start] = len(index)
        stack.append(start)
        on_stack.add(start)
        while work:
            node, targets = work[-1]
            advanced = False
            for target in targets:
                if target not in index:
                    index[target] = low[target] = len(index)
                    stack.append(target)
                    on_stack.add(target)
                    work.append((target, iter(sorted(graph.get(target, ())))))
                    advanced = True
                    break
                if target in on_stack:
                    low[node] = min(low[node], index[target])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                group = set()
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    group.add(member)
                    if member == node:
                        break
                if len(group) > 1 or node in graph.get(node, ()):
                    groups.append(group)
    cycles = []
    for group in groups:
        first = min(group)
        path, seen = [first], {first}
        while True:                           # walk inside the group until it closes
            nexts = sorted(t for t in graph.get(path[-1], ()) if t in group)
            step = next((t for t in nexts if t not in seen), None)
            if first in nexts and len(path) > 1 or nexts == [first] or step is None:
                break
            path.append(step)
            seen.add(step)
        cycles.append(path)
    return sorted(cycles)


# ------------------------------------------------------------ check rules

def check_manifest(project: Project, unit: Unit):
    where, manifest, lines = unit.manifest_path, unit.manifest, unit.lines
    todo = []

    def bad(message, *key, fix=None):
        project.add("M2", where, message, lines.get(tuple(key)) if key else None, fix)

    def summary_of(value, label, *key, field="summary"):
        if not isinstance(value, str) or not value.strip():
            bad(f"{label} needs a '{field}': one line of text", *key)
        elif "\n" in value.strip():
            bad(f"the {field} of {label} must be one line", *key)
        elif PLACEHOLDER.match(value.strip()):
            bad(f"the {field} of {label} is a placeholder ({value.strip()}); write the "
                f"{field}, or `TODO` for a draft", *key)
        elif TODO.match(value.strip()):
            todo.append(label)

    for key in manifest:
        if not isinstance(key, str):
            bad(f"key {show_value(key)} is not text; quote it")
        elif key.startswith("x-") or key in UNIT_KEYS:
            continue
        elif key in ROOT_KEYS:
            if not unit.is_root:
                bad(f"key '{key}' belongs in the root manifest", key)
        elif key == "unit":
            bad("key 'unit' is not used: the name of a unit is the name of its folder"
                + (" (the root may set `name`)" if unit.is_root else ""), key,
                fix="Delete the line.")
        elif key == "summary":
            bad("key 'summary' on a unit is 'responsibility' since unifold 0.3: what the unit is "
                "responsible for, in one sentence", key, fix="Rename the key to `responsibility`.")
        else:
            close = difflib.get_close_matches(key.lower(), ROOT_KEYS + UNIT_KEYS, 1)
            hint = f"; did you mean '{close[0]}'?" if close else ""
            bad(f"unknown key '{key}'{hint}", key)
    summary_of(manifest.get("responsibility"), "the unit", "responsibility", field="responsibility")
    for key in ("kind", "owner", "name", "diagram-links"):
        if key in manifest and not _text(manifest[key]):
            bad(f"'{key}' must be text, not {show_value(manifest[key])}", key)
    if unit.children and not unit.is_root and not unit.kind:
        bad("a unit with children states a `kind`: what the box is to its parent's wiring "
            "(`logic`, `stateful`, `adapter`, or a word of the project)", fix="Add `kind:` to the manifest.")
    if unit.kind and unit.kind not in WELL_KNOWN_KINDS:
        project.add("K1", where, f"kind '{unit.kind}' is not one of {', '.join(WELL_KNOWN_KINDS)}; "
                                 "no rule applies to it", lines.get(("kind",)))
    check_unit_fields(project, unit)
    for key, allowed in (("status", STATUSES), ("diagrams", DIAGRAM_MODES)):
        value = manifest.get(key, allowed[0])
        if key in manifest and (not isinstance(value, str) or value not in allowed):
            hint = " (YAML reads yes, no, on and off as true and false)" \
                if isinstance(value, bool) else ""
            bad(f"'{key}' is {show_value(value)}; allowed: {', '.join(allowed)}{hint}", key)
    if unit.is_root:
        ignore = manifest.get("ignore")
        if ignore is not None and (not isinstance(ignore, list)
                                   or not all(isinstance(p, str) and p.strip() for p in ignore)):
            bad("'ignore' must be a list of folders, for example `ignore: [vendor]`", "ignore")
        limit = manifest.get("max-lines")
        if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 1):
            bad(f"'max-lines' must be a positive number, not {show_value(limit)}", "max-lines")
        links = _text(manifest.get("diagram-links"))
        if links and links not in ("none", "relative") and not re.match(r"^https?://", links):
            bad("'diagram-links' is `none`, `relative` or the base URL of the repository's "
                f"file view, not '{links}'", "diagram-links")
    for section, allowed in (("capabilities", CAPABILITY_KEYS), ("needs", NEED_KEYS)):
        raw = manifest.get(section)
        if raw is None:
            continue
        if not isinstance(raw, dict):
            bad(f"'{section}' must be a mapping of names, not {show_value(raw)}", section)
            continue
        what = "capability" if section == "capabilities" else "need"
        for name, spec in raw.items():
            label = f"{what} '{name}'"
            if not isinstance(name, str) or not ENTRY_NAME.match(name):
                bad(f"the name of {label} may contain only letters, digits, '-' and '_'",
                    section, str(name))
            if isinstance(spec, str):
                summary_of(spec, label, section, name)
                continue
            if not isinstance(spec, dict):
                bad(f"{label} must be a summary text or a mapping with 'summary', not "
                    f"{show_value(spec)}", section, str(name))
                continue
            summary_of(spec.get("summary"), label, section, name)
            for key, value in spec.items():
                if isinstance(key, str) and (key in allowed or key.startswith("x-")
                                             or key in ("platform", "verified-by")):
                    continue                          # platform and verified-by are reported below
                if value is None and isinstance(key, str) and " " in key:
                    bad(f"{label}: '{key}' is read as a key. A comma inside `{{...}}` ends "
                        "the value: quote the summary, or write the entry on separate lines",
                        section, name)
                elif key == "optional":
                    bad(f"{label}: 'optional' is allowed on a need only", section, name, key)
                else:
                    close = difflib.get_close_matches(str(key).lower(), allowed, 1)
                    hint = f"; did you mean '{close[0]}'?" if close else ""
                    bad(f"{label}: unknown key '{key}'{hint}", section, name, str(key))
            if "kind" in spec and not _text(spec["kind"]):
                bad(f"{label}: 'kind' must be text, not {show_value(spec['kind'])}",
                    section, name, "kind")
            if "optional" in spec and not isinstance(spec["optional"], bool):
                bad(f"{label}: 'optional' must be true or false, not "
                    f"{show_value(spec['optional'])}", section, name, "optional")
            if "platform" in spec:
                if not isinstance(spec["platform"], bool):
                    bad(f"{label}: 'platform' must be true or false, not "
                        f"{show_value(spec['platform'])}", section, name, "platform")
                elif section != "needs" or not unit.is_root:
                    bad(f"{label}: 'platform' is allowed on a need of the root only; it marks a "
                        "service of the host such as time or randomness", section, name, "platform")
            if "verified-by" in spec:
                bad(f"{label}: 'verified-by' was removed in unifold 0.3; nothing ran it", section, name,
                    "verified-by", fix="Delete the line. The examples of the contract are the tests.")
            if "contract" in spec:
                check_contract_key(project, unit, label, spec["contract"], section, name)
    raw = manifest.get("wiring")
    if raw is not None and not isinstance(raw, dict):
        bad(f"'wiring' must be a mapping of need to provider, not {show_value(raw)}", "wiring")
    for line, message in unit.schema_problems:
        project.add("M2", where, message, line)
    if todo:
        shown = ", ".join(todo[:6]) + (f" and {len(todo) - 6} more" if len(todo) > 6 else "")
        project.add("M10", where, f"TODO instead of a text: {shown}", lines.get(("responsibility",)))


def check_contract_key(project: Project, unit: Unit, label: str, value, section: str, name: str):
    """`contract` is a path, or a mapping with `path` and `parts` (rules M2, M7, M11)."""
    where, lines = unit.manifest_path, unit.lines
    line = lines.get((section, name, "contract"))
    parts = None
    if isinstance(value, dict):
        unknown = [k for k in value if k not in ("path", "parts")]
        if unknown:
            project.add("M2", where, f"{label}: 'contract' has the keys `path` and `parts`, not "
                                     f"'{unknown[0]}'", line)
        parts = value.get("parts")
        if parts is not None and (not isinstance(parts, list)
                                  or not all(isinstance(x, str) and x.strip() for x in parts)):
            project.add("M2", where, f"{label}: 'parts' must be a list of part names", line)
            parts = None
        value = value.get("path")
    if not isinstance(value, str) or not value.strip():
        project.add("M2", where, f"{label}: 'contract' must be one path, or a mapping with `path` and "
                                 f"`parts`, not {show_value(value)}", line)
        return
    problem = path_problem(project, unit, value.strip(), True)
    if problem:
        project.add("M7", where, f"{label}: 'contract' {problem}: {value.strip()}", line)
        return
    if parts:
        contract = contract_of_path(project, contract_target(project, unit, value.strip())[1])
        for part in parts:
            if part not in contract["parts"]:
                known = ", ".join(contract["parts"]) or "none"
                project.add("M11", where, f"{label}: part '{part}' is not a part of {project.rel(contract['path'])} "
                                          f"(its parts: {known})", line)


def check_unit_fields(project: Project, unit: Unit):
    """`secret` (K5) and `not` (K6)."""
    where, lines, manifest = unit.manifest_path, unit.lines, unit.manifest
    if "secret" in manifest:
        secret, line = manifest["secret"], lines.get(("secret",))
        if not isinstance(secret, dict) or set(secret) - {"what", "decision"} or not secret:
            project.add("K5", where, "`secret` is a mapping with `what` and `decision`", line)
        else:
            what = secret.get("what")
            if not isinstance(what, str) or not what.strip() or "\n" in what.strip():
                project.add("K5", where, "`secret.what` is one line of text", lines.get(("secret", "what"), line))
            decision = secret.get("decision")
            if not isinstance(decision, str) or not decision.strip():
                project.add("K5", where, "`secret.decision` is a path to a decision",
                            lines.get(("secret", "decision"), line))
            else:
                problem = decision_problem(project, unit, decision.strip())
                if problem:
                    project.add("K5", where, f"`secret.decision` {problem}: {decision.strip()}",
                                lines.get(("secret", "decision"), line))
    if "not" in manifest:
        items, line = manifest["not"], lines.get(("not",))
        if not isinstance(items, list):
            project.add("K6", where, f"`not` is a list, not {show_value(items)}", line)
        else:
            for item in items:
                if isinstance(item, str):
                    if not item.strip() or "\n" in item.strip():
                        project.add("K6", where, "an item of `not` is one line of text", line)
                elif isinstance(item, dict) and len(item) == 1:
                    text, need = next(iter(item.items()))
                    if not isinstance(need, str) or need not in unit.needs:
                        project.add("K6", where, f"`not` item '{text}' names '{need}', which is not a need of "
                                                 f"this unit (needs: {', '.join(unit.needs) or 'none'})", line)
                else:
                    project.add("K6", where, "an item of `not` is one line of text, or one line mapped to a "
                                             f"need of this unit, not {show_value(item)}", line)


def decision_problem(project: Project, unit: Unit, value: str):
    """Why a `secret.decision` path is not acceptable, or None."""
    if SCHEME.match(value) or os.path.isabs(value):
        return "must be a path relative to the manifest"
    target = os.path.normpath(os.path.join(unit.path, value))
    if not project.inside(target):
        return "points outside the project"
    if project.kind_of(target) != "file":
        return "does not exist"
    kind, owner = project.owner_of(target)
    if kind != "unit" or (owner is not unit and owner not in unit.ancestors()):
        return "is not a decision of this unit or of an ancestor"
    folder = os.path.join(owner.path, "docs", "decisions") + os.sep
    if not target.startswith(folder) or not DECISION_FILE.match(os.path.basename(target)):
        return "is not a file in docs/decisions/ of this unit or of an ancestor"
    return None


def path_problem(project: Project, unit: Unit, value: str, contract: bool = True):
    """Why a contract value is not acceptable, or None."""
    if SCHEME.match(value) and not re.match(r"^[A-Za-z]:[\\/]", value):
        return "must be a reference in docs/references/, not a URL; the reference links the URL" \
            if contract else None
    if os.path.isabs(value) or re.match(r"^[A-Za-z]:[\\/]", value):
        return "must be a path relative to the manifest" + ("" if contract else ", or a URL")
    target = os.path.normpath(os.path.join(unit.path, value.split("#", 1)[0]))
    if not project.inside(target):
        return "points outside the project"
    if not project.kind_of(target):
        return "does not exist"
    kind, owner = project.owner_of(target)
    if kind == "foreign":
        return "lies in a nested project"
    if owner is not unit and owner not in unit.ancestors() and unit not in owner.ancestors():
        return f"lies in the sibling unit '{owner.rel}'"
    if not contract:
        return None
    if owner is not unit and owner not in unit.ancestors():
        return f"lies in the unit '{owner.rel}' below; a contract lies in the unit that wires the connection"
    if not target.startswith(os.path.join(owner.path, "docs", "references") + os.sep) \
            or not target.endswith(".md"):
        return "is not a Markdown file in docs/references/"
    return None


def contract_target(project: Project, unit: Unit, value):
    """(display text, absolute path or None, URL or None) for a contract value."""
    if not value:
        return "", None, None
    if SCHEME.match(value):
        return value, None, value
    target = os.path.normpath(os.path.join(unit.path, value.split("#", 1)[0]))
    return project.rel(target), target, None


def check_wiring(project: Project, unit: Unit):
    where = unit.manifest_path
    wiring_line = unit.lines.get(("wiring",))
    for line, message in unit.problems:
        project.add("W1", where, message, line)
    if unit.broken:
        return
    graph: dict = {}
    reported = set()

    def contract_of(owner: Unit, spec: dict):
        shown, target, url = contract_target(project, owner, spec.get("contract"))
        return url or target or None

    def contracts_agree(key: str, side: Unit, side_spec: dict, side_text: str,
                        other: Unit, other_spec: dict, other_text: str, line):
        if other.broken:                     # its manifest is reported once, as M1
            return
        mine, theirs = contract_of(side, side_spec), contract_of(other, other_spec)
        if mine is None and key not in reported:
            reported.add(key)
            project.add("W11", where, f"{side_text} names no contract", line)
        if theirs is None and other_text not in reported:
            reported.add(other_text)
            project.add("W11", where, f"{other_text} names no contract", line)
        if mine is not None and theirs is not None and mine != theirs:
            project.add("W11", where, f"{side_text} names the contract "
                                      f"{project.rel(mine) if os.path.isabs(mine) else mine}, "
                                      f"{other_text} names {project.rel(theirs) if os.path.isabs(theirs) else theirs}",
                        line)

    for child in unit.children:
        if child.broken:
            continue
        ref = child.ref_in_parent()
        for need, spec in child.needs.items():
            conn = unit.conn.get((child, need))
            if conn is None:
                if not spec["optional"] and need not in child.inner:
                    offers = [c.ref_in_parent() + "." + need for c in unit.children[:2000]
                              if c is not child and need in c.capabilities]
                    up = f"and pass it up (`{ref}.{need}: {need}`)"
                    fix = f"Add `{ref}.{need}: {offers[0]}` to the wiring." if offers else \
                        (f"Add `{ref}.{need}: <provider>` to the wiring of this manifest, or "
                         f"declare a need `{need}` here {up}" +
                         ("." if not unit.is_root else " to the outside world."))
                    project.add("W2", where, f"need '{ref}.{need}' has no provider",
                                wiring_line, fix)
                continue
            for entry in conn.entries:
                if entry.kind == "child":
                    graph.setdefault(ref, set()).add(entry.unit.ref_in_parent())
                    other_spec = entry.unit.capabilities.get(entry.capability, {})
                    other = other_spec.get("kind", "")
                    contracts_agree(f"{ref}.{need}", child, spec, f"need '{ref}.{need}'",
                                    entry.unit, other_spec, f"capability '{entry.raw}'", conn.line)
                else:
                    other_spec = unit.needs[entry.capability]
                    other = other_spec["kind"]
                    contracts_agree(f"{ref}.{need}", child, spec, f"need '{ref}.{need}'",
                                    unit, other_spec, f"need '{entry.capability}' of this unit",
                                    conn.line)
                if spec["kind"] and other and spec["kind"] != other:
                    project.add("W4", where, f"'{ref}.{need}' is of kind '{spec['kind']}', its "
                                             f"provider '{entry.raw}' of kind '{other}'", conn.line)
            if child.status == "active" and not spec["optional"] \
                    and not child.need_users.get(need):
                default = conn.entries[0].config
                for item in providers_of(child, need):
                    if item["where"] == "unit" and item["config"] in (None, default) \
                            and item["unit"].status != "active":
                        project.add("W9", where, f"active unit '{ref}' gets '{need}' from "
                                                 f"'{item['unit'].rel}', which is "
                                                 f"{item['unit'].status}", conn.line)
        for capability in child.capabilities:
            if not unit.capability_users.get((child, capability)):
                project.add("W3", where, f"'{ref}.{capability}' is provided but nothing uses it",
                            wiring_line)
    for capability, conn in unit.impl.items():
        spec = unit.capabilities[capability]
        kind = spec["kind"]
        for entry in conn.entries:
            other_spec = entry.unit.capabilities.get(entry.capability, {})
            other = other_spec.get("kind", "")
            contracts_agree(capability, unit, spec, f"capability '{capability}' of this unit",
                            entry.unit, other_spec, f"capability '{entry.raw}'", conn.line)
            if kind and other and kind != other:
                project.add("W4", where, f"capability '{capability}' is of kind '{kind}', the capability "
                                         f"'{entry.raw}' that implements it of kind '{other}'",
                            conn.line)
    for need, conn in unit.inner.items():
        spec = unit.needs[need]
        for entry in conn.entries:
            other_spec = entry.unit.capabilities.get(entry.capability, {})
            other = other_spec.get("kind", "")
            contracts_agree(f"need '{need}' of this unit", unit, spec, f"need '{need}' of this unit",
                            entry.unit, other_spec, f"capability '{entry.raw}'", conn.line)
            if spec["kind"] and other and spec["kind"] != other:
                project.add("W4", where, f"need '{need}' of this unit is of kind '{spec['kind']}', "
                                         f"its provider '{entry.raw}' of kind '{other}'", conn.line)
        if unit.status == "active" and not spec["optional"]:
            default = conn.entries[0].config
            for item in providers_of(unit, need):
                if item["where"] == "unit" and item["config"] in (None, default) \
                        and item["unit"].status != "active":
                    project.add("W9", where, f"active unit '{unit.rel}' gets '{need}' from "
                                             f"'{item['unit'].rel}', which is "
                                             f"{item['unit'].status}", conn.line)
    for cycle in find_cycles(graph):
        project.add("W7", where, "children need each other in a cycle: "
                    + " -> ".join(cycle + [cycle[0]]), wiring_line)


# ----- documents

def managed_files(project: Project, unit: Unit) -> list:
    """The hand-written Markdown files of a unit that the document rules cover: README.md
    and the files in docs/decisions, docs/explanation, docs/references, docs/skills and
    docs/tutorials. AGENTS.md is generated and not among them."""
    readme = os.path.join(unit.path, "README.md")
    files = [readme] if project.kind_of(readme) == "file" else []
    doc = os.path.join(unit.path, "docs")
    for name in ("decisions", "explanation", "references", "skills", "tutorials"):
        top = os.path.join(doc, name)
        if project.kind_of(top) != "dir":
            continue
        for folder, subs, names in os.walk(top):
            subs[:] = sorted(s for s in subs if not s.startswith(".") and not (
                name == "skills" and s in ("assets", "scripts")
                and os.path.dirname(folder) == top)
                and not project.is_ignored(os.path.join(folder, s)))
            for file_name in sorted(names):
                path = os.path.join(folder, file_name)
                if file_name.endswith(".md") and not project.is_ignored(path):
                    files.append(path)
    return files


def generated_location(unit: Unit, path: str) -> bool:
    """Whether the generator owns this path of the unit: diagrams, the decision index and
    AGENTS.md."""
    doc = os.path.join(unit.path, "docs")
    return os.path.dirname(path) == os.path.join(doc, "diagrams") \
        or path == os.path.join(doc, "decisions", "index.md") \
        or path == os.path.join(unit.path, "AGENTS.md")


def documents_of(project: Project, unit: Unit) -> dict:
    """The hand-written documents of a unit by kind, as AGENTS.md and `show` list them:
    {"tutorials": [...], "references": [...], "explanation": [...]} of (text, path).

    Tutorials are the `.md` files of docs/tutorials/, by name. References are the `.md`
    files directly in docs/references/ and, for a sub-folder with an index.md, that index
    under the folder's name, in one alphabetical order. Explanation files come in the fixed
    order context, requirements, reasoning, invariants, runtime, deployment, risks, then
    the other files by name.
    """
    docs = os.path.join(unit.path, "docs")

    def entries(folder: str) -> list:
        return project.listdir(folder) if project.kind_of(folder) == "dir" else []

    def md_files(folder: str) -> list:
        return [n for n in entries(folder)
                if n.endswith(".md") and os.path.isfile(os.path.join(folder, n))]

    out: dict = {"tutorials": [], "references": [], "explanation": []}
    folder = os.path.join(docs, "tutorials")
    out["tutorials"] = [(n[:-3], os.path.join(folder, n)) for n in md_files(folder)]
    folder = os.path.join(docs, "references")
    for name in entries(folder):
        path = os.path.join(folder, name)
        if name.endswith(".md") and os.path.isfile(path):
            out["references"].append((name[:-3], path))
        elif os.path.isdir(path) and os.path.isfile(os.path.join(path, "index.md")):
            out["references"].append((name, os.path.join(path, "index.md")))
    folder = os.path.join(docs, "explanation")
    names = md_files(folder)
    fixed = [n for n in (f"{k}.md" for k in EXPLANATION_ORDER) if n in names]
    out["explanation"] = [(n[:-3], os.path.join(folder, n))
                          for n in fixed + [n for n in names if n not in fixed]]
    return out


def skills_of(project: Project, unit: Unit) -> list:
    out, folder = [], os.path.join(unit.path, "docs", "skills")
    if project.kind_of(folder) != "dir":
        return out
    for name in project.listdir(folder):
        path = os.path.join(folder, name)
        if not os.path.isdir(path):
            continue
        skill = os.path.join(path, "SKILL.md")
        meta = project.doc(skill).meta if project.kind_of(skill) == "file" else None
        meta = meta if isinstance(meta, dict) else {}
        out.append({"name": name, "folder": path, "path": skill,
                    "exists": project.kind_of(skill) == "file",
                    "meta-name": meta.get("name"),
                    "description": " ".join(_text(meta.get("description")).split())})
    return out


def decisions_of(project: Project, unit: Unit) -> list:
    folder = os.path.join(unit.path, "docs", "decisions")
    if project.kind_of(folder) != "dir":
        return []
    out = []
    for name in project.listdir(folder):
        path = os.path.join(folder, name)
        if name.endswith(".md") and name != "index.md" and os.path.isfile(path):
            out.append(decision_info(project, path))
    return out


def decision_info(project: Project, path: str) -> dict:
    doc = project.doc(path)
    meta = doc.meta if isinstance(doc.meta, dict) else {}
    status = meta.get("status")
    date = meta.get("date")
    answer = next((h for h in doc.headings if h[1] == 2 and h[3] == "answer"), None)
    answer_empty = None
    if answer is not None:
        section = doc.section(answer[3]) or []
        answer_empty = not any(line.strip() for line in section[1:])
    return {"path": path, "name": os.path.basename(path),
            "title": doc.title() or os.path.basename(path)[:-3],
            "status": " ".join(status.split()) if isinstance(status, str) else "",
            "raw-status": status,
            "date": date.isoformat() if hasattr(date, "isoformat") else str(date or ""),
            "makers": meta.get("decision-makers"), "error": doc.meta_error,
            "derived-from": " ".join(_text(meta.get("derived-from")).split()) or None,
            "source-says": any(h[1] == 2 and h[3] == "source-says" for h in doc.headings),
            "answer": None if answer is None else {"empty": answer_empty},
            "has-meta": doc.meta is not None and bool(meta)}


def status_mark(status: str) -> str:
    """How a status that is not in force is shown to readers and agents."""
    return {"planned": "planned: not built yet", "deprecated": "deprecated: to be removed",
            "proposed": "proposed: not accepted, does not bind",
            "derived": "derived: a source settles it; binds until a person accepts it"}.get(status, status)


def context_items(doc: Doc) -> list:
    """The items of a docs/explanation/context.md: heading, link, stamp, Says and Here."""
    items, current = [], None
    heading_lines = {h[0]: h for h in doc.headings}
    for number, line in doc.prose:
        heading = heading_lines.get(number)
        if heading:
            current = None
            if heading[1] == 3:
                link = INLINE_LINK.search(heading[2])
                target = link.group(1) if link else None
                if target and target.startswith("<"):
                    target = target[1:-1]
                current = {"line": number, "heading": heading[2], "link": target,
                           "stamp": None, "stamp-line": None, "says": [], "here": False,
                           "part": None, "first": True}
                items.append(current)
            continue
        if current is None or not line.strip():
            continue
        match = STAMP.match(line.strip())
        if match and current["first"]:
            current["stamp"], current["stamp-line"] = match.group(1), number
        elif re.match(r"^Says\b", line):
            current["part"] = "says"
        elif re.match(r"^Here\b", line):
            current["part"], current["here"] = "here", True
        if current["part"] == "says":
            current["says"].append(line.strip())
        current["first"] = False
    for item in items:
        text = " ".join(item["says"])
        item["has-says"] = bool(item["says"])
        item["says"] = re.sub(r"^Says\s*[:,]?\s*", "", text)
        title = re.sub(r"\]\(.*$", "", item["heading"]).lstrip("[").strip()
        item["title"] = title or item["heading"]
    return items


def cited_hash(project: Project, context_path: str, link: str):
    """(hash or None, problem or None) of what a context item cites."""
    if not link or SCHEME.match(link) or link.startswith(("#", "/")):
        return None, None
    rel_path, anchor = split_link(link)
    target = os.path.normpath(os.path.join(os.path.dirname(context_path), rel_path))
    if project.kind_of(target) != "file":
        return None, None                            # a broken link is rule L1
    doc = project.doc(target)
    if anchor:
        section = doc.section(anchor.lower())
        if section is None:
            return None, (f"'#{anchor}' is neither a heading nor the first cell of a table "
                          f"row in {project.rel(target)}")
        return content_hash(section), None
    return content_hash(doc.lines), None


def check_documents(project: Project, unit: Unit):
    """The document conventions for the files of one unit."""
    if unit.broken:
        return
    readme = os.path.join(unit.path, "README.md")
    docs = os.path.join(unit.path, "docs")
    context = os.path.join(docs, "explanation", "context.md")
    if project.kind_of(readme) != "file":
        project.add("S3", unit.path, "the unit has no README.md")
    if project.kind_of(docs) == "dir":
        for name in project.listdir(docs):
            if name not in DOC_KINDS:
                project.add("S12", os.path.join(docs, name),
                            f"'{name}' is not one of the folders of docs/: " + ", ".join(DOC_KINDS))
    for skill in skills_of(project, unit):
        if not skill["exists"]:
            project.add("S7", skill["folder"], "skill folder has no SKILL.md")
            continue
        doc = project.doc(skill["path"])
        if doc.meta_error or not isinstance(doc.meta, dict):
            project.add("S7", skill["path"], doc.meta_error or "SKILL.md needs YAML front matter "
                                                               "with `name` and `description`", 1)
        else:
            if skill["meta-name"] != skill["name"]:
                project.add("S7", skill["path"], f"`name` is {show_value(skill['meta-name'])}; "
                                                 f"it must equal the folder name '{skill['name']}'", 2)
            if not skill["description"]:
                project.add("S7", skill["path"], "the skill needs a `description`", 2)
    check_decisions(project, unit)
    for path in managed_files(project, unit):
        if generated_location(unit, path):
            continue
        doc = project.doc(path)
        if len(doc.lines) > project.max_lines:
            project.add("T1", path, f"{len(doc.lines)} lines; the limit is {project.max_lines}")
        check_links(project, unit, path, doc, path == context)
    if project.kind_of(readme) == "file":
        doc, section = project.doc(readme), ""
        for number, level, text, _ in doc.headings:
            if level <= 2:
                section = text.strip().lower() if level == 2 else ""
            elif level == 3 and section in ("capabilities", "needs"):
                names = [m.group(2) for m in CODE_SPAN.finditer(text)]
                known = unit.capabilities if section == "capabilities" else unit.needs
                if names and names[0] not in known:
                    close = difflib.get_close_matches(names[0], list(known), 1)
                    hint = f"; did you mean '{close[0]}'?" if close else ""
                    project.add("T5", readme, f"heading '{names[0]}' under '## "
                                              f"{section.title()}' is not in the manifest{hint}", number)
        for index, (number, level, text, _) in enumerate(doc.headings):
            if level == 2 and text.strip().lower() == "why":
                end = next((n for n, lvl, _, _ in doc.headings[index + 1:] if lvl <= 2),
                           len(doc.lines) + 1)
                why = sum(1 for line in doc.lines[number:end - 1] if line.strip())
                if why > MAX_WHY_LINES:
                    project.add("T4", readme, f"'## Why' has {why} lines that are not blank; "
                                              f"at most {MAX_WHY_LINES}", number)
                break
    if project.kind_of(context) == "file":
        check_context(project, unit, context)
    check_constants(project, unit)


def constants_table(project: Project, unit: Unit):
    """The nearest docs/references/constants.md of `unit` or an ancestor: (path, names, pattern), or None."""
    for owner in [unit] + unit.ancestors():
        path = os.path.join(owner.path, "docs", "references", "constants.md")
        if project.kind_of(path) == "file":
            return constants_of(project, path)
    return None


def constants_of(project: Project, path: str):
    doc = project.doc(path)
    names, prose = set(), doc.prose
    for index, (number, line) in enumerate(prose):
        text = line.strip()
        if not text.startswith("|") or TABLE_RULE.match(text):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", text.strip("|"))]
        if index + 1 < len(prose) and TABLE_RULE.match(prose[index + 1][1].strip()):
            if len(cells) < 2 or cells[0].strip("`* ").lower() != "name" or cells[1].strip("`* ").lower() != "value":
                return None                     # another table: not a constants table
            continue
        if cells:
            names.add(heading_slug(cells[0]).upper().replace("-", "_"))
            names.add(re.sub(r"[`*]", "", cells[0]).strip())
    meta = doc.meta if isinstance(doc.meta, dict) else {}
    pattern = meta.get("name-pattern") if isinstance(meta.get("name-pattern"), str) else CONSTANT_PATTERN
    try:
        compiled = re.compile(pattern)
    except re.error:
        compiled = re.compile(CONSTANT_PATTERN)
    return path, names, compiled


def check_constants(project: Project, unit: Unit):
    """T6: every constant name in a code span of a hand-written document is a row of a constants table."""
    tables = []
    for owner in [unit] + unit.ancestors():
        path = os.path.join(owner.path, "docs", "references", "constants.md")
        if project.kind_of(path) == "file":
            found = constants_of(project, path)
            if found:
                tables.append(found)
    if not tables:
        return
    nearest, names, pattern = tables[0]
    for _, more, _ in tables[1:]:
        names = names | more
    for path in managed_files(project, unit):
        if generated_location(unit, path):
            continue
        doc = project.doc(path)
        for number, line in doc.prose:
            for match in CODE_SPAN.finditer(line):
                for name in pattern.findall(match.group(2)):
                    name = name if isinstance(name, str) else name[0]
                    if name and name not in names:
                        project.add("T6", path, f"`{name}` is not a row of {project.rel(nearest)}", number)


def check_decisions(project: Project, unit: Unit):
    infos = decisions_of(project, unit)
    numbers: dict = {}
    for info in infos:
        match = DECISION_FILE.match(info["name"])
        if match:
            numbers.setdefault(match.group(1), []).append(info["name"])
    for info in infos:
        path, match = info["path"], DECISION_FILE.match(info["name"])
        if not match:
            project.add("S9", path, "a decision file is named like 0001-short-title.md "
                                    "(four digits, then lower-case words with hyphens)")
        elif numbers[match.group(1)][0] != info["name"]:
            project.add("S9", path, f"decision number {match.group(1)} is used twice (also by "
                                    f"{numbers[match.group(1)][0]})")
        if info["error"] or not info["has-meta"]:
            project.add("S9", path, info["error"] or "a decision needs YAML front matter with "
                                                     "`status` and `date`", 1)
            continue
        status = DECISION_STATUS.match(info["status"])
        if not status:
            project.add("S9", path, f"status is {show_value(info['raw-status'])}; allowed: "
                                    "proposed, accepted, rejected, deprecated, superseded by NNNN, derived", 2)
        elif status.group(2) and status.group(2) not in numbers:
            project.add("S9", path, f"status names decision {status.group(2)}, which does not "
                                    "exist in this unit", 2)
        if not ISO_DATE.match(info["date"]):
            project.add("S9", path, "a decision needs a `date` in the form 2026-10-07"
                        + (f", not '{info['date']}'" if info["date"] else ""), 2)
        if info["status"] == "accepted" and not info["makers"]:
            project.add("S9", path, "an accepted decision names its `decision-makers`", 2)
        if info["status"] == "derived":
            if not info["derived-from"]:
                project.add("S9", path, "a derived decision names the passage in `derived-from`", 2)
            if not info["source-says"]:
                project.add("S9", path, "a derived decision has a section `## Source says` that restates "
                                        "the passage", 2)


def manifest_targets(project: Project, unit: Unit) -> set:
    """The files that the manifest of `unit` names as contract."""
    out = set()
    for entries in (unit.capabilities, unit.needs):
        for spec in entries.values():
            target = contract_target(project, unit, spec.get("contract"))[1]
            if target:
                out.add(target)
    return out


def check_links(project: Project, unit: Unit, path: str, doc: Doc, is_context: bool):
    base = os.path.dirname(path)
    for line, link in doc.links:
        if SCHEME.match(link) or link.startswith("//"):
            continue
        if link.startswith("#"):
            anchor = unquote(link[1:]).lower()
            if anchor and anchor not in doc.anchors():
                project.add("L1", path, f"no heading or table row for the anchor {link}", line)
            continue
        if link.startswith("/"):
            project.add("L2", path, f"absolute link '{link}'; links are relative", line,
                        "Write the link relative to this file.")
            continue
        rel_path, anchor = split_link(link)
        target = os.path.normpath(os.path.join(base, rel_path))
        kind = project.kind_of(target)
        if not kind:
            hint, folder = "", os.path.dirname(target)
            if project.kind_of(folder) == "dir":
                close = difflib.get_close_matches(os.path.basename(target), os.listdir(folder), 1)
                hint = f"; did you mean '{close[0]}'?" if close else ""
            project.add("L1", path, f"link target does not exist: {link}{hint}", line)
            continue
        if anchor and kind == "file" and target.endswith(".md") \
                and anchor.lower() not in project.doc(target).anchors():
            project.add("L1", path, f"no heading or table row for the anchor in {link}", line)
        if target in manifest_targets(project, unit):
            continue
        owner_kind, owner = project.owner_of(target)
        if owner_kind is None:
            project.add("L2", path, f"link leaves the project: {link}", line,
                        "Cite things outside the project by full URL.")
        elif owner_kind == "foreign":
            if project.foreign[owner] is not unit or \
                    target not in (owner, os.path.join(owner, "README.md")):
                project.add("L11", path, "a nested project is linked only by its README.md, "
                                        f"from the unit that contains it: {link}", line)
        elif owner is unit:
            continue
        elif owner.parent is unit:
            if target not in (owner.path, os.path.join(owner.path, "README.md")):
                project.add("L11", path, f"link into the child '{owner.name}' must target its "
                                        f"README.md: {link}", line)
        elif owner.depth_below(unit) is not None:
            project.add("L11", path, f"link reaches into '{owner.rel}', below a child; link to "
                                    f"the README.md of the direct child instead: {link}", line)
        elif unit.depth_below(owner) is not None:
            decisions = os.path.join(owner.path, "docs", "decisions") + os.sep
            references = os.path.join(owner.path, "docs", "references") + os.sep
            if not is_context:
                project.add("L11", path, f"upward link outside docs/explanation/context.md: {link}",
                            line, "Cite it as an item in docs/explanation/context.md and link to "
                                  "that file.")
            elif not (target == os.path.join(owner.path, "README.md")
                      or target.startswith((decisions, references))):
                project.add("L11", path, "docs/explanation/context.md cites only an ancestor's "
                                        f"README.md, decisions and references: {link}", line)
            elif target.startswith(decisions) and target.endswith(".md") \
                    and os.path.basename(target) != "index.md" and kind == "file":
                status = decision_info(project, target)["status"]
                if status.startswith(("rejected", "deprecated", "superseded")):
                    project.add("L7", path, f"cites a decision that is {status}: {link}", line)
                elif status == "proposed" and unit.status == "active":   # derived binds
                    project.add("L7", path, "an active unit relies on a decision that is "
                                            f"still proposed: {link}", line)
        else:
            project.add("L11", path, f"sideways link into '{owner.rel}'; a unit does not know "
                                    f"its siblings: {link}", line)


def check_context(project: Project, unit: Unit, path: str):
    doc = project.doc(path)
    items = context_items(doc)
    if not items:
        project.add("L9", path, "no item found; an item is a `### [title](link)` heading, "
                                "then `Says` and `Here`")
    unstamped = []
    for item in items:
        missing = [text for text, ok in (
            ("a link in the heading", bool(item["link"])),
            ("a paragraph that starts with 'Says'", item["has-says"]),
            ("a paragraph that starts with 'Here'", item["here"])) if not ok]
        if missing:
            project.add("L9", path, f"item '{item['title'][:60]}' lacks " + ", ".join(missing),
                        item["line"])
        expected, problem = cited_hash(project, path, item["link"])
        if problem:
            project.add("L10", path, f"item '{item['title'][:60]}': {problem}", item["line"])
        elif expected is None:
            continue
        elif item["stamp"] is None:
            unstamped.append(item)
        elif item["stamp"] != expected:
            project.add("L10", path, f"item '{item['title'][:60]}': the cited source changed "
                                     "since the stamp was written", item["line"])
    if unstamped:
        project.add("L10", path, f"{len(unstamped)} item(s) without a stamp, first: "
                                 f"'{unstamped[0]['title'][:60]}'", unstamped[0]["line"],
                    "Compare each `Says` with its source, then run `unifold stamp`.")


def stamp_file(project: Project, path: str) -> list:
    """Write the stamps of one docs/explanation/context.md. Returns one row per stamp written.

    A missing stamp is added and a stamp whose source changed is replaced. This is the
    deliberate act of `unifold stamp`; no other command writes a stamp.
    """
    doc = project.doc(path)
    lines, rows = list(doc.lines), []
    for item in reversed(context_items(doc)):
        expected, _ = cited_hash(project, path, item["link"])
        if expected is None or item["stamp"] == expected:
            continue
        stamp = f"<!-- unifold:cites sha={expected} -->"
        if item["stamp-line"]:
            lines[item["stamp-line"] - 1] = stamp
        else:
            lines.insert(item["line"], stamp)
        rel_path, anchor = split_link(item["link"])
        cited = project.rel(os.path.normpath(os.path.join(os.path.dirname(path), rel_path)))
        rows.append({"file": project.rel(path), "line": item["line"],
                     "cites": cited + (f"#{anchor}" if anchor else ""), "title": item["title"],
                     "action": "refreshed" if item["stamp"] is not None else "added"})
    if rows:
        write_text(path, "\n".join(lines) + "\n")
        project.forget(path)
    return rows[::-1]


def stamp_all(project: Project, below: str = None) -> list:
    rows = []
    for unit in project.units:
        path = os.path.join(unit.path, "docs", "explanation", "context.md")
        if os.path.isfile(path) and \
                (below is None or unit.path == below or unit.path.startswith(below + os.sep)):
            rows += stamp_file(project, path)
    return rows


# ----- contracts

def contract_of_path(project: Project, path: str) -> dict:
    """A contract, parsed once: its parts and what each has.

    {"path", "folder": bool, "has-parts": bool, "has-fake": bool, "parts": {name: part}} where a
    part is {"kind", "fence", "fields": set, "examples": rows, "line", "file"}. A file named
    index.md is a contract folder: its parts are the other .md files beside it.
    """
    cache = project.__dict__.setdefault("_contracts", {})
    found = cache.get(path)
    if found is not None:
        return found
    doc = project.doc(path)
    out = {"path": path, "folder": os.path.basename(path) == "index.md", "parts": {},
           "has-parts": any(h[1] == 2 and h[3] == "parts" for h in doc.headings),
           "has-fake": any(h[1] == 2 and h[3] == "fake" for h in doc.headings), "fake": None}
    fake = next((h for h in doc.headings if h[1] == 2 and h[3] == "fake"), None)
    if fake is not None:
        first = next((line.strip() for line in (doc.section("fake") or [])[1:] if line.strip()), "")
        out["fake"] = "real" if "the real implementation" in first.lower() else "described"

    def part_of(lines: list, start_line: int, file: str) -> dict:
        part = {"kind": None, "fence": False, "fields": set(), "examples": 0, "line": start_line, "file": file}
        fence, table, in_examples = None, [], False
        for line in lines:
            match = FENCE.match(line)
            if fence:
                if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
                        and not match.group(2).strip():
                    fence = None
                continue
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                fence, part["fence"] = match.group(1), True
                continue
            field = FIELD_LINE.match(line)
            if field:
                part["fields"].add(field.group(1))
                if field.group(1) == "Kind":
                    part["kind"] = field.group(2).strip().lower()
                in_examples = field.group(1) == "Examples"
                table = []
                continue
            text = line.strip()
            if in_examples:
                if text.startswith("|"):
                    table.append(text)
                elif text:
                    in_examples = False
                part["examples"] = max(part["examples"], len([r for r in table[2:] if not TABLE_RULE.match(r)]))
        return part

    if out["folder"]:
        folder = os.path.dirname(path)
        for name in project.listdir(folder):
            file = os.path.join(folder, name)
            if name.endswith(".md") and name != "index.md" and os.path.isfile(file):
                part_doc = project.doc(file)
                out["parts"][name[:-3]] = part_of(part_doc.lines[part_doc.body_start:], 1, file)
    else:
        headings = doc.headings
        inside = False
        for index, (number, level, text, slug) in enumerate(headings):
            if level == 2:
                inside = slug == "parts"
            elif level == 3 and inside:
                end = next((n for n, lvl, _, _ in headings[index + 1:] if lvl <= 3), len(doc.lines) + 1)
                out["parts"][heading_slug(text)] = part_of(doc.lines[number:end - 1], number, path)
    cache[path] = out
    return out


def contracts_of_project(project: Project) -> dict:
    """{absolute contract path: [units whose manifests name it]} for every contract named."""
    out: dict = {}
    for unit in project.units:
        if unit.broken:
            continue
        for entries in (unit.capabilities, unit.needs):
            for spec in entries.values():
                target = contract_target(project, unit, spec.get("contract"))[1]
                if target and project.kind_of(target) == "file" \
                        and path_problem(project, unit, spec["contract"]) is None:
                    out.setdefault(target, []).append(unit)
    return out


def check_contracts(project: Project):
    """C1 to C5: the body of every contract that a manifest names."""
    types: dict = {}                                  # type name -> [(holder unit, contract path)]
    for path, users in sorted(contracts_of_project(project).items()):
        contract = contract_of_path(project, path)
        holder = project.unit_at(path)
        if not contract["has-parts"]:
            project.add("C1", path, "no `## Parts` section; a contract lists its parts, one `###` heading each")
        elif not contract["parts"]:
            project.add("C1", path, "`## Parts` holds no part" + (
                " (a contract folder holds one .md file per part beside index.md)" if contract["folder"] else ""))
        for name, part in contract["parts"].items():
            where, line = part["file"], part["line"]
            if part["kind"] not in PART_KINDS:
                project.add("C1", where, f"part '{name}' has `Kind: {part['kind'] or ''}`; one of "
                                         + ", ".join(PART_KINDS), line)
            if not part["fence"]:
                project.add("C3", where, f"part '{name}' has no fenced code block with its signature", line)
            if part["kind"] in ("command", "query"):
                missing = [f for f in ("Pre", "Result", "Errors") if f not in part["fields"]]
                if "Examples" not in part["fields"]:
                    missing.append("Examples")
                elif part["examples"] < 1:
                    missing.append("a row in the Examples table")
                if missing:
                    project.add("C2", where, f"part '{name}' lacks " + ", ".join(f"`{m}:`" if m[0].isupper() and " " not in m else m for m in missing), line)
            if part["kind"] == "type":
                types.setdefault(name, []).append((holder, where, line))
        if not contract["has-fake"]:
            project.add("C5", path, "no `## Fake` section: say what stands in for this contract in the tests "
                                    "of its consumers")
    for name, places in sorted(types.items()):
        for index, (holder, where, line) in enumerate(places):
            for other_holder, other_where, _ in places[:index]:
                if other_where == where:
                    continue
                if holder is other_holder or holder in other_holder.ancestors() or other_holder in holder.ancestors():
                    project.add("C4", where, f"type '{name}' is also defined in {project.rel(other_where)}; "
                                             "one definition in a subtree, the other contract links to it", line)
                    break


# ----- kinds

def check_kinds(project: Project):
    """K2, K3 and K4: the rules of the well-known kinds."""
    for unit in project.units:
        if unit.broken:
            continue
        where = unit.manifest_path
        if unit.kind == "logic":
            for child in unit.children:
                if child.kind != "logic":
                    project.add("K2", where, f"logic unit has the child '{child.ref_in_parent()}' of kind "
                                             f"'{child.kind or 'none'}'; a logic unit is logic throughout",
                                unit.lines.get(("kind",)))
            for need in unit.needs:
                for item in providers_of(unit, need):
                    if item["where"] == "outside":
                        project.add("K2", where, f"need '{need}' of a logic unit reaches the need "
                                                 f"'{item['capability']}' of the root; a logic unit does no "
                                                 "input or output", unit.lines.get(("needs", need)))
                    elif item["unit"].kind != "logic":
                        project.add("K2", where, f"need '{need}' of a logic unit is finally provided by "
                                                 f"'{item['unit'].rel}' of kind '{item['unit'].kind or 'none'}'",
                                    unit.lines.get(("needs", need)))
        if unit.kind == "adapter":
            for need in unit.needs:
                for item in providers_of(unit, need):
                    if item["where"] == "unit" and item["unit"].kind == "adapter":
                        project.add("K3", where, f"need '{need}' of an adapter is finally provided by the "
                                                 f"adapter '{item['unit'].rel}'; one adapter talks to one "
                                                 "external system", unit.lines.get(("needs", need)))
    root = project.root_unit
    if root is not None and not root.broken:
        for need, spec in root.needs.items():
            if spec["platform"] or need in root.inner:
                continue
            for user, _ in final_users(root, need):
                if user is not root and user.kind and user.kind != "adapter":
                    project.add("K4", root.manifest_path, f"need '{need}' of the root is finally reached by "
                                                          f"'{user.rel}' of kind '{user.kind or 'none'}'; an "
                                                          "external system is reached by adapters only",
                                root.lines.get(("needs", need)))


# ----- scenarios

def chain_of_need(unit: Unit, need: str) -> list:
    """Every (unit, capability, [(holder, key)]) that provides for a need of `unit`, at every level
    on the way to the final provider, with the wiring lines used so far."""
    out: list = []

    def down(target: Unit, capability: str, via: list):
        out.append((target, capability, list(via)))
        conn = target.impl.get(capability)
        if conn:
            for entry in conn.entries:
                down(entry.unit, entry.capability, via + [(target, conn.key)])

    inside = unit.inner.get(need)
    if inside is not None:
        for entry in inside.entries:
            down(entry.unit, entry.capability, [(unit, inside.key)])
        return out
    current, name, via = unit, need, []
    while current.parent is not None:
        conn = current.parent.conn.get((current, name))
        if conn is None:
            return out
        via = via + [(current.parent, conn.key)]
        passed = None
        for entry in conn.entries:
            if entry.kind == "child":
                down(entry.unit, entry.capability, via)
            else:
                passed = entry.capability
        if passed is None:
            return out
        current, name = current.parent, passed
    return out


def chain_up(unit: Unit, need: str, holder: Unit):
    """(name of the need at `holder`, lines used) when a need of `unit` is passed up to `holder`, else None."""
    current, name, via = unit, need, []
    while current is not holder:
        if current.parent is None:
            return None
        conn = current.parent.conn.get((current, name))
        if conn is None:
            return None
        via.append((current.parent, conn.key))
        passed = [e.capability for e in conn.entries if e.kind == "own"]
        if not passed:
            return None
        current, name = current.parent, passed[0]
    return name, via


def find_descendant(project: Project, holder: Unit, path: str):
    """The unit below `holder` at `path` (segments by '/', plain folders included), or None."""
    target = os.path.normpath(os.path.join(holder.path, *[p for p in path.strip("/").split("/") if p]))
    unit = project.by_path.get(target)
    if unit is not None and unit is not holder and unit.depth_below(holder):
        return unit
    unit = holder                                     # by unit names, plain folders left out
    for part in [p for p in path.strip("/").split("/") if p]:
        found = [c for c in unit.children if c.name == part]
        if len(found) != 1:
            return None
        unit = found[0]
    return unit if unit is not holder else None


def resolve_hop(project: Project, holder: Unit, hop: str):
    """Resolve one hop of a scenario of `holder`.

    Returns (result, error). result: {"caller", "target", "part", "kind": the part's kind, "contract":
    abs path, "via": [(unit, key)], "caller-unit", "target-unit"}; the unit fields are None for a
    bare capability or need of the holder.
    """
    match = HOP.match(hop)
    if not match:
        return None, f"a hop is written `caller -> target.part`, not '{hop}'"
    caller_text, target_text = match.group(1), match.group(2)
    target_path, _, part = target_text.rpartition(".")
    if not target_path or not part:
        return None, f"the target of hop '{hop}' is `unit.part` or `need.part`"

    def lookup(name: str, side: str):
        unit = find_descendant(project, holder, name)
        entry = name in (holder.capabilities if side == "capability" else holder.needs)
        if unit is not None and entry:
            return None, None, f"'{name}' is both a unit below and a {side} of this unit; rename one"
        if unit is None and not entry:
            other = "need" if side == "capability" else "capability"
            hint = f"; it is a {other} of this unit, and a {other} is not a {'caller' if side == 'capability' else 'target'}" \
                if name in (holder.needs if side == "capability" else holder.capabilities) else ""
            return None, None, f"'{name}' is neither a unit below this one nor a {side} of it{hint}"
        return unit, (name if entry else None), None

    caller, caller_cap, error = lookup(caller_text, "capability")
    if error:
        return None, error
    target, target_need, error = lookup(target_path, "need")
    if error:
        return None, error

    def has_part(contract_path):
        return contract_path and contract_of_path(project, contract_path)["parts"].get(part) is not None

    def contract_path_of(owner: Unit, spec: dict):
        return contract_target(project, owner, spec.get("contract"))[1]

    found = []                                       # (contract path, via)
    if caller is not None and target is not None:
        for need, spec in caller.needs.items():
            for unit, capability, via in chain_of_need(caller, need):
                if unit is target:
                    found.append((contract_path_of(caller, spec), via, need))
                    break
        if not found:
            return None, f"no need of '{caller_text}' is provided for by '{target_path}'"
    elif caller_cap is not None and target is not None:
        spec = holder.capabilities[caller_cap]
        for unit, capability, via in chain_of_need_of_capability(holder, caller_cap):
            if unit is target:
                found.append((contract_path_of(holder, spec), via, caller_cap))
                break
        if not found:
            return None, f"capability '{caller_cap}' of this unit is not implemented by '{target_path}'"
    elif caller is not None and target_need is not None:
        for need, spec in caller.needs.items():
            up = chain_up(caller, need, holder)
            if up and up[0] == target_need:
                found.append((contract_path_of(caller, spec), up[1], need))
        if not found:
            return None, f"no need of '{caller_text}' is passed up to the need '{target_need}' of this unit"
    else:
        if holder.children:
            return None, (f"a hop from the capability '{caller_cap}' to the need '{target_need}' of this unit "
                          "is for a unit without children; here it goes through the children")
        found.append((contract_path_of(holder, holder.needs[target_need]), [], target_need))
    with_part = [f for f in found if has_part(f[0])]
    if not with_part:
        contracts = sorted({project.rel(f[0]) for f in found if f[0]} or {"none"})
        return None, f"part '{part}' is not in the contract {', '.join(contracts)}"
    if len(with_part) > 1:
        return None, (f"'{caller_text}' reaches '{target_path}' through {len(with_part)} connections whose contracts "
                      f"both have the part '{part}' (needs {', '.join(f[2] for f in with_part)}); rename one part")
    contract, via, _ = with_part[0]
    return {"caller": caller_text, "target": target_path, "part": part, "contract": contract, "via": via,
            "kind": contract_of_path(project, contract)["parts"][part].get("kind"),
            "caller-unit": caller, "target-unit": target, "caller-capability": caller_cap,
            "target-need": target_need}, None


def chain_of_need_of_capability(unit: Unit, capability: str) -> list:
    """Every (unit, capability, lines) that implements a capability of `unit`, at every level down."""
    out: list = []

    def down(target: Unit, name: str, via: list):
        conn = target.impl.get(name)
        if conn:
            for entry in conn.entries:
                out.append((entry.unit, entry.capability, via + [(target, conn.key)]))
                down(entry.unit, entry.capability, via + [(target, conn.key)])

    down(unit, capability, [])
    return out


def resolved_scenarios(project: Project) -> list:
    """Every scenario of the project with its hops resolved: [{"unit", "name", "spec", "hops": [(hop,
    result, error)]}], cached."""
    cached = project.__dict__.get("_scenarios")
    if cached is not None:
        return cached
    out = []
    for unit in project.units:
        if unit.broken:
            continue
        for name, spec in unit.scenarios.items():
            hops = [(hop, *resolve_hop(project, unit, hop)) for hop in spec["hops"]]
            out.append({"unit": unit, "name": name, "spec": spec, "hops": hops})
    project.__dict__["_scenarios"] = out
    return out


def scenarios_through(project: Project, unit: Unit) -> list:
    """The scenarios whose hops name `unit` or use a wiring line of it."""
    out = []
    for scenario in resolved_scenarios(project):
        for _, result, _ in scenario["hops"]:
            if result and (result["caller-unit"] is unit or result["target-unit"] is unit
                           or any(holder is unit for holder, _ in result["via"])
                           or scenario["unit"] is unit):
                out.append(scenario)
                break
    return out


def check_scenarios(project: Project):
    """N1, N2 and N3."""
    used: dict = {}                                   # unit -> set of wiring keys used by hops
    for unit in project.units:
        if unit.broken:
            continue
        raw = unit.manifest.get("scenarios")
        if raw is not None and not isinstance(raw, dict):
            project.add("M2", unit.manifest_path, f"'scenarios' must be a mapping of names, not {show_value(raw)}",
                        unit.lines.get(("scenarios",)))
            continue
        for name, spec in (raw or {}).items():
            line = unit.lines.get(("scenarios", str(name)))
            if not isinstance(name, str) or not ENTRY_NAME.match(name):
                project.add("M2", unit.manifest_path, f"the name of scenario '{name}' may contain only letters, "
                                                      "digits, '-' and '_'", line)
            if not isinstance(spec, dict):
                project.add("N2", unit.manifest_path, f"scenario '{name}' must be a mapping with summary, hops "
                                                      f"and expect, not {show_value(spec)}", line)
                continue
            for key in spec:
                if isinstance(key, str) and (key in SCENARIO_KEYS or key.startswith("x-")):
                    continue
                project.add("M2", unit.manifest_path, f"scenario '{name}': unknown key '{key}'", line)
            missing = [k for k in ("summary", "hops", "expect") if not spec.get(k)]
            if missing:
                project.add("N2", unit.manifest_path, f"scenario '{name}' lacks " + ", ".join(f"`{m}`" for m in missing),
                            line)
            hops = spec.get("hops")
            if hops is not None and (not isinstance(hops, list) or not all(isinstance(h, str) for h in hops)):
                project.add("N2", unit.manifest_path, f"scenario '{name}': `hops` is a list of `caller -> target.part`",
                            line)
            for key in ("summary", "expect", "source"):
                if key in spec and (not isinstance(spec[key], str) or not spec[key].strip()):
                    project.add("N2", unit.manifest_path, f"scenario '{name}': `{key}` is one line of text", line)
    unresolved: set = set()                           # holders of a scenario with an unresolved hop
    for scenario in resolved_scenarios(project):
        unit, name = scenario["unit"], scenario["name"]
        line = unit.lines.get(("scenarios", name))
        for hop, result, error in scenario["hops"]:
            if error:
                project.add("N1", unit.manifest_path, f"scenario '{name}', hop '{hop}': {error}", line)
                unresolved.add(unit)
            else:
                for holder, key in result["via"]:
                    used.setdefault(holder, set()).add(key)
    for unit, keys in used.items():
        wiring = unit.manifest.get("wiring")
        if not isinstance(wiring, dict) or unit in unresolved:   # fix N1 first
            continue
        for key in wiring:
            if str(key).strip() not in keys:
                project.add("N3", unit.manifest_path, f"wiring line '{key}' is used by no hop of the scenarios "
                                                      "that pass through this unit", unit.lines.get(("wiring", str(key))))


# ----- generated files

def check_generated(project: Project):
    expected = project.expected()
    for path, content in expected.items():
        kind = project.kind_of(path)
        if kind != "file":
            project.add("G1", path, "generated file is missing" if not kind else
                        "a folder is in the place of a generated file")
            continue
        if project.git_ignores(path):
            project.add("G1", path, "generated file is ignored by git; generated files are committed",
                        fix="Remove the pattern that ignores it from `.gitignore`, then commit the file.")
            continue
        text = project.text(path)
        if text == content:
            continue
        if MARK_PREFIX in text[:2000]:
            project.add("G1", path, "generated file is out of date")
        elif os.path.basename(path) == "AGENTS.md":
            project.add("G1", path, "AGENTS.md is generated, and this one is "
                                    "hand-written (no generated marker)", fix=AGENTS_FIX)
        else:
            project.add("G1", path, "this path is written by the generator, but the file has "
                                    "no generated marker", fix="Move the file elsewhere, then "
                                                               "run `unifold generate`.")
    for path, marked in leftovers(project, expected):
        if marked:
            project.add("G1", path, "leftover generated file; the generator no longer writes it")
        else:
            project.add("G1", path, "hand-written file in a generated folder",
                        fix="Move it out of docs/diagrams/; that folder holds generated files only.")


def leftovers(project: Project, expected: dict) -> list:
    """(path, has marker) of files in generated locations that the generator does not write."""
    out = []
    for unit in project.units:
        doc = os.path.join(unit.path, "docs")
        folder = os.path.join(doc, "diagrams")
        candidates = []
        if project.kind_of(folder) == "dir":
            candidates = [os.path.join(folder, n) for n in project.listdir(folder)
                          if n.endswith(".md")]
        candidates.append(os.path.join(doc, "decisions", "index.md"))
        for path in candidates:
            if path in expected or project.kind_of(path) != "file":
                continue
            marked = project.doc(path).generated
            if marked or os.path.dirname(path) == folder:
                out.append((path, marked))
    for folder in project.plain:                # a folder that stopped being a unit
        diagrams = os.path.join(folder, "docs", "diagrams")
        candidates = [os.path.join(folder, "AGENTS.md"), os.path.join(folder, "docs", "decisions", "index.md")]
        if os.path.isdir(diagrams):
            candidates += [os.path.join(diagrams, n) for n in sorted(os.listdir(diagrams)) if n.endswith(".md")]
        for path in candidates:
            if os.path.isfile(path) and project.doc(path).generated:
                out.append((path, True))
    for stub_dir in STUB_DIRS:
        folder = os.path.join(project.root, *stub_dir.split("/"))
        if project.kind_of(folder) != "dir":
            continue
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name, "SKILL.md")
            if path not in expected and os.path.isfile(path) and STUB_MARK in project.text(path):
                out.append((path, True))
    return out


# ------------------------------------------------------------- generation

def safe_id(text: str) -> str:
    """Letters and digits stay; everything else is encoded so that ids stay unique."""
    return "".join(c if c.isascii() and c.isalnum() else
                   {"/": "__", "-": "_d", "_": "_u"}.get(c, f"_x{ord(c):x}") for c in text)


def node_id(unit: Unit) -> str:
    return "u_root" if unit.parent is None else "u_" + safe_id(unit.rel)


def side_id(unit: Unit, side: str, capability: str) -> str:
    return f"{side}_{node_id(unit)[2:]}___" + safe_id(capability)


def label(text: str) -> str:
    """Text inside a quoted Mermaid label."""
    return str(text).replace('"', "#quot;").replace("\n", " ")


def responsibility_note(unit: Unit) -> str:
    """The responsibility of a unit as small text under its name, in a box of the explorer: about
    as wide as the name (28 to 34 characters), with every character that HTML or Mermaid reads
    as code written as an entity. A frame gets its responsibility beside its name from the page."""
    text = " ".join(unit.responsibility.split())
    lines = textwrap.wrap(text, max(28, min(34, round(len(unit_label(unit)) * 2.0))))   # within the 200px Mermaid wraps at
    text = "<br/>".join("".join(f"#{ord(c)};" if c in '<>&"#;' else c for c in line) for line in lines)
    return f"<br/><span class='note'>{text}</span>" if text else ""


def unit_label(unit: Unit) -> str:
    """The name of a unit in a diagram, with its kind where it has one."""
    return f"{unit.name} ({unit.kind})" if unit.kind else unit.name


def diagram_kinds(project: Project, unit: Unit) -> list:
    """Which diagrams the generator writes for a unit, in the order of the navigation."""
    mode = project.diagrams
    if mode == "none" or unit.broken:
        return []
    kinds = []
    if (unit.parent is not None and (unit.children or mode == "all")) \
            or (mode == "all" and not unit.children):
        kinds.append("context")
    if unit.children:
        kinds.append("component")
    if any(child.children for child in unit.children):
        kinds.append("architecture")
    return kinds


def best_diagram(project: Project, unit: Unit):
    kinds = diagram_kinds(project, unit)
    kind = "component" if "component" in kinds else kinds[0] if kinds else None
    return os.path.join(unit.path, "docs", "diagrams", kind + ".md") if kind else None


def link_to(out_dir: str, target: str) -> str:
    return url_path(os.path.relpath(target, out_dir))


def file_link(project: Project, out_dir: str, text: str, target) -> str:
    """A Markdown link if the target exists (or will be generated), else the plain text."""
    if target and (project.kind_of(target) or os.path.basename(os.path.dirname(target)) == "diagrams"):
        return f"[{cell(text)}]({link_to(out_dir, target)})"
    return cell(text)


def click_line(project: Project, node: str, target, out_dir: str):
    if project.links == "none" or not target:
        return None
    if project.links == "relative":
        return f'  click {node} href "{link_to(out_dir, target)}"'
    base = project.links.rstrip("/")
    return f'  click {node} href "{base}/{url_path(project.rel(target))}" _blank'


def diagram(project: Project, frame: Unit, depth: int, out_dir: str, focus: Unit = None, notes=False):
    """Build one flowchart of the inside of `frame`.

    Without `focus`: all children, opened `depth` levels deep. With `focus` (a child of
    `frame`): that child and the siblings it is connected to. With `notes` (the explorer), every
    unit and frame shows its responsibility in small text under its name.
    Returns (mermaid lines, units shown, {node id: unit}, shared connections as text).
    """
    def expanded(unit: Unit) -> bool:
        if focus is not None or unit is frame or not unit.children:
            return False
        level = unit.depth_below(frame)
        return level is not None and level < depth

    def sources(unit: Unit, need: str) -> list:
        if expanded(unit):
            found = [s for child, name in unit.need_users.get(need, ()) for s in sources(child, name)]
            if found:
                return found
        return [unit]

    def targets(unit: Unit, capability: str) -> list:
        if expanded(unit):
            conn = unit.impl.get(capability)
            found = [t for e in (conn.entries if conn else ()) for t in targets(e.unit, e.capability)]
            if found:
                return found
        return [unit]

    edges: dict = {}
    frame_sides: dict = {}
    touched: set = set()
    shared: list = []

    def edge(source, target, dashed, text):
        labels = edges.setdefault((source, target, dashed), [])
        if text and text not in labels:
            labels.append(text)

    passed: dict = {}                    # need of the frame -> (child, need) that pass up to it
    if focus is None:
        for (child, need), conn in frame.conn.items():
            if len(conn.entries) == 1 and conn.entries[0].kind == "own":
                passed.setdefault(conn.entries[0].capability, []).append((child, need))
    for need, users in sorted(passed.items()):
        if len(users) >= SHARED_FROM:
            optional = all(c.needs.get(n, {}).get("optional") for c, n in users)
            shared.append("- need " + ", ".join(f"`{c.ref_in_parent()}.{n}`" for c, n in users)
                          + f" → need `{need}` of `{frame.name}`, passed up"
                          + (" (optional)" if optional else ""))

    def collect(unit: Unit):
        for (child, need), conn in unit.conn.items():
            if unit is frame and len(conn.entries) == 1 and conn.entries[0].kind == "own" and \
                    len(passed.get(conn.entries[0].capability, ())) >= SHARED_FROM:
                continue                    # listed below the picture, like a shared connection
            if focus is not None and child is not focus and \
                    not any(e.kind == "child" and e.unit is focus for e in conn.entries):
                continue
            for index, entry in enumerate(conn.entries):
                if focus is not None and child is not focus and entry.unit is not focus:
                    continue
                if entry.kind == "child":
                    tos, capability = [node_id(t) for t in targets(entry.unit, entry.capability)], entry.capability
                    touched.add(entry.unit)
                elif unit is frame:
                    pid = side_id(frame, "n", entry.capability)
                    frame_sides[pid] = f'{{{{"{label(entry.capability)}"}}}}'
                    tos, capability = [pid], entry.capability
                else:
                    continue                    # passed further up: drawn from the level above
                touched.add(child)
                text = need if need == capability else f"{need} → {capability}"
                if entry.config:
                    text += f" ({entry.config})"
                if child.needs.get(need, {}).get("optional"):
                    text += " (optional)"
                for source in sources(child, need):
                    for target in tos:
                        edge(node_id(source), target, index > 0, text)
        if unit is frame:
            for capability, conn in unit.impl.items():
                for index, entry in enumerate(conn.entries):
                    if focus is not None and entry.unit is not focus:
                        continue
                    pid = side_id(frame, "p", capability)
                    frame_sides[pid] = f'(["{label(capability)}"])'
                    touched.add(entry.unit)
                    text = ("" if capability == entry.capability else entry.capability) \
                        + (f" ({entry.config})" if entry.config else "")
                    for target in targets(entry.unit, entry.capability):
                        edge(pid, node_id(target), index > 0, text)
            for need, conn in unit.inner.items():      # a need of the frame, met by a child
                for index, entry in enumerate(conn.entries):
                    if focus is not None and entry.unit is not focus:
                        continue
                    pid = side_id(frame, "n", need)
                    frame_sides[pid] = f'{{{{"{label(need)}"}}}}'
                    touched.add(entry.unit)
                    text = ("" if need == entry.capability else entry.capability) \
                        + (f" ({entry.config})" if entry.config else "") \
                        + (" (optional)" if unit.needs[need].get("optional") else "")
                    for target in targets(entry.unit, entry.capability):
                        edge(pid, node_id(target), index > 0, text)
        for child in unit.children:
            if expanded(child):
                collect(child)

    collect(frame)
    if focus is None:
        for capability in frame.capabilities:
            frame_sides.setdefault(side_id(frame, "p", capability), f'(["{label(capability)}"])')
        for need in frame.needs:
            frame_sides.setdefault(side_id(frame, "n", need), f'{{{{"{label(need)}"}}}}')
    shown: list = [frame]
    ids: dict = {node_id(frame): frame}
    note = responsibility_note if notes else (lambda unit: "")
    lines = ["flowchart LR", f'  subgraph {node_id(frame)}["{label(frame.name)}"]']
    clicks, marks = [], {"planned": [], "deprecated": []}

    def emit(unit: Unit, indent: str):
        shown.append(unit)
        ids[node_id(unit)] = unit
        if unit.status in marks:
            marks[unit.status].append(node_id(unit))
        if expanded(unit):
            lines.append(f'{indent}subgraph {node_id(unit)}["{label(unit_label(unit))}"]')
            for child in unit.children:
                emit(child, indent + "  ")
            lines.append(f"{indent}end")
        else:
            lines.append(f'{indent}{node_id(unit)}["{label(unit_label(unit))}{note(unit)}"]')
            click = click_line(project, node_id(unit), best_diagram(project, unit), out_dir)
            if click:
                clicks.append(click)

    for child in frame.children:
        if focus is None or child is focus or child in touched:
            emit(child, "    ")
    lines.append("  end")
    for pid, shape in frame_sides.items():
        lines.append(f"  {pid}{shape}")
    for (source, target, dashed), labels in edges.items():
        arrow = "-.->" if dashed else "-->"
        text = label(", ".join(labels))
        lines.append(f'  {source} {arrow}|"{text}"| {target}' if text
                     else f"  {source} {arrow} {target}")
    lines += clicks
    lines.append("  classDef focus stroke-width:4px")
    lines.append("  classDef planned stroke-dasharray:6 4")
    lines.append("  classDef deprecated stroke-dasharray:2 2,opacity:0.6")
    lines.append("  classDef plain stroke-dasharray:2 3")
    for status, nodes in marks.items():
        if nodes:
            lines.append(f"  class {','.join(nodes)} {status}")
    if focus is not None:
        lines.append(f"  class {node_id(focus)} focus")
    return lines, shown, ids, shared


def lone_context(project: Project, unit: Unit, out_dir: str, notes=False):
    """A unit without a parent, alone with its capabilities and needs."""
    uid = node_id(unit)
    lines = ["flowchart LR", f'  {uid}["{label(unit.name)}{responsibility_note(unit) if notes else ""}"]']
    for capability in unit.capabilities:
        pid = side_id(unit, "p", capability)
        lines += [f'  {pid}(["{label(capability)}"])', f"  {pid} --> {uid}"]
    for need in unit.needs:
        pid = side_id(unit, "n", need)
        lines += [f'  {pid}{{{{"{label(need)}"}}}}', f"  {uid} --> {pid}"]
    lines += ["  classDef focus stroke-width:4px", f"  class {uid} focus"]
    return lines


def status_cell(unit: Unit) -> str:
    return f"**{unit.status}**" if unit.status != "active" else unit.status


def unit_table(project: Project, units: list, out_dir: str) -> list:
    targets = [best_diagram(project, unit) for unit in units]
    extra = any(targets)
    rows = ["| Unit | Kind | Responsibility | Status |" + (" Diagram |" if extra else ""),
            "|---|---|---|---|" + ("---|" if extra else "")]
    for unit, target in zip(units, targets):
        name = file_link(project, out_dir, unit.name, os.path.join(unit.path, "README.md"))
        link = f"[{os.path.basename(target)[:-3]}]({link_to(out_dir, target)})" if target else ""
        rows.append(f"| {name} | {cell(unit.kind)} | {cell(unit.responsibility)} | "
                    f"{status_cell(unit)} |" + (f" {link} |" if extra else ""))
    return rows


def unit_ref(project: Project, unit: Unit, out_dir: str) -> str:
    text = unit.rel if unit.parent else unit.name
    mark = f" ({unit.status})" if unit.status != "active" else ""
    return file_link(project, out_dir, text, os.path.join(unit.path, "README.md")) + mark


def path_link(project: Project, unit: Unit, value, out_dir: str, text: str) -> str:
    shown, target, url = contract_target(project, unit, value)
    if url:
        return f"[{text}]({url})"
    if target and project.kind_of(target):
        return f"[{text}]({link_to(out_dir, target)})"
    return f"`{cell(shown)}`" if shown else ""


def via_note(item: dict) -> str:
    return f" ({item['config']})" if item.get("config") else ""


def connection_tables(project: Project, unit: Unit, out_dir: str) -> list:
    """Final providers and final users of a unit, as tables."""
    rows = []
    if unit.needs:
        rows += ["", "### Who provides what this unit needs", "",
                 "| Need | Kind | Contract | Provided by | Capability |",
                 "|---|---|---|---|---|"]
        for need, spec in unit.needs.items():
            head = f"| {need} | {cell(spec['kind'])} | " \
                   f"{path_link(project, unit, spec['contract'], out_dir, 'contract')} | "
            found = providers_of(unit, need)
            if not found:
                note = "nobody (optional)" if spec["optional"] else "**no provider**"
                rows.append(head + f"{note} | |")
            for item in found:
                note = via_note(item)
                if item["where"] == "outside":
                    rows.append(head + f"outside the project, as need `{item['capability']}` of the "
                                       f"root{note} | |")
                else:
                    target = item["unit"]
                    rows.append(head + f"{unit_ref(project, target, out_dir)}{note} | {item['capability']} |")
    if unit.capabilities:
        rows += ["", "### Who uses what this unit provides", "",
                 "| Capability | Kind | Contract | Used by | As need |",
                 "|---|---|---|---|---|"]
        for capability, spec in unit.capabilities.items():
            head = f"| {capability} | {cell(spec['kind'])} | " \
                   f"{path_link(project, unit, spec['contract'], out_dir, 'contract')} | "
            found = users_of(unit, capability)
            if not found:
                rows.append(head + "nobody | |")
            for item in found:
                if item["where"] == "outside":
                    rows.append(head + f"outside the project, as capability `{item['need']}` of the "
                                       "root | |")
                else:
                    user = item["unit"]
                    rows.append(
                        head + f"{unit_ref(project, user, out_dir)}{via_note(item)} | "
                        f"{item['need']} |")
    return rows


def wiring_table(unit: Unit) -> list:
    """The connections inside a unit, as a table."""
    rows = []
    for capability, conn in unit.impl.items():
        rows.append(f"| capability `{capability}` of `{unit.name}` | "
                    + " or ".join(f"`{e.raw}`" for e in conn.entries) + " | implemented by |")
    for need, conn in unit.inner.items():
        to = " or ".join(f"`{e.raw}`" + (f" ({e.config})" if e.config else "") for e in conn.entries)
        note = "optional" if unit.needs[need].get("optional") else ""
        rows.append(f"| need `{need}` of `{unit.name}` | {to} | {note} |")
    for (child, need), conn in unit.conn.items():
        key = f"`{child.ref_in_parent()}.{need}`"
        to = " or ".join((f"`{e.raw}`" if e.kind != "own" else f"need `{e.capability}` of `{unit.name}`")
                         + (f" ({e.config})" if e.config else "") for e in conn.entries)
        note = "optional" if child.needs.get(need, {}).get("optional") else ""
        rows.append(f"| {key} | {to} | {note} |")
    if not rows:
        return []
    return ["", "### Connections", "", "| Need | Provider | Note |", "|---|---|---|", *rows]


LEGEND = ("An arrow points from the unit that needs something to the unit that provides "
          "it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed "
          "arrow is an alternative provider; a dashed border marks a unit that is planned.")


def page(project: Project, unit: Unit, kinds: list, current: str, title: str, intro: str,
         chart: list, after: list) -> str:
    out_dir = os.path.join(unit.path, "docs", "diagrams")
    crumbs = []
    for ancestor in reversed(unit.ancestors()):
        crumbs.append(file_link(project, out_dir, ancestor.name, best_diagram(project, ancestor)))
    crumbs.append(f"**{cell(unit.name)}**")
    nav = []
    readme = os.path.join(unit.path, "README.md")
    if project.kind_of(readme) == "file":
        nav.append(f"[README]({link_to(out_dir, readme)})")
    nav += [f"[{kind}]({kind}.md)" for kind in kinds if kind != current]
    return "\n".join([MARK, f"# {title}", "", " / ".join(crumbs)
                      + ("".join(" · " + n for n in nav)), "", intro, "",
                      "```mermaid", *chart, "```", *after, ""])


def diagrams_for(project: Project, unit: Unit) -> dict:
    """For each diagram of a unit: (mermaid lines, units shown, node ids, shared lines)."""
    out_dir = os.path.join(unit.path, "docs", "diagrams")
    out = {}
    for kind in diagram_kinds(project, unit):
        if kind == "context":
            if unit.parent is None:
                out[kind] = (lone_context(project, unit, out_dir), [unit],
                             {node_id(unit): unit}, [])
            else:
                out[kind] = diagram(project, unit.parent, 0, out_dir, focus=unit)
        elif kind == "component":
            out[kind] = diagram(project, unit, 1, out_dir)
        else:
            for depth in range(MAX_DEPTH, 1, -1):
                found = diagram(project, unit, depth, out_dir)
                if len(found[0]) + len(found[1]) <= max(project.max_lines, MAX_LINES) or depth == 2:
                    break
            out[kind] = (*found, depth)
    return out


def scenario_sequence(scenario: dict) -> tuple:
    """The sequence diagram of a scenario, one lifeline per name as written, in order of first use:
    (Mermaid lines, {name: participant id}).

    A step is drawn as the kind of its part says: a command or query from the caller to the target,
    an event from the target that raises it to the caller that receives it, with an open arrowhead.
    The receiver of a step is active until a lifeline further out makes the next step, or the
    scenario ends; a unit below the receiver acts for it, as it implements the receiver's
    capability. A query answers with a dashed arrow when its receiver's activation ends."""
    names: list = []
    for hop, result, error in scenario["hops"]:
        for text in ((result["caller"], result["target"]) if result else
                     [s.strip() for s in hop.split("->", 1)] if "->" in hop else [hop]):
            text = text.rsplit(".", 1)[0] if text is not hop and "." in text and result is None else text
            if text not in names:
                names.append(text)
    ids = {n: "p" + safe_id(n) for n in names}
    text = lambda t: label(str(t).replace(";", "#59;"))  # a `;` ends a statement of a sequence diagram
    holder, about = scenario["unit"], {}              # name -> (kind, what it does): a unit, or a capability or need
    for hop, result, error in scenario["hops"]:
        if not result:
            continue
        for name, unit, entry in ((result["caller"], result["caller-unit"], holder.capabilities.get(result["caller-capability"])),
                                  (result["target"], result["target-unit"], holder.needs.get(result["target-need"]))):
            about[name] = (unit.kind, unit.responsibility) if unit else (entry["kind"], entry["summary"]) if entry else ("", "")
    boxes = {}                                        # name -> its lines: the name, «kind», the text wrapped by hand
    for n in names:
        kind, what = about.get(n, ("", ""))
        boxes[n] = [n] + ([f"«{kind}»"] if kind else []) + textwrap.wrap(str(what or ""), 32, break_long_words=False)
    most = max((len(b) for b in boxes.values()), default=1)
    lines = ["---", "config:", "  sequence:", f"    height: {max(65, 16 * most + 28)}", "---"] if most > 3 else []
    lines.append("sequenceDiagram")                   # a box keeps the height of the config, whatever its text: room for every line
    for n in names:
        lines.append(f'  participant {ids[n]} as {"<br/>".join(text(line) for line in boxes[n])}')
    busy: list = []                                   # (receiver, sender, step, kind) of the steps still running, innermost last
    within = lambda a, b: a == b or a.startswith(b + "/") or b.startswith(a + "/")   # the same lifeline, or one below the other

    def done(step: tuple):
        receiver, sender, index, kind = step
        if kind == "query":
            lines.append(f"  {ids[receiver]}-->>{ids[sender]}: ↩ {index}")
        lines.append(f"  deactivate {ids[receiver]}")

    for index, (hop, result, error) in enumerate(scenario["hops"], 1):
        if not result:
            continue
        kind = result.get("kind")
        sender, receiver = (result["target"], result["caller"]) if kind == "event" else (result["caller"], result["target"])
        while busy and not within(sender, busy[-1][0]):   # the steps inside the last one are over when a lifeline further out acts
            done(busy.pop())
        lines.append(f"  {ids[sender]}{'-)' if kind == 'event' else '->>'}{ids[receiver]}: {index} · {text(result['part'])}")
        lines.append(f"  activate {ids[receiver]}")
        busy.append((receiver, sender, index, kind))
    while busy:
        done(busy.pop())
    expect = scenario["spec"]["expect"]
    if expect and names and names[-1]:                # `wrap:` keeps a long expectation within the lifelines
        lines.append(f"  Note over {ids[names[0]]},{ids[names[-1]]}: wrap: Expect: {text(expect)}"
                     if len(names) > 1 else f"  Note over {ids[names[0]]}: wrap: Expect: {text(expect)}")
    return lines, ids


def scenario_page(project: Project, scenario: dict) -> str:
    """docs/diagrams/scenario-<name>.md: a sequence diagram of the hops, end to end, and a table."""
    unit, name, spec = scenario["unit"], scenario["name"], scenario["spec"]
    out_dir = os.path.join(unit.path, "docs", "diagrams")
    lines, _ = scenario_sequence(scenario)
    rows = ["| # | Caller | Target | Part | Kind | Contract |", "|---|---|---|---|---|---|"]
    for index, (hop, result, error) in enumerate(scenario["hops"], 1):
        if result:
            caller, target = result["caller"], result["target"]
            contract = file_link(project, out_dir, os.path.basename(result["contract"])[:-3], result["contract"])
            rows.append(f"| {index} | `{cell(caller)}` | `{cell(target)}` | `{cell(result['part'])}` | "
                        f"{cell(result.get('kind') or '')} | {contract} |")
        else:
            rows.append(f"| {index} | `{cell(hop)}` | | | | **does not resolve** |")
    crumbs = []
    for ancestor in reversed(unit.ancestors()):
        crumbs.append(file_link(project, out_dir, ancestor.name, best_diagram(project, ancestor)))
    crumbs.append(f"**{cell(unit.name)}**")
    nav = []
    readme = os.path.join(unit.path, "README.md")
    if project.kind_of(readme) == "file":
        nav.append(f"[README]({link_to(out_dir, readme)})")
    nav += [f"[{kind}]({kind}.md)" for kind in diagram_kinds(project, unit)]
    intro = [f"**{cell(spec['summary'])}**" if spec["summary"] else "",
             f"Source: {cell(spec['source'])}" if spec["source"] else "",
             f"Expect: {cell(spec['expect'])}" if spec["expect"] else ""]
    return "\n".join([MARK, f"# Scenario: {name}", "", " / ".join(crumbs) + "".join(" · " + n for n in nav), "",
                      *[line for line in intro if line], "",
                      "A unit is named by its path from `" + unit.name + "`; a capability or need of `" + unit.name
                      + "` is named bare. Every step is one hop along one connection of the map, drawn as the kind of "
                      "its part says: a command or query goes from the caller to the target, and a dashed arrow brings "
                      "the result of a query back; an event goes from the provider that raises it to the caller that "
                      "receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends "
                      "when a lifeline further out makes the next step, and a unit below the busy one acts for it.", "",
                      "```mermaid", *lines, "```", "", *rows, ""])


def skill_stubs(project: Project) -> dict:
    """{stub name: (unit, skill)} for every skill of the project.

    A skill of the root keeps its name. A skill of another unit is `<unit>-<skill>`; if
    that name is taken, the unit's path with `-` replaces the unit's name.
    """
    def slug(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

    out = {}
    for unit in project.units:
        for skill in skills_of(project, unit):
            if not skill["exists"]:
                continue
            base = slug(skill["name"]) or "skill"
            prefix = slug(unit.name)
            name = base if unit.parent is None or base.startswith(prefix + "-") \
                else f"{prefix}-{base}"
            if name[:64].strip("-") in out and unit.parent is not None:
                name = f"{slug(unit.rel)}-{base}"
            name, count = name[:64].strip("-"), 1
            while name in out:                        # still taken: number it
                count += 1
                name = f"{name[:60].strip('-')}-{count}" if count == 2 else \
                    re.sub(r"-\d+$", f"-{count}", name)
            out[name] = (unit, skill)
    return out


def stub_text(project: Project, name: str, unit: Unit, skill: dict, folder: str) -> str:
    target = link_to(folder, skill["path"])
    owner = "the project root" if unit.parent is None else f"the unit `{unit.rel}`"
    return "\n".join([
        "---", f"name: {name}",
        "description: " + json.dumps(skill["description"] or f"Skill {skill['name']} of {unit.name}",
                                     ensure_ascii=False),
        "---", STUB_MARK, "",
        f"Read [{project.rel(skill['path'])}]({target}) and follow it. "
        f"The skill belongs to {owner}; relative paths in it start from that file.", ""])


def tool_command(project: Project) -> str:
    script = "docs/skills/unifold/scripts/unifold.py"
    if os.path.isfile(os.path.join(project.root, *script.split("/"))):
        return f"python3 {script}"
    return "unifold"


def agents_block(project: Project) -> str:
    """The marked block for the root AGENTS.md: what unifold is, three commands, unit index."""
    tool = tool_command(project)
    lines = [
        BLOCK_BEGIN,
        "## unifold",
        "",
        f"This repository has a [unifold]({SITE_URL}) map. A folder with a `{MANIFEST}` is a "
        "unit: the file says what the unit provides and needs, and the unit above connects "
        "needs to providers. Read the map before you change an interface; keep it true after.",
        "",
        f"- `{tool} show PATH`: a unit, its capabilities and needs, and who is on the other side",
        f"- `{tool} capability PATH NAME`: both ends of one connection, with contracts",
        f"- `{tool} check`: is the map consistent (`--fix` rewrites generated files)",
    ]
    skills = [(n, t) for n, t in (("unifold", "How to read and write the map"),
                                  ("unifold-convert", "How to bring folders into the map"))
              if os.path.isfile(os.path.join(project.root, "docs", "skills", n, "SKILL.md"))]
    if skills:
        lines += ["", " ".join(f"{t}: the skill [{n}](docs/skills/{n}/SKILL.md)." for n, t in skills)]
    units = [u for u in project.units if u.parent is not None]
    if units and len(units) <= INDEX_LIMIT:
        lines += ["", "| Unit | Path | Responsibility |", "|---|---|---|"]
        for unit in units:
            mark = f" ({unit.status})" if unit.status != "active" else ""
            lines.append(f"| {cell(unit.name)} | `{cell(unit.rel)}` | {cell(unit.responsibility)}{mark} |")
    elif units:
        lines += ["", f"{len(units)} units; `{tool} tree` lists them."]
    lines.append(BLOCK_END)
    return "\n".join(lines)


def agents_text(project: Project, unit: Unit) -> str:
    """The AGENTS.md of a unit: where the documents and skills are.

    No project knowledge, only the way to it. The root's file also carries the unifold
    block with the unit index.
    """
    docs = documents_of(project, unit)

    def links(items: list) -> str:
        return ", ".join(f"[{cell(text)}]({url_path(os.path.relpath(path, unit.path))})"
                         for text, path in items)

    decisions = ["[decisions](docs/decisions/index.md)"] if decisions_of(project, unit) else []
    rows = []
    for kind, folder, extra in (("Learn", "tutorials", []), ("Look up", "references", []),
                                ("Understand", "explanation", decisions)):
        items = docs[folder]
        parts = [f"{len(items)} files in docs/{folder}/"] if len(items) > LIST_LIMIT \
            else [links(items)] if items else []
        if parts or extra:
            rows.append(f"| {kind} | {', '.join(parts + extra)} |")
    lines = [MARK, f"# AGENTS.md: {unit.name}", "",
             "unifold unit; run `unifold show` here. Read [README.md](README.md) first: it "
             "says what the unit is for and why it is built this way. Everything else is in "
             "`docs/`."]
    if rows:
        lines += ["", "## Documents", "", "| Kind | Files |", "|---|---|", *rows]
    skills = [s for s in skills_of(project, unit) if s["exists"]]
    if skills:
        lines += ["", "## Skills", "", "| Skill | Description |", "|---|---|"]
        lines += [f"| [{cell(s['name'])}](docs/skills/{url_path(s['name'])}/SKILL.md) | "
                  f"{cell(s['description'])} |" for s in skills]
    if unit.parent is None:
        lines += ["", agents_block(project)]
    return "\n".join(lines) + "\n"


def generate(project: Project, force=()) -> dict:
    """Return {path: content} for every generated file of the project.

    `force` may contain "stubs": write skill stubs even where the folders do not exist
    yet. AGENTS.md is written whole for every unit, the root's with the unifold block.
    """
    out: dict = {}
    if not project.usable:
        return out
    for unit in project.units:
        folder = os.path.join(unit.path, "docs", "diagrams")
        kinds = diagram_kinds(project, unit)
        data = diagrams_for(project, unit)
        name = unit.name
        if "context" in data:
            chart, shown, _, shared = data["context"]
            if unit.parent is None:
                intro = (f"`{name}` and the outside world: the capabilities it provides (rounded) "
                         "and what it needs from outside (hexagons).")
                after = connection_tables(project, unit, folder)
            else:
                intro = (f"`{name}` inside `{unit.parent.name}`, with the units it is "
                         f"connected to. " + LEGEND)
                after = (["", "Shared connections, not drawn:", "", *shared] if shared else []) \
                    + ["", *unit_table(project, shown[1:], folder)] \
                    + connection_tables(project, unit, folder)
            out[os.path.join(folder, "context.md")] = page(
                project, unit, kinds, "context", f"Context diagram: {name}", intro, chart, after)
        if "component" in data:
            chart, shown, _, shared = data["component"]
            intro = f"The units directly inside `{name}` and how they are connected. " + LEGEND
            after = (["", "Shared connections, not drawn:", "", *shared] if shared else []) \
                + ["", *unit_table(project, shown[1:], folder)] + wiring_table(unit)
            out[os.path.join(folder, "component.md")] = page(
                project, unit, kinds, "component", f"Component diagram: {name}", intro, chart, after)
        if "architecture" in data:
            chart, shown, _, shared, depth = data["architecture"]
            note = "" if depth == MAX_DEPTH else f" Opened {depth} levels only, to stay readable."
            intro = f"`{name}` opened up {depth} levels deep.{note} " + LEGEND
            after = (["", "Shared connections, not drawn:", "", *shared] if shared else []) \
                + ["", *unit_table(project, shown[1:], folder)]
            out[os.path.join(folder, "architecture.md")] = page(
                project, unit, kinds, "architecture", f"Architecture diagram: {name}", intro,
                chart, after)
    if project.diagrams != "none":
        for scenario in resolved_scenarios(project):
            unit = scenario["unit"]
            folder = os.path.join(unit.path, "docs", "diagrams")
            out[os.path.join(folder, f"scenario-{scenario['name']}.md")] = scenario_page(project, scenario)
    for unit in project.units:
        infos = decisions_of(project, unit)
        if not infos:
            continue
        folder = os.path.join(unit.path, "docs", "decisions")
        rows = ["| No. | Decision | Status | Date |", "|---|---|---|---|"]
        for info in infos:
            status = info["status"]
            shown = f"**{status_mark(status)}**" if status in ("proposed", "derived") else cell(status)
            rows.append(f"| {info['name'][:4]} | [{cell(info['title'])}]({url_path(info['name'])}) | "
                        f"{shown} | {info['date']} |")
        nav = [f"[{n}]({link_to(folder, os.path.join(unit.path, n))})"
               for n in ("README.md", "AGENTS.md")
               if n == "AGENTS.md" or project.kind_of(os.path.join(unit.path, n)) == "file"]
        out[os.path.join(folder, "index.md")] = "\n".join(
            [MARK, f"# Decisions of {unit.name}", "", *([" · ".join(nav), ""] if nav else []),
             "Accepted and derived decisions bind.", "", *rows, ""])
    stubs = skill_stubs(project)
    for stub_dir in STUB_DIRS:
        base = os.path.join(project.root, *stub_dir.split("/"))
        if "stubs" not in force and not os.path.isdir(base):
            continue
        for name, (unit, skill) in stubs.items():
            folder = os.path.join(base, name)
            path = os.path.join(folder, "SKILL.md")
            if os.path.isfile(path) and STUB_MARK not in project.text(path):
                continue                        # a skill somebody wrote there: not ours
            out[path] = stub_text(project, name, unit, skill, folder)
    for unit in project.units:
        out[os.path.join(unit.path, "AGENTS.md")] = agents_text(project, unit)
    return out


def write_generated(project: Project, force=()) -> dict:
    """Write what `generate` returns; remove leftovers. Returns counts and refusals."""
    project._expected = None
    expected = generate(project, force)
    result = {"written": [], "removed": [], "refused": []}
    for path, content in expected.items():
        kind = project.kind_of(path)
        if kind == "file":
            text = project.text(path)
            if text == content:
                continue
            if MARK_PREFIX not in text[:2000]:
                result["refused"].append(project.rel(path))
                continue
        elif kind == "dir":
            result["refused"].append(project.rel(path))
            continue
        write_text(path, content)
        project.forget(path)
        result["written"].append(project.rel(path))
    for path, marked in leftovers(project, expected):
        if marked:
            try:
                os.remove(path)
                folder = os.path.dirname(path)
                if os.path.basename(os.path.dirname(folder)) == "skills" and not os.listdir(folder):
                    os.rmdir(folder)
            except OSError as exc:
                raise Fail("not-writable", f"cannot remove {path}: {exc.strerror or exc}")
            project.forget(path)
            result["removed"].append(project.rel(path))
    project._expected = None
    return result


# ------------------------------------------------------------ description

def describe(project: Project, unit: Unit) -> dict:
    """Everything an agent needs to start work in a unit, as plain data."""
    rel = project.rel

    def brief(other: Unit) -> dict:
        return {"path": other.rel, "name": other.name, "status": other.status,
                "responsibility": other.responsibility}

    def provider(item: dict) -> dict:
        if item["where"] == "outside":
            return {"outside": True, "root-need": item["capability"], "config": item["config"]}
        target = item["unit"]
        return {"unit": target.rel, "status": target.status, "capability": item["capability"],
                "config": item["config"]}

    def user(item: dict) -> dict:
        if item["where"] == "outside":
            return {"outside": True, "root-capability": item["need"]}
        other = item["unit"]
        return {"unit": other.rel, "status": other.status, "need": item["need"],
                "config": item["config"]}

    def entry(spec: dict) -> dict:
        return {"kind": spec["kind"] or None, "summary": spec["summary"],
                "contract": contract_target(project, unit, spec["contract"])[0] or None,
                "parts": spec["parts"]}

    files = [rel(p) for p in managed_files(project, unit) if not generated_location(unit, p)]
    return {
        "name": unit.name, "path": unit.rel, "responsibility": unit.responsibility,
        "kind": unit.kind or None, "status": unit.status, "owner": unit.owner or None,
        "secret": secret_data(project, unit), "not": [{"text": text, "need": need} for text, need in unit.nots],
        "manifest": rel(unit.manifest_path),
        "parent": brief(unit.parent) if unit.parent else None,
        "children": [brief(c) for c in unit.children],
        "nested-projects": [rel(p) for p in unit.foreign],
        "capabilities": {capability: {**entry(spec),
                            "used-by": [user(i) for i in users_of(unit, capability)]}
                     for capability, spec in unit.capabilities.items()},
        "needs": {need: {**entry(spec), "optional": spec["optional"], "platform": spec["platform"],
                         "provided-by": [provider(i) for i in providers_of(unit, need)]}
                  for need, spec in unit.needs.items()},
        "scenarios": [{"unit": s["unit"].rel, "name": s["name"], "summary": s["spec"]["summary"]}
                      for s in scenarios_through(project, unit)],
        "skills": [{"name": s["name"], "path": rel(s["path"]), "description": s["description"]}
                   for s in skills_of(project, unit) if s["exists"]],
        "decisions": [{"path": rel(d["path"]), "title": d["title"], "status": d["status"]}
                      for d in decisions_of(project, unit)],
        "documents": {kind: [rel(p) for _, p in items]
                      for kind, items in documents_of(project, unit).items()},
        "diagrams": [rel(os.path.join(unit.path, "docs", "diagrams", k + ".md"))
                     for k in diagram_kinds(project, unit)],
        "files": files,
    }


def secret_data(project: Project, unit: Unit):
    if unit.secret is None:
        return None
    decision = unit.secret["decision"]
    target = os.path.normpath(os.path.join(unit.path, decision)) if decision else None
    return {"what": unit.secret["what"],
            "decision": project.rel(target) if target and project.inside(target) else decision}


def mark(status) -> str:
    """` [planned: not built yet]` for anything that is not in force, else ''."""
    return f" [{status_mark(status)}]" if status and status not in ("active", "accepted", "derived") else ""


def named(rel: str) -> str:
    """A unit in text output: its path, or 'the root'."""
    return "the root" if rel == "." else rel


def print_show(info: dict):
    def line(name, value):
        if value:
            print(f"{name:<10}{value}")
    line("unit", f"{info['name']}  ({info['path']}){mark(info['status'])}")
    line("does", info["responsibility"])
    line("status", " · ".join(x for x in (
        info["status"], info["kind"] and "kind " + info["kind"], info["owner"] and "owner " + info["owner"]) if x))
    if info.get("secret"):
        line("secret", f"{info['secret']['what']}  decision {info['secret']['decision']}")
    for item in info.get("not") or []:
        line("not", item["text"] + (f"  → need '{item['need']}'" if item["need"] else ""))
    line("manifest", info["manifest"])
    parent = info["parent"]
    line("parent", (parent["name"] if parent["path"] == "." else parent["path"])
         + mark(parent["status"]) if parent else "none (this is the root)")
    line("children", ", ".join(c["path"] + mark(c["status"]) for c in info["children"]) or "none")
    line("nested", ", ".join(info["nested-projects"]))
    if info["capabilities"]:
        print("capabilities")
    for capability, spec in info["capabilities"].items():
        extra = f"  contract {spec['contract']}" if spec["contract"] else ""
        extra += f" (parts {', '.join(spec['parts'])})" if spec.get("parts") else ""
        kind = f" ({spec['kind']})" if spec["kind"] else ""
        print(f"  {capability}{kind}: {spec['summary']}{extra}")
        for item in spec["used-by"] or [None]:
            if item is None:
                print("      used by nobody")
            elif item.get("outside"):
                print(f"      used from outside the project (capability '{item['root-capability']}' of the root)")
            else:
                config = f" [{item['config']}]" if item.get("config") else ""
                print(f"      used by {named(item['unit'])}{mark(item['status'])} as need "
                      f"'{item['need']}'{config}")
    if info["needs"]:
        print("needs")
    for need, spec in info["needs"].items():
        extra = f"  contract {spec['contract']}" if spec["contract"] else ""
        extra += f" (parts {', '.join(spec['parts'])})" if spec.get("parts") else ""
        flags = [x for x in (spec["kind"], "optional" if spec["optional"] else "",
                             "platform" if spec.get("platform") else "") if x]
        kind = f" ({', '.join(flags)})" if flags else ""
        print(f"  {need}{kind}: {spec['summary']}{extra}")
        for item in spec["provided-by"] or [None]:
            if item is None:
                print("      no provider" + (" (optional)" if spec["optional"] else ""))
                continue
            note = f" (alternative '{item['config']}')" if item.get("config") else ""
            if item.get("outside"):
                print(f"      provided from outside the project (need '{item['root-need']}' "
                      f"of the root){note}")
            else:
                print(f"      provided by {named(item['unit'])}{mark(item['status'])} capability "
                      f"'{item['capability']}'{note}")
    for scenario in info.get("scenarios") or []:
        held = "" if scenario["unit"] == info["path"] else f"  (held by {named(scenario['unit'])})"
        print(f"scenario  {scenario['name']}: {scenario['summary']}{held}")
    for skill in info["skills"]:
        print(f"skill     {skill['name']}: {skill['path']}")
    for decision in info["decisions"]:
        print(f"decision  {decision['path']}{mark(decision['status'] or 'no status')}")
    for kind, paths in info.get("documents", {}).items():
        if paths:
            print(f"{kind:<12}{', '.join(paths)}")
    line("diagrams", ", ".join(info["diagrams"]))
    line("files", ", ".join(info["files"]))


def readme_section(project: Project, unit: Unit, name: str) -> str:
    """The text below the `###` heading that names a capability, in the unit's README.md."""
    readme = os.path.join(unit.path, "README.md")
    if project.kind_of(readme) != "file":
        return ""
    doc = project.doc(readme)
    for number, level, text, anchor in doc.headings:
        if level == 3 and name in [m.group(2) for m in CODE_SPAN.finditer(text)]:
            section = doc.section(anchor) or []
            return "\n".join(section[1:]).strip()
    return ""


def capability_data(project: Project, unit: Unit, name: str) -> dict:
    """Both ends of every connection of one capability or need."""
    def end(owner: Unit, entry: str, side: str, extra=None) -> dict:
        spec = (owner.capabilities if side == "capabilities" else owner.needs).get(entry, {})
        return {"unit": owner.rel, "status": owner.status, "side": side, "name": entry,
                "kind": spec.get("kind") or None, "summary": spec.get("summary", ""),
                "contract": contract_target(project, owner, spec.get("contract"))[0] or None,
                "parts": spec.get("parts"),
                "optional": bool(spec.get("optional")) if side == "needs" else None,
                "readme": readme_section(project, owner, entry) or None, **(extra or {})}

    if name in unit.capabilities:
        ends = [end(unit, name, "capabilities")]
        for item in users_of(unit, name):
            if item["where"] == "unit":
                ends.append(end(item["unit"], item["need"], "needs", {"config": item["config"]}))
            else:
                ends.append({"outside": True, "side": "needs", "name": item["need"],
                             "summary": f"used from outside the project, as capability "
                                        f"'{item['need']}' of the root"})
    elif name in unit.needs:
        ends = [end(unit, name, "needs")]
        for item in providers_of(unit, name):
            extra = {"config": item["config"]}
            if item["where"] == "unit":
                ends.append(end(item["unit"], item["capability"], "capabilities", extra))
            else:
                root_need = project.root_unit.needs.get(item["capability"], {})
                ends.append({"outside": True, "side": "capabilities", "name": item["capability"],
                             "summary": "provided from outside the project, as need "
                                        f"'{item['capability']}' of the root: "
                                        f"{root_need.get('summary', '')}", **extra})
    else:
        names = list(unit.capabilities) + list(unit.needs)
        close = difflib.get_close_matches(name, names, 1)
        raise Fail("unknown-capability", f"unit '{unit.rel}' has no capability or need '{name}'"
                   + (f"; did you mean '{close[0]}'?" if close else
                      f" (it has: {', '.join(names) or 'none'})"))
    return {"unit": unit.rel, "name": name, "side": ends[0]["side"], "ends": ends}


def print_capability(data: dict):
    for item in data["ends"]:
        if item.get("outside"):
            print(f"--- outside: {item['summary']}\n")
            continue
        note = f" ({item['config']})" if item.get("config") else ""
        kind = f" ({item['kind']})" if item["kind"] else ""
        side = "capabilities" if item["side"] == "capabilities" else "needs"
        print(f"--- {named(item['unit'])}{mark(item['status'])} {side} '{item['name']}'"
              f"{kind}{note}: {item['summary']}")
        if item.get("contract"):
            print(f"    contract: {item['contract']}" + (f" (parts {', '.join(item['parts'])})" if item.get("parts") else ""))
        if item.get("optional"):
            print("    optional")
        if item["readme"]:
            print(item["readme"])
        else:
            print("    (no section for it in README.md)")
        print()


def citations(project: Project, wanted) -> list:
    """Context items and links that cite a file for which `wanted(path)` is true."""
    out = []
    for unit in project.units:
        context = os.path.join(unit.path, "docs", "explanation", "context.md")
        for path in managed_files(project, unit):
            if generated_location(unit, path):
                continue
            doc = project.doc(path)
            base = os.path.dirname(path)
            items = {i["line"]: i for i in context_items(doc)} if path == context else {}
            for line, link in doc.links:
                if SCHEME.match(link) or link.startswith(("#", "/")):
                    continue
                target = os.path.normpath(os.path.join(base, split_link(link)[0]))
                if target == path or not wanted(target):
                    continue
                item = items.get(line)
                row = {"file": project.rel(path), "line": line, "cites": project.rel(target),
                       "kind": "context-item" if item else "link"}
                if item:
                    expected, problem = cited_hash(project, path, item["link"])
                    row.update({"title": item["title"], "says": item["says"],
                                "stamp": "missing" if item["stamp"] is None else
                                "current" if item["stamp"] == expected else "stale"})
                out.append(row)
    return out


def print_citations(rows: list):
    for row in rows:
        if row["kind"] == "context-item":
            stale = "" if row["stamp"] == "current" else f" [stamp {row['stamp']}]"
            print(f"{row['file']}:{row['line']}: {row['title']}{stale}")
            print(f"    Says: {row['says'] or '(nothing)'}")
        else:
            print(f"{row['file']}:{row['line']}: link to {row['cites']}")


def impact(project: Project, unit: Unit, capability=None, file=None) -> dict:
    """Everything that depends on a unit or on one of its capabilities, transitively."""
    if capability is not None and capability not in unit.capabilities:
        what = "a need, and impact follows capabilities" if capability in unit.needs else "not a capability"
        raise Fail("unknown-capability", f"'{capability}' is {what} of '{unit.rel}' (capabilities: "
                                   f"{', '.join(unit.capabilities) or 'none'})")
    dependents, outside, reached, exposed = {}, [], [], []
    queue = [(unit, name, 1) for name in ([capability] if capability else unit.capabilities)]
    seen = set((u, p) for u, p, _ in queue)
    for owner, name, _ in list(queue):                # units above that offer the capability as theirs
        stack = [(owner, name)]
        while stack:
            holder, held = stack.pop()
            if holder.parent is None:
                continue
            for use in holder.parent.capability_users.get((holder, held), ()):
                if use[0] == "capability":
                    item = {"unit": holder.parent.rel, "capability": use[1]}
                    if item not in exposed:
                        exposed.append(item)
                        stack.append((holder.parent, use[1]))
    while queue:
        owner, name, distance = queue.pop(0)
        for item in users_of(owner, name):
            if item["where"] == "outside":
                target = outside if owner is unit else reached
                if item["need"] not in target:
                    target.append(item["need"])
                continue
            user = item["unit"]
            if user is unit:
                continue
            if user not in dependents:
                dependents[user] = {"unit": user.rel, "status": user.status,
                                    "distance": distance,
                                    "via": f"need '{item['need']}' is met by capability '{name}' "
                                           f"of {owner.rel}"}
            for other in user.capabilities:
                if (user, other) not in seen:
                    seen.add((user, other))
                    queue.append((user, other, distance + 1))
    if file:
        wanted = lambda target: target == file
    else:
        wanted = lambda target: project.owner_of(target) == ("unit", unit)
    cited = [row for row in citations(project, wanted) if row["kind"] == "context-item"
             or file]
    return {"unit": unit.rel, "status": unit.status, "capability": capability,
            "file": project.rel(file) if file else None,
            "dependents": sorted(dependents.values(), key=lambda d: (d["distance"], d["unit"])),
            "exposed-as": exposed, "outside": outside,
            "root-capabilities-affected": sorted(set(outside + reached)), "citations": cited}


def print_impact(data: dict):
    what = f"capability '{data['capability']}' of {data['unit']}" if data["capability"] else f"unit {data['unit']}"
    print(f"impact of {what}{mark(data['status'])}")
    for item in data["exposed-as"]:
        where = "the root" if item["unit"] == "." else item["unit"]
        print(f"  offered as capability '{item['capability']}' of {where}")
    for name in data["outside"]:
        print(f"  used from outside the project (capability '{name}' of the root)")
    indirect = [n for n in data["root-capabilities-affected"] if n not in data["outside"]]
    if indirect:
        print("  capabilities of the root that depend on it: " + ", ".join(indirect))
    if not data["dependents"]:
        print("  no unit of the project depends on it")
    for item in data["dependents"]:
        print(f"  {item['distance']}  {named(item['unit'])}{mark(item['status'])}: {item['via']}")
    if data["citations"]:
        print("cited by")
        for row in data["citations"]:
            stale = "" if row.get("stamp") in (None, "current") else f" [stamp {row['stamp']}]"
            print(f"  {row['file']}:{row['line']}: {row.get('title') or 'link'}{stale}")
            if row.get("says"):
                print(f"      Says: {row['says']}")


def tree_data(project: Project, depth=None) -> list:
    out = []
    for unit in project.units:
        level = len(unit.ancestors())
        if depth is not None and level > depth:
            continue
        out.append({"path": unit.rel, "name": unit.name, "depth": level,
                    "status": unit.status, "kind": unit.kind or None,
                    "responsibility": unit.responsibility, "parent": unit.parent.rel if unit.parent else None,
                    "capabilities": list(unit.capabilities), "needs": list(unit.needs),
                    "children": [c.rel for c in unit.children],
                    "nested-projects": [project.rel(p) for p in unit.foreign]})
    return out


def print_tree(project: Project, depth=None):
    stack = [(project.root_unit, 0)]
    while stack:
        unit, level = stack.pop()
        if isinstance(unit, str):
            print(f"{'  ' * level}{unit} [nested project, checked on its own]")
            continue
        parts = []
        if unit.capabilities:
            parts.append("provides " + ", ".join(unit.capabilities))
        if unit.needs:
            parts.append("needs " + ", ".join(unit.needs))
        suffix = f"  ({'; '.join(parts)})" if parts else ""
        between = unit.parent is not None and os.path.dirname(unit.path) != unit.parent.path
        path = f"  <{unit.rel}>" if between else ""
        print(f"{'  ' * level}{unit.name}{mark(unit.status)}{path}{suffix}")
        if depth is not None and level >= depth:
            continue
        below = [(c, level + 1) for c in unit.children] \
            + [(os.path.basename(p), level + 1) for p in unit.foreign]
        stack.extend(reversed(below))


# ------------------------------------------------------------------- init

MINIMAL_SKILL = """---
name: unifold
description: Read and maintain the unifold architecture map of this repository, the unifold.yaml files that say what each folder provides and needs and how they are connected. Use it before changing an interface between folders, when adding, moving or removing a unit, and when `unifold check` reports a finding.
---
# unifold

This repository has a [unifold](https://unifold.md) map. A folder with a `unifold.yaml` is a unit. The file says what the unit provides and what it needs; the unit above connects needs to providers in `wiring`.

The tool is `scripts/unifold.py` in this folder (Python 3.9+, PyYAML; `uv run` installs the dependency by itself).

1. Before you work in a folder: `unifold.py show PATH`.
2. Before you change a capability: `unifold.py capability PATH NAME` and `unifold.py impact PATH NAME`.
3. After a change: `unifold.py check --fix`, then correct every error it reports. Each finding names a rule; `unifold.py rules ID` explains it.

The standard: https://unifold.md/spec. How agents use it: https://unifold.md/agents. The rules: https://unifold.md/rules.
"""


SKILLS = ("unifold", "unifold-convert")          # installed by `init --agents`


def install_agents(root: str) -> list:
    """Install the skills, sync the stubs, write the AGENTS.md block. Returns notes."""
    notes = []
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    packaged = os.path.join(sys.prefix, "share", "unifold", "skills")
    skills_dir = os.path.join(root, "docs", "skills")
    script = os.path.join(skills_dir, "unifold", "scripts", "unifold.py")
    try:
        if os.path.realpath(here) == os.path.realpath(skills_dir):
            notes.append("the skills are already in docs/skills (the tool runs from there)")
        else:
            installed = []
            for name in SKILLS:
                source_dir = next((os.path.join(d, name) for d in (here, packaged)
                                   if os.path.isfile(os.path.join(d, name, "SKILL.md"))), None)
                if source_dir is None:
                    continue
                target = os.path.join(skills_dir, name)
                for folder, subs, names in os.walk(source_dir):
                    subs[:] = [s for s in subs if s != "__pycache__" and not s.startswith(".")]
                    for file_name in names:
                        source = os.path.join(folder, file_name)
                        goal = os.path.join(target, os.path.relpath(source, source_dir))
                        os.makedirs(os.path.dirname(goal), exist_ok=True)
                        shutil.copyfile(source, goal)
                installed.append(name)
            os.makedirs(os.path.dirname(script), exist_ok=True)
            shutil.copyfile(os.path.abspath(__file__), script)
            if installed:
                notes.append(f"installed the skill(s) {', '.join(installed)} into docs/skills")
            else:
                skill = os.path.join(skills_dir, "unifold", "SKILL.md")
                if not os.path.isfile(skill):
                    write_text(skill, MINIMAL_SKILL)
                notes.append("wrote a minimal skill that points to https://unifold.md, and a copy "
                             "of the tool, into docs/skills/unifold")
    except OSError as exc:
        raise Fail("not-writable", f"cannot install the skills into {skills_dir}: {exc}")
    project = Project(root)
    result = write_generated(project, force=("stubs",))
    stubs = sum(1 for p in result["written"] if p.endswith("SKILL.md"))
    what = "wrote AGENTS.md (generated, with the unifold block)" \
        if "AGENTS.md" in result["written"] else "AGENTS.md is current"
    if "AGENTS.md" in result["refused"]:
        what = "the hand-written AGENTS.md stays"
    notes.append(f"{what}; {stubs} skill stub(s) written into {' and '.join(STUB_DIRS)}")
    claude = os.path.join(root, "CLAUDE.md")
    if os.path.isfile(claude) and "AGENTS.md" not in read_text(claude):
        notes.append("CLAUDE.md exists and does not mention AGENTS.md: add the line "
                     "`@AGENTS.md` to it, or Claude Code will not load AGENTS.md")
    return notes


def root_manifest_text(name: str) -> str:
    """The root manifest that `init` writes: the version, the name, and a responsibility to fill in."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        name = json.dumps(name, ensure_ascii=False)
    return (f"# yaml-language-server: $schema={SITE_URL}/{SPEC_VERSIONS[-1]}/unifold.schema.json\n"
            f"unifold: \"{SPEC_VERSIONS[-1]}\"\nname: {name}\nresponsibility: TODO\n")


def ask(question: str) -> bool:
    """Ask a yes/no question on the terminal. False when nobody can answer."""
    try:
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            return False
        answer = input(question + " [y/N] ")
    except (EOFError, OSError, KeyboardInterrupt):
        return False
    return answer.strip().lower() in ("y", "yes")


def init_project(target: str, agents=False, interactive=False) -> dict:
    """Start a project in `target`: the root manifest and `README.md` if there is none, then
    the generated files.

    No other manifest is written. The units of a repository are chosen by a person or by an
    agent with the skill `unifold-convert`; this tool checks what they wrote. A
    hand-written `AGENTS.md` is replaced only when `interactive` and the person says yes.
    """
    root = real(target)
    try:
        os.makedirs(root, exist_ok=True)
    except OSError as exc:
        raise Fail("not-writable", f"cannot create {root}: {exc.strerror or exc}")
    if not os.path.isdir(root):
        raise Fail("not-a-folder", f"{target} is not a folder")
    result = {"root": root, "written": [], "notes": [], "units": 0}
    manifest = os.path.join(root, MANIFEST)
    outer = find_root(os.path.dirname(root)) if os.path.dirname(root) != root else None
    if os.path.isfile(manifest):
        if not ROOT_LINE.search(read_text(manifest)):
            raise Fail("not-a-root", f"{manifest} exists and has no key 'unifold'. Add "
                                     f"`unifold: \"{SPEC_VERSIONS[-1]}\"` to make this folder a "
                                     "project root.")
        result["notes"].append(f"{MANIFEST} exists: this is a project already; no manifest "
                               "was changed")
    else:
        if outer:
            result["notes"].append(f"this folder lies inside the project {outer}; it becomes "
                                   "a nested project, checked on its own")
        write_text(manifest, root_manifest_text(os.path.basename(root)))
        result["written"].append(MANIFEST)
        result["notes"].append("the root manifest says `responsibility: TODO`. The units of the "
                               "repository are written by hand or with the skill "
                               "`unifold-convert`; this tool drafts none")
    readme = os.path.join(root, "README.md")
    if not os.path.exists(readme):
        write_text(readme, README_TEMPLATE.replace("<folder-name>", os.path.basename(root), 1))
        result["written"].append("README.md")
        result["notes"].append("README.md was written from the template: replace every <...> "
                               "with what the project is and why, and delete what does not apply")
    agents_file = os.path.join(root, "AGENTS.md")
    if os.path.isfile(agents_file) and MARK_PREFIX not in read_text(agents_file)[:2000]:
        if interactive and ask(f"{agents_file} is hand-written, and unifold generates AGENTS.md. "
                               "Replace it? Its content is lost unless you have moved it into "
                               "README.md and docs/."):
            os.remove(agents_file)
            result["notes"].append("replaced the hand-written AGENTS.md")
        else:
            result["notes"].append("kept the hand-written AGENTS.md; " + AGENTS_FIX)
    project = Project(root)
    if not project.usable:
        first = project.findings[0]
        raise Fail("bad-root", f"the root manifest is not usable: {first['message']}")
    result["units"] = len(project.units)
    generated = write_generated(project)
    result["written"] += generated["written"]
    if agents:
        result["notes"] += install_agents(root)
    return result


# ------------------------------------------------------------------- site

MD_ITEM = re.compile(r"^( {0,3})([-*+]|(\d{1,9})[.)])(?:( +)(.*))?$")
MD_HR = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
MD_QUOTE = re.compile(r"^ {0,3}> ?(.*)$")
MD_SETEXT = re.compile(r"^ {0,3}(=+|-+)\s*$")
MD_REF = re.compile(r"^ {0,3}\[((?:[^\]\\]|\\.)+)\]:\s*(<[^>\n]*>|\S+)(?:\s+(\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*$")
MD_TASK = re.compile(r"^\[([ xX])\]\s+")
MD_URL = re.compile(r"(?<![\w/\"'=@])https?://[^\s<>\x00]*[^\s<>\x00.,:;!?\"'*_)\]]")
MD_EMPHASIS = ((r"\*\*\*(?=\S)(.+?)(?<=\S)\*\*\*", "<strong><em>", "</em></strong>"),
               (r"\*\*(?=\S)(.+?)(?<=\S)\*\*", "<strong>", "</strong>"),
               (r"(?<![A-Za-z0-9_])__(?=\S)(.+?)(?<=\S)__(?![A-Za-z0-9_])", "<strong>", "</strong>"),
               (r"(?<!\*)\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?!\*)", "<em>", "</em>"),
               (r"(?<![A-Za-z0-9_])_(?=[^\s_])(.+?)(?<=[^\s_])_(?![A-Za-z0-9_])", "<em>", "</em>"),
               (r"~~(?=\S)(.+?)(?<=\S)~~", "<del>", "</del>"))
LINK_SCHEMES = ("http", "https", "mailto")       # a link with another scheme in a document is shown as text


def escape_html(text) -> str:
    """Text for HTML, in an element or an attribute: nothing in it can open a tag or end a value."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


class Markdown:
    """Markdown into HTML for the explorer: headings with anchors, paragraphs, emphasis, code, links
    and images (inline and by reference), nested lists with tasks, GFM tables, fenced code, Mermaid
    blocks, quotes and rules. Every character of the source is escaped, raw HTML too: only `<br>`
    becomes a line break and comments are dropped, so the tags of the result are the ones made here.
    `link(target)` gives the href of a link target, or None for a link not to follow. A heading has
    the id `md-<anchor>`, its anchor as `check` reads it; a level-1 heading that opens the document
    becomes `title`."""

    def __init__(self, link):
        self.link = link
        self.refs, self.seen, self.keep, self.title, self.opening = {}, {}, [], None, True

    def render(self, text: str) -> str:
        lines, fence = [], None
        for line in text.replace("\x00", "").replace("\t", "    ").split("\n"):
            match = FENCE.match(line)                     # reference definitions are taken out, outside code
            if fence:
                if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not match.group(2).strip():
                    fence = None
            elif match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                fence = match.group(1)
            elif MD_REF.match(line):
                label, target = MD_REF.match(line).group(1, 2)
                self.refs.setdefault(" ".join(label.lower().split()), target.strip("<>"))
                continue
            lines.append(line)
        return self.blocks(lines)

    def text(self, text: str) -> str:
        """One line of Markdown, such as a value of the front matter."""
        return self.inline(str(text).replace("\x00", ""))

    def starts(self, lines: list, i: int) -> bool:
        """Whether line i opens a block that ends a paragraph."""
        line, item = lines[i], MD_ITEM.match(lines[i])
        return bool(ATX.match(line) or MD_HR.match(line) or MD_QUOTE.match(line) or FENCE.match(line)
                    or (item and item.group(5) and (not item.group(3) or item.group(3) == "1"))
                    or ("|" in line and i + 1 < len(lines) and "|" in lines[i + 1] and TABLE_RULE.match(lines[i + 1].strip())))

    def blocks(self, lines: list, tight=False) -> str:
        out, i, n = [], 0, len(lines)
        while i < n:
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if line.lstrip().startswith("<!--"):           # a comment: the mark of a generated file, a stamp
                while i < n and "-->" not in lines[i]:
                    i += 1
                i += 1
                continue
            first, self.opening = self.opening, False
            fence = FENCE.match(line)
            if fence and not (fence.group(1)[0] == "`" and "`" in fence.group(2)):
                mark, info = fence.group(1), (fence.group(2).split() or [""])[0].lower()
                indent, body, i = len(line) - len(line.lstrip(" ")), [], i + 1
                while i < n:
                    end = FENCE.match(lines[i])
                    if end and end.group(1)[0] == mark[0] and len(end.group(1)) >= len(mark) and not end.group(2).strip():
                        i += 1
                        break
                    body.append(lines[i][indent:] if not lines[i][:indent].strip() else lines[i].lstrip())
                    i += 1
                source = escape_html("\n".join(body))
                language = f' class="language-{info}"' if re.match(r"^[a-z0-9+#.-]+$", info) else ""
                out.append(f'<pre class="mermaid">{source}</pre>' if info == "mermaid" else f"<pre><code{language}>{source}</code></pre>")
                continue
            heading = ATX.match(line)
            if heading:
                out.append(self.heading(len(heading.group(1)), heading.group(2) or "", first))
                i += 1
                continue
            if MD_HR.match(line):
                out.append("<hr>")
                i += 1
                continue
            if "|" in line and i + 1 < n and "|" in lines[i + 1] and TABLE_RULE.match(lines[i + 1].strip()):
                i = self.table(lines, i, out)
                continue
            if MD_QUOTE.match(line):
                inner = []
                while i < n and lines[i].strip() and (MD_QUOTE.match(lines[i]) or not self.starts(lines, i)):
                    quoted = MD_QUOTE.match(lines[i])
                    inner.append(quoted.group(1) if quoted else lines[i])
                    i += 1
                out.append(f"<blockquote>{self.blocks(inner)}</blockquote>")
                continue
            if MD_ITEM.match(line):
                i = self.items(lines, i, out)
                continue
            para = []                                     # a paragraph, or the text of a setext heading
            while i < n and lines[i].strip() and not (para and (MD_SETEXT.match(lines[i]) or self.starts(lines, i))):
                para.append(lines[i].lstrip() if lines[i].endswith("  ") else lines[i].strip())
                i += 1
            if para and i < n and MD_SETEXT.match(lines[i]):
                out.append(self.heading(1 if "=" in lines[i] else 2, " ".join(para), first))
                i += 1
                continue
            groups = []                                   # the fields of a part of a contract (Kind, Pre, Result, ...) each on a line
            for line in para:
                if FIELD_LINE.match(line) or not groups:
                    groups.append([line])
                else:
                    groups[-1].append(line)
            for group in groups:
                field = FIELD_LINE.match(group[0])
                text = self.inline("\n".join([field.group(2)] + group[1:]) if field else "\n".join(group))
                text = f"<strong>{field.group(1)}:</strong> {text}" if field else text
                out.append(text if tight and len(groups) == 1 else f'<p{" class=field" if field else ""}>{text}</p>')
        return "\n".join(o for o in out if o)

    def heading(self, level: int, text: str, first: bool) -> str:
        slug = heading_slug(text.strip())                 # the anchors of Doc.headings, which `check` checks links against
        count = self.seen.get(slug, 0)
        self.seen[slug] = count + 1
        slug = slug if not count else f"{slug}-{count}"
        html = self.inline(text.strip())
        if level == 1 and first and self.title is None:
            self.title = html
            return ""
        return f'<h{level} id="md-{escape_html(slug)}">{html}</h{level}>' if slug else f"<h{level}>{html}</h{level}>"

    def table(self, lines: list, i: int, out: list) -> int:
        def cells(row):
            row = row.strip()
            row = row[1:] if row.startswith("|") else row
            row = row[:-1] if row.endswith("|") and not row.endswith("\\|") else row
            return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", row)]
        head, rule = cells(lines[i]), cells(lines[i + 1])
        align = [' class="c"' if c.startswith(":") and c.endswith(":") else ' class="r"' if c.endswith(":") else "" for c in rule]
        align += [""] * (len(head) - len(align))
        rows, i = [], i + 2
        while i < len(lines) and lines[i].strip() and "|" in lines[i] and not (ATX.match(lines[i]) or FENCE.match(lines[i])):
            rows.append(cells(lines[i]))
            i += 1
        top = "<tr>" + "".join(f"<th{a}>{self.inline(c)}</th>" for c, a in zip(head, align)) + "</tr>"
        body = "".join("<tr>" + "".join(f"<td{a}>{self.inline(c)}</td>" for c, a in zip(row + [""] * len(head), align)) + "</tr>"
                       for row in rows)
        out.append(f'<div class="table"><table><thead>{top}</thead>{"<tbody>" + body + "</tbody>" if body else ""}</table></div>')
        return i

    def items(self, lines: list, i: int, out: list) -> int:
        """A list: items of one sort, each with the lines indented under it and lazy lines of its text."""
        first = MD_ITEM.match(lines[i])
        ordered, sort = bool(first.group(3)), first.group(2)[-1]
        start, items, loose, n = int(first.group(3) or 1), [], False, len(lines)
        while i < n:
            match = MD_ITEM.match(lines[i])
            if not match or bool(match.group(3)) != ordered or match.group(2)[-1] != sort:
                break
            space = match.group(4) or " "
            width = len(match.group(1)) + len(match.group(2)) + (len(space) if len(space) <= 4 else 1)
            content = [(match.group(5) or "") if len(space) <= 4 else space[1:] + (match.group(5) or "")]
            i += 1
            while i < n:
                line = lines[i]
                if not line.strip():
                    content.append("")
                elif len(line) - len(line.lstrip(" ")) >= width:
                    content.append(line[width:])
                elif content[-1] and not self.starts(lines, i) and not MD_ITEM.match(line):
                    content.append(line.strip())        # a lazy line of the paragraph
                else:
                    break
                i += 1
            following = MD_ITEM.match(lines[i]) if i < n else None
            while len(content) > 1 and not content[-1]:
                content.pop()                           # a blank line between two items of this list makes it loose
                loose = loose or bool(following and bool(following.group(3)) == ordered and following.group(2)[-1] == sort)
            loose = loose or ("" in content[1:] and not any(FENCE.match(c) for c in content))
            items.append(content)
        html = []
        for content in items:
            task = MD_TASK.match(content[0])
            if task:
                content = [content[0][task.end():]] + content[1:]
            box = f'<input type="checkbox" disabled{" checked" if task.group(1) != " " else ""}> ' if task else ""
            html.append(f'<li{" class=task" if task else ""}>{box}{self.blocks(content, tight=not loose)}</li>')
        tag = "ol" if ordered else "ul"
        out.append(f"<{tag}{f' start={start}' if ordered and start != 1 else ''}>" + "".join(html) + f"</{tag}>")
        return i

    def hold(self, html: str) -> str:
        """A finished piece of HTML, kept out of the text until the end."""
        self.keep.append(html)
        return f"\x00{len(self.keep) - 1}\x00"

    def inline(self, text: str, links=True) -> str:
        def code(match):
            body = match.group(2).replace("\n", " ")
            body = body[1:-1] if len(body) > 2 and body[0] == body[-1] == " " and body.strip() else body
            return self.hold("<code>" + escape_html(body) + "</code>")
        text = re.sub(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", code, text, flags=re.S)
        text = re.sub(r"(?: {2,}|\\)\n", lambda m: self.hold("<br>\n"), text)
        text = re.sub(r"\\([!-/:-@\[-`{-~])", lambda m: self.hold(escape_html(m.group(1))), text)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        text = re.sub(r"<br\s*/?>", lambda m: self.hold("<br>"), text, flags=re.I)
        text = re.sub(r"&(?:#\d{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});", lambda m: self.hold(m.group()), text)   # an entity stays one
        if links:
            text = re.sub(r"<((?:https?|mailto):[^\s<>]+)>", lambda m: self.anchor_tag(m.group(1), escape_html(m.group(1))), text)
            text = self.links(text)
            text = MD_URL.sub(lambda m: self.anchor_tag(m.group(), escape_html(m.group())), text)
        else:
            text = self.links(text, images=True)        # the text of a link: images, no more links
        text = escape_html(text)
        for pattern, opening, closing in MD_EMPHASIS:
            text = re.sub(pattern, lambda m: opening + m.group(1) + closing, text, flags=re.S)
        while "\x00" in text:
            text = re.sub(r"\x00(\d+)\x00", lambda m: self.keep[int(m.group(1))], text)
        return text

    def anchor_tag(self, target: str, html: str, title="") -> str:
        href = self.link(target)
        if href is None:
            return self.hold(html)
        title = f' title="{escape_html(title)}"' if title else ""
        return self.hold(f'<a href="{escape_html(href)}"{title}>{html}</a>')

    def links(self, text: str, images=False) -> str:
        """Links and images, inline or by reference; the text of a link is read again. With
        `images`, only images."""
        out, at, look = [], 0, 0
        while True:
            start = text.find("[", look)
            if start < 0:
                return "".join(out) + text[at:]
            depth, end = 0, start
            while end < len(text):
                depth += {"[": 1, "]": -1}.get(text[end], 0)
                if depth == 0:
                    break
                end += 1
            image = start > at and text[start - 1] == "!"
            label, rest, target, title, stop = text[start + 1:end], text[end + 1:], None, "", end + 1
            inline = re.match(r"\(\s*(<[^<>\n]*>|(?:[^\s()\\]|\\.|\((?:[^\s()\\]|\\.)*\))*)"
                              r"(?:\s+(\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)", rest) if end < len(text) else None
            if inline:
                target, title, stop = inline.group(1).strip("<>"), (inline.group(2) or "")[1:-1], end + 1 + inline.end()
            elif end < len(text):
                full = re.match(r"\[((?:[^\]\\]|\\.)*)\]", rest)
                key = " ".join((full.group(1) if full and full.group(1) else label).lower().split())
                if key in self.refs:
                    target, stop = self.refs[key], end + 1 + (full.end() if full else 0)
            if target is None or (images and not image):
                look = start + 1
                continue
            target = re.sub(r"\\(.)", r"\1", target)
            out.append(text[at:start - 1 if image else start])
            if image:
                href, alt = self.link(target), escape_html(re.sub(r"[\[\]*_`]", "", label))
                out.append(self.hold(f'<img src="{escape_html(href)}" alt="{alt}" loading="lazy">' if href and not href.startswith("#") else alt))
            else:
                out.append(self.anchor_tag(target, self.inline(label, links=False), title))
            at = look = stop


def site_documents(project: Project, charts: dict, scenes: set, base: str, up: str) -> dict:
    """The Markdown files of every unit as pages of the explorer: {path: page}. A page has its
    unit, its kind (a folder of docs/, `readme` or `other`), its title and its HTML; a page with
    front matter its `summary` (the description) and `facts`, a decision its `status`, a part of a
    folder contract its `contract`, a README its `intro` (its first paragraph, inline) and `why`
    (its section `## Why`). A link between documents opens the page of the target in the
    explorer: a README its unit (with an anchor other than `why`: its own page), a diagram file its tab, a scenario file its page; a link to any
    other file goes to the file. `charts` is {unit: its diagram tabs}, `scenes` {(holder, name)}."""
    files, units = {}, {u.path: u for u in project.units}
    for unit in project.units:
        tool = [os.path.join(unit.path, "docs", "skills", s) + os.sep for s in SKILLS] if unit is project.root_unit else []
        top = [os.path.join(unit.path, n) for n in project.listdir(unit.path) if n.endswith(".md") and n != "README.md"]
        for path in managed_files(project, unit) + [p for p in top if os.path.isfile(p)]:
            if not any(path.startswith(t) for t in tool):
                files[path] = unit

    def href(route: str, anchor="") -> str:
        return "#" + quote(route, safe="/@:") + ("#" + quote(anchor, safe="") if anchor else "")

    def route(path: str):
        """Where a path opens in the explorer, or None for a file that has no page there."""
        unit = files.get(path)
        if unit is not None:
            rest = os.path.relpath(path, unit.path).replace(os.sep, "/")
            return unit.rel if rest == "README.md" else unit.rel + "@doc:" + rest
        if path in units:
            return units[path].rel
        folder, name = os.path.split(path)
        owner = units.get(os.path.dirname(os.path.dirname(folder)))
        if owner is None or os.path.basename(folder) != "diagrams" or not name.endswith(".md"):
            return None
        name = name[:-3]
        if name.startswith("scenario-") and (owner.rel, name[9:]) in scenes:
            return owner.rel + "@scenario:" + name[9:]
        return owner.rel + "@" + name if name in charts.get(owner.rel, ()) else None

    def show(value) -> str:
        if isinstance(value, list):
            return ", ".join(show(v) for v in value)
        if isinstance(value, dict):
            return "; ".join(f"{k}: {show(v)}" for k, v in value.items())
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return ("true" if value else "false") if isinstance(value, bool) else "" if value is None else str(value).strip()

    pages = {}
    for path, unit in files.items():
        doc, here = project.doc(path), route(path)
        own = unit.rel + "@doc:README.md"                 # the page of a README, besides its unit
        here = own if here == unit.rel else here

        def link(target: str, path=path, here=here):
            if SCHEME.match(target):
                return target if target.split(":", 1)[0].lower() in LINK_SCHEMES else None
            part, anchor = split_link(target)
            if not part:
                return href(here, anchor)
            full = os.path.normpath(os.path.join(project.root, part.lstrip("/")) if part.startswith("/")
                                    else os.path.join(os.path.dirname(path), part))
            found = route(full)
            if found and anchor not in ("", "why") and os.path.basename(full) == "README.md" and found == route(os.path.dirname(full)):
                found += "@doc:README.md"
            if found:
                return href(found, anchor)
            rel = "/".join(quote(s, safe="") for s in os.path.relpath(full, project.root).replace(os.sep, "/").split("/"))
            return (base + "/" + rel if base else up + rel) + ("#" + quote(anchor, safe="") if anchor else "")

        md = Markdown(link)
        html = md.render("\n".join(doc.lines[doc.body_start:]))
        rest = os.path.relpath(path, unit.path).split(os.sep)
        kind = rest[1] if len(rest) > 2 and rest[0] == "docs" else "readme" if rest == ["README.md"] else "other"
        page = {"unit": unit.rel, "kind": kind, "title": md.title or escape_html(os.path.basename(path)[:-3]), "html": html}
        if kind == "readme":                              # on the page of the unit: the first paragraph on top, `## Why` above the tables
            body, i, para = doc.lines[doc.body_start:], 0, []
            while i < len(body) and not para and not re.match(r"^ {0,3}##\s", body[i]):
                if FENCE.match(body[i]):                  # code is not the first paragraph
                    i += 1
                    while i < len(body) and not FENCE.match(body[i]):
                        i += 1
                elif body[i].strip() and not body[i].lstrip().startswith("<!--") and not md.starts(body, i) \
                        and not MD_ITEM.match(body[i]) and "|" not in body[i]:
                    while i < len(body) and body[i].strip() and not md.starts(body, i):
                        para.append(body[i].strip())
                        i += 1
                i += 1
            if para:
                page["intro"] = Markdown(link).text("\n".join(para))
            why = doc.section("why")
            if why:
                page["why"] = Markdown(link).render("\n".join(why))
        meta = doc.meta if isinstance(doc.meta, dict) else {}
        if meta.get("description"):
            page["summary"] = " ".join(show(meta["description"]).split())
        if kind == "decisions" and isinstance(meta.get("status"), str):
            page["status"] = " ".join(meta["status"].split())
        facts = [[str(k).replace("-", " "), md.text(show(v)) if k != "status" else
                  f'<span class="badge {escape_html(show(v).split()[0] if show(v).split() else "")}">{escape_html(show(v))}</span>']
                 for k, v in meta.items() if k != "description" and show(v).strip()]
        if facts:
            page["facts"] = facts
        pages[project.rel(path)] = page
    for path, unit in files.items():                     # a folder contract: its index and its parts
        if os.path.basename(path) == "index.md" and os.sep + "references" + os.sep in path[len(unit.path):]:
            parts = sorted(project.rel(p) for p in files if os.path.dirname(p) == os.path.dirname(path) and p != path)
            for part in parts:
                pages[part]["contract"] = project.rel(path)
            if parts:
                pages[project.rel(path)]["parts"] = parts
    return pages


SITE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ · unifold</title>
<script>/* light or dark, as on unifold.md: the button keeps a choice in localStorage and sets data-theme before the style sheet applies; without a choice the system decides */
(() => {const root = document.documentElement, key = "unifold-theme", system = matchMedia("(prefers-color-scheme: dark)");
try { const t = localStorage.getItem(key); if (t === "light" || t === "dark") root.dataset.theme = t; } catch {}
const dark = () => (root.dataset.theme || (system.matches ? "dark" : "light")) === "dark";
const show = () => document.querySelectorAll("button.theme").forEach(b => { b.hidden = false; b.setAttribute("aria-pressed", dark()); });
const changed = () => { show(); dispatchEvent(new Event("themechange")); };
addEventListener("DOMContentLoaded", show); system.addEventListener("change", changed);
addEventListener("click", ev => { if (!ev.target.closest("button.theme")) return; const t = dark() ? "light" : "dark";
  if (t === (system.matches ? "dark" : "light")) delete root.dataset.theme; else root.dataset.theme = t;   // a choice that matches the system is forgotten
  try { root.dataset.theme ? localStorage.setItem(key, t) : localStorage.removeItem(key); } catch {}
  changed(); });})();
</script>
<style>
/* the colours, type and flat shapes of unifold.md; Patua One is there when the page is served from the site */
@font-face{font-family:"Patua One";src:local("Patua One"),url("/patua-one.woff2") format("woff2");font-display:swap}
:root{color-scheme:light dark;--bg:#fff;--fg:#141c20;--fg-2:#33424a;--mute:#5d6c73;--line:#e2e6e7;--hi:#0a7462;--panel:#f5f6f6;--code:#eaeef0;--code-line:#d5dcdf;--warn:#9a5b00;--warnbg:#ffe1a3;
--ink:#141c20;--paper:#fff;--unit:#e6f5f0;--unit-focus:#b5e6d9;--box-0:#f5f6f6;--box-1:#eceff0;--box-2:#e3e7e8;--frame:#c9d1d3;--accent:#0a7462;--accent-soft:#dcf2ec;--teal-hl:#bfeadf;--amber:#9a5b00;--amber-hl:#ffe1a3;
--sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI Variable Text","Segoe UI",Roboto,"Helvetica Neue","Noto Sans",Arial,sans-serif;
--slab:"Patua One",Rockwell,"Rockwell Nova","Roboto Slab",Georgia,serif;
--mono:ui-monospace,"SF Mono",SFMono-Regular,"JetBrains Mono","Cascadia Code",Menlo,Consolas,"Liberation Mono",monospace}
/* dark: chosen with the button (data-theme on <html>) or, without a choice, by the system; both blocks hold the same tokens */
:root[data-theme=light]{color-scheme:light}
:root[data-theme=dark]{color-scheme:dark;--bg:#0e1214;--fg:#e8eef0;--fg-2:#c3cfd3;--mute:#8e9ea5;--line:#222c31;--hi:#5fd3bb;--panel:#141a1d;--code:#25313a;--code-line:#3a4a54;--warn:#f2c56b;--warnbg:rgba(242,180,60,.2);
--ink:#e8eef0;--paper:#12181b;--unit:#26363c;--unit-focus:#1d5348;--box-0:#151b1e;--box-1:#1a2226;--box-2:#20292e;--frame:#33414a;--accent:#5fd3bb;--accent-soft:#173430;--teal-hl:rgba(95,211,187,.28);--amber:#f2c56b;--amber-hl:rgba(242,180,60,.28)}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){color-scheme:dark;--bg:#0e1214;--fg:#e8eef0;--fg-2:#c3cfd3;--mute:#8e9ea5;--line:#222c31;--hi:#5fd3bb;--panel:#141a1d;--code:#25313a;--code-line:#3a4a54;--warn:#f2c56b;--warnbg:rgba(242,180,60,.2);
--ink:#e8eef0;--paper:#12181b;--unit:#26363c;--unit-focus:#1d5348;--box-0:#151b1e;--box-1:#1a2226;--box-2:#20292e;--frame:#33414a;--accent:#5fd3bb;--accent-soft:#173430;--teal-hl:rgba(95,211,187,.28);--amber:#f2c56b;--amber-hl:rgba(242,180,60,.28)}}
*{box-sizing:border-box}body{margin:0;font:15px/1.6 var(--sans);background:var(--bg);color:var(--fg);display:flex;min-height:100vh;-webkit-font-smoothing:antialiased}
nav{width:260px;flex:none;border-right:1px solid var(--line);background:var(--panel);padding:16px 12px;overflow:auto;max-height:100vh;position:sticky;top:0}
nav ul{list-style:none;margin:0;padding-left:14px}nav>ul{padding-left:0}
nav a{display:block;margin:1px 0;padding:3px 8px;border-left:3px solid transparent;border-radius:0 3px 3px 0;color:var(--fg-2);text-decoration:none;cursor:pointer}
nav a:hover{background:var(--bg);color:var(--fg)}
nav a.on{background:var(--accent-soft);border-left-color:var(--accent);color:var(--fg);font-weight:700}
main{flex:1;min-width:0;padding:20px 32px 40px}
a{color:var(--hi);text-underline-offset:.2em;text-decoration-thickness:.07em}a:hover{text-decoration-thickness:.13em}
h1{font:400 30px/1.15 var(--slab);margin:.2em 0 .3em}h2{font:400 21px/1.2 var(--slab);margin:1.8em 0 .5em}
.mute{color:var(--mute)}.crumbs{font-size:14px}.crumbs a,.go{cursor:pointer}
.badge{display:inline-block;font:600 12px/1.6 var(--sans);padding:0 8px;border-radius:3px;border:1px solid var(--line);color:var(--mute);vertical-align:middle}
.badge.planned,.badge.deprecated,.badge.proposed{color:var(--warn);background:var(--warnbg);border-color:transparent}
.tabs button{font:600 14px/1.2 var(--sans);padding:6px 14px;margin-right:6px;border:2px solid var(--frame);background:var(--bg);color:var(--fg);border-radius:3px;cursor:pointer}
.tabs button:hover{border-color:var(--fg)}
.tabs button.on{background:var(--fg);color:var(--bg);border-color:var(--fg);box-shadow:3px 3px 0 var(--teal-hl)}
#diagram{border:1.5px solid var(--frame);border-radius:4px;padding:20px;margin:12px 0;overflow:auto;max-height:85vh;background:var(--paper)}
#diagram svg{max-width:none;height:auto;display:block;margin:0 auto}#diagram.fit svg{max-width:100%}#diagram .pick{cursor:pointer}#diagram pre{margin:8px 0 0;font-size:12px}
/* diagrams (the label fonts are not under #diagram: Mermaid measures labels outside it): paper boxes with an ink rim and a flat offset shadow, capabilities and needs of the framing unit in amber, teal lines, framing units as dashed, shaded fields */
:is(#diagram,.figure) .node :is(rect,polygon,path,circle,ellipse){fill:var(--paper)!important;stroke:var(--ink)!important;stroke-width:2px!important;filter:drop-shadow(4px 4px 0 var(--teal-hl))}
:is(#diagram,.figure) .node rect{rx:8px;ry:8px}
:is(#diagram,.figure) .node:is([id*="-p_"],[id*="-n_"]) :is(rect,polygon,path){stroke:var(--amber)!important;filter:drop-shadow(4px 4px 0 var(--amber-hl))}
:is(#diagram,.figure) .node[id*="-u_"] :is(rect,polygon,path){fill:var(--unit)!important}   /* a unit with nothing inside stands out from the fields around it */
:is(#diagram,.figure) .node.focus :is(rect,polygon,path){fill:var(--unit-focus)!important;stroke:var(--accent)!important;stroke-width:3px!important;filter:drop-shadow(5px 5px 0 var(--accent))}
:is(#diagram,.figure) .node.pick:hover :is(rect,polygon,path){stroke:var(--accent)!important;filter:drop-shadow(6px 6px 0 var(--teal-hl))}
.node .nodeLabel,.node text{font:600 16px/1.3 var(--sans)!important;color:var(--ink)!important;fill:var(--ink)!important}
:is(#diagram,.figure) .cluster>rect{fill:var(--box-0)!important;stroke:var(--frame)!important;stroke-width:1.5px!important;stroke-dasharray:6 4;rx:14px;ry:14px}
:is(#diagram,.figure) .cluster[data-depth="1"]>rect{fill:var(--box-1)!important}:is(#diagram,.figure) .cluster[data-depth="2"]>rect{fill:var(--box-2)!important}
:is(#diagram,.figure) .cluster.focus>rect{stroke:var(--accent)!important;stroke-width:2.5px!important}
.cluster-label .nodeLabel,.cluster-label text{font:700 24px/1.2 var(--sans)!important;letter-spacing:-.01em;color:var(--ink)!important;fill:var(--ink)!important;
  --halo:var(--paper);text-shadow:0 0 3px var(--halo),0 0 3px var(--halo),0 0 2px var(--halo)}
:is(#diagram,.figure) .cluster-label foreignObject{overflow:visible}:is(#diagram,.figure) .cluster-label foreignObject>div{display:block!important;width:max-content!important;text-align:left!important}
:is(#diagram,.figure) .cluster.pick:hover>rect{stroke:var(--accent)!important}
:is(#diagram,.figure) .flowchart-link{stroke:var(--accent)!important;stroke-width:2px!important;fill:none!important}
:is(#diagram,.figure) marker path,:is(#diagram,.figure) .arrowMarkerPath{fill:var(--accent)!important;stroke:var(--accent)!important}
/* line labels without a background, letters with a halo in the colour of the paper: the line stays visible behind the text */
.edgeLabel{font:500 14px/1.35 var(--sans)!important;color:var(--ink)!important}
.cluster-label .note.beside{display:-webkit-inline-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;margin:0 0 0 14px;vertical-align:middle;white-space:normal;text-align:left}
.nodeLabel .note{display:inline-block;margin-top:2px;font:400 11px/1.3 var(--sans);letter-spacing:0;color:var(--mute)!important}   /* the responsibility of a unit under its name; outside #diagram too, where Mermaid measures */
:is(#diagram,.figure) :is(.edgeLabel,.edgeLabel p,.labelBkg){background-color:transparent!important}:is(#diagram,.figure) .edgeLabel rect{fill:transparent!important}
:is(#diagram,.figure) .edgeLabel p{--halo:var(--paper);text-shadow:1px 1px 0 var(--halo),-1px -1px 0 var(--halo),1px -1px 0 var(--halo),-1px 1px 0 var(--halo),0 0 2px var(--halo),0 0 3px var(--halo),0 0 4px var(--halo)}
/* the sequence diagram of a scenario in the same look: units as boxes with an ink rim, capabilities and needs of the holding unit in amber, dashed lifelines, teal steps, the expectation as an amber note */
:is(#diagram,.figure) rect.actor{fill:var(--unit)!important;stroke:var(--ink)!important;stroke-width:2px!important;rx:8px;ry:8px;filter:drop-shadow(4px 4px 0 var(--teal-hl))}
:is(#diagram,.figure) .side rect.actor{fill:var(--paper)!important;stroke:var(--amber)!important;filter:drop-shadow(4px 4px 0 var(--amber-hl))}
:is(#diagram,.figure) .planned rect.actor{stroke-dasharray:6 4}:is(#diagram,.figure) .deprecated rect.actor{stroke-dasharray:2 2;opacity:.6}
:is(#diagram,.figure) .pick:hover rect.actor{stroke:var(--accent)!important;filter:drop-shadow(6px 6px 0 var(--teal-hl))}
:is(#diagram,.figure) :is(text.actor,text.actor tspan){font-family:var(--sans)!important;font-size:15px!important;font-weight:600!important;fill:var(--ink)!important;stroke:none!important}
:is(#diagram,.figure) :is(text.actor.kind,text.actor.kind tspan){font-size:13px!important;font-weight:400!important;font-style:italic;fill:var(--mute)!important}
:is(#diagram,.figure) :is(text.actor.what,text.actor.what tspan){font-size:13px!important;font-weight:400!important;fill:var(--fg-2)!important}
:is(#diagram,.figure) .actor-line{stroke:var(--frame)!important;stroke-width:1.5px!important;stroke-dasharray:6 4}
:is(#diagram,.figure) .messageLine0{stroke:var(--accent)!important;stroke-width:2px!important}:is(#diagram,.figure) .messageLine1{stroke:var(--fg-2)!important;stroke-width:1.5px!important;stroke-dasharray:5 4!important}
:is(#diagram,.figure) :is(.activation0,.activation1,.activation2){fill:var(--unit)!important;stroke:var(--ink)!important;stroke-width:1.5px!important}
:is(#diagram,.figure) .messageText{font-family:var(--sans)!important;font-weight:500!important;fill:var(--ink)!important;stroke:var(--paper)!important;stroke-width:4px!important;stroke-linejoin:round;paint-order:stroke}
:is(#diagram,.figure) rect.note{fill:var(--amber-hl)!important;stroke:var(--amber)!important;stroke-width:1.5px!important;rx:6px;ry:6px}:is(#diagram,.figure) rect.under{fill:var(--paper)!important;stroke:none!important;rx:6px;ry:6px}
:is(#diagram,.figure) :is(.noteText,.noteText tspan){font-family:var(--sans)!important;fill:var(--ink)!important;stroke:none!important}
#zoom{float:right;font:600 13px/1.2 var(--sans);padding:5px 12px;border:2px solid var(--frame);background:var(--bg);color:var(--fg);border-radius:3px;cursor:pointer}#zoom:hover{border-color:var(--fg)}
.st{display:inline-block;width:9px;height:9px;border-radius:50%;margin-left:6px;vertical-align:baseline;border:1.5px dashed currentColor;opacity:.75}
.st.deprecated{border-style:solid;background:linear-gradient(to top right,transparent 44%,currentColor 44% 56%,transparent 56%)}
nav .legend{margin:14px 6px 0;font-size:12px;color:var(--mute)}nav .legend .st{margin:0 4px 0 0}
nav .navhead{margin:20px 8px 4px;font:600 12px/1.4 var(--sans);text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}nav .holder{margin:8px 8px 0;font-size:12px;color:var(--mute)}
#facts{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;margin:4px 0 18px;padding:12px 16px;background:var(--panel);border-left:3px solid var(--accent);border-radius:0 4px 4px 0}#facts[hidden]{display:none}
.nw{white-space:nowrap}td.text{min-width:14em}#facts dt{font:600 12px/1.6 var(--sans);text-transform:uppercase;letter-spacing:.05em;color:var(--mute);padding-top:2px}#facts dd{margin:0}
table{border-collapse:collapse;margin:10px 0;width:100%;font-size:14px;border:1px solid var(--line)}th,td{border-bottom:1px solid var(--line);padding:8px 12px;text-align:left;vertical-align:top}
th{background:var(--panel);font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);white-space:nowrap}
code{font:.88em var(--mono);background:var(--code);padding:.04em .3em;border:1px solid var(--code-line);border-radius:3px}   /* inline code: a tint and a hairline, lighter than the page in dark */#info{overflow-x:auto}
tr.flash td{animation:flash 2.4s ease-out}#diagram text.messageText.step:hover{fill:var(--accent)!important;text-decoration:underline}#diagram line.step:hover{stroke-width:4px!important}@keyframes flash{0%,40%{background:var(--amber-hl)}}
.theme{float:right;display:flex;align-items:center;justify-content:center;width:34px;height:34px;margin:0 0 8px 16px;padding:0;border:2px solid var(--frame);border-radius:3px;background:var(--bg);color:var(--fg);cursor:pointer}
.theme:hover{border-color:var(--fg)}.theme:focus-visible{outline:2px solid var(--accent);outline-offset:3px}.theme[hidden],.theme[aria-pressed="true"] .sun,.theme:not([aria-pressed="true"]) .moon{display:none}
/* a document: README.md on the page of its unit, every other Markdown file on a page of its own; set like the chapters of unifold.md */
.prose{font-size:16px;line-height:1.65;overflow-wrap:break-word}.prose>*{max-width:46rem}.prose>:is(.table,pre,.figure){max-width:100%}.prose>:first-child{margin-top:.5em}
.prose h2{font:400 22px/1.2 var(--slab);margin:1.9em 0 .5em}.prose h3{font:700 17px/1.3 var(--sans);margin:1.7em 0 .4em}.prose :is(h4,h5,h6){font:700 15px/1.35 var(--sans);margin:1.5em 0 .3em}
.prose :is(p,ul,ol,blockquote){margin:.85em 0}.prose :is(ul,ol){padding-left:1.6em}.prose li{margin:.3em 0}.prose li>:is(p,ul,ol){margin:.35em 0}
.prose p.field{margin:.5em 0}.prose li.task{list-style:none}.prose li.task>input{margin:0 .45em 0 -1.4em;accent-color:var(--accent)}
.prose pre{margin:1.1em 0;padding:12px 16px;background:var(--code);border-radius:4px;overflow-x:auto;font:13px/1.55 var(--mono);tab-size:2}.prose pre code{background:none;border:0;padding:0;font-size:inherit}
.prose blockquote{padding:2px 0 2px 16px;border-left:3px solid var(--frame);color:var(--fg-2)}.prose hr{border:0;border-top:1px solid var(--line);margin:2em 0}.prose img{max-width:100%;height:auto}
.prose .table{overflow-x:auto;margin:1.1em 0}.prose .table table{margin:0}.prose .table th{white-space:normal}.prose :is(th,td).c{text-align:center}.prose :is(th,td).r{text-align:right}
.anchor{margin-left:.35em;color:var(--mute);text-decoration:none;opacity:0;font-weight:400}:is(h2,h3,h4,h5,h6):hover>.anchor,.anchor:focus-visible{opacity:1}
.figure{margin:1.2em 0;padding:16px;border:1.5px solid var(--frame);border-radius:4px;background:var(--paper);overflow-x:auto}.figure svg{display:block;max-width:100%;height:auto;margin:0 auto}
:is(#diagram,.figure) .node circle.state-start{fill:var(--ink)!important}:is(#diagram,.figure) path.transition{stroke:var(--accent)!important;stroke-width:2px!important;fill:none!important}   /* a state diagram: its start, its steps */
#info .wide>*{max-width:none}#info .wide>h2:first-child{margin-top:1.4em}#info .wide li{margin:.3em 0}#doc[hidden],#bar[hidden],#diagram[hidden]{display:none}
#info h3{font:600 12px/1.4 var(--sans);text-transform:uppercase;letter-spacing:.05em;color:var(--mute);margin:1.4em 0 .2em}#info ul{margin:.3em 0;padding-left:1.4em}#info li{margin:.2em 0}#info li.on{font-weight:700}
@media(hover:none){.anchor{opacity:.45}}
@media(max-width:800px){.theme{position:absolute;top:12px;right:12px;margin:0}body{display:block}nav{width:auto;max-height:none;position:static}main{padding:16px}th,td{padding:6px 8px}
  nav .docs{display:none}.prose{font-size:15.5px}.prose pre{padding:10px 12px}.figure{padding:10px}}
</style></head><body>
<nav id="tree"></nav>
<main>
<button class="theme" type="button" aria-label="Dark theme" aria-pressed="false" title="Light or dark" hidden><svg class="sun" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 13.3A8.5 8.5 0 1 1 10.7 3.5a6.6 6.6 0 0 0 9.8 9.8z"/></svg></button>
<div class="crumbs mute" id="crumbs"></div>
<h1 id="title"></h1><p id="summary"></p><p class="mute" id="meta"></p><dl id="facts" hidden></dl>
<article class="prose" id="doc" hidden></article>
<div class="tabs" id="bar"><button id="zoom" hidden></button><span id="tabs"></span></div>
<div id="diagram">Loading the diagram renderer…</div>
<div id="shared"></div>
<p class="mute" id="hint"></p>
<div id="info"></div>
</main>
__INLINE__<script type="module">
const model = __MODEL__;
const MERMAID = __MERMAID__;
const units = model.units, byPath = Object.fromEntries(units.map(u => [u.path, u]));
const el = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const file = p => model.base ? model.base + "/" + p.split("/").map(encodeURIComponent).join("/") : model.up + p.split("/").map(encodeURIComponent).join("/");
const badge = s => s && s !== "active" && s !== "accepted" ? ` <span class="badge ${esc(s.split(" ")[0])}">${esc(s)}</span>` : "";
const pick = (p, t) => `<a class="go" data-path="${esc(p)}">${esc(t ?? (p === "." ? model.name : p))}</a>` + badge(byPath[p] && byPath[p].status);
const docs = model.docs || {}, KINDS = {readme: "README", tutorials: "Tutorials", references: "Reference", explanation: "Explanation", decisions: "Decisions", skills: "Skills", other: "Other"};
const enc = s => encodeURIComponent(s).replace(/%(2F|40|3A)/g, m => decodeURIComponent(m));   // a route stays readable: unit@doc:docs/references/x.md
const hashOf = (route, anchor) => "#" + enc(route) + (anchor ? "#" + encodeURIComponent(anchor) : "");
const pageOf = p => { const d = docs[p]; return d && d.unit + "@doc:" + (d.unit === "." ? p : p.slice(d.unit.length + 1)); };   // the page of a document
const routeOf = p => docs[p] && docs[p].kind === "readme" ? docs[p].unit : pageOf(p);   // a link to a README opens its unit
const href = v => { const [p, a] = v.split("#"), r = routeOf(p); return r ? hashOf(r, a) : file(p) + (a ? "#" + encodeURIComponent(a) : ""); };   // a document opens here, any other file as it is
const ref = v => v ? (/^[a-z][a-z0-9+.-]*:/i.test(v) ? `<a href="${esc(v)}">${esc(v)}</a>` : `<a href="${esc(href(v))}">${esc(v)}</a>`) : "";
const part = (contract, name) => { const dir = contract.endsWith("/index.md") && contract.slice(0, -8) + name + ".md";   // a part: its file in a folder contract, its heading in a file
  return `<a href="${esc(href(dir && docs[dir] ? dir : contract + "#" + name))}">${esc(name)}</a>`; };
const title = p => docs[p].title || esc(p.split("/").pop().replace(/\.md$/, ""));
const plain = h => { const t = document.createElement("template"); t.innerHTML = h; return t.content.textContent; };
const docLink = (p, on) => on ? `<li class="on">${title(p)}</li>` : `<li><a href="${esc(href(p))}">${title(p)}</a>` + (docs[p].kind === "decisions" ? badge(docs[p].status || "no status") : "")
  + (docs[p].kind === "skills" && docs[p].summary ? ": " + esc(docs[p].summary) : "") + "</li>";
function groups(u){                  // the documents of a unit by kind, in the order of AGENTS.md: learn, look up, understand, decide, do
  const of = {tutorials: u.documents.tutorials, references: u.documents.references, explanation: u.documents.explanation, decisions: u.decisions.map(d => d.path),
    skills: u.skills.map(s => s.path), other: Object.keys(docs).filter(p => docs[p].unit === u.path && docs[p].kind === "other")};
  return Object.entries(KINDS).map(([k, label]) => [k, label, (of[k] || []).filter(p => docs[p])]).filter(g => g[2].length);}
function anchors(box, route){        // the link beside a heading; the ids come with the document
  for (const h of box.querySelectorAll(":is(h2,h3,h4,h5,h6)[id^='md-']")) h.insertAdjacentHTML("beforeend", ` <a class="anchor" href="${esc(hashOf(route, h.id.slice(3)))}" aria-label="Link to this section">#</a>`);}
let figure = 0;
async function figures(box){         // the Mermaid blocks of a document, drawn like the map; without Mermaid they stay source
  if (!mermaid) return;
  for (const pre of [...box.querySelectorAll("pre.mermaid")]) {
    try { const {svg} = await mermaid.render("f" + ++figure, pre.textContent); if (!pre.isConnected) return;
      const f = document.createElement("div"); f.className = "figure"; f.innerHTML = svg; pre.replaceWith(f);
    } catch (err) { if (pre.isConnected) pre.title = "The diagram could not be drawn: " + err; }
  }
}
function seek(anchor){const t = anchor && document.getElementById("md-" + anchor); if (t) t.scrollIntoView();}
let mermaid = null, mermaidError = null, fit = null, fitted = false, state = {path: ".", kind: null}, row = null;
function shade(){                    // a framing box is shaded by how deep it sits; its name moves to its top left
  const clusters = [...el("diagram").querySelectorAll(".cluster")].map(c => [c, c.querySelector(":scope > rect").getBoundingClientRect()]);
  for (const [c, r] of clusters) c.dataset.depth = Math.min(2, clusters.filter(([o, b]) => o !== c && b.left <= r.left && b.right >= r.right && b.top <= r.top && b.bottom >= r.bottom).length);
  for (const [c] of clusters) {      // the name of a framing box: top left, drawn above the boxes inside it, which start only 20px lower
    const rect = c.querySelector(":scope > rect"), name = c.querySelector(":scope > .cluster-label");
    if (!name) continue;
    name.setAttribute("transform", `translate(${+rect.getAttribute("x") + 16}, ${+rect.getAttribute("y") + 8})`);
    name.style.setProperty("--halo", getComputedStyle(rect).fill); name.dataset.frame = c.id; c.parentNode.appendChild(name);
  }
}
function zoom(map){const box = el("diagram"), svg = box.querySelector("svg"), b = el("zoom");
  box.classList.remove("fit"); const room = box.clientWidth - 24, width = svg ? svg.getBoundingClientRect().width : 0;
  const wide = width > room; fitted = wide && (fit ?? (map || width <= room * 1.45));   // a map opens fitted; a scenario: a little too wide shrinks, much too wide scrolls; a choice with the button holds
  b.hidden = !wide; box.classList.toggle("fit", fitted);
  b.textContent = fitted ? "Full size" : "Fit to width"; box.scrollLeft = 0;}
const scenes = model.scenarios || [], scene = (p, n) => scenes.find(s => s.unit === p && s.name === n);
const decode = s => { try { return decodeURIComponent(s); } catch { return s; } };
function fromHash(){const raw = location.hash.slice(1), cut = raw.indexOf("#");   // unit@kind, holder@scenario:name or unit@doc:path, then #anchor
  const h = decode(cut < 0 ? raw : raw.slice(0, cut)), at = h.indexOf("@"), p = at < 0 ? h : h.slice(0, at), k = at < 0 ? "" : h.slice(at + 1);
  const s = k.startsWith("scenario:") ? scene(p, k.slice(9)) : null, d = k.startsWith("doc:") ? (p === "." ? "" : p + "/") + k.slice(4) : null;
  state = {path: byPath[p] ? p : ".", kind: s || d || !k ? null : k, scenario: s, doc: d && docs[d] ? d : null, anchor: cut < 0 ? "" : decode(raw.slice(cut + 1))};}
function go(path, kind){location.hash = enc(path + (kind ? "@" + kind : ""));}
function tree(path){const u = byPath[path]; const kids = u.children.map(c => tree(c.path)).join("");
  return `<li><a data-path="${esc(path)}" class="go${path === state.path && !state.scenario ? " on" : ""}">${esc(u.name)}${u.status !== "active" ? `<span class="st ${esc(u.status)}" title="${esc(u.status)}"></span>` : ""}</a>${kids ? "<ul>" + kids + "</ul>" : ""}</li>`;}
const named = p => p === "." ? model.name : p;
const pin = (p, t) => { const st = byPath[p].status; return `<span class="nw"><a class="go" data-path="${esc(p)}">${esc(t ?? named(p))}</a>` + (st !== "active" ? `<span class="st ${esc(st)}" title="${esc(st)}"></span>` : "") + "</span>"; };   // the status as in the tree
function docTree(u){                 // the documents of the unit shown, beside the map
  const g = groups(u); if (!g.length) return "";
  return `<div class="docs"><p class="navhead">Documents of ${esc(u.name)}</p>` + g.map(([k, label, paths]) => `<p class="holder">${label}</p><ul>`
    + paths.map(p => `<li><a href="${esc(href(p))}"${p === state.doc || (state.doc && docs[state.doc].contract === p) ? ' class="on"' : ""}>${title(p)}</a></li>`).join("") + "</ul>").join("") + "</div>";}
function map(on){for (const id of ["bar", "diagram", "shared", "hint"]) el(id).hidden = !on;}
const sceneLink = (s, t) => `<a class="go" data-path="${esc(s.unit)}" data-scenario="${esc(s.name)}">${t ?? esc(s.name)}</a>`;
function sceneTree(){                // every scenario of the project, under the unit that holds it when there are several
  const holders = [...new Set(scenes.map(s => s.unit))];
  return scenes.length ? "<p class='navhead'>Scenarios</p>" + holders.map(h => (holders.length > 1 ? `<p class="holder">${esc(named(h))}</p>` : "")
    + "<ul>" + scenes.filter(s => s.unit === h).map(s => `<li><a class="go${s === state.scenario ? " on" : ""}" data-path="${esc(s.unit)}" data-scenario="${esc(s.name)}" title="${esc(s.summary)}">${esc(s.name)}</a></li>`).join("") + "</ul>").join("") : "";}
const legend = ["planned", "deprecated"].filter(s => units.some(u => u.status === s))
  .map(s => `<span class="st ${s}"></span>${s}`).join(" &nbsp; ");
function note(i){return i.config ? " <span class='mute'>(" + esc(i.config) + ")</span>" : "";}
function who(list, key){return list.map(i => i.outside ? "outside the project" + note(i)
  : pick(i.unit) + " · <code>" + esc(i[key]) + "</code>" + note(i)).join("<br>") || "–";}
function code(text){return esc(text).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/^- /, "");}
async function render(){
  const u = byPath[state.path]; const kinds = Object.keys(u.diagrams);
  const kind = kinds.includes(state.kind) ? state.kind : (kinds.includes("component") ? "component" : kinds[0]);
  el("tree").innerHTML = "<ul>" + tree(".") + "</ul>" + docTree(u) + sceneTree() + (legend ? `<p class="legend">${legend}</p>` : "");
  const chain = []; for (let p = u.parent; p; p = byPath[p.path].parent) chain.unshift(p.path);
  if (state.doc) return reading(state.doc, chain);
  map(true);
  if (state.scenario) return story(state.scenario, chain);
  el("facts").hidden = true; el("hint").textContent = "Click a box to open that unit, a capability or need to find it in the tables. An arrow points from a need to its provider. A dashed border marks a unit that is planned.";
  document.title = u.name + " · " + model.name;
  el("crumbs").innerHTML = chain.map(p => `<a class="go" data-path="${esc(p)}">${esc(byPath[p].name)}</a>`).concat(esc(u.name)).join(" / ");
  const readme = u.readme && docs[u.readme];   // the README: its first paragraph on top (the responsibility is in the boxes of the diagram), its Why above the tables
  el("title").innerHTML = esc(u.name) + badge(u.status); el("summary").innerHTML = readme && readme.intro || esc(u.responsibility);
  el("meta").innerHTML = [u.kind, u.owner && "owner " + u.owner].filter(Boolean).map(esc)
    .concat([`<a href="${esc(file(u.manifest))}">manifest</a>`], u.readme ? [`<a href="${esc(readme ? hashOf(pageOf(u.readme)) : file(u.readme))}">README</a>`] : [],
            u.agents ? [`<a href="${esc(href(u.agents))}">AGENTS.md</a>`] : []).join(" · ");
  el("doc").hidden = true;
  el("tabs").innerHTML = kinds.map(k => `<button data-kind="${k}" class="${k === kind ? "on" : ""}">${k}</button>`).join("");
  let html = readme && readme.why ? `<div class="prose wide">${readme.why}</div>` : "";   // Why, then what the unit leaves out, as sections of the same rank
  const p = Object.entries(u.capabilities), n = Object.entries(u.needs);
  if (u.secret) html += `<div class="prose wide"><p><strong>Secret:</strong> ${esc(u.secret.what)} (${ref(u.secret.decision)})</p></div>`;
  if (u.not && u.not.length) html += `<div class="prose wide"><h2 id="out-of-scope">Out of scope</h2><ul>` + u.not.map(n => "<li>" + code(n.text) + (n.need ? ` → <code>${esc(n.need)}</code>` : "") + "</li>").join("") + "</ul></div>";
  if (p.length) html += "<h2>Capabilities</h2><table><tr><th>Capability</th><th>Kind</th><th>Summary</th><th>Contract</th><th>Used by</th></tr>"
    + p.map(([k, v]) => `<tr id="capability:${esc(k)}"><td><code>${esc(k)}</code></td><td>${esc(v.kind)}</td><td>${esc(v.summary)}</td><td>${ref(v.contract)}${v.parts && v.contract ? " <span class='mute'>(" + v.parts.map(n => part(v.contract, n)).join(", ") + ")</span>" : ""}</td><td>${who(v["used-by"], "need")}</td></tr>`).join("") + "</table>";
  if (n.length) html += "<h2>Needs</h2><table><tr><th>Need</th><th>Kind</th><th>Summary</th><th>Contract</th><th>Provided by</th></tr>"
    + n.map(([k, v]) => `<tr id="need:${esc(k)}"><td><code>${esc(k)}</code>${v.optional ? " <span class='mute'>optional</span>" : ""}${v.platform ? " <span class='mute'>platform</span>" : ""}</td><td>${esc(v.kind)}</td><td>${esc(v.summary)}</td><td>${ref(v.contract)}${v.parts && v.contract ? " <span class='mute'>(" + v.parts.map(n => part(v.contract, n)).join(", ") + ")</span>" : ""}</td><td>${who(v["provided-by"], "capability")}</td></tr>`).join("") + "</table>";
  if (u.children.length) html += "<h2>Units inside</h2><table><tr><th>Unit</th><th>Kind</th><th>Responsibility</th></tr>"
    + u.children.map(c => `<tr><td>${pick(c.path, c.name)}</td><td>${esc(byPath[c.path].kind)}</td><td>${esc(c.responsibility)}</td></tr>`).join("") + "</table>";
  if (u.scenarios && u.scenarios.length) html += "<h2>Scenarios</h2><ul>" + u.scenarios.map(s => `<li>${scene(s.unit, s.name) ? sceneLink(s) : esc(s.name)}: ${esc(s.summary)}${s.unit !== u.path ? ` <span class="mute">(held by <a class="go" data-path="${esc(s.unit)}">${esc(named(s.unit))}</a>)</span>` : ""}</li>`).join("") + "</ul>";
  const g = groups(u);
  if (g.length) html += "<h2>Documents</h2>" + g.map(([k, label, paths]) => `<h3 id="docs:${k}">${label}</h3><ul>` + paths.map(p => docLink(p)).join("") + "</ul>").join("");
  el("info").innerHTML = html;
  if (readme && readme.why) { anchors(el("info").firstChild, u.path); figures(el("info").firstChild); }
  const target = row && document.getElementById(row); row = null;   // a capability or need clicked in the diagram
  if (target) { target.scrollIntoView({behavior: "smooth", block: "center"}); target.classList.add("flash"); }
  const d = u.diagrams[kind];
  el("shared").innerHTML = d && d.shared.length ? "<p class='mute'>Shared connections, not drawn:</p><ul>" + d.shared.map(s => "<li>" + code(s) + "</li>").join("") + "</ul>" : "";
  el("zoom").hidden = true;
  if (!d) { el("diagram").textContent = "No diagram for this unit."; return; }
  return draw(d.source, () => {
    shade(); zoom(true);
    const ids = Object.keys(d.nodes).concat(Object.keys(d.sides));
    for (const node of el("diagram").querySelectorAll("[id]")) {
      const hit = ids.find(id => node.id === id || new RegExp("(^|-)" + id + "(-\\d+)?$").test(node.id));
      if (hit && (node.classList.contains("node") || node.classList.contains("cluster"))) {
        node.classList.add("pick"); node.addEventListener("click", ev => {ev.stopPropagation();
          if (d.nodes[hit]) { go(d.nodes[hit]); return; }
          const [path, side, name] = d.sides[hit]; row = side + ":" + name;   // a capability or need: its row in the tables of its unit
          if (path === state.path) render(); else go(path);});
      }
    }
    for (const name of el("diagram").querySelectorAll(".cluster-label[data-frame]")) {   // a name drawn apart from its box opens the same unit
      const frame = document.getElementById(name.dataset.frame);
      if (frame && frame.classList.contains("pick")) { name.classList.add("pick"); name.addEventListener("click", ev => {ev.stopPropagation(); frame.dispatchEvent(new MouseEvent("click"));}); }
      const hit = frame && Object.keys(d.nodes).find(id => frame.id === id || new RegExp("(^|-)" + id + "(-\\d+)?$").test(frame.id));
      const unit = hit && byPath[d.nodes[hit]], text = name.querySelector(".nodeLabel"), fo = name.querySelector("foreignObject");
      if (unit && unit.responsibility && text && fo) {   // the responsibility of a frame beside its name, in two lines at most: it takes no room from the boxes below
        const room = +frame.querySelector(":scope > rect").getAttribute("width") - +fo.getAttribute("width") - 56;
        text.insertAdjacentHTML("beforeend", `<span class="note beside" title="${esc(unit.responsibility)}" style="max-width:${Math.round(Math.max(170, Math.min(440, room)))}px">${esc(unit.responsibility)}</span>`);
      }
    }
  });
}
function story(s, chain){             // a scenario: what it is and expects, its sequence diagram, its steps and its lifelines
  const h = byPath[s.unit], d = s.diagram, lives = Object.values(d.lifelines);
  const life = (text, unit, side) => unit ? pin(unit, text) : `<a class="go" data-path="${esc(s.unit)}" data-row="${side}:${esc(text)}"><code>${esc(text)}</code></a>`;
  document.title = s.name + " · " + model.name;
  el("crumbs").innerHTML = chain.concat(s.unit).map(p => `<a class="go" data-path="${esc(p)}">${esc(byPath[p].name)}</a>`).concat(esc(s.name)).join(" / ");
  el("title").innerHTML = esc(s.name); el("summary").textContent = s.summary;
  el("meta").innerHTML = ["scenario of " + pin(s.unit), s.hops.length + (s.hops.length === 1 ? " step" : " steps"), lives.length + " lifelines"]
    .concat(s.page ? [`<a href="${esc(file(s.page))}">Markdown</a>`] : [], [`<a href="${esc(file(h.manifest))}">manifest</a>`]).join(" · ");
  el("doc").hidden = true;
  el("facts").innerHTML = (s.source ? `<dt>Source</dt><dd>${code(s.source)}</dd>` : "") + `<dt>Expect</dt><dd>${code(s.expect)}</dd>`; el("facts").hidden = false;
  el("tabs").innerHTML = `<button class="on">sequence</button>`; el("shared").innerHTML = ""; el("zoom").hidden = true;
  el("hint").textContent = `An arrow is one step, numbered in order, along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. The note at the end is what the scenario expects. Click a step to find it in the table, a lifeline to open its unit, or a capability or need of ${named(s.unit)} to find it in its tables. A dashed border marks a unit that is planned.`;
  let html = "<h2>Steps</h2><table><tr><th>#</th><th>Caller</th><th>Target</th><th>Part</th><th>Contract</th><th>Wiring</th></tr>" + s.hops.map((x, i) => x.unresolved
    ? `<tr id="step:${i + 1}"><td>${i + 1}</td><td colspan="5"><code>${esc(x.unresolved)}</code> <span class="badge planned">does not resolve</span> ${esc(x.error)}</td></tr>`
    : `<tr id="step:${i + 1}"><td>${i + 1}</td><td>${life(x.caller, x["caller-unit"], "capability")}</td><td>${life(x.target, x["target-unit"], "need")}</td><td><a href="${esc(href(x["part-file"] && x["part-file"] !== x.contract ? x["part-file"] : x.contract + "#" + x.part))}"><code>${esc(x.part)}</code></a>${x["part-kind"] ? " <span class='mute'>" + esc(x["part-kind"]) + "</span>" : ""}</td><td>${ref(x.contract)}</td><td>${x.via.map(v => `<span class="nw"><code>${esc(v.key)}</code> <span class="mute">in</span> ${pin(v.unit)}</span>`).join("<br>") || "–"}</td></tr>`).join("") + "</table>";
  html += "<h2>Lifelines</h2><table><tr><th>Lifeline</th><th>Kind</th><th>Responsibility</th><th>Steps</th></tr>" + lives.map(l => {
    const u = l.side ? null : byPath[l.unit], e = l.side ? h[l.side === "capability" ? "capabilities" : "needs"][l.entry] : null;
    const steps = (k, word) => { const at = s.hops.flatMap((x, i) => x[k] === l.name ? [i + 1] : []); return at.length ? word + " " + at.join(", ") : ""; };
    return `<tr><td>${life(l.name, u && l.unit, l.side)}</td><td>${u ? esc(u.kind) : esc(l.side + " of " + named(s.unit))}</td><td class="text">${esc(u ? u.responsibility : e && e.summary)}</td><td>${[steps("caller", "calls in"), steps("target", "called in")].filter(Boolean).join("<br>")}</td></tr>`;}).join("") + "</table>";
  const more = scenes.filter(o => o.unit === s.unit && o !== s);
  if (more.length) html += `<h2>More scenarios of ${esc(named(s.unit))}</h2><ul>` + more.map(o => `<li>${sceneLink(o)}: ${esc(o.summary)}</li>`).join("") + "</ul>";
  el("info").innerHTML = html;
  return draw(d.source, () => {
    for (const box of el("diagram").querySelectorAll("rect.actor[name]")) {   // a lifeline, at the top and the bottom: its unit, or its row in the tables
      const l = d.lifelines[box.getAttribute("name")], g = box.parentNode; if (!l) continue;
      g.classList.add("pick", l.side ? "side" : byPath[l.unit].status);
      g.querySelectorAll("text.actor").forEach((t, i) => t.classList.add(i ? (t.textContent.startsWith("«") ? "kind" : "what") : "who"));   // the lines of its box
      g.addEventListener("click", ev => {ev.stopPropagation(); row = l.side ? l.side + ":" + l.entry : null; go(l.unit);});
    }
    for (const label of el("diagram").querySelectorAll("text.messageText")) {   // a step, by the number of its label: its row in the table
      const n = /^\s*(?:(\d+)\s*·|↩\s*(\d+))/.exec(label.textContent), line = label.nextElementSibling; if (!n) continue;   // `3 · part`, or `↩ 3` for the result of step 3
      for (const part of line && /messageLine/.test(line.getAttribute("class")) ? [label, line] : [label]) {
        part.classList.add("pick", "step"); part.addEventListener("click", ev => {ev.stopPropagation(); flash("step:" + (n[1] || n[2]));});
      }
    }
    for (const note of el("diagram").querySelectorAll("rect.note")) { const under = note.cloneNode(); under.setAttribute("class", "under"); note.before(under); }   // paper under the note: no lifeline shows through
    zoom();
  });
}
function reading(p, chain){           // a document: where it belongs, its front matter, its text, and the documents beside it
  const d = docs[p], u = byPath[d.unit], label = KINDS[d.kind] || "Documents", whole = d.contract && docs[d.contract];
  document.title = plain(title(p)) + " · " + model.name;
  el("crumbs").innerHTML = chain.concat(d.unit).map(c => `<a class="go" data-path="${esc(c)}">${esc(byPath[c].name)}</a>`)
    .concat(`<a class="go" data-path="${esc(d.unit)}" data-row="docs:${esc(d.kind)}">${label}</a>`, whole ? [`<a href="${esc(href(d.contract))}">${title(d.contract)}</a>`] : [], title(p)).join(" / ");
  el("title").innerHTML = title(p) + badge(d.status); el("summary").textContent = d.summary || "";
  el("meta").innerHTML = [(whole ? "Part of a contract" : label) + " of " + pin(d.unit), `<a href="${esc(file(p))}">Markdown</a>`].join(" · ");
  el("facts").innerHTML = (d.facts || []).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join(""); el("facts").hidden = !d.facts;
  map(false); el("doc").className = "prose"; el("doc").hidden = false; el("doc").innerHTML = d.html; anchors(el("doc"), pageOf(p));
  const g = groups(u).find(x => x[0] === d.kind), near = whole ? whole.parts : g ? g[2] : [];
  el("info").innerHTML = near.length > 1 ? `<h2>${whole ? "Parts of " + title(d.contract) : label + " of " + esc(u.name)}</h2><ul>` + near.map(o => docLink(o, o === p)).join("") + "</ul>" : "";
  return figures(el("doc"));
}
function flash(id){const target = document.getElementById(id); if (!target) return;   // a row of the tables: in view, lit up for a moment
  target.scrollIntoView({behavior: "smooth", block: "center"}); target.classList.remove("flash"); void target.offsetWidth; target.classList.add("flash");}
let drawn = 0;
async function draw(source, wire){   // Mermaid source into the diagram box; `wire` makes its boxes clickable
  el("zoom").hidden = true;
  if (!mermaid) {
    if (mermaidError) el("diagram").innerHTML = "<p>The diagram renderer (Mermaid) could not be loaded" + (MERMAID.url ? " from " + esc(MERMAID.url) : "")
      + ". The tables below are complete without it. To embed the renderer in this page: <code>unifold site --mermaid path/to/mermaid.min.js</code>.</p><details><summary>Diagram source</summary><pre>" + esc(source) + "</pre></details>";
    return;
  }
  const mine = ++drawn;
  try {
    const {svg} = await mermaid.render("g" + Date.now(), source);
    if (mine !== drawn) return;          // a newer page is on its way
    el("diagram").innerHTML = svg; wire();
  } catch (err) { el("diagram").innerHTML = "<p>The diagram could not be drawn: " + esc(err) + "</p><pre>" + esc(source) + "</pre>"; }
}
document.addEventListener("click", ev => {
  const a = ev.target.closest(".go");
  if (a) { row = a.dataset.row || null;   // a capability or need of the holder of a scenario: its row in the tables
    if (a.dataset.scenario) go(a.dataset.path, "scenario:" + a.dataset.scenario);
    else if (row && a.dataset.path === state.path && !state.scenario && !state.doc) render(); else go(a.dataset.path);
    return; }
  const b = ev.target.closest("button[data-kind]"); if (b) go(state.path, b.dataset.kind);
  if (ev.target.id === "zoom") { fit = !fitted; zoom(); }
});
addEventListener("hashchange", () => { const was = state, top = !row; fromHash(); render();
  const main = document.querySelector("main");   // another page: from its top, unless a row or a heading is to be shown
  if (state.anchor) seek(state.anchor);
  else if (top && (was.path !== state.path || was.scenario !== state.scenario || was.doc !== state.doc) && main.getBoundingClientRect().top < 0) main.scrollIntoView(); });
async function loadMermaid(){
  if (window.mermaid) return window.mermaid;
  if (!MERMAID.url) throw new Error("no renderer");
  if (/\.mjs(\?|$)/.test(MERMAID.url)) return (await import(MERMAID.url)).default;
  await new Promise((ok, fail) => { const s = document.createElement("script"); s.src = MERMAID.url;
    s.onload = ok; s.onerror = () => fail(new Error("not loaded")); document.head.appendChild(s); });
  return window.mermaid;
}
fromHash(); render(); seek(state.anchor);
function setup(){   // the renderer; set up again when light or dark changes
  mermaid.initialize({startOnLoad: false, securityLevel: "loose", maxEdges: 2000,   // the colours come from the style sheet above
    flowchart: {useMaxWidth: false, curve: "basis", padding: 8, nodeSpacing: 28, rankSpacing: 60,
      subGraphTitleMargin: {top: 10, bottom: 18}},   // room for the large name of a framing unit above its content
    sequence: {useMaxWidth: false, width: 120, actorMargin: 36, boxMargin: 12, messageMargin: 44, noteMargin: 12,   // a scenario
      actorFontSize: 14, actorFontWeight: 500, messageFontSize: 14, messageFontWeight: 500, noteFontSize: 14, noteAlign: "left"},
    theme: "base", themeVariables: {fontFamily: getComputedStyle(document.body).getPropertyValue("--sans"), fontSize: "16px",
      darkMode: getComputedStyle(document.documentElement).colorScheme === "dark"}});   // dark as the style sheet has it: by the button or by the system
}
try {
  mermaid = await loadMermaid();
  setup();
} catch (err) { mermaid = null; mermaidError = err; }
render();
addEventListener("themechange", () => { if (mermaid) { setup(); render(); } });   // light or dark changed: draw again in the new colours
</script></body></html>
"""


def build_site(project: Project, out: str, mermaid: str) -> str:
    """Write the HTML explorer. `mermaid` is a URL, or a local single-file build to embed."""
    if os.path.isdir(out):
        out = os.path.join(out, "unifold.html")
    inline, source = "", {"url": mermaid}
    if not re.match(r"^https?://", mermaid):
        if not os.path.isfile(mermaid):
            raise Fail("no-mermaid", f"--mermaid: {mermaid} is neither a URL nor a file")
        text = read_text(mermaid)
        if re.search(r"^\s*(import|export)\b", text[:20000], re.M) or mermaid.endswith(".mjs"):
            raise Fail("no-mermaid", "--mermaid: a local file must be the single-file build "
                                     "`mermaid.min.js` (dist/mermaid.min.js of the npm package), "
                                     "not the ES module")
        inline = "<script>" + text.replace("</script", "<\\/script") + "</script>\n"
        source = {"url": ""}
    saved, project.links = project.links, "none"
    out_dir = os.path.dirname(os.path.abspath(out))
    units = []
    sides = {side_id(u, "p", c): [u.rel, "capability", c] for u in project.units for c in u.capabilities}
    sides.update({side_id(u, "n", n): [u.rel, "need", n] for u in project.units for n in u.needs})
    for unit in project.units:
        info = describe(project, unit)
        if unit is project.root_unit:            # the skills `init --agents` installs are the tool's
            info["skills"] = [s for s in info["skills"] if s["name"] not in SKILLS]
        for name, key in (("README.md", "readme"), ("AGENTS.md", "agents")):
            path = os.path.join(unit.path, name)
            info[key] = project.rel(path) if project.kind_of(path) == "file" else None
        charts = {}
        if unit.parent is not None:
            charts["context"] = diagram(project, unit.parent, 0, out_dir, focus=unit, notes=True)
        elif not unit.children:
            charts["context"] = (lone_context(project, unit, out_dir, notes=True), [unit],
                                 {node_id(unit): unit}, [])
        if unit.children:
            charts["component"] = diagram(project, unit, 1, out_dir, notes=True)
        if any(c.children for c in unit.children):
            charts["architecture"] = diagram(project, unit, MAX_DEPTH, out_dir, notes=True)
        info["diagrams"] = {kind: {"source": "\n".join(value[0]),
                                   "nodes": {i: u.rel for i, u in value[2].items()},
                                   "sides": {i: side for i, side in sides.items()
                                             if re.search(rf"^\s+{i}\b", "\n".join(value[0]), re.M)},
                                   "shared": value[3]} for kind, value in charts.items()}
        units.append(info)
    scenarios = []                                    # the scenario pages: the data of `model`, a lifeline per name
    for scenario in resolved_scenarios(project):
        holder, data = scenario["unit"], scenario_data(project, scenario)
        lines, ids = scenario_sequence(scenario)
        lifelines = {}                                # participant id -> its unit, or a capability or need of the holder
        for (_, result, _), hop in zip(scenario["hops"], data["hops"]):
            if not result:
                continue
            part = contract_of_path(project, result["contract"])["parts"].get(result["part"]) or {}
            hop["part-file"] = project.rel(part["file"]) if part.get("file") else None
            for name, unit, side, entry in ((result["caller"], result["caller-unit"], "capability", result["caller-capability"]),
                                            (result["target"], result["target-unit"], "need", result["target-need"])):
                lifelines[ids[name]] = {"name": name, "unit": unit.rel} if unit else \
                    {"name": name, "unit": holder.rel, "side": side, "entry": entry}
        page = os.path.join(holder.path, "docs", "diagrams", f"scenario-{scenario['name']}.md")
        scenarios.append({**data, "unit": holder.rel, "page": project.rel(page) if project.kind_of(page) == "file" else None,
                          "diagram": {"source": "\n".join(lines),
                                      "lifelines": {i: lifelines[i] for i in ids.values() if i in lifelines}}})
    project.links = saved
    base = saved.rstrip("/") if saved not in ("none", "relative") else ""
    up = os.path.relpath(project.root, out_dir).replace(os.sep, "/")
    up = "" if up == "." else up + "/"
    docs = site_documents(project, {u["path"]: u["diagrams"] for u in units},
                          {(s["unit"], s["name"]) for s in scenarios}, base, up)
    model = {"name": project.root_unit.name, "units": units, "scenarios": scenarios, "docs": docs,
             "base": base, "up": up}
    parts = {"__TITLE__": cell(project.root_unit.name).replace("<", "&lt;"),
             "__MODEL__": json.dumps(model, ensure_ascii=False).replace("</", "<\\/"),
             "__MERMAID__": json.dumps(source), "__INLINE__": inline}
    html = re.sub(r"__(?:TITLE|MODEL|MERMAID|INLINE)__", lambda m: parts[m.group()], SITE)
    write_text(out, html)
    return out


# --------------------------------------------------------------- commands

def run_check(path: str, fix=False, strict=False, only=None, ignore=None) -> dict:
    """Check the project that contains `path`. Returns the result as plain data."""
    project = open_project(path, need_usable=False)
    fixed = None
    if project.usable:
        if fix:
            fixed = write_generated(project)
            project = Project(project.root)
        for unit in project.units:
            if not unit.broken:
                check_manifest(project, unit)
            check_wiring(project, unit)
        check_kinds(project)
        check_scenarios(project)
        check_contracts(project)
        for unit in project.units:
            check_documents(project, unit)
        check_generated(project)
    seen, findings, ignored = set(), [], {}
    for item in project.findings:
        key = (item["rule"], item["file"], item["line"], item["message"])
        if key in seen or (only and item["rule"] not in only):
            continue
        seen.add(key)
        if ignore and item["rule"] in ignore:
            ignored[item["rule"]] = ignored.get(item["rule"], 0) + 1
            continue
        findings.append(item)
    first = {"M1": 0, "S1": 0}
    findings.sort(key=lambda f: (first.get(f["rule"], 1), sort_key(f["file"]) if f["file"] != "."
                                 else [], f["line"] or 0, SEVERITY_ORDER[f["severity"]],
                                 f["rule"], f["message"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    rules: dict = {}
    for item in findings:
        rules[item["rule"]] = rules.get(item["rule"], 0) + 1
    summary = {"units": len(project.units), **counts, "rules": rules, "ignored": dict(sorted(ignored.items())),
               "root": project.root, "tool": TOOL_VERSION}
    if fixed is not None:
        summary["fixed"] = fixed
    ok = not counts["error"] and not (strict and counts["warn"])
    return {"ok": ok, "summary": summary, "findings": findings}


def print_check(result: dict, quiet=False):
    for item in result["findings"]:
        if quiet and item["severity"] == "info":
            continue
        where = item["file"] + (f":{item['line']}" if item["line"] else "")
        print(f"{item['severity']} {item['rule']} {where}: {item['message']}")
        if not quiet and item["fix"]:
            print(f"    fix: {item['fix']}")
    summary = result["summary"]
    fixed = summary.get("fixed")
    if fixed and (fixed["written"] or fixed["removed"]):
        print(f"fixed: {len(fixed['written'])} generated file(s) written, "
              f"{len(fixed['removed'])} removed")
    if fixed and fixed["refused"]:
        print("not overwritten (no generated marker): " + ", ".join(fixed["refused"]))
    per_rule = [f"{rule}×{count}" for rule, count in sorted(summary["rules"].items())]
    per_rule += [f"{rule}×{count} ignored" for rule, count in sorted(summary.get("ignored", {}).items())]
    print(f"{summary['units']} unit(s): {summary['error']} error(s), {summary['warn']} "
          f"warning(s), {summary['info']} info" + (f"  [{', '.join(per_rule)}]" if per_rule else ""))


def print_github(result: dict):
    """Workflow commands that put findings on the pull request."""
    def esc(text, prop=False):
        text = str(text).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        return text.replace(":", "%3A").replace(",", "%2C") if prop else text
    root, cwd = result["summary"]["root"], os.getcwd()
    for item in result["findings"]:
        level = {"error": "error", "warn": "warning", "info": "notice"}[item["severity"]]
        path = os.path.relpath(os.path.join(root, *item["file"].split("/")), cwd) \
            if item["file"] != "." else os.path.relpath(root, cwd)
        props = f"file={esc(path.replace(os.sep, '/'), True)}"
        if item["line"]:
            props += f",line={item['line']}"
        props += f",title={esc('unifold ' + item['rule'], True)}"
        text = item["message"] + (f" Fix: {item['fix']}" if item["fix"] else "")
        print(f"::{level} {props}::{esc(text)}")
    summary = result["summary"]
    print(f"unifold: {summary['units']} unit(s), {summary['error']} error(s), "
          f"{summary['warn']} warning(s), {summary['info']} info")


def scenario_data(project: Project, scenario: dict) -> dict:
    """One resolved scenario as plain data: an entry of `scenarios` in the schema `unifold-model`."""
    rel, hops = project.rel, []
    for hop, result, error in scenario["hops"]:
        if result:
            hops.append({"caller": result["caller"], "target": result["target"], "part": result["part"],
                         "part-kind": result.get("kind"), "contract": rel(result["contract"]),
                         "caller-unit": result["caller-unit"].rel if result["caller-unit"] else None,
                         "target-unit": result["target-unit"].rel if result["target-unit"] else None,
                         "via": [{"unit": holder.rel, "key": key} for holder, key in result["via"]]})
        else:
            hops.append({"caller": None, "target": None, "part": None, "contract": None,
                         "caller-unit": None, "target-unit": None, "via": [],
                         "unresolved": hop, "error": error})
    spec = scenario["spec"]
    return {"name": scenario["name"], "summary": spec["summary"], "source": spec["source"] or None,
            "expect": spec["expect"], "hops": hops, "x": spec["x"]}


def build_model(project: Project) -> dict:
    """The resolved project as plain data: the schema `unifold-model` of tool-json.md."""
    rel = project.rel

    def end(item: dict, side: str) -> dict:
        if item["where"] == "outside":
            key = "root-need" if side == "provider" else "root-capability"
            return {"outside": True, key: item["capability" if side == "provider" else "need"],
                    "config": item.get("config")}
        return {"unit": item["unit"].rel, "capability" if side == "provider" else "need":
                item["capability" if side == "provider" else "need"], "config": item.get("config")}

    def contract_parts(unit: Unit, spec: dict):
        target = contract_target(project, unit, spec.get("contract"))[1]
        if not target or project.kind_of(target) != "file":
            return None, None
        contract = contract_of_path(project, target)
        return ([{"name": name, "kind": part["kind"]} for name, part in contract["parts"].items()],
                contract["fake"])

    def entry(unit: Unit, name: str, spec: dict, side: str) -> dict:
        parts, fake = contract_parts(unit, spec)
        data = {"name": name, "summary": spec["summary"], "kind": spec["kind"] or None,
                "contract": contract_target(project, unit, spec["contract"])[0] or None,
                "parts": spec["parts"], "contract-parts": parts, "fake": fake}
        if side == "needs":
            data.update({"optional": spec["optional"], "platform": spec["platform"],
                         "final-providers": [end(i, "provider") for i in providers_of(unit, name)]})
        else:
            data["final-users"] = [end(i, "user") for i in users_of(unit, name)]
        data["x"] = spec.get("x", {})
        return data

    def wiring_rows(unit: Unit) -> list:
        rows = []
        for capability, conn in unit.impl.items():
            for e in conn.entries:
                rows.append({"key": conn.key, "value": e.raw, "alternative": e.config, "form": "implemented-by",
                             "user": None, "need": None, "provider": e.unit.rel, "capability": e.capability,
                             "to-need": None})
        for need, conn in unit.inner.items():
            for e in conn.entries:
                rows.append({"key": conn.key, "value": e.raw, "alternative": e.config, "form": "met-inside",
                             "user": unit.rel, "need": need, "provider": e.unit.rel, "capability": e.capability,
                             "to-need": None})
        for (child, need), conn in unit.conn.items():
            for e in conn.entries:
                if e.kind == "child":
                    rows.append({"key": conn.key, "value": e.raw, "alternative": e.config, "form": "connection",
                                 "user": child.rel, "need": need, "provider": e.unit.rel,
                                 "capability": e.capability, "to-need": None})
                else:
                    rows.append({"key": conn.key, "value": e.raw, "alternative": e.config, "form": "passed-up",
                                 "user": child.rel, "need": need, "provider": None, "capability": None,
                                 "to-need": e.capability})
        return rows

    by_unit = {}
    for scenario in resolved_scenarios(project):
        by_unit.setdefault(scenario["unit"], []).append(scenario_data(project, scenario))
    units = []
    for unit in project.units:
        readme = os.path.join(unit.path, "README.md")
        units.append({
            "path": unit.rel, "name": unit.name, "parent": unit.parent.rel if unit.parent else None,
            "children": [c.rel for c in unit.children], "responsibility": unit.responsibility,
            "kind": unit.kind or None, "status": unit.status, "owner": unit.owner or None,
            "readme": rel(readme) if project.kind_of(readme) == "file" else None,
            "secret": secret_data(project, unit),
            "not": [{"text": text, "need": need} for text, need in unit.nots],
            "capabilities": [entry(unit, n, s, "capabilities") for n, s in unit.capabilities.items()],
            "needs": [entry(unit, n, s, "needs") for n, s in unit.needs.items()],
            "wiring": wiring_rows(unit),
            "scenarios": by_unit.get(unit, []),
            "decisions": [{"path": rel(d["path"]), "title": d["title"], "status": d["status"], "date": d["date"],
                           "derived-from": d["derived-from"], "answer": d["answer"]}
                          for d in decisions_of(project, unit)],
            "documents": {kind: [rel(p) for _, p in items] for kind, items in documents_of(project, unit).items()},
            "x": {k: v for k, v in unit.manifest.items() if isinstance(k, str) and k.startswith("x-")}})
    root = project.root_unit
    root_needs = [{"name": need, "platform": spec["platform"],
                   "reached-by": sorted({u.rel for u, _ in final_users(root, need) if u is not root})}
                  for need, spec in root.needs.items() if need not in root.inner]
    return {"unifold-model": MODEL_VERSION, "tool": TOOL_VERSION, "project": root.name, "root": project.root,
            "units": units, "root-needs": root_needs}


def unit_for(project: Project, path: str) -> Unit:
    """The unit that contains `path` (a folder or a file, which need not exist)."""
    target = real(path)
    kind, owner = project.owner_of(target)
    if kind == "foreign":
        raise Fail("nested-project", f"{path} lies in the nested project "
                                     f"{project.rel(owner)}; run the command there")
    return owner if kind == "unit" else project.root_unit


def skills_list(project: Project) -> list:
    return [{"name": s["name"], "unit": u.rel, "path": project.rel(s["path"]),
             "description": s["description"]}
            for u in project.units for s in skills_of(project, u) if s["exists"]]


# ----- command line

COMMANDS = {
    "init": "start a project in DIR (default: here): the root manifest and README.md if there "
            "are none, and the generated files; with --agents also install the skills and the "
            "skill stubs",
    "check": "check manifests, wiring, contracts, documents and generated files",
    "generate": "write diagrams, decision indexes, the AGENTS.md of every unit and, "
                "where they exist, skill stubs",
    "show": "describe the unit that contains PATH, with its resolved neighbours",
    "capability": "print both ends of every connection of one capability or need",
    "impact": "list everything that depends on a unit or capability, and who cites its files",
    "tree": "print the unit tree with status, capabilities and needs",
    "model": "print the resolved project as JSON with a stable schema: units, connections, final "
             "providers, scenarios, decisions",
    "stamp": "write or refresh the stamps of the context items at or below PATH, and print "
             "each one with the source it cites",
    "cited-by": "list the context items and links that cite FILE",
    "skills": "list every skill; `skills sync` writes stubs into .agents/skills and .claude/skills",
    "site": "write the HTML explorer",
    "rules": "print the rules that `check` applies, or one rule",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unifold", description=__doc__.split("\n\n")[0] + "\n\n" + __doc__.split("\n\n")[1],
        epilog="Exit codes: 0 ok; 1 findings; 2 cannot run (usage, no project, unusable "
               f"root); 3 internal error. Documentation: {SITE_URL}",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"unifold {TOOL_VERSION}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    def command(name, path=True, as_json=True):
        cmd = sub.add_parser(name, help=COMMANDS[name], description=COMMANDS[name])
        if path:
            cmd.add_argument("path", nargs="?", default=".",
                             help="a folder inside the project (default: the current folder)")
        if as_json:
            cmd.add_argument("--json", action="store_true", help="print JSON")
        return cmd

    cmd = command("init", path=False)
    cmd.add_argument("target", nargs="?", default=".", metavar="DIR")
    cmd.add_argument("--agents", action="store_true",
                     help="install the skills `unifold` and `unifold-convert` and the skill stubs")
    cmd = command("check")
    cmd.add_argument("--fix", action="store_true",
                     help="first write the generated files (what `generate` writes); "
                          "stamps are written only by `unifold stamp`")
    cmd.add_argument("--strict", action="store_true", help="exit with 1 on warnings too")
    cmd.add_argument("--quiet", "-q", action="store_true",
                     help="hide info findings and fix hints")
    cmd.add_argument("--format", choices=("text", "json", "github"), default="text",
                     help="github: workflow annotations")
    cmd.add_argument("--rule", action="append", metavar="ID",
                     help="report only this rule (repeatable)")
    cmd.add_argument("--ignore", action="append", metavar="ID",
                     help="drop the findings of this rule from the output and the exit code (repeatable)")
    command("generate")
    command("model")
    command("show")
    cmd = command("capability", path=False)
    cmd.add_argument("path", help="folder of the unit")
    cmd.add_argument("name", help="name of a capability or need of the unit")
    cmd = command("impact", path=False)
    cmd.add_argument("path", help="folder of the unit, or a file in it")
    cmd.add_argument("capability", nargs="?", help="limit to one capability")
    cmd = command("tree")
    cmd.add_argument("--depth", type=int, help="levels below the root to print")
    command("stamp")
    cmd = command("cited-by", path=False)
    cmd.add_argument("file", help="the cited file; it need not exist any more")
    cmd = command("skills", path=False)
    cmd.add_argument("args", nargs="*", metavar="[sync] [PATH]")
    cmd = command("site")
    cmd.add_argument("-o", "--output", help="file to write (default: unifold.html in the root)")
    cmd.add_argument("--mermaid", default=MERMAID_URL, metavar="URL|FILE",
                     help="where the page gets Mermaid: a URL (default: a CDN), or a local "
                          "mermaid.min.js, which is embedded so that the page works offline")
    cmd = command("rules", path=False)
    cmd.add_argument("id", nargs="?", help="a rule id, for example W2")
    return parser


def emit(args, data, text):
    """Print `data` as JSON if asked for, else call `text()`."""
    if getattr(args, "json", False):
        print(json.dumps(data, indent=1, ensure_ascii=False))
    else:
        text()


def run(args) -> int:
    name = args.command
    if name == "rules":
        rows = [{"id": rule, "severity": spec[0], "what": spec[1],
                 "fix": spec[2], "url": f"{SITE_URL}/rules#{rule.lower()}"}
                for rule, spec in RULES.items()]
        if args.id:
            rows = [r for r in rows if r["id"] == args.id.upper()]
            if not rows:
                raise Fail("unknown-rule", f"no rule '{args.id}'; rules: {', '.join(RULES)}")

        def text():
            for row in rows:
                if args.id:
                    print(f"{row['id']} ({row['severity']})\n{row['what']}\n"
                          f"Fix: {row['fix']}\n{row['url']}")
                else:
                    print(f"{row['id']:<4}{row['severity']:<6} {row['what']}")
        emit(args, rows, text)
        return 0
    if name == "init":
        result = init_project(args.target, args.agents, interactive=not args.json)

        def text():
            wrote = MANIFEST in result["written"]
            readme = "README.md" in result["written"]
            print(f"{result['root']}: {result['units']} unit(s); root manifest "
                  f"{'written' if wrote else 'kept'}; "
                  f"{'README.md written from the template; ' if readme else ''}"
                  f"{len(result['written']) - int(wrote) - int(readme)} generated file(s) written")
            for note in result["notes"]:
                print(f"note: {note}")
            print("Next: describe the parts of the repository as units, by hand or with the "
                  "skill `unifold-convert`; `unifold check` says what is missing." +
                  ("" if args.agents else " `unifold init --agents` sets up coding agents."))
        emit(args, {"ok": True, **result}, text)
        return 0
    if name == "check":
        if args.format == "json":
            args.json = True
        result = run_check(args.path, args.fix, args.strict,
                           {r.upper() for r in args.rule} if args.rule else None,
                           {r.upper() for r in args.ignore} if args.ignore else None)
        if args.json:
            print(json.dumps(result, indent=1, ensure_ascii=False))
        elif args.format == "github":
            print_github(result)
        else:
            print_check(result, args.quiet)
        return 0 if result["ok"] else 1
    if name == "skills":
        words = list(args.args)
        sync = bool(words) and words[0] == "sync"
        words = words[1:] if sync else words
        if len(words) > 1:
            raise Fail("usage", "usage: unifold skills [sync] [PATH]")
        project = open_project(words[0] if words else ".")
        if sync:
            result = write_generated(project, force=("stubs",))
            stubs = [p for p in result["written"] if p.startswith(STUB_DIRS)]
            emit(args, {"ok": True, **result},
                 lambda: print(f"{len(stubs)} skill stub(s) written, {len(result['removed'])} "
                               f"file(s) removed, in {' and '.join(STUB_DIRS)}"))
            return 0
        rows = skills_list(project)

        def text():
            for row in rows:
                print(f"{row['name']}  [{row['unit']}]  {row['path']}\n    {row['description']}")
        emit(args, rows, text)
        return 0
    if name == "cited-by":
        project = open_project(args.file)
        target = real(args.file)
        rows = citations(project, lambda path: path == target)
        emit(args, rows, lambda: print_citations(rows) if rows else
             print(f"nothing cites {project.rel(target)}"))
        return 0
    if not os.path.exists(args.path):
        raise Fail("no-such-path", f"{args.path} does not exist")
    project = open_project(args.path)
    if name == "generate":
        result = write_generated(project)

        def text():
            print(f"{len(result['written'])} generated file(s) written, "
                  f"{len(result['removed'])} removed, for {len(project.units)} unit(s)")
            for path in result["refused"]:
                print(f"not overwritten: {path} has no generated marker; move it elsewhere",
                      file=sys.stderr)
        emit(args, {"ok": not result["refused"], **result}, text)
        return 1 if result["refused"] else 0
    if name == "stamp":
        target = real(args.path)
        rows = stamp_all(project, None if target == project.root else
                         unit_for(project, args.path).path)

        def text():
            for row in rows:
                print(f"{row['action']} {row['file']}:{row['line']}: '{row['title']}' "
                      f"cites {row['cites']}")
            print(f"{len(rows)} stamp(s) written" + (
                "; a stamp says that somebody compared `Says` with the cited source"
                if rows else ""))
        emit(args, {"ok": True, "stamped": len(rows), "items": rows}, text)
        return 0
    if name == "tree":
        emit(args, tree_data(project, args.depth), lambda: print_tree(project, args.depth))
        return 0
    if name == "model":
        print(json.dumps(build_model(project), indent=1, ensure_ascii=False))
        return 0
    if name == "site":
        out = build_site(project, os.path.abspath(args.output) if args.output
                         else os.path.join(project.root, "unifold.html"), args.mermaid)
        emit(args, {"ok": True, "written": out}, lambda: print(f"wrote {out}"))
        return 0
    unit = unit_for(project, args.path)
    if name == "show":
        info = describe(project, unit)
        emit(args, info, lambda: print_show(info))
    elif name == "capability":
        data = capability_data(project, unit, args.name)
        emit(args, data, lambda: print_capability(data))
    elif name == "impact":
        target = real(args.path)
        data = impact(project, unit, args.capability, target if os.path.isfile(target) else None)
        emit(args, data, lambda: print_impact(data))
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if "--json" in argv[1:]:                          # a flag may stand anywhere
        argv = [argv[0], "--json"] + [a for a in argv[1:] if a != "--json"]
    wants_json = "--json" in argv or "--format=json" in argv or \
        any(a == "--format" and argv[i + 1:i + 2] == ["json"] for i, a in enumerate(argv))

    def fail(code: str, message: str, status: int) -> int:
        if wants_json:
            data = {"ok": False, "error": {"code": code, "message": message}}
            if "check" in argv[:1]:
                data.update({"summary": {"units": 0, "error": 0, "warn": 0, "info": 0},
                             "findings": []})
            print(json.dumps(data, indent=1, ensure_ascii=False))
        print(f"unifold: {message}", file=sys.stderr)
        return status

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code and wants_json:
            data = {"ok": False, "error": {"code": "usage", "message": "invalid command line"}}
            if "check" in argv[:1]:
                data.update({"summary": {"units": 0, "error": 0, "warn": 0, "info": 0},
                             "findings": []})
            print(json.dumps(data))
        return exc.code if isinstance(exc.code, int) else 2
    try:
        return run(args)
    except Fail as exc:
        return fail(exc.code, exc.message, 2)
    except BrokenPipeError:
        raise
    except KeyboardInterrupt:
        return 130
    except OSError as exc:
        if os.environ.get("UNIFOLD_DEBUG"):
            raise
        where = f" ({exc.filename})" if exc.filename else ""
        return fail("io", f"{exc.strerror or exc}{where}", 2)
    except Exception as exc:                          # a bug: say so, and do not look like "findings"
        if os.environ.get("UNIFOLD_DEBUG"):
            raise
        return fail("internal", f"internal error ({type(exc).__name__}: {exc}). This is a bug "
                                "in unifold; set UNIFOLD_DEBUG=1 for the traceback.", 3)


def cli():
    """Entry point of the installed command."""
    for stream in (sys.stdout, sys.stderr):           # a console that cannot show a character
        try:
            stream.reconfigure(errors="backslashreplace")
        except (AttributeError, ValueError):
            pass
    try:
        code = main()
        sys.stdout.flush()
    except BrokenPipeError:                           # the reader of a pipe stopped
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        code = 0
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stderr.fileno())
    sys.exit(code)


if __name__ == "__main__":
    cli()
