# youmedoc

Say "you, me, doc": documents for the people who read them and the agents who
write them.

**A README per folder, plus a map that cannot go stale.** Each part of a
repository says in a few lines of YAML what it provides and what it needs.
Its parent connects every need to a provider. A script checks that nothing is
left unconnected and draws the architecture diagrams from those lines.

```yaml
# storage/unit.yaml
unit: storage
summary: Durable key-value storage with a write-ahead log
provides:
  kv-api: {summary: Read and write keys in transactions}
needs:
  clock: {summary: A monotonic time source}
```

```yaml
# unit.yaml of the parent
wiring:
  api.store: storage.kv-api
  storage.clock: platform.time-api
```

**Why.** One large architecture document or one root instruction file for
agents goes stale, and neither a new contributor nor a coding agent can take
it in. Here the knowledge about a folder is in that folder, a folder can be
understood without reading its neighbours, and the picture of how the parts
connect is generated, so it cannot disagree with what is declared.

**What it costs.** Two small files per folder you choose to describe. Start
with one folder. Most folders never need it.

**Try it.** From a copy of this repository:

```sh
python3 doc/skills/check-docs/scripts/youmedoc.py init --level core /path/to/your/repo
python3 doc/skills/check-docs/scripts/youmedoc.py check /path/to/your/repo
```

The tool needs Python 3.9 or newer with PyYAML; `uv run` instead of `python3`
fetches PyYAML by itself.

- **The rules on one page:** [core.md](doc/references/youmedoc/core.md).
- **The full standard:** [index.md](doc/references/youmedoc/index.md). It adds
  an `AGENTS.md` per unit, decisions, references, skills and a ruleset.
- **A small example:** [examples/slugline](examples/slugline/README.md), a
  library with three units at level `core`.
- **A large example:** [examples/plantwatch](examples/plantwatch/README.md),
  a sensor device, its emulator, a test rig, a mobile app and cloud services,
  designed in documents before any code.
- **This repository follows the standard itself.**

Status: draft 0.1. The rules may still change.

## Questions

**Do I need the tool?** No. The ten rules of the core can be followed with a
text editor. The tool finds mistakes and draws the diagrams.

**Do I need an AI agent?** No. The files are plain Markdown and YAML.
Agents benefit because each folder tells them what they need and nothing
else.

**Does it fit a library with one package?** Hardly. A project of one unit
gets a one-box diagram. youmedoc pays off when there are several parts with
interfaces between them.

**What about my docs site and my `docs/` folder?** They stay. youmedoc uses a
folder named `doc/` for the people and agents who work on the code
([coexistence.md](doc/references/youmedoc/coexistence.md)).

**Does it check my code?** Only if you give it the dependencies your build
system knows: `check --deps` compares them with the wiring
([checker.md](doc/references/youmedoc/checker.md)).

## Use the full standard in your repository

```sh
python3 doc/skills/check-docs/scripts/youmedoc.py init /path/to/your/repo
```

This copies the chapters and the three skills into the repository, writes
`unit.yaml`, `README.md` and `AGENTS.md` where they are missing, and
generates the first diagram. Then follow
[workflow.md](doc/references/youmedoc/workflow.md). Adoption can proceed one
folder at a time.

## Provides

### `specification`

The standard: an overview, the core on one page, fourteen further chapters
and a JSON Schema, in
[doc/references/youmedoc/](doc/references/youmedoc/index.md). It defines the
files of a unit, the manifest, the wiring, the generated diagrams, the
writing rules and the ruleset, and says which design principles the rules
come from.

### `skills`

Three skills in the [Agent Skills](https://agentskills.io/specification)
format, with file templates:

| Skill | Purpose |
|---|---|
| [read-docs](doc/skills/read-docs/SKILL.md) | Find your way through a youmedoc project |
| [write-docs](doc/skills/write-docs/SKILL.md) | Create and change units, decisions, references and skills |
| [check-docs](doc/skills/check-docs/SKILL.md) | Enforce the ruleset with the checker and by review |

### `checker`

One Python file,
[youmedoc.py](doc/skills/check-docs/scripts/youmedoc.py). It checks the
mechanical rules, generates diagrams and indexes, describes a unit with its
resolved neighbours, and writes a clickable HTML explorer of a project. It is
described in [checker.md](doc/references/youmedoc/checker.md) and tested by
[tests/conformance.py](tests/conformance.py). It compares documents with each
other. It does not read code.

## Needs

### `python`

Only the checker needs it. The standard can be followed without the tool;
the [check-docs](doc/skills/check-docs/SKILL.md) skill says how.

## Out of scope

- No build, packaging or deployment.
- No check that code matches the documents.
- No rules for Markdown files outside units and their `doc/` folders.

## Contributing

Changes to the standard are proposed as decision records. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Licensed under either of the Apache License, Version 2.0
([LICENSE-APACHE](LICENSE-APACHE)) or the MIT license
([LICENSE-MIT](LICENSE-MIT)), at your option. This covers the text of the
standard, the skills, the tool and the example.

The templates in `doc/skills/write-docs/assets/`, and everything the
generator writes into a project, may be used, copied and changed without
attribution. The documents of your project are yours.

Unless you explicitly state otherwise, any contribution intentionally
submitted for inclusion in this work by you shall be dual licensed as above,
without any additional terms or conditions.

## More

- [AGENTS.md](AGENTS.md): why the standard is built this way
- [Context diagram](doc/diagrams/context.md): this repository as a unit
- [doc/architecture.md](doc/architecture.md): where the ideas come from, and the known limits
- [Decisions](doc/decisions/index.md)
