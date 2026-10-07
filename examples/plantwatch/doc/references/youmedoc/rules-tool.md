# Tool rules

These rules are enforced by the [checker](checker.md). The overview and the
severity letters are in [rules.md](rules.md). "Managed file" means `README.md`
and `AGENTS.md` of a unit and every `.md` file below its `doc/` folder, except
files in a skill's `assets/` and `scripts/` folders.

## S: structure

| ID | Sev. | Rule |
|---|---|---|
| S1 | E | The project root has a `README.md` whose manifest contains `unit` and `youmedoc`. |
| S2 | E | The `unit` name of every unit except the root equals the name of its folder. |
| S3 | E | Every unit has an `AGENTS.md`. |
| S4 | E | The children of a unit have different names. |
| S5 | W | `doc/` contains only `context.md`, `architecture.md`, `decisions/`, `references/`, `skills/`, `diagrams/` and `assets/`. |
| S6 | E | The root unit contains `doc/skills/read-docs/SKILL.md` and `doc/references/youmedoc/index.md`. |
| S7 | E | Every folder in `doc/skills/` contains a `SKILL.md` whose front matter has a `name` equal to the folder name and a `description`. |
| S8 | E | `AGENTS.md` links to the `SKILL.md` of every skill of the unit. |
| S9 | E | Every file in `doc/decisions/` except `index.md` is named `NNNN-short-title.md` and has front matter with a valid `status` and a `date`. |

## M: manifest

| ID | Sev. | Rule |
|---|---|---|
| M1 | E | The front matter is a valid YAML mapping, is closed with `---`, and has no duplicate keys. |
| M2 | E | The manifest has a one-line `summary`. |
| M3 | E | Unit names and port names follow the patterns in [manifest.md](manifest.md). |
| M4 | E | `provides`, `needs` and `wiring` are mappings, and every port has a `summary`. |
| M5 | W | The manifest and its ports contain only known keys. |
| M6 | E | `status` is `planned`, `active` or `deprecated`. |
| M7 | E / W | A relative `contract` path stays inside the unit (error) and exists (warning). |

## W: wiring

| ID | Sev. | Rule |
|---|---|---|
| W1 | E | Every wiring endpoint has an allowed form and names an existing direct child and an existing port on the correct side ([wiring.md](wiring.md)). |
| W2 | E | Every need of every child that is not `optional` is a key in the parent's wiring. |
| W3 | W | Every provided port of every child is the value of at least one wiring line. |
| W4 | W | A need and its provider have the same `kind`, if both state one. |
| W5 | I | An own need of a unit with children is passed to at least one child. |
| W6 | I | An own provided port of a unit with children is delegated to a child. |

## L: links

| ID | Sev. | Rule |
|---|---|---|
| L1 | E | The target of every relative link in a managed file exists. |
| L2 | E | A link that leaves the unit downward targets the `README.md` of a direct child, or of a nested project directly below the unit. |
| L3 | E | A link to a file of an ancestor occurs only in `doc/context.md` and targets the ancestor's `README.md`, `doc/decisions/` or `doc/references/`. |
| L4 | E | No link targets a sibling, any other unit that is neither ancestor nor descendant, or a file outside the project. No link is an absolute path. |
| L5 | W | Every managed file is reachable by links from the unit's `README.md` or `AGENTS.md`. |

`L2`, `L3` and `L4` do not apply to generated files. Links inside code blocks
and code spans are ignored. Anchors are not checked. For `L5`, links in
generated files count: a decision is reachable through the generated index.

## T: text

| ID | Sev. | Rule |
|---|---|---|
| T1 | E | A managed file has at most 200 lines. |
| T2 | W | A managed file starts with a `# ` title, after front matter and marker comment. |

## G: generated files

| ID | Sev. | Rule |
|---|---|---|
| G1 | W | Every generated file exists and equals what the generator would produce now. No leftover generated file exists. |
| G2 | E | A file in a generated location (`doc/diagrams/*.md`, `doc/decisions/index.md`) carries the generated marker. |

## Reading a finding

The checker prints one line per finding:

```text
E W2 cloud/README.md: need 'alerts.push' is not wired
```

The parts are: severity, rule ID, the file to change, and what is wrong. For
wiring rules the file is the parent's `README.md`, because the wiring lives
there.

## How to fix common findings

| Finding | Fix |
|---|---|
| `W2` need is not wired | Add a line to the parent's `wiring`. If no sibling provides it, add a need to the parent and pass it up, or mark the child's need `optional`. |
| `W3` provided but not needed | Remove the port, or wire the unit that should use it, or delegate it from a port of the parent. |
| `L3` upward link outside context.md | Move the citation to `doc/context.md`, restate it there, and link to `context.md` instead. |
| `L4` sideways link | Remove it. State what is wanted as a need in the manifest. |
| `L5` not reachable | Link the file from `AGENTS.md`, `README.md` or a file they link to. |
| `T1` too long | Split the file ([markdown.md](markdown.md)). |
| `G1` stale | Run the generator. |
