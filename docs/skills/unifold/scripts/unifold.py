#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""unifold: check, draw and query the architecture map of a repository.

A folder with a `unifold.yaml` is a unit: it says what it provides and what it
needs. The unit above wires needs to providers. This tool checks that map
against itself and against the dependencies it finds in the code.

  init [DIR] [--agents]       start a project: root manifest, generated files; --agents adds the skills
  check [PATH] [--fix]        report findings; --fix first writes the generated files
  generate [PATH]             write diagrams, decision indexes, AGENTS.md, skill stubs
  show [PATH]                 one unit with its resolved neighbours
  capability PATH NAME        both ends of every connection of one entry
  impact PATH [CAPABILITY]    everything that depends on a unit or capability
  tree [PATH]                 the unit tree
  deps [PATH]                 dependencies between units, as found in the code
  stamp [PATH]                confirm context items: write and refresh their stamps
  cited-by FILE               context items and links that cite FILE
  skills [sync] [PATH]        list skills, or write stubs where agents look for them
  site [PATH]                 write the HTML explorer
  rules [ID]                  the rules that `check` applies
  mcp [PATH]                  serve show, capability, impact, check, tree over MCP (stdio)

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
from urllib.parse import quote, unquote

try:
    import yaml
except ImportError:                                   # pragma: no cover
    sys.stderr.write("unifold needs the PyYAML package. Run it with `uvx unifold` or "
                     "`uv run unifold.py`, or install PyYAML (python3 -m pip install pyyaml).\n")
    sys.exit(2)

try:                                                  # Python 3.11+
    import tomllib as _toml
except ImportError:                                   # pragma: no cover
    try:
        import tomli as _toml
    except ImportError:
        _toml = None

TOOL_VERSION = "0.1"
SPEC_VERSIONS = ("0.1",)
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

<Why this unit exists and why it is cut this way: the forces that shaped it, the main trade-off, what must stay true. Write the reasons a newcomer cannot guess. At most 20 lines that are not blank; the long form is docs/explanation/reasoning.md. No list of children, capabilities or connections: the manifest holds them and `unifold show` prints them.>

## Capabilities

<One `###` section for each capability whose summary does not say everything. Delete the ones that are self-explanatory, and the whole section if none is left.>

### `<capability-name>`

<What a user can rely on, each guarantee in a form a test could check: a value, a limit, an order, a response. One short example. End with the link to the contract both sides name: `Contract: [name](docs/references/name.md).`>

## Needs

<One `###` section for each need that the one-line summary does not explain.>

### `<need-name>`

<What this unit expects from whoever provides this, in this unit's own words: what is required, never who supplies it. For an optional need: what the unit does without it.>

## Out of scope

- <What this unit deliberately does not do, so that nobody asks for it here.>

## Commands

<!-- Optional: the few commands to build, test and run this unit. Delete the section otherwise. -->

## Read next

<!-- Optional: a few links into docs/ whose order matters. Delete the section otherwise. -->
"""   # the same text as the skill asset assets/README.template.md
ROOT_KEYS = ("unifold", "name", "ignore", "diagrams", "diagram-links", "max-lines")
UNIT_KEYS = ("summary", "kind", "status", "owner", "capabilities", "needs", "wiring")
CAPABILITY_KEYS = ("summary", "kind", "contract", "verified-by")
NEED_KEYS = ("summary", "kind", "contract", "verified-by", "optional")
STATUSES = ("planned", "active", "deprecated")
DIAGRAM_MODES = ("parents", "all", "none")
DECISION_STATUS = re.compile(r"^(proposed|accepted|rejected|deprecated|superseded by (\d{4}))$")
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

# rule id: (severity, what the rule demands, how to fix a finding)
RULES = {
    "S1": ("error", "The root manifest states a version of the standard that this tool supports, as a string.",
           "Write `unifold: \"0.1\"` in the root `unifold.yaml`."),
    "S3": ("error", "Every unit has a `README.md`.",
           "Write the file (template in the `unifold` skill)."),
    "S7": ("error", "Every folder in `docs/skills/` has a `SKILL.md` whose front matter has `name`, equal to the folder name, and `description`.",
           "Correct the front matter."),
    "S9": ("error", "A decision file is named `NNNN-short-title.md` with a number that is unique in the unit; its front matter has a valid `status` and an ISO `date`; `accepted` names `decision-makers`; `superseded by NNNN` names an existing decision.",
           "Correct the file name or the front matter."),
    "S12": ("info", "Every entry directly in `docs/` is one of `tutorials`, `skills`, `references`, `explanation`, `decisions`, `diagrams`.",
            "Move the file or folder into the folder of its kind: tutorials (learn), skills (do), references (look up), explanation (understand)."),
    "M1": ("error", "A manifest is a YAML mapping without duplicate keys.",
           "Correct the YAML. The unit and its wiring are not checked until it parses."),
    "M2": ("error", "A manifest has a one-line `summary` and otherwise only the keys, types and values of the standard; root-only keys are in the root; names of capabilities and needs use letters, digits, `-` and `_` and start with a letter or digit; no summary is a placeholder (`<...>`).",
           "Correct the key or value named in the message. Project-specific keys start with `x-`."),
    "M7": ("error", "`contract` and `verified-by` are a URL or a path, relative to the manifest, that exists and lies in this unit, a unit above it or a unit below it, never in a sibling.",
           "Correct the path, create the file, or remove the key until there is something to point at. A definition that two siblings share lies in the unit above both."),
    "M10": ("warn", "No summary is still `TODO`.",
            "Replace `TODO` with one line that says what the unit, capability or need is."),
    "W1": ("error", "Every wiring line has an allowed form and names an existing direct child, capability or need, on the correct side. A connection joins two units; a folder is never a provider.",
           "Correct the reference. `unifold show` lists the names; where two children share a folder name, write the path (`a/utils.capability`)."),
    "W2": ("error", "Every need of every child has a provider, unless it is `optional`: a wiring line, or a need of the same name in the parent (implicit pass-up).",
           "Add `child.need: provider` to the parent's wiring, or declare a need of the same name in the parent to pass it up. Do not mark a need optional to silence this."),
    "W3": ("warn", "Every capability of a child is used: a wiring line names it as provider, a capability of the parent is implemented by it, or code of the parent itself is observed to depend on the child.",
           "Wire the unit that should use it, or implement a capability of the parent with it (`capability: child.capability`), or remove the capability."),
    "W4": ("warn", "A need and its provider have the same `kind`, if both state one.",
           "Put an adapter unit between the two, or correct the kind that is wrong."),
    "W7": ("warn", "The children of a unit do not need each other in a cycle.",
           "Move what both need into a third unit, or turn one direction around (the other side subscribes)."),
    "W9": ("warn", "An `active` unit does not get a mandatory need from a provider that is `planned` or `deprecated` (default alternative).",
           "Correct the status, or wire a provider that exists."),
    "W11": ("error", "Every side of a connection names a contract, and both sides name the same document.",
            "Write the definition as a reference of this unit, the one that holds the wiring, or of a unit above it, and point both sides at it with `contract`."),
    "L1": ("error", "The target of every relative link in a hand-written document exists, including its anchor: a heading, or the first cell of a table row.",
           "Correct the link."),
    "L2": ("error", "A link stays inside the unit, goes down to a direct child (its folder or its `README.md`), goes up from `docs/explanation/context.md` to an ancestor's `README.md`, decisions or references, or targets a file that the unit's manifest names as `contract` or `verified-by`. No other link goes sideways, deeper, out of the project, or is an absolute path.",
           "Remove the link. What the unit wants from a sibling is a need in its manifest; what it takes from above is an item in `docs/explanation/context.md`."),
    "L7": ("warn", "`docs/explanation/context.md` cites no decision that is rejected, deprecated or superseded, and an `active` unit cites no decision that is still `proposed`.",
           "Cite the successor, or have the decision accepted."),
    "L9": ("warn", "Every item of `docs/explanation/context.md` is a `###` heading with a link, followed by a paragraph that starts with `Says` and one that starts with `Here`.",
           "Complete the item."),
    "L10": ("warn", "Every context item carries a stamp, and the cited part (the file, or the section or table row that the fragment of the link names) has not changed since the stamp was written.",
            "Read the cited source again, correct `Says`, then run `unifold stamp`. Only `unifold stamp` writes stamps; `check --fix` never does."),
    "T1": ("warn", "A hand-written document has at most `max-lines` lines (default 200).",
           "Split the file: a reference into parts, the long why into `docs/explanation/reasoning.md`, a procedure into a skill."),
    "T4": ("warn", "The `## Why` section of `README.md` has at most 20 lines that are not blank.",
           "Move the long form to `docs/explanation/reasoning.md`."),
    "T5": ("warn", "A `###` heading in code font under `## Capabilities` or `## Needs` of a `README.md` names a capability or need of the manifest.",
           "Rename or remove the section; the manifest is the list of capabilities and needs."),
    "G1": ("error", "Every generated file exists and equals what the generator writes now; no leftover generated file remains; `docs/diagrams/` holds only generated files and `AGENTS.md` is generated.",
           "Run `unifold generate` (or `unifold check --fix`)."),
    "D1": ("error", "Code in one unit depends on code in another unit only where a connection covers it. A dependency that only tests have is exempt.",
           "Declare the need and wire it, give the code a manifest if it has none, or remove the dependency from the code."),
    "D2": ("warn", "For every connection between two units whose dependencies are extracted, a dependency is found in code.",
           "Remove the stale wiring line and need, or pass the dependency that the extractor cannot see with `--deps FILE`."),
    "D3": ("error", "A dependency list given with `--deps` is a JSON list of `{\"from\", \"to\"}` whose paths exist in the project.",
           "Correct the list; paths are relative to the project root."),
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


def load_toml(path: str):
    """Return (mapping or None, error or None). Uses tomllib, tomli or a small reader."""
    try:
        text = read_text(path)
        if _toml is not None and not os.environ.get("UNIFOLD_MINI_TOML"):
            return _toml.loads(text), None
        return _MiniToml(text).parse(), None
    except OSError as exc:
        return None, f"cannot read {path}: {exc.strerror or exc}"
    except RecursionError:
        return None, f"{path}: nested too deeply"
    except Exception as exc:                          # tomllib.TOMLDecodeError, ValueError
        extra = "" if _toml is not None else \
            " (built-in TOML reader; Python 3.11+ or the package `tomli` reads every file)"
        return None, f"{path}: not readable as TOML: {exc}{extra}"


class _MiniToml:
    """Reads the TOML that build files use, for Python 3.9 and 3.10 without `tomli`."""

    def __init__(self, text: str):
        self.s, self.i = text, 0

    def error(self, what):
        line = self.s.count("\n", 0, self.i) + 1
        raise ValueError(f"line {line}: {what}")

    def skip(self, newlines=False):
        s = self.s
        while self.i < len(s):
            c = s[self.i]
            if c in " \t" or (newlines and c in "\r\n"):
                self.i += 1
            elif c == "#":
                while self.i < len(s) and s[self.i] != "\n":
                    self.i += 1
            else:
                break

    def parse(self) -> dict:
        root: dict = {}
        table = root
        while True:
            self.skip(True)
            if self.i >= len(self.s):
                return root
            if self.s.startswith("[[", self.i):
                self.i += 2
                keys = self.keys()
                if not self.s.startswith("]]", self.i):
                    self.error("expected ]]")
                self.i += 2
                parent = self.descend(root, keys[:-1])
                items = parent.setdefault(keys[-1], [])
                if not isinstance(items, list):
                    self.error("not an array of tables")
                table = {}
                items.append(table)
            elif self.s[self.i] == "[":
                self.i += 1
                keys = self.keys()
                if self.s[self.i:self.i + 1] != "]":
                    self.error("expected ]")
                self.i += 1
                table = self.descend(root, keys)
            else:
                keys = self.keys()
                if self.s[self.i:self.i + 1] != "=":
                    self.error("expected =")
                self.i += 1
                self.skip()
                self.descend(table, keys[:-1])[keys[-1]] = self.value()
            self.skip()
            if self.i < len(self.s) and self.s[self.i] not in "\r\n":
                self.error("unexpected text")

    def descend(self, table, keys):
        for key in keys:
            nxt = table.setdefault(key, {})
            if isinstance(nxt, list) and nxt and isinstance(nxt[-1], dict):
                nxt = nxt[-1]
            if not isinstance(nxt, dict):
                self.error(f"'{key}' is not a table")
            table = nxt
        return table

    def keys(self):
        out = []
        while True:
            self.skip()
            c = self.s[self.i:self.i + 1]
            if c in ('"', "'"):
                out.append(self.string())
            else:
                match = re.compile(r"[A-Za-z0-9_-]+").match(self.s, self.i)
                if not match:
                    self.error("expected a key")
                out.append(match.group())
                self.i = match.end()
            self.skip()
            if self.s[self.i:self.i + 1] != ".":
                return out
            self.i += 1

    def string(self):
        s, q = self.s, self.s[self.i]
        if s.startswith(q * 3, self.i):
            end = s.find(q * 3, self.i + 3)
            if end < 0:
                self.error("unterminated string")
            while s.startswith(q, end + 3):               # quotes right before the end
                end += 1
            raw = s[self.i + 3:end]
            self.i = end + 3
            raw = raw[1:] if raw.startswith("\n") else raw
            return self.unescape(re.sub(r"\\[ \t]*\n\s*", "", raw)) if q == '"' else raw
        j = self.i + 1
        while j < len(s) and s[j] != q:
            if s[j] == "\n":
                self.error("unterminated string")
            j += 2 if (s[j] == "\\" and q == '"') else 1
        if j >= len(s):
            self.error("unterminated string")
        raw = s[self.i + 1:j]
        self.i = j + 1
        return self.unescape(raw) if q == '"' else raw

    @staticmethod
    def unescape(raw):
        def one(match):
            c = match.group(1)
            if c[0] in "uU":
                return chr(int(c[1:], 16))
            return {"b": "\b", "t": "\t", "n": "\n", "f": "\f", "r": "\r", "e": "\x1b"}.get(c, c)
        return re.sub(r"\\(u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}|.)", one, raw)

    def value(self):
        s = self.s
        c = s[self.i:self.i + 1]
        if c in ('"', "'"):
            return self.string()
        if c == "[":
            self.i += 1
            out = []
            while True:
                self.skip(True)
                if s[self.i:self.i + 1] == "]":
                    self.i += 1
                    return out
                out.append(self.value())
                self.skip(True)
                if s[self.i:self.i + 1] == ",":
                    self.i += 1
                elif s[self.i:self.i + 1] != "]":
                    self.error("expected , or ]")
        if c == "{":
            self.i += 1
            out = {}
            while True:
                self.skip(True)
                if s[self.i:self.i + 1] == "}":
                    self.i += 1
                    return out
                keys = self.keys()
                if s[self.i:self.i + 1] != "=":
                    self.error("expected =")
                self.i += 1
                self.skip()
                self.descend(out, keys[:-1])[keys[-1]] = self.value()
                self.skip(True)
                if s[self.i:self.i + 1] == ",":
                    self.i += 1
                elif s[self.i:self.i + 1] != "}":
                    self.error("expected , or }")
        match = re.compile(r"[^\s,\]}#]+(?: \d\d:[^\s,\]}#]+)?").match(s, self.i)
        if not match:
            self.error("expected a value")
        self.i = match.end()
        word = match.group()
        if word in ("true", "false"):
            return word == "true"
        try:
            return int(word.replace("_", ""), 0)
        except ValueError:
            try:
                return float(word.replace("_", ""))
            except ValueError:
                return word                                # dates and times stay text


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


def slug_name(text: str) -> str:
    """A package name as a capability name: letters, digits, '-' and '_'."""
    text = re.sub(r"[^A-Za-z0-9_-]+", "-", str(text).split("/")[-1] if str(text).startswith("@")
                  else str(text)).strip("-_")
    return text or "main"


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
    """A need (or an own capability) with its providers. origin: explicit or implicit."""
    __slots__ = ("key", "entries", "origin", "line")

    def __init__(self, key, entries, origin, line):
        self.key, self.entries, self.origin, self.line = key, entries, origin, line


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
        self.summary = " ".join(_text(manifest.get("summary")).split())
        self.kind = _text(manifest.get("kind"))
        status = manifest.get("status")
        self.status = status if status in STATUSES else "active"
        self.own_owner = _text(manifest.get("owner"))
        self.capabilities = self._entries("capabilities")
        self.needs = self._entries("needs")
        self.conn: dict = {}                    # (child, need) -> Conn
        self.impl: dict = {}                    # own capability -> Conn (implemented by children)
        self.need_users: dict = {}              # own need -> [(child, need)]
        self.capability_users: dict = {}              # (child, capability) -> [("need", child, need, config) | ("capability", name)]
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
                out[str(name)] = {
                    "summary": " ".join(_text(spec.get("summary")).split()),
                    "kind": _text(spec.get("kind")),
                    "contract": _text(spec.get("contract")) or None,
                    "verified-by": _text(spec.get("verified-by")) or None,
                    "optional": spec.get("optional") is True}
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

    def chain(self) -> list:
        """The root first, this unit last."""
        return [self, *self.ancestors()][::-1]

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
        self.by_path: dict = {}
        self.root_unit = None
        self.usable = False                     # False: only `check` can say something
        self.ignore: set = set()                # folders named by `ignore` in the root manifest
        self.git_ignored: set = git_ignored(root)   # files and folders that git ignores
        self.links, self.diagrams, self.max_lines = "none", "parents", MAX_LINES
        self._texts: dict = {}
        self._docs: dict = {}
        self._kinds: dict = {}
        self._owners: dict = {}
        self._rels: dict = {root: "."}
        self._expected = None
        self.deps_notes: list = []
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
        for unit in self.units:
            self._connect(unit)

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
            or rel in self.git_ignored \
            or any(rel.startswith(item) for item in self.git_ignored if item.endswith("/"))

    def ignored_paths(self) -> set:
        """What the dependency scan skips: the `ignore` folders and what git ignores."""
        return self.ignore | {item.rstrip("/") for item in self.git_ignored}

    def listdir(self, folder: str) -> list:
        """The visible entries of a folder, sorted: no dot files, nothing ignored."""
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            return []
        return [n for n in names if not n.startswith(".")
                and not self.is_ignored(os.path.join(folder, n))]

    # ----- wiring

    def _provider(self, unit, for_port, key_child, config, value):
        """Resolve one provider reference. Returns (Entry or None, error or None)."""
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
        if for_port:
            return None, f"a capability cannot be wired to an own need ('{value}'); " \
                         "a capability is implemented by a child (`child.capability`)"
        if value not in unit.needs:
            hint = "; a capability of a child is written 'child." + value + "'" \
                if any(value in c.capabilities for c in unit.children[:500]) else ""
            return None, f"'{value}' is not a need of this unit{hint}"
        return Entry(config, "own", value, capability=value), None

    def _connect(self, unit):
        raw = unit.manifest.get("wiring")
        if not isinstance(raw, dict) or unit.broken:
            raw = {}
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
            key_child, need = None, None
            if key.startswith("./") or key.startswith("*"):
                unit.problems.append((line, f"wiring key '{key}': a key is a need of a child "
                                            "(`child.need`) or a capability of this unit; every unit "
                                            "is written out"))
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
                    side = " It is a capability there; write the line as `user.need: " \
                           f"{key}`." if need in key_child.capabilities else ""
                    unit.problems.append((line, f"wiring key '{key}': '{key_child.rel}' has no "
                                                f"need '{need}'{hint}{side}"))
                    continue
            elif key not in unit.capabilities:
                hint = " (a need of a child is written `child.need`)" \
                    if any(key in c.needs for c in unit.children[:500]) else ""
                unit.problems.append((line, f"wiring key '{key}': not a capability of this unit{hint}"))
                continue
            entries = []
            for config, target in pairs:
                entry, error = self._provider(unit, key_child is None,
                                              key_child, config, target)
                if error:
                    shown = target if isinstance(target, str) else show_value(target)
                    unit.problems.append((line, f"wiring '{key}: {shown}': {error}"))
                else:
                    entries.append(entry)
            if not entries:
                continue
            if key_child is not None:
                unit.conn[(key_child, need)] = Conn(key, entries, "explicit", line)
            else:
                unit.impl[key] = Conn(key, entries, "explicit", line)
        for child in unit.children:
            for need in child.needs:
                if (child, need) not in unit.conn and need in unit.needs:
                    unit.conn[(child, need)] = Conn(
                        f"{child.ref_in_parent()}.{need}",
                        [Entry(None, "own", need, capability=need)], "implicit", None)
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
    parent = unit.parent
    if parent is None:
        return [{"where": "outside", "capability": need, "config": None, "via": []}]
    conn = parent.conn.get((unit, need))
    if conn is None:
        return []
    via = [] if conn.origin == "explicit" else [conn.origin]
    out = []
    for entry in conn.entries:
        if entry.kind == "child":
            for target, capability in implementers(entry.unit, entry.capability):
                out.append({"where": "unit", "unit": target, "capability": capability,
                            "config": entry.config, "via": via})
        else:
            for item in providers_of(parent, entry.capability):
                out.append({**item, "config": item["config"] or entry.config,
                            "via": via + [v for v in item["via"] if v not in via]})
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

    def summary_of(value, label, *key):
        if not isinstance(value, str) or not value.strip():
            bad(f"{label} needs a 'summary': one line of text", *key)
        elif "\n" in value.strip():
            bad(f"the summary of {label} must be one line", *key)
        elif PLACEHOLDER.match(value.strip()):
            bad(f"the summary of {label} is a placeholder ({value.strip()}); write the "
                "summary, or `TODO` for a draft", *key)
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
        else:
            close = difflib.get_close_matches(key.lower(), ROOT_KEYS + UNIT_KEYS, 1)
            hint = f"; did you mean '{close[0]}'?" if close else ""
            bad(f"unknown key '{key}'{hint}", key)
    summary_of(manifest.get("summary"), "the unit", "summary")
    for key in ("kind", "owner", "name", "diagram-links"):
        if key in manifest and not _text(manifest[key]):
            bad(f"'{key}' must be text, not {show_value(manifest[key])}", key)
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
                if isinstance(key, str) and (key in allowed or key.startswith("x-")):
                    continue
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
            for field in ("contract", "verified-by"):
                if field not in spec:
                    continue
                value = spec[field]
                line = lines.get((section, name, field))
                if not isinstance(value, str) or not value.strip():
                    bad(f"{label}: '{field}' must be one path or URL, not {show_value(value)}",
                        section, name, field)
                    continue
                problem = path_problem(project, unit, value.strip())
                if problem:
                    project.add("M7", where, f"{label}: '{field}' {problem}: {value.strip()}", line)
    raw = manifest.get("wiring")
    if raw is not None and not isinstance(raw, dict):
        bad(f"'wiring' must be a mapping of need to provider, not {show_value(raw)}", "wiring")
    for line, message in unit.schema_problems:
        project.add("M2", where, message, line)
    if todo:
        shown = ", ".join(todo[:6]) + (f" and {len(todo) - 6} more" if len(todo) > 6 else "")
        project.add("M10", where, f"summary still says TODO: {shown}", lines.get(("summary",)))


def path_problem(project: Project, unit: Unit, value: str):
    """Why a contract or verified-by value is not acceptable, or None."""
    if SCHEME.match(value) and not re.match(r"^[A-Za-z]:[\\/]", value):
        return None
    if os.path.isabs(value) or re.match(r"^[A-Za-z]:[\\/]", value):
        return "must be a path relative to the manifest, or a URL"
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
    return None


def contract_target(project: Project, unit: Unit, value):
    """(display text, absolute path or None, URL or None) for a contract or verified-by value."""
    if not value:
        return "", None, None
    if SCHEME.match(value):
        return value, None, value
    target = os.path.normpath(os.path.join(unit.path, value.split("#", 1)[0]))
    return project.rel(target), target, None


def check_wiring(project: Project, unit: Unit, parent_uses=frozenset()):
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
                if not spec["optional"]:
                    offers = [c.ref_in_parent() + "." + need for c in unit.children[:2000]
                              if c is not child and need in c.capabilities]
                    fix = f"Add `{ref}.{need}: {offers[0]}` to the wiring." if offers else \
                        (f"Add `{ref}.{need}: <provider>` to the wiring of this manifest, or "
                         f"declare a need `{need}` here to pass it up" +
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
            if not unit.capability_users.get((child, capability)) and (unit, child) not in parent_uses:
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
    return {"path": path, "name": os.path.basename(path),
            "title": doc.title() or os.path.basename(path)[:-3],
            "status": " ".join(status.split()) if isinstance(status, str) else "",
            "raw-status": status,
            "date": date.isoformat() if hasattr(date, "isoformat") else str(date or ""),
            "makers": meta.get("decision-makers"), "error": doc.meta_error,
            "has-meta": doc.meta is not None and bool(meta)}


def status_mark(status: str) -> str:
    """How a status that is not in force is shown to readers and agents."""
    return {"planned": "planned: not built yet", "deprecated": "deprecated: to be removed",
            "proposed": "proposed: not accepted, does not bind"}.get(status, status)


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
                                    "proposed, accepted, rejected, deprecated, superseded by NNNN", 2)
        elif status.group(2) and status.group(2) not in numbers:
            project.add("S9", path, f"status names decision {status.group(2)}, which does not "
                                    "exist in this unit", 2)
        if not ISO_DATE.match(info["date"]):
            project.add("S9", path, "a decision needs a `date` in the form 2026-10-07"
                        + (f", not '{info['date']}'" if info["date"] else ""), 2)
        if info["status"] == "accepted" and not info["makers"]:
            project.add("S9", path, "an accepted decision names its `decision-makers`", 2)


def manifest_targets(project: Project, unit: Unit) -> set:
    """The files that the manifest of `unit` names as contract or verified-by."""
    out = set()
    for entries in (unit.capabilities, unit.needs):
        for spec in entries.values():
            for field in ("contract", "verified-by"):
                target = contract_target(project, unit, spec.get(field))[1]
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
                project.add("L2", path, "a nested project is linked only by its README.md, "
                                        f"from the unit that contains it: {link}", line)
        elif owner is unit:
            continue
        elif owner.parent is unit:
            if target not in (owner.path, os.path.join(owner.path, "README.md")):
                project.add("L2", path, f"link into the child '{owner.name}' must target its "
                                        f"README.md: {link}", line)
        elif owner.depth_below(unit) is not None:
            project.add("L2", path, f"link reaches into '{owner.rel}', below a child; link to "
                                    f"the README.md of the direct child instead: {link}", line)
        elif unit.depth_below(owner) is not None:
            decisions = os.path.join(owner.path, "docs", "decisions") + os.sep
            references = os.path.join(owner.path, "docs", "references") + os.sep
            if not is_context:
                project.add("L2", path, f"upward link outside docs/explanation/context.md: {link}",
                            line, "Cite it as an item in docs/explanation/context.md and link to "
                                  "that file.")
            elif not (target == os.path.join(owner.path, "README.md")
                      or target.startswith((decisions, references))):
                project.add("L2", path, "docs/explanation/context.md cites only an ancestor's "
                                        f"README.md, decisions and references: {link}", line)
            elif target.startswith(decisions) and target.endswith(".md") \
                    and os.path.basename(target) != "index.md" and kind == "file":
                status = decision_info(project, target)["status"]
                if status.startswith(("rejected", "deprecated", "superseded")):
                    project.add("L7", path, f"cites a decision that is {status}: {link}", line)
                elif status == "proposed" and unit.status == "active":
                    project.add("L7", path, "an active unit relies on a decision that is "
                                            f"still proposed: {link}", line)
        else:
            project.add("L2", path, f"sideways link into '{owner.rel}'; a unit does not know "
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


# ----- generated files

def check_generated(project: Project):
    expected = project.expected()
    for path, content in expected.items():
        kind = project.kind_of(path)
        if kind != "file":
            project.add("G1", path, "generated file is missing" if not kind else
                        "a folder is in the place of a generated file")
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
    for stub_dir in STUB_DIRS:
        folder = os.path.join(project.root, *stub_dir.split("/"))
        if project.kind_of(folder) != "dir":
            continue
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name, "SKILL.md")
            if path not in expected and os.path.isfile(path) and STUB_MARK in project.text(path):
                out.append((path, True))
    return out


# ----- dependencies in code

def load_deps_file(project: Project, source: str) -> list:
    """Read a list of observed dependencies. Problems become D3 findings."""
    shown = source if not project.inside(real(source)) else real(source)
    try:
        data = json.loads(read_text(source))
    except (OSError, ValueError) as exc:
        project.add("D3", shown, f"cannot read the dependency list: {exc}")
        return []
    if not isinstance(data, list):
        project.add("D3", shown, "the dependency list must be a JSON list of "
                                 '{"from": path, "to": path} entries, not '
                                 + ("an object" if isinstance(data, dict) else "a single value"))
        return []
    edges, malformed, unknown = [], [], []
    for index, item in enumerate(data, 1):
        if not isinstance(item, dict) or not isinstance(item.get("from"), str) \
                or not isinstance(item.get("to"), str):
            malformed.append(index)
            continue
        edge = {"kind": str(item.get("kind") or "given"),
                "evidence": str(item.get("evidence") or f"{os.path.basename(source)} entry {index}")}
        for side in ("from", "to"):
            value = item[side].replace("\\", "/")
            path = value if os.path.isabs(value) else os.path.join(project.root, value)
            path = os.path.normpath(path)
            if not project.inside(path) or not os.path.exists(path):
                unknown.append(f"entry {index}: '{item[side]}'")
                edge = None
                break
            edge[side] = project.rel(path)
        if edge:
            edges.append(edge)
    if malformed:
        project.add("D3", shown, f"{len(malformed)} entr{'y is' if len(malformed) == 1 else 'ies are'}"
                                 f" not of the form {{\"from\": path, \"to\": path}} (first: entry "
                                 f"{malformed[0]})")
    if unknown:
        project.add("D3", shown, f"{len(unknown)} path(s) do not exist in the project: "
                    + "; ".join(unknown[:3]) + (" …" if len(unknown) > 3 else ""))
    return edges


def is_dev(edge: dict) -> bool:
    return str(edge.get("kind", "")).endswith("-dev")


def map_edges(project: Project, edges: list):
    """Sort edges by what they mean for the unit tree.

    Returns (between, upward, parent_uses): `between` maps (common, first, second) to the
    edges between two children of `common`; `upward` maps (ancestor, first) to edges from
    below `first` to own code of the ancestor; `parent_uses` holds (unit, child) where
    own code of the unit uses something below the child.
    """
    between, upward, parent_uses = {}, {}, set()
    for edge in edges:
        src = os.path.join(project.root, *edge["from"].split("/")) if edge["from"] != "." else project.root
        dst = os.path.join(project.root, *edge["to"].split("/")) if edge["to"] != "." else project.root
        if project.is_ignored(src) or project.is_ignored(dst):
            continue
        (kind_a, a), (kind_b, b) = project.owner_of(src), project.owner_of(dst)
        if kind_a != "unit" or kind_b != "unit" or a is b:
            continue
        chain_a, chain_b = a.chain(), b.chain()
        depth = 0
        while depth < min(len(chain_a), len(chain_b)) and chain_a[depth] is chain_b[depth]:
            depth += 1
        common = chain_a[depth - 1]
        if a is common:
            parent_uses.add((a, chain_b[depth]))
        elif b is common:
            upward.setdefault((common, chain_a[depth]), []).append((edge, a, dst))
        else:
            between.setdefault((common, chain_a[depth], chain_b[depth]), []).append((edge, a, b))
    return between, upward, parent_uses


def evidence_text(items: list) -> str:
    edge = next((e for e, *_ in items if not is_dev(e)), items[0][0])
    count = sum(1 for e, *_ in items if not is_dev(e))
    text = edge.get("evidence") or f"{edge['from']} -> {edge['to']}"
    return f"{edge.get('kind', 'given')}: {text}" + (f"; {count - 1} more" if count > 1 else "")


def check_deps(project: Project, mapped, covered: dict):
    """D1 and D2: compare observed dependencies with the wiring."""
    between, upward, _ = mapped
    wired: dict = {}
    for unit in project.units:
        for (child, _), conn in unit.conn.items():
            for entry in conn.entries:
                if entry.kind == "child":
                    wired.setdefault((unit, child, entry.unit), conn)
    for (common, first, second), items in between.items():
        real_items = [i for i in items if not is_dev(i[0])]
        if not real_items or (common, first, second) in wired or first.broken or second.broken:
            continue
        _, a, b = real_items[0]
        ref_a, ref_b = first.ref_in_parent(), second.ref_in_parent()
        capability = next(iter(b.capabilities), "<capability>") if b is second else "<capability>"
        need = slug_name(b.name)
        names = {need, *b.capabilities, *second.capabilities}
        names |= {slug_name(e.get("evidence", "").split("(")[0].split()[-1])
                  for e, *_ in real_items if e.get("evidence", "").split("(")[0].split()}
        present = [n for n in a.needs if n in names
                   and (a is not first or (first, n) not in common.conn)]
        if present:
            need = present[0]
            steps = f"Wire need `{need}` of {a.rel}/{MANIFEST}, which is declared but not " \
                    "connected"
            if a is not first:
                steps += f": declare the same need in each unit up to '{first.rel}'"
            steps += (", and" if a is not first else ":") + \
                f" add `{ref_a}.{need}: {ref_b}.{capability}` to the wiring here. " \
                "Or remove the dependency from the code."
        else:
            steps = f"Add a need to {a.rel}/{MANIFEST} (for example `{need}`)"
            if a is not first:
                steps += f", declare the same need in each unit up to '{first.rel}'"
            steps += f", and add `{ref_a}.{need}: {ref_b}.{capability}` to the wiring here. " \
                     "Or remove the dependency from the code."
        project.add("D1", common.manifest_path,
                    f"'{a.rel}' depends on '{b.rel}', but no need of '{ref_a}' is connected "
                    f"to '{ref_b}' ({evidence_text(real_items)})",
                    common.lines.get(("wiring",)), steps)
    for (common, first), items in upward.items():
        open_items = [i for i in items if not is_dev(i[0])]
        if not open_items or first.broken:
            continue
        _, a, dst = open_items[0]
        project.add("D1", common.manifest_path,
                    f"'{a.rel}' depends on code of its ancestor '{common.rel}' that lies in "
                    f"no unit ({evidence_text(open_items)})",
                    common.lines.get(("wiring",)),
                    f"Give that code a folder with a {MANIFEST} and a capability, declare a "
                    f"need in {a.rel}/{MANIFEST} and wire the two here; or remove the dependency.")
    for (unit, child, provider), conn in wired.items():
        if (unit, child, provider) in between or conn.origin == "implicit":
            continue
        shared = [eco for eco, units in covered.items() if child in units and provider in units]
        if not shared:
            continue
        need = next(n for (c, n), k in unit.conn.items() if c is child and k is conn)
        project.add("D2", unit.manifest_path,
                    f"need '{need}' of '{child.rel}' is connected to '{provider.rel}', but no "
                    f"dependency between them was found in code ({', '.join(sorted(shared))})",
                    conn.line)


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


def diagram(project: Project, frame: Unit, depth: int, out_dir: str, focus: Unit = None):
    """Build one flowchart of the inside of `frame`.

    Without `focus`: all children, opened `depth` levels deep. With `focus` (a child of
    `frame`): that child and the siblings it is connected to.
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

    passed: dict = {}                    # need of the frame -> children that pass it up by name
    if focus is None:
        for (child, need), conn in frame.conn.items():
            if conn.origin == "implicit":
                passed.setdefault(need, []).append(child)
    for need, users in sorted(passed.items()):
        if len(users) >= SHARED_FROM:
            optional = all(c.needs.get(need, {}).get("optional") for c in users)
            shared.append(f"- need `{need}` of " + ", ".join(f"`{c.ref_in_parent()}`" for c in users)
                          + f" → need `{need}` of `{frame.name}`, passed up by name"
                          + (" (optional)" if optional else ""))

    def collect(unit: Unit):
        for (child, need), conn in unit.conn.items():
            if unit is frame and conn.origin == "implicit" and \
                    len(passed.get(need, ())) >= SHARED_FROM:
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
    lines = ["flowchart LR", f'  subgraph {node_id(frame)}["{label(frame.name)}"]']
    clicks, marks = [], {"planned": [], "deprecated": []}

    def emit(unit: Unit, indent: str):
        shown.append(unit)
        ids[node_id(unit)] = unit
        if unit.status in marks:
            marks[unit.status].append(node_id(unit))
        if expanded(unit):
            lines.append(f'{indent}subgraph {node_id(unit)}["{label(unit.name)}"]')
            for child in unit.children:
                emit(child, indent + "  ")
            lines.append(f"{indent}end")
        else:
            lines.append(f'{indent}{node_id(unit)}["{label(unit.name)}"]')
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


def lone_context(project: Project, unit: Unit, out_dir: str):
    """A unit without a parent, alone with its capabilities and needs."""
    uid = node_id(unit)
    lines = ["flowchart LR", f'  {uid}["{label(unit.name)}"]']
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
    rows = ["| Unit | Kind | Summary | Status |" + (" Diagram |" if extra else ""),
            "|---|---|---|---|" + ("---|" if extra else "")]
    for unit, target in zip(units, targets):
        name = file_link(project, out_dir, unit.name, os.path.join(unit.path, "README.md"))
        link = f"[{os.path.basename(target)[:-3]}]({link_to(out_dir, target)})" if target else ""
        rows.append(f"| {name} | {cell(unit.kind)} | {cell(unit.summary)} | "
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
    notes = []
    if item.get("config"):
        notes.append(str(item["config"]))
    if "implicit" in item.get("via", ()):
        notes.append("passed up by name")
    return f" ({'; '.join(notes)})" if notes else ""


def connection_tables(project: Project, unit: Unit, out_dir: str) -> list:
    """Final providers and final users of a unit, as tables."""
    rows = []
    if unit.needs:
        rows += ["", "### Who provides what this unit needs", "",
                 "| Need | Kind | Contract | Provided by | Capability | Verified by |",
                 "|---|---|---|---|---|---|"]
        for need, spec in unit.needs.items():
            head = f"| {need} | {cell(spec['kind'])} | " \
                   f"{path_link(project, unit, spec['contract'], out_dir, 'contract')} | "
            found = providers_of(unit, need)
            if not found:
                note = "nobody (optional)" if spec["optional"] else "**no provider**"
                rows.append(head + f"{note} | | |")
            for item in found:
                note = via_note(item)
                if item["where"] == "outside":
                    rows.append(head + f"outside the project, as need `{item['capability']}` of the "
                                       f"root{note} | | |")
                else:
                    target = item["unit"]
                    theirs = target.capabilities.get(item["capability"], {})
                    rows.append(
                        head + f"{unit_ref(project, target, out_dir)}{note} | {item['capability']} | "
                        f"{path_link(project, target, theirs.get('verified-by'), out_dir, 'checks')} |")
    if unit.capabilities:
        rows += ["", "### Who uses what this unit provides", "",
                 "| Capability | Kind | Contract | Verified by | Used by | As need |",
                 "|---|---|---|---|---|---|"]
        for capability, spec in unit.capabilities.items():
            head = f"| {capability} | {cell(spec['kind'])} | " \
                   f"{path_link(project, unit, spec['contract'], out_dir, 'contract')} | " \
                   f"{path_link(project, unit, spec['verified-by'], out_dir, 'checks')} | "
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
    for (child, need), conn in unit.conn.items():
        key = f"`{child.ref_in_parent()}.{need}`"
        to = " or ".join((f"`{e.raw}`" if e.kind != "own" else f"need `{e.capability}` of `{unit.name}`")
                         + (f" ({e.config})" if e.config else "") for e in conn.entries)
        note = {"implicit": "passed up by name", "explicit": ""}[conn.origin]
        if child.needs.get(need, {}).get("optional"):
            note = (note + ", " if note else "") + "optional"
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
        f"- `{tool} check`: is the map consistent, and does the code agree (`--fix` rewrites generated files)",
    ]
    skills = [(n, t) for n, t in (("unifold", "How to read and write the map"),
                                  ("unifold-convert", "How to bring folders into the map"))
              if os.path.isfile(os.path.join(project.root, "docs", "skills", n, "SKILL.md"))]
    if skills:
        lines += ["", " ".join(f"{t}: the skill [{n}](docs/skills/{n}/SKILL.md)." for n, t in skills)]
    units = [u for u in project.units if u.parent is not None]
    if units and len(units) <= INDEX_LIMIT:
        lines += ["", "| Unit | Path | Summary |", "|---|---|---|"]
        for unit in units:
            mark = f" ({unit.status})" if unit.status != "active" else ""
            lines.append(f"| {cell(unit.name)} | `{cell(unit.rel)}` | {cell(unit.summary)}{mark} |")
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
    for unit in project.units:
        infos = decisions_of(project, unit)
        if not infos:
            continue
        folder = os.path.join(unit.path, "docs", "decisions")
        rows = ["| No. | Decision | Status | Date |", "|---|---|---|---|"]
        for info in infos:
            status = info["status"]
            shown = f"**{status_mark(status)}**" if status == "proposed" else cell(status)
            rows.append(f"| {info['name'][:4]} | [{cell(info['title'])}]({url_path(info['name'])}) | "
                        f"{shown} | {info['date']} |")
        nav = [f"[{n}]({link_to(folder, os.path.join(unit.path, n))})"
               for n in ("README.md", "AGENTS.md")
               if n == "AGENTS.md" or project.kind_of(os.path.join(unit.path, n)) == "file"]
        out[os.path.join(folder, "index.md")] = "\n".join(
            [MARK, f"# Decisions of {unit.name}", "", *([" · ".join(nav), ""] if nav else []),
             "Only accepted decisions bind.", "", *rows, ""])
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
                "summary": other.summary}

    def provider(item: dict) -> dict:
        via = [{"implicit": "passed up by name"}[v] for v in item["via"]]
        if item["where"] == "outside":
            return {"outside": True, "root-need": item["capability"], "config": item["config"],
                    "via": via}
        target = item["unit"]
        spec = target.capabilities.get(item["capability"], {})
        return {"unit": target.rel, "status": target.status, "capability": item["capability"],
                "verified-by": contract_target(project, target, spec.get("verified-by"))[0] or None,
                "config": item["config"], "via": via}

    def user(item: dict) -> dict:
        if item["where"] == "outside":
            return {"outside": True, "root-capability": item["need"]}
        other = item["unit"]
        return {"unit": other.rel, "status": other.status, "need": item["need"],
                "config": item["config"]}

    def entry(spec: dict) -> dict:
        return {"kind": spec["kind"] or None, "summary": spec["summary"],
                "contract": contract_target(project, unit, spec["contract"])[0] or None,
                "verified-by": contract_target(project, unit, spec["verified-by"])[0] or None}

    files = [rel(p) for p in managed_files(project, unit) if not generated_location(unit, p)]
    return {
        "name": unit.name, "path": unit.rel, "summary": unit.summary,
        "kind": unit.kind or None, "status": unit.status, "owner": unit.owner or None,
        "manifest": rel(unit.manifest_path),
        "parent": brief(unit.parent) if unit.parent else None,
        "children": [brief(c) for c in unit.children],
        "nested-projects": [rel(p) for p in unit.foreign],
        "capabilities": {capability: {**entry(spec),
                            "used-by": [user(i) for i in users_of(unit, capability)]}
                     for capability, spec in unit.capabilities.items()},
        "needs": {need: {**entry(spec), "optional": spec["optional"],
                         "provided-by": [provider(i) for i in providers_of(unit, need)]}
                  for need, spec in unit.needs.items()},
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
    return f" [{status_mark(status)}]" if status and status not in ("active", "accepted") else ""


def print_show(info: dict):
    def line(name, value):
        if value:
            print(f"{name:<10}{value}")
    line("unit", f"{info['name']}  ({info['path']}){mark(info['status'])}")
    line("summary", info["summary"])
    line("status", " · ".join(x for x in (
        info["status"], info["kind"], info["owner"] and "owner " + info["owner"]) if x))
    line("manifest", info["manifest"])
    parent = info["parent"]
    line("parent", (parent["name"] if parent["path"] == "." else parent["path"])
         + mark(parent["status"]) if parent else "none (this is the root)")
    line("children", ", ".join(c["path"] + mark(c["status"]) for c in info["children"]) or "none")
    line("nested", ", ".join(info["nested-projects"]))
    if info["capabilities"]:
        print("capabilities")
    for capability, spec in info["capabilities"].items():
        extra = "".join(f"  {name} {spec[key]}" for key, name in (
            ("contract", "contract"), ("verified-by", "verified by")) if spec[key])
        kind = f" ({spec['kind']})" if spec["kind"] else ""
        print(f"  {capability}{kind}: {spec['summary']}{extra}")
        for item in spec["used-by"] or [None]:
            if item is None:
                print("      used by nobody")
            elif item.get("outside"):
                print(f"      used from outside the project (capability '{item['root-capability']}' of the root)")
            else:
                config = f" [{item['config']}]" if item.get("config") else ""
                print(f"      used by {item['unit']}{mark(item['status'])} as need "
                      f"'{item['need']}'{config}")
    if info["needs"]:
        print("needs")
    for need, spec in info["needs"].items():
        extra = "".join(f"  {name} {spec[key]}" for key, name in (
            ("contract", "contract"), ("verified-by", "verified by")) if spec[key])
        kind = f" ({spec['kind']}{', optional' if spec['optional'] else ''})" \
            if spec["kind"] else " (optional)" if spec["optional"] else ""
        print(f"  {need}{kind}: {spec['summary']}{extra}")
        for item in spec["provided-by"] or [None]:
            if item is None:
                print("      no provider" + (" (optional)" if spec["optional"] else ""))
                continue
            notes = ([f"alternative '{item['config']}'"] if item.get("config") else []) + item["via"]
            note = f" ({'; '.join(notes)})" if notes else ""
            if item.get("outside"):
                print(f"      provided from outside the project (need '{item['root-need']}' "
                      f"of the root){note}")
            else:
                more = "".join(f"  {name} {item[key]}" for key, name in (
                    ("verified-by", "verified by"),) if item.get(key))
                print(f"      provided by {item['unit']}{mark(item['status'])} capability "
                      f"'{item['capability']}'{note}{more}")
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
                "verified-by": contract_target(project, owner, spec.get("verified-by"))[0] or None,
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
            extra = {"config": item["config"],
                     "via": [{"implicit": "passed up by name"}[v] for v in item["via"]]}
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
        notes = [n for n in ([item.get("config")] + list(item.get("via") or [])) if n]
        note = f" ({'; '.join(notes)})" if notes else ""
        kind = f" ({item['kind']})" if item["kind"] else ""
        side = "capabilities" if item["side"] == "capabilities" else "needs"
        print(f"--- {item['unit']}{mark(item['status'])} {side} '{item['name']}'"
              f"{kind}{note}: {item['summary']}")
        for key, text in (("contract", "contract"), ("verified-by", "verified by")):
            if item.get(key):
                print(f"    {text}: {item[key]}")
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
        print(f"  {item['distance']}  {item['unit']}{mark(item['status'])}: {item['via']}")
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
                    "summary": unit.summary, "parent": unit.parent.rel if unit.parent else None,
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


# ----------------------------------------------- dependencies found in code

BUILD_FILES = {"Cargo.toml", "package.json", "go.mod", "go.work", "pyproject.toml", "setup.py",
               "setup.cfg", "pnpm-workspace.yaml", "lerna.json"}
NOT_SOURCE = {"vendor", "third_party", "testdata", "site-packages"}
PY_TEST_DIRS = {"tests", "test", "testing"}


class Scan:
    """One walk over the repository: build files and source files by folder."""

    def __init__(self, root: str, ignore=()):
        self.root, self.notes = root, []
        self.named: dict = {name: [] for name in BUILD_FILES}
        self.go: dict = {}
        self.py: dict = {}
        self.inits: set = set()
        self._dirs: dict = {}
        ignore = set(ignore)
        for folder, subs, names in os.walk(root):
            rel = "" if folder == root else folder[len(root) + 1:].replace(os.sep, "/")
            keep = []
            for sub in sorted(subs):
                path = os.path.join(folder, sub)
                sub_rel = f"{rel}/{sub}" if rel else sub
                if sub.startswith(".") or sub in NEVER_SCANNED or sub in NOT_SOURCE \
                        or sub_rel in ignore or is_build_output(path):
                    continue
                manifest = os.path.join(path, MANIFEST)
                if os.path.isfile(manifest):
                    try:
                        if ROOT_LINE.search(read_text(manifest)):
                            continue                # a nested project is checked on its own
                    except OSError:
                        pass
                keep.append(sub)
            subs[:] = keep
            for name in names:
                if (f"{rel}/{name}" if rel else name) in ignore:
                    continue
                if name in BUILD_FILES:
                    self.named[name].append(os.path.join(folder, name))
                elif name.endswith(".go"):
                    self.go.setdefault(folder, []).append(name)
                elif name.endswith(".py"):
                    self.py.setdefault(folder, []).append(name)
                    if name == "__init__.py":
                        self.inits.add(folder)

    def rel(self, path: str) -> str:
        return "." if path == self.root else path[len(self.root) + 1:].replace(os.sep, "/")

    def isdir(self, path: str) -> bool:
        found = self._dirs.get(path)
        if found is None:
            found = self._dirs[path] = os.path.isdir(path)
        return found


def under(path: str, folder: str) -> bool:
    return path == folder or path.startswith(folder + os.sep)


def glob_match(rel: str, patterns) -> bool:
    """Does a relative folder match one of the workspace patterns (`packages/*`, `apps/**`)?"""
    for pattern in patterns:
        if not isinstance(pattern, str):
            continue
        pattern = os.path.normpath(pattern.strip()).replace(os.sep, "/").strip("/")
        regex = ""
        for part in re.split(r"(\*\*/?|\*|\?)", pattern):
            regex += {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}.get(part) \
                or re.escape(part)
        if re.fullmatch(regex, rel):
            return True
    return False


class Edges:
    def __init__(self, scan: Scan):
        self.scan, self.found = scan, {}

    def add(self, source: str, target: str, kind: str, evidence: str):
        key = (self.scan.rel(source), self.scan.rel(target), kind)
        if key[0] != key[1]:
            self.found.setdefault(key, evidence)

    def list(self) -> list:
        return [{"from": a, "to": b, "kind": kind, "evidence": evidence}
                for (a, b, kind), evidence in sorted(self.found.items())]


def extract_cargo(scan: Scan, edges: Edges, covered: dict):
    tomls = {}
    for path in scan.named["Cargo.toml"]:
        data, error = load_toml(path)
        if error:
            scan.notes.append(error)
        elif isinstance(data, dict):
            tomls[os.path.dirname(path)] = data
    roots = [d for d in tomls if isinstance(tomls[d].get("workspace"), dict)]

    def workspace_of(folder):
        found = [r for r in roots if under(folder, r)]
        return max(found, key=len) if found else None

    def is_package(folder):
        return isinstance(tomls.get(folder, {}).get("package"), dict)

    members = set()
    for root in roots:
        space = tomls[root]["workspace"]
        patterns = space.get("members") if isinstance(space.get("members"), list) else []
        excluded = space.get("exclude") if isinstance(space.get("exclude"), list) else []
        if is_package(root):
            members.add(root)
        for folder in tomls:
            if folder != root and under(folder, root) and is_package(folder):
                rel = os.path.relpath(folder, root).replace(os.sep, "/")
                if glob_match(rel, patterns) and not any(
                        glob_match(rel, [e]) or rel.startswith(str(e).strip("/") + "/")
                        for e in excluded):
                    members.add(folder)
    for folder in tomls:
        if is_package(folder) and not any(o != folder and under(folder, o) for o in tomls):
            members.add(folder)

    def dependencies(folder):
        data = tomls[folder]
        tables = [(name, data.get(name)) for name in
                  ("dependencies", "dev-dependencies", "build-dependencies")]
        targets = data.get("target")
        if isinstance(targets, dict):
            for target in targets.values():
                if isinstance(target, dict):
                    tables += [(name, target.get(name)) for name in
                               ("dependencies", "dev-dependencies", "build-dependencies")]
        for section, table in tables:
            if not isinstance(table, dict):
                continue
            for name, spec in table.items():
                if not isinstance(spec, dict):
                    continue
                base = folder
                if spec.get("workspace") is True:
                    base = workspace_of(folder)
                    shared = tomls.get(base, {}).get("workspace", {}).get("dependencies", {}) \
                        if base else {}
                    spec = shared.get(name) if isinstance(shared, dict) else None
                if isinstance(spec, dict) and isinstance(spec.get("path"), str):
                    yield section, name, os.path.normpath(os.path.join(base, spec["path"]))

    def source_folder(folder):
        """Where the code of a package lies, if not in the package folder itself.

        A package may keep the sources of its library and binaries elsewhere
        (`[[bin]] path = "crates/core/main.rs"`). If all of them lie in one folder below
        the package folder, the dependencies belong to that folder, which may be a unit.
        """
        data, paths = tomls[folder], []
        lib = data.get("lib")
        bins = data.get("bin") if isinstance(data.get("bin"), list) else []
        if isinstance(lib, dict) and isinstance(lib.get("path"), str):
            paths.append(lib["path"])
        elif os.path.isfile(os.path.join(folder, "src", "lib.rs")):
            paths.append("src/lib.rs")
        for target in bins:
            if isinstance(target, dict) and isinstance(target.get("path"), str):
                paths.append(target["path"])
        if data["package"].get("autobins") is not False and (
                not bins or any(isinstance(t, dict) and "path" not in t for t in bins)):
            if os.path.isfile(os.path.join(folder, "src", "main.rs")):
                paths.append("src/main.rs")
            if os.path.isdir(os.path.join(folder, "src", "bin")):
                paths.append("src/bin/x.rs")
        folders = {os.path.dirname(os.path.normpath(os.path.join(folder, p))) for p in paths}
        if not folders:
            return folder, ""
        common = os.path.commonpath(sorted(folders)) if len(folders) > 1 else folders.pop()
        if not under(common, folder) or common == folder or under(common, os.path.join(folder, "src")):
            return folder, ""
        return common, f" (its code is in {scan.rel(common)})"

    queue, done, code_at = sorted(members), set(), set()
    while queue:
        folder = queue.pop()
        if folder in done:
            continue
        done.add(folder)
        code, where = source_folder(folder)
        code_at.add(code)
        for section, name, target in dependencies(folder):
            if not is_package(target):
                continue
            kind = "cargo-dev" if section == "dev-dependencies" else "cargo"
            source = code if section == "dependencies" else folder
            edges.add(source, target, kind,
                      f"{scan.rel(os.path.join(folder, 'Cargo.toml'))} [{section}] {name}"
                      + (where if source is not folder else ""))
            if target not in done:
                queue.append(target)
    if done:
        covered["cargo"] = set(done) | code_at


def extract_npm(scan: Scan, edges: Edges, covered: dict):
    found = {}
    for path in scan.named["package.json"]:
        try:
            data = json.loads(read_text(path))
        except (OSError, ValueError) as exc:
            scan.notes.append(f"{scan.rel(path)}: not readable as JSON: {exc}")
            continue
        if isinstance(data, dict):
            found[os.path.dirname(path)] = data
    spaces = {}
    for folder, data in found.items():
        patterns = data.get("workspaces")
        if isinstance(patterns, dict):
            patterns = patterns.get("packages")
        if isinstance(patterns, list):
            spaces[folder] = list(patterns)
    for path in scan.named["pnpm-workspace.yaml"]:
        try:
            data = yaml.safe_load(read_text(path))
        except (OSError, yaml.YAMLError):
            continue
        if isinstance(data, dict) and isinstance(data.get("packages"), list):
            spaces.setdefault(os.path.dirname(path), []).extend(data["packages"])
    for path in scan.named["lerna.json"]:
        try:
            data = json.loads(read_text(path))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and isinstance(data.get("packages"), list):
            spaces.setdefault(os.path.dirname(path), list(data["packages"]))
    members = {}
    for root in sorted(spaces, key=len, reverse=True):
        patterns = [p for p in spaces[root] if isinstance(p, str)]
        wanted = [p for p in patterns if not p.startswith("!")]
        unwanted = [p[1:] for p in patterns if p.startswith("!")]
        if root in found:
            members.setdefault(root, root)
        for folder in found:
            if folder != root and under(folder, root):
                rel = os.path.relpath(folder, root).replace(os.sep, "/")
                if glob_match(rel, wanted) and not glob_match(rel, unwanted):
                    members.setdefault(folder, root)
    if scan.root in found:
        members.setdefault(scan.root, scan.root)
    names = {}
    for folder, root in members.items():
        if isinstance(found[folder].get("name"), str):
            names[(root, found[folder]["name"])] = folder
    for folder, root in sorted(members.items()):
        data = found[folder]
        for section in ("dependencies", "devDependencies", "peerDependencies",
                        "optionalDependencies"):
            table = data.get(section)
            if not isinstance(table, dict):
                continue
            for name, spec in table.items():
                target = None
                if isinstance(spec, str) and spec.startswith(("file:", "link:", "portal:")):
                    target = os.path.normpath(os.path.join(folder, spec.split(":", 1)[1]))
                    target = target if target in found else None
                target = target or names.get((root, name))
                if target and target != folder:
                    edges.add(folder, target, "npm",
                              f"{scan.rel(os.path.join(folder, 'package.json'))} {section} {name}")
    if len(members) > 1:
        covered["npm"] = set(members)


GO_DECL = re.compile(r"^(?:func|type|var|const)\b", re.M)
GO_IMPORT = re.compile(r"\bimport\s*(?:\(([^)]*)\)|(?:[\w.]+\s+)?\"([^\"]+)\")")


def go_imports(text: str) -> list:
    cut = GO_DECL.search(text)
    head = text[:cut.start()] if cut else text
    head = re.sub(r"/\*.*?\*/", "", head, flags=re.S)
    head = re.sub(r"(?m)^\s*//[^\n]*", "", head)
    out = []
    for block, single in GO_IMPORT.findall(head):
        out += re.findall(r"\"([^\"]+)\"", block) if block else [single]
    return out


def extract_go(scan: Scan, edges: Edges, covered: dict, skip_sources=False):
    modules = {}
    for path in scan.named["go.mod"]:
        try:
            match = re.search(r"^module\s+(\S+)", read_text(path), re.M)
        except OSError:
            continue
        if match:
            modules[os.path.dirname(path)] = match.group(1).strip('"')
    if not modules:
        return
    ordered = sorted(modules.items(), key=lambda kv: -len(kv[1]))
    prefixes = tuple(path for _, path in ordered)
    dirs = sorted(modules, key=len, reverse=True)
    sources = set()
    for folder, names in sorted(scan.go.items()):
        module = next((d for d in dirs if under(folder, d)), None)
        if module is None:
            continue
        for name in sorted(names):
            is_test = name.endswith("_test.go")
            if not is_test:
                sources.add(folder)
            if skip_sources:
                continue
            path = os.path.join(folder, name)
            try:
                if os.path.getsize(path) > 2_000_000:
                    continue
                text = read_text(path)
            except OSError:
                continue
            for imported in go_imports(text):
                if not imported.startswith(prefixes):
                    continue
                for target_module, module_path in ordered:
                    if imported == module_path or imported.startswith(module_path + "/"):
                        target = os.path.normpath(os.path.join(
                            target_module, *imported[len(module_path):].strip("/").split("/")))
                        if target != folder and scan.isdir(target):
                            edges.add(folder, target, "go-dev" if is_test else "go",
                                      f"{scan.rel(path)} imports {imported}")
                        break
    covered["go"] = sources


def py_is_test(folder_rel: str, name: str) -> bool:
    return bool(PY_TEST_DIRS.intersection(folder_rel.split("/"))) or name.startswith("test_") \
        or name.endswith("_test.py") or name == "conftest.py"


def py_imports(text: str) -> list:
    """(level, module parts, [imported names]) of every import statement."""
    import ast
    out = []
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        for match in re.finditer(r"^[ \t]*(?:from[ \t]+(\.*)([\w.]*)[ \t]+import[ \t]+([^\n#]+)"
                                 r"|import[ \t]+([^\n#]+))", text, re.M):
            if match.group(4):
                for item in match.group(4).split(","):
                    name = item.split(" as ")[0].strip()
                    if re.fullmatch(r"[\w.]+", name):
                        out.append((0, name.split("."), []))
            else:
                names = [n.split(" as ")[0].strip() for n in match.group(3).strip("() ").split(",")]
                out.append((len(match.group(1)), [p for p in match.group(2).split(".") if p],
                            [n for n in names if re.fullmatch(r"\w+", n)]))
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [(0, alias.name.split("."), []) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            out.append((node.level or 0, node.module.split(".") if node.module else [],
                        [alias.name for alias in node.names if alias.name != "*"]))
    return out


def extract_python(scan: Scan, edges: Edges, covered: dict, skip_sources=False):
    projects = {}                                 # folder -> its build file
    for path in scan.named["pyproject.toml"]:
        data, error = load_toml(path)
        if error:
            scan.notes.append(error)
            continue
        folder = os.path.dirname(path)
        tool = data.get("tool") if isinstance(data.get("tool"), dict) else {}
        project = data.get("project") if isinstance(data.get("project"), dict) else \
            tool.get("poetry") if isinstance(tool.get("poetry"), dict) else None
        if project and isinstance(project.get("name"), str):
            projects[folder] = path
    for path in scan.named["setup.cfg"]:
        folder = os.path.dirname(path)
        if folder in projects:
            continue
        import configparser
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read_string(read_text(path))
            name = parser.get("metadata", "name", fallback="")
        except (OSError, configparser.Error):
            continue
        if name and not name.startswith(("attr:", "file:")):
            projects[folder] = path
    for path in scan.named["setup.py"]:
        folder = os.path.dirname(path)
        if folder in projects:
            continue
        try:
            text = read_text(path)
        except OSError:
            continue
        name = re.search(r"\bname\s*=\s*[\"']([^\"']+)[\"']", text)
        if name:
            projects[folder] = path
    if not scan.py:
        return
    covered["python"] = {folder for folder, names in scan.py.items()
                         if any(not py_is_test(scan.rel(folder), n) for n in names)}
    if skip_sources:
        return
    tops = {}                                         # top-level name -> [folder or file]
    for folder in scan.inits:
        if os.path.dirname(folder) not in scan.inits:
            tops.setdefault(os.path.basename(folder), []).append(folder)
    roots = {os.path.dirname(f) for found in tops.values() for f in found} | set(projects) \
        | {os.path.join(p, "src") for p in projects}
    for root in roots:
        if root in scan.inits:
            continue
        for name in scan.py.get(root, ()):
            if name not in ("setup.py", "conftest.py", "__init__.py"):
                tops.setdefault(name[:-3], []).append(os.path.join(root, name))

    def descend(start: str, parts: list) -> str:
        """The deepest folder that the dotted path names, starting in `start`."""
        current = start
        for part in parts:
            deeper = os.path.join(current, part)
            if deeper in scan.py or scan.isdir(deeper) and deeper in scan.inits:
                current = deeper
            else:
                break
        return current

    def resolve(parts: list, source: str):
        found = tops.get(parts[0])
        if not found:
            return None
        if len(found) > 1:
            scored = sorted(found, key=lambda f: len(os.path.commonpath([f, source])),
                            reverse=True)
            if len(os.path.commonpath([scored[0], source])) == \
                    len(os.path.commonpath([scored[1], source])):
                return None                           # ambiguous: do not guess
            found = scored
        first = found[0]
        if first.endswith(".py") and not scan.isdir(first):
            return os.path.dirname(first)
        return descend(first, parts[1:])

    for folder, names in sorted(scan.py.items()):
        folder_rel = scan.rel(folder)
        for name in sorted(names):
            path = os.path.join(folder, name)
            try:
                if os.path.getsize(path) > 1_000_000:
                    continue
                text = read_text(path)
            except OSError:
                continue
            if "import" not in text:
                continue
            kind = "python-dev" if py_is_test(folder_rel, name) else "python"
            for level, module, imported in py_imports(text):
                targets = []
                if level:
                    base = folder
                    for _ in range(level - 1):
                        base = os.path.dirname(base)
                    if not under(base, scan.root):
                        continue
                    for item in imported or [None]:
                        targets.append(descend(base, module + ([item] if item else [])))
                elif module:
                    for item in imported or [None]:
                        targets.append(resolve(module + ([item] if item else []), path))
                dotted = "." * level + ".".join(module)
                for target in targets:
                    if target and target != folder and under(target, scan.root):
                        edges.add(folder, target, kind, f"{scan.rel(path)} imports {dotted}")


def extract(root: str, ignore=(), owner=None) -> dict:
    """Find the dependencies between folders of a repository.

    `owner` maps a folder to its unit; where all sources of a language lie in one unit,
    its files are not read.
    """
    scan = Scan(root, ignore)
    edges, covered = Edges(scan), {}

    def one_owner(folders) -> bool:
        return owner is not None and len({owner(f) for f in folders}) < 2

    extract_cargo(scan, edges, covered)
    extract_npm(scan, edges, covered)
    extract_go(scan, edges, covered, skip_sources=one_owner(scan.go))
    extract_python(scan, edges, covered, skip_sources=one_owner(scan.py))
    return {"edges": edges.list(), "covered": covered, "notes": scan.notes}


def covered_units(project: Project, covered: dict) -> dict:
    """{ecosystem: units that contain extracted code}."""
    out = {}
    for eco, folders in covered.items():
        units = set()
        for folder in folders:
            kind, unit = project.owner_of(folder)
            while kind == "unit" and unit is not None and unit not in units:
                units.add(unit)
                unit = unit.parent
        out[eco] = units
    return out


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
    """The root manifest that `init` writes: the version, the name, and a summary to fill in."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        name = json.dumps(name, ensure_ascii=False)
    return (f"# yaml-language-server: $schema={SITE_URL}/{SPEC_VERSIONS[-1]}/unifold.schema.json\n"
            f"unifold: \"{SPEC_VERSIONS[-1]}\"\nname: {name}\nsummary: TODO\n")


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
    agent with the skill `unifold-convert`; this tool only checks them against the code. A
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
        result["notes"].append("the root manifest says `summary: TODO`. The units of the "
                               "repository are written by hand or with the skill "
                               "`unifold-convert`; this tool drafts none from the code")
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

SITE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ · unifold</title>
<style>
:root{--bg:#fff;--fg:#1c1e21;--mute:#667;--line:#d6d9de;--hi:#0b62d6;--panel:#f6f7f9;--warn:#9a5b00;--warnbg:#fff4d6}
@media(prefers-color-scheme:dark){:root{--bg:#16181c;--fg:#e6e8eb;--mute:#9aa3ad;--line:#333a44;--hi:#6cb0ff;--panel:#1e2228;--warn:#ffcf70;--warnbg:#3a2f12}}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg);display:flex;min-height:100vh}
nav{width:260px;flex:none;border-right:1px solid var(--line);background:var(--panel);padding:12px;overflow:auto;max-height:100vh;position:sticky;top:0}
nav ul{list-style:none;margin:0;padding-left:14px}nav>ul{padding-left:0}
nav a{display:block;padding:2px 6px;border-radius:4px;color:var(--fg);text-decoration:none;cursor:pointer}
nav a.on{background:var(--hi);color:#fff}nav a:hover{outline:1px solid var(--line)}
main{flex:1;min-width:0;padding:16px 24px}a{color:var(--hi)}
h1{font-size:22px;margin:.2em 0}h2{font-size:17px;margin:1.2em 0 .3em}.mute{color:var(--mute)}.crumbs a,.go{cursor:pointer}
.badge{display:inline-block;font-size:12px;padding:0 7px;border-radius:9px;border:1px solid var(--line);color:var(--mute);vertical-align:middle}
.badge.planned,.badge.deprecated,.badge.proposed{color:var(--warn);background:var(--warnbg);border-color:var(--warn)}
.tabs button{font:inherit;padding:4px 12px;margin-right:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:6px;cursor:pointer}
.tabs button.on{background:var(--hi);color:#fff;border-color:var(--hi)}
#diagram{border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0;overflow:auto;background:var(--bg);max-height:85vh}
#diagram svg{max-width:none;height:auto;display:block}#diagram.fit svg{max-width:100%}#diagram .pick{cursor:pointer}#diagram pre{margin:8px 0 0;font-size:12px}
#diagram .cluster rect{fill:var(--panel)!important;stroke:var(--line)!important}
#zoom{float:right;font:inherit;font-size:13px;padding:2px 10px;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:6px;cursor:pointer}
.st{display:inline-block;width:9px;height:9px;border-radius:50%;margin-left:6px;vertical-align:baseline;border:1.5px dashed currentColor;opacity:.75}
.st.deprecated{border-style:solid;background:linear-gradient(to top right,transparent 44%,currentColor 44% 56%,transparent 56%)}
nav .legend{margin:14px 6px 0;font-size:12px;color:var(--mute)}nav .legend .st{margin:0 4px 0 0}
table{border-collapse:collapse;margin:8px 0;width:100%}th,td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}
th{background:var(--panel)}code{background:var(--panel);padding:0 4px;border-radius:3px}
@media(max-width:800px){body{display:block}nav{width:auto;max-height:none;position:static}}
</style></head><body>
<nav id="tree"></nav>
<main>
<div class="crumbs mute" id="crumbs"></div>
<h1 id="title"></h1><p id="summary"></p><p class="mute" id="meta"></p>
<div class="tabs"><button id="zoom" hidden></button><span id="tabs"></span></div>
<div id="diagram">Loading the diagram renderer…</div>
<div id="shared"></div>
<p class="mute">Click a box to open that unit. An arrow points from a need to its provider. A dashed border marks a unit that is planned.</p>
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
const ref = v => v ? (/^[a-z][a-z0-9+.-]*:/i.test(v) ? `<a href="${esc(v)}">${esc(v)}</a>` : `<a href="${esc(file(v))}">${esc(v)}</a>`) : "";
let mermaid = null, mermaidError = null, fit = null, fitted = false, state = {path: ".", kind: null};
function zoom(){const box = el("diagram"), svg = box.querySelector("svg"), b = el("zoom");
  box.classList.remove("fit"); const room = box.clientWidth - 24, width = svg ? svg.getBoundingClientRect().width : 0;
  const wide = width > room; fitted = wide && (fit ?? width <= room * 1.45);   // a little too wide: shrink; much too wide: scroll
  b.hidden = !wide; box.classList.toggle("fit", fitted);
  b.textContent = fitted ? "Full size" : "Fit to width"; box.scrollLeft = 0;}
function fromHash(){const h = decodeURIComponent(location.hash.slice(1)); const [p, k] = h.split("@");
  state = {path: byPath[p] ? p : ".", kind: k || null};}
function go(path, kind){location.hash = encodeURIComponent(path + (kind ? "@" + kind : ""));}
function tree(path){const u = byPath[path]; const kids = u.children.map(c => tree(c.path)).join("");
  return `<li><a data-path="${esc(path)}" class="go${path === state.path ? " on" : ""}">${esc(u.name)}${u.status !== "active" ? `<span class="st ${esc(u.status)}" title="${esc(u.status)}"></span>` : ""}</a>${kids ? "<ul>" + kids + "</ul>" : ""}</li>`;}
const legend = ["planned", "deprecated"].filter(s => units.some(u => u.status === s))
  .map(s => `<span class="st ${s}"></span>${s}`).join(" &nbsp; ");
function note(i){const n = [].concat(i.config ? [i.config] : [], i.via || []); return n.length ? " <span class='mute'>(" + esc(n.join("; ")) + ")</span>" : "";}
function who(list, key){return list.map(i => i.outside ? "outside the project" + note(i)
  : pick(i.unit) + " · <code>" + esc(i[key]) + "</code>" + note(i)).join("<br>") || "–";}
function code(text){return esc(text).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/^- /, "");}
async function render(){
  const u = byPath[state.path]; const kinds = Object.keys(u.diagrams);
  const kind = kinds.includes(state.kind) ? state.kind : (kinds.includes("component") ? "component" : kinds[0]);
  document.title = u.name + " · " + model.name;
  el("tree").innerHTML = "<ul>" + tree(".") + "</ul>" + (legend ? `<p class="legend">${legend}</p>` : "");
  const chain = []; for (let p = u.parent; p; p = byPath[p.path].parent) chain.unshift(p.path);
  el("crumbs").innerHTML = chain.map(p => `<a class="go" data-path="${esc(p)}">${esc(byPath[p].name)}</a>`).concat(esc(u.name)).join(" / ");
  el("title").innerHTML = esc(u.name) + badge(u.status); el("summary").textContent = u.summary;
  el("meta").innerHTML = [u.kind, u.owner && "owner " + u.owner].filter(Boolean).map(esc)
    .concat([`<a href="${esc(file(u.manifest))}">manifest</a>`], u.readme ? [`<a href="${esc(file(u.readme))}">README</a>`] : [],
            u.agents ? [`<a href="${esc(file(u.agents))}">AGENTS.md</a>`] : []).join(" · ");
  el("tabs").innerHTML = kinds.map(k => `<button data-kind="${k}" class="${k === kind ? "on" : ""}">${k}</button>`).join("");
  let html = "";
  const p = Object.entries(u.capabilities), n = Object.entries(u.needs);
  if (p.length) html += "<h2>Capabilities</h2><table><tr><th>Capability</th><th>Kind</th><th>Summary</th><th>Contract</th><th>Verified by</th><th>Used by</th></tr>"
    + p.map(([k, v]) => `<tr><td><code>${esc(k)}</code></td><td>${esc(v.kind)}</td><td>${esc(v.summary)}</td><td>${ref(v.contract)}</td><td>${ref(v["verified-by"])}</td><td>${who(v["used-by"], "need")}</td></tr>`).join("") + "</table>";
  if (n.length) html += "<h2>Needs</h2><table><tr><th>Need</th><th>Kind</th><th>Summary</th><th>Provided by</th></tr>"
    + n.map(([k, v]) => `<tr><td><code>${esc(k)}</code>${v.optional ? " <span class='mute'>optional</span>" : ""}</td><td>${esc(v.kind)}</td><td>${esc(v.summary)}</td><td>${who(v["provided-by"], "capability")}</td></tr>`).join("") + "</table>";
  if (u.children.length) html += "<h2>Units inside</h2><table><tr><th>Unit</th><th>Summary</th></tr>"
    + u.children.map(c => `<tr><td>${pick(c.path, c.name)}</td><td>${esc(c.summary)}</td></tr>`).join("") + "</table>";
  if (u.skills.length) html += "<h2>Skills</h2><ul>" + u.skills.map(s => `<li><a href="${esc(file(s.path))}">${esc(s.name)}</a>: ${esc(s.description)}</li>`).join("") + "</ul>";
  if (u.decisions.length) html += "<h2>Decisions</h2><ul>" + u.decisions.map(d => `<li><a href="${esc(file(d.path))}">${esc(d.title)}</a>${badge(d.status || "no status")}</li>`).join("") + "</ul>";
  el("info").innerHTML = html;
  const d = u.diagrams[kind];
  el("shared").innerHTML = d && d.shared.length ? "<p class='mute'>Shared connections, not drawn:</p><ul>" + d.shared.map(s => "<li>" + code(s) + "</li>").join("") + "</ul>" : "";
  el("zoom").hidden = true;
  if (!d) { el("diagram").textContent = "No diagram for this unit."; return; }
  if (!mermaid) {
    if (mermaidError) el("diagram").innerHTML = "<p>The diagram renderer (Mermaid) could not be loaded" + (MERMAID.url ? " from " + esc(MERMAID.url) : "")
      + ". The tables below are complete without it. To embed the renderer in this page: <code>unifold site --mermaid path/to/mermaid.min.js</code>.</p><details><summary>Diagram source</summary><pre>" + esc(d.source) + "</pre></details>";
    return;
  }
  try {
    const {svg} = await mermaid.render("g" + Date.now(), d.source);
    el("diagram").innerHTML = svg; zoom();
    for (const node of el("diagram").querySelectorAll("[id]")) {
      const hit = Object.keys(d.nodes).find(id => node.id === id || new RegExp("(^|-)" + id + "(-\\d+)?$").test(node.id));
      if (hit && (node.classList.contains("node") || node.classList.contains("cluster"))) {
        node.classList.add("pick"); node.addEventListener("click", ev => {ev.stopPropagation(); go(d.nodes[hit]);});
      }
    }
  } catch (err) { el("diagram").innerHTML = "<p>The diagram could not be drawn: " + esc(err) + "</p><pre>" + esc(d.source) + "</pre>"; }
}
document.addEventListener("click", ev => {
  const a = ev.target.closest(".go"); if (a) { go(a.dataset.path); return; }
  const b = ev.target.closest("button[data-kind]"); if (b) go(state.path, b.dataset.kind);
  if (ev.target.id === "zoom") { fit = !fitted; zoom(); }
});
addEventListener("hashchange", () => { fromHash(); render(); });
async function loadMermaid(){
  if (window.mermaid) return window.mermaid;
  if (!MERMAID.url) throw new Error("no renderer");
  if (/\.mjs(\?|$)/.test(MERMAID.url)) return (await import(MERMAID.url)).default;
  await new Promise((ok, fail) => { const s = document.createElement("script"); s.src = MERMAID.url;
    s.onload = ok; s.onerror = () => fail(new Error("not loaded")); document.head.appendChild(s); });
  return window.mermaid;
}
fromHash(); render();
try {
  mermaid = await loadMermaid();
  mermaid.initialize({startOnLoad: false, securityLevel: "loose", maxEdges: 2000, flowchart: {useMaxWidth: false},
    theme: matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "default"});
} catch (err) { mermaid = null; mermaidError = err; }
render();
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
    for unit in project.units:
        info = describe(project, unit)
        for name, key in (("README.md", "readme"), ("AGENTS.md", "agents")):
            path = os.path.join(unit.path, name)
            info[key] = project.rel(path) if project.kind_of(path) == "file" else None
        charts = {}
        if unit.parent is not None:
            charts["context"] = diagram(project, unit.parent, 0, out_dir, focus=unit)
        elif not unit.children:
            charts["context"] = (lone_context(project, unit, out_dir), [unit],
                                 {node_id(unit): unit}, [])
        if unit.children:
            charts["component"] = diagram(project, unit, 1, out_dir)
        if any(c.children for c in unit.children):
            charts["architecture"] = diagram(project, unit, MAX_DEPTH, out_dir)
        info["diagrams"] = {kind: {"source": "\n".join(value[0]),
                                   "nodes": {i: u.rel for i, u in value[2].items()},
                                   "shared": value[3]} for kind, value in charts.items()}
        units.append(info)
    project.links = saved
    base = saved.rstrip("/") if saved not in ("none", "relative") else ""
    up = os.path.relpath(project.root, out_dir).replace(os.sep, "/")
    model = {"name": project.root_unit.name, "units": units, "base": base,
             "up": "" if up == "." else up + "/"}
    parts = {"__TITLE__": cell(project.root_unit.name).replace("<", "&lt;"),
             "__MODEL__": json.dumps(model, ensure_ascii=False).replace("</", "<\\/"),
             "__MERMAID__": json.dumps(source), "__INLINE__": inline}
    html = re.sub(r"__(?:TITLE|MODEL|MERMAID|INLINE)__", lambda m: parts[m.group()], SITE)
    write_text(out, html)
    return out


# --------------------------------------------------------------- commands

def gather_deps(project: Project, deps_file=None, no_deps=False):
    """Observed dependencies: extracted, plus a given list. Returns (edges, covered units)."""
    edges, covered = [], {}
    if not no_deps and len(project.units) > 1:
        found = extract(project.root, project.ignored_paths(),
                        owner=lambda f: project.owner_of(f)[1])
        edges += found["edges"]
        covered = covered_units(project, found["covered"])
        project.deps_notes = found["notes"]
    if deps_file:
        given = load_deps_file(project, deps_file)
        edges += given
        if no_deps:
            folders = {os.path.join(project.root, *e[side].split("/")) if e[side] != "."
                       else project.root for e in given for side in ("from", "to")}
            covered = covered_units(project, {"given list": folders})
    return edges, covered


def run_check(path: str, fix=False, deps_file=None, no_deps=False, strict=False,
              only=None) -> dict:
    """Check the project that contains `path`. Returns the result as plain data."""
    project = open_project(path, need_usable=False)
    fixed = None
    edges = []
    if project.usable:
        if fix:
            fixed = write_generated(project)
            project = Project(project.root)
        edges, covered = gather_deps(project, deps_file, no_deps)
        mapped = map_edges(project, edges)
        for unit in project.units:
            if not unit.broken:
                check_manifest(project, unit)
            check_wiring(project, unit, mapped[2])
        for unit in project.units:
            check_documents(project, unit)
        check_generated(project)
        check_deps(project, mapped, covered)
    seen, findings = set(), []
    for item in project.findings:
        key = (item["rule"], item["file"], item["line"], item["message"])
        if key not in seen and (not only or item["rule"] in only):
            seen.add(key)
            findings.append(item)
    first = {"M1": 0, "S1": 0}
    findings.sort(key=lambda f: (first.get(f["rule"], 1), sort_key(f["file"]) if f["file"] != "."
                                 else [], f["line"] or 0, SEVERITY_ORDER[f["severity"]],
                                 f["rule"], f["message"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    rules: dict = {}
    for item in findings:
        rules[item["rule"]] = rules.get(item["rule"], 0) + 1
    summary = {"units": len(project.units), **counts, "rules": rules,
               "root": project.root, "tool": TOOL_VERSION,
               "dependencies": {"observed": len(edges),
                                "extracted": not no_deps and len(project.units) > 1,
                                "notes": project.deps_notes}}
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
    for note in summary["dependencies"]["notes"]:
        print(f"note: {note}")
    per_rule = ", ".join(f"{rule}×{count}" for rule, count in sorted(summary["rules"].items()))
    print(f"{summary['units']} unit(s): {summary['error']} error(s), {summary['warn']} "
          f"warning(s), {summary['info']} info" + (f"  [{per_rule}]" if per_rule else "")
          + f"; {summary['dependencies']['observed']} dependencies observed in code")


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


# ----- MCP

MCP_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
MCP_TOOLS = [
    {"name": "show", "description": "One unit of the unifold map: summary, status, capabilities and "
     "needs, who finally provides each need and who uses each capability, skills, decisions, "
     "documents by kind (tutorials, references, explanation), files.",
     "inputSchema": {"type": "object", "properties": {"path": {
         "type": "string", "description": "Folder or file inside the project. Default: the project root."}}}},
    {"name": "capability", "description": "Both ends of every connection of one capability or need: "
     "summaries, contracts, verified-by, status, and the README section of each side.",
     "inputSchema": {"type": "object", "required": ["name"], "properties": {
         "path": {"type": "string", "description": "Folder of the unit."},
         "name": {"type": "string", "description": "Name of a capability or need of that unit."}}}},
    {"name": "impact", "description": "Everything that depends on a unit, or on one of its "
     "capabilities, transitively, with status; and the context items that cite its files.",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Folder of the unit, or a file in it."},
         "capability": {"type": "string", "description": "Limit to one capability of the unit."}}}},
    {"name": "check", "description": "Check the map: manifests, wiring, generated files, "
     "documents, and the comparison with dependencies found in code. Returns "
     "findings with rule, severity, file, line, message and fix. Changes nothing.",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Any folder inside the project."},
         "no_deps": {"type": "boolean", "description": "Skip the comparison with code."}}}},
    {"name": "tree", "description": "The unit tree: path, name, status, summary, capabilities and "
     "needs of every unit.",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Any folder inside the project."},
         "depth": {"type": "integer", "description": "Levels below the root to list."}}}},
]


def mcp_call(name: str, args: dict, base: str):
    path = args.get("path") or "."
    if not isinstance(path, str):
        raise Fail("bad-argument", "'path' must be a string")
    path = path if os.path.isabs(path) else os.path.join(base, path)
    if name == "check":
        return run_check(path, no_deps=bool(args.get("no_deps")))
    project = open_project(path)
    if name == "tree":
        depth = args.get("depth")
        return {"units": tree_data(project, depth if isinstance(depth, int) else None)}
    unit = unit_for(project, path)
    if name == "show":
        return describe(project, unit)
    if name == "capability":
        if not isinstance(args.get("name"), str):
            raise Fail("bad-argument", "'name' is required: the name of a capability or need")
        return capability_data(project, unit, args["name"])
    if name == "impact":
        target = real(path)
        return impact(project, unit, args.get("capability"), target if os.path.isfile(target) else None)
    raise Fail("unknown-tool", f"unknown tool '{name}'")


def mcp_handle(message, base: str):
    """Answer one JSON-RPC message. Returns the response, or None for a notification."""
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" \
            or not isinstance(message.get("method"), str):
        if isinstance(message, dict) and "method" not in message and "id" in message:
            return None                               # a response to us: nothing to do
        return {"jsonrpc": "2.0", "id": message.get("id") if isinstance(message, dict) else None,
                "error": {"code": -32600, "message": "not a JSON-RPC 2.0 request"}}
    method, params = message["method"], message.get("params")
    params = params if isinstance(params, dict) else {}
    if "id" not in message:
        return None
    reply = {"jsonrpc": "2.0", "id": message["id"]}
    if method == "initialize":
        wanted = params.get("protocolVersion")
        reply["result"] = {
            "protocolVersion": wanted if wanted in MCP_VERSIONS else MCP_VERSIONS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "unifold", "version": TOOL_VERSION},
            "instructions": "Read-only access to the unifold architecture map of this "
                            "repository. Start with `tree`, then `show` for a unit."}
    elif method == "ping":
        reply["result"] = {}
    elif method == "tools/list":
        reply["result"] = {"tools": [{**tool, "annotations": {"readOnlyHint": True}}
                                     for tool in MCP_TOOLS]}
    elif method == "tools/call":
        name, args = params.get("name"), params.get("arguments")
        if name not in [tool["name"] for tool in MCP_TOOLS]:
            reply["error"] = {"code": -32602, "message": f"unknown tool: {name}"}
            return reply
        try:
            data = mcp_call(name, args if isinstance(args, dict) else {}, base)
            failed = False
        except Fail as exc:
            data, failed = {"ok": False, "error": {"code": exc.code, "message": exc.message}}, True
        except Exception as exc:                      # the server must survive any call
            data, failed = {"ok": False, "error": {"code": "internal",
                                                   "message": f"{type(exc).__name__}: {exc}"}}, True
        reply["result"] = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}],
                           "structuredContent": data, "isError": failed}
    else:
        reply["error"] = {"code": -32601, "message": f"method not found: {method}"}
    return reply


def serve_mcp(base: str) -> int:
    """Model Context Protocol over stdio: one JSON-RPC message per line."""
    stdin = sys.stdin.buffer
    while True:
        raw = stdin.readline()
        if not raw:
            return 0
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None,
                     "error": {"code": -32700, "message": "parse error"}}
        else:
            if isinstance(message, list):
                reply = [r for r in (mcp_handle(m, base) for m in message) if r is not None] or None
            else:
                reply = mcp_handle(message, base)
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


# ----- command line

COMMANDS = {
    "init": "start a project in DIR (default: here): the root manifest and README.md if there "
            "are none, and the generated files; with --agents also install the skills and the "
            "skill stubs",
    "check": "check manifests, wiring, generated files, documents and the comparison with code",
    "generate": "write diagrams, decision indexes, the AGENTS.md of every unit and, "
                "where they exist, skill stubs",
    "show": "describe the unit that contains PATH, with its resolved neighbours",
    "capability": "print both ends of every connection of one capability or need",
    "impact": "list everything that depends on a unit or capability, and who cites its files",
    "tree": "print the unit tree with status, capabilities and needs",
    "deps": "print the dependencies between folders that the extractors find in code, as JSON",
    "stamp": "write or refresh the stamps of the context items at or below PATH, and print "
             "each one with the source it cites",
    "cited-by": "list the context items and links that cite FILE",
    "skills": "list every skill; `skills sync` writes stubs into .agents/skills and .claude/skills",
    "site": "write the HTML explorer",
    "rules": "print the rules that `check` applies, or one rule",
    "mcp": "serve show, capability, impact, check and tree as MCP tools over stdio",
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
    cmd.add_argument("--deps", metavar="FILE",
                     help="JSON list of further observed dependencies")
    cmd.add_argument("--no-deps", action="store_true",
                     help="do not extract dependencies from code")
    cmd.add_argument("--rule", action="append", metavar="ID",
                     help="report only this rule (repeatable)")
    command("generate")
    command("show")
    cmd = command("capability", path=False)
    cmd.add_argument("path", help="folder of the unit")
    cmd.add_argument("name", help="name of a capability or need of the unit")
    cmd = command("impact", path=False)
    cmd.add_argument("path", help="folder of the unit, or a file in it")
    cmd.add_argument("capability", nargs="?", help="limit to one capability")
    cmd = command("tree")
    cmd.add_argument("--depth", type=int, help="levels below the root to print")
    cmd = command("deps", as_json=False)
    cmd.add_argument("--write", metavar="FILE", help="write the list to FILE instead of printing it")
    cmd.add_argument("--json", action="store_true", help="accepted; the output is always JSON")
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
    command("mcp", as_json=False)
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
                  "skill `unifold-convert`; `unifold check` compares the map with the code." +
                  ("" if args.agents else " `unifold init --agents` sets up coding agents."))
        emit(args, {"ok": True, **result}, text)
        return 0
    if name == "mcp":
        return serve_mcp(os.path.abspath(args.path))
    if name == "check":
        if args.format == "json":
            args.json = True
        result = run_check(args.path, args.fix, args.deps, args.no_deps, args.strict,
                           {r.upper() for r in args.rule} if args.rule else None)
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
    if name == "deps":
        project = open_project(args.path)
        found = extract(project.root, project.ignored_paths())
        text = json.dumps(found["edges"], indent=1, ensure_ascii=False) + "\n"
        for note in found["notes"]:
            sys.stderr.write(f"note: {note}\n")
        if args.write:
            write_text(os.path.abspath(args.write), text)
            sys.stderr.write(f"{len(found['edges'])} dependencies written to {args.write}\n")
        else:
            sys.stdout.write(text)
        return 0
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
