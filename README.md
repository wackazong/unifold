# unifold: architecture as code

> Your project structure is your architecture. Keep your documentation, architecture, and project structure aligned.

A folder with a `unifold.yaml` is a unit: it declares what it is responsible for, what it provides and what it needs, next to the code, and the unit above connects every need to a provider. A contract defines every connection, part by part, with examples and the fake that tests use; a scenario tells a story of the system as hops across the map. The unifold tool checks that all of this is consistent and generates the diagrams, so nobody draws them and they cannot disagree with the files. Every unit keeps its documents in the same places, so that a person or a coding agent can understand one folder without reading its neighbours.

## Why

One large architecture document, one root file for agents and a wiki beside the code go stale, and neither a newcomer nor a coding agent can take them in. Here the knowledge about a folder is in that folder. Structure is declared once and generated, because it is cheap to derive and expensive to keep correct by hand. Reasons are written, because they cannot be derived, and because nobody should make the same mistake twice.

The standard is explainable in one minute and adoptable in five. That is why the normative text is one page, and why everything else is reference, explanation or a tutorial.

## How it works

```yaml
# billing/unifold.yaml
responsibility: Creates invoices
needs:
  clock:
    summary: A time source
    contract: ../docs/references/clock.md
```

```yaml
# platform/unifold.yaml
responsibility: Shared runtime services
capabilities:
  clock:
    summary: The current time
    contract: ../docs/references/clock.md
```

```yaml
# unifold.yaml in the repository root
unifold: "0.3"
name: shop
responsibility: Shop backend
wiring:
  billing.clock: platform.clock
```

`billing` says what it needs, never who supplies it; the root connects the need to `platform`. Both sides name one document, `docs/references/clock.md` of the root: the contract of the connection, which says what a clock gives and in which form. `unifold check` reads the three manifests and writes the component diagram. It fails on a need without a provider, and on two sides that name different contracts. Without the wiring line in the root:

```text
error W2 unifold.yaml: need 'billing.clock' has no provider
    fix: Add `billing.clock: platform.clock` to the wiring.
```

`unifold show billing` prints the unit, its need and who finally provides it. The tutorial [Your first map](https://unifold.md/first-map) takes fifteen minutes.

## What a unit has

| File | What it is |
|---|---|
| `unifold.yaml` | The manifest: the unit's responsibility, kind and secret, what it provides and needs, the wiring of its children and the scenarios it holds. Checked against the other manifests and the contracts. |
| `README.md` | The front page: what the unit is for, and why it is built this way. The contracts say what can be relied on. |
| `docs/` | Everything else written about the unit, in fixed places sorted by what the reader is doing: tutorials, skills, references, explanation, decisions. A file exists only when it has content. |
| `AGENTS.md` | Generated: where the documents and skills of the unit are, for coding agents. |

## How people use it

A newcomer opens a folder and reads its `README.md`. `docs/tutorials/` teaches, `docs/skills/` says how to do a task, `docs/references/` holds the facts, `docs/explanation/` the reasoning, the invariants, the runtime, the deployment and the risks, and `docs/decisions/` the choices. A reviewer runs `unifold check` and works through the [review checklist](https://unifold.md/writing#review-checklist).

## How agents use it

`unifold init --agents` installs the two skills, writes their stubs into `.agents/skills/` and `.claude/skills/`, and adds the unifold block to the root `AGENTS.md`. Every unit's `AGENTS.md` is generated: a pointer to `README.md`, the documents by kind, the skills. Most agents read `AGENTS.md` and find the stubs; Kiro and Aider do not ([agents](https://unifold.md/agents)). Every agent with a shell can run `unifold show`, which prints a folder's capabilities, needs and resolved neighbours, as text or JSON.

## What this repository provides

### The standard

The standard on one page, [spec.md](https://unifold.md/spec), with the reference chapters beside it and a [JSON Schema](https://unifold.md/0.3/unifold.schema.json) for the manifest. Published at [unifold.md](https://unifold.md).

### The skills

Two skills in the [Agent Skills](https://agentskills.io/specification) format. [unifold](https://unifold.md/skill/SKILL.md), with file templates, teaches an agent to find its unit, read the right files, change manifests and documents, and check the result. [unifold-convert](https://unifold.md/skill/unifold-convert/SKILL.md) brings an existing repository into the map: the agent chooses the units, writes their manifests, and compares them with the code. No script derives units from code.

### The tool

The reference tool, described in [tool.md](https://unifold.md/tool) and tested by [tests/conformance.py](https://github.com/wackazong/unifold/blob/main/tests/conformance.py). It checks manifests, wiring, contracts, scenarios and documents, generates the diagrams and the `AGENTS.md` files, and prints the resolved model as JSON for tools that build on the map. A [GitHub Action](https://github.com/wackazong/unifold/blob/main/action.yml) and [pre-commit](https://pre-commit.com) hooks run it.

## Questions

**Do I need the tool?** Anyone can implement the standard, but its two promises, "checked" and "generated", need a checker. The reference tool is one Python file.

**Do I need an AI agent?** No. The files are YAML and Markdown. Still, unifold is complex to maintain as a human and is a standard optimized for using it with AI agents.

**Does it read my code?** No. It reads the `unifold.yaml` files and the Markdown documents, so your code may be in any language. Keeping the code and the map in step is part of every change and its review.

**Do I have to write documentation?** Every unit has a `README.md` that says what it is for and why. Everything else in `docs/` is written when there is something to say.

**Does it fit a project with one package?** Yes. A unit is a folder, not a package, so one package is one unit or several: its module folders, such as `src/billing/` and `src/platform/`, are units when their interfaces are worth naming. With one unit the map is one box, and the value is the root's `README.md` and `docs/` ([requirements](https://unifold.md/requirements)).

**What ends up in my repository?** The `unifold.yaml` files, the generated diagrams and the generated `AGENTS.md` of every unit. The standard is not copied; the root manifest names its version. With `--agents`, also the skills, the tool and the stubs.

**What about my `docs/` folder, docs site and ADR tool?** `docs/` is where unifold keeps the documents, sorted by kind, and a software artifact can be built from it. Existing decision records move to `docs/decisions/` ([documents](https://unifold.md/documents)).

## Needs

### uv

[uv](https://docs.astral.sh/uv/), for the tool, the tests and the site. `uv run` installs Python 3.9 or newer and the packages that the header of each script names: PyYAML, and Markdown for the site. The standard itself needs nothing.

## Commands

```sh
# test the tool
uv run tests/conformance.py
# check an example
uv run docs/skills/unifold/scripts/unifold.py check examples/plantwatch
# build the site and check its links
uv run site/build.py --check
```

## Read next

| Kind | Pages |
|---|---|
| The standard | [spec.md](https://unifold.md/spec), the standard on one page; [unifold.schema.json](https://unifold.md/0.3/unifold.schema.json) |
| Reference | [documents](https://unifold.md/documents), [writing](https://unifold.md/writing), [contracts](https://unifold.md/contracts), [agents](https://unifold.md/agents), [tool](https://unifold.md/tool), [tool JSON](https://unifold.md/tool-json), [rules](https://unifold.md/rules) |
| Explanation | [requirements](https://unifold.md/requirements), [reasoning](https://unifold.md/reasoning), [wiring](https://unifold.md/wiring), [invariants](https://unifold.md/invariants), [risks](https://unifold.md/risks), [decisions](https://github.com/wackazong/unifold/blob/main/docs/decisions/index.md) |
| Tutorial | [Your first map](https://unifold.md/first-map) |
| Examples | [slugline](https://github.com/wackazong/unifold/tree/main/examples/slugline), a tested Cargo workspace; [serial-line](https://github.com/wackazong/unifold/tree/main/examples/serial-line), a small design with contracts, scenarios and the three kinds; [plantwatch](https://github.com/wackazong/unifold/tree/main/examples/plantwatch), a design written before any code, with every document convention |

## Contributing and licence

Changes to the standard are proposed as decision records; see [CONTRIBUTING.md](https://github.com/wackazong/unifold/blob/main/CONTRIBUTING.md) and the [decisions](https://github.com/wackazong/unifold/blob/main/docs/decisions/index.md).

Licensed under either of the Apache License, Version 2.0 ([LICENSE-APACHE](https://github.com/wackazong/unifold/blob/main/LICENSE-APACHE)) or the MIT license ([LICENSE-MIT](https://github.com/wackazong/unifold/blob/main/LICENSE-MIT)), at your option. The templates of the skill and everything the tool generates may be used without attribution. Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this work by you shall be dual licensed as above, without any additional terms or conditions.
