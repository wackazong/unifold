# Unifold: architecture as code

Define the architecture by organizing your repo. Declare interfaces,contracts, dependencies and capabilities next to the code. Give people and agents the documentation they need, where they need it.

Units are the architectural building blocks. Units produce software artifacts. A whole repository can be just one unit, or multiple nested units.

Selected folders are declared as units. A unit describes what it provides and what it needs; the unit's parent unit connects its need to a provider. The integrated unifold check script fails when a need is unconnected, when a connection names something that does not exist, or when the code uses something that is not wired. The architecture diagrams are generated, so nobody draws them and they cannot disagree with the files.

The standard is explainable in one minute and adoptable in five. That is why the normative text is one page. Everything else is explanation, reference or a tutorial, and must not grow back into the standard. Two examples provide guidance for beginners. This repository itself is a specification, and a specification is not a unit: it has no manifest.

## Why

One large architecture document, one root file for agents, and a wiki beside the code go stale, and neither a newcomer nor a coding agent can take them in. Here the knowledge about a folder is in that folder, in the same places everywhere, and a folder can be understood without reading its neighbors. Structure is declared once and diagrams are generated. Reasons are written, because not making the same mistake twice matters.

## How it works

```text
# billing/unifold.yaml
summary: Creates invoices
needs:
  clock: {summary: A time source, contract: ../docs/references/time-protocol.md}
```

```text
# platform/unifold.yaml
summary: Shared runtime services
capabilities:
  clock: {summary: The current time, contract: ../docs/references/time-protocol.md}
```

```text
# unifold.yaml in the repository root
unifold: "0.1"
summary: Shop backend
wiring:
  billing.clock: platform.clock
```

Both sides name one document, `docs/references/time-protocol.md` of the root: the contract of the connection, which says what a clock gives and in which form. `unifold check` reads the three files and the build files, reports a need without a capability provider, a connection whose sides name different contracts or a dependency without a connection, and writes the component diagram. `unifold show billing` prints the unit, its need and who finally provides for it. The tutorial [Your first map](docs/tutorials/first-map.md) takes fifteen minutes.

## What a unit has

| File           | What it is                                                                                                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `unifold.yaml` | The manifest: what the unit provides and needs, and the wiring of its children. Checked against the siblings and the code.                                                                 |
| `README.md`    | The front page: what the unit is for, why it is built this way, what can be relied on.                                                                                                     |
| `docs/`        | Everything else written about the unit, in fixed places sorted by what the reader is doing: tutorials, skills, references, explanation, decisions. A file exists only when it has content. |
| `AGENTS.md`    | Generated: where the documents and skills of the unit are, for coding agents.                                                                                                              |

## How people use it

A newcomer opens a folder and finds its `README.md`: what the unit is for, why it is built this way, what can be relied on. `docs/tutorials/` teaches, `docs/skills/` says how to do a task, `docs/references/` holds the facts, `docs/explanation/` the reasoning, the invariants, the runtime, the deployment and the risks, one file each, and `docs/decisions/` the choices. A reviewer runs `unifold check` and the checklist in
[writing.md](docs/references/unifold/writing.md).

## How agents use it

`unifold init --agents` installs the two skills, writes their stubs into `.agents/skills` and `.claude/skills`, and adds the unifold block to the root `AGENTS.md`. Every unit's `AGENTS.md` is generated: a pointer to `README.md`, the documents by kind, the skills. `AGENTS.md` is read by most agents and the stubs are found by most; Kiro and Aider do not look there ([agents.md](docs/references/unifold/agents.md)). Every agent with a shell can run `unifold show`, which prints a folder's capabilities, needs and resolved neighbours, as text or JSON.

## Questions

**Do I need the tool?** The standard can be implemented by anyone, but the two promises, "checked" and "generated", need a checker. The reference tool is one Python file.

**Do I need an AI agent?** No. The files are YAML and Markdown.

**Does it read my code?** It reads build files and imports to find which unit depends on which, and compares that with the wiring. It works per pair of units. It does not judge whether a description is true.

**Do I have to write documentation?** Every unit has a `README.md` that says what it is for and why. Everything else in `docs/` is written when there is something to say. The checker reads links, headings and length, never meaning.

**Does it fit a project with one package?** Yes: a project of one unit. The map is one box; the documentation of the root is the point
([requirements](docs/explanation/requirements.md)).

**What ends up in my repository?** The `unifold.yaml` files, the generated diagrams and the generated `AGENTS.md` of every unit. The standard is not copied; the root manifest names its version. With `--agents`, also the skills and their stubs.

**What about my** `**docs/**` **folder, docs site and ADR tool?** `docs/` is where unifold keeps the documents, sorted by kind; a site is built from it. Existing decision records move to `docs/decisions/`
([documents.md](docs/references/unifold/documents.md)).

**Is it stable?** No. This is draft 0.1, unpublished. It has been tried on a handful of repositories and not measured in use
([risks](docs/explanation/risks.md)).

## Capabilities

What this repository provides. It is a specification, not a unit, so these are not declared in a manifest.

### The standard

The standard on one page, [spec.md](docs/references/unifold/spec.md), with the reference chapters beside it and a JSON Schema for the manifest. Published at
[https://unifold.md](https://unifold.md).

### The skills

Two skills in the [Agent Skills](https://agentskills.io/specification) format. [unifold-convert](docs/skills/unifold-convert/SKILL.md) brings an existing repository into the format: it has the agent find the units, write their manifests and check them against the code. No script derives units from code. [unifold](docs/skills/unifold/SKILL.md), with file templates, teaches an agent to find its unit, read the right files, change manifests and documents, and check the result.

### The tool

The reference tool, described in [tool.md](docs/references/unifold/tool.md) and tested by [tests/conformance.py](tests/conformance.py). It checks manifests, compares the wiring with dependencies in code, and generates the diagrams and the `AGENTS.md` files.

## Needs

### Python

Python 3.9 or newer with PyYAML, for the tool and the tests. The standard itself needs nothing.

## Commands

```text
# test the tool
python3 tests/conformance.py                                  

# check an example
python3 docs/skills/unifold/scripts/unifold.py check examples/plantwatch
```

## Read next

| Kind         | Pages                                                                                                                                                                                                                                                                                |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| The standard | [spec.md](docs/references/unifold/spec.md), the standard on one page; [unifold.schema.json](docs/references/unifold/unifold.schema.json)                                                                                                                                             |
| Reference    | [documents](docs/references/unifold/documents.md), [writing](docs/references/unifold/writing.md), [agents](docs/references/unifold/agents.md), [tool](docs/references/unifold/tool.md), [tool JSON](docs/references/unifold/tool-json.md), [rules](docs/references/unifold/rules.md) |
| Explanation  | [requirements](docs/explanation/requirements.md), [reasoning](docs/explanation/reasoning.md), [wiring](docs/explanation/wiring.md), [invariants](docs/explanation/invariants.md), [risks](docs/explanation/risks.md), [decisions](docs/decisions/index.md)                           |
| Tutorial     | [Your first map](docs/tutorials/first-map.md)                                                                                                                                                                                                                                        |
| Examples     | [examples/slugline](examples/slugline/README.md), a tested Cargo workspace; [examples/plantwatch](examples/plantwatch/README.md), a design written before any code, with every document convention                                                                                   |

## Contributing and licence

Changes to the standard are proposed as decision records; see [CONTRIBUTING.md](CONTRIBUTING.md) and the [decisions](docs/decisions/index.md).

Licensed under either of the Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE)) or the MIT license ([LICENSE-MIT](LICENSE-MIT)), at your option. The templates of the skill and everything the tool generates may be used without attribution. Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this work by you shall be dual licensed as above, without any additional terms or conditions.
