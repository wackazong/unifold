# Unifold: every doc at the right place

**Keep architecture and documentation close to the code.**

Define the architecture with your folder structure. Declare interfaces,
contracts, dependencies and capabilities next to the code. Give people and
agents the documentation they need, where they need it.

Folders become units. A unit declares what it provides and what it needs,
never who supplies it; the unit above connects every need to a provider. A
checker fails when a need is unconnected, when a connection names something
that does not exist, or when the code uses something that is not wired. The
architecture diagrams are generated, so nobody draws them and they cannot
disagree with the files. Draft 0.1, published at <https://unifold.md>.

## Why

One large architecture document, one root file for agents, and a wiki
beside the code go stale, and neither a newcomer nor a coding agent can
take them in. Here the knowledge about a folder is in that folder, in the
same places everywhere, and a folder can be understood without reading its
neighbours. Structure is declared once and generated, because it is cheap
to derive and expensive to keep correct by hand; reasons are written,
because they cannot be derived.

The standard must be explainable in one minute and adoptable in five. That
is why the normative text is one page, why level `core` asks for nothing
but manifests, and why a skill and not a script converts a repository.
Everything else is explanation, reference or a tutorial, and must not grow
back into the standard. The standard follows its own rules, so that every
rule is tried on a real text before a project has to follow it; this
repository is a project of one unit at level `full`.

## How it works

```yaml
# billing/unifold.yaml
summary: Creates invoices
needs:
  clock: A time source
```

```yaml
# platform/unifold.yaml
summary: Shared runtime services
capabilities:
  clock: The current time
```

```yaml
# unifold.yaml in the repository root
unifold: "0.1"
summary: Shop backend
wiring:
  billing.clock: platform.clock
```

`unifold check` reads the three files and the build files, reports a need
without a provider or a dependency without a connection, and writes the
component diagram. `unifold show billing` prints the unit, its need and who
finally provides it. The tutorial [Your first map](docs/tutorials/first-map.md)
takes fifteen minutes.

## Two levels

| Level | A unit has | Use it for |
|---|---|---|
| `core` (default) | `unifold.yaml` | The checked map. No prose is required or checked. |
| `full` | also `README.md` and a `docs/` folder; `AGENTS.md` is generated | All documentation of the unit in fixed places, sorted by what the reader is doing: tutorials, skills, references, explanation, decisions. For one unit or for a whole tree. |

## How people use it

A newcomer opens a folder and finds its `README.md`: what the unit is for,
why it is built this way, what can be relied on. `docs/tutorials/` teaches,
`docs/skills/` says how to do a task, `docs/references/` holds the facts,
`docs/explanation/` the reasoning, the invariants, the runtime, the
deployment and the risks, one file each, and `docs/decisions/` the choices.
A reviewer runs `unifold check` and the checklist in
[writing.md](docs/references/unifold/writing.md).

## How agents use it

`unifold init --agents` installs the two skills, writes their stubs into
`.agents/skills` and `.claude/skills`, and adds the unifold block to the
root `AGENTS.md`. At level `full` every unit's `AGENTS.md` is generated: a
pointer to `README.md`, the documents by kind, the skills. `AGENTS.md` is
read by most agents and the stubs are found by most; Kiro and Aider do not
look there ([agents.md](docs/references/unifold/agents.md)). Every agent
with a shell can run `unifold show`, which prints a folder's capabilities,
needs and resolved neighbours, as text or JSON.

## Compared with

| | What it is | What unifold adds | What unifold does not replace |
|---|---|---|---|
| [AGENTS.md](https://agents.md/) | Free-text instructions for agents | A declared, checked structure; the file is generated from it | The convention: agents still read `AGENTS.md` first |
| [C4](https://c4model.com/), [Structurizr](https://github.com/structurizr/structurizr), [LikeC4](https://github.com/likec4/likec4) | One central architecture model with generated diagrams | A manifest in each folder, needs that do not name their provider, a completeness check, the comparison with build files; deployment and runtime views as files of the unit they belong to | A model that cuts across the folder tree |
| [arc42](https://github.com/arc42/arc42-template) | A template for architecture documentation | The building-block view as checked data; the other sections as one file per concern in every unit | The questions arc42 asks |
| [Diátaxis](https://diataxis.fr) | Four kinds of documentation | A fixed folder per kind in every unit, and a tool that knows them | The way of writing each kind |
| [Backstage catalog](https://github.com/backstage/backstage) | YAML beside code for a portal across repositories | Wiring by the parent; works without a portal | A catalogue across repositories; keep both |
| ADRs ([MADR](https://adr.github.io/madr/)) | Decision records | At level `full`: a place per unit; agents propose, people accept | The format: unifold uses MADR |

## Questions

**Do I need the tool?** The standard can be implemented by anyone, but the
two promises, "checked" and "generated", need a checker. The reference
tool is one Python file.

**Do I need an AI agent?** No. The files are YAML and Markdown.

**Does it read my code?** It reads build files and imports to find which
unit depends on which, and compares that with the wiring. It works per
pair of units. It does not judge whether a description is true.

**Do I have to write documentation?** No. At level `core` nothing reads or
constrains your READMEs.

**Does it fit a project with one package?** Yes: a project of one unit. The
map is one box; the documentation of the root is the point
([requirements](docs/explanation/requirements.md)).

**What ends up in my repository?** The `unifold.yaml` files, the generated
diagrams and, at level `full`, the generated `AGENTS.md`. The standard is
not copied; the root manifest names its version. With `--agents`, also the
skills and their stubs.

**What about my `docs/` folder, docs site and ADR tool?** `docs/` is where
unifold keeps the documents, sorted by kind; a site is built from it.
Existing decision records move to `docs/decisions/`
([documents.md](docs/references/unifold/documents.md)).

**Is it stable?** No. This is draft 0.1, unpublished. It has been tried on
a handful of repositories and not measured in use
([risks](docs/explanation/risks.md)).

## Documentation

| Kind | Pages |
|---|---|
| The standard | [spec.md](docs/references/unifold/spec.md), the whole of level `core` on one page; [unifold.schema.json](docs/references/unifold/unifold.schema.json) |
| Reference | [documents](docs/references/unifold/documents.md), [writing](docs/references/unifold/writing.md), [agents](docs/references/unifold/agents.md), [tool](docs/references/unifold/tool.md), [tool JSON](docs/references/unifold/tool-json.md), [rules](docs/references/unifold/rules.md) |
| Explanation | [requirements](docs/explanation/requirements.md), [reasoning](docs/explanation/reasoning.md), [wiring](docs/explanation/wiring.md), [invariants](docs/explanation/invariants.md), [risks](docs/explanation/risks.md), [decisions](docs/decisions/index.md) |
| Tutorial | [Your first map](docs/tutorials/first-map.md) |
| Examples | [examples/slugline](examples/slugline/README.md), a tested Cargo workspace; [examples/plantwatch](examples/plantwatch/README.md), a design written before any code, at level `full` |

## Capabilities

### `specification`

The standard on one page, [spec.md](docs/references/unifold/spec.md), with
the reference chapters beside it and a JSON Schema for the manifest.
Published at <https://unifold.md>.

### `skill`

Two skills in the [Agent Skills](https://agentskills.io/specification)
format. [unifold-convert](docs/skills/unifold-convert/SKILL.md) brings an
existing repository into the format: it has the agent find the units,
write their manifests and check them against the code. No script derives
units from code. [unifold](docs/skills/unifold/SKILL.md), with file
templates, teaches an agent to find its unit, read the right files, change
manifests and documents, and check the result.

### `tool`

The reference tool, described in [tool.md](docs/references/unifold/tool.md)
and tested by [tests/conformance.py](tests/conformance.py). It checks
manifests, compares the wiring with dependencies in code, and generates the
diagrams and the `AGENTS.md` files.

## Needs

### `python`

Python 3.9 or newer with PyYAML, for the tool. The standard needs nothing.

## Commands

```sh
python3 tests/conformance.py                                  # test the tool
python3 docs/skills/unifold/scripts/unifold.py check --fix     # generated files (never stamps)
python3 docs/skills/unifold/scripts/unifold.py check           # this project
python3 site/build.py                                         # the site, into site/_out
```

## Contributing and licence

Changes to the standard are proposed as decision records; see
[CONTRIBUTING.md](CONTRIBUTING.md) and the
[decisions](docs/decisions/index.md).

Licensed under either of the Apache License, Version 2.0
([LICENSE-APACHE](LICENSE-APACHE)) or the MIT license
([LICENSE-MIT](LICENSE-MIT)), at your option. The templates of the skill
and everything the tool generates may be used without attribution. Unless
you explicitly state otherwise, any contribution intentionally submitted
for inclusion in this work by you shall be dual licensed as above, without
any additional terms or conditions.
