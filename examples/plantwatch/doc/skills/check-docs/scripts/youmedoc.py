#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""youmedoc reference checker and generator.

Commands:
  check [PATH]      check a youmedoc project against the tool-checked rules
  generate [PATH]   write diagrams and decision indexes from the manifests
  tree [PATH]       print the unit tree with ports
  init TARGET       copy the standard (references and skills) into TARGET

PATH is any folder inside a youmedoc project (default: current folder).
The rule IDs printed by `check` are defined in doc/references/youmedoc/rules-tool.md.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

TOOL_VERSION = "0.1.0"
SPEC_VERSION = "0.1"
MAX_LINES = 200
MAX_DEPTH = 3
MARK = "<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->"
MARK_PREFIX = "<!-- youmedoc:generated"
SKIP_DIRS = {"node_modules", "target", "__pycache__"}
DOC_ENTRIES = {"context.md", "architecture.md", "decisions", "references",
               "skills", "diagrams", "assets"}
MANIFEST_KEYS = {"unit", "summary", "youmedoc", "kind", "status",
                 "provides", "needs", "wiring"}
PROVIDE_KEYS = {"kind", "summary", "contract"}
NEED_KEYS = {"kind", "summary", "optional"}
STATUSES = {"planned", "active", "deprecated"}
DECISION_STATUSES = ("proposed", "accepted", "rejected", "deprecated", "superseded")
UNIT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
PORT_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DECISION_FILE = re.compile(r"^\d{4}-[a-z0-9][a-z0-9-]*\.md$")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
INLINE_LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^)]*[\"'])?\s*\)")
REF_LINK = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?\s*$")


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
    return path.read_text(encoding="utf-8", errors="replace")


def front_matter(path: Path):
    """Return (mapping or None, error or None) for the YAML front matter."""
    if not path.is_file():
        return None, None
    text = read_text(path)
    if not text.startswith("---"):
        return None, None
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, "front matter is not closed with '---'"
    try:
        data = yaml.load("\n".join(lines[1:end]), Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        return None, "invalid YAML front matter: " + " ".join(str(exc).split())
    if data is None:
        return {}, None
    if not isinstance(data, dict):
        return None, "front matter must be a YAML mapping"
    return data, None


def body_lines(path: Path) -> list[str]:
    """File lines without front matter."""
    lines = read_text(path).splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            return lines[end + 1:]
    return lines


def links_in(path: Path) -> list[str]:
    """Link targets in a Markdown file, ignoring code blocks and code spans."""
    out, fence = [], None
    for line in read_text(path).splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = stripped[:3]
            fence = None if fence == token else (fence or token)
            continue
        if fence:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        out += INLINE_LINK.findall(line)
        ref = REF_LINK.match(line)
        if ref:
            out.append(ref.group(1))
    return out


# ------------------------------------------------------------------ model

class Unit:
    def __init__(self, path: Path, manifest: dict, parent: "Unit | None"):
        self.path = path
        self.manifest = manifest
        self.parent = parent
        self.children: list[Unit] = []
        self.foreign: list[Path] = []          # nested projects below this unit
        self.name = str(manifest.get("unit", path.name))
        self.summary = str(manifest.get("summary") or "").strip()
        self.status = str(manifest.get("status", "active"))
        self.provides = self._ports("provides")
        self.needs = self._ports("needs")
        self.wiring: dict[str, list[str]] = {}
        raw = manifest.get("wiring")
        if isinstance(raw, dict):
            for key, value in raw.items():
                values = value if isinstance(value, list) else [value]
                self.wiring[str(key)] = [str(v) for v in values]

    def _ports(self, key: str) -> dict:
        raw = self.manifest.get(key)
        if not isinstance(raw, dict):
            return {}
        return {str(k): (v if isinstance(v, dict) else {}) for k, v in raw.items()}

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def child(self, name: str) -> "Unit | None":
        return next((c for c in self.children if c.name == name), None)

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
        manifest, error = front_matter(root / "README.md")
        if error:
            self.add("E", "M1", root / "README.md", error)
        if not isinstance(manifest, dict) or "unit" not in manifest \
                or "youmedoc" not in manifest:
            self.add("E", "S1", root / "README.md",
                     "project root needs a README.md manifest with 'unit' and 'youmedoc'")
            self.root_unit = None
            return
        self.root_unit = Unit(root, manifest, None)
        self.units.append(self.root_unit)
        self._walk(root, self.root_unit)

    def add(self, severity: str, rule: str, path: Path, message: str):
        self.findings.append((severity, rule, self.rel(path), message))

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix() or "."
        except ValueError:
            return str(path)

    def _walk(self, folder: Path, owner: Unit):
        for sub in sorted(p for p in folder.iterdir() if p.is_dir()):
            if sub.name.startswith(".") or sub.name in SKIP_DIRS:
                continue
            if sub.name == "doc" and folder == owner.path:
                continue
            manifest, error = front_matter(sub / "README.md")
            if error:
                self.add("E", "M1", sub / "README.md", error)
            current = owner
            if isinstance(manifest, dict) and "unit" in manifest:
                if "youmedoc" in manifest:           # nested project: opaque
                    owner.foreign.append(sub)
                    self.foreign[sub] = owner
                    continue
                current = Unit(sub, manifest, owner)
                owner.children.append(current)
                self.units.append(current)
            self._walk(sub, current)

    def owner_of(self, target: Path):
        """Return ('unit', Unit), ('foreign', Path) or (None, None)."""
        try:
            target.relative_to(self.root)
        except ValueError:
            return None, None
        for folder in self.foreign:
            if target == folder or folder in target.parents:
                return "foreign", folder
        best = self.root_unit
        for unit in self.units:
            if (unit.path == target or unit.path in target.parents) \
                    and len(unit.path.parts) > len(best.path.parts):
                best = unit
        return "unit", best


def find_root(start: Path) -> Path | None:
    folder = start.resolve()
    for candidate in [folder, *folder.parents]:
        manifest, _ = front_matter(candidate / "README.md")
        if isinstance(manifest, dict) and "unit" in manifest and "youmedoc" in manifest:
            return candidate
    return None


def managed_files(unit: Unit) -> list[Path]:
    """Markdown files that youmedoc rules apply to, for one unit."""
    files = [p for p in (unit.path / "README.md", unit.path / "AGENTS.md") if p.is_file()]
    doc = unit.path / "doc"
    if doc.is_dir():
        for path in sorted(doc.rglob("*.md")):
            parts = path.relative_to(doc).parts
            if len(parts) > 2 and parts[0] == "skills" and parts[2] in ("assets", "scripts"):
                continue
            files.append(path)
    return files


def is_generated(path: Path) -> bool:
    return path.is_file() and read_text(path).lstrip().startswith(MARK_PREFIX)


# ------------------------------------------------------------ check rules

def check_manifest(project: Project, unit: Unit):
    readme, m = unit.path / "README.md", unit.manifest
    if not unit.is_root and unit.name != unit.path.name:
        project.add("E", "S2", readme, f"unit '{unit.name}' must equal the folder name "
                                       f"'{unit.path.name}'")
    if not UNIT_NAME.match(unit.name):
        project.add("E", "M3", readme, f"unit name '{unit.name}' must match {UNIT_NAME.pattern}")
    summary = m.get("summary")
    if not isinstance(summary, str) or not summary.strip() or "\n" in summary.strip():
        project.add("E", "M2", readme, "manifest needs a one-line 'summary'")
    for key in m:
        if key not in MANIFEST_KEYS:
            project.add("W", "M5", readme, f"unknown manifest key '{key}'")
    if unit.status not in STATUSES:
        project.add("E", "M6", readme, f"status '{unit.status}' must be one of "
                                       f"{sorted(STATUSES)}")
    for section, allowed in (("provides", PROVIDE_KEYS), ("needs", NEED_KEYS)):
        raw = m.get(section)
        if raw is None:
            continue
        if not isinstance(raw, dict):
            project.add("E", "M4", readme, f"'{section}' must be a mapping of port names")
            continue
        for port, spec in raw.items():
            if not PORT_NAME.match(str(port)):
                project.add("E", "M3", readme, f"port name '{port}' must match "
                                               f"{PORT_NAME.pattern}")
            if not isinstance(spec, dict) or not str(spec.get("summary") or "").strip():
                project.add("E", "M4", readme, f"{section}.{port} needs a 'summary'")
                continue
            for key in spec:
                if key not in allowed:
                    project.add("W", "M5", readme, f"unknown key '{key}' in {section}.{port}")
            contract = spec.get("contract")
            if section == "provides" and isinstance(contract, str) \
                    and not SCHEME.match(contract):
                target = (unit.path / contract).resolve()
                if unit.path.resolve() not in [target, *target.parents]:
                    project.add("E", "M7", readme, f"contract of '{port}' points outside "
                                                   f"the unit: {contract}")
                elif not target.exists():
                    project.add("W", "M7", readme, f"contract of '{port}' does not exist "
                                                   f"yet: {contract}")
    raw = m.get("wiring")
    if raw is not None and not isinstance(raw, dict):
        project.add("E", "M4", readme, "'wiring' must be a mapping of need to provider")


def check_wiring(project: Project, unit: Unit):
    readme = unit.path / "README.md"
    names = [c.name for c in unit.children]
    for name in sorted({n for n in names if names.count(n) > 1}):
        project.add("E", "S4", readme, f"two child units are named '{name}'")
    used_providers: set[str] = set()
    used_own_needs: set[str] = set()
    for key, values in unit.wiring.items():
        need_kind = None
        if "." in key:
            child_name, need = key.split(".", 1)
            child = unit.child(child_name)
            if child is None:
                project.add("E", "W1", readme, f"wiring key '{key}': no child unit "
                                               f"'{child_name}'")
            elif need not in child.needs:
                project.add("E", "W1", readme, f"wiring key '{key}': '{child_name}' "
                                               f"has no need '{need}'")
            else:
                need_kind = child.needs[need].get("kind")
        elif key not in unit.provides:
            project.add("E", "W1", readme, f"wiring key '{key}': not a provided port of "
                                           f"'{unit.name}'")
        else:
            need_kind = unit.provides[key].get("kind")
        for value in values:
            kind = None
            if "." in value:
                child_name, port = value.split(".", 1)
                child = unit.child(child_name)
                if child is None:
                    project.add("E", "W1", readme, f"wiring '{key}: {value}': no child "
                                                   f"unit '{child_name}'")
                elif port not in child.provides:
                    project.add("E", "W1", readme, f"wiring '{key}: {value}': "
                                                   f"'{child_name}' does not provide '{port}'")
                else:
                    kind = child.provides[port].get("kind")
                    used_providers.add(value)
                    if "." in key and key.split(".", 1)[0] == child_name:
                        project.add("E", "W1", readme, f"wiring '{key}: {value}': a unit "
                                                       "cannot provide its own need")
            elif "." not in key:
                project.add("E", "W1", readme, f"wiring '{key}: {value}': a provided port "
                                               "cannot be wired straight to an own need")
            elif value not in unit.needs:
                project.add("E", "W1", readme, f"wiring '{key}: {value}': not a need of "
                                               f"'{unit.name}'")
            else:
                kind = unit.needs[value].get("kind")
                used_own_needs.add(value)
            if need_kind and kind and need_kind != kind:
                project.add("W", "W4", readme, f"wiring '{key}: {value}': kinds differ "
                                               f"({need_kind} vs {kind})")
    for child in unit.children:
        for need, spec in child.needs.items():
            if f"{child.name}.{need}" not in unit.wiring and not spec.get("optional"):
                project.add("E", "W2", readme, f"need '{child.name}.{need}' is not wired")
        for port in child.provides:
            if f"{child.name}.{port}" not in used_providers:
                project.add("W", "W3", readme, f"'{child.name}.{port}' is provided but "
                                               "nothing needs it")
    if unit.children:
        for need in unit.needs:
            if need not in used_own_needs:
                project.add("I", "W5", readme, f"own need '{need}' is not passed to any "
                                               "child (used by this unit's own code?)")
        for port in unit.provides:
            if port not in unit.wiring:
                project.add("I", "W6", readme, f"provided port '{port}' is not delegated "
                                               "to a child (implemented by this unit's own code?)")


def check_structure(project: Project, unit: Unit):
    agents = unit.path / "AGENTS.md"
    if not agents.is_file():
        project.add("E", "S3", unit.path, "unit has no AGENTS.md")
    doc = unit.path / "doc"
    if doc.is_dir():
        for entry in sorted(doc.iterdir()):
            if entry.name not in DOC_ENTRIES and not entry.name.startswith("."):
                project.add("W", "S5", entry, "unknown entry in doc/")
    if unit.is_root:
        for required in ("doc/skills/read-docs/SKILL.md", "doc/references/youmedoc/index.md"):
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
    decisions = doc / "decisions"
    if decisions.is_dir():
        for path in sorted(decisions.glob("*.md")):
            if path.name == "index.md":
                continue
            if not DECISION_FILE.match(path.name):
                project.add("E", "S9", path, "decision file name must look like "
                                             "0001-short-title.md")
            meta, error = front_matter(path)
            if error or not isinstance(meta, dict):
                project.add("E", "S9", path, error or "decision needs YAML front matter "
                                                      "with status and date")
                continue
            status = str(meta.get("status") or "")
            if not status.startswith(DECISION_STATUSES):
                project.add("E", "S9", path, f"decision status must start with one of "
                                             f"{list(DECISION_STATUSES)}")
            if not meta.get("date"):
                project.add("E", "S9", path, "decision needs a 'date'")


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
            here = project.rel(path)
            if link.startswith("/"):
                project.add("E", "L4", path, f"absolute link '{link}'; use a relative link")
                continue
            target = (path.parent / unquote(re.split(r"[#?]", link)[0])).resolve()
            if not target.exists():
                project.add("E", "L1", path, f"link target does not exist: {link}")
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
                allowed = [(owner.path / "README.md").resolve()]
                roots = [(owner.path / "doc" / d).resolve() for d in ("decisions", "references")]
                ok = target in allowed or any(r in target.parents for r in roots)
                if path.resolve() != context:
                    project.add("E", "L3", path, f"upward link outside doc/context.md: {link}")
                elif not ok:
                    project.add("E", "L3", path, f"context.md may only cite an ancestor's "
                                                 f"README.md, decisions or references: {link}")
            else:
                project.add("E", "L4", path, f"sideways link into '{owner.name}' ({here} "
                                             f"must not know its siblings): {link}")
    start = [p.resolve() for p in (unit.path / "README.md", unit.path / "AGENTS.md")]
    seen, queue = set(start), list(start)
    while queue:
        for target in graph.get(queue.pop(), ()):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    for path in files:
        if path.resolve() not in seen:
            project.add("W", "L5", path, "file is not reachable by links from README.md "
                                         "or AGENTS.md")


def check_text(project: Project, unit: Unit):
    for path in managed_files(unit):
        count = len(read_text(path).splitlines())
        if count > MAX_LINES:
            project.add("E", "T1", path, f"{count} lines; the limit is {MAX_LINES}")
        first = next((l for l in body_lines(path)
                      if l.strip() and not l.lstrip().startswith("<!--")), "")
        if not first.startswith("# "):
            project.add("W", "T2", path, "file should start with a '# ' title")


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
        check_text(project, unit)
    check_generated(project)


# ------------------------------------------------------------- generation

def node_id(project: Project, unit: Unit) -> str:
    rel = project.rel(unit.path)
    return "u_root" if rel == "." else "u_" + re.sub(r"[^A-Za-z0-9]", "_", rel)


def port_id(project: Project, unit: Unit, side: str, port: str) -> str:
    return f"{side}_{node_id(project, unit)[2:]}_" + re.sub(r"[^A-Za-z0-9]", "_", port)


def link_to(source_dir: Path, target: Path) -> str:
    return Path(os.path.relpath(target, source_dir)).as_posix()


def best_diagram(unit: Unit) -> Path:
    name = "component.md" if unit.children else "context.md"
    return unit.path / "doc" / "diagrams" / name


def mermaid(project: Project, frame: Unit, focus: Unit, depth: int, out_dir: Path):
    """Build one diagram. Returns (mermaid lines, units shown)."""
    def expanded(unit: Unit) -> bool:
        level = unit.depth_below(focus)
        return bool(unit.children) and unit is not frame \
            and level is not None and level <= depth - 1

    def need_sources(unit: Unit, need: str) -> list[str]:
        if expanded(unit):
            found = []
            for key, values in unit.wiring.items():
                if "." in key and need in values:
                    child = unit.child(key.split(".", 1)[0])
                    if child:
                        found += need_sources(child, key.split(".", 1)[1])
            if found:
                return found
        return [node_id(project, unit)]

    def providers(unit: Unit, port: str) -> list[str]:
        if expanded(unit):
            found = []
            for value in unit.wiring.get(port, []):
                if "." in value:
                    child = unit.child(value.split(".", 1)[0])
                    if child:
                        found += providers(child, value.split(".", 1)[1])
            if found:
                return found
        return [node_id(project, unit)]

    shown: list[Unit] = [frame]
    lines = ["flowchart LR"]
    planned, clicks = [], []

    def emit(unit: Unit, indent: str):
        shown.append(unit)
        if unit.status == "planned":
            planned.append(node_id(project, unit))
        if expanded(unit):
            lines.append(f'{indent}subgraph {node_id(project, unit)}["{unit.name}"]')
            for child in unit.children:
                emit(child, indent + "  ")
            lines.append(f"{indent}end")
        else:
            lines.append(f'{indent}{node_id(project, unit)}["{unit.name}"]')
            clicks.append(f'  click {node_id(project, unit)} href '
                          f'"{link_to(out_dir, unit.path / "README.md")}"')

    lines.append(f'  subgraph {node_id(project, frame)}["{frame.name}"]')
    if frame.status == "planned":
        planned.append(node_id(project, frame))
    for child in frame.children:
        emit(child, "    ")
    lines.append("  end")

    edges: list[tuple[str, str, str, bool]] = []
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
        for key, values in unit.wiring.items():
            dashed = len(values) > 1
            for value in values:
                if unit is frame and not touches(key, value):
                    continue
                if "." in key:
                    child = unit.child(key.split(".", 1)[0])
                    need = key.split(".", 1)[1]
                    if child is None:
                        continue
                    sources = need_sources(child, need)
                    if "." in value:
                        sibling = unit.child(value.split(".", 1)[0])
                        port = value.split(".", 1)[1]
                        if sibling is None:
                            continue
                        targets = providers(sibling, port)
                    elif unit is frame and value in unit.needs:
                        port = value
                        pid = port_id(project, frame, "n", value)
                        frame_ports[pid] = f'{{{{"{value}"}}}}'
                        targets = [pid]
                    else:
                        continue
                    label = need if need == port else f"{need} → {port}"
                elif unit is frame and "." in value and key in unit.provides:
                    child = unit.child(value.split(".", 1)[0])
                    port = value.split(".", 1)[1]
                    if child is None:
                        continue
                    pid = port_id(project, frame, "p", key)
                    frame_ports[pid] = f'(["{key}"])'
                    sources, targets = [pid], providers(child, port)
                    label = "" if key == port else port
                else:
                    continue
                for source in sources:
                    for target in targets:
                        edge = (source, target, label, dashed)
                        if edge not in edges:
                            edges.append(edge)
        for child in unit.children:
            if expanded(child):
                collect(child)

    collect(frame)
    for pid, shape in frame_ports.items():
        lines.append(f"  {pid}{shape}")
    for source, target, label, dashed in edges:
        arrow = "-.->" if dashed else "-->"
        lines.append(f'  {source} {arrow}|"{label}"| {target}' if label
                     else f"  {source} {arrow} {target}")
    lines += clicks
    lines.append("  classDef focus stroke-width:4px")
    lines.append("  classDef planned stroke-dasharray:6 4")
    if planned:
        lines.append(f"  class {','.join(planned)} planned")
    if focus is not frame:
        lines.append(f"  class {node_id(project, focus)} focus")
    return lines, shown


def unit_table(units: list[Unit], out_dir: Path) -> list[str]:
    rows = ["| Unit | Summary | Status | Diagram |", "|---|---|---|---|"]
    for unit in units:
        readme = link_to(out_dir, unit.path / "README.md")
        diagram = best_diagram(unit)
        rows.append(f"| [{unit.name}]({readme}) | {unit.summary} | {unit.status} | "
                    f"[{diagram.stem}]({link_to(out_dir, diagram)}) |")
    return rows


def page(unit: Unit, title: str, intro: str, diagram: list[str], table: list[str],
         kinds: list[str], current: str) -> str:
    nav = [f"[{unit.name}](../../README.md)"]
    nav += [f"[{k}]({k}.md)" for k in kinds if k != current]
    return "\n".join([MARK, f"# {title}", "", " · ".join(nav), "", intro, "",
                      "```mermaid", *diagram, "```", "", *table, ""])


LEGEND = ("Arrows point from the side that needs something to the side that provides "
          "it. Rounded nodes are ports the framing unit provides, hexagons are its "
          "needs. Dashed arrows are alternative providers; dashed borders mark planned "
          "units.")


def root_context(project: Project, unit: Unit, out_dir: Path):
    uid = node_id(project, unit)
    lines = ["flowchart LR", f'  {uid}["{unit.name}"]']
    rows = ["| Port | Direction | Kind | Summary |", "|---|---|---|---|"]
    for port, spec in unit.provides.items():
        pid = port_id(project, unit, "p", port)
        lines += [f'  {pid}(["{port}"])', f"  {pid} --> {uid}"]
        rows.append(f"| {port} | provided | {spec.get('kind', '')} | {spec.get('summary', '')} |")
    for need, spec in unit.needs.items():
        pid = port_id(project, unit, "n", need)
        lines += [f'  {pid}{{{{"{need}"}}}}', f"  {uid} --> {pid}"]
        rows.append(f"| {need} | needed | {spec.get('kind', '')} | {spec.get('summary', '')} |")
    lines += ["  classDef focus stroke-width:4px", f"  class {uid} focus"]
    return lines, rows


def generate(project: Project) -> dict[Path, str]:
    """Return {path: content} for every generated file of the project."""
    out: dict[Path, str] = {}
    if project.root_unit is None:
        return out
    for unit in project.units:
        folder = unit.path / "doc" / "diagrams"
        kinds = ["context"] + (["component", "architecture"] if unit.children else [])
        if unit.is_root:
            diagram, table = root_context(project, unit, folder)
            intro = (f"`{unit.name}` and the outside world: the ports it provides "
                     "(rounded) and the things it needs from outside (hexagons).")
        else:
            diagram, shown = mermaid(project, unit.parent, unit, 0, folder)
            table = unit_table(shown, folder)
            intro = (f"`{unit.name}` among its siblings inside `{unit.parent.name}`. "
                     f"Only connections that touch `{unit.name}` are drawn. " + LEGEND)
        out[folder / "context.md"] = page(unit, f"Context diagram: {unit.name}", intro,
                                          diagram, table, kinds, "context")
        if not unit.children:
            continue
        diagram, shown = mermaid(project, unit, unit, 1, folder)
        intro = f"The units directly inside `{unit.name}` and how they are wired. " + LEGEND
        out[folder / "component.md"] = page(unit, f"Component diagram: {unit.name}", intro,
                                            diagram, unit_table(shown, folder), kinds,
                                            "component")
        frame = unit if unit.is_root else unit.parent
        for depth in range(MAX_DEPTH, 0, -1):
            diagram, shown = mermaid(project, frame, unit, depth, folder)
            note = "" if depth == MAX_DEPTH else \
                f" Depth reduced to {depth} to stay within {MAX_LINES} lines."
            where = "" if unit.is_root else f" next to its siblings in `{frame.name}`"
            intro = (f"`{unit.name}`{where}, opened up to {depth} level(s) down."
                     f"{note} " + LEGEND)
            content = page(unit, f"Architecture diagram: {unit.name}", intro, diagram,
                           unit_table(shown, folder), kinds, "architecture")
            if len(content.splitlines()) <= MAX_LINES:
                break
        out[folder / "architecture.md"] = content
    for unit in project.units:
        folder = unit.path / "doc" / "decisions"
        files = sorted(p for p in folder.glob("*.md") if p.name != "index.md") \
            if folder.is_dir() else []
        if not files:
            continue
        rows = ["| No. | Decision | Status | Date |", "|---|---|---|---|"]
        for path in files:
            meta, _ = front_matter(path)
            meta = meta if isinstance(meta, dict) else {}
            title = next((l[2:].strip() for l in body_lines(path) if l.startswith("# ")),
                         path.stem)
            rows.append(f"| {path.name[:4]} | [{title}]({path.name}) | "
                        f"{meta.get('status', '')} | {meta.get('date', '')} |")
        out[folder / "index.md"] = "\n".join(
            [MARK, f"# Decisions of {unit.name}", "",
             "[README](../../README.md) · [AGENTS.md](../../AGENTS.md)", "", *rows, ""])
    return out


def write_generated(project: Project) -> int:
    expected, changed = generate(project), 0
    for path, content in expected.items():
        if not path.is_file() or read_text(path) != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            changed += 1
    for unit in project.units:
        folder = unit.path / "doc" / "diagrams"
        if folder.is_dir():
            for path in folder.glob("*.md"):
                if path not in expected and is_generated(path):
                    path.unlink()
                    changed += 1
    return changed


# --------------------------------------------------------------- commands

def print_tree(project: Project):
    def show(unit: Unit, indent: str):
        ports = []
        if unit.provides:
            ports.append("provides " + ", ".join(unit.provides))
        if unit.needs:
            ports.append("needs " + ", ".join(unit.needs))
        suffix = f"  ({'; '.join(ports)})" if ports else ""
        print(f"{indent}{unit.name} [{unit.status}]{suffix}")
        for child in unit.children:
            show(child, indent + "  ")
        for folder in unit.foreign:
            print(f"{indent}  {folder.name} [nested project, not checked]")
    show(project.root_unit, "")


def init(target: Path) -> int:
    source = Path(__file__).resolve().parents[4]
    items = ["doc/references/youmedoc", "doc/skills/read-docs",
             "doc/skills/write-docs", "doc/skills/check-docs"]
    for item in items:
        if not (source / item).exists():
            print(f"error: {source / item} not found; run init from a full copy of the "
                  "standard", file=sys.stderr)
            return 2
    for item in items:
        shutil.copytree(source / item, target / item, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
        print(f"copied {item}")
    print("Next: write README.md (manifest with 'youmedoc: \"%s\"') and AGENTS.md from "
          "the templates in doc/skills/write-docs/assets/." % SPEC_VERSION)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="youmedoc", description=__doc__.split("\n")[0])
    parser.add_argument("--version", action="version", version=TOOL_VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "generate", "tree"):
        cmd = sub.add_parser(name)
        cmd.add_argument("path", nargs="?", default=".")
        if name == "check":
            cmd.add_argument("--strict", action="store_true",
                             help="exit with 1 on warnings too")
            cmd.add_argument("--quiet", action="store_true", help="hide info findings")
    sub.add_parser("init").add_argument("target")
    args = parser.parse_args(argv)
    if args.command == "init":
        return init(Path(args.target))
    root = find_root(Path(args.path))
    if root is None:
        print("error: no youmedoc project found (no README.md manifest with 'youmedoc' "
              "here or above)", file=sys.stderr)
        return 2
    project = Project(root)
    if args.command == "tree":
        if project.root_unit:
            print_tree(project)
        return 0
    if args.command == "generate":
        if project.root_unit is None:
            print("error: root manifest is invalid; run check", file=sys.stderr)
            return 2
        print(f"{write_generated(project)} generated file(s) written or removed "
              f"for {len(project.units)} unit(s)")
        return 0
    run_checks(project)
    order = {"E": 0, "W": 1, "I": 2}
    findings = sorted(set(project.findings), key=lambda f: (f[2], order[f[0]], f[1], f[3]))
    counts = {s: sum(1 for f in findings if f[0] == s) for s in "EWI"}
    for severity, rule, path, message in findings:
        if severity == "I" and args.quiet:
            continue
        print(f"{severity} {rule} {path}: {message}")
    print(f"{len(project.units)} unit(s): {counts['E']} error(s), {counts['W']} "
          f"warning(s), {counts['I']} info")
    return 1 if counts["E"] or (args.strict and counts["W"]) else 0


if __name__ == "__main__":
    sys.exit(main())
