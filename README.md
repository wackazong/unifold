# unifold: architecture as code

> Your project structure is your architecture. Keep your documentation, architecture, and project structure aligned.

A folder with a `unifold.yaml` is a unit: it declares what it is responsible for, what it provides and what it needs, next to the code, and the unit above connects every need to a provider. A contract defines every connection, part by part, with examples and the fake that tests use; a scenario tells a story of the system as hops across the map. The unifold tool checks that all of this is consistent and draws the diagrams from the files, so nobody draws them by hand and they cannot disagree with the files. Every unit keeps its documents in the same places, so that a person or a coding agent can understand one folder without reading its neighbours.

## Why

One large architecture document, one root file for agents and a wiki beside the code go stale, and neither a newcomer nor a coding agent can take them in. Here the knowledge about a folder is in that folder. Structure is declared once and generated, because it is cheap to derive and expensive to keep correct by hand. Reasons are written, because they cannot be derived, and because nobody should make the same mistake twice.

The standard is explainable in one minute and adoptable in five. That is why the rules for manifests, wiring and generated files fit four short pages, why the rules for the documents of a unit are six chapters that are read when a document is written, and why everything else is reference, explanation or a tutorial.

## Install

The tool is on PyPI as [unifold](https://pypi.org/project/unifold/) and needs Python 3.9 or newer. `uvx unifold check` runs it without installing; `uv tool install unifold` or `pipx install unifold` installs the `unifold` command. `unifold init` starts a project, and `unifold init --agents` also installs the skills for coding agents ([tool](https://unifold.md/tool)).

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
unifold: "0.4"
name: shop
responsibility: Shop backend
wiring:
  billing.clock: platform.clock
```

`billing` says what it needs, never who supplies it; the root connects the need to `platform`. Both sides name one document, `docs/references/clock.md` of the root: the contract of the connection, which says what a clock gives and in which form. `unifold check` reads the three manifests and changes nothing; `unifold explore` draws them as a component diagram. `check` fails on a need without a provider, and on two sides that name different contracts. Without the wiring line in the root, it reports among its findings:

```text
error W2 unifold.yaml: need 'billing.clock' has no provider
    fix: Add `billing.clock: platform.clock` to the wiring.
```

`unifold show billing` prints the unit, its need and who finally provides it. The tutorial [Your first map](https://unifold.md/first-map) takes fifteen minutes.

## What a unit has

| File | What it is |
|---|---|
| `unifold.yaml` | The manifest: the unit's responsibility and kind, what it provides and needs, the wiring of its children and the scenarios it holds. Checked against the other manifests and the contracts. |
| `README.md` | The front page: what the unit is for, and why it is built this way. The contracts say what can be relied on. |
| `docs/` | Everything else written about the unit, in fixed places sorted by what the reader is doing: tutorials, skills, references, explanation, decisions. A file exists only when it has content. |
| `AGENTS.md` | Generated, at the root only: where the documents and skills are, for coding agents. |

## How people use it

A newcomer opens a folder and reads its `README.md`. `docs/tutorials/` teaches, `docs/skills/` says how to do a task, `docs/references/` holds the facts, `docs/explanation/` the reasoning, the invariants, the runtime, the deployment and the risks, and `docs/decisions/` the choices. Anyone who wants the whole picture runs `unifold explore`, which opens the map in the browser with every document beside it. A reviewer runs `unifold check` and works through the [review checklist](https://unifold.md/writing#review-checklist).

## How agents use it

`unifold init --agents` installs the two skills, writes their stubs into `.agents/skills/` and `.claude/skills/`, and adds the unifold block to the root `AGENTS.md`. The root `AGENTS.md` is generated: a pointer to `README.md`, the documents by kind, the skills, and the index of units. Most agents read `AGENTS.md` and find the stubs ([agents](https://unifold.md/agents)). Every agent with a shell can run `unifold show`, which prints a folder's capabilities, needs and resolved neighbours, as text or JSON.

## What this repository provides

### The standard

Four pages on manifests, wiring, scenarios and conformance, starting at [spec.md](https://unifold.md/spec), six chapters on the documents of a unit, starting at [documents.md](https://unifold.md/documents), and a [JSON Schema](https://unifold.md/0.4/unifold.schema.json) for the manifest. Published at [unifold.md](https://unifold.md).

### The skills

Two skills in the [Agent Skills](https://agentskills.io/specification) format. [unifold](https://unifold.md/skill/SKILL.md), with file templates, teaches an agent to find its unit, read the right files, change manifests and documents, and check the result. [unifold-convert](https://unifold.md/skill/unifold-convert/SKILL.md) brings an existing repository into the map: the agent chooses the units, writes their manifests, and compares them with the code. No script derives units from code.

### The tool

The reference tool, described in [tool.md](https://unifold.md/tool) and tested by [tests/conformance.py](https://github.com/wackazong/unifold/blob/main/tests/conformance.py). It checks manifests, wiring, contracts, scenarios and documents, generates the root `AGENTS.md` and the decision indexes, prints what to implement in a unit (`brief`) and which examples of its contracts the tests name (`trace`), and prints the resolved model as JSON for tools that build on the map. `unifold explore` opens the explorer: the whole map as one page in the browser, every box clickable, every README, contract and decision beside it; the [examples](https://unifold.md/examples/plantwatch/) show one. A [GitHub Action](https://github.com/wackazong/unifold/blob/main/action.yml) and [pre-commit](https://pre-commit.com) hooks run it.

## Questions

**Do I need the tool?** Anyone can implement the standard, but its two promises, "checked" and "generated", need a checker. The reference tool is one Python file.

**Do I need an AI agent?** No. The files are YAML and Markdown. Still, a unifold map is a lot to keep current by hand, and the standard is made for work with AI agents.

**Does it read my code?** No. It reads the `unifold.yaml` files and the Markdown documents, so your code may be in any language. Keeping the code and the map in step is part of every change and its review.

**Do I have to write documentation?** Every unit has a `README.md` that says what it is for and why. Everything else in `docs/` is written when there is something to say.

**Does it fit a project with one package?** Yes. A unit is a folder, not a package, so one package is one unit or several: its module folders, such as `src/billing/` and `src/platform/`, are units when their interfaces are worth naming ([requirements](https://unifold.md/requirements#for-which-repositories)).

**What ends up in my repository?** The `unifold.yaml` files, the generated root `AGENTS.md` and the generated indexes of the decisions. The standard is not copied; the root manifest names its version. With `--agents`, also the skills, the tool and the stubs.

**What about my `docs/` folder, docs site and ADR tool?** `docs/` is where unifold keeps the documents, sorted by kind, and a software artifact can be built from it. Existing decision records move to `docs/decisions/` ([documents](https://unifold.md/documents)).

## Read next

| Kind | Pages |
|---|---|
| The standard | [spec.md](https://unifold.md/spec), [spec-wiring.md](https://unifold.md/spec-wiring), [spec-scenarios.md](https://unifold.md/spec-scenarios) and [spec-conformance.md](https://unifold.md/spec-conformance) for manifests, wiring, scenarios and generated files; [documents](https://unifold.md/documents), [where things go](https://unifold.md/placement), [writing](https://unifold.md/writing), [decisions](https://unifold.md/decision-records), [contracts](https://unifold.md/contracts) and [their parts](https://unifold.md/contract-parts) for the documents of a unit; [unifold.schema.json](https://unifold.md/0.4/unifold.schema.json) |
| Reference | [agents](https://unifold.md/agents), [tool](https://unifold.md/tool), [setting up the tool](https://unifold.md/tool-setup), [generated files and the explorer](https://unifold.md/tool-output), [tool JSON](https://unifold.md/tool-json), [rules](https://unifold.md/rules) |
| Explanation | [requirements](https://unifold.md/requirements), [reasoning](https://unifold.md/reasoning), [design ideas](https://unifold.md/principles), [wiring](https://unifold.md/wiring), [scenarios](https://unifold.md/scenarios), [invariants](https://unifold.md/invariants), [risks](https://unifold.md/risks), [decisions](https://github.com/wackazong/unifold/blob/main/docs/decisions/index.md) |
| Tutorial | [Your first map](https://unifold.md/first-map) |
| Examples | [slugline](https://github.com/wackazong/unifold/tree/main/examples/slugline), a tested Cargo workspace; [serial-line](https://github.com/wackazong/unifold/tree/main/examples/serial-line), a small design with contracts, scenarios and the three kinds; [plantwatch](https://github.com/wackazong/unifold/tree/main/examples/plantwatch), a design written before any code, with every document convention |

## Contributing and licence

Changes to the standard are proposed as decision records; see [CONTRIBUTING.md](https://github.com/wackazong/unifold/blob/main/CONTRIBUTING.md) and the [decisions](https://github.com/wackazong/unifold/blob/main/docs/decisions/index.md).

Licensed under either of the Apache License, Version 2.0 ([LICENSE-APACHE](https://github.com/wackazong/unifold/blob/main/LICENSE-APACHE)) or the MIT license ([LICENSE-MIT](https://github.com/wackazong/unifold/blob/main/LICENSE-MIT)), at your option. The templates of the skill and everything the tool generates may be used without attribution. Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this work by you shall be dual licensed as above, without any additional terms or conditions.
