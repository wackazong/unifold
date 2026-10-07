# Tool rules

These rules are enforced by the [checker](checker.md). The overview and the
severity letters are in [rules.md](rules.md). "Managed file" is defined in
[markdown.md](markdown.md).

## S: structure

| ID | Sev. | Rule |
|---|---|---|
| S1 | E | The project root has a manifest that contains `unit` and `unifold`, and the version is one the tool supports. |
| S2 | E | The `unit` name of every unit except the root equals the name of its folder. |
| S3 | E | Every unit has a `README.md`. |
| S4 | E | The children of a unit have different names. |
| S5 | W | `doc/` contains only the entries the standard defines. Other entries are reported and not checked. |
| S6 | E | The root unit contains `doc/skills/read-docs/SKILL.md` and `doc/references/unifold/index.md`. |
| S7 | E | Every folder in `doc/skills/` contains a `SKILL.md` whose front matter has a `name` equal to the folder name and a `description`. |
| S8 | E | `AGENTS.md` links to the `SKILL.md` of every skill of the unit. |
| S9 | E | Every decision file is named `NNNN-short-title.md` with a number that is unique in the unit, and has front matter with a valid `status` and a `date`. |
| S10 | E | A decision with status `accepted` names its `decision-makers`. |
| S11 | E | Every unit has an `AGENTS.md`. |

## M: manifest

| ID | Sev. | Rule |
|---|---|---|
| M1 | E | The manifest is a valid YAML mapping without duplicate keys, and it is in one place: `unit.yaml` or the front matter of `README.md`. |
| M2 | E | The manifest has a one-line `summary`. |
| M3 | E | Unit names and port names follow the patterns in [manifest.md](manifest.md). |
| M4 | E | `provides`, `needs` and `wiring` are mappings, every port has a `summary`, `optional` is `true` or `false`, and a provider is one endpoint or a map of named alternatives. |
| M5 | E | The manifest and its ports contain only known keys or keys that start with `x-`. Root-only keys are in the root manifest. |
| M6 | E | `status` is `planned`, `active` or `deprecated`. `level` is `core` or `full`. |
| M7 | E / W | A relative `contract` or `verified-by` path stays inside the unit (error) and exists (warning). |
| M8 | W | Every provided port of an `active` unit has `verified-by`. |
| M9 | E | `conforms-to` of a provided port names a need of the same unit. |

## W: wiring

| ID | Sev. | Rule |
|---|---|---|
| W1 | E | Every wiring endpoint has an allowed form and names an existing direct child and an existing port on the correct side, or a plain folder inside the unit ([wiring.md](wiring.md)). |
| W2 | E | Every need of every child that is not `optional` is a key in the parent's wiring. |
| W3 | W | Every provided port of every child is the value of at least one wiring line. |
| W4 | W | A need and its provider have the same `kind`, if both state one. |
| W5 | I | An own need of a unit with children is passed to at least one child. |
| W6 | I | An own provided port of a unit with children is delegated to a child. |
| W7 | W | The children of a unit do not need each other in a cycle. |
| W8 | I | A need is met by a plain folder that is not a unit yet. |
| W9 | W | A unit that is `active` does not get a need from a unit that is only `planned`. |
| W10 | W | Alternatives of one need that say `conforms-to` conform to the same definition. |

## L: links and mentions

| ID | Sev. | Rule |
|---|---|---|
| L1 | E | The target of every relative link in a managed file exists. |
| L2 | E | A link that leaves the unit downward targets the `README.md` of a direct child, or of a nested project directly below the unit. |
| L3 | E | A link to a file of an ancestor occurs only in `doc/context.md` and targets the ancestor's `README.md`, `doc/decisions/` or `doc/references/`. |
| L4 | E | No link targets a sibling, any other unit that is neither ancestor nor descendant, or a file outside the project. No link is an absolute path. |
| L5 | E | Every managed file is reachable by links from the unit's `README.md` or `AGENTS.md`. |
| L6 | W | No file except `doc/context.md` contains the name of a sibling or ancestor unit in code font. The name of the root unit is exempt; it is usually the name of the product. |
| L7 | W | `doc/context.md` cites no decision that is rejected, deprecated or superseded. |
| L8 | W | `doc/context.md` of an `active` unit cites no decision that is still `proposed`. |
| L9 | W | Every item of `doc/context.md` is a `###` heading with a link, followed by a paragraph that starts with `Says` and one that starts with `Here`. |

`L2`, `L3`, `L4` and `L6` do not apply to generated files. Links inside code
blocks and code spans are ignored. Anchors are not checked. For `L5`, links
in generated files count: a decision is reachable through the generated
index.

## T: text

| ID | Sev. | Rule |
|---|---|---|
| T1 | E | A managed file has at most 200 lines. |
| T2 | W | A managed file starts with a `# ` title, after front matter and marker comment. |
| T3 | W | A hand-written managed file has no line of more than 400 characters. |
| T4 | W | The `## Why` section of `AGENTS.md` has at most 20 non-blank lines. |
| T5 | W | A `###` heading in code font under `## Provides` or `## Needs` of a `README.md` names a port or need of the manifest. |
| T6 | W | The title of a unit's `README.md` is the unit name. The root unit is exempt. |

## G: generated files

| ID | Sev. | Rule |
|---|---|---|
| G1 | W | Every generated file exists and equals what the generator would produce now. No leftover generated file exists. |
| G2 | E | A file in a generated location (`doc/diagrams/*.md`, `doc/decisions/index.md`) carries the generated marker. |

## D: dependencies in code

Checked only when `check` is given a list of observed dependencies with
`--deps` ([checker.md](checker.md)).

| ID | Sev. | Rule |
|---|---|---|
| D1 | E | Code in one unit depends on code in another unit only where a need of the first is wired to the second, or the second is a direct child. |
| D2 | I | For every wiring line of kind `library`, a dependency between the two units was observed. |

## Levels

At level `core` only `S1` to `S4` and the `M`, `W`, `G` and `D` rules apply.
At level `full` all rules apply.

## Reading a finding

The checker prints one line per finding:

```text
E W2 cloud/README.md: need 'alerts.push' is not wired
```

The parts are: severity, rule ID, the file to change, and what is wrong. For
wiring rules the file is the parent's manifest, because the wiring lives
there.

## How to fix common findings

| Finding | Fix |
|---|---|
| `W2` need is not wired | Add a line to the parent's `wiring`. If no sibling provides it, add a need to the parent and pass it up, or name the plain folder that provides it today. Never mark a need `optional` to silence this. |
| `W3` provided but not needed | Remove the port, or wire the unit that should use it, or delegate it from a port of the parent. |
| `W4` kinds differ | Put an adapter unit between the two. Do not change the kind of the need to match. |
| `W7` cycle | Move what both need into a third unit, or turn one direction into an event the other subscribes to. |
| `L3` upward link outside context.md | Move the citation to `doc/context.md`, restate it there, and link to `context.md` instead. |
| `L4` sideways link, `L6` sibling named | Remove it. State what is wanted as a need in the manifest. |
| `L1` or `L5` on a diagram or decision index | Run the generator. |
| `T1` too long, `T3` long line | Split the file or the table ([markdown.md](markdown.md)). |
| `M8` no `verified-by` | Point to the tests of the port. If there are none, the unit is not `active` yet. |
| `D1` undeclared dependency | Declare the need and wire it, or remove the dependency from the code. |
| `T5` stale heading | Rename or remove the section; the manifest is the list of ports. |
| `G1` stale | Run the generator. |
