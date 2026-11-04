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
  check [PATH] [--fix]        report findings; --fix first writes every generated file
  show [PATH]                 one unit with its resolved neighbours
  capability PATH NAME        both ends of every connection of one entry
  impact PATH [CAPABILITY]    everything that depends on a unit or capability, or cites a file
  brief [PATH]                what to implement in a unit: its contracts, examples, fakes and scenarios
  scenario PATH NAME          one scenario as a sequence diagram with its steps, as Markdown
  states PATH CONTRACT        the states of a contract as a state diagram with its table, as Markdown
  trace [PATH]                which examples of a unit's contracts a test names, and which none does
  tree [PATH]                 the unit tree
  model [PATH]                the resolved project as JSON
  skills [PATH]               list the skills of the project
  explore [PATH]              write the explorer and open it in a browser
  rules [ID]                  the rules that `check` applies

Documentation: https://unifold.md
"""
from __future__ import annotations

import argparse
import difflib
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import webbrowser
from urllib.parse import quote, unquote

try:
    import yaml
except ImportError:                                   # pragma: no cover
    sys.stderr.write("unifold needs the PyYAML package. Run it with `uvx unifold` or "
                     "`uv run unifold.py`, or install PyYAML (python3 -m pip install pyyaml).\n")
    sys.exit(2)

TOOL_VERSION = "0.4.0"
SPEC_VERSIONS = ("0.4",)
MODEL_VERSION = "0.4"
SITE_URL = "https://unifold.md"
MANIFEST = "unifold.yaml"
MAX_WORDS = 1500               # words of a hand-written document, outside its front matter
MAX_WHY_WORDS = 250            # words under `## Why` of a README.md
LIST_LIMIT = 12                # more files of one kind than this are counted, not linked, in AGENTS.md
MAX_DEPTH = 3
SHARED_FROM = 3                # so many children passing one need up are listed, not drawn
INDEX_LIMIT = 40
MARK_PREFIX = "<!-- unifold:generated"
MARK = MARK_PREFIX + " - do not edit; run `unifold check --fix` -->"
STUB_MARK = MARK_PREFIX + " - do not edit; run `unifold check --fix` -->"
BLOCK_BEGIN = "<!-- unifold:begin - generated block; run `unifold check --fix` to refresh -->"
BLOCK_BEGIN_PREFIX = "<!-- unifold:begin"
BLOCK_END = "<!-- unifold:end -->"
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

<Why this unit exists and why it is cut this way: what it hides because it is hard to get right or likely to change, what it leaves to others and why, the forces that shaped it, the main trade-off, what must stay true. Write the reasons a newcomer cannot guess, in whole sentences. Where a decision gives a reason, state the reason and link the decision. At most 250 words; the long form is docs/explanation/reasoning.md. No list of children, capabilities or connections: the manifest holds them and `unifold show` prints them. No list of decisions either: the decisions are their own record.>
"""   # the same text as the skill asset assets/README.template.md
ROOT_KEYS = ("unifold", "name", "ignore", "diagrams")
UNIT_KEYS = ("responsibility", "kind", "runs-as", "status", "not", "capabilities", "needs", "wiring",
             "scenarios")
CAPABILITY_KEYS = ("summary", "contract")
NEED_KEYS = ("summary", "contract", "optional", "platform")
SCENARIO_KEYS = ("summary", "source", "given", "hops", "expect")
STATUSES = ("planned", "active", "deprecated")
WELL_KNOWN_KINDS = ("logic", "stateful", "adapter")
PART_KINDS = ("command", "query", "event", "callback", "type")
CALL_KINDS = ("command", "query")                 # the consumer calls the provider
NBSP = "\u00a0"
STEP_WIDTH = 34                                     # the characters of one line of a step in a sequence diagram; a wider one shrinks the picture
RAISE_KINDS = ("event", "callback")               # the provider calls the consumer
SCENARIO_REF = re.compile(r"^\s*(?:([A-Za-z0-9][\w./-]*)\s*->\s*)?([A-Za-z0-9][\w./-]*)\.([A-Za-z0-9][\w-]*)\s*$")
DIAGRAM_MODES = ("parents", "none")
DECISION_STATUS = re.compile(r"^(proposed|accepted|rejected|deprecated|derived|superseded by (\d{4}))$")
HOP = re.compile(r"^\s*(\S.*?)\s*->\s*(\S.*?)\s*$")
CONSTANT_PATTERN = r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b"
FIELD_LINE = re.compile(r"^(Kind|Pre|Result|Errors|Examples|When|Delivery):\s*(.*?)\s*$")
HEADER_LINE = re.compile(r"^(Notation|Sources|Binding|Carried by|Version):\s*(.*?)\s*$")
RUNS_AS = ("library", "process", "job", "ui", "firmware")
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
    "S1": ("error", "The root manifest states `unifold: \"0.4\"`, as a string.",
           "Write `unifold: \"0.4\"` in the root `unifold.yaml`. A 0.3 project is rewritten by hand: every hop gets a result, `caller -> target.part(input): result`. A 0.2 project also needs `responsibility` instead of `summary` on a unit, and no `verified-by`."),
    "S3": ("error", "Every unit has a `README.md`.",
           "Write the file (the template is in the `unifold` skill)."),
    "S7": ("warn", "Every folder in `docs/skills/` has a `SKILL.md` whose front matter has `name`, equal to the folder name, and `description`.",
           "Correct the front matter."),
    "S9": ("error", "A decision file is named `NNNN-short-title.md` with a number that is unique in the unit; its front matter has an ISO `date` and a `status` that is proposed, accepted, rejected, deprecated, superseded by NNNN, or derived; `accepted` names `decision-makers`; `superseded by NNNN` names an existing decision; `derived` has `derived-from` and a section `## Source says`.",
           "Correct the file name or the front matter; give a derived decision the passage it rests on."),
    "S12": ("info", "Every entry directly in `docs/` is one of `tutorials`, `skills`, `references`, `explanation`, `decisions`, `diagrams`.",
           "Move the file or folder into the folder of its kind: tutorials (learn), skills (do), references (look up), explanation (understand)."),
    "M1": ("error", "A manifest is a YAML mapping without duplicate keys.",
           "Correct the YAML. The unit and its wiring are not checked until it parses."),
    "M2": ("error", "A manifest has a one-line `responsibility` and otherwise only the keys, types and values of the standard; root-only keys are in the root; `runs-as` is one of `library`, `process`, `job`, `ui` and `firmware`; `platform` stands on a need of the root only; `contract` is a path or a mapping with `path` and `parts`; names of capabilities, needs and scenarios use letters, digits, `-` and `_` and start with a letter or digit; `contract` names a file, not a fragment; a folder under `ignore` exists; no text of the manifest is a placeholder (`<...>`).",
           "Correct the key or value named in the message. A unit has `responsibility`, not `summary`. Project-specific keys start with `x-`: write `owner`, and `kind` on a capability or need, as `x-owner` and `x-kind`. `max-lines` and `diagram-links` do not exist; delete them."),
    "M7": ("error", "`contract` is a path, relative to the manifest, to a Markdown file that exists in `docs/references/` of this unit or of an ancestor.",
           "Write the contract as `docs/references/<topic>.md` of the unit that wires the connection, and name it from both sides. A schema file is not a contract, and a definition from outside the project is linked from the reference by its URL. Otherwise correct the path, create the file, or remove the key until there is something to point at."),
    "M10": ("warn", "No responsibility or summary starts with `TODO`.",
           "Replace `TODO` with one line that says what the unit, capability or need is."),
    "M11": ("error", "Every name under `parts` is a part of the named contract: a `###` heading under `## Parts`, or a file in the contract folder.",
           "Correct the name, or add the part to the contract."),
    "W1": ("error", "Every wiring line has an allowed form and names an existing direct child, capability or need, on the correct side. A bare key names a capability or a need of the unit, not both. A need of a child is passed up only to a need that the unit does not meet inside, and a need that a child meets inside is not wired again. A connection joins two units; a folder is never a provider.",
           "Correct the reference. `unifold show` lists the names; where two children share a folder name, write the path (`a/utils.matcher`). Code that is not a unit gets a folder with a `unifold.yaml`."),
    "W2": ("error", "Every need of every child is connected by a line in the parent's wiring, unless it is `optional` or the child meets it inside.",
           "Add `child.need: provider` to the parent's wiring, for a capability of a sibling, or declare a need in the parent and pass the need up (`child.need: need`). Do not mark a need optional to silence this."),
    "W3": ("warn", "Every capability of a child is used: a wiring line names it as the provider of a need of a sibling or of the parent itself, or a capability of the parent is implemented by it.",
           "Wire the unit that should use it; where code of the parent itself uses it, declare a need in the parent and wire it (`need: child.capability`); or implement a capability of the parent with it (`capability: child.capability`); or remove the capability."),
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
    "K4": ("warn", "A need of the root without `platform: true` is finally reached only by `adapter` units. Silent for a unit whose `kind` is not `logic` or `stateful`.",
           "Put an adapter between the unit named and the external system, or mark a host service `platform: true`."),
    "K6": ("error", "`not` is a list of one-line texts.",
           "Write each item as one line of text."),
    "N1": ("error", "Every hop resolves to one connection in the direction of the call: a command or query from the consumer to the provider, an event or callback from the provider to the consumer. Its part is a command, query, event or callback of that connection's contract, and no name is ambiguous: a name that is both a descendant and a capability or need of the holding unit, or two connections between the same units whose contracts both have the part, unless the hop names the capability (`target.capability.part`).",
           "Wire the connection the hop needs, add the part to the contract, or write `target.capability.part`."),
    "N2": ("error", "A scenario has `summary`, `hops` and `expect`; its name follows the rule for names. A hop is `caller -> target.part: result`, with an optional input in parentheses after the part, and a result that is text; a command or query has a result. An item of `hops` is also `parallel`, a list of two or more lists of hops, `repeat`, a mapping with `hops` and `until` or `times`, or `child.scenario`, a scenario of a unit below. `given` is a list whose items are a sentence or `connection: state`.",
           "Complete the scenario. Give every hop its result, for example `- host -> session.open(): ok`. Quote a result that YAML reads as something other than text, such as `\"1000\"`, `\"yes\"` or `\"null\"`."),
    "N3": ("warn", "Every wiring line of a unit is used by a hop of a scenario: one that passes through the unit, or one of a child at the capability or need the line connects. Silent where no scenario passes through the unit.",
           "Write the scenario that needs the line, or remove the connection."),
    "N4": ("info", "Every command, query and event of a contract is used by a hop of a scenario. Silent where the project has no scenario, or a hop does not resolve.",
           "Write the scenario that uses the part, or remove the part from the contract."),
    "N5": ("error", "An item `connection: state` under `given` names a connection the way a hop names its target, `unit.capability` or a need of the holding unit, whose contract has `## States`, and a state of that table.",
           "Correct the name or the state, or write the condition as a sentence."),
    "N6": ("error", "Every hop over a connection whose contract has `## States` is allowed in the current state of that connection, with its result. A connection starts in the state that `given` names, or else in the start state of its contract. The hops of a `repeat` are followed twice.",
           "Correct the hop or its result, set the state the path starts from under `given`, or add the row that allows the step to the `## States` table of the contract."),
    "N7": ("error", "A hop agrees with the examples of its part: a result `= <case>` names an example of the part, and a hop whose input is the `Input` of an example has that example's `Expected` as its result.",
           "Correct the hop, or correct the example in the contract; the examples are the tests."),
    "N8": ("warn", "A result that is not `ok` and not a literal of the contract is spelled exactly like an error case of the part: a result that differs from an error case only in case, or in `-` and `_`, is reported.",
           "Spell the error case as `Errors:` names it; a result that is not an error case counts as a success and moves the state."),
    "C1": ("warn", "A contract has `## Parts` with at least one part, each with `Kind:` command, query, event, callback or type.",
           "Write the parts as [contracts.md](contracts.md#parts) says."),
    "C2": ("warn", "A command, query or callback has `Pre:`, `Result:`, `Errors:` and an `Examples:` table with the columns `Case | Input | Expected`, or `Case | Given | Input | Expected`, at least one row, and a case name that is unique within the part.",
           "Complete the part; the examples are the first tests. Name each case once: its slug is the id of the example."),
    "C3": ("warn", "Every part has a fenced code block, its signature.",
           "Write the signature in the notation the header names."),
    "C4": ("warn", "A type is defined once within the subtree of the unit that holds the contract.",
           "Keep one definition and link to it from the other contract."),
    "C5": ("warn", "A contract has `## Fake`.",
           "Say what stands in for the contract in the tests of its consumers."),
    "C6": ("warn", "A contract has `## Use`.",
           "Say how a consumer uses the connection: in which order it calls the parts, what it does when a call fails, and the rules that hold for every part."),
    "C7": ("error", "A `## States` section has a line `Start: <state>` and a table `State | Part | Result | Next`. Every part is a command, query or event of the contract, every result is empty, `ok` or an error case of the part, every next state is a state of the table, the start state is one of them, and no two rows match the same step.",
           "Correct the table. A deadline is an event part that the provider raises when the time is up, or the error of the next call."),
    "C8": ("warn", "A `## Qualities` section of a contract is a table with the columns `Aspect | Guarantee`.",
           "Write the qualities as rows: latency, throughput, concurrency, ordering, delivery, idempotency, timeout, availability, limits, security, or others."),
    "C9": ("warn", "An event has `When:` and `Delivery:`; its `Examples:` table, where it has one, has the columns `Case | Action | Emitted` or `Case | Given | Action | Emitted`.",
           "Say what raises the event and how it is delivered (at-most-once, at-least-once or exactly-once, and the order key)."),
    "C10": ("warn", "A type is used: the signature of a command, query, event or callback names it, directly or through another type; a manifest lists it under `parts`; or a contract links to it. Silent for a contract that has only types.",
            "Name the type in the signature of the part that uses it, or remove it. Properties of a device or a service belong in `## Qualities`."),
    "L1": ("error", "The target of every relative link in a hand-written document exists, including its anchor: a heading, or the first cell of a table row.",
           "Correct the link."),
    "L2": ("error", "A relative link stays inside the project, and no link is an absolute path.",
           "Write the link relative to this file; cite things outside the project by full URL."),
    "L11": ("warn", "No link goes sideways: its target lies in the unit, in a unit above it or in a unit below it.",
           "Remove the link, and declare a need for what the unit wants from the sibling."),
    "T1": ("warn", "A hand-written document has at most 1,500 words outside its front matter. A word is a string between spaces that contains a letter or a digit.",
           "Split the file: a reference into parts, the long why into `docs/explanation/reasoning.md`, a procedure into a skill."),
    "T4": ("warn", "The `## Why` section of `README.md` has at most 250 words.",
           "Move the long form to `docs/explanation/reasoning.md`."),
    "T9": ("warn", "`README.md` starts with a `#` title and one paragraph, has a `## Why` section, and holds no placeholder in angle brackets (`<...>`).",
           "Write the title, the first paragraph and `## Why`; replace every `<...>` of the template with text."),
    "G1": ("error", "Every generated file exists, is not ignored by git, and equals what the generator writes now, the scenario diagrams included; no leftover generated file remains; `docs/diagrams/` holds only generated files and the root `AGENTS.md` is generated.",
           "Run `unifold check --fix`. A hand-written `AGENTS.md` at the root is not overwritten: move its content to `README.md` and `docs/`, delete it, then run the command."),
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
        row `| **unit** | ... |` is `#unit`. The first row with a slug wins.
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
        self.runs_as = _text(manifest.get("runs-as"))
        self.nots: list = [" ".join(item.split()) for item in (manifest.get("not") if isinstance(manifest.get("not"), list) else [])
                           if isinstance(item, str)]
        self.scenarios: dict = {}               # name -> {summary, source, expect, given: [raw], hops: [raw], x: {}}
        raw = manifest.get("scenarios")
        if isinstance(raw, dict):
            for name, spec in raw.items():
                spec = spec if isinstance(spec, dict) else {}
                hops, given = spec.get("hops"), spec.get("given")
                self.scenarios[str(name)] = {
                    "summary": " ".join(_text(spec.get("summary")).split()),
                    "source": " ".join(_text(spec.get("source")).split()),
                    "expect": " ".join(_text(spec.get("expect")).split()),
                    "given": given if isinstance(given, list) else [],
                    "hops": [h for h in hops if isinstance(h, (str, dict))] if isinstance(hops, list) else [],
                    "x": {k: v for k, v in spec.items() if isinstance(k, str) and k.startswith("x-")}}
        status = manifest.get("status")
        self.status = status if status in STATUSES else "active"
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
                inherit = value is None or value == {}          # an empty entry takes summary and contract from its one connection
                contract, parts = spec.get("contract"), None
                if isinstance(contract, dict):
                    raw_parts = contract.get("parts")
                    parts = [str(x) for x in raw_parts] if isinstance(raw_parts, list) else None
                    contract = contract.get("path")
                out[str(name)] = {
                    "summary": " ".join(_text(spec.get("summary")).split()),
                    "contract": _text(contract) or None,
                    "parts": parts, "inherit": inherit, "inherited-from": None,
                    "optional": spec.get("optional") is True,
                    "platform": spec.get("platform") is True,
                    "x": {k: v for k, v in spec.items() if isinstance(k, str) and k.startswith("x-")}}
        return out

    @property
    def is_root(self) -> bool:
        return self.parent is None

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
        self.diagrams = "parents"
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
        if data.get("diagrams") in DIAGRAM_MODES:
            self.diagrams = data["diagrams"]
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
        self._inherit()

    def _inherit(self):
        """An empty entry takes its summary and contract from the one entry its wiring joins it to:
        a child's need from its provider, a unit's capability from the child that implements it, a
        unit's own need from the child that meets it. Chains are followed until nothing changes."""
        def source(unit, side, name):
            if side == "needs":
                conn = unit.inner.get(name)
                if conn is None and unit.parent is not None:
                    conn = unit.parent.conn.get((unit, name))
                    if conn is not None and len(conn.entries) == 1 and conn.entries[0].kind == "own":
                        return unit.parent, "needs", conn.entries[0].capability
            else:
                conn = unit.impl.get(name)
            if conn is None or len(conn.entries) != 1 or conn.entries[0].kind != "child":
                return None
            return conn.entries[0].unit, "capabilities", conn.entries[0].capability

        for _ in range(len(self.units) + 1):
            changed = False
            for unit in self.units:
                for side in ("capabilities", "needs"):
                    for name, spec in getattr(unit, side).items():
                        if not spec["inherit"] or spec["summary"]:
                            continue
                        found = source(unit, side, name)
                        if found is None:
                            continue
                        other, other_side, other_name = found
                        other_spec = getattr(other, other_side).get(other_name)
                        if not other_spec or not other_spec["summary"]:
                            continue
                        spec["summary"], spec["inherited-from"] = other_spec["summary"], f"{other.rel}.{other_name}"
                        if other_spec["contract"] and not SCHEME.match(other_spec["contract"]):
                            target = os.path.normpath(os.path.join(other.path, other_spec["contract"].split("#")[0]))
                            spec["contract"] = os.path.relpath(target, unit.path).replace(os.sep, "/")
                        changed = True
            if not changed:
                break

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
        elif key == "owner":
            bad("key 'owner' is not part of the standard; nothing reads it", key,
                fix="Rename the key to `x-owner` to keep it for the project, or delete the line.")
        elif key == "secret":
            bad("key 'secret' is not part of the standard", key,
                fix="Delete the key. Say what the unit hides in the first sentence of `## Why` of its README.md, and link the decision there.")
        elif key in ("max-lines", "diagram-links"):
            bad(f"key '{key}' is not part of the standard"
                + ("; the word limit is 1,500 in every project" if key == "max-lines" else "; boxes in diagrams do not link"),
                key, fix="Delete the line.")
        else:
            close = difflib.get_close_matches(key.lower(), ROOT_KEYS + UNIT_KEYS, 1)
            hint = f"; did you mean '{close[0]}'?" if close else ""
            bad(f"unknown key '{key}'{hint}", key)
    summary_of(manifest.get("responsibility"), "the unit", "responsibility", field="responsibility")
    for key in ("kind", "name"):
        if key in manifest and not _text(manifest[key]):
            bad(f"'{key}' must be text, not {show_value(manifest[key])}", key)
    if unit.kind and unit.kind not in WELL_KNOWN_KINDS:
        project.add("K1", where, f"kind '{unit.kind}' is not one of {', '.join(WELL_KNOWN_KINDS)}; "
                                 "no rule applies to it", lines.get(("kind",)))
    check_unit_fields(project, unit)
    for key, allowed in (("status", STATUSES), ("diagrams", DIAGRAM_MODES), ("runs-as", RUNS_AS)):
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
        elif ignore:
            for item in ignore:
                if SCHEME.match(item) or os.path.isabs(item) or item.strip().startswith(".."):
                    bad(f"'ignore' names a folder relative to the root, not '{item}'", "ignore")
                elif not os.path.isdir(os.path.join(project.root, item.strip())):
                    bad(f"'ignore' names a folder that does not exist: '{item}'", "ignore",
                        fix="Delete the entry, or correct the path.")
    for key in ("kind",):
        if isinstance(manifest.get(key), str) and PLACEHOLDER.match(manifest[key].strip()):
            bad(f"'{key}' is a placeholder ({manifest[key].strip()}); write a value or delete the line", key)
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
            if spec is None or spec == {}:
                entry = getattr(unit, section).get(str(name), {})
                if not entry.get("summary"):
                    bad(f"{label} is empty and nothing is wired to it to take a summary and a contract from; "
                        "write its summary, or wire it to exactly one entry", section, str(name))
                continue
            if not isinstance(spec, dict):
                bad(f"{label} must be a summary text, a mapping with 'summary', or empty, not "
                    f"{show_value(spec)}", section, name)
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
                elif key == "kind":
                    bad(f"{label}: 'kind' is a key of a unit, not of a {what}; the contract says what the "
                        "connection carries", section, name, key,
                        fix="Rename the key to `x-kind` to keep it for the project, or delete the line.")
                else:
                    close = difflib.get_close_matches(str(key).lower(), allowed, 1)
                    hint = f"; did you mean '{close[0]}'?" if close else ""
                    bad(f"{label}: unknown key '{key}'{hint}", section, name, str(key))
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
    if "#" in value:
        project.add("M2", where, f"{label}: 'contract' names a file, not a fragment: {value.strip()}", line,
                    fix="Delete the `#...` part; `parts` says which parts this side uses.")
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
    """`not` (K6)."""
    where, lines, manifest = unit.manifest_path, unit.lines, unit.manifest
    if "not" in manifest:
        items, line = manifest["not"], lines.get(("not",))
        if not isinstance(items, list):
            project.add("K6", where, f"`not` is a list, not {show_value(items)}", line)
        else:
            for item in items:
                if not isinstance(item, str) or not item.strip() or "\n" in item.strip():
                    project.add("K6", where, "an item of `not` is one line of text, not "
                                             f"{show_value(item)}", line)
                elif PLACEHOLDER.match(item.strip()):
                    project.add("M2", where, f"an item of `not` is a placeholder ({item.strip()})", line)


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
                    contracts_agree(f"{ref}.{need}", child, spec, f"need '{ref}.{need}'",
                                    entry.unit, other_spec, f"capability '{entry.raw}'", conn.line)
                else:
                    other_spec = unit.needs[entry.capability]
                    contracts_agree(f"{ref}.{need}", child, spec, f"need '{ref}.{need}'",
                                    unit, other_spec, f"need '{entry.capability}' of this unit",
                                    conn.line)
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
        for entry in conn.entries:
            other_spec = entry.unit.capabilities.get(entry.capability, {})
            contracts_agree(capability, unit, spec, f"capability '{capability}' of this unit",
                            entry.unit, other_spec, f"capability '{entry.raw}'", conn.line)
    for need, conn in unit.inner.items():
        spec = unit.needs[need]
        for entry in conn.entries:
            other_spec = entry.unit.capabilities.get(entry.capability, {})
            contracts_agree(f"need '{need}' of this unit", unit, spec, f"need '{need}' of this unit",
                            entry.unit, other_spec, f"capability '{entry.raw}'", conn.line)
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

def word_count(lines: list) -> int:
    """The words of some lines: the strings between spaces that contain a letter or a digit."""
    return sum(1 for line in lines for token in line.split() if any(c.isalnum() for c in token))


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


def check_documents(project: Project, unit: Unit):
    """The document conventions for the files of one unit."""
    if unit.broken:
        return
    readme = os.path.join(unit.path, "README.md")
    docs = os.path.join(unit.path, "docs")
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
        count = word_count(doc.lines[doc.body_start:])
        if count > MAX_WORDS:
            project.add("T1", path, f"{count:,} words; the limit is {MAX_WORDS:,}")
        check_links(project, unit, path, doc)
    if project.kind_of(readme) == "file":
        doc = project.doc(readme)
        has_why = False
        for index, (number, level, text, _) in enumerate(doc.headings):
            if level == 2 and text.strip().lower() == "why":
                has_why = True
                end = next((n for n, lvl, _, _ in doc.headings[index + 1:] if lvl <= 2),
                           len(doc.lines) + 1)
                why = word_count(doc.lines[number:end - 1])
                if why > MAX_WHY_WORDS:
                    project.add("T4", readme, f"'## Why' has {why} words; at most {MAX_WHY_WORDS}", number)
                break
        title = next((h for h in doc.headings if h[1] == 1), None)
        first = next((n for n, line in doc.prose if line.strip() and not line.lstrip().startswith("<!--")), None)
        if title is None or title[0] != first:
            project.add("T9", readme, "README.md starts with a `#` title", 1)
        else:
            following = next((h[0] for h in doc.headings if h[0] > title[0]), len(doc.lines) + 1)
            if not any(title[0] < n < following and line.strip() for n, line in doc.prose):
                project.add("T9", readme, "one paragraph follows the title: what the unit is for, and for whom", title[0])
        if not has_why:
            project.add("T9", readme, "README.md has no `## Why` section", 1)
        placeholder = next(((n, line) for n, line in doc.prose
                            if PLACEHOLDER.match(line.strip()) and not line.lstrip().startswith("<!--")), None)
        if placeholder:
            project.add("T9", readme, f"a placeholder of the template is still there: {placeholder[1].strip()[:60]}",
                        placeholder[0])


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


def check_links(project: Project, unit: Unit, path: str, doc: Doc):
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
            project.add("L2", path, f"link leaves the project, into the nested project '{project.rel(owner)}': {link}",
                        line, "Cite a nested project by full URL, or declare a need for what it provides.")
        elif owner_kind == "unit" and owner is not unit and owner.depth_below(unit) is None \
                and unit.depth_below(owner) is None:
            project.add("L11", path, f"sideways link into '{owner.rel}'; a unit does not know "
                                    f"its siblings: {link}", line)


# ----- contracts

def plain(text: str) -> str:
    """Text without code font, bold and surrounding space."""
    return re.sub(r"[`*]", "", str(text)).strip()


def split_call(text: str, keep: bool = False) -> tuple:
    """(part, input or None) of a call such as `send([01])`, `open()` or `lost`. With `keep`, the
    text keeps its code font and bold."""
    text = text.strip() if keep else plain(text)
    if text.endswith(")") and "(" in text:
        depth = 0
        for index in range(len(text) - 1, -1, -1):
            depth += {")": 1, "(": -1}.get(text[index], 0)
            if depth == 0:
                return text[:index].strip(), text[index + 1:-1].strip()
    return text, None


def first_table(lines: list, first_line: int) -> tuple:
    """The first Markdown table in `lines`: (header cells in lower case, [(line number, cells)]),
    or (None, []). `first_line` is the line number of `lines[0]`."""
    header, rows, started = None, [], False
    for offset, line in enumerate(lines):
        text = line.strip()
        if text.startswith("|"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", text.strip("|"))]
            if header is None:
                header = [plain(c).lower() for c in cells]
            elif not TABLE_RULE.match(text):
                rows.append((first_line + offset, cells))
            started = True
        elif started:
            break
    return header, rows


def level_two(doc: Doc, slug: str):
    """(line number, lines up to the next heading of level 1 or 2) of the `##` heading with this anchor, or None."""
    headings = doc.headings
    for index, (number, level, _, anchor) in enumerate(headings):
        if level == 2 and anchor == slug:
            end = next((n for n, lvl, _, _ in headings[index + 1:] if lvl <= 2), len(doc.lines) + 1)
            return number, doc.lines[number - 1:end - 1]
    return None


def outcome(result: str, errors: set):
    """The error case that a result names, or None for a result that is not an error."""
    for name in re.findall(r"`([^`]+)`", result):
        if " ".join(name.split()) in errors:
            return " ".join(name.split())
    bare = " ".join(plain(result).split())
    return bare if bare in errors else None


def row_result(text: str) -> str:
    """What the Result cell of a `## States` row matches: "any", "ok", or an error case."""
    text = plain(text)
    return "any" if not text else "ok" if text.lower() == "ok" else text


def next_state(contract: dict, current: str, part: str, result: str) -> tuple:
    """(next state, None) when the `## States` table allows the step, else (None, why not).

    A failure that the table does not name for the part in this state leaves the state as it is.
    A part that the state does not list, or a success that only error rows cover, is not allowed."""
    rows = [r for r in contract["states"]["rows"] if r["state"] == current and r["part"] == part]
    if not rows:
        return None, f"state '{current}' allows no '{part}'"
    error = outcome(result, (contract["parts"].get(part) or {}).get("errors", set()))
    for want in ((error, "any") if error else ("ok", "any")):
        hit = next((r for r in rows if row_result(r["result"]) == want), None)
        if hit:
            return hit["next"], None
    if error:
        return current, None
    return None, (f"in state '{current}', '{part}' is allowed only with "
                  + ", ".join(sorted({f"`{row_result(r['result'])}`" for r in rows})))


def contract_states(doc: Doc):
    """The `## States` section: {"line", "start", "start-line", "header", "rows": [{"line", "state",
    "part", "result", "next"}], "states": [names in order]}, or None."""
    found = level_two(doc, "states")
    if found is None:
        return None
    number, lines = found
    out = {"line": number, "start": None, "start-line": None, "rows": [], "states": []}
    for offset, line in enumerate(lines):
        match = re.match(r"^Start:\s*(.*?)\.?\s*$", line.strip())
        if match:
            out["start"], out["start-line"] = plain(match.group(1)), number + offset
            break
    header, rows = first_table(lines, number)
    out["header"] = header
    for line, cells in rows:
        cells = (cells + ["", "", "", ""])[:4]
        out["rows"].append({"line": line, "state": plain(cells[0]), "part": split_call(cells[1])[0],
                            "result": cells[2].strip(), "next": plain(cells[3])})
    for name in [out["start"]] + [r["state"] for r in out["rows"]] + [r["next"] for r in out["rows"]]:
        if name and name not in out["states"]:
            out["states"].append(name)
    return out


def contract_of_path(project: Project, path: str) -> dict:
    """A contract, parsed once: its parts and what each has.

    {"path", "folder": bool, "has-parts": bool, "has-fake": bool, "has-use": bool, "parts": {name: part},
    "states": the `## States` section or None} where a part is
    {"kind", "fence", "fields": set, "errors": set, "examples": rows, "line", "file"}. A file named
    index.md is a contract folder: its parts are the other .md files beside it.
    """
    cache = project.__dict__.setdefault("_contracts", {})
    found = cache.get(path)
    if found is not None:
        return found
    doc = project.doc(path)
    out = {"path": path, "folder": os.path.basename(path) == "index.md", "parts": {}, "header": {},
           "carrier": None, "qualities": None,
           "has-parts": any(h[1] == 2 and h[3] == "parts" for h in doc.headings),
           "has-fake": any(h[1] == 2 and h[3] == "fake" for h in doc.headings), "fake": None,
           "has-use": any(h[1] == 2 and h[3] == "use" for h in doc.headings),
           "states": contract_states(doc)}
    first_section = next((h[0] for h in doc.headings if h[1] == 2), len(doc.lines) + 1)
    for number, line in doc.prose:                    # the header: the lines before the first section
        if number >= first_section:
            break
        field = HEADER_LINE.match(line.strip())
        if field:
            out["header"][field.group(1)] = field.group(2)
    carried = out["header"].get("Carried by")
    if carried:
        link = INLINE_LINK.search("](" + carried + ")") if not carried.startswith("[") else INLINE_LINK.search(carried)
        target = (link.group(1).strip("<>") if link else carried).split("#")[0]
        out["carrier"] = os.path.normpath(os.path.join(os.path.dirname(path), target))
    qualities = level_two(doc, "qualities")
    if qualities is not None:
        header, rows = first_table(qualities[1], qualities[0])
        out["qualities"] = {"line": qualities[0], "header": header,
                            "rows": [{"aspect": plain(c[0]), "guarantee": c[1].strip() if len(c) > 1 else ""} for _, c in rows]}
    fake = next((h for h in doc.headings if h[1] == 2 and h[3] == "fake"), None)
    out["fake-text"] = ""
    if fake is not None:
        body = [line for line in (doc.section("fake") or [])[1:]]
        first = next((line.strip() for line in body if line.strip()), "")
        out["fake"] = "real" if "the real implementation" in first.lower() else "described"
        out["fake-text"] = "\n".join(body).strip()

    def part_of(name: str, lines: list, start_line: int, file: str) -> dict:
        part = {"name": name, "kind": None, "fence": False, "signature": "", "fields": set(), "texts": {},
                "errors": set(), "examples": 0, "header": None, "rows": [], "line": start_line, "file": file}
        fence, signature, table, in_examples = None, [], [], False
        for offset, line in enumerate(lines):
            match = FENCE.match(line)
            if fence:
                if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
                        and not match.group(2).strip():
                    fence = None
                    if not part["signature"]:
                        part["signature"] = "\n".join(signature)
                else:
                    signature.append(line)
                continue
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                fence, part["fence"], signature = match.group(1), True, []
                continue
            field = FIELD_LINE.match(line)
            if field:
                part["fields"].add(field.group(1))
                part["texts"][field.group(1)] = field.group(2).strip()
                if field.group(1) == "Kind":
                    part["kind"] = field.group(2).strip().lower()
                elif field.group(1) == "Errors":           # the error cases: names in code font, not constants or expressions
                    part["errors"].update(" ".join(n.split()) for n in re.findall(r"`([^`()<>=]+)`", field.group(2))
                                          if n.strip() and not re.fullmatch(CONSTANT_PATTERN, n.strip()))
                in_examples = field.group(1) == "Examples"
                continue
            text = line.strip()
            if in_examples:
                if text.startswith("|"):
                    table.append((start_line + offset, line))
                elif text:
                    in_examples = False
        if table:                                      # the first table under `Examples:`
            header, rows = first_table([l for _, l in table], table[0][0])
            part["header"], part["examples"] = header, len(rows)
            columns = {c: i for i, c in enumerate(header or [])}
            for number, cells in rows:
                get = lambda c: cells[columns[c]].strip() if c in columns and columns[c] < len(cells) else ""
                case = get("case")
                part["rows"].append({"line": number, "case": case, "given": get("given"),
                                     "input": get("input") or get("action"), "expected": get("expected") or get("emitted"),
                                     "id": example_id(path, name, case)})
        return part

    if out["folder"]:
        folder = os.path.dirname(path)
        for name in project.listdir(folder):
            file = os.path.join(folder, name)
            if name.endswith(".md") and name != "index.md" and os.path.isfile(file):
                part_doc = project.doc(file)
                out["parts"][name[:-3]] = part_of(name[:-3], part_doc.lines[part_doc.body_start:], 1, file)
    else:
        headings = doc.headings
        inside = False
        for index, (number, level, text, slug) in enumerate(headings):
            if level == 2:
                inside = slug == "parts"
            elif level == 3 and inside:
                end = next((n for n, lvl, _, _ in headings[index + 1:] if lvl <= 3), len(doc.lines) + 1)
                out["parts"][heading_slug(text)] = part_of(heading_slug(text), doc.lines[number:end - 1], number, path)
    cache[path] = out
    return out


EXAMPLE_HEADERS = (["case", "input", "expected"], ["case", "given", "input", "expected"])
EVENT_HEADERS = (["case", "action", "emitted"], ["case", "given", "action", "emitted"])


def example_id(contract_path: str, part: str, case: str) -> str:
    """The id of an example row: `<contract>#<part>/<case-slug>`; a test names it."""
    return f"{contract_topic(contract_path)}#{part}/{heading_slug(plain(case))}"


def example_row(part: dict, case: str):
    """The example row of a part whose case has this slug, or None."""
    wanted = heading_slug(plain(case))
    return next((r for r in part["rows"] if heading_slug(plain(r["case"])) == wanted), None)


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
    """C1 to C6, C8 to C10, and through check_states C7: the body of every contract that a manifest names."""
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
            if part["kind"] in ("command", "query", "callback"):
                missing = [f for f in ("Pre", "Result", "Errors") if f not in part["fields"]]
                if "Examples" not in part["fields"]:
                    missing.append("Examples")
                elif part["examples"] < 1:
                    missing.append("a row in the Examples table")
                if missing:
                    project.add("C2", where, f"part '{name}' lacks " + ", ".join(f"`{m}:`" if m[0].isupper() and " " not in m else m for m in missing), line)
                elif part["header"] not in EXAMPLE_HEADERS:
                    project.add("C2", where, f"part '{name}': the examples table has the columns `Case | Input | Expected` "
                                             f"or `Case | Given | Input | Expected`, not `{' | '.join(part['header'] or [])}`",
                                part["rows"][0]["line"] - 2 if part["rows"] else line)
                else:
                    seen = {}
                    for row in part["rows"]:
                        slug = heading_slug(plain(row["case"]))
                        if not slug:
                            project.add("C2", where, f"part '{name}': an example row names its case", row["line"])
                        elif slug in seen:
                            project.add("C2", where, f"part '{name}': the case '{row['case']}' is also the case of the row "
                                                     f"on line {seen[slug]}; name each case once", row["line"])
                        seen.setdefault(slug, row["line"])
            if part["kind"] == "event":
                missing = [f for f in ("When", "Delivery") if f not in part["fields"]]
                if missing:
                    project.add("C9", where, f"event '{name}' lacks " + ", ".join(f"`{m}:`" for m in missing), line)
                if "Examples" in part["fields"] and part["header"] not in EVENT_HEADERS:
                    project.add("C9", where, f"event '{name}': the examples table has the columns `Case | Action | Emitted` "
                                             f"or `Case | Given | Action | Emitted`, not `{' | '.join(part['header'] or [])}`",
                                part["rows"][0]["line"] - 2 if part["rows"] else line)
            if part["kind"] == "type":
                types.setdefault(name, []).append((holder, where, line))
        if not contract["has-fake"]:
            project.add("C5", path, "no `## Fake` section: say what stands in for this contract in the tests "
                                    "of its consumers")
        if not contract["has-use"]:
            project.add("C6", path, "no `## Use` section: say what a consumer does with the connection")
        qualities = contract["qualities"]
        if qualities is not None and qualities["header"] != ["aspect", "guarantee"]:
            project.add("C8", path, "`## Qualities` needs a table with the columns `Aspect | Guarantee`", qualities["line"])
        check_states(project, path, contract)
    for name, places in sorted(types.items()):
        for index, (holder, where, line) in enumerate(places):
            for other_holder, other_where, _ in places[:index]:
                if other_where == where:
                    continue
                if holder is other_holder or holder in other_holder.ancestors() or other_holder in holder.ancestors():
                    project.add("C4", where, f"type '{name}' is also defined in {project.rel(other_where)}; "
                                             "one definition in a subtree, the other contract links to it", line)
                    break
    check_unused_types(project)


def names_type(signature: str, name: str) -> bool:
    """Whether a signature names a type, in the spelling of its notation: `exit-status`, `exit_status`,
    `exit status` or `ExitStatus`. `sensor` is not named by `sensor-id`."""
    words = r"[ _-]?".join(re.escape(word) for word in re.split(r"[-_]", name))
    return re.search(r"(?<![\w-])" + words + r"(?![\w-])", signature, re.IGNORECASE) is not None


def references_to_parts(project: Project, contracts: dict) -> set:
    """{(contract path, part name)} that a manifest lists under `parts` or a link in a contract points to."""
    out = set()
    for unit in project.units:
        if unit.broken:
            continue
        for entries in (unit.capabilities, unit.needs):
            for spec in entries.values():
                target = contract_target(project, unit, spec.get("contract"))[1]
                out.update((target, part) for part in spec.get("parts") or [])
    for path, contract in contracts.items():
        for file in {path} | {part["file"] for part in contract["parts"].values()}:
            for _, link in project.doc(file).links:
                if SCHEME.match(link) or link.startswith("/"):
                    continue
                rel_path, anchor = split_link(link)
                target = os.path.normpath(os.path.join(os.path.dirname(file), rel_path)) if rel_path else file
                if contract["folder"] and file == path and os.path.dirname(target) == os.path.dirname(path):
                    continue                          # the index of a contract folder lists its parts; that is no use
                if target in contracts and anchor:
                    out.add((target, anchor.lower()))
                elif os.path.join(os.path.dirname(target), "index.md") in contracts and target.endswith(".md"):
                    out.add((os.path.join(os.path.dirname(target), "index.md"), os.path.basename(target)[:-3]))
    return out


def check_unused_types(project: Project):
    """C10: a type some part reaches. Only a name in a signature counts, not the same word in a sentence."""
    contracts = {path: contract_of_path(project, path) for path in contracts_of_project(project)}
    referenced = references_to_parts(project, contracts)
    for path, contract in sorted(contracts.items()):
        parts = contract["parts"]
        types = {name for name, part in parts.items() if part["kind"] == "type"}
        users = [part["signature"] for part in parts.values() if part["kind"] in CALL_KINDS + RAISE_KINDS]
        if not users:                                 # a contract of types only offers the types themselves
            continue
        used = {name for name in types if (path, name) in referenced}
        waiting = users + [parts[name]["signature"] for name in used]
        while waiting:
            signature = waiting.pop()
            for name in sorted(types - used):
                if names_type(signature, name):
                    used.add(name)
                    waiting.append(parts[name]["signature"])
        for name in sorted(types - used):
            project.add("C10", parts[name]["file"], f"type '{name}' is used by no part of the contract", parts[name]["line"])


def calling_kinds(contract: dict) -> set:
    return {n for n, p in contract["parts"].items() if p["kind"] in CALL_KINDS + RAISE_KINDS}


def check_states(project: Project, path: str, contract: dict):
    """C7: the `## States` table of a contract."""
    states = contract["states"]
    if states is None:
        return
    if states["header"] != ["state", "part", "result", "next"]:
        project.add("C7", path, "`## States` needs a table with the columns `State | Part | Result | Next`",
                    states["line"])
        return
    if not states["start"]:
        project.add("C7", path, "`## States` needs a line `Start: <state>`", states["line"])
    elif states["start"] not in [r["state"] for r in states["rows"]]:
        project.add("C7", path, f"the start state '{states['start']}' has no row in the table", states["start-line"])
    known, seen = calling_kinds(contract), {}
    for row in states["rows"]:
        if not row["state"] or not row["next"]:
            project.add("C7", path, "a row of `## States` names its state and its next state", row["line"])
            continue
        if row["part"] not in known:
            project.add("C7", path, f"'{row['part']}' is not a command, query, event or callback of this contract", row["line"])
            continue
        wanted = row_result(row["result"])
        part = contract["parts"][row["part"]]
        if wanted not in ("any", "ok") and wanted not in part["errors"]:
            project.add("C7", path, f"result '{wanted}' is not an error case of '{row['part']}'; a result is empty, "
                                    "`ok` or an error case that `Errors:` names", row["line"])
        key = (row["state"], row["part"], wanted)
        if key in seen:
            project.add("C7", path, f"this row and the one on line {seen[key]} match the same step", row["line"])
        seen.setdefault(key, row["line"])


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
                if user is not root and user.kind in ("logic", "stateful"):
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
    """Resolve one hop of a scenario of `holder`, written in the direction of the call.

    Returns (result, error). result: {"caller", "target", "part", "input", "kind": the part's kind,
    "direction": "call" (consumer to provider) or "raise" (provider to consumer), "contract": abs path,
    "via": [(unit, key)], "caller-unit", "target-unit", "caller-side", "target-side" ("unit", "capability"
    or "need" of the holder), "caller-entry", "target-entry", "provider", "provider-key"}.
    """
    match = HOP.match(hop)
    if not match:
        return None, f"a hop is written `caller -> target.part`, not '{hop}'"
    caller_text, (target_text, given_input) = match.group(1), split_call(match.group(2), keep=True)
    target_path, _, part = target_text.rpartition(".")
    if not target_path or not part:
        return None, f"the target of hop '{hop}' is `unit.part`, `need.part` or `capability.part`"

    def lookup(name: str):
        """(unit, "capability"|"need"|None, entry name, error): what a name of the holder's level means."""
        unit = find_descendant(project, holder, name)
        cap, need = name in holder.capabilities, name in holder.needs
        if unit is not None and (cap or need):
            return None, None, None, f"'{name}' is both a unit below and a {'capability' if cap else 'need'} of this unit; rename one"
        if unit is None and not cap and not need:
            return None, None, None, f"'{name}' is neither a unit below this one nor a capability or need of it"
        return unit, ("capability" if cap else "need" if need else "unit"), (name if cap or need else None), None

    qualifier = None                                 # `target.capability.part` names the connection when two share the part
    target, target_side, target_entry, error = lookup(target_path)
    if error and "." in target_path:
        shorter, _, capability = target_path.rpartition(".")
        unit_here = find_descendant(project, holder, shorter)
        if unit_here is not None and capability in unit_here.capabilities:
            target_path, qualifier = shorter, capability
            target, target_side, target_entry, error = lookup(target_path)
    if error:
        return None, error
    caller, caller_side, caller_entry, error = lookup(caller_text)
    if error:
        return None, error

    def contract_path_of(owner: Unit, spec: dict):
        return contract_target(project, owner, spec.get("contract"))[1]

    def connections(consumer, consumer_side, consumer_entry, provider, provider_side, provider_entry):
        """[(contract, via, need, capability)] from a consumer (a unit, or a capability of the holder flowing
        down) to a provider (a unit, or a need of the holder passed up), or (None, why not)."""
        found = []
        if consumer_side == "need" or provider_side == "capability":
            return None, None
        if consumer_side == "unit" and provider_side == "unit":
            for need, spec in consumer.needs.items():
                for unit, capability, via in chain_of_need(consumer, need):
                    if unit is provider:
                        found.append((contract_path_of(consumer, spec), via, need, capability))
                        break
            return found, f"no need of '{consumer.rel if consumer else consumer_entry}' is provided for by '{provider.rel}'"
        if consumer_side == "capability" and provider_side == "unit":
            spec = holder.capabilities[consumer_entry]
            for unit, capability, via in chain_of_need_of_capability(holder, consumer_entry):
                if unit is provider:
                    found.append((contract_path_of(holder, spec), via, consumer_entry, capability))
                    break
            return found, f"capability '{consumer_entry}' of this unit is not implemented by '{provider.rel}'"
        if consumer_side == "unit" and provider_side == "need":
            for need, spec in consumer.needs.items():
                up = chain_up(consumer, need, holder)
                if up and up[0] == provider_entry:
                    found.append((contract_path_of(consumer, spec), up[1], need, None))
            return found, f"no need of '{consumer.rel}' is passed up to the need '{provider_entry}' of this unit"
        if holder.children:
            return None, (f"a hop between the capability '{consumer_entry}' and the need '{provider_entry}' of this unit "
                          "is for a unit without children; here it goes through the children")
        return [(contract_path_of(holder, holder.needs[provider_entry]), [], provider_entry, None)], None

    def matches(found, kinds):
        """The connections of `found` whose contract has the part with one of `kinds`, after the qualifier."""
        if not found:
            return []
        out = []
        for item in found:
            if qualifier is not None and item[3] != qualifier:
                continue
            contract = item[0] and contract_of_path(project, item[0])
            if contract and contract["parts"].get(part) is not None:
                out.append((item, contract["parts"][part].get("kind")))
        return [(item, kind) for item, kind in out if kind in kinds]

    forward, why_forward = connections(caller, caller_side, caller_entry, target, target_side, target_entry)
    reverse, why_reverse = connections(target, target_side, target_entry, caller, caller_side, caller_entry)
    calls = matches(forward, CALL_KINDS)
    raises = matches(reverse, RAISE_KINDS)
    if not calls and not raises:
        wrong_way = matches(forward, RAISE_KINDS) or matches(reverse, CALL_KINDS)
        if wrong_way:
            kind = wrong_way[0][1]
            who = "the provider raises it" if kind in RAISE_KINDS else "the consumer calls it"
            return None, (f"'{part}' is {'an' if kind == 'event' else 'a'} {kind}, and {who}: write "
                          f"`{target_path} -> {caller_text}.{part}`")
        typed = [item for item in (forward or []) + (reverse or [])
                 if item[0] and contract_of_path(project, item[0])["parts"].get(part, {}).get("kind") == "type"]
        if typed:
            return None, f"'{part}' is a type of {project.rel(typed[0][0])}; a hop names a command, query, event or callback"
        if forward:
            contracts = sorted({project.rel(f[0]) for f in forward if f[0]} or {"none"})
            return None, f"part '{part}' is not in the contract {', '.join(contracts)}"
        if reverse and not forward:
            contracts = sorted({project.rel(f[0]) for f in reverse if f[0]} or {"none"})
            return None, f"part '{part}' is not in the contract {', '.join(contracts)}"
        return None, why_forward or why_reverse or f"'{caller_text}' and '{target_path}' are not connected"
    chosen = calls or raises
    if len(chosen) > 1:
        caps = sorted({item[3] for item, _ in chosen if item[3]})
        return None, (f"'{caller_text}' reaches '{target_path}' through {len(chosen)} connections whose contracts "
                      f"both have the part '{part}' (needs {', '.join(item[2] for item, _ in chosen)}); write "
                      + (f"`{target_path}.<capability>.{part}` with one of {', '.join(caps)}" if caps else "the need"))
    (contract, via, need, capability), kind = chosen[0]
    direction = "call" if calls else "raise"
    provider, provider_unit = (target_path, target) if direction == "call" else (caller_text, caller)
    provider_entry = target_entry if direction == "call" else caller_entry
    return {"caller": caller_text, "target": target_path, "part": part, "input": given_input,
            "contract": contract, "via": via, "kind": kind, "direction": direction, "problems": [],
            "caller-unit": caller, "target-unit": target,
            "caller-side": caller_side, "target-side": target_side,
            "caller-entry": caller_entry, "target-entry": target_entry,
            "caller-capability": caller_entry if caller_side == "capability" else None,
            "target-need": target_entry if target_side == "need" else None,
            "provider": provider, "provider-key": (provider_unit or ("need", provider_entry), contract)}, None


def check_hop_result(project: Project, result: dict):
    """N7 and N8: the result of a resolved hop against the examples and the error cases of its part.
    A result `= <case>` takes the input and the expected result of that example."""
    part = contract_of_path(project, result["contract"])["parts"][result["part"]]
    value = result.get("result")
    if value is None:
        return
    where = f"{project.rel(result['contract'])}, part '{result['part']}'"
    if value.startswith("="):
        row = example_row(part, value[1:].strip())
        if row is None:
            result["problems"].append(("N7", f"no example '{value[1:].strip()}' in {where}"))
            return
        result["example"], result["result"] = row["id"], plain(row["expected"])
        if result.get("input") is None and row["input"]:
            result["input"] = plain(row["input"])
        return
    if result.get("input") is not None:
        rows = [r for r in part["rows"] if plain(r["input"]) == plain(result["input"]) and r["input"]]
        if rows and all(plain(r["expected"]) != plain(value) for r in rows):
            row = rows[0]
            result["problems"].append(("N7", f"the example '{row['case']}' of {where} expects "
                                              f"'{plain(row['expected'])}' for this input, not '{value}'"))
        elif rows:
            result["example"] = next(r["id"] for r in rows if plain(r["expected"]) == plain(value))
    bare = plain(value)
    if bare.lower() != "ok" and bare not in part["errors"]:
        loose = lambda s: re.sub(r"[-_\s]", "", s).lower()
        close = [e for e in part["errors"] if loose(e) == loose(bare)]
        if close:
            result["problems"].append(("N8", f"the result '{value}' is not the error case `{close[0]}` of {where}; "
                                              "it counts as a success"))


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


def include_of(project: Project, holder: Unit, text: str):
    """(unit, scenario name, caller) when `text` includes a scenario of a unit below `holder`:
    `<unit>.<scenario>` or `<caller> -> <unit>.<scenario>`; else None. A hop whose part is also a
    scenario of the target counts as an include only when no connection has that part."""
    match = SCENARIO_REF.match(text)
    if not match:
        return None
    child = find_descendant(project, holder, match.group(2))
    if child is None or match.group(3) not in child.scenarios:
        return None
    return child, match.group(3), match.group(1)


def expand_reference(project: Project, holder: Unit, text: str, seen: tuple):
    """The hops of a scenario of a unit below `holder`, rewritten to the names of `holder`'s level:
    ([(item, group path)], groups, error). `text` is `<unit>.<scenario>` or `<caller> -> <unit>.<scenario>`;
    the caller picks the user of a capability of the included unit where it has several."""
    found = include_of(project, holder, text)
    if found is None:
        match = SCENARIO_REF.match(text)
        return None, None, (f"'{match.group(2)}' is not a unit below this one, or holds no scenario '{match.group(3)}'"
                            if match else f"'{text}' is neither a hop nor `unit.scenario`")
    child, name, caller_text = found
    hint = None
    if caller_text is not None:
        hint_unit = find_descendant(project, holder, caller_text)
        if hint_unit is not None:
            hint = hint_unit
        elif caller_text in holder.capabilities:
            hint = ("capability", caller_text)
        else:
            return None, None, f"'{caller_text}' is neither a unit below this one nor a capability of it"
    if name not in child.scenarios:
        return None, None, f"'{child.rel}' holds no scenario '{name}'"
    if (child, name) in seen:
        return None, None, f"scenario '{name}' of '{child.rel}' includes itself"
    prefix = os.path.relpath(child.path, holder.path).replace(os.sep, "/")

    def above(child_ref: Unit, side: str, entry: str):
        """How the holder's level names a capability or need of the included unit: its user or provider there."""
        if side == "capability" and not child_ref.children:   # a leaf's own code implements its capability
            return prefix, None
        current, current_entry = child_ref, entry
        while current is not holder:
            parent = current.parent
            if side == "capability":
                users = parent.capability_users.get((current, current_entry), [])
                if len(users) > 1 and hint is not None and parent is holder:
                    users = [u for u in users if (u[0] == "need" and u[1] is hint) or (u[0] == "capability" and ("capability", u[1]) == hint)] or users
                if len(users) != 1:
                    return None, (f"'{current.rel}.{current_entry}' has {len(users)} users in '{parent.rel}'; a scenario that includes "
                                  "it needs exactly one")
                use = users[0]
                if use[0] == "need" and use[1] is parent:
                    return None, f"'{current.rel}.{current_entry}' meets a need of '{parent.rel}' itself, which no hop can name"
                if use[0] == "need":
                    if parent is not holder:
                        return None, "a scenario includes scenarios of direct children only"
                    return os.path.relpath(use[1].path, holder.path).replace(os.sep, "/"), None
                current, current_entry = parent, use[1]
            else:
                conn = parent.conn.get((current, current_entry))
                if conn is None:
                    return None, f"need '{current_entry}' of '{current.rel}' is not connected"
                entry_ = conn.entries[0]
                if entry_.kind == "child":
                    if parent is not holder:
                        return None, "a scenario includes scenarios of direct children only"
                    return os.path.relpath(entry_.unit.path, holder.path).replace(os.sep, "/"), None
                current, current_entry = parent, entry_.capability
        return current_entry, None

    groups, out = [], []
    flat, problems = flatten_hops(child.scenarios[name]["hops"], groups)
    if problems:
        return None, None, f"scenario '{name}' of '{child.rel}': {problems[0]}"
    pending, index = list(flat), 0                    # an include inserts its hops here, at the child's level, and they are mapped like the others
    while index < len(pending):
        item, path = pending[index]
        index += 1
        text_, value, problem = hop_item(item)
        if text_ is not None and include_of(project, child, text_) is not None:
            inner, inner_groups, error = expand_reference(project, child, text_, seen + ((child, name),))
            if error:
                return None, None, error
            base = len(groups)
            for g in inner_groups:
                g["id"] += base
                g["parent"] = (g["parent"] + base) if g["parent"] is not None else (path[-1] if path else None)
                g["branches"] = [b + base for b in g["branches"]]
            groups += inner_groups
            pending[index:index] = [(inner_item, path + tuple(p + base for p in inner_path)) for inner_item, inner_path in inner]
            continue
        if text_ is None:
            out.append((item, path))
            continue
        result, error = resolve_hop(project, child, text_)
        if error:
            return None, None, f"scenario '{name}' of '{child.rel}', hop '{text_}': {error}"
        names = {}
        for side in ("caller", "target"):
            if result[f"{side}-side"] == "unit":
                names[side] = prefix + "/" + result[side]
            else:
                mapped, error = above(child, result[f"{side}-side"], result[f"{side}-entry"])
                if error:
                    return None, None, f"scenario '{name}' of '{child.rel}', hop '{text_}': {error}"
                names[side] = mapped
        call = result["part"] + (f"({result['input']})" if result.get("input") is not None else "")
        out.append(({f"{names['caller']} -> {names['target']}.{call}": value}, path))
    return out, groups, None


def hop_item(item) -> tuple:
    """(hop text or None, result text or None, problem or None) of one hop of `hops`. A hop without a result
    is allowed here; whether its part needs one is checked once the hop is resolved."""
    if isinstance(item, str):
        return item, None, None
    if not isinstance(item, dict) or len(item) != 1:
        return None, None, "a hop is one line, `caller -> target.part: result`"
    (text, value), = item.items()
    if value is None:
        return str(text), None, None
    if not isinstance(value, str):
        why = f"its result is read as {show_value(value)}, not as text; quote it" \
            if isinstance(value, (bool, int, float)) else "its result is text"
        return str(text), None, why
    value = " ".join(value.split())
    return str(text), (value or None), None


def flatten_hops(items, groups: list, path: tuple = ()) -> tuple:
    """([(item, group path)], problems) of the items of `hops`: hops and references flat, the blocks
    `parallel` and `repeat` as groups. A group is {"id", "kind", "label", "parent", "branches"}."""
    out, problems = [], []
    for item in items if isinstance(items, list) else []:
        if isinstance(item, dict) and len(item) == 1 and next(iter(item)) in ("parallel", "repeat"):
            (kind, value), = item.items()
            gid = len(groups)
            if kind == "parallel":
                if not isinstance(value, list) or len(value) < 2 or not all(isinstance(b, list) and b for b in value):
                    problems.append("`parallel` is a list of two or more lists of hops")
                    continue
                group = {"id": gid, "kind": "parallel", "label": "", "parent": path[-1] if path else None, "branches": []}
                groups.append(group)
                for branch in value:
                    bid = len(groups)
                    groups.append({"id": bid, "kind": "branch", "label": "", "parent": gid, "branches": []})
                    group["branches"].append(bid)
                    inner, more = flatten_hops(branch, groups, path + (gid, bid))
                    out += inner
                    problems += more
            else:
                if not isinstance(value, dict) or not isinstance(value.get("hops"), list) or not value["hops"] \
                        or ("until" in value) == ("times" in value) \
                        or ("times" in value and (isinstance(value["times"], bool) or not isinstance(value["times"], int) or value["times"] < 1)) \
                        or ("until" in value and not isinstance(value["until"], str)) \
                        or set(value) - {"hops", "until", "times"}:
                    problems.append("`repeat` is a mapping with `hops` and `until` (text) or `times` (a number)")
                    continue
                label = f"until {value['until']}" if "until" in value else f"{value['times']} times"
                groups.append({"id": gid, "kind": "repeat", "label": label, "parent": path[-1] if path else None, "branches": []})
                inner, more = flatten_hops(value["hops"], groups, path + (gid,))
                out += inner
                problems += more
        else:
            out.append((item, path))
    return out, problems


def given_item(item) -> tuple:
    """(connection or None, state or condition text, problem or None) of one item of `given`."""
    if isinstance(item, str) and item.strip():
        return None, " ".join(item.split()), None
    if isinstance(item, dict) and len(item) == 1:
        (key, value), = item.items()
        if isinstance(value, (str, int, float)) and not isinstance(value, bool) and str(value).strip():
            return str(key).strip(), plain(str(value)), None
    return None, None, "an item of `given` is a sentence or `connection: state`"


def stateful(contract: dict) -> bool:
    states = contract["states"]
    return states is not None and states["header"] == ["state", "part", "result", "next"]


def given_connection(project: Project, holder: Unit, name: str) -> tuple:
    """((target, contract path), None) for a connection that `given` names, or (None, problem). The target
    is a unit below `holder`, or ("need", name) for a need of `holder`."""
    if "." not in name:
        spec = holder.needs.get(name)
        if spec is None:
            return None, f"'{name}' is not a need of this unit; a connection is `unit.capability` or a need of this unit"
        target, contract = ("need", name), contract_target(project, holder, spec.get("contract"))[1]
    else:
        path, _, capability = name.rpartition(".")
        unit = find_descendant(project, holder, path)
        if unit is None or capability not in unit.capabilities:
            return None, f"'{name}' is not a capability of a unit below this one"
        target, contract = unit, contract_target(project, unit, unit.capabilities[capability].get("contract"))[1]
    if not contract or project.kind_of(contract) != "file" or not stateful(contract_of_path(project, contract)):
        return None, f"the contract of '{name}' has no `## States`"
    return (target, contract), None


def walk_states(project: Project, scenario: dict):
    """Resolve `given` and follow every connection with `## States` hop by hop. Sets scenario["given"]:
    [{"connection", "text", "state", "rule", "problem"}] and scenario["states"]: per hop (state before,
    state after, problem), both None for a hop over a connection without states."""
    holder, current, given = scenario["unit"], {}, []
    for item in scenario["spec"]["given"]:
        name, text, problem = given_item(item)
        entry = {"connection": name, "text": text, "state": None, "rule": "N2" if problem else None,
                 "problem": problem}
        if name is not None:
            key, problem = given_connection(project, holder, name)
            if problem:
                entry.update(rule="N5", problem=problem)
            elif text not in contract_of_path(project, key[1])["states"]["states"]:
                entry.update(rule="N5", problem=f"'{text}' is not a state of {project.rel(key[1])}")
            else:
                entry["state"], current[key] = text, text
        given.append(entry)
    states = [(None, None, None)] * len(scenario["hops"])
    groups, paths = scenario["groups"], scenario["paths"]

    def order(indices: list, level: int) -> list:
        """The hops in the order the walk follows them: the hops of a `repeat` twice, so that a round can follow a round."""
        out, i = [], 0
        while i < len(indices):
            path = paths[indices[i]]
            if len(path) <= level:
                out.append(indices[i])
                i += 1
                continue
            gid, j = path[level], i
            while j < len(indices) and len(paths[indices[j]]) > level and paths[indices[j]][level] == gid:
                j += 1
            out += order(indices[i:j], level + 1) * (2 if groups[gid]["kind"] == "repeat" else 1)
            i = j
        return out

    for index in order(list(range(len(scenario["hops"]))), 0):
        _, result, _ = scenario["hops"][index]
        contract = contract_of_path(project, result["contract"]) if result else None
        if contract is None or not stateful(contract) or (result.get("result") is None and result["kind"] not in RAISE_KINDS):
            continue
        key = result["provider-key"]
        before = current.get(key, contract["states"]["start"])
        if before is None:                            # unknown after an earlier problem
            continue
        after, why = next_state(contract, before, result["part"], result["result"] if result.get("result") is not None else "")
        if states[index] == (None, None, None):
            states[index] = (before, after, why and f"{why} ({project.rel(result['contract'])})")
        elif why and not states[index][2]:            # the second round of a repeat
            states[index] = states[index][:2] + (f"{why} when the repeat runs again ({project.rel(result['contract'])})",)
        current[key] = after
    scenario["given"], scenario["states"] = given, states


def resolved_scenarios(project: Project) -> list:
    """Every scenario of the project with its hops resolved: [{"unit", "name", "spec", "hops": [(hop,
    result, error)], "groups", "paths", "given", "states"}], cached. A result carries the hop's "input"
    and "result". Blocks (`parallel`, `repeat`) are groups; a hop's path lists the groups it is in."""
    cached = project.__dict__.get("_scenarios")
    if cached is not None:
        return cached
    out = []
    for unit in project.units:
        if unit.broken:
            continue
        for name, spec in unit.scenarios.items():
            groups: list = []
            flat, _ = flatten_hops(spec["hops"], groups)
            hops, paths = [], []
            for item, path in flat:
                text, value, problem = hop_item(item)
                if text is None:
                    hops.append((str(item), None, "a hop is one line, `caller -> target.part: result`"))
                    paths.append(path)
                    continue
                included = include_of(project, unit, text)
                if included is not None or ("->" not in text and SCENARIO_REF.match(text)):
                    if included is not None and "->" in text and resolve_hop(project, unit, text)[0] is not None:
                        hops.append((text, None, f"'{text}' is both a hop and the scenario '{included[1]}' of '{included[0].rel}'; rename one"))
                        paths.append(path)
                        continue
                    inner, inner_groups, error = expand_reference(project, unit, text, ((unit, name),))
                    if error:
                        hops.append((text, None, error))
                        paths.append(path)
                        continue
                    child, scenario_name, caller_text = included
                    base = len(groups)
                    ref_id = base
                    groups.append({"id": ref_id, "kind": "ref", "label": f"{os.path.relpath(child.path, unit.path).replace(os.sep, '/')}.{scenario_name}",
                                   "parent": path[-1] if path else None, "branches": [],
                                   "caller": caller_text, "unit": os.path.relpath(child.path, unit.path).replace(os.sep, "/"),
                                   "caller-unit": find_descendant(project, unit, caller_text) if caller_text else None,
                                   "child": child})
                    for g in inner_groups:
                        g["id"] += base + 1
                        g["parent"] = (g["parent"] + base + 1) if g["parent"] is not None else ref_id
                        g["branches"] = [b + base + 1 for b in g["branches"]]
                    groups += inner_groups
                    for inner_item, inner_path in inner:
                        inner_text, inner_value, _ = hop_item(inner_item)
                        result, error = resolve_hop(project, unit, inner_text)
                        if result:
                            result["result"] = inner_value
                            check_hop_result(project, result)
                        hops.append((inner_text, result, error))
                        paths.append(path + (ref_id,) + tuple(p + base + 1 for p in inner_path))
                    continue
                result, error = resolve_hop(project, unit, text)
                if result:
                    result["result"] = value
                    if value is None and result["kind"] in CALL_KINDS and not problem:
                        result["problems"].append(("N2", f"it has no result; a {result['kind']} has one"))
                    check_hop_result(project, result)
                elif problem:
                    error = problem
                hops.append((text, result, error))
                paths.append(path)
            scenario = {"unit": unit, "name": name, "spec": spec, "hops": hops, "groups": groups, "paths": paths}
            walk_states(project, scenario)
            out.append(scenario)
    project.__dict__["_scenarios"] = out
    return out


def lines_outside(unit: Unit, side: str, entry) -> list:
    """The wiring lines above `unit` that a step at one of its capabilities or needs goes through, and
    the lines below the providers of the need: a scenario of a child uses the lines of its parents."""
    out, current, name = [], unit, entry
    if side == "need":
        while current.parent is not None and name not in current.inner:
            conn = current.parent.conn.get((current, name))
            if conn is None:
                break
            out.append((current.parent, conn.key))
            for e in conn.entries:                    # the lines below a provider, down to the unit that implements it
                if e.kind == "child":
                    out += [line for _, _, via in chain_of_need_of_capability(e.unit, e.capability) for line in via]
            passed = next((e.capability for e in conn.entries if e.kind == "own"), None)
            if passed is None:
                break
            current, name = current.parent, passed
        return out
    if side != "capability":
        return []
    while current.parent is not None:
        parent = current.parent
        for conn in parent.conn.values():             # the needs of siblings wired to the capability
            if any(e.kind == "child" and e.unit is current and e.capability == name for e in conn.entries):
                out.append((parent, conn.key))
        up = next((cap for cap, conn in parent.impl.items() if any(e.unit is current and e.capability == name for e in conn.entries)), None)
        if up is None:
            break
        out.append((parent, parent.impl[up].key))     # the capability of the parent it implements
        current, name = parent, up
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
    """N1 to N6."""
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
            if hops is not None and not isinstance(hops, list):
                project.add("N2", unit.manifest_path, f"scenario '{name}': `hops` is a list of "
                                                      "`caller -> target.part: result`", line)
            flat, problems = flatten_hops(hops if isinstance(hops, list) else [], [])
            for problem in problems:
                project.add("N2", unit.manifest_path, f"scenario '{name}': {problem}", line)
            for item, _ in flat:
                text, _, problem = hop_item(item)
                if problem:
                    project.add("N2", unit.manifest_path, f"scenario '{name}', hop '{text or show_value(item)}': "
                                                          f"{problem}", line)
            given = spec.get("given")
            if given is not None and not isinstance(given, list):
                project.add("N2", unit.manifest_path, f"scenario '{name}': `given` is a list of sentences and "
                                                      "`connection: state` items", line)
            for key in ("summary", "expect", "source"):
                if key in spec and (not isinstance(spec[key], str) or not spec[key].strip()):
                    project.add("N2", unit.manifest_path, f"scenario '{name}': `{key}` is one line of text", line)
                elif key in spec and PLACEHOLDER.match(spec[key].strip()):
                    project.add("M2", unit.manifest_path, f"scenario '{name}': `{key}` is a placeholder ({spec[key].strip()})", line)
    unresolved: set = set()                           # holders of a scenario with an unresolved hop
    for scenario in resolved_scenarios(project):
        unit, name = scenario["unit"], scenario["name"]
        line = unit.lines.get(("scenarios", name))
        for entry in scenario["given"]:
            if entry["problem"]:
                project.add(entry["rule"], unit.manifest_path, f"scenario '{name}', given "
                            f"'{entry['connection'] or entry['text'] or ''}': {entry['problem']}", line)
        for index, ((hop, result, error), (_, _, problem)) in enumerate(zip(scenario["hops"], scenario["states"]), 1):
            if error:
                rule = "N2" if error.startswith("its result") or "a hop is one line" in error else "N1"
                project.add(rule, unit.manifest_path, f"scenario '{name}', hop '{hop}': {error}", line)
                unresolved.add(unit)
            else:
                for holder, key in result["via"]:
                    used.setdefault(holder, set()).add(key)
                for side, entry in ((result["caller-side"], result["caller-entry"]), (result["target-side"], result["target-entry"])):
                    for holder, key in lines_outside(unit, side, entry):   # a scenario of a child uses the lines of its parents
                        used.setdefault(holder, set()).add(key)
                carrier = contract_of_path(project, result["contract"])["carrier"]
                if carrier:                           # the carrier's connections at the units of the hop count as used
                    ends = {u for u in (result["caller-unit"], result["target-unit"]) if u is not None}
                    for owner in project.units:
                        for (child, need), conn in owner.conn.items():
                            if child in ends and contract_target(project, child, child.needs[need].get("contract"))[1] == carrier:
                                used.setdefault(owner, set()).add(conn.key)
                        for need, conn in owner.inner.items():
                            if owner in ends and contract_target(project, owner, owner.needs[need].get("contract"))[1] == carrier:
                                used.setdefault(owner, set()).add(conn.key)
            if problem:
                project.add("N6", unit.manifest_path, f"scenario '{name}', hop {index} '{hop}: "
                                                      f"{result['result']}': {problem}", line)
            for rule, message in (result or {}).get("problems", []):
                project.add(rule, unit.manifest_path, f"scenario '{name}', hop {index} '{hop}': {message}", line)
    for unit, keys in used.items():
        wiring = unit.manifest.get("wiring")
        if not isinstance(wiring, dict) or unit in unresolved:   # fix N1 first
            continue
        for key in wiring:
            if str(key).strip() not in keys:
                project.add("N3", unit.manifest_path, f"wiring line '{key}' is used by no hop of the scenarios "
                                                      "that pass through this unit", unit.lines.get(("wiring", str(key))))
    if not resolved_scenarios(project) or unresolved:     # N4 says nothing without stories, and N1 comes first
        return
    used_parts = {(result["contract"], result["part"]) for scenario in resolved_scenarios(project)
                  for _, result, _ in scenario["hops"] if result}
    for path in sorted(contracts_of_project(project)):
        contract = contract_of_path(project, path)
        for name, part in contract["parts"].items():
            if part["kind"] in CALL_KINDS + RAISE_KINDS and (path, name) not in used_parts:
                project.add("N4", part["file"], f"part '{name}' is used by no hop of a scenario", part["line"])


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
                                                               "run `unifold check --fix`.")
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
        if unit.parent is not None:
            candidates.append(os.path.join(unit.path, "AGENTS.md"))
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


def kind_and_runs_as(unit: Unit) -> str:
    """What a unit is and what it runs as, as far as its manifest says: `stateful, process`."""
    return ", ".join(x for x in (unit.kind, unit.runs_as) if x)


def unit_label(unit: Unit) -> str:
    """The name of a unit in a diagram, with its kind and what it runs as where it states them."""
    about = kind_and_runs_as(unit)
    return f"{unit.name} ({about})" if about else unit.name


def diagram_kinds(project: Project, unit: Unit) -> list:
    """Which diagrams the generator writes for a unit, in the order of the navigation."""
    mode = project.diagrams
    if mode == "none" or unit.broken:
        return []
    return ["component"] if unit.children else []


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
    marks = {"planned": [], "deprecated": []}

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
        rows.append(f"| {name} | {cell(kind_and_runs_as(unit))} | {cell(unit.responsibility)} | "
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
        out[kind] = diagram(project, unit, 1, out_dir)
    return out


def lifelines_of(scenario: dict) -> dict:
    """{name: (kind, what it does)} of the lifelines of a scenario: a unit, or a capability or need of the holder."""
    holder, about = scenario["unit"], {}
    for hop, result, error in scenario["hops"]:
        if not result:
            continue
        for name, unit, side, entry in ((result["caller"], result["caller-unit"], result["caller-side"], result["caller-entry"]),
                                        (result["target"], result["target-unit"], result["target-side"], result["target-entry"])):
            spec = (holder.capabilities if side == "capability" else holder.needs).get(entry) if side != "unit" else None
            info = (kind_and_runs_as(unit), unit.responsibility) if unit else ("", spec["summary"]) if spec else ("", "")
            if name not in about or (info[1] and not about[name][1]):
                about[name] = info
    return about


# A long picture repeats its boxes at the bottom: the top has scrolled away by then, and Mermaid draws a
# lifeline only 2000 high unless it repeats them. A row, an arrow or a note, takes at most about 80.
LONG_SEQUENCE = 24
SEQUENCE_ROW = re.compile(r"^\s*(Note |\S+?(-->>|->>|-\))\S+:)")


def scenario_sequence(scenario: dict) -> tuple:
    """The sequence diagram of a scenario, one lifeline per name as written: (Mermaid lines,
    {name: participant id}). A lifeline stands right after the ones introduced through the same
    partner: the lifelines form a tree by the first step that names each, walked depth first.

    A step is drawn as the kind of its part says: a command, query or callback with a solid arrow
    from the caller to the target, an event with an open arrowhead from the unit that raises it to
    the one that receives it. The receiver of a step is active until a lifeline further out makes
    the next step, or the scenario ends; a unit below the receiver acts for it, as it implements
    the receiver's capability. When the receiver is done, a dashed arrow returns its result; a step
    that nothing follows inside leaves no bar and carries its result on its own arrow. An event is
    asynchronous: when a unit raises one, the call it was handling has returned, and so has every
    call that waited for that return and does nothing more afterwards; a unit handling an event
    keeps running; an event from a unit outside the open calls arrives during them. An event lands
    on the open bar of its receiver; only an idle receiver gets a new bar."""
    within = lambda a, b: a == b or a.startswith(b + "/") or b.startswith(a + "/")   # the same lifeline, or one below the other
    kids: dict = {}                                   # name -> the lifelines its steps introduced, in order
    roots: list = []                                  # the lifelines no earlier one introduced
    for hop, result, error in scenario["hops"]:
        ends = list((result["caller"], result["target"]) if result else
                    [s.strip() for s in hop.split("->", 1)] if "->" in hop else [hop])
        ends = [e.rsplit(".", 1)[0] if e is not hop and "." in e and result is None else e for e in ends]
        for i, name in enumerate(ends):
            if name in kids:
                continue
            kids[name] = []
            other = ends[1 - i] if len(ends) == 2 else None
            parent = other if other in kids and other != name else next((k for k in kids if k != name and within(name, k)), None)
            (kids[parent] if parent else roots).append(name)
    names: list = []

    def walk(name: str):
        names.append(name)
        for kid in kids[name]:
            walk(kid)

    for root in roots:
        walk(root)
    ids = {n: "p" + safe_id(n) for n in names}
    text = lambda t: label(str(t).replace(";", "#59;"))  # a `;` ends a statement of a sequence diagram
    wrapped = lambda t: "<br/>".join(text(line.replace(NBSP, " ")) for line in textwrap.wrap(   # a step number, a result and a count of steps stay with their word
        re.sub(r"^(↩ )?(\d+) · ", lambda m: f"{m[1] or ''}{m[2]}{NBSP}·{NBSP}", str(t)).replace(" → ", f" →{NBSP}").replace(" steps)", f"{NBSP}steps)").replace(" step)", f"{NBSP}step)"),
        STEP_WIDTH, break_long_words=False, break_on_hyphens=False))
    about = lifelines_of(scenario)
    lines = ["---", "config:", "  sequence:", "    mirrorActors: false", "---", "sequenceDiagram"]   # the names stand on top only, unless the picture is long: see the end
    for n in names:
        kind = about.get(n, ("", ""))[0]              # what a lifeline does is in the table of the page: a narrow box leaves the picture wide enough to read
        lines.append(f'  participant {ids[n]} as {text(n)}' + (f"<br/>{text(f'«{kind}»')}" if kind else ""))
    busy: list = []                                   # (receiver, sender, step, kind, answer, path, note) of the steps still running, innermost last

    def done(step: tuple):
        """The receiver of the step is done: its result returns, its bar ends and the state its step
        led to is noted. A step with nothing inside leaves no bar: a command or callback then carries
        its result on its own arrow, and a query answers with a dashed arrow."""
        receiver, sender, index, kind, answer, _, note = step
        back = f"  {ids[receiver]}-->>{ids[sender]}: " + wrapped(f"↩ {index}" + (f" · {answer}" if answer else ""))
        if lines[-1] == f"  activate {ids[receiver]}":
            lines.pop()
            if kind == "query":
                lines.append(back)
            elif answer and kind != "event":
                lines[-1] = lines[-1][:lines[-1].index(": ") + 2] + wrapped(f"{steps[index]} → {answer}")
        else:
            if kind != "event":
                lines.append(back)
            lines.append(f"  deactivate {ids[receiver]}")
        if note:
            lines.append(note)

    steps: dict = {}                                  # step -> the text of its arrow: a result that stays on the arrow joins it
    shown: set = set()                                # the stateful connections whose state is drawn already
    states = scenario.get("states") or [(None, None, None)] * len(scenario["hops"])
    groups, paths = scenario.get("groups") or [], scenario.get("paths") or [()] * len(scenario["hops"])
    opened: list = []                                 # the groups whose block is open, outermost first

    def closes(next_path: tuple):
        while opened and opened[-1] not in next_path:   # a block ends with the steps that started inside it
            while busy and opened[-1] in busy[-1][5]:
                done(busy.pop())
            if groups[opened[-1]]["kind"] != "branch":   # the `end` of a par closes its last branch too
                lines.append("  end")
            opened.pop()

    def idle_after(index: int) -> bool:
        """Whether the receiver of the innermost open step takes no further step before a lifeline
        further out does: its call has returned."""
        receiver, outer = busy[-1][0], [b[1] for b in busy]
        for hop, result, error in scenario["hops"][index:]:
            if result and within(result["caller"], receiver):
                return False
            if result and any(within(result["caller"], o) for o in outer):
                return True
        return True

    for index, ((hop, result, error), (before, after, _), path) in enumerate(zip(scenario["hops"], states, paths), 1):
        if not result:
            continue
        closes(path)
        kind = result.get("kind")
        sender, receiver = result["caller"], result["target"]
        raises = kind == "event" or result.get("raised")
        if (raises and not any(within(sender, b[0]) or within(sender, b[1]) for b in busy)) or (kind == "include" and sender == receiver):
            pass                                      # a unit outside the open calls raises it, or nobody calls: it happens during them
        else:
            while busy and not within(sender, busy[-1][0]):   # the steps inside the last one are over when a lifeline further out acts
                done(busy.pop())
            waiting = sender                          # an event is asynchronous: the call its raiser was handling has returned,
            while raises and busy and busy[-1][3] != "event" and within(waiting, busy[-1][0]) \
                    and (waiting == sender or idle_after(index)):   # and so has every call that waited for it and does nothing more
                waiting = busy[-1][1]
                done(busy.pop())
        for gid in path:
            if gid in opened:
                continue
            group = groups[gid]
            if group["kind"] == "parallel":
                lines.append("  par")
            elif group["kind"] == "branch":
                if groups[group["parent"]]["branches"].index(gid) > 0:
                    lines.append("  and")
            elif group["kind"] == "repeat":
                lines.append(f"  loop {text(group['label'])}")
            else:
                lines.append("  rect rgba(128, 128, 128, 0.1)")   # translucent: a shade on a light page and on a dark one
                lines.append(f"  Note over {ids[result['caller']]}: {text('scenario ' + group['label'])}")
            opened.append(gid)
        key = result.get("provider-key")
        if key is not None and before is not None and key not in shown:   # the state a connection starts the scenario in
            shown.add(key)
            lines.append(f"  Note over {ids[result['provider']]}: {text(contract_topic(result['contract']) + ': ' + before)}")
        if kind == "include":                         # a collapsed included scenario: one step, no bar; a note when no caller is named
            lines.append(f"  Note over {ids[receiver]}: {wrapped(f'{index} · ' + result['label'])}" if sender == receiver else
                         f"  {ids[sender]}{'-)' if raises else '->>'}{ids[receiver]}: {wrapped(f'{index} · ' + result['label'])}")
            continue
        call = result["part"] + (f"({result['input']})" if result.get("input") is not None else "")
        answer = result.get("result") or ""
        note = (f"  Note over {ids[result['provider']]}: {text(contract_topic(result['contract']) + ': ' + after)}"
                if key is not None and after is not None and after != before else None)
        steps[index] = f"{index} · {call}"
        lines.append(f"  {ids[sender]}{'-)' if kind == 'event' else '->>'}{ids[receiver]}: "
                     + wrapped(steps[index] + (f" → {answer}" if answer and kind == "event" else "")))
        if kind == "event" and note:                  # an event changes the state when it is raised; a call when it returns
            lines.append(note)
        if kind == "event" and any(b[0] == receiver for b in busy):   # it lands on the open bar of its receiver
            continue
        lines.append(f"  activate {ids[receiver]}")
        busy.append((receiver, sender, index, kind, answer, path, None if kind == "event" else note))
    closes(())
    while busy:
        done(busy.pop())
    expect = scenario["spec"]["expect"]
    if expect and names and names[-1]:                # `wrap:` keeps a long expectation within the lifelines
        lines.append(f"  Note over {ids[names[0]]},{ids[names[-1]]}: wrap: Expect: {text(expect)}"
                     if len(names) > 1 else f"  Note over {ids[names[0]]}: wrap: Expect: {text(expect)}")
    if sum(1 for line in lines if SEQUENCE_ROW.match(line)) > LONG_SEQUENCE:
        lines[3] = "    mirrorActors: true"
    return lines, ids


def collapsed(scenario: dict) -> dict:
    """The scenario with every included scenario folded into one step: the view `unifold scenario`
    prints by default. Hops that lie in a top-level `ref` group become one step of kind `include`, from
    the caller of its first step, unless the include names one. A first step whose caller lies inside
    the included unit has no caller here: the step is a note on the unit."""
    groups = scenario.get("groups") or []
    hops, paths, states, done = [], [], [], set()
    for (hop, result, error), path, state in zip(scenario["hops"], scenario.get("paths") or [()] * len(scenario["hops"]),
                                                 scenario.get("states") or [(None, None, None)] * len(scenario["hops"])):
        ref = next((g for g in path if groups[g]["kind"] == "ref"), None)
        if ref is None:
            hops.append((hop, result, error))
            paths.append(path)
            states.append(state)
            continue
        if ref in done:
            continue
        done.add(ref)
        group = groups[ref]
        inside = sum(1 for p in scenario["paths"] if ref in p)
        first = result or {}                          # the first hop that lies in the group
        outside = first.get("caller") and first["caller"] != group["unit"] and not first["caller"].startswith(group["unit"] + "/")
        caller = group.get("caller") or (first["caller"] if outside else group["unit"])
        same = caller == first.get("caller")
        hops.append((group["label"], {"caller": caller, "target": group["unit"], "part": group["label"], "input": None,
                                      "result": f"{inside} step{'s' if inside != 1 else ''}", "kind": "include", "direction": "call", "contract": None,
                                      "label": f"scenario {group['label']} ({inside} step{'s' if inside != 1 else ''})", "via": [], "problems": [],
                                      "raised": first.get("kind") == "event" and same,
                                      "caller-unit": first.get("caller-unit") if same else group.get("caller-unit") or group["child"],
                                      "target-unit": group["child"],
                                      "caller-side": first.get("caller-side", "unit") if same else "unit", "target-side": "unit",
                                      "caller-entry": first.get("caller-entry") if same else None, "target-entry": None,
                                      "provider": group["unit"], "provider-key": None}, None))
        paths.append(tuple(g for g in path[:path.index(ref)]))
        states.append((None, None, None))
    return {**scenario, "hops": hops, "paths": paths, "states": states}


def scenario_page(project: Project, scenario: dict, expand: bool = False) -> str:
    """The page of a scenario, as `unifold scenario` prints it: a sequence diagram of the hops, end to end, and a table."""
    unit, name, spec = scenario["unit"], scenario["name"], scenario["spec"]
    out_dir = os.getcwd()                             # the page is printed, so its links start where the reader is
    if not expand:
        scenario = collapsed(scenario)
    lines, ids = scenario_sequence(scenario)
    about = lifelines_of(scenario)
    lifelines = ["| Lifeline | Kind | What it does |", "|---|---|---|"]
    lifelines += [f"| `{cell(name)}` | {cell(about.get(name, ('', ''))[0])} | {cell(about.get(name, ('', ''))[1])} |" for name in ids]
    rows = ["| # | Caller | Target | Call | Kind | Result | State | Contract |", "|---|---|---|---|---|---|---|---|"]
    states = scenario.get("states") or [(None, None, None)] * len(scenario["hops"])
    groups, paths = scenario.get("groups") or [], scenario.get("paths") or [()] * len(scenario["hops"])
    for index, ((hop, result, error), (_, after, _), path) in enumerate(zip(scenario["hops"], states, paths), 1):
        if result and result.get("kind") == "include":
            rows.append(f"| {index} | {'`' + cell(result['caller']) + '`' if result['caller'] != result['target'] else ''} | `{cell(result['target'])}` | scenario `{cell(result['part'])}` | include | "
                        f"{cell(result['result'])} |  | `unifold scenario {cell(project.rel(result['target-unit'].path))} {cell(result['part'].rsplit('.', 1)[-1])}` |")
        elif result:
            caller, target = result["caller"], result["target"]
            call = result["part"] + (f"({result['input']})" if result.get("input") is not None else "")
            contract = file_link(project, out_dir, contract_topic(result["contract"]), result["contract"])
            where = ", ".join(f"{groups[g]['kind']} {groups[g]['label']}".strip() for g in path if groups[g]["kind"] != "branch")
            rows.append(f"| {index} | `{cell(caller)}` | `{cell(target)}` | `{cell(call)}` | "
                        f"{cell(result.get('kind') or '')} | {cell(result.get('result') or '')} | {cell(after or '')} | {contract}"
                        + (f" ({cell(where)})" if where else "") + " |")
        else:
            rows.append(f"| {index} | `{cell(hop)}` | | | | | | **does not resolve** |")
    crumbs = []
    for ancestor in reversed(unit.ancestors()):
        crumbs.append(file_link(project, out_dir, ancestor.name, best_diagram(project, ancestor)))
    crumbs.append(f"**{cell(unit.name)}**")
    nav = []
    readme = os.path.join(unit.path, "README.md")
    if project.kind_of(readme) == "file":
        nav.append(f"[README]({link_to(out_dir, readme)})")
    nav += [f"[{kind}]({kind}.md)" for kind in diagram_kinds(project, unit)]
    given = "; ".join(f"`{e['connection']}` is {e['text']}" if e["connection"] else e["text"]
                      for e in scenario.get("given") or [] if e["text"])
    intro = [f"**{cell(spec['summary'])}**" if spec["summary"] else "",
             f"Source: {cell(spec['source'])}" if spec["source"] else "",
             f"Given: {cell(given)}" if given else "",
             f"Expect: {cell(spec['expect'])}" if spec["expect"] else ""]
    return "\n".join([f"# Scenario: {name}", "", " / ".join(crumbs) + "".join(" · " + n for n in nav), "",
                      *[line for line in intro if line], "",
                      "A unit is named by its path from `" + unit.name + "`; a capability or need of `" + unit.name
                      + "` is named bare. Every step is one hop along one connection of the map, in the direction of the "
                      "call: a command, query or callback from the caller to the target, with a dashed arrow back for the result; "
                      "an event from the unit that raises it to the one that receives it, with an open arrowhead. A bar is the "
                      "time a lifeline is busy with a step; it ends when a lifeline further out makes the next step. A step "
                      "shows its result; a note on a provider's lifeline shows the state of a connection whose contract has "
                      "states, with the name of the contract. An event is asynchronous: the call that raised it has returned. Steps in parallel and repeated steps are blocks; "
                      + ("an included scenario is one step, which `--expand` opens." if not expand else "an included scenario is a shaded block."), "",
                      "```mermaid", *lines, "```", "", *rows, "", *lifelines, ""])


def contract_topic(path: str) -> str:
    """The name of a contract: its file name, or the name of its folder for an index.md."""
    name = os.path.basename(path)
    return os.path.basename(os.path.dirname(path)) if name == "index.md" else name[:-3]


def states_page(project: Project, path: str, contract: dict) -> tuple:
    """(a name, text) of the page of the `## States` of a contract, as `unifold states` prints it: a state diagram and the table.
    The diagram shows every row: a row that stays in its state stands in the box of the state, a row
    that moves stands on the arrow, one arrow per pair of states, because Mermaid draws one label per loop."""
    states = contract["states"]
    out_dir = os.getcwd()                             # the page is printed, so its links start where the reader is
    topic = contract_topic(path)
    ids = {name: "s" + safe_id(name) for name in states["states"]}
    text = lambda t: label(str(t)).replace(":", "#58;").replace(";", "#59;")
    chart = ["stateDiagram-v2"] + [f'  state "{text(name)}" as {ids[name]}' for name in states["states"]]
    if states["start"] in ids:
        chart.append(f"  [*] --> {ids[states['start']]}")
    rows, arrows = ["| State | Part | Result | Next |", "|---|---|---|---|"], {}
    for row in states["rows"]:
        if row["state"] in ids and row["next"] in ids:
            result = row_result(row["result"])
            step = text(row["part"]) + ("" if result == "any" else f" · {text(result)}")
            if row["state"] == row["next"]:
                chart.append(f"  {ids[row['state']]}: {step}")
            else:
                arrows.setdefault((row["state"], row["next"]), []).append(step)
        rows.append(f"| {cell(row['state'])} | `{cell(row['part'])}` | {cell(plain(row['result']))} | {cell(row['next'])} |")
    chart += [f"  {ids[a]} --> {ids[b]}: {'<br/>'.join(steps)}" for (a, b), steps in arrows.items()]
    body = [f"# States: {topic}", "", f"The states of the contract {file_link(project, out_dir, topic, path)}: "
            "what a consumer can see of the connection, and the parts that move it from one state to the next. "
            "In the diagram, the parts inside a state's box leave the state as it is. "
            "A part that a state does not list must not be called in it. A failure that the table does not name "
            "leaves the state as it is.", "", "```mermaid", *chart, "```", "", *rows, ""]
    return topic, "\n".join(body)


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
        return f"uv run {script}"
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
    """The AGENTS.md of the root: where its documents and skills are, and the unifold block
    with the unit index. No project knowledge, only the way to it."""
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
    lines += ["", agents_block(project)]
    return "\n".join(lines) + "\n"


def generate(project: Project, force=()) -> dict:
    """Return {path: content} for every generated file of the project.

    `force` may contain "stubs": write skill stubs even where the folders do not exist
    yet. AGENTS.md is written at the root only, whole, with the unifold block.
    """
    out: dict = {}
    if not project.usable:
        return out
    for unit in project.units:
        folder = os.path.join(unit.path, "docs", "diagrams")
        kinds = diagram_kinds(project, unit)
        data = diagrams_for(project, unit)
        name = unit.name
        if "component" in data:
            chart, shown, _, shared = data["component"]
            intro = f"The units directly inside `{name}` and how they are connected. " + LEGEND
            after = (["", "Shared connections, not drawn:", "", *shared] if shared else []) \
                + ["", *unit_table(project, shown[1:], folder)] + wiring_table(unit)
            out[os.path.join(folder, "component.md")] = page(
                project, unit, kinds, "component", f"Component diagram: {name}", intro, chart, after)
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
               if (n == "AGENTS.md" and unit.parent is None)
               or (n == "README.md" and project.kind_of(os.path.join(unit.path, n)) == "file")]
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
    if project.root_unit is not None:
        out[os.path.join(project.root_unit.path, "AGENTS.md")] = agents_text(project, project.root_unit)
    return out


def write_generated(project: Project, force=()) -> dict:
    """Write the generated files; remove leftovers. Returns counts and refusals."""
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
        return {"summary": spec["summary"],
                "contract": contract_target(project, unit, spec["contract"])[0] or None,
                "parts": spec["parts"], "inherited-from": spec.get("inherited-from")}

    files = [rel(p) for p in managed_files(project, unit) if not generated_location(unit, p)]
    return {
        "name": unit.name, "path": unit.rel, "responsibility": unit.responsibility,
        "kind": unit.kind or None, "runs-as": unit.runs_as or None, "status": unit.status,
        "not": list(unit.nots),
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
        info["status"], info["kind"] and "kind " + info["kind"], info.get("runs-as") and "runs as " + info["runs-as"]) if x))
    for item in info.get("not") or []:
        line("not", item)
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
        extra += f"  (from {spec['inherited-from']})" if spec.get("inherited-from") else ""
        print(f"  {capability}: {spec['summary']}{extra}")
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
        extra += f"  (from {spec['inherited-from']})" if spec.get("inherited-from") else ""
        flags = [x for x in ("optional" if spec["optional"] else "",
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


def capability_data(project: Project, unit: Unit, name: str) -> dict:
    """Both ends of every connection of one capability or need."""
    def end(owner: Unit, entry: str, side: str, extra=None) -> dict:
        spec = (owner.capabilities if side == "capabilities" else owner.needs).get(entry, {})
        return {"unit": owner.rel, "status": owner.status, "side": side, "name": entry,
                "summary": spec.get("summary", ""),
                "contract": contract_target(project, owner, spec.get("contract"))[0] or None,
                "parts": spec.get("parts"),
                "optional": bool(spec.get("optional")) if side == "needs" else None, **(extra or {})}

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
        side = "capabilities" if item["side"] == "capabilities" else "needs"
        print(f"--- {named(item['unit'])}{mark(item['status'])} {side} '{item['name']}'"
              f"{note}: {item['summary']}")
        if item.get("contract"):
            print(f"    contract: {item['contract']}" + (f" (parts {', '.join(item['parts'])})" if item.get("parts") else ""))
        if item.get("optional"):
            print("    optional")
        print()


def citations(project: Project, wanted) -> list:
    """Links that cite a file for which `wanted(path)` is true; "context" for a link from a
    docs/explanation/context.md, which is how a unit takes something over from above."""
    out = []
    for unit in project.units:
        context = os.path.join(unit.path, "docs", "explanation", "context.md")
        for path in managed_files(project, unit):
            if generated_location(unit, path):
                continue
            doc = project.doc(path)
            base = os.path.dirname(path)
            for line, link in doc.links:
                if SCHEME.match(link) or link.startswith(("#", "/")):
                    continue
                target = os.path.normpath(os.path.join(base, split_link(link)[0]))
                if target == path or not wanted(target):
                    continue
                out.append({"file": project.rel(path), "line": line, "cites": project.rel(target),
                            "kind": "context" if path == context else "link"})
    return out


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
    cited = [row for row in citations(project, wanted) if row["kind"] == "context" or file]
    return {"unit": unit.rel, "status": unit.status, "capability": capability,
            "file": project.rel(file) if file else None,
            "dependents": sorted(dependents.values(), key=lambda d: (d["distance"], d["unit"])),
            "exposed-as": exposed, "outside": outside,
            "root-capabilities-affected": sorted(set(outside + reached)), "citations": cited}


TRACE_RULES = {
    "X1": ("info", "Every example of a contract of a capability of the unit is named by a test: a file below the unit, outside `docs/`, holds the example's id.",
           "Write the test, and put the id `<contract>#<part>/<case>` in its name or in a comment."),
    "X2": ("warn", "Every example id that a file below the unit names is an example of a contract of the unit.",
           "Rename the id after its example, or delete it."),
}
EXAMPLE_ID = re.compile(r"(?<![\w/])([A-Za-z0-9][\w.-]*)#([a-z0-9][a-z0-9_-]*)/([a-z0-9][a-z0-9_-]*)")


def context_items_of(project: Project, unit: Unit) -> list:
    """[{"heading", "link", "text"}] of docs/explanation/context.md: each `###` heading with its paragraphs."""
    path = os.path.join(unit.path, "docs", "explanation", "context.md")
    if project.kind_of(path) != "file":
        return []
    doc, items = project.doc(path), []
    for index, (number, level, text, _) in enumerate(doc.headings):
        if level != 3:
            continue
        end = next((n for n, lvl, _, _ in doc.headings[index + 1:] if lvl <= 3), len(doc.lines) + 1)
        link = INLINE_LINK.search(text)
        body = " ".join(line.strip() for line in doc.lines[number:end - 1] if line.strip())
        items.append({"heading": re.sub(r"\]\(.*$", "", text).lstrip("[").strip(), "path": project.rel(path),
                      "link": link.group(1).strip("<>") if link else None, "text": body})
    return items


def constants_of(project: Project, unit: Unit) -> list:
    """The rows of the nearest docs/references/constants.md at or above the unit: [{"name", "value", "file"}]."""
    current = unit
    while current is not None:
        path = os.path.join(current.path, "docs", "references", "constants.md")
        if project.kind_of(path) == "file":
            doc = project.doc(path)
            header, rows = first_table(doc.lines[doc.body_start:], doc.body_start + 1)
            columns = {c: i for i, c in enumerate(header or [])}
            if "name" in columns and "value" in columns:
                return [{"name": plain(cells[columns["name"]]), "value": plain(cells[columns["value"]])
                         if columns["value"] < len(cells) else "", "file": project.rel(path)}
                        for _, cells in rows if cells]
        current = current.parent
    return []


def part_data(part: dict) -> dict:
    return {"name": part["name"], "kind": part["kind"], "signature": part["signature"],
            "pre": part["texts"].get("Pre"), "result": part["texts"].get("Result"),
            "when": part["texts"].get("When"), "delivery": part["texts"].get("Delivery"),
            "errors": sorted(part["errors"]),
            "examples": [{"id": r["id"], "case": r["case"], "given": r["given"] or None,
                          "input": r["input"], "expected": r["expected"]} for r in part["rows"]]}


def brief_data(project: Project, unit: Unit) -> dict:
    """What an implementer of `unit` needs: the parts of its capabilities with their examples, the fakes
    of its needs, the states, the scenarios through it, its constants and its context items."""
    rel = project.rel

    def contract_block(owner: Unit, spec: dict, used):
        target = contract_target(project, owner, spec.get("contract"))[1]
        if not target or project.kind_of(target) != "file":
            return None
        contract = contract_of_path(project, target)
        parts = [part_data(p) for n, p in contract["parts"].items() if used is None or n in used]
        states = None
        if stateful(contract):
            states = {"start": contract["states"]["start"],
                      "rows": [{"state": r["state"], "part": r["part"], "result": row_result(r["result"]), "next": r["next"]}
                               for r in contract["states"]["rows"]]}
        return {"path": rel(target), "header": contract["header"], "parts": parts, "states": states,
                "qualities": [{"aspect": r["aspect"], "guarantee": r["guarantee"]} for r in contract["qualities"]["rows"]]
                if contract["qualities"] else [], "fake": contract["fake"], "fake-text": contract["fake-text"]}

    capabilities = []
    for name, spec in unit.capabilities.items():
        impl = unit.impl.get(name)
        capabilities.append({"name": name, "summary": spec["summary"],
                             "implemented-by": [f"{e.unit.rel}.{e.capability}" for e in impl.entries] if impl else [],
                             "contract": contract_block(unit, spec, None)})
    needs = []
    for name, spec in unit.needs.items():
        needs.append({"name": name, "summary": spec["summary"], "optional": spec["optional"],
                      "parts-used": spec["parts"], "contract": contract_block(unit, spec, spec["parts"]),
                      "provided-by": [{"unit": i["unit"].rel, "capability": i["capability"]} if i["where"] == "unit"
                                      else {"outside": True, "root-need": i["capability"]} for i in providers_of(unit, name)]})
    scenarios = []
    for scenario in scenarios_through(project, unit):
        hops = []
        for hop, result, error in scenario["hops"]:
            if result:
                call = result["part"] + (f"({result['input']})" if result.get("input") is not None else "")
                hops.append({"text": f"{result['caller']} -> {result['target']}.{call}: {result.get('result') or ''}",
                             "example": result.get("example"), "touches-unit": result["caller-unit"] is unit or result["target-unit"] is unit})
            else:
                hops.append({"text": hop, "example": None, "touches-unit": False, "error": error})
        scenarios.append({"unit": scenario["unit"].rel, "name": scenario["name"], "summary": scenario["spec"]["summary"],
                          "expect": scenario["spec"]["expect"], "hops": hops})
    readme = os.path.join(unit.path, "README.md")
    return {"unit": unit.rel, "name": unit.name, "responsibility": unit.responsibility, "kind": unit.kind or None,
            "runs-as": unit.runs_as or None, "status": unit.status, "not": list(unit.nots),
            "readme": rel(readme) if project.kind_of(readme) == "file" else None,
            "capabilities": capabilities, "needs": needs, "scenarios": scenarios,
            "constants": constants_of(project, unit), "context": context_items_of(project, unit)}


def print_brief(data: dict):
    print(f"brief for {named(data['unit'])}{mark(data['status'])}: {data['responsibility']}")
    for item in data["not"]:
        print(f"  not: {item}")
    if data["readme"]:
        print(f"  why: {data['readme']} (## Why)")

    def parts(block):
        for part in block["parts"]:
            print(f"    {part['name']} ({part['kind']})")
            for line in (part["signature"] or "").splitlines():
                print(f"        {line}")
            for key in ("pre", "result", "when", "delivery"):
                if part.get(key):
                    print(f"      {key}: {part[key]}")
            if part["errors"]:
                print(f"      errors: {', '.join(part['errors'])}")
            for example in part["examples"]:
                given = f" given {example['given']}" if example["given"] else ""
                print(f"      {example['id']}:{given} {example['input']} -> {example['expected']}")
        if block["states"]:
            print(f"    states: start {block['states']['start']}")
            for row in block["states"]["rows"]:
                print(f"      {row['state']} --{row['part']}" + (f" {row['result']}" if row["result"] != "any" else "")
                      + f"--> {row['next']}")

    print("\nimplement")
    for capability in data["capabilities"]:
        by = f" (implemented by {', '.join(capability['implemented-by'])})" if capability["implemented-by"] else ""
        print(f"  {capability['name']}: {capability['summary']}{by}")
        if capability["contract"]:
            header = ", ".join(f"{k.lower()} {v}" for k, v in capability["contract"]["header"].items() if k in ("Binding", "Version"))
            print(f"    contract {capability['contract']['path']}" + (f" ({header})" if header else ""))
            for row in capability["contract"]["qualities"]:
                print(f"    quality {row['aspect']}: {row['guarantee']}")
            parts(capability["contract"])
            if capability["contract"]["fake"] == "real":
                print("    fake: the real implementation; your users test against this code")
    print("\nfake, for your tests")
    for need in data["needs"]:
        optional = " (optional)" if need["optional"] else ""
        print(f"  {need['name']}: {need['summary']}{optional}")
        if need["contract"]:
            print(f"    contract {need['contract']['path']}" + (f" (parts {', '.join(need['parts-used'])})" if need["parts-used"] else ""))
            for line in (need["contract"]["fake-text"] or "").splitlines():
                if line.strip():
                    print(f"    fake: {line.strip()}")
            parts(need["contract"])
    if data["scenarios"]:
        print("\nscenarios through this unit")
    for scenario in data["scenarios"]:
        print(f"  {scenario['name']} ({named(scenario['unit'])}): {scenario['summary']}")
        for hop in scenario["hops"]:
            marker = "*" if hop["touches-unit"] else " "
            print(f"    {marker} {hop['text']}" + (f"  [{hop['example']}]" if hop.get("example") else ""))
        print(f"    expect: {scenario['expect']}")
    if data["constants"]:
        print("\nconstants (" + data["constants"][0]["file"] + ")")
        for row in data["constants"]:
            print(f"  {row['name']} = {row['value']}")
    if data["context"]:
        print("\ncontext (" + data["context"][0]["path"] + ")")
        for item in data["context"]:
            print(f"  {item['heading']}: {item['text']}")


def trace_files(project: Project, unit: Unit, patterns: list) -> list:
    """The files below `unit` that may hold tests: outside any docs/ folder, not ignored, not generated."""
    out = []
    for folder, subs, names in os.walk(unit.path):
        subs[:] = sorted(s for s in subs if not s.startswith(".") and s != "docs" and s not in NEVER_SCANNED
                         and not project.is_ignored(os.path.join(folder, s)) and not is_build_output(os.path.join(folder, s))
                         and not os.path.islink(os.path.join(folder, s)))
        for name in sorted(names):
            path = os.path.join(folder, name)
            if name.startswith(".") or name == MANIFEST or project.is_ignored(path) or os.path.islink(path):
                continue
            rel = project.rel(path)
            if patterns and not any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(name, p) for p in patterns):
                continue
            out.append(path)
    return out


def trace_data(project: Project, unit: Unit, patterns: list) -> dict:
    """Which example ids of the contracts of the unit's capabilities appear in which files, and which do not."""
    ids, topics = {}, {}
    for name, spec in unit.capabilities.items():
        target = contract_target(project, unit, spec.get("contract"))[1]
        if not target or project.kind_of(target) != "file":
            continue
        topics[contract_topic(target)] = project.rel(target)
        for part in contract_of_path(project, target)["parts"].values():
            for row in part["rows"]:
                ids[row["id"]] = {"id": row["id"], "contract": project.rel(target), "part": part["name"],
                                  "case": row["case"], "line": row["line"], "tests": []}
    unknown = []
    for path in trace_files(project, unit, patterns):
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        if "\0" in text[:4000]:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for match in EXAMPLE_ID.finditer(line):
                found = match.group(0)
                if found in ids:
                    if project.rel(path) not in ids[found]["tests"]:
                        ids[found]["tests"].append(project.rel(path))
                elif match.group(1) in topics:
                    unknown.append({"file": project.rel(path), "line": number, "id": found})
    findings = []
    for item in ids.values():
        if not item["tests"]:
            findings.append({"rule": "X1", "severity": "info", "file": item["contract"], "line": item["line"],
                             "message": f"example {item['id']} is named by no test", "fix": TRACE_RULES["X1"][2]})
    for item in unknown:
        findings.append({"rule": "X2", "severity": "warn", "file": item["file"], "line": item["line"],
                         "message": f"{item['id']} is not an example of a contract of this unit", "fix": TRACE_RULES["X2"][2]})
    return {"unit": unit.rel, "examples": list(ids.values()), "unknown": unknown, "findings": findings,
            "summary": {"examples": len(ids), "tested": sum(1 for i in ids.values() if i["tests"]),
                        "untested": sum(1 for i in ids.values() if not i["tests"]), "unknown": len(unknown)}}


def print_trace(data: dict):
    for item in data["examples"]:
        print(f"{'ok  ' if item['tests'] else 'none'} {item['id']}" + (f"  {', '.join(item['tests'])}" if item["tests"] else ""))
    for item in data["unknown"]:
        print(f"warn {item['file']}:{item['line']}: {item['id']} is not an example of a contract of this unit")
    s = data["summary"]
    print(f"{s['examples']} example(s): {s['tested']} named by a test, {s['untested']} by none; {s['unknown']} unknown id(s)")


def print_impact(data: dict):
    what = f"capability '{data['capability']}' of {data['unit']}" if data["capability"] else f"unit {data['unit']}"
    if data["file"]:
        what = f"{data['file']}, in {what}"
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
            print(f"  {row['file']}:{row['line']}")


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


# --------------------------------------------------------------- explorer

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
            if line.lstrip().startswith("<!--"):           # a comment, such as the mark of a generated file
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


def explorer_documents(project: Project, charts: dict, scenes: set, up: str) -> dict:
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
            return up + rel + ("#" + quote(anchor, safe="") if anchor else "")

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


EXPLORER = r"""<!doctype html>
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
--ink:#141c20;--navhead:#141c20;--paper:#fff;--unit:#e6f5f0;--unit-focus:#b5e6d9;--box-0:#f5f6f6;--box-1:#eceff0;--box-2:#e3e7e8;--frame:#c9d1d3;--accent:#0a7462;--accent-soft:#dcf2ec;--teal-hl:#bfeadf;--amber:#9a5b00;--amber-hl:#ffe1a3;
--sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI Variable Text","Segoe UI",Roboto,"Helvetica Neue","Noto Sans",Arial,sans-serif;
--slab:"Patua One",Rockwell,"Rockwell Nova","Roboto Slab",Georgia,serif;
--mono:ui-monospace,"SF Mono",SFMono-Regular,"JetBrains Mono","Cascadia Code",Menlo,Consolas,"Liberation Mono",monospace}
/* dark: chosen with the button (data-theme on <html>) or, without a choice, by the system; both blocks hold the same tokens */
:root[data-theme=light]{color-scheme:light}
:root[data-theme=dark]{color-scheme:dark;--bg:#0e1214;--fg:#e8eef0;--fg-2:#c3cfd3;--mute:#8e9ea5;--line:#222c31;--hi:#5fd3bb;--panel:#141a1d;--code:#25313a;--code-line:#3a4a54;--warn:#f2c56b;--warnbg:rgba(242,180,60,.2);
--ink:#e8eef0;--navhead:#fff;--paper:#12181b;--unit:#26363c;--unit-focus:#1d5348;--box-0:#151b1e;--box-1:#1a2226;--box-2:#20292e;--frame:#33414a;--accent:#5fd3bb;--accent-soft:#173430;--teal-hl:rgba(95,211,187,.28);--amber:#f2c56b;--amber-hl:rgba(242,180,60,.28)}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){color-scheme:dark;--bg:#0e1214;--fg:#e8eef0;--fg-2:#c3cfd3;--mute:#8e9ea5;--line:#222c31;--hi:#5fd3bb;--panel:#141a1d;--code:#25313a;--code-line:#3a4a54;--warn:#f2c56b;--warnbg:rgba(242,180,60,.2);
--ink:#e8eef0;--navhead:#fff;--paper:#12181b;--unit:#26363c;--unit-focus:#1d5348;--box-0:#151b1e;--box-1:#1a2226;--box-2:#20292e;--frame:#33414a;--accent:#5fd3bb;--accent-soft:#173430;--teal-hl:rgba(95,211,187,.28);--amber:#f2c56b;--amber-hl:rgba(242,180,60,.28)}}
*{box-sizing:border-box}body{margin:0;font:15px/1.6 var(--sans);background:var(--bg);color:var(--fg);display:flex;min-height:100vh;-webkit-font-smoothing:antialiased}
nav{width:260px;flex:none;border-right:1px solid var(--line);background:var(--panel);padding:16px 12px;overflow:auto;max-height:100vh;position:sticky;top:0}
nav ul{list-style:none;margin:0;padding-left:14px}nav>ul{padding-left:0}
nav a{display:block;margin:1px 0;padding:3px 8px;border-left:3px solid transparent;border-radius:0 3px 3px 0;color:var(--fg-2);text-decoration:none;cursor:pointer}
nav a:hover{background:var(--bg);color:var(--fg)}
nav a.on{background:var(--accent-soft);border-left-color:var(--accent);color:var(--fg);font-weight:700}
main{flex:1;min-width:0;padding:20px 32px 40px}
a{color:var(--hi);text-underline-offset:.2em;text-decoration-thickness:.07em}a:hover{text-decoration-thickness:.13em}
h1{font:400 60px/1.1 var(--slab);margin:.2em 0 .3em;overflow-wrap:anywhere}h2{font:400 44px/1.2 var(--slab);margin:1.2em 0 .4em}
.mute{color:var(--mute)}.crumbs{font-size:14px}.crumbs a,.go{cursor:pointer}
.badge{display:inline-block;font:600 12px/1.6 var(--sans);padding:0 8px;border-radius:3px;border:1px solid var(--line);color:var(--mute);vertical-align:middle}
.badge.planned,.badge.deprecated,.badge.proposed{color:var(--warn);background:var(--warnbg);border-color:transparent}
.tabs button{font:600 14px/1.2 var(--sans);padding:6px 14px;margin-right:6px;border:2px solid var(--frame);background:var(--bg);color:var(--fg);border-radius:3px;cursor:pointer}
.tabs button:hover{border-color:var(--fg)}
.tabs button.on{background:var(--fg);color:var(--bg);border-color:var(--fg);box-shadow:3px 3px 0 var(--teal-hl)}
#diagram{position:relative;border:1.5px solid var(--frame);border-radius:4px;padding:20px;margin:12px 0;overflow:auto;max-height:85vh;background:var(--paper)}#diagram.story{max-height:none}   /* a map scrolls inside its frame; a scenario takes the height it needs */
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
:is(#diagram,.figure) .labelBox{fill:var(--box-2)!important;stroke:var(--frame)!important}:is(#diagram,.figure) .loopLine{stroke:var(--frame)!important;fill:none!important}   /* the frame of a repeat or of parallel steps */
:is(#diagram,.figure) :is(.labelText,.labelText tspan,.loopText,.loopText tspan){font-family:var(--sans)!important;fill:var(--ink)!important;stroke:none!important}
#zoom,#play{float:right;font:600 13px/1.2 var(--sans);padding:5px 12px;margin-left:8px;border:2px solid var(--frame);background:var(--bg);color:var(--fg);border-radius:3px;cursor:pointer}#zoom:hover,#play:hover{border-color:var(--fg)}
/* the path of a scenario on the map: what the story uses is lit and numbered, the rest steps back; a dot runs the current step, its row and its connection in amber */
#diagram.trace .edgePaths path:not(.lit){opacity:.3}
#diagram.trace .node:not(.lit) :is(rect,polygon,path,circle,ellipse){stroke:var(--frame)!important;fill:var(--paper)!important;filter:none!important}
#diagram.trace .node:not(.lit) :is(.nodeLabel,.nodeLabel *),#diagram.trace .edgeLabel:not(.lit) :is(p,span){color:var(--frame)!important}
#strip{display:flex;gap:6px;margin:12px 0 -4px;overflow-x:auto;white-space:nowrap;font:14px/1.2 var(--sans);padding-bottom:4px;scrollbar-width:none}#strip::-webkit-scrollbar{display:none}   /* it still scrolls, and follows the run: a scrollbar would only flicker */
#strip .chip{display:inline-flex;align-items:center;gap:7px;padding:5px 11px;border:1.5px solid var(--frame);border-radius:999px;color:var(--fg-2);cursor:pointer;flex:none}
#strip .chip b{font-weight:700;color:var(--ink)}#strip .chip:hover{border-color:var(--fg)}#strip .chip.now{background:var(--amber-hl);border-color:var(--amber);color:var(--ink);transition:background .25s,border-color .25s}
#diagram.trace .edgePaths path.lit{stroke:var(--accent)!important;stroke-width:2.5px!important}#diagram.trace .edgePaths path.now{stroke:var(--amber)!important;stroke-width:4px!important}
#diagram.trace .node.lit :is(rect,polygon,path){stroke-width:3px!important}#diagram.trace .node.now :is(rect,polygon,path){stroke:var(--amber)!important;filter:drop-shadow(4px 4px 0 var(--amber-hl))}
#diagram.trace .cluster.now>rect{stroke:var(--amber)!important;stroke-width:3px!important}
#diagram text.steps{font:700 17px var(--sans);fill:var(--ink);stroke:var(--paper);stroke-width:5px;paint-order:stroke;stroke-linejoin:round}
#diagram .runner{position:absolute;left:-11px;top:-11px;width:22px;height:22px;border-radius:50%;background:var(--amber);border:2px solid var(--ink);pointer-events:none;will-change:transform}#diagram .runner.hollow{background:var(--paper);border:3.5px solid var(--amber)}   /* an HTML dot above the drawing: a moving SVG shape leaves traces in Safari */
#diagram.trace .edgeLabel.lit :is(p,span){color:var(--ink)!important}   /* the colour only: a bolder label would overflow the width Mermaid measured for it */
tr.now td{background:var(--amber-hl)}
.st{display:inline-block;width:9px;height:9px;border-radius:50%;margin-left:6px;vertical-align:baseline;border:1.5px dashed currentColor;opacity:.75}
.st.deprecated{border-style:solid;background:linear-gradient(to top right,transparent 44%,currentColor 44% 56%,transparent 56%)}
nav .legend{margin:14px 6px 0;font-size:12px;color:var(--mute)}nav .legend .st{margin:0 4px 0 0}
nav .navhead{margin:24px 8px 6px;font:400 22px/1.2 var(--slab);color:var(--navhead)}nav>.navhead:first-child{margin-top:0}nav .holder{margin:8px 8px 0;font-size:12px;color:var(--mute)}
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
.prose h3{font:700 34px/1.2 var(--sans);margin:1.2em 0 .3em}
.prose.contract h2:not(:first-child){margin-top:1.4em;padding-top:.6em;border-top:1px solid var(--line)}   /* a contract: its sections ruled off, each part named in code font */
.prose.contract h3{font:600 32px/1.2 var(--mono);margin:1.4em 0 .4em}.prose :is(h4,h5,h6){font:700 15px/1.35 var(--sans);margin:1.5em 0 .3em}
.prose :is(p,ul,ol,blockquote){margin:.85em 0}.prose :is(ul,ol){padding-left:1.6em}.prose li{margin:.3em 0}.prose li>:is(p,ul,ol){margin:.35em 0}
.prose p.field{margin:.5em 0}.prose li.task{list-style:none}.prose li.task>input{margin:0 .45em 0 -1.4em;accent-color:var(--accent)}
.prose pre{margin:1.1em 0;padding:12px 16px;background:var(--code);border-radius:4px;overflow-x:auto;font:13px/1.55 var(--mono);tab-size:2}.prose pre code{background:none;border:0;padding:0;font-size:inherit}
.prose blockquote{padding:2px 0 2px 16px;border-left:3px solid var(--frame);color:var(--fg-2)}.prose hr{border:0;border-top:1px solid var(--line);margin:2em 0}.prose img{max-width:100%;height:auto}
.prose .table{overflow-x:auto;margin:1.1em 0}.prose .table table{margin:0}.prose .table th{white-space:normal}.prose :is(th,td).c{text-align:center}.prose :is(th,td).r{text-align:right}
.anchor{margin-left:.35em;color:var(--mute);text-decoration:none;opacity:0;font-weight:400}:is(h2,h3,h4,h5,h6):hover>.anchor,.anchor:focus-visible{opacity:1}
.figure{margin:1.2em 0;padding:16px;border:1.5px solid var(--frame);border-radius:4px;background:var(--paper);overflow-x:auto}.figure svg{display:block;max-width:100%;height:auto;margin:0 auto}
:is(#diagram,.figure) .node circle.state-start{fill:var(--ink)!important}:is(#diagram,.figure) path.transition{stroke:var(--accent)!important;stroke-width:2px!important;fill:none!important}   /* a state diagram: its start, its steps */
#info .wide>*{max-width:none}#info .wide>h2:first-child{margin-top:1.4em}#info .wide li{margin:.3em 0}#doc[hidden],#bar[hidden],#diagram[hidden]{display:none}
#info h3{font:600 24px/1.3 var(--sans);text-transform:uppercase;letter-spacing:.05em;color:var(--mute);margin:1.2em 0 .2em}#info ul{margin:.3em 0;padding-left:1.4em}#info li{margin:.2em 0}#info li.on{font-weight:700}
@media(hover:none){.anchor{opacity:.45}}
@media(max-width:800px){.theme{position:absolute;top:12px;right:12px;margin:0}body{display:block}nav{width:auto;max-height:none;position:static}main{padding:16px}th,td{padding:6px 8px}
  nav .docs{display:none}.prose{font-size:15.5px}.prose pre{padding:10px 12px}.figure{padding:10px}
  h1{font-size:38px}h2{font-size:30px}.prose h3{font-size:24px}.prose.contract h3{font-size:22px}#info h3{font-size:18px}}   /* the large headings would fill a phone */
</style></head><body>
<nav id="tree"></nav>
<main>
<button class="theme" type="button" aria-label="Dark theme" aria-pressed="false" title="Light or dark" hidden><svg class="sun" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 13.3A8.5 8.5 0 1 1 10.7 3.5a6.6 6.6 0 0 0 9.8 9.8z"/></svg></button>
<div class="crumbs mute" id="crumbs"></div>
<h1 id="title"></h1><p id="summary"></p><p class="mute" id="meta"></p><dl id="facts" hidden></dl>
<article class="prose" id="doc" hidden></article>
<div class="tabs" id="bar"><button id="zoom" hidden></button><button id="play" hidden></button><span id="tabs"></span></div>
<div id="strip" hidden></div>
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
const file = p => model.up + p.split("/").map(encodeURIComponent).join("/");
const badge = s => s && s !== "active" && s !== "accepted" ? ` <span class="badge ${esc(s.split(" ")[0])}">${esc(s)}</span>` : "";
const pick = (p, t) => `<a class="go" data-path="${esc(p)}">${esc(t ?? (p === "." ? model.name : p))}</a>` + badge(byPath[p] && byPath[p].status);
const docs = model.docs || {}, KINDS = {readme: "README", tutorials: "Tutorials", contracts: "Contracts", references: "Reference", explanation: "Explanation", decisions: "Decisions", skills: "Skills", other: "Other"};
const enc = s => encodeURIComponent(s).replace(/%(2F|40|3A)/g, m => decodeURIComponent(m));   // a route stays readable: unit@doc:docs/references/x.md
const hashOf = (route, anchor) => "#" + enc(route) + (anchor ? "#" + encodeURIComponent(anchor) : "");
const pageOf = p => { const d = docs[p]; return d && d.unit + "@doc:" + (d.unit === "." ? p : p.slice(d.unit.length + 1)); };   // the page of a document
const routeOf = p => docs[p] && docs[p].kind === "readme" ? docs[p].unit : pageOf(p);   // a link to a README opens its unit
const href = v => { const [p, a] = v.split("#"), r = routeOf(p); return r ? hashOf(r, a) : file(p) + (a ? "#" + encodeURIComponent(a) : ""); };   // a document opens here, any other file as it is
const ref = v => v ? (/^[a-z][a-z0-9+.-]*:/i.test(v) ? `<a href="${esc(v)}">${esc(v)}</a>` : `<a href="${esc(href(v))}">${esc(v)}</a>`) : "";
const part = (contract, name) => { const dir = contract.endsWith("/index.md") && contract.slice(0, -8) + name + ".md";   // a part: its file in a folder contract, its heading in a file
  return `<a href="${esc(href(dir && docs[dir] ? dir : contract + "#" + name))}">${esc(name)}</a>`; };
const title = p => docs[p].title || esc(p.split("/").pop().replace(/\.md$/, ""));
const uses = {};                      // contract path -> part -> [[scenario, step]]: the steps of the stories that use the part
for (const s of (model.scenarios || [])) s.hops.forEach((x, i) => { if (x.contract) ((uses[x.contract] ||= {})[x.part] ||= []).push([s, i + 1]); });
const partsOf = {};                   // contract path -> its parts with their kinds, from the manifests that name it
for (const u of units) for (const e of Object.values(u.capabilities).concat(Object.values(u.needs))) if (e.contract && e["contract-parts"]) partsOf[e.contract] = e["contract-parts"];
const usedIn = (contract, name) => {  // the stories that use a part, with their steps; or the word that none does
  const by = new Map(); for (const [s, n] of (uses[contract] || {})[name] || []) by.set(s, (by.get(s) || []).concat(n));
  return by.size ? [...by].map(([s, ns]) => sceneLink(s) + ` <span class="mute">step ${ns.join(", ")}</span>`).join("<br>") : `<span class="mute">no scenario uses this part</span>`; };
const plain = h => { const t = document.createElement("template"); t.innerHTML = h; return t.content.textContent; };
const docLink = (p, on) => on ? `<li class="on">${title(p)}</li>` : `<li><a href="${esc(href(p))}">${title(p)}</a>` + (docs[p].kind === "decisions" ? badge(docs[p].status || "no status") : "")
  + (docs[p].kind === "skills" && docs[p].summary ? ": " + esc(docs[p].summary) : "") + "</li>";
function groups(u){                  // the documents of a unit by kind, in the order of AGENTS.md: learn, look up, understand, decide, do
  const of = {tutorials: u.documents.tutorials, contracts: u.documents.references.filter(p => partsOf[p]), references: u.documents.references.filter(p => !partsOf[p]),   // a reference that a manifest names is a contract
    explanation: u.documents.explanation, decisions: u.decisions.map(d => d.path),
    skills: u.skills.map(s => s.path), other: Object.keys(docs).filter(p => docs[p].unit === u.path && docs[p].kind === "other")};
  return Object.entries(KINDS).map(([k, label]) => [k, label, (of[k] || []).filter(p => docs[p])]).filter(g => g[2].length);}
function anchors(box, route){        // the link beside a heading; the ids come with the document
  for (const h of box.querySelectorAll(":is(h2,h3,h4,h5,h6)[id^='md-']")) h.insertAdjacentHTML("beforeend", ` <a class="anchor" href="${esc(hashOf(route, h.id.slice(3)))}" aria-label="Link to this section">#</a>`);}
function lifelines(box){             // Mermaid draws a lifeline 2000 high and corrects it only when it repeats the boxes at the bottom, which a short scenario does not
  const svg = box.querySelector("svg"); if (!svg || svg.querySelector(".actor-bottom")) return; const v = svg.viewBox.baseVal;
  for (const l of svg.querySelectorAll(".actor-line")) l.setAttribute("y2", v.y + v.height);}
let figure = 0;
async function figures(box){         // the Mermaid blocks of a document, drawn like the map; without Mermaid they stay source
  if (!mermaid) return;
  for (const pre of [...box.querySelectorAll("pre.mermaid")]) {
    try { const {svg} = await mermaid.render("f" + ++figure, pre.textContent); if (!pre.isConnected) return;
      const f = document.createElement("div"); f.className = "figure"; f.innerHTML = svg; lifelines(f); pre.replaceWith(f);
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
  const sv = k.startsWith("scenario:") ? k.slice(9).split(":") : [], s = sv.length ? scene(p, sv[0]) : null, d = k.startsWith("doc:") ? (p === "." ? "" : p + "/") + k.slice(4) : null;
  state = {path: byPath[p] ? p : ".", kind: s || d || !k ? null : k, scenario: s, view: sv[1] || null, doc: d && docs[d] ? d : null, anchor: cut < 0 ? "" : decode(raw.slice(cut + 1))};}
function go(path, kind){location.hash = enc(path + (kind ? "@" + kind : ""));}
function tree(path){const u = byPath[path]; const kids = u.children.map(c => tree(c.path)).join("");
  return `<li><a data-path="${esc(path)}" class="go${path === state.path && !state.scenario ? " on" : ""}">${esc(u.name)}${u.status !== "active" ? `<span class="st ${esc(u.status)}" title="${esc(u.status)}"></span>` : ""}</a>${kids ? "<ul>" + kids + "</ul>" : ""}</li>`;}
const named = p => p === "." ? model.name : p;
const pin = (p, t) => { const st = byPath[p].status; return `<span class="nw"><a class="go" data-path="${esc(p)}">${esc(t ?? named(p))}</a>` + (st !== "active" ? `<span class="st ${esc(st)}" title="${esc(st)}"></span>` : "") + "</span>"; };   // the status as in the tree
function docTree(u){                 // the documents of the unit shown, beside the map
  const g = groups(u); if (!g.length) return "";
  return `<div class="docs"><p class="navhead">Documents</p>` + g.map(([k, label, paths]) => `<p class="holder">${label}</p><ul>`
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
  run++; el("play").hidden = true; el("strip").hidden = true;
  const kind = kinds.includes(state.kind) ? state.kind : (kinds.includes("component") ? "component" : kinds[0]);
  el("tree").innerHTML = "<p class='navhead'>Units</p><ul>" + tree(".") + "</ul>" + sceneTree() + docTree(u) + (legend ? `<p class="legend">${legend}</p>` : "");
  const chain = []; for (let p = u.parent; p; p = byPath[p.path].parent) chain.unshift(p.path);
  if (state.doc) return reading(state.doc, chain);
  map(true);
  if (state.scenario) return story(state.scenario, chain);
  el("facts").hidden = true; el("hint").textContent = "Click a box to open that unit, a capability or need to find it in the tables. An arrow points from a need to its provider. A dashed border marks a unit that is planned.";
  document.title = u.name + " · " + model.name;
  el("crumbs").innerHTML = chain.map(p => `<a class="go" data-path="${esc(p)}">${esc(byPath[p].name)}</a>`).concat(esc(u.name)).join(" / ");
  const readme = u.readme && docs[u.readme];   // the README: its first paragraph on top (the responsibility is in the boxes of the diagram), its Why above the tables
  el("title").innerHTML = esc(u.name) + badge(u.status); el("summary").innerHTML = readme && readme.intro || esc(u.responsibility);
  el("meta").innerHTML = [u.kind].filter(Boolean).map(esc)
    .concat([`<a href="${esc(file(u.manifest))}">manifest</a>`], u.readme ? [`<a href="${esc(readme ? hashOf(pageOf(u.readme)) : file(u.readme))}">README</a>`] : [],
            u.agents ? [`<a href="${esc(href(u.agents))}">AGENTS.md</a>`] : []).join(" · ");
  el("doc").hidden = true;
  el("tabs").innerHTML = kinds.map(k => `<button data-kind="${k}" class="${k === kind ? "on" : ""}">${k}</button>`).join("");
  let html = readme && readme.why ? `<div class="prose wide">${readme.why}</div>` : "";   // Why, then what the unit leaves out, as sections of the same rank
  const p = Object.entries(u.capabilities), n = Object.entries(u.needs);
  if (u.not && u.not.length) html += `<div class="prose wide"><h2 id="out-of-scope">Out of scope</h2><ul>` + u.not.map(n => "<li>" + code(n) + "</li>").join("") + "</ul></div>";
  if (p.length) html += "<h2>Capabilities</h2><table><tr><th>Capability</th><th>Summary</th><th>Contract</th><th>Used by</th></tr>"
    + p.map(([k, v]) => `<tr id="capability:${esc(k)}"><td><code>${esc(k)}</code></td><td>${esc(v.summary)}</td><td>${ref(v.contract)}${v.parts && v.contract ? " <span class='mute'>(" + v.parts.map(n => part(v.contract, n)).join(", ") + ")</span>" : ""}</td><td>${who(v["used-by"], "need")}</td></tr>`).join("") + "</table>";
  if (n.length) html += "<h2>Needs</h2><table><tr><th>Need</th><th>Summary</th><th>Contract</th><th>Provided by</th></tr>"
    + n.map(([k, v]) => `<tr id="need:${esc(k)}"><td><code>${esc(k)}</code>${v.optional ? " <span class='mute'>optional</span>" : ""}${v.platform ? " <span class='mute'>platform</span>" : ""}</td><td>${esc(v.summary)}</td><td>${ref(v.contract)}${v.parts && v.contract ? " <span class='mute'>(" + v.parts.map(n => part(v.contract, n)).join(", ") + ")</span>" : ""}</td><td>${who(v["provided-by"], "capability")}</td></tr>`).join("") + "</table>";
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
  el("zoom").hidden = true; el("diagram").classList.remove("story");
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
function story(s, chain){             // a scenario: what it is and expects, its sequence diagram or its path on the map, its steps and its lifelines
  const h = byPath[s.unit], d = s.diagram, lives = Object.values(d.lifelines);
  const frame = frameOf(s), mapKind = frame && ["architecture", "component"].find(k => byPath[frame].diagrams[k]), view = state.view === "map" && mapKind ? "map" : "sequence";
  const life = (text, unit, side) => unit ? pin(unit, text) : `<a class="go" data-path="${esc(s.unit)}" data-row="${side}:${esc(text)}"><code>${esc(text)}</code></a>`;
  document.title = s.name + " · " + model.name;
  el("crumbs").innerHTML = chain.concat(s.unit).map(p => `<a class="go" data-path="${esc(p)}">${esc(byPath[p].name)}</a>`).concat(esc(s.name)).join(" / ");
  el("title").innerHTML = esc(s.name); el("summary").textContent = s.summary;
  el("meta").innerHTML = ["scenario of " + pin(s.unit), s.hops.length + (s.hops.length === 1 ? " step" : " steps"), lives.length + " lifelines"]
    .concat(s.page ? [`<a href="${esc(file(s.page))}">Markdown</a>`] : [], [`<a href="${esc(file(h.manifest))}">manifest</a>`]).join(" · ");
  el("doc").hidden = true;
  el("facts").innerHTML = (s.source ? `<dt>Source</dt><dd>${code(s.source)}</dd>` : "") + `<dt>Expect</dt><dd>${code(s.expect)}</dd>`; el("facts").hidden = false;
  el("tabs").innerHTML = `<button data-view="sequence" class="${view === "sequence" ? "on" : ""}">sequence</button>` + (mapKind ? `<button data-view="map" class="${view === "map" ? "on" : ""}">map</button>` : "");
  el("shared").innerHTML = ""; el("zoom").hidden = true; el("diagram").classList.toggle("story", view === "sequence"); el("diagram").classList.toggle("trace", view === "map");
  el("strip").hidden = view !== "map"; el("strip").innerHTML = view === "map" ? s.hops.map((x, i) => `<span class="chip" data-step="${i + 1}"><b>${i + 1}</b>${esc(x.part || x.unresolved)}</span>`).join("") : "";
  el("hint").textContent = view === "map" ? `The ${mapKind} diagram of ${named(frame)} with the path of this scenario: the boxes and connections its steps use are lit and carry the numbers of the steps, the rest steps back. A dot runs every step in the direction of the data, in order; a hollow dot brings the result of a query back. Click a number or a lit connection to find the step in the table, a box to open its unit.` : `An arrow is one step, numbered in order, along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one. The note at the end is what the scenario expects. Click a step to find it in the table, a lifeline to open its unit, or a capability or need of ${named(s.unit)} to find it in its tables. A dashed border marks a unit that is planned.`;
  let html = "<h2>Steps</h2><table><tr><th>#</th><th>Caller</th><th>Target</th><th>Part</th><th>Contract</th><th>Wiring</th></tr>" + s.hops.map((x, i) => x.unresolved
    ? `<tr id="step:${i + 1}"><td>${i + 1}</td><td colspan="5"><code>${esc(x.unresolved)}</code> <span class="badge planned">does not resolve</span> ${esc(x.error)}</td></tr>`
    : `<tr id="step:${i + 1}"><td>${i + 1}</td><td>${life(x.caller, x["caller-unit"], "capability")}</td><td>${life(x.target, x["target-unit"], "need")}</td><td><a href="${esc(href(x["part-file"] && x["part-file"] !== x.contract ? x["part-file"] : x.contract + "#" + x.part))}"><code>${esc(x.part)}</code></a>${x["part-kind"] ? " <span class='mute'>" + esc(x["part-kind"]) + "</span>" : ""}</td><td>${ref(x.contract)}</td><td>${x.via.map(v => `<span class="nw"><code>${esc(v.key)}</code> <span class="mute">in</span> ${pin(v.unit)}</span>`).join("<br>") || "–"}</td></tr>`).join("") + "</table>";
  html += "<h2>Lifelines</h2><table><tr><th>Lifeline</th><th>Kind</th><th>Responsibility</th><th>Steps</th></tr>" + lives.map(l => {
    const u = l.side ? null : byPath[l.unit], e = l.side ? h[l.side === "capability" ? "capabilities" : "needs"][l.entry] : null;
    const steps = (k, word) => { const at = s.hops.flatMap((x, i) => x[k] === l.name ? [i + 1] : []); return at.length ? word + " " + at.join(", ") : ""; };
    return `<tr><td>${life(l.name, u && l.unit, l.side)}</td><td>${u ? esc([u.kind, u["runs-as"]].filter(Boolean).join(", ")) : esc(l.side + " of " + named(s.unit))}</td><td class="text">${esc(u ? u.responsibility : e && e.summary)}</td><td>${[steps("caller", "calls in"), steps("target", "called in")].filter(Boolean).join("<br>")}</td></tr>`;}).join("") + "</table>";
  const more = scenes.filter(o => o.unit === s.unit && o !== s);
  if (more.length) html += `<h2>More scenarios of ${esc(named(s.unit))}</h2><ul>` + more.map(o => `<li>${sceneLink(o)}: ${esc(o.summary)}</li>`).join("") + "</ul>";
  el("info").innerHTML = html;
  if (view === "map") return trace(s, frame, byPath[frame].diagrams[mapKind]);
  return draw(d.source, () => {
    for (const m of el("diagram").querySelectorAll('marker[id$="-filled-head"]')) m.setAttribute("markerUnits", "userSpaceOnUse");   // the head of an event: Mermaid scales it with the stroke, which is thicker here; the other heads are fixed
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
const NS = "http://www.w3.org/2000/svg";
let run = 0;                          // the run of a story on the map; a newer page or view ends the older run
function frameOf(s){                  // the deepest unit whose map holds every unit of a scenario: the common ancestor of the units its hops name, with a diagram of its children
  const paths = s.hops.flatMap(x => [x["caller-unit"], x["target-unit"]].filter(Boolean));
  let f = paths.length ? paths.reduce((a, b) => { const A = a.split("/"), B = b.split("/"); let i = 0; while (i < A.length && A[i] === B[i]) i++; return i && a !== "." ? A.slice(0, i).join("/") : "."; }) : s.unit;
  while (!byPath[f] && f !== ".") f = f.includes("/") ? f.slice(0, f.lastIndexOf("/")) : ".";   // the common folder may be plain: it belongs to the nearest unit above it
  while (byPath[f] && !byPath[f].diagrams.component && byPath[f].parent) f = byPath[f].parent.path;
  return byPath[f] && byPath[f].diagrams.component ? f : null;
}
function trace(s, f, m){              // the map of `f` with the path of the scenario on it: lit, numbered, and run by a dot
  const drawnAs = r => {              // the boxes a unit is drawn as: itself or the units inside it, else the nearest box it lies in
    const inside = Object.keys(m.nodes).filter(id => m.nodes[id] === r || m.nodes[id].startsWith(r + "/"));
    for (let p = inside.length ? null : byPath[r] && byPath[r].parent; p; p = byPath[p.path].parent) {
      const up = Object.keys(m.nodes).filter(id => m.nodes[id] === p.path); if (up.length) return up; }
    return inside; };
  const sideIds = (unit, kind, name) => Object.keys(m.sides).filter(id => m.sides[id][0] === unit && m.sides[id][1] === kind && m.sides[id][2] === name);
  const within = r => r === f || r.startsWith(f === "." ? "" : f + "/");
  const fName = byPath[f].name, fParent = byPath[f].parent && byPath[f].parent.path;
  const endOf = (x, role) => {        // the boxes an end of a step is drawn as: a unit inside the frame, a capability or need of the frame, or the side of the frame the step crosses
    const r = x[role + "-unit"];
    if (r && within(r)) return drawnAs(r);
    if (!r && f === s.unit) return sideIds(f, x[role + "-side"], x[role]);
    if (role === (x.direction === "raise" ? "caller" : "target")) { const v = x.via.find(v => v.unit === fParent && v.key.startsWith(fName + ".")); return v ? sideIds(f, "need", v.key.slice(fName.length + 1)) : []; }
    const v = x.via.find(v => v.unit === f && !v.key.includes(".") && byPath[f].capabilities[v.key]); return v ? sideIds(f, "capability", v.key) : []; };
  return draw(m.source, () => {
    shade(); zoom(true);
    const box = el("diagram"), paths = [...box.querySelectorAll("g.edgePaths path")], parts = [...box.querySelectorAll(".node, .cluster")];
    const between = (a, b) => paths.filter(p => new RegExp(`-L_${a}_${b}_\\d+$`).test(p.id));
    const steps = s.hops.map((x, i) => {   // every step: the connections it runs along, the boxes at its ends, and whether its data runs against the arrow
      const from = x.unresolved ? [] : endOf(x, "caller"), to = x.unresolved ? [] : endOf(x, "target");
      let edges = from.flatMap(a => to.flatMap(b => between(a, b))), back = false;
      if (!edges.length) { edges = from.flatMap(a => to.flatMap(b => between(b, a))); back = true; }
      const ends = from.concat(to).flatMap(id => parts.filter(n => new RegExp(`-flowchart-${id}-\\d+$|-${id}$`).test(n.id)));
      return {n: i + 1, edges, ends, reverse: back, query: x["part-kind"] === "query"};
    });
    const numbers = new Map();        // a lit connection -> the numbers of the steps on it
    for (const st of steps) {
      for (const n of st.ends) n.classList.add("lit");
      for (const p of st.edges) { numbers.set(p, (numbers.get(p) || []).concat(st.n));
        const l = box.querySelector(`.edgeLabels .label[data-id="${p.id.slice(p.id.indexOf("-L_") + 1)}"]`); if (l) l.closest(".edgeLabel").classList.add("lit"); }
    }
    for (const [p, ns] of numbers) {   // the numbers above the middle of the connection, clear of its label
      const at = p.getPointAtLength(p.getTotalLength() / 2), t = document.createElementNS(NS, "text");
      t.setAttribute("class", "steps pick"); t.setAttribute("x", at.x); t.setAttribute("y", at.y - 16); t.setAttribute("text-anchor", "middle"); t.textContent = ns.join(" · ");
      p.classList.add("lit", "pick"); p.parentNode.appendChild(t);
      for (const e of [p, t]) e.addEventListener("click", ev => {ev.stopPropagation(); flash("step:" + ns[0]);});
    }
    const legs = steps.flatMap(st => st.edges.length   // a step runs each of its connections; a query comes back hollow; a step not on the map is only marked
      ? st.edges.flatMap(p => st.query ? [{st, p, back: st.reverse}, {st, p, back: !st.reverse, hollow: true}] : [{st, p, back: st.reverse}]) : [{st}]);
    if (!legs.length || !paths.length) return;
    const dot = document.createElement("div"); dot.className = "runner"; dot.hidden = true; box.appendChild(dot);
    const mine = ++run, button = el("play"); let k = 0, since = null, playing = true;
    const mark = st => {              // the current step: its chip in the strip, its row in the table, its connections and boxes
      for (const e of document.querySelectorAll(".now")) e.classList.remove("now");
      const r = document.getElementById("step:" + st.n); if (r) r.classList.add("now"); for (const e of st.edges.concat(st.ends)) e.classList.add("now");
      const strip = el("strip"), c = strip.querySelector(`.chip[data-step="${st.n}"]`); if (!c) return; c.classList.add("now");
      if (strip.scrollWidth > strip.clientWidth) strip.scrollTo({left: c.offsetLeft - strip.clientWidth / 2 + c.offsetWidth / 2, behavior: "smooth"}); };
    let map = null;                   // how the drawing maps into the box, with its scale: found once per leg and after a resize, not every frame
    addEventListener("resize", () => map = null);
    const place = (leg, e) => {       // the dot at a point of the leg, from 0 to 1, as big as the drawing is
      if (!leg.p) { dot.hidden = true; return; }
      if (!map || map.p !== leg.p) { const m = leg.p.getScreenCTM(), r = box.getBoundingClientRect();
        map = {p: leg.p, m, l: leg.p.getTotalLength(), s: Math.hypot(m.a, m.b), x: m.e - r.left - box.clientLeft + box.scrollLeft, y: m.f - r.top - box.clientTop + box.scrollTop}; }
      const q = leg.p.getPointAtLength(map.l * (leg.back ? 1 - e : e)), m = map.m;
      dot.style.transform = `translate3d(${m.a * q.x + m.c * q.y + map.x}px, ${m.b * q.x + m.d * q.y + map.y}px, 0) scale(${map.s})`;
      dot.classList.toggle("hollow", !!leg.hollow); dot.hidden = false; };
    function tick(now){
      if (mine !== run || !box.isConnected || !playing) return;
      const leg = legs[k], D = leg.p ? 1375 : 600, R = k + 1 === legs.length ? 1600 : 250;   // the time of a leg and the rest after it, longer at the end of the story
      if (since === null) { since = now; mark(leg.st); }
      const f = Math.min(1, (now - since) / D), e = f < .5 ? 2 * f * f : 1 - (2 - 2 * f) ** 2 / 2;
      place(leg, e);
      if (now - since >= D + R) { k = (k + 1) % legs.length; since = null; }
      requestAnimationFrame(tick);
    }
    button.hidden = false; button.textContent = "Pause";
    button.onclick = () => { playing = !playing; button.textContent = playing ? "Pause" : "Play"; if (playing) { since = null; requestAnimationFrame(tick); } };
    for (const chip of el("strip").querySelectorAll(".chip")) chip.onclick = () => {   // a chip jumps the run to its step
      const at = legs.findIndex(l => l.st.n === +chip.dataset.step); if (at < 0) return;
      k = at; since = null; if (!playing) { mark(legs[k].st); place(legs[k], 0); } };
    requestAnimationFrame(tick);
  });
}
function reading(p, chain){           // a document: where it belongs, its front matter, its text, and the documents beside it
  const d = docs[p], u = byPath[d.unit], whole = d.contract && docs[d.contract], agreed = partsOf[p] || (whole && partsOf[d.contract]);   // a contract, or a part of one
  const kind = agreed ? "contracts" : d.kind, label = KINDS[kind] || "Documents";
  document.title = plain(title(p)) + " · " + model.name;
  el("crumbs").innerHTML = chain.concat(d.unit).map(c => `<a class="go" data-path="${esc(c)}">${esc(byPath[c].name)}</a>`)
    .concat(`<a class="go" data-path="${esc(d.unit)}" data-row="docs:${esc(kind)}">${label}</a>`, whole ? [`<a href="${esc(href(d.contract))}">${title(d.contract)}</a>`] : [], title(p)).join(" / ");
  el("title").innerHTML = title(p) + badge(d.status); el("summary").textContent = d.summary || "";
  el("meta").innerHTML = [(whole ? "Part of a contract" : label) + " of " + pin(d.unit), `<a href="${esc(file(p))}">Markdown</a>`].join(" · ");
  const mine = whole && partsOf[d.contract] && partsOf[d.contract].find(x => d.contract.slice(0, -8) + x.name + ".md" === p);   // a part of a folder contract: which stories use it
  el("facts").innerHTML = (d.facts || []).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join("") + (mine ? `<dt>Used in</dt><dd>${usedIn(d.contract, mine.name)}</dd>` : "");
  el("facts").hidden = !d.facts && !mine;
  const parts = partsOf[p], table = parts ? "<h2>Parts in the scenarios</h2><div class='table'><table><tr><th>Part</th><th>Kind</th><th>Used in</th></tr>" + parts.map(x =>
    `<tr><td>${part(p, x.name)}</td><td>${esc(x.kind || "")}</td><td>${x.kind === "type" ? "" : usedIn(p, x.name)}</td></tr>`).join("") + "</table></div>" : "";   // a contract: its parts and the stories that use them
  map(false); el("doc").className = "prose" + (agreed ? " contract" : ""); el("doc").hidden = false; el("doc").innerHTML = d.html;
  if (table) { const at = el("doc").querySelector("#md-parts"); if (at) at.insertAdjacentHTML("beforebegin", table); else el("doc").insertAdjacentHTML("beforeend", table); }   // after the description, before the parts
  anchors(el("doc"), pageOf(p));
  const g = groups(u).find(x => x[0] === kind), near = whole ? whole.parts : g ? g[2] : [];
  el("info").innerHTML = near.length > 1 ? `<h2>${whole ? "Parts of " + title(d.contract) : label + " of " + esc(u.name)}</h2><ul>` + near.map(o => docLink(o, o === p)).join("") + "</ul>" : "";
  return figures(el("doc"));
}
function flash(id){const target = document.getElementById(id); if (!target) return;   // a row of the tables: in view, lit up for a moment
  target.scrollIntoView({behavior: "smooth", block: "center"}); target.classList.remove("flash"); void target.offsetWidth; target.classList.add("flash");}
let drawn = 0;
async function draw(source, wire){   // Mermaid source into the diagram box; `wire` makes its boxes clickable
  el("zoom").hidden = true; el("play").hidden = true;
  if (!mermaid) {
    if (mermaidError) el("diagram").innerHTML = "<p>The diagram renderer (Mermaid) could not be loaded" + (MERMAID.url ? " from " + esc(MERMAID.url) : "")
      + ". The tables below are complete without it. To embed the renderer in this page: <code>unifold explore --mermaid path/to/mermaid.min.js</code>.</p><details><summary>Diagram source</summary><pre>" + esc(source) + "</pre></details>";
    return;
  }
  const mine = ++drawn;
  try {
    const {svg} = await mermaid.render("g" + Date.now(), source);
    if (mine !== drawn) return;          // a newer page is on its way
    el("diagram").innerHTML = svg; lifelines(el("diagram")); wire();
  } catch (err) { el("diagram").innerHTML = "<p>The diagram could not be drawn: " + esc(err) + "</p><pre>" + esc(source) + "</pre>"; }
}
document.addEventListener("click", ev => {
  const a = ev.target.closest(".go");
  if (a) { row = a.dataset.row || null;   // a capability or need of the holder of a scenario: its row in the tables
    if (a.dataset.scenario) go(a.dataset.path, "scenario:" + a.dataset.scenario);
    else if (row && a.dataset.path === state.path && !state.scenario && !state.doc) render(); else go(a.dataset.path);
    return; }
  const b = ev.target.closest("button[data-kind]"); if (b) go(state.path, b.dataset.kind);
  const v = ev.target.closest("button[data-view]"); if (v && state.scenario) go(state.path, "scenario:" + state.scenario.name + (v.dataset.view === "map" ? ":map" : ""));
  if (ev.target.id === "zoom") { fit = !fitted; zoom(); dispatchEvent(new Event("resize")); }   // a running story maps its dot anew
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


def open_in_browser(path: str) -> bool:
    """Open a local file in the browser of the system. False when no browser could be started."""
    try:
        return bool(webbrowser.open("file://" + quote(os.path.abspath(path))))
    except Exception:                                 # pragma: no cover
        return False


def explorer_default(project: Project) -> str:
    """Where `explore` writes without `-o`: outside the repository, in the temporary folder of the
    system, one file per project name. The explorer is a view of the map, not a file of it."""
    name = re.sub(r"[^\w.-]+", "-", project.root_unit.name) or "project"
    return os.path.join(tempfile.gettempdir(), "unifold", name, "explorer.html")


def build_explorer(project: Project, out: str, mermaid: str) -> str:
    """Write the explorer: one HTML page. `mermaid` is a URL, or a local single-file build to embed."""
    if os.path.isdir(out):
        out = os.path.join(out, "explorer.html")
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
    out_dir = os.path.dirname(os.path.abspath(out))
    units = []
    sides = {side_id(u, "p", c): [u.rel, "capability", c] for u in project.units for c in u.capabilities}
    sides.update({side_id(u, "n", n): [u.rel, "need", n] for u in project.units for n in u.needs})
    for unit in project.units:
        info = describe(project, unit)
        if unit is project.root_unit:            # the skills `init --agents` installs are the tool's
            info["skills"] = [s for s in info["skills"] if s["name"] not in SKILLS]
        for side in ("capabilities", "needs"):   # the parts of each contract, with their kinds: the page of a contract lists them with the stories that use them
            for name, entry in info[side].items():
                target = contract_target(project, unit, (unit.capabilities if side == "capabilities" else unit.needs)[name].get("contract"))[1]
                entry["contract-parts"] = [{"name": n, "kind": part["kind"]} for n, part in contract_of_path(project, target)["parts"].items()] \
                    if target and project.kind_of(target) == "file" else None
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
            for name, unit, side, entry in ((result["caller"], result["caller-unit"], result["caller-side"], result["caller-entry"]),
                                            (result["target"], result["target-unit"], result["target-side"], result["target-entry"])):
                lifelines[ids[name]] = {"name": name, "unit": unit.rel} if unit else \
                    {"name": name, "unit": holder.rel, "side": side, "entry": entry}
        scenarios.append({**data, "unit": holder.rel,
                          "diagram": {"source": "\n".join(lines),
                                      "lifelines": {i: lifelines[i] for i in ids.values() if i in lifelines}}})
    up = os.path.relpath(project.root, out_dir).replace(os.sep, "/")
    up = "" if up == "." else up + "/"
    docs = explorer_documents(project, {u["path"]: u["diagrams"] for u in units},
                          {(s["unit"], s["name"]) for s in scenarios}, up)
    model = {"name": project.root_unit.name, "units": units, "scenarios": scenarios, "docs": docs,
             "up": up}
    parts = {"__TITLE__": cell(project.root_unit.name).replace("<", "&lt;"),
             "__MODEL__": json.dumps(model, ensure_ascii=False).replace("</", "<\\/"),
             "__MERMAID__": json.dumps(source), "__INLINE__": inline}
    html = re.sub(r"__(?:TITLE|MODEL|MERMAID|INLINE)__", lambda m: parts[m.group()], EXPLORER)
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
                         "input": result.get("input"), "result": result.get("result"),
                         "example": result.get("example"), "direction": result.get("direction"),
                         "caller-side": result.get("caller-side"), "target-side": result.get("target-side"),
                         "part-kind": result.get("kind"), "contract": rel(result["contract"]),
                         "caller-unit": result["caller-unit"].rel if result["caller-unit"] else None,
                         "target-unit": result["target-unit"].rel if result["target-unit"] else None,
                         "via": [{"unit": holder.rel, "key": key} for holder, key in result["via"]]})
        else:
            hops.append({"caller": None, "target": None, "part": None, "contract": None,
                         "caller-unit": None, "target-unit": None, "via": [],
                         "unresolved": hop, "error": error})
    for hop, (before, after, _), path in zip(hops, scenario.get("states") or [], scenario.get("paths") or []):
        hop["state-before"], hop["state"], hop["groups"] = before, after, list(path)
    spec = scenario["spec"]
    given = [{"connection": e["connection"], "state": e["text"]} if e["connection"] else {"condition": e["text"]}
             for e in scenario.get("given") or [] if e["text"]]
    return {"name": scenario["name"], "summary": spec["summary"], "source": spec["source"] or None,
            "given": given, "expect": spec["expect"], "hops": hops,
            "groups": [{"id": g["id"], "kind": g["kind"], "label": g["label"], "parent": g["parent"]}
                       for g in scenario.get("groups") or []], "x": spec["x"]}


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

    def contract_states_of(unit: Unit, spec: dict):
        """The states of the contract an entry names, as plain data, or None."""
        target = contract_target(project, unit, spec.get("contract"))[1]
        if not target or project.kind_of(target) != "file":
            return None
        contract = contract_of_path(project, target)
        return {"start": contract["states"]["start"],
                "rows": [{"state": r["state"], "part": r["part"], "result": row_result(r["result"]), "next": r["next"]}
                         for r in contract["states"]["rows"]]} if stateful(contract) else None

    def entry(unit: Unit, name: str, spec: dict, side: str) -> dict:
        parts, fake = contract_parts(unit, spec)
        states = contract_states_of(unit, spec)
        data = {"name": name, "summary": spec["summary"],
                "contract": contract_target(project, unit, spec["contract"])[0] or None,
                "parts": spec["parts"], "contract-parts": parts, "fake": fake,
                "contract-states": states}
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
            "kind": unit.kind or None, "runs-as": unit.runs_as or None, "status": unit.status,
            "readme": rel(readme) if project.kind_of(readme) == "file" else None,
            "not": list(unit.nots),
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
    "check": "check manifests, wiring, contracts, documents and generated files; with --fix, "
             "first write the generated files: diagrams, decision indexes, the root AGENTS.md and skill stubs",
    "show": "describe the unit that contains PATH, with its resolved neighbours",
    "capability": "print both ends of every connection of one capability or need",
    "impact": "list everything that depends on a unit or capability, and who cites its files; "
              "for a file, also a deleted one, who cites it",
    "brief": "print what to implement in the unit that contains PATH: the parts of its capabilities with "
             "signatures and examples, the fakes of its needs, the states, the scenarios through it, its "
             "constants and context items",
    "trace": "search the files below the unit for the ids of the examples of its contracts, and report "
             "the examples that no test names and the ids that no example has",
    "scenario": "print one scenario of the unit that contains PATH as Markdown: its sequence diagram and the table of its steps; "
                "an included scenario is one step unless --expand is given",
    "states": "print the `## States` of a contract (a path, or its name in docs/references/ of the unit) as Markdown: a state diagram and the table",
    "tree": "print the unit tree with status, capabilities and needs",
    "model": "print the resolved project as JSON: units, connections, final "
             "providers, scenarios, decisions",
    "skills": "list every skill of the project",
    "explore": "write the explorer, one HTML page with the map and every document, and open it "
               "in a browser",
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
                     help="first write the generated files: diagrams, decision indexes, the root "
                          "AGENTS.md and the skill stubs")
    cmd.add_argument("--strict", action="store_true", help="exit with 1 on warnings too")
    cmd.add_argument("--quiet", "-q", action="store_true",
                     help="hide info findings and fix hints")
    cmd.add_argument("--format", choices=("text", "json", "github"), default="text",
                     help="github: workflow annotations")
    cmd.add_argument("--rule", action="append", metavar="ID",
                     help="report only this rule (repeatable)")
    cmd.add_argument("--ignore", action="append", metavar="ID",
                     help="drop the findings of this rule from the output and the exit code (repeatable)")
    command("model")
    command("show")
    cmd = command("capability", path=False)
    cmd.add_argument("path", help="folder of the unit")
    cmd.add_argument("name", help="name of a capability or need of the unit")
    cmd = command("impact", path=False)
    cmd.add_argument("path", help="folder of the unit, or a file in it; the file need not exist any more")
    cmd.add_argument("capability", nargs="?", help="limit to one capability")
    cmd = command("tree")
    cmd.add_argument("--depth", type=int, help="levels below the root to print")
    command("brief")
    cmd = command("scenario", path=False)
    cmd.add_argument("path", help="folder of the unit that holds the scenario")
    cmd.add_argument("name", help="name of the scenario")
    cmd.add_argument("--expand", action="store_true", help="open every included scenario instead of showing it as one step")
    cmd = command("states", path=False)
    cmd.add_argument("path", help="folder of the unit, or the contract file")
    cmd.add_argument("contract", nargs="?", help="the contract: a path, or its name under docs/references/ of the unit")
    cmd = command("trace")
    cmd.add_argument("--tests", action="append", metavar="GLOB",
                     help="search only files whose path or name matches (repeatable); default: every file below the unit outside docs/")
    cmd.add_argument("--strict", action="store_true", help="exit with 1 when an example is named by no test")
    command("skills")
    cmd = command("explore")
    cmd.add_argument("-o", "--output", metavar="FILE|DIR",
                     help="file to write, or a folder for explorer.html (default: explorer.html "
                          "under the temporary folder of the system, outside the repository)")
    cmd.add_argument("--no-open", action="store_true", help="write the page without opening a browser")
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
    if name == "impact" and not os.path.exists(args.path):   # a deleted file: who still cites it
        project = open_project(args.path)
        target = real(args.path)
        folder = os.path.dirname(target)
        while not os.path.isdir(folder) and folder != os.path.dirname(folder):
            folder = os.path.dirname(folder)
        data = impact(project, unit_for(project, folder), args.capability, target)
        emit(args, data, lambda: print_impact(data))
        return 0
    if not os.path.exists(args.path):
        raise Fail("no-such-path", f"{args.path} does not exist")
    project = open_project(args.path)
    if name == "skills":
        rows = skills_list(project)

        def text():
            for row in rows:
                print(f"{row['name']}  [{row['unit']}]  {row['path']}\n    {row['description']}")
        emit(args, rows, text)
        return 0
    if name == "tree":
        emit(args, tree_data(project, args.depth), lambda: print_tree(project, args.depth))
        return 0
    if name == "model":
        print(json.dumps(build_model(project), indent=1, ensure_ascii=False))
        return 0
    if name == "explore":
        out = build_explorer(project, os.path.abspath(args.output) if args.output
                             else explorer_default(project), args.mermaid)
        opened = False if args.no_open else open_in_browser(out)
        emit(args, {"ok": True, "written": out, "opened": opened},
             lambda: print(f"wrote {out}" + ("" if opened or args.no_open else "; no browser found, open it yourself")))
        return 0
    unit = unit_for(project, args.path)
    if name == "show":
        info = describe(project, unit)
        emit(args, info, lambda: print_show(info))
    elif name == "brief":
        data = brief_data(project, unit)
        emit(args, data, lambda: print_brief(data))
    elif name == "scenario":
        scenario = next((s for s in resolved_scenarios(project) if s["unit"] is unit and s["name"] == args.name), None)
        if scenario is None:
            raise Fail("unknown-scenario", f"'{unit.rel}' holds no scenario '{args.name}' (it holds: "
                                           f"{', '.join(unit.scenarios) or 'none'})")
        emit(args, scenario_data(project, scenario), lambda: print(scenario_page(project, scenario, args.expand), end=""))
    elif name == "states":
        given = args.contract or args.path
        target = real(given) if os.path.isfile(given) else os.path.join(unit.path, "docs", "references", given + ("" if given.endswith(".md") else ".md"))
        if project.kind_of(target) != "file":
            raise Fail("no-such-path", f"no contract {given} in {unit.rel}")
        contract = contract_of_path(project, target)
        if not stateful(contract):
            raise Fail("unknown-capability", f"{project.rel(target)} has no `## States`")
        _, text = states_page(project, target, contract)
        emit(args, {"contract": project.rel(target), "states": contract["states"]["states"],
                    "start": contract["states"]["start"], "rows": contract["states"]["rows"]}, lambda: print(text, end=""))
    elif name == "trace":
        data = trace_data(project, unit, args.tests or [])
        emit(args, data, lambda: print_trace(data))
        bad = any(f["severity"] == "warn" for f in data["findings"]) or \
            (args.strict and any(f["severity"] == "info" for f in data["findings"]))
        return 1 if bad else 0
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
