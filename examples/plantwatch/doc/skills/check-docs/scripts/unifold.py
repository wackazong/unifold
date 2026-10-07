#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""unifold reference checker and generator.

Commands (PATH is any folder inside a unifold project, default: current folder):
  check [PATH]        check the project against the tool rules
  generate [PATH]     write diagrams and decision indexes from the manifests
  show [PATH]         one unit: ports, who provides its needs, who uses its ports
  tree [PATH]         the unit tree with status and ports
  skills [PATH]       all skills of the project
  decisions [PATH]    all decision records of the project
  cited-by FILE       managed files that link to FILE
  site [PATH]         write a clickable HTML explorer of the project
  init TARGET         copy the standard (references and skills) into TARGET

The rule IDs printed by `check` are defined in doc/references/unifold/rules-tool.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:                                   # pragma: no cover
    sys.exit("unifold needs the PyYAML package: run it with `uv run`, or install "
             "PyYAML into a virtual environment (python3 -m pip install pyyaml)")

TOOL_VERSION = "0.1"
SPEC_VERSIONS = {"0.1"}
MAX_LINES = 200
MAX_LINE_LENGTH = 400
MAX_WHY_LINES = 20
MAX_DEPTH = 3
MARK = "<!-- unifold:generated - do not edit; run `unifold generate` -->"
MARK_PREFIX = "<!-- unifold:generated"
MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"
SKIP_DIRS = {"node_modules", "target", "__pycache__"}
DOC_FILES = {"context.md", "architecture.md"}
DOC_DIRS = {"decisions", "references", "skills", "diagrams"}
DOC_ENTRIES = DOC_FILES | DOC_DIRS | {"assets"}
ROOT_KEYS = {"unifold", "ignore", "diagram-links", "level"}
LEVELS = {"core", "full"}
# rules that apply at level "core": manifests, wiring, generated files, code edges
CORE_RULES = {"S1", "S2", "S3", "S4"}          # plus every M, W, G and D rule
STANDARD_PATHS = ("doc/references/unifold/", "doc/skills/read-docs/",
                  "doc/skills/write-docs/", "doc/skills/check-docs/")
MANIFEST_KEYS = {"unit", "summary", "kind", "status", "owner", "provides", "needs",
                 "wiring"} | ROOT_KEYS
PROVIDE_KEYS = {"kind", "summary", "contract", "verified-by", "conforms-to"}
NEED_KEYS = {"kind", "summary", "optional", "contract"}
STATUSES = {"planned", "active", "deprecated"}
DECISION_STATUSES = ("proposed", "accepted", "rejected", "deprecated", "superseded")
NOT_IN_FORCE = ("rejected", "deprecated", "superseded")
UNIT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
PORT_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DECISION_FILE = re.compile(r"^\d{4}-[a-z0-9][a-z0-9-]*\.md$")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
INLINE_LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^)]*[\"'])?\s*\)")
REF_LINK = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?\s*$")
CODE_SPAN = re.compile(r"`([^`\n]+)`")


# ---------------------------------------------------------------- parsing

class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, f"duplicate key '{key}'", key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def cell(text) -> str:
    """Text made safe for a Markdown table cell."""
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def parse_yaml(text: str):
    """Return (mapping or None, error or None)."""
    try:
        data = yaml.load(text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        return None, "invalid YAML: " + " ".join(str(exc).split())
    if data is None:
        return {}, None
    if not isinstance(data, dict):
        return None, "must be a YAML mapping"
    return data, None


def front_matter(path: Path):
    """Return (mapping or None, error or None) for the YAML front matter."""
    if not path.is_file():
        return None, None
    lines = read_text(path).splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, "front matter is not closed with '---'"
    return parse_yaml("\n".join(lines[1:end]))


def load_manifest(folder: Path):
    """Return (manifest or None, file it is in or None, error or None).

    The manifest is `unit.yaml`, or the front matter of README.md when that
    front matter contains the key `unit`.
    """
    sidecar, readme = folder / "unit.yaml", folder / "README.md"
    in_readme, error = front_matter(readme)
    readme_has = isinstance(in_readme, dict) and "unit" in in_readme
    if error and not sidecar.is_file():
        head = read_text(readme).split("\n---", 1)[0]
        if re.search(r"^unit\s*:", head, re.M):
            return None, readme, error
    if sidecar.is_file():
        data, error = parse_yaml(read_text(sidecar))
        if error:
            return None, sidecar, error
        if readme_has:
            return None, sidecar, "manifest is in unit.yaml and in README.md; keep one"
        if "unit" not in data:
            return None, sidecar, "unit.yaml has no key 'unit'"
        return data, sidecar, None
    if readme_has:
        return in_readme, readme, None
    return None, None, None


def body_lines(path: Path) -> list[str]:
    """File lines without front matter."""
    lines = read_text(path).splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            return lines[end + 1:]
    return lines


def prose_lines(path: Path) -> list[str]:
    """Lines of a Markdown file outside fenced code blocks."""
    out, fence = [], None
    for line in read_text(path).splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = stripped[:3]
            fence = None if fence == token else (fence or token)
            continue
        if not fence:
            out.append(line)
    return out


def links_in(path: Path) -> list[str]:
    """Link targets in a Markdown file, ignoring code blocks and code spans."""
    out = []
    for line in prose_lines(path):
        line = CODE_SPAN.sub("", line)
        out += INLINE_LINK.findall(line)
        ref = REF_LINK.match(line)
        if ref:
            out.append(ref.group(1))
    return out


def decision_info(path: Path) -> dict:
    meta, error = front_matter(path)
    meta = meta if isinstance(meta, dict) else {}
    title = next((l[2:].strip() for l in body_lines(path) if l.startswith("# ")), path.stem)
    makers = meta.get("decision-makers")
    return {"path": path, "title": title, "status": str(meta.get("status") or ""),
            "date": str(meta.get("date") or ""), "makers": makers, "error": error,
            "has_meta": bool(meta)}


# ------------------------------------------------------------------ model

class Unit:
    def __init__(self, path: Path, manifest: dict, manifest_path: Path,
                 parent: "Unit | None"):
        self.path = path
        self.manifest = manifest
        self.manifest_path = manifest_path
        self.parent = parent
        self.children: list[Unit] = []
        self.foreign: list[Path] = []          # nested projects below this unit
        self.name = str(manifest.get("unit", path.name))
        self.summary = str(manifest.get("summary") or "").strip()
        self.kind = str(manifest.get("kind") or "")
        self.status = str(manifest.get("status", "active"))
        self.own_owner = str(manifest.get("owner") or "")
        self.provides = self._ports("provides")
        self.needs = self._ports("needs")
        self.wiring: dict[str, list[tuple[str | None, str]]] = {}
        self.wildcards: dict[str, list[tuple[str | None, str]]] = {}
        self.wiring_errors: list[str] = []
        self.wildcard_errors: list[str] = []
        raw = manifest.get("wiring")
        if isinstance(raw, dict):
            for key, value in raw.items():
                if isinstance(value, dict) and value:
                    entries = [(str(k), str(v)) for k, v in value.items()]
                elif isinstance(value, str):
                    entries = [(None, value)]
                else:
                    self.wiring_errors.append(
                        f"wiring '{key}': the provider must be one endpoint or a map "
                        "of named alternatives")
                    continue
                if str(key).startswith("*."):
                    self.wildcards[str(key)[2:]] = entries
                else:
                    self.wiring[str(key)] = entries

    def _ports(self, key: str) -> dict:
        raw = self.manifest.get(key)
        if not isinstance(raw, dict):
            return {}
        return {str(k): (v if isinstance(v, dict) else {}) for k, v in raw.items()}

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

    def child(self, name: str) -> "Unit | None":
        return next((c for c in self.children if c.name == name), None)

    def ancestors(self) -> list["Unit"]:
        out, unit = [], self.parent
        while unit is not None:
            out.append(unit)
            unit = unit.parent
        return out

    def depth_below(self, other: "Unit") -> int | None:
        """Levels between self and ancestor `other` (0 if same), else None."""
        depth, unit = 0, self
        while unit is not None:
            if unit is other:
                return depth
            unit, depth = unit.parent, depth + 1
        return None


class Project:
    def __init__(self, root: Path):
        self.root = root
        self.units: list[Unit] = []
        self.findings: list[tuple[str, str, str, str]] = []
        self.foreign: dict[Path, Unit] = {}    # nested project dir -> owning unit
        self.root_unit = None
        manifest, where, error = load_manifest(root)
        if error:
            self.add("E", "M1", where, error)
        if not isinstance(manifest, dict) or "unifold" not in manifest:
            self.add("E", "S1", root, "project root needs a manifest with 'unit' and "
                                      "'unifold' (unit.yaml or README.md front matter)")
            return
        if str(manifest["unifold"]) not in SPEC_VERSIONS:
            self.add("E", "S1", where, f"unifold version '{manifest['unifold']}' is "
                                       f"not supported by this tool {sorted(SPEC_VERSIONS)}")
        ignore = manifest.get("ignore") or []
        self.ignore = {os.path.normpath(str(p)).replace(os.sep, "/").strip("/")
                       for p in ignore} if isinstance(ignore, list) else set()
        self.links = str(manifest.get("diagram-links") or "none")
        self.level = str(manifest.get("level") or "full")
        self.root_unit = Unit(root, manifest, where, None)
        self.units.append(self.root_unit)
        self._walk(root, self.root_unit)
        self.by_path = {u.path: u for u in self.units}
        for unit in self.units:
            self._expand_wildcards(unit)

    def _expand_wildcards(self, unit: "Unit"):
        """`*.need: provider` wires that need of every child that has it."""
        for need, entries in unit.wildcards.items():
            providers = {e.split(".", 1)[0] for _, e in entries if "." in e}
            matched = [c for c in unit.children if need in c.needs and c.name not in providers]
            if not matched:
                unit.wildcard_errors.append(f"wiring key '*.{need}': no child has a need "
                                            f"'{need}'")
            for child in matched:
                unit.wiring.setdefault(f"{child.name}.{need}", entries)

    def add(self, severity: str, rule: str, path: Path, message: str):
        self.findings.append((severity, rule, self.rel(path), message))

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix() or "."
        except ValueError:
            return str(path)

    def _walk(self, folder: Path, owner: Unit):
        for sub in sorted(p for p in folder.iterdir() if p.is_dir()):
            if sub.name.startswith(".") or sub.is_symlink() or self.rel(sub) in self.ignore:
                continue
            if sub.name == "doc" and folder == owner.path:
                continue
            manifest, where, error = load_manifest(sub)
            if sub.name in SKIP_DIRS and manifest is None and not error:
                continue
            if error:
                self.add("E", "M1", where, error)
            current = owner
            if isinstance(manifest, dict):
                if "unifold" in manifest:           # nested project: opaque
                    owner.foreign.append(sub)
                    self.foreign[sub] = owner
                    continue
                current = Unit(sub, manifest, where, owner)
                owner.children.append(current)
                self.units.append(current)
            self._walk(sub, current)

    def owner_of(self, target: Path):
        """Return ('unit', Unit), ('foreign', Path) or (None, None)."""
        try:
            target.relative_to(self.root)
        except ValueError:
            return None, None
        for folder in [target, *target.parents]:
            if folder in self.foreign:
                return "foreign", folder
            if folder in self.by_path:
                return "unit", self.by_path[folder]
        return "unit", self.root_unit

    def unit_at(self, path: Path) -> Unit:
        kind, owner = self.owner_of(path.resolve())
        return owner if kind == "unit" else self.root_unit


def is_root(folder: Path) -> bool:
    """True if a manifest in this folder, valid or not, declares `unifold`."""
    sources = [front_matter(folder / "README.md")[0]]
    if (folder / "unit.yaml").is_file():
        sources.append(parse_yaml(read_text(folder / "unit.yaml"))[0])
    return any(isinstance(m, dict) and "unifold" in m for m in sources)


def find_root(start: Path) -> Path | None:
    folder = start.resolve()
    for candidate in [folder, *folder.parents]:
        if is_root(candidate):
            return candidate
    return None


def managed_files(unit: Unit) -> list[Path]:
    """Markdown files that unifold rules apply to, for one unit."""
    files = [p for p in (unit.path / "README.md", unit.path / "AGENTS.md") if p.is_file()]
    doc = unit.path / "doc"
    files += [doc / name for name in sorted(DOC_FILES) if (doc / name).is_file()]
    for name in sorted(DOC_DIRS):
        if not (doc / name).is_dir():
            continue
        for path in sorted((doc / name).rglob("*.md")):
            parts = path.relative_to(doc).parts
            if parts[0] == "skills" and len(parts) > 2 and parts[2] in ("assets", "scripts"):
                continue
            files.append(path)
    return files


def is_generated(path: Path) -> bool:
    return path.is_file() and read_text(path).lstrip().startswith(MARK_PREFIX)


def skills_of(unit: Unit) -> list[dict]:
    out, folder = [], unit.path / "doc" / "skills"
    if folder.is_dir():
        for sub in sorted(p for p in folder.iterdir() if p.is_dir()):
            meta, _ = front_matter(sub / "SKILL.md")
            meta = meta if isinstance(meta, dict) else {}
            out.append({"name": sub.name, "path": sub / "SKILL.md",
                        "description": str(meta.get("description") or "")})
    return out


def decisions_of(unit: Unit) -> list[dict]:
    folder = unit.path / "doc" / "decisions"
    if not folder.is_dir():
        return []
    return [decision_info(p) for p in sorted(folder.glob("*.md")) if p.name != "index.md"]


# -------------------------------------------------------------- resolution

def implementers(unit: Unit, port: str) -> list[tuple[Unit, str]]:
    """Follow the delegation of a provided port down to the units that implement it."""
    found = []
    for _, endpoint in unit.wiring.get(port, []):
        if "." in endpoint and not endpoint.startswith("./"):
            child = unit.child(endpoint.split(".", 1)[0])
            if child:
                found += implementers(child, endpoint.split(".", 1)[1])
    return found or [(unit, port)]


def need_users(unit: Unit, need: str) -> list[tuple[Unit, str]]:
    """Follow an own need down to the units that actually use it."""
    found = []
    for key, entries in unit.wiring.items():
        if "." in key and any(endpoint == need for _, endpoint in entries):
            child = unit.child(key.split(".", 1)[0])
            if child:
                found += need_users(child, key.split(".", 1)[1])
    return found or [(unit, need)]


def providers_of(unit: Unit, need: str) -> list[dict]:
    """Who meets a need of `unit`, resolved through all levels."""
    parent = unit.parent
    if parent is None:
        return [{"where": "outside", "port": need, "config": None}]
    out = []
    for config, endpoint in parent.wiring.get(f"{unit.name}.{need}", []):
        if endpoint.startswith("./"):
            out.append({"where": "plain", "path": (parent.path / endpoint).resolve(),
                        "port": "", "config": config})
        elif "." in endpoint:
            sibling = parent.child(endpoint.split(".", 1)[0])
            if sibling:
                for target, port in implementers(sibling, endpoint.split(".", 1)[1]):
                    out.append({"where": "unit", "unit": target, "port": port,
                                "config": config})
        else:
            for item in providers_of(parent, endpoint):
                out.append({**item, "config": item["config"] or config})
    return out


def users_of(unit: Unit, port: str) -> list[dict]:
    """Who needs a provided port of `unit`, resolved through all levels."""
    parent = unit.parent
    if parent is None:
        return [{"where": "outside", "need": port}]
    out = []
    for key, entries in parent.wiring.items():
        if not any(endpoint == f"{unit.name}.{port}" for _, endpoint in entries):
            continue
        if "." in key:
            child = parent.child(key.split(".", 1)[0])
            if child:
                for user, need in need_users(child, key.split(".", 1)[1]):
                    out.append({"where": "unit", "unit": user, "need": need})
        else:
            out += users_of(parent, key)
    return out


# ------------------------------------------------------------ check rules

def check_manifest(project: Project, unit: Unit):
    where, m = unit.manifest_path, unit.manifest
    if not unit.is_root and unit.name != unit.path.name:
        project.add("E", "S2", where, f"unit '{unit.name}' must equal the folder name "
                                      f"'{unit.path.name}'")
    if not UNIT_NAME.match(unit.name):
        project.add("E", "M3", where, f"unit name '{unit.name}' must match {UNIT_NAME.pattern}")
    summary = m.get("summary")
    if not isinstance(summary, str) or not summary.strip() or "\n" in summary.strip():
        project.add("E", "M2", where, "manifest needs a one-line 'summary'")
    for key in m:
        if key not in MANIFEST_KEYS and not str(key).startswith("x-"):
            project.add("E", "M5", where, f"unknown manifest key '{key}' (project-specific "
                                          "keys start with 'x-')")
        if key in ROOT_KEYS and not unit.is_root and key != "unifold":
            project.add("E", "M5", where, f"key '{key}' belongs in the root manifest")
    if unit.status not in STATUSES:
        project.add("E", "M6", where, f"status '{unit.status}' must be one of "
                                      f"{sorted(STATUSES)}")
    if unit.is_root and project.level not in LEVELS:
        project.add("E", "M6", where, f"level '{project.level}' must be one of "
                                      f"{sorted(LEVELS)}")
    for section, allowed in (("provides", PROVIDE_KEYS), ("needs", NEED_KEYS)):
        raw = m.get(section)
        if raw is None:
            continue
        if not isinstance(raw, dict):
            project.add("E", "M4", where, f"'{section}' must be a mapping of port names")
            continue
        for port, spec in raw.items():
            if not PORT_NAME.match(str(port)):
                project.add("E", "M3", where, f"port name '{port}' must match "
                                              f"{PORT_NAME.pattern}")
            if not isinstance(spec, dict) or not str(spec.get("summary") or "").strip():
                project.add("E", "M4", where, f"{section}.{port} needs a 'summary'")
                continue
            for key in spec:
                if key not in allowed and not str(key).startswith("x-"):
                    project.add("E", "M5", where, f"unknown key '{key}' in {section}.{port}")
            if "optional" in spec and not isinstance(spec["optional"], bool):
                project.add("E", "M4", where, f"optional of '{port}' must be true or false")
            for field in ("contract", "verified-by"):
                value = spec.get(field)
                if not isinstance(value, str) or SCHEME.match(value):
                    continue
                target = (unit.path / value).resolve()
                if unit.path.resolve() not in [target, *target.parents]:
                    project.add("E", "M7", where, f"{field} of '{port}' points outside "
                                                  f"the unit: {value}")
                elif not target.exists():
                    project.add("W", "M7", where, f"{field} of '{port}' does not exist "
                                                  f"yet: {value}")
            conforms = spec.get("conforms-to")
            if section == "provides" and conforms is not None \
                    and str(conforms) not in unit.needs:
                project.add("E", "M9", where, f"conforms-to of '{port}' must name a need "
                                              f"of this unit, not '{conforms}'")
            if section == "provides" and unit.status == "active" \
                    and not spec.get("verified-by"):
                project.add("W", "M8", where, f"unit is active but port '{port}' has no "
                                              "'verified-by'")
    raw = m.get("wiring")
    if raw is not None and not isinstance(raw, dict):
        project.add("E", "M4", where, "'wiring' must be a mapping of need to provider")
    for message in unit.wiring_errors:
        project.add("E", "M4", where, message)


def check_wiring(project: Project, unit: Unit):
    where = unit.manifest_path
    names = [c.name for c in unit.children]
    for name in sorted({n for n in names if names.count(n) > 1}):
        project.add("E", "S4", where, f"two child units are named '{name}'")
    used_providers: set[str] = set()
    used_own_needs: set[str] = set()
    graph: dict[str, set[str]] = {}
    for key, entries in unit.wiring.items():
        need_kind, key_child = None, None
        if "." in key:
            key_child, need = key.split(".", 1)
            child = unit.child(key_child)
            if child is None:
                project.add("E", "W1", where, f"wiring key '{key}': no child unit "
                                              f"'{key_child}'")
            elif need not in child.needs:
                project.add("E", "W1", where, f"wiring key '{key}': '{key_child}' "
                                              f"has no need '{need}'")
            else:
                need_kind = child.needs[need].get("kind")
        elif key not in unit.provides:
            project.add("E", "W1", where, f"wiring key '{key}': not a provided port of "
                                          f"'{unit.name}'")
        else:
            need_kind = unit.provides[key].get("kind")
        for _, value in entries:
            kind = None
            if value.startswith("./"):
                target = (unit.path / value).resolve()
                kind_of, owner = project.owner_of(target)
                if not target.is_dir() or unit.path.resolve() not in target.parents:
                    project.add("E", "W1", where, f"wiring '{key}: {value}': not a folder "
                                                  "inside this unit")
                elif kind_of == "unit" and owner is not unit:
                    project.add("E", "W1", where, f"wiring '{key}: {value}': the folder "
                                                  f"belongs to unit '{owner.name}'; name "
                                                  "its port instead")
                else:
                    project.add("I", "W8", where, f"'{key}' is provided by {value}, which "
                                                  "is not a unit yet")
            elif "." in value:
                child_name, port = value.split(".", 1)
                child = unit.child(child_name)
                if child is None:
                    project.add("E", "W1", where, f"wiring '{key}: {value}': no child "
                                                  f"unit '{child_name}'")
                elif port not in child.provides:
                    project.add("E", "W1", where, f"wiring '{key}: {value}': "
                                                  f"'{child_name}' does not provide '{port}'")
                else:
                    kind = child.provides[port].get("kind")
                    used_providers.add(value)
                    if key_child == child_name:
                        project.add("E", "W1", where, f"wiring '{key}: {value}': a unit "
                                                      "cannot provide its own need")
                    elif key_child:
                        graph.setdefault(key_child, set()).add(child_name)
            elif "." not in key:
                project.add("E", "W1", where, f"wiring '{key}: {value}': a provided port "
                                              "cannot be wired straight to an own need")
            elif value not in unit.needs:
                project.add("E", "W1", where, f"wiring '{key}: {value}': not a need of "
                                              f"'{unit.name}'")
            else:
                kind = unit.needs[value].get("kind")
                used_own_needs.add(value)
            if need_kind and kind and need_kind != kind:
                project.add("W", "W4", where, f"wiring '{key}: {value}': kinds differ "
                                              f"({need_kind} vs {kind}); put an adapter "
                                              "unit between them")
        definitions = alternative_definitions(unit, entries)
        if len(entries) > 1 and None not in definitions and len(set(definitions)) > 1:
            project.add("W", "W10", where, f"wiring '{key}': the alternatives conform to "
                                           "different definitions")
    for message in unit.wildcard_errors:
        project.add("E", "W1", where, message)
    for child in unit.children:
        for need, spec in child.needs.items():
            if f"{child.name}.{need}" not in unit.wiring and spec.get("optional") is not True:
                project.add("E", "W2", where, f"need '{child.name}.{need}' is not wired")
            if child.status == "active":
                for item in providers_of(child, need):
                    if item["where"] == "unit" and item["unit"].status == "planned":
                        project.add("W", "W9", where, f"active unit '{child.name}' needs "
                                                      f"'{need}' from '{item['unit'].name}', "
                                                      "which is only planned")
        for port in child.provides:
            if f"{child.name}.{port}" not in used_providers:
                project.add("W", "W3", where, f"'{child.name}.{port}' is provided but "
                                              "nothing needs it")
    if unit.children:
        for need in unit.needs:
            if need not in used_own_needs:
                project.add("I", "W5", where, f"own need '{need}' is not passed to any "
                                              "child (used by this unit's own code?)")
        for port in unit.provides:
            if port not in unit.wiring:
                project.add("I", "W6", where, f"provided port '{port}' is not delegated "
                                              "to a child (implemented by this unit's own code?)")
    for cycle in find_cycles(graph):
        project.add("W", "W7", where, "children need each other in a cycle: "
                                      + " -> ".join(cycle + [cycle[0]]))


def alternative_definitions(unit: Unit, entries) -> list:
    """For each alternative provider: what its port says it conforms to, resolved."""
    out = []
    for _, endpoint in entries:
        found = None
        if "." in endpoint and not endpoint.startswith("./"):
            child = unit.child(endpoint.split(".", 1)[0])
            if child:
                target, port = implementers(child, endpoint.split(".", 1)[1])[0]
                need = target.provides.get(port, {}).get("conforms-to")
                if isinstance(need, str) and need in target.needs:
                    found = frozenset(
                        (str(i.get("unit").path) if i["where"] == "unit" else i["where"],
                         i["port"]) for i in providers_of(target, need))
        out.append(found)
    return out


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """One cycle per group of nodes that can reach each other (linear time)."""
    index, low, on_stack, stack, groups = {}, {}, set(), [], []

    def visit(node: str):
        index[node] = low[node] = len(index)
        stack.append(node)
        on_stack.add(node)
        for target in sorted(graph.get(node, ())):
            if target not in index:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in on_stack:
                low[node] = min(low[node], index[target])
        if low[node] == index[node]:
            group = []
            while True:
                member = stack.pop()
                on_stack.discard(member)
                group.append(member)
                if member == node:
                    break
            if len(group) > 1 or node in graph.get(node, ()):
                groups.append(set(group))

    for node in sorted(graph):
        if node not in index:
            visit(node)
    cycles = []
    for group in groups:
        start = min(group)
        path, seen = [start], {start}
        while True:                       # walk inside the group until it closes
            nexts = sorted(t for t in graph.get(path[-1], ()) if t in group)
            if start in nexts and len(path) > 1 or nexts == [start]:
                break
            step = next((t for t in nexts if t not in seen), None)
            if step is None:
                break
            path.append(step)
            seen.add(step)
        cycles.append(path)
    return sorted(cycles)


def check_structure(project: Project, unit: Unit):
    agents = unit.path / "AGENTS.md"
    if not (unit.path / "README.md").is_file():
        project.add("E", "S3", unit.path, "unit has no README.md")
    if not agents.is_file():
        project.add("E", "S11", unit.path, "unit has no AGENTS.md")
    doc = unit.path / "doc"
    if doc.is_dir():
        for entry in sorted(doc.iterdir()):
            if entry.name not in DOC_ENTRIES and not entry.name.startswith("."):
                project.add("W", "S5", entry, "entry in doc/ is not defined by unifold "
                                              "and is not checked")
    if unit.is_root:
        for required in ("doc/skills/read-docs/SKILL.md", "doc/references/unifold/index.md"):
            if not (unit.path / required).is_file():
                project.add("E", "S6", unit.path / required, "the root unit must contain "
                                                             "this file")
    agent_links = set()
    if agents.is_file():
        for link in links_in(agents):
            if not SCHEME.match(link) and not link.startswith("#"):
                agent_links.add((agents.parent / unquote(re.split(r"[#?]", link)[0])).resolve())
    skills = doc / "skills"
    if skills.is_dir():
        for folder in sorted(p for p in skills.iterdir() if p.is_dir()):
            skill = folder / "SKILL.md"
            meta, error = front_matter(skill)
            if not skill.is_file():
                project.add("E", "S7", folder, "skill folder has no SKILL.md")
                continue
            if error or not isinstance(meta, dict):
                project.add("E", "S7", skill, error or "SKILL.md needs YAML front matter")
            else:
                if meta.get("name") != folder.name:
                    project.add("E", "S7", skill, f"skill name must equal the folder name "
                                                  f"'{folder.name}'")
                if not str(meta.get("description") or "").strip():
                    project.add("E", "S7", skill, "skill needs a 'description'")
            if agents.is_file() and skill.resolve() not in agent_links:
                project.add("E", "S8", agents, f"AGENTS.md does not link to skill "
                                               f"'{folder.name}'")
    numbers: dict[str, Path] = {}
    for info in decisions_of(unit):
        path = info["path"]
        if path.name[:4] in numbers and DECISION_FILE.match(path.name):
            project.add("E", "S9", path, f"decision number {path.name[:4]} is used twice "
                                         f"(also by {numbers[path.name[:4]].name})")
        numbers.setdefault(path.name[:4], path)
        if not DECISION_FILE.match(path.name):
            project.add("E", "S9", path, "decision file name must look like "
                                         "0001-short-title.md")
        if info["error"] or not info["has_meta"]:
            project.add("E", "S9", path, info["error"] or "decision needs YAML front "
                                                          "matter with status and date")
            continue
        if not info["status"].startswith(DECISION_STATUSES):
            project.add("E", "S9", path, f"decision status must start with one of "
                                         f"{list(DECISION_STATUSES)}")
        if not info["date"]:
            project.add("E", "S9", path, "decision needs a 'date'")
        if info["status"].startswith("accepted") and not info["makers"]:
            project.add("E", "S10", path, "an accepted decision names its "
                                          "'decision-makers'")


def check_links(project: Project, unit: Unit):
    files = managed_files(unit)
    context = (unit.path / "doc" / "context.md").resolve()
    graph: dict[Path, set[Path]] = {}
    for path in files:
        generated = is_generated(path)
        targets = graph.setdefault(path.resolve(), set())
        for link in links_in(path):
            if SCHEME.match(link) or link.startswith("#"):
                continue
            if link.startswith("/"):
                project.add("E", "L4", path, f"absolute link '{link}'; use a relative link")
                continue
            target = (path.parent / unquote(re.split(r"[#?]", link)[0])).resolve()
            if not target.exists():
                hint = "; run generate" if target.parent.name == "diagrams" \
                    or target.name == "index.md" and target.parent.name == "decisions" else ""
                project.add("E", "L1", path, f"link target does not exist: {link}{hint}")
                continue
            targets.add(target)
            if generated:
                continue
            kind, owner = project.owner_of(target)
            if kind is None:
                project.add("E", "L4", path, f"link leaves the project: {link}")
            elif kind == "foreign":
                if project.foreign[owner] is not unit or target != (owner / "README.md").resolve():
                    project.add("E", "L2", path, f"a nested project may only be linked "
                                                 f"through its README.md from its parent "
                                                 f"unit: {link}")
            elif owner is unit:
                continue
            elif owner.parent is unit:
                if target != (owner.path / "README.md").resolve():
                    project.add("E", "L2", path, f"link into child '{owner.name}' must "
                                                 f"target its README.md: {link}")
            elif owner.depth_below(unit) is not None:
                project.add("E", "L2", path, f"link skips a level into '{owner.name}'; "
                                             f"link to the direct child instead: {link}")
            elif unit.depth_below(owner) is not None:
                decisions = (owner.path / "doc" / "decisions").resolve()
                references = (owner.path / "doc" / "references").resolve()
                ok = target == (owner.path / "README.md").resolve() \
                    or decisions in target.parents or references in target.parents
                if path.resolve() != context:
                    project.add("E", "L3", path, f"upward link outside doc/context.md: {link}")
                elif not ok:
                    project.add("E", "L3", path, f"context.md may only cite an ancestor's "
                                                 f"README.md, decisions or references: {link}")
                elif decisions in target.parents and target.name != "index.md":
                    status = decision_info(target)["status"]
                    if status.startswith(NOT_IN_FORCE):
                        project.add("W", "L7", path, f"cites a decision that is {status}: "
                                                     f"{link}")
                    elif status.startswith("proposed") and unit.status == "active":
                        project.add("W", "L8", path, f"an active unit relies on a decision "
                                                     f"that is still proposed: {link}")
            else:
                project.add("E", "L4", path, f"sideways link into '{owner.name}'; a unit "
                                             f"must not know its siblings: {link}")
    # a skill that AGENTS.md does not link is reported once, by S8, not per file
    start = [p.resolve() for p in (unit.path / "README.md", unit.path / "AGENTS.md")] \
        + [s["path"].resolve() for s in skills_of(unit)]
    seen, queue = set(start), list(start)
    while queue:
        for target in graph.get(queue.pop(), ()):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    for path in files:
        if path.resolve() not in seen:
            hint = " (run generate: the decision index links it)" \
                if path.parent.name == "decisions" else ""
            project.add("E", "L5", path, "file is not reachable by links from README.md "
                                         f"or AGENTS.md{hint}")


def check_mentions(project: Project, unit: Unit):
    """L6: a sibling's or ancestor's unit name in code font outside doc/context.md."""
    if unit.is_root:
        return
    names = {s.name for s in unit.parent.children} | {a.name for a in unit.ancestors()}
    names -= {unit.name, project.root_unit.name} | {c.name for c in unit.children} \
        | set(unit.provides) | set(unit.needs)
    context = unit.path / "doc" / "context.md"
    for path in managed_files(unit):
        if path == context or is_generated(path):
            continue
        hits = {span for line in prose_lines(path) for span in CODE_SPAN.findall(line)
                if span in names}
        for name in sorted(hits):
            project.add("W", "L6", path, f"names the unit '{name}'; a unit does not know "
                                         "its siblings or ancestors outside doc/context.md")


def check_text(project: Project, unit: Unit):
    for path in managed_files(unit):
        lines = read_text(path).splitlines()
        if len(lines) > MAX_LINES:
            project.add("E", "T1", path, f"{len(lines)} lines; the limit is {MAX_LINES}")
        first = next((l for l in body_lines(path)
                      if l.strip() and not l.lstrip().startswith("<!--")), "")
        if not first.startswith("# "):
            project.add("W", "T2", path, "file should start with a '# ' title")
        if is_generated(path):
            continue
        long_lines = [i + 1 for i, l in enumerate(lines) if len(l) > MAX_LINE_LENGTH]
        if long_lines:
            project.add("W", "T3", path, f"line {long_lines[0]} has more than "
                                         f"{MAX_LINE_LENGTH} characters ({len(long_lines)} "
                                         "such line(s)); wrap or shorten")
    readme = unit.path / "README.md"
    if readme.is_file():
        section, title = "", None
        for line in body_lines(readme) if not is_generated(readme) else []:
            if line.startswith("# ") and title is None:
                title = line[2:].strip().strip("`")
            elif line.startswith("## "):
                section = line[3:].strip().lower()
            elif line.startswith("### ") and section in ("provides", "needs"):
                names = CODE_SPAN.findall(line)
                known = unit.provides if section == "provides" else unit.needs
                for name in names[:1]:
                    if name not in known:
                        project.add("W", "T5", readme, f"heading '{name}' under "
                                                       f"'## {section.title()}' is not in "
                                                       "the manifest")
        if not unit.is_root and title is not None and title != unit.name:
            project.add("W", "T6", readme, f"title '{title}' is not the unit name "
                                           f"'{unit.name}'")
    agents = unit.path / "AGENTS.md"
    if agents.is_file():
        inside, count = False, 0
        for line in read_text(agents).splitlines():
            if line.startswith("## "):
                inside = line.strip().lower() == "## why"
            elif inside and line.strip():
                count += 1
        if count > MAX_WHY_LINES:
            project.add("W", "T4", agents, f"'## Why' has {count} lines; move the long "
                                           "form to doc/architecture.md")


def check_context(project: Project, unit: Unit):
    """L9: every item of doc/context.md has a linked heading, Says and Here."""
    path = unit.path / "doc" / "context.md"
    if not path.is_file():
        return
    items, current = [], None
    for line in prose_lines(path):
        if line.startswith("### "):
            current = {"title": line[4:].strip(), "text": ""}
            items.append(current)
        elif line.startswith("#"):
            current = None
        elif current is not None:
            current["text"] += line + "\n"
    if not items:
        project.add("W", "L9", path, "no item found; each inherited item is a '### ' "
                                     "heading with a link, then 'Says:' and 'Here:'")
    for item in items:
        missing = [name for name, ok in (
            ("a link in the heading", bool(INLINE_LINK.search(item["title"]))),
            ("a paragraph that starts with 'Says'",
             re.search(r"^Says\b", item["text"], re.M) is not None),
            ("a paragraph that starts with 'Here'",
             re.search(r"^Here\b", item["text"], re.M) is not None)) if not ok]
        if missing:
            title = re.sub(r"\]\(.*", "", item["title"]).lstrip("[")[:50]
            project.add("W", "L9", path, f"item '{title}' lacks " + ", ".join(missing))


def check_generated(project: Project):
    expected = generate(project)
    for path, content in expected.items():
        if not path.is_file():
            project.add("W", "G1", path, "generated file is missing; run generate")
        elif read_text(path) != content:
            if not is_generated(path):
                project.add("E", "G2", path, "file in a generated location lacks the "
                                             "generated marker")
            else:
                project.add("W", "G1", path, "generated file is stale; run generate")
    for unit in project.units:
        folder = unit.path / "doc" / "diagrams"
        if folder.is_dir():
            for path in sorted(folder.glob("*.md")):
                if path not in expected:
                    rule = "G1" if is_generated(path) else "G2"
                    project.add("W" if rule == "G1" else "E", rule, path,
                                "file is not produced by the generator; remove it")


def run_checks(project: Project):
    if project.root_unit is None:
        return
    for unit in project.units:
        check_manifest(project, unit)
        check_wiring(project, unit)
        check_structure(project, unit)
        check_links(project, unit)
        check_mentions(project, unit)
        check_text(project, unit)
        check_context(project, unit)
    check_generated(project)
    if project.level == "core":
        project.findings = [f for f in project.findings
                            if f[1] in CORE_RULES or f[1][0] in "MWGD"]


def check_deps(project: Project, source: Path):
    """D1, D2: compare observed dependencies between files with the wiring.

    `source` is a JSON list of {"from": path, "to": path}, relative to the root.
    """
    try:
        edges = json.loads(read_text(source))
        assert isinstance(edges, list)
    except (OSError, ValueError, AssertionError) as exc:
        project.add("E", "D1", source, f"cannot read dependency edges: {exc}")
        return
    root = project.root_unit

    def chain(unit: Unit) -> list[Unit]:
        return [unit, *unit.ancestors()][::-1]          # root first

    seen: dict[tuple, tuple] = {}
    used: set[tuple] = set()
    for edge in edges:
        if not isinstance(edge, dict) or "from" not in edge or "to" not in edge:
            continue
        src, dst = (project.root / str(edge["from"])), (project.root / str(edge["to"]))
        kinds = project.owner_of(src)[0], project.owner_of(dst)[0]
        if "foreign" in kinds or None in kinds:
            continue
        a, b = project.unit_at(src), project.unit_at(dst)
        if a is b:
            continue
        ca, cb = chain(a), chain(b)
        depth = 0
        while depth < min(len(ca), len(cb)) and ca[depth] is cb[depth]:
            depth += 1
        common = ca[depth - 1]
        problem = None
        if b is common:                               # child uses code of an ancestor
            first = ca[depth]
            folders = [(common.path / e[2:]).resolve() for k, es in common.wiring.items()
                       if k.startswith(first.name + ".") for _, e in es if e.startswith("./")]
            if not any(f == dst.resolve() or f in dst.resolve().parents for f in folders):
                problem = f"'{project.rel(a.path)}' uses code of its ancestor " \
                          f"'{b.name}' that no wiring line provides"
        elif a is common:                             # own code uses a descendant
            if len(cb) - depth > 1:
                problem = f"code of '{a.name}' reaches into '{project.rel(b.path)}' " \
                          f"past its child '{cb[depth].name}'"
        else:
            first, second = ca[depth], cb[depth]
            wired = any(k.startswith(first.name + ".") and
                        any(e.startswith(second.name + ".") for _, e in es)
                        for k, es in common.wiring.items())
            if wired:
                used.add((common.path, first.name, second.name))
            else:
                problem = f"'{project.rel(a.path)}' depends on '{project.rel(b.path)}' " \
                          f"but no need of '{first.name}' is wired to '{second.name}'"
        if problem:
            key = (common.path, problem)
            count, example = seen.get(key, (0, f"{edge['from']} -> {edge['to']}"))
            seen[key] = (count + 1, example)
    for (where, problem), (count, example) in seen.items():
        unit = project.by_path[where]
        project.add("E", "D1", unit.manifest_path, f"{problem} ({count} edge(s), for "
                                                   f"example {example})")
    for unit in project.units:
        for key, entries in unit.wiring.items():
            if "." not in key:
                continue
            first, need = key.split(".", 1)
            child = unit.child(first)
            if child is None or child.needs.get(need, {}).get("kind") != "library":
                continue
            for _, endpoint in entries:
                if "." in endpoint and not endpoint.startswith("./") \
                        and (unit.path, first, endpoint.split(".", 1)[0]) not in used:
                    project.add("I", "D2", unit.manifest_path,
                                f"'{key}: {endpoint}' is wired but no dependency from "
                                f"'{first}' to '{endpoint.split('.', 1)[0]}' was observed")


# ------------------------------------------------------------- generation

def node_id(project: Project, unit: Unit) -> str:
    rel = project.rel(unit.path)
    return "u_root" if rel == "." else "u_" + safe_id(rel)


def safe_id(text: str) -> str:
    """Letters and digits stay; everything else is encoded so that ids stay unique."""
    return "".join(c if c.isascii() and c.isalnum() else
                   {"/": "__", "-": "_d", "_": "_u"}.get(c, f"_x{ord(c):x}") for c in text)


def port_id(project: Project, unit: Unit, side: str, port: str) -> str:
    return f"{side}_{node_id(project, unit)[2:]}___" + safe_id(port)


def link_to(source_dir: Path, target: Path) -> str:
    return Path(os.path.relpath(target, source_dir)).as_posix()


def best_diagram(unit: Unit) -> Path:
    name = "component.md" if unit.children else "context.md"
    return unit.path / "doc" / "diagrams" / name


def click_line(project: Project, node: str, target: Path, out_dir: Path) -> str | None:
    if project.links == "none":
        return None
    if project.links == "relative":
        return f'  click {node} href "{link_to(out_dir, target)}"'
    base = project.links.rstrip("/")
    return f'  click {node} href "{base}/{project.rel(target)}" _blank'


def mermaid(project: Project, frame: Unit, focus: Unit, depth: int, out_dir: Path):
    """Build one diagram. Returns (mermaid lines, units shown, {node id: unit})."""
    def expanded(unit: Unit) -> bool:
        level = unit.depth_below(focus)
        return bool(unit.children) and unit is not frame \
            and level is not None and level <= depth - 1

    def sources(unit: Unit, need: str) -> list[str]:
        if expanded(unit):
            found = []
            for key, entries in unit.wiring.items():
                if "." in key and any(endpoint == need for _, endpoint in entries):
                    child = unit.child(key.split(".", 1)[0])
                    if child:
                        found += sources(child, key.split(".", 1)[1])
            if found:
                return found
        return [node_id(project, unit)]

    def targets(unit: Unit, port: str) -> list[str]:
        if expanded(unit):
            found = []
            for _, endpoint in unit.wiring.get(port, []):
                if "." in endpoint and not endpoint.startswith("./"):
                    child = unit.child(endpoint.split(".", 1)[0])
                    if child:
                        found += targets(child, endpoint.split(".", 1)[1])
            if found:
                return found
        return [node_id(project, unit)]

    shown: list[Unit] = [frame]
    ids: dict[str, Unit] = {node_id(project, frame): frame}
    lines = ["flowchart LR"]
    planned, clicks, plain = [], [], {}
    if frame.status == "planned":
        planned.append(node_id(project, frame))

    def emit(unit: Unit, indent: str):
        shown.append(unit)
        ids[node_id(project, unit)] = unit
        if unit.status == "planned":
            planned.append(node_id(project, unit))
        if expanded(unit):
            lines.append(f'{indent}subgraph {node_id(project, unit)}["{unit.name}"]')
            for child in unit.children:
                emit(child, indent + "  ")
            lines.append(f"{indent}end")
        else:
            lines.append(f'{indent}{node_id(project, unit)}["{unit.name}"]')
            click = click_line(project, node_id(project, unit), best_diagram(unit), out_dir)
            if click:
                clicks.append(click)

    lines.append(f'  subgraph {node_id(project, frame)}["{frame.name}"]')
    for child in frame.children:
        emit(child, "    ")
    edges: dict[tuple[str, str, bool], list[str]] = {}
    frame_ports: dict[str, str] = {}
    whole_frame = frame is focus
    if whole_frame:
        for port in frame.provides:
            frame_ports[port_id(project, frame, "p", port)] = f'(["{port}"])'
        for need in frame.needs:
            frame_ports[port_id(project, frame, "n", need)] = f'{{{{"{need}"}}}}'

    def touches(key: str, value: str) -> bool:
        if whole_frame:
            return True
        return focus.name in (key.split(".", 1)[0] if "." in key else None,
                              value.split(".", 1)[0] if "." in value else None)

    def collect(unit: Unit):
        for key, entries in unit.wiring.items():
            for index, (config, value) in enumerate(entries):
                if unit is frame and not touches(key, value):
                    continue
                dashed = index > 0
                suffix = f" ({config})" if config else ""
                if "." in key:
                    child = unit.child(key.split(".", 1)[0])
                    need = key.split(".", 1)[1]
                    if child is None:
                        continue
                    froms = sources(child, need)
                    if value.startswith("./"):
                        pid = "x_" + safe_id(value[2:])
                        plain[pid] = value[2:]
                        tos, port = [pid], need
                    elif "." in value:
                        sibling = unit.child(value.split(".", 1)[0])
                        port = value.split(".", 1)[1]
                        if sibling is None:
                            continue
                        tos = targets(sibling, port)
                    elif unit is frame and value in unit.needs:
                        port = value
                        pid = port_id(project, frame, "n", value)
                        frame_ports[pid] = f'{{{{"{value}"}}}}'
                        tos = [pid]
                    else:
                        continue
                    label = (need if need == port else f"{need} → {port}") + suffix
                elif unit is frame and "." in value and key in unit.provides:
                    child = unit.child(value.split(".", 1)[0])
                    port = value.split(".", 1)[1]
                    if child is None:
                        continue
                    pid = port_id(project, frame, "p", key)
                    frame_ports[pid] = f'(["{key}"])'
                    froms, tos = [pid], targets(child, port)
                    label = ("" if key == port else port) + suffix
                else:
                    continue
                for source in froms:
                    for target in tos:
                        labels = edges.setdefault((source, target, dashed), [])
                        if label and label not in labels:
                            labels.append(label)
        for child in unit.children:
            if expanded(child):
                collect(child)

    collect(frame)
    for pid, label in plain.items():
        lines.append(f'    {pid}["{label}"]:::plain')
    lines.append("  end")
    for pid, shape in frame_ports.items():
        lines.append(f"  {pid}{shape}")
    for (source, target, dashed), labels in edges.items():
        arrow = "-.->" if dashed else "-->"
        label = ", ".join(labels)
        lines.append(f'  {source} {arrow}|"{label}"| {target}' if label
                     else f"  {source} {arrow} {target}")
    lines += clicks
    lines.append("  classDef focus stroke-width:4px")
    lines.append("  classDef planned stroke-dasharray:6 4")
    lines.append("  classDef plain stroke-dasharray:2 3")
    if planned:
        lines.append(f"  class {','.join(planned)} planned")
    if focus is not frame:
        lines.append(f"  class {node_id(project, focus)} focus")
    return lines, shown, ids


def unit_table(units: list[Unit], out_dir: Path, full: bool) -> list[str]:
    if full:
        rows = ["| Unit | Kind | Summary | Status | Diagram |", "|---|---|---|---|---|"]
    else:
        rows = ["| Unit | Kind | Diagram |", "|---|---|---|"]
    for unit in units:
        readme = link_to(out_dir, unit.path / "README.md")
        diagram = best_diagram(unit)
        link = f"[{diagram.stem}]({link_to(out_dir, diagram)})"
        if full:
            rows.append(f"| [{unit.name}]({readme}) | {unit.kind} | {cell(unit.summary)} | "
                        f"{unit.status} | {link} |")
        else:
            rows.append(f"| [{unit.name}]({readme}) | {unit.kind} | {link} |")
    return rows


def unit_link(project: Project, unit: Unit, out_dir: Path) -> str:
    return f"[{project.rel(unit.path)}]({link_to(out_dir, unit.path / 'README.md')})" \
        if not unit.is_root else f"[{unit.name}]({link_to(out_dir, unit.path / 'README.md')})"


def contract_link(unit: Unit, spec: dict, out_dir: Path) -> str:
    contract = spec.get("contract")
    if not isinstance(contract, str):
        return ""
    if SCHEME.match(contract):
        return f"[contract]({contract})"
    return f"[contract]({link_to(out_dir, unit.path / contract)})"


def connection_tables(project: Project, unit: Unit, out_dir: Path) -> list[str]:
    """Resolved neighbours of a unit, as text for readers who do not look at pictures."""
    rows = []
    if unit.needs:
        rows += ["", "### Who provides what this unit needs", "",
                 "| Need | Kind | Own contract | Provided by | Port | Their contract |",
                 "|---|---|---|---|---|---|"]
        for need, spec in unit.needs.items():
            found = providers_of(unit, need)
            own = contract_link(unit, spec, out_dir)
            if not found:
                note = "nobody (optional)" if spec.get("optional") else "**not wired**"
                rows.append(f"| {need} | {spec.get('kind', '')} | {own} | {note} | | |")
            for item in found:
                config = f" ({item['config']})" if item.get("config") else ""
                if item["where"] == "outside":
                    rows.append(f"| {need} | {spec.get('kind', '')} | {own} | outside the "
                                f"project, as need `{item['port']}` of the root{config} | | |")
                elif item["where"] == "plain":
                    rows.append(f"| {need} | {spec.get('kind', '')} | {own} | folder "
                                f"`{project.rel(item['path'])}`, not a unit yet{config} | | |")
                else:
                    target = item["unit"]
                    rows.append(f"| {need} | {spec.get('kind', '')} | {own} | "
                                f"{unit_link(project, target, out_dir)}{config} | "
                                f"{item['port']} | "
                                f"{contract_link(target, target.provides.get(item['port'], {}), out_dir)} |")
    if unit.provides:
        rows += ["", "### Who uses what this unit provides", "",
                 "| Port | Kind | Used by | As need | Their contract |",
                 "|---|---|---|---|---|"]
        for port, spec in unit.provides.items():
            found = users_of(unit, port)
            if not found:
                rows.append(f"| {port} | {spec.get('kind', '')} | nobody | | |")
            for item in found:
                if item["where"] == "outside":
                    rows.append(f"| {port} | {spec.get('kind', '')} | outside the project, "
                                f"as port `{item['need']}` of the root | | |")
                else:
                    user = item["unit"]
                    theirs = contract_link(user, user.needs.get(item["need"], {}), out_dir)
                    rows.append(f"| {port} | {spec.get('kind', '')} | "
                                f"{unit_link(project, user, out_dir)} | {item['need']} | "
                                f"{theirs} |")
    return rows


def breadcrumb(unit: Unit, out_dir: Path) -> str:
    parts = [f"[{a.name}]({link_to(out_dir, best_diagram(a))})"
             for a in reversed(unit.ancestors())]
    return " / ".join(parts + [f"**{unit.name}**"])


def page(unit: Unit, title: str, intro: str, diagram: list[str], tables: list[str],
         kinds: list[str], current: str, out_dir: Path) -> str:
    nav = [f"[README]({link_to(out_dir, unit.path / 'README.md')})"]
    nav += [f"[{k}]({k}.md)" for k in kinds if k != current]
    return "\n".join([MARK, f"# {title}", "", breadcrumb(unit, out_dir) + " · "
                      + " · ".join(nav), "", intro, "", "```mermaid", *diagram, "```",
                      "", *tables, ""])


LEGEND = ("Arrows point from the side that needs something to the side that provides "
          "it. Rounded nodes are ports the framing unit provides, hexagons are its "
          "needs. A dashed arrow is an alternative provider; a dashed border marks a "
          "planned unit.")


def root_context(project: Project, unit: Unit, out_dir: Path):
    uid = node_id(project, unit)
    lines = ["flowchart LR", f'  {uid}["{unit.name}"]']
    rows = ["| Port | Direction | Kind | Summary |", "|---|---|---|---|"]
    for port, spec in unit.provides.items():
        pid = port_id(project, unit, "p", port)
        lines += [f'  {pid}(["{port}"])', f"  {pid} --> {uid}"]
        rows.append(f"| {port} | provided | {spec.get('kind', '')} | "
                    f"{cell(spec.get('summary'))} |")
    for need, spec in unit.needs.items():
        pid = port_id(project, unit, "n", need)
        lines += [f'  {pid}{{{{"{need}"}}}}', f"  {uid} --> {pid}"]
        rows.append(f"| {need} | needed | {spec.get('kind', '')} | "
                    f"{cell(spec.get('summary'))} |")
    click = click_line(project, uid, best_diagram(unit), out_dir)
    lines += ([click] if click else []) + ["  classDef focus stroke-width:4px",
                                           f"  class {uid} focus"]
    return lines, rows


def diagrams_for(project: Project, unit: Unit) -> dict[str, tuple]:
    """Mermaid lines and shown units per diagram kind, for one unit."""
    folder = unit.path / "doc" / "diagrams"
    out = {}
    if unit.is_root:
        lines, rows = root_context(project, unit, folder)
        out["context"] = (lines, rows, {node_id(project, unit): unit}, MAX_DEPTH)
    else:
        lines, shown, ids = mermaid(project, unit.parent, unit, 0, folder)
        out["context"] = (lines, shown, ids, MAX_DEPTH)
    if unit.children:
        lines, shown, ids = mermaid(project, unit, unit, 1, folder)
        out["component"] = (lines, shown, ids, MAX_DEPTH)
        frame = unit if unit.is_root else unit.parent
        out["architecture"] = [(mermaid(project, frame, unit, depth, folder), depth)
                               for depth in range(MAX_DEPTH, 0, -1)]
    return out


def generate(project: Project) -> dict[Path, str]:
    """Return {path: content} for every generated file of the project."""
    out: dict[Path, str] = {}
    if project.root_unit is None:
        return out
    for unit in project.units:
        folder = unit.path / "doc" / "diagrams"
        kinds = ["context"] + (["component", "architecture"] if unit.children else [])
        data = diagrams_for(project, unit)
        lines, shown = data["context"][0], data["context"][1]
        if unit.is_root:
            tables = shown
            intro = (f"`{unit.name}` and the outside world: the ports it provides "
                     "(rounded) and the things it needs from outside (hexagons).")
        else:
            tables = unit_table(shown, folder, False) \
                + connection_tables(project, unit, folder)
            intro = (f"`{unit.name}` among its siblings inside `{unit.parent.name}`. "
                     f"Only connections that touch `{unit.name}` are drawn. " + LEGEND)
        out[folder / "context.md"] = page(unit, f"Context diagram: {unit.name}", intro,
                                          lines, tables, kinds, "context", folder)
        if not unit.children:
            continue
        lines, shown = data["component"][0], data["component"][1]
        intro = f"The units directly inside `{unit.name}` and how they are wired. " + LEGEND
        out[folder / "component.md"] = page(unit, f"Component diagram: {unit.name}", intro,
                                            lines, unit_table(shown, folder, True), kinds,
                                            "component", folder)
        for (lines, shown, _), depth in data["architecture"]:
            note = "" if depth == MAX_DEPTH else \
                f" Depth reduced to {depth} to stay within {MAX_LINES} lines."
            where = "" if unit.is_root else f" next to its siblings in `{unit.parent.name}`"
            intro = (f"`{unit.name}`{where}, opened up {depth} level(s) down."
                     f"{note} " + LEGEND)
            content = page(unit, f"Architecture diagram: {unit.name}", intro, lines,
                           unit_table(shown, folder, False), kinds, "architecture", folder)
            if len(content.splitlines()) <= MAX_LINES:
                break
        out[folder / "architecture.md"] = content
    for unit in project.units:
        infos = decisions_of(unit)
        if not infos:
            continue
        folder = unit.path / "doc" / "decisions"
        rows = ["| No. | Decision | Status | Date |", "|---|---|---|---|"]
        for info in infos:
            name = info["path"].name
            rows.append(f"| {name[:4]} | [{cell(info['title'])}]({name}) | {info['status']} | "
                        f"{info['date']} |")
        out[folder / "index.md"] = "\n".join(
            [MARK, f"# Decisions of {unit.name}", "",
             "[README](../../README.md) · [AGENTS.md](../../AGENTS.md)", "", *rows, ""])
    return out


def write_generated(project: Project) -> int:
    expected, changed = generate(project), 0
    for path, content in expected.items():
        if path.is_file() and not is_generated(path):
            print(f"not overwritten: {project.rel(path)} has no generated marker; move "
                  "or delete it", file=sys.stderr)
            continue
        if not path.is_file() or read_text(path) != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            changed += 1
    for unit in project.units:
        folder = unit.path / "doc" / "diagrams"
        if folder.is_dir():
            for path in folder.glob("*.md"):
                if path not in expected and is_generated(path):
                    path.unlink()
                    changed += 1
    return changed


# ------------------------------------------------------------ description

def describe(project: Project, unit: Unit) -> dict:
    """Everything an agent needs to start work in a unit, as plain data."""
    rel = project.rel

    def provider(item):
        if item["where"] == "outside":
            return {"outside": True, "root-need": item["port"], "config": item["config"]}
        if item["where"] == "plain":
            return {"plain-folder": rel(item["path"]), "config": item["config"]}
        spec = item["unit"].provides.get(item["port"], {})
        contract = spec.get("contract")
        if isinstance(contract, str) and not SCHEME.match(contract):
            contract = rel(item["unit"].path / contract)
        return {"unit": rel(item["unit"].path), "port": item["port"],
                "contract": contract, "config": item["config"]}

    def user(item):
        if item["where"] == "outside":
            return {"outside": True, "root-port": item["need"]}
        contract = item["unit"].needs.get(item["need"], {}).get("contract")
        if isinstance(contract, str) and not SCHEME.match(contract):
            contract = rel(item["unit"].path / contract)
        return {"unit": rel(item["unit"].path), "need": item["need"], "contract": contract}

    files = [rel(p) for p in managed_files(unit) if "diagrams" not in p.parts
             and p.name != "index.md" and not rel(p).startswith(STANDARD_PATHS)]
    return {
        "unit": unit.name, "path": rel(unit.path), "summary": unit.summary,
        "kind": unit.kind, "status": unit.status, "owner": unit.owner,
        "manifest": rel(unit.manifest_path),
        "parent": rel(unit.parent.path) if unit.parent else None,
        "children": [rel(c.path) for c in unit.children],
        "provides": {port: {"kind": spec.get("kind"), "summary": spec.get("summary"),
                            "contract": spec.get("contract"),
                            "verified-by": spec.get("verified-by"),
                            "conforms-to": spec.get("conforms-to"),
                            "used-by": [user(i) for i in users_of(unit, port)]}
                     for port, spec in unit.provides.items()},
        "needs": {need: {"kind": spec.get("kind"), "summary": spec.get("summary"),
                         "optional": bool(spec.get("optional")),
                         "contract": spec.get("contract"),
                         "provided-by": [provider(i) for i in providers_of(unit, need)]}
                  for need, spec in unit.needs.items()},
        "skills": [{"name": s["name"], "path": rel(s["path"]),
                    "description": s["description"]} for s in skills_of(unit)],
        "decisions": [{"path": rel(d["path"]), "title": d["title"], "status": d["status"]}
                      for d in decisions_of(unit)],
        "files": files,
    }


def print_show(info: dict):
    def line(label, value):
        if value:
            print(f"{label:<10}{value}")
    line("unit", f"{info['unit']}  ({info['path']})")
    line("summary", info["summary"])
    line("status", " · ".join(x for x in (info["status"], info["kind"],
                                          info["owner"] and "owner " + info["owner"]) if x))
    line("manifest", info["manifest"])
    line("parent", info["parent"] or "none (root unit)")
    line("children", ", ".join(info["children"]) or "none")
    if info["provides"]:
        print("provides")
    for port, spec in info["provides"].items():
        extra = "".join(f"  {k} {spec[k]}" for k in ("contract", "verified-by",
                                                       "conforms-to") if spec[k])
        print(f"  {port} ({spec['kind'] or '-'}){extra}")
        for item in spec["used-by"] or [None]:
            if item is None:
                print("      used by nobody")
            elif item.get("outside"):
                print(f"      used from outside the project (root port '{item['root-port']}')")
            else:
                contract = f"  contract {item['contract']}" if item.get("contract") else ""
                print(f"      used by {item['unit']} as need '{item['need']}'{contract}")
    if info["needs"]:
        print("needs")
    for need, spec in info["needs"].items():
        extra = (" optional" if spec["optional"] else "") \
            + (f"  contract {spec['contract']}" if spec["contract"] else "")
        print(f"  {need} ({spec['kind'] or '-'}){extra}")
        for item in spec["provided-by"] or [None]:
            config = f" [{item['config']}]" if item and item.get("config") else ""
            if item is None:
                print("      not wired")
            elif item.get("outside"):
                print(f"      provided from outside the project (root need "
                      f"'{item['root-need']}'){config}")
            elif "plain-folder" in item:
                print(f"      provided by folder {item['plain-folder']} (not a unit){config}")
            else:
                contract = f"  contract {item['contract']}" if item["contract"] else ""
                print(f"      provided by {item['unit']} port '{item['port']}'{config}{contract}")
    for skill in info["skills"]:
        print(f"skill     {skill['name']}: {skill['path']}")
    for decision in info["decisions"]:
        print(f"decision  [{decision['status']}] {decision['path']}")
    line("files", ", ".join(info["files"]))


def print_tree(project: Project):
    def show(unit: Unit, indent: str):
        ports = []
        if unit.provides:
            ports.append("provides " + ", ".join(unit.provides))
        if unit.needs:
            ports.append("needs " + ", ".join(unit.needs))
        suffix = f"  ({'; '.join(ports)})" if ports else ""
        between = unit.parent is not None and unit.path.parent != unit.parent.path
        path = f"  <{project.rel(unit.path)}>" if between else ""
        print(f"{indent}{unit.name} [{unit.status}]{path}{suffix}")
        for child in unit.children:
            show(child, indent + "  ")
        for folder in unit.foreign:
            print(f"{indent}  {folder.name} [nested project, not checked]")
    show(project.root_unit, "")


# ------------------------------------------------------------------- site

SITE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ · unifold</title>
<style>
:root{--bg:#fff;--fg:#1c1e21;--mute:#667;--line:#d6d9de;--hi:#0b62d6;--panel:#f6f7f9}
@media(prefers-color-scheme:dark){:root{--bg:#16181c;--fg:#e6e8eb;--mute:#9aa3ad;--line:#333a44;--hi:#6cb0ff;--panel:#1e2228}}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg);display:flex;min-height:100vh}
nav{width:250px;flex:none;border-right:1px solid var(--line);background:var(--panel);padding:12px;overflow:auto;max-height:100vh;position:sticky;top:0}
nav ul{list-style:none;margin:0;padding-left:14px}nav>ul{padding-left:0}
nav a{display:block;padding:2px 6px;border-radius:4px;color:var(--fg);text-decoration:none;cursor:pointer}
nav a.on{background:var(--hi);color:#fff}nav a:hover{outline:1px solid var(--line)}
main{flex:1;min-width:0;padding:16px 24px}a{color:var(--hi)}
h1{font-size:22px;margin:.2em 0}.mute{color:var(--mute)}.crumbs a{cursor:pointer}
.tabs button{font:inherit;padding:4px 12px;margin-right:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:6px;cursor:pointer}
.tabs button.on{background:var(--hi);color:#fff;border-color:var(--hi)}
#diagram{border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0;overflow:auto;background:var(--bg)}
#diagram svg{max-width:none;height:auto}#diagram .pick{cursor:pointer}
table{border-collapse:collapse;margin:8px 0;width:100%}th,td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}
th{background:var(--panel)}code{background:var(--panel);padding:0 4px;border-radius:3px}
@media(max-width:800px){body{display:block}nav{width:auto;max-height:none;position:static}}
</style></head><body>
<nav id="tree"></nav>
<main>
<div class="crumbs mute" id="crumbs"></div>
<h1 id="title"></h1><p id="summary"></p><p class="mute" id="meta"></p>
<div class="tabs" id="tabs"></div>
<div id="diagram">Loading the diagram renderer…</div>
<p class="mute">Click a box to open that unit. Arrows point from a need to its provider.</p>
<div id="info"></div>
</main>
<script type="module">
const model = __MODEL__;
const units = model.units, byPath = Object.fromEntries(units.map(u => [u.path, u]));
const el = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const file = p => model.base ? model.base + "/" + p : model.up + p;
const pick = (p, t) => `<a class="go" data-path="${esc(p)}">${esc(t ?? (p === "." ? model.name : p))}</a>`;
let mermaid = null, state = {path: ".", kind: null};
function fromHash(){const h = decodeURIComponent(location.hash.slice(1)); const [p, k] = h.split("@");
  state = {path: byPath[p] ? p : ".", kind: k || null};}
function go(path, kind){location.hash = encodeURIComponent(path + (kind ? "@" + kind : ""));}
function tree(path){const u = byPath[path]; const kids = u.children.map(tree).join("");
  return `<li><a data-path="${esc(path)}" class="go${path === state.path ? " on" : ""}">${esc(u.unit)}</a>${kids ? "<ul>" + kids + "</ul>" : ""}</li>`;}
function who(list, key){return list.map(i => i.outside ? "outside the project"
  : i["plain-folder"] ? "folder <code>" + esc(i["plain-folder"]) + "</code>"
  : pick(i.unit) + " · <code>" + esc(i[key]) + "</code>" + (i.config ? " (" + esc(i.config) + ")" : "")).join("<br>") || "–";}
async function render(){
  const u = byPath[state.path]; const kinds = Object.keys(u.diagrams);
  const kind = kinds.includes(state.kind) ? state.kind : (kinds.includes("component") ? "component" : "context");
  document.title = u.unit + " · " + model.name;
  el("tree").innerHTML = "<ul>" + tree(".") + "</ul>";
  const chain = []; for (let p = u.parent; p !== null; p = byPath[p].parent) chain.unshift(p);
  el("crumbs").innerHTML = chain.map(p => pick(p, byPath[p].unit)).concat(esc(u.unit)).join(" / ");
  el("title").textContent = u.unit; el("summary").textContent = u.summary;
  el("meta").innerHTML = [u.status, u.kind, u.owner && "owner " + u.owner].filter(Boolean).map(esc).join(" · ")
    + ` · <a href="${esc(file(u.readme))}">README</a> · <a href="${esc(file(u.agents))}">AGENTS.md</a>`;
  el("tabs").innerHTML = kinds.map(k => `<button data-kind="${k}" class="${k === kind ? "on" : ""}">${k}</button>`).join("");
  let html = "";
  const p = Object.entries(u.provides), n = Object.entries(u.needs);
  if (p.length) html += "<h2>Provides</h2><table><tr><th>Port</th><th>Kind</th><th>Summary</th><th>Used by</th></tr>"
    + p.map(([k, v]) => `<tr><td><code>${esc(k)}</code></td><td>${esc(v.kind)}</td><td>${esc(v.summary)}</td><td>${who(v["used-by"], "need")}</td></tr>`).join("") + "</table>";
  if (n.length) html += "<h2>Needs</h2><table><tr><th>Need</th><th>Kind</th><th>Summary</th><th>Provided by</th></tr>"
    + n.map(([k, v]) => `<tr><td><code>${esc(k)}</code></td><td>${esc(v.kind)}</td><td>${esc(v.summary)}</td><td>${who(v["provided-by"], "port")}</td></tr>`).join("") + "</table>";
  if (u.skills.length) html += "<h2>Skills</h2><ul>" + u.skills.map(s => `<li><a href="${esc(file(s.path))}">${esc(s.name)}</a>: ${esc(s.description)}</li>`).join("") + "</ul>";
  if (u.decisions.length) html += "<h2>Decisions</h2><ul>" + u.decisions.map(d => `<li><a href="${esc(file(d.path))}">${esc(d.title)}</a> <span class="mute">${esc(d.status)}</span></li>`).join("") + "</ul>";
  el("info").innerHTML = html;
  if (!mermaid) return;
  const d = u.diagrams[kind];
  try {
    const {svg} = await mermaid.render("g" + Date.now(), d.source);
    el("diagram").innerHTML = svg;
    for (const node of el("diagram").querySelectorAll("[id]")) {
      const hit = Object.keys(d.nodes).find(id => node.id === id || new RegExp("(^|-)" + id + "(-\\d+)?$").test(node.id));
      if (hit && (node.classList.contains("node") || node.classList.contains("cluster"))) {
        node.classList.add("pick"); node.addEventListener("click", ev => {ev.stopPropagation(); go(d.nodes[hit]);});
      }
    }
  } catch (err) { el("diagram").textContent = "The diagram could not be drawn: " + err; }
}
document.addEventListener("click", ev => {
  const a = ev.target.closest(".go"); if (a) { go(a.dataset.path); return; }
  const b = ev.target.closest("button[data-kind]"); if (b) go(state.path, b.dataset.kind);
});
addEventListener("hashchange", () => { fromHash(); render(); });
fromHash(); render();
try {
  mermaid = (await import("__MERMAID__")).default;
  mermaid.initialize({startOnLoad: false, securityLevel: "loose",
    theme: matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "default"});
  render();
} catch (err) { el("diagram").textContent = "The diagram renderer could not be loaded (" + err + "). The tables below still work."; }
</script></body></html>
"""


def build_site(project: Project, out: Path, mermaid_url: str) -> None:
    saved, project.links = project.links, "none"
    units = []
    for unit in project.units:
        info = describe(project, unit)
        info["readme"] = project.rel(unit.path / "README.md")
        info["agents"] = project.rel(unit.path / "AGENTS.md")
        info["diagrams"] = {}
        data = diagrams_for(project, unit)
        for kind, value in data.items():
            lines, _, ids = value[0][0] if kind == "architecture" else value[:3]
            info["diagrams"][kind] = {"source": "\n".join(lines),
                                      "nodes": {i: project.rel(u.path) for i, u in ids.items()}}
        units.append(info)
    project.links = saved
    base = saved.rstrip("/") if saved not in ("none", "relative") else ""
    up = link_to(out.parent.resolve(), project.root)
    model = {"name": project.root_unit.name, "units": units, "base": base,
             "up": "" if up == "." else up + "/"}
    html = SITE.replace("__TITLE__", project.root_unit.name) \
        .replace("__MODEL__", json.dumps(model).replace("</", "<\\/")) \
        .replace("__MERMAID__", mermaid_url)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


# --------------------------------------------------------------- commands

ROOT_README = """# {name}

<What this project is and what it is for.>

This repository is documented with [unifold]({url}): some folders are units
with a declared interface. The interface of the project is in
[unit.yaml](unit.yaml).
"""

ROOT_AGENTS = """# AGENTS.md: {name}

This folder is a [unifold]({url}) unit and the root of the project. Use the
[read-docs](doc/skills/read-docs/SKILL.md) skill before anything else.

## Why

<Why the project is cut the way it is, and what makes it change.>

## Read next

1. [README.md](README.md): what the project provides and needs
2. [doc/diagrams/context.md](doc/diagrams/context.md): the project and the outside world

## Skills

| Skill | Use it when |
|---|---|
| [read-docs](doc/skills/read-docs/SKILL.md) | You enter this repository or a folder you do not know |
| [write-docs](doc/skills/write-docs/SKILL.md) | You create or change units, decisions, references or skills |
| [check-docs](doc/skills/check-docs/SKILL.md) | You have changed documents, or review a change |

## Commands

```sh
python3 doc/skills/check-docs/scripts/unifold.py show PATH   # a unit and its neighbours
python3 doc/skills/check-docs/scripts/unifold.py generate    # diagrams and indexes
python3 doc/skills/check-docs/scripts/unifold.py check       # the tool rules
```
"""

SPEC_URL = "https://unifold.md"


def init(target: Path, level: str) -> int:
    """Copy the standard into TARGET and, in a new project, write a clean start."""
    source = Path(__file__).resolve().parents[4]
    items = ["doc/references/unifold", "doc/skills/read-docs",
             "doc/skills/write-docs", "doc/skills/check-docs"]
    if level == "full":
        for item in items:
            if not (source / item).exists():
                print(f"error: {source / item} not found; run init from a full copy of "
                      "the standard", file=sys.stderr)
                return 2
        if target.resolve() == source:
            print("error: TARGET is the project this tool belongs to; init copies the "
                  "standard from here into another project. To update this project, "
                  "run init from a newer copy of the standard.", file=sys.stderr)
            return 2
    fresh = not is_root(target)
    target.mkdir(parents=True, exist_ok=True)
    if level == "full":
        for item in items:
            if (target / item).exists():
                shutil.rmtree(target / item)
            shutil.copytree(source / item, target / item,
                            ignore=shutil.ignore_patterns("__pycache__"))
            print(f"copied {item}")
    if not fresh:
        print("The copy of the standard was replaced. Run generate and check."
              if level == "full" else "This folder is a project already; nothing to do.")
        return 0
    name = re.sub(r"[^A-Za-z0-9_-]", "-", target.resolve().name).strip("-") or "project"
    written = []
    manifest, where, _ = load_manifest(target)
    if manifest is None:
        text = (f"unit: {name}\nunifold: \"{TOOL_VERSION}\"\n"
                + ("level: core\n" if level == "core" else "")
                + "summary: <what the project is, in one line>\nstatus: active\n")
        (target / "unit.yaml").write_text(text, encoding="utf-8", newline="\n")
        written.append("unit.yaml")
    else:
        print(f"error: {where} is a manifest without the key 'unifold'; add "
              f"'unifold: \"{TOOL_VERSION}\"' to make this folder a project root",
              file=sys.stderr)
        return 2
    if not (target / "README.md").exists():
        (target / "README.md").write_text(ROOT_README.format(name=name, url=SPEC_URL),
                                          encoding="utf-8", newline="\n")
        written.append("README.md")
    if level == "full" and not (target / "AGENTS.md").exists():
        (target / "AGENTS.md").write_text(ROOT_AGENTS.format(name=name, url=SPEC_URL),
                                          encoding="utf-8", newline="\n")
        written.append("AGENTS.md")
    project = Project(target.resolve())
    write_generated(project)
    print("written: " + ", ".join(written) + "; diagrams generated")
    agents = target / "AGENTS.md"
    if level == "full" and "AGENTS.md" not in written \
            and "doc/skills/read-docs/SKILL.md" not in read_text(agents):
        block = ROOT_AGENTS.format(name=name, url=SPEC_URL)
        block = block[block.index("## Read next"):block.index("## Commands")]
        agents.write_text(read_text(agents).rstrip("\n") + "\n\n" + block.rstrip("\n") + "\n",
                          encoding="utf-8", newline="\n")
        print("AGENTS.md existed: appended the sections 'Read next' and 'Skills'.")
    print("Next: fill in the summary in unit.yaml, then make the first folders units "
          "(a unit.yaml and a README.md each) and wire them in the root manifest.")
    return 0


def readme_section(unit: Unit, name: str) -> str:
    """The text below the `###` heading that names a port, in the unit's README.md."""
    readme = unit.path / "README.md"
    if not readme.is_file():
        return ""
    out, inside = [], False
    for line in body_lines(readme):
        if line.startswith("#"):
            if inside:
                break
            inside = line.startswith("### ") and name in CODE_SPAN.findall(line)
        elif inside:
            out.append(line)
    return "\n".join(out).strip()


def print_port(project: Project, unit: Unit, name: str) -> int:
    """Both ends of every connection of one port, for comparing them (rule C13)."""
    rel = project.rel

    def side(owner: Unit, port: str, kind: str):
        spec = (owner.provides if kind == "provides" else owner.needs).get(port, {})
        contract = spec.get("contract")
        print(f"--- {rel(owner.path)} {kind} '{port}' ({spec.get('kind') or '-'}): "
              f"{spec.get('summary', '')}")
        if contract:
            print(f"    contract: {contract if SCHEME.match(str(contract)) else rel(owner.path / contract)}")
        if spec.get("conforms-to"):
            print(f"    conforms-to: {spec['conforms-to']}")
        text = readme_section(owner, port)
        print(text if text else "    (no section for this port in README.md)")
        print()

    if name in unit.provides:
        side(unit, name, "provides")
        for item in users_of(unit, name):
            if item["where"] == "unit":
                side(item["unit"], item["need"], "needs")
            else:
                print(f"--- used from outside the project (root port '{item['need']}')\n")
    elif name in unit.needs:
        side(unit, name, "needs")
        for item in providers_of(unit, name):
            if item["where"] == "unit":
                side(item["unit"], item["port"], "provides")
            elif item["where"] == "outside":
                print(f"--- provided from outside the project (root need '{item['port']}')")
                print(readme_section(project.root_unit, item["port"]) + "\n")
            else:
                print(f"--- provided by folder {rel(item['path'])} (not a unit)\n")
    else:
        print(f"error: unit '{unit.name}' has no port or need '{name}'", file=sys.stderr)
        return 2
    return 0


def stats(project: Project) -> dict:
    """How much has been written, per unit and in total."""
    rows = []
    for unit in project.units:
        files = [p for p in managed_files(unit) if not is_generated(p)
                 and not project.rel(p).startswith(STANDARD_PATHS)]
        context = unit.path / "doc" / "context.md"
        items = sum(1 for l in prose_lines(context) if l.startswith("### ")) \
            if context.is_file() else 0
        rows.append({"unit": project.rel(unit.path), "files": len(files),
                     "words": sum(len(read_text(p).split()) for p in files),
                     "context-items": items})
    lines = [(k, e) for u in project.units for k, es in u.wiring.items() for _, e in es]
    decisions = [d["status"].split()[0] for u in project.units for d in decisions_of(u)]
    ports = [s for u in project.units for s in u.provides.values()]
    return {"units": rows,
            "total": {"units": len(rows), "files": sum(r["files"] for r in rows),
                      "words": sum(r["words"] for r in rows),
                      "context-items": sum(r["context-items"] for r in rows),
                      "wiring-lines": len(lines),
                      "wiring-pass-up": sum(1 for k, e in lines if "." in k and "." not in e
                                            and not e.startswith("./")),
                      "wiring-delegation": sum(1 for k, e in lines if "." not in k),
                      "ports": len(ports),
                      "ports-with-contract": sum(1 for s in ports if s.get("contract")),
                      "ports-verified": sum(1 for s in ports if s.get("verified-by")),
                      "units-by-status": {s: sum(1 for u in project.units if u.status == s)
                                          for s in sorted(STATUSES)},
                      "decisions-by-status": {s: decisions.count(s)
                                              for s in sorted(set(decisions))}}}


COMMANDS = {
    "check": "check the project against the tool rules; changes nothing",
    "generate": "write diagrams and decision indexes from the manifests",
    "show": "describe the unit that contains PATH, with its resolved neighbours",
    "port": "print both ends of every connection of one port or need",
    "tree": "print the unit tree with status and ports",
    "stats": "count files, words, context items and wiring lines",
    "skills": "list every skill of the project",
    "decisions": "list every decision of the project",
    "site": "write the interactive HTML explorer",
    "cited-by": "list the managed files that link to FILE",
    "init": "start a project in TARGET, or replace its copy of the standard",
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="unifold", description=__doc__.split("\n")[0])
    parser.add_argument("--version", action="version", version=TOOL_VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "generate", "show", "port", "tree", "stats", "skills",
                 "decisions", "site"):
        cmd = sub.add_parser(name, help=COMMANDS[name], description=COMMANDS[name])
        cmd.add_argument("path", nargs="?", default=".",
                         help="a folder inside the project (default: the current folder)")
        if name == "port":
            cmd.add_argument("name", help="name of a provided port or a need of the unit")
        if name in ("check", "show", "tree", "stats", "skills", "decisions"):
            cmd.add_argument("--json", action="store_true", help="print JSON")
        if name == "check":
            cmd.add_argument("--strict", action="store_true",
                             help="exit with 1 on warnings too")
            cmd.add_argument("--quiet", action="store_true", help="hide info findings")
            cmd.add_argument("--deps", metavar="FILE",
                             help="JSON list of observed dependencies between files, "
                                  "to compare with the wiring (rules D1, D2)")
        if name == "decisions":
            cmd.add_argument("--status", help="only decisions whose status starts with this")
        if name == "site":
            cmd.add_argument("-o", "--output", help="file to write (default: "
                                                    "unifold.html in the project root)")
            cmd.add_argument("--mermaid", default=MERMAID_URL,
                             help="URL of the Mermaid ES module to load")
    cmd = sub.add_parser("cited-by", help=COMMANDS["cited-by"], description=COMMANDS["cited-by"])
    cmd.add_argument("file")
    cmd = sub.add_parser("init", help=COMMANDS["init"], description=COMMANDS["init"])
    cmd.add_argument("target")
    cmd.add_argument("--level", choices=sorted(LEVELS), default="full",
                     help="core: manifests, wiring and diagrams only, no copy of the "
                          "standard; full (default): the whole standard")
    args = parser.parse_args(argv)
    if args.command == "init":
        return init(Path(args.target), args.level)
    given = Path(args.file if args.command == "cited-by" else args.path)
    if not given.exists():
        print(f"error: {given} does not exist", file=sys.stderr)
        return 2
    root = find_root(given if given.is_dir() else given.parent)
    if root is None:
        print("error: no unifold project found (no manifest with 'unifold' here or "
              "above)", file=sys.stderr)
        return 2
    project = Project(root)
    if project.root_unit is None and args.command != "check":
        print("error: the root manifest is invalid; run check", file=sys.stderr)
        return 2
    rel = project.rel
    if args.command == "tree":
        if args.json:
            print(json.dumps([describe(project, u) for u in project.units], indent=1))
        else:
            print_tree(project)
        return 0
    if args.command == "show":
        info = describe(project, project.unit_at(given))
        print(json.dumps(info, indent=1)) if args.json else print_show(info)
        return 0
    if args.command == "port":
        return print_port(project, project.unit_at(given), args.name)
    if args.command == "stats":
        data = stats(project)
        if args.json:
            print(json.dumps(data, indent=1))
            return 0
        print(f"{'files':>6} {'words':>8} {'context':>8}  unit")
        for row in data["units"]:
            print(f"{row['files']:>6} {row['words']:>8} {row['context-items']:>8}  {row['unit']}")
        total = data["total"]
        print(f"{total['files']:>6} {total['words']:>8} {total['context-items']:>8}  "
              f"total of {total['units']} unit(s), hand-written, without the copy of "
              "the standard")
        print(f"wiring: {total['wiring-lines']} line(s), of which {total['wiring-pass-up']} "
              f"pass a need up and {total['wiring-delegation']} delegate a port")
        print(f"ports: {total['ports']}, with contract {total['ports-with-contract']}, "
              f"with verified-by {total['ports-verified']}")
        print("units: " + ", ".join(f"{v} {k}" for k, v in total["units-by-status"].items() if v))
        print("decisions: " + (", ".join(f"{v} {k}" for k, v in
                                         total["decisions-by-status"].items()) or "none"))
        return 0
    if args.command == "skills":
        rows = [{"name": s["name"], "unit": rel(u.path), "path": rel(s["path"]),
                 "description": s["description"]}
                for u in project.units for s in skills_of(u)]
        if args.json:
            print(json.dumps(rows, indent=1))
        for row in rows if not args.json else []:
            print(f"{row['name']}  [{row['unit']}]  {row['path']}\n    {row['description']}")
        return 0
    if args.command == "decisions":
        rows = [{"path": rel(d["path"]), "unit": rel(u.path), "status": d["status"],
                 "date": d["date"], "title": d["title"]}
                for u in project.units for d in decisions_of(u)
                if not args.status or d["status"].startswith(args.status)]
        if args.json:
            print(json.dumps(rows, indent=1))
        for row in rows if not args.json else []:
            print(f"{row['status']:<10} {row['date']:<10} {row['path']}  {row['title']}")
        return 0
    if args.command == "cited-by":
        wanted = given.resolve()
        for unit in project.units:
            for path in managed_files(unit):
                if is_generated(path):
                    continue
                for link in links_in(path):
                    if SCHEME.match(link) or link.startswith(("#", "/")):
                        continue
                    if (path.parent / unquote(re.split(r"[#?]", link)[0])).resolve() == wanted:
                        print(rel(path))
                        break
        return 0
    if args.command == "site":
        out = Path(args.output) if args.output else root / "unifold.html"
        build_site(project, out, args.mermaid)
        print(f"wrote {out}")
        return 0
    if args.command == "generate":
        print(f"{write_generated(project)} generated file(s) written or removed "
              f"for {len(project.units)} unit(s)")
        return 0
    run_checks(project)
    if args.deps and project.root_unit is not None:
        check_deps(project, Path(args.deps))
    order = {"E": 0, "W": 1, "I": 2}
    findings = sorted(set(project.findings), key=lambda f: (f[2], order[f[0]], f[1], f[3]))
    counts = {s: sum(1 for f in findings if f[0] == s) for s in "EWI"}
    shown = [f for f in findings if not (args.quiet and f[0] == "I")]
    if args.json:
        print(json.dumps([{"severity": s, "rule": r, "file": p, "message": m}
                          for s, r, p, m in shown], indent=1))
    else:
        for severity, rule, path, message in shown:
            print(f"{severity} {rule} {path}: {message}")
        level = getattr(project, "level", "full")
        note = "Review rules C1 to C15 are not checked by this tool." if level == "full" \
            else "Level core: only manifests, wiring and generated files are checked."
        print(f"{len(project.units)} unit(s): {counts['E']} error(s), {counts['W']} "
              f"warning(s), {counts['I']} info. {note}")
    if project.root_unit is None:
        return 2
    return 1 if counts["E"] or (args.strict and counts["W"]) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:                 # output was piped into a command that stopped
        sys.stderr.close()
        sys.exit(0)
