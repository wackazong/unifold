# unifold

Draft 0.1. Published at <https://unifold.md>. Licensed under MIT or
Apache-2.0, at your option ([LICENSE-MIT](LICENSE-MIT),
[LICENSE-APACHE](LICENSE-APACHE)).

unifold is a convention for keeping the knowledge about a software project in
Markdown files that sit next to the code they describe. The files are written
mainly by AI agents and are read and corrected by humans. Both read the same
files. The name says it: documents for you and me.

## Goals

1. **Local knowledge.** What you need to know about a folder is in that folder.
2. **Information hiding.** A parent knows its children only through their
   interfaces. The top of the tree stays small.
3. **Comprehension portability.** Everything needed to *understand* a unit sits
   inside its folder. Copying the folder does not give you working software,
   but it gives you the full explanation.
4. **Design first.** The folder tree and its documents can exist before code.
5. **Declared once.** Structure is declared in one place, the manifest.
   Diagrams and indexes are generated from it.
6. **Checkable.** A tool checks the mechanical rules. An agent or a human
   checks the rest against a written ruleset.

## What it is not

- Not a build system and not a package manager.
- Not a proof that the code matches the documents. The checker compares the
  documents with each other.
- Not a replacement for API reference produced from code.
- Not tied to a language, a framework or a kind of system.

## The idea in one minute

Some folders are **units**. A unit has a manifest that says what it
**provides** and what it **needs**. It never says who uses it or who supplies
its needs:

```yaml
unit: storage
summary: Durable key-value storage with a write-ahead log
provides:
  kv-api: {kind: library, summary: Read and write keys in transactions}
needs:
  clock: {kind: library, summary: A monotonic time source}
```

The parent unit connects each need to a provider:

```yaml
wiring:
  storage.clock: platform.time-api
  api.store: storage.kv-api
```

A unit has two required files and an optional `doc/` folder:

```text
storage/
├── README.md         interface: what the unit provides and needs
├── AGENTS.md         why the unit is built this way, and pointers
└── doc/
    ├── context.md        what the unit inherits from the levels above
    ├── architecture.md   longer explanation of the design
    ├── decisions/        decision records (MADR)
    ├── references/       facts: contracts, formats, glossary
    ├── skills/           procedures for agents and humans
    └── diagrams/         generated from the manifests
```

## The rules in brief

Rules 1, 3, 4 and 6 are the core. They fit on one page, [core.md](core.md),
and can be adopted alone.

1. A unit is a folder with a manifest. Being a unit is optional
   ([concepts.md](concepts.md)).
2. A unit has a `README.md` that describes it as a closed box and an
   `AGENTS.md` that says why it is built as it is
   ([unit-files.md](unit-files.md)).
3. The manifest declares provided ports and needs. A need says what is
   needed, never who has it ([manifest.md](manifest.md)).
4. The parent wires every need of its children to a provider. Nothing reaches
   into a grandchild ([wiring.md](wiring.md)).
5. A unit refers to its direct children only through their `README.md`, to its
   ancestors only in `doc/context.md` with a restatement, and to nothing else
   in the project ([rules.md](rules.md)).
6. Structure is never written by hand. Diagrams and indexes are generated
   ([diagrams.md](diagrams.md)).
7. Reasons are recorded: the why in `AGENTS.md`, choices as decisions that an
   agent proposes and a human accepts ([doc-folder.md](doc-folder.md)).
8. Facts live in references and procedures in skills, each in the lowest unit
   that covers it. Every fact has one home.
9. Every promise of a port is written so that it can be checked, and an
   active unit says what checks it ([principles.md](principles.md)).
10. A Markdown file has at most 200 lines and is reachable by links
    ([markdown.md](markdown.md)).
11. The root unit names the version of the standard and carries a copy of it.

## Chapters

| Chapter | Content | Read it when |
|---|---|---|
| [core.md](core.md) | The ten rules of the core, on one page | First |
| [concepts.md](concepts.md) | Terms and the three principles | Second |
| [unit-files.md](unit-files.md) | `README.md` and `AGENTS.md` of a unit | You write or review a unit |
| [doc-folder.md](doc-folder.md) | Everything inside `doc/` | You add context, decisions, references or skills |
| [manifest.md](manifest.md) | The manifest fields | You declare or change an interface |
| [wiring.md](wiring.md) | How needs are connected to providers | You compose units |
| [diagrams.md](diagrams.md) | Generated diagrams and how to click through them | You read or regenerate diagrams |
| [markdown.md](markdown.md) | Writing rules: 200 lines, links, style | You write any file |
| [principles.md](principles.md) | How ports and adapters, DDD, SOLID and test-first design map to the rules | You decide where a boundary goes |
| [rules.md](rules.md) | The ruleset and the reference-direction rules | You check a project |
| [rules-tool.md](rules-tool.md) | Rules the checker enforces | The checker reports a rule ID |
| [rules-review.md](rules-review.md) | Rules an agent or human enforces | You review a change |
| [workflow.md](workflow.md) | Start, adopt step by step, change, copy | You start or change a project |
| [coexistence.md](coexistence.md) | Living with existing docs, sites, ADRs, owners files, registries | You adopt unifold in an existing repository |
| [checker.md](checker.md) | The reference checker and generator | You run the tool |

The machine-readable form of the manifest is
[manifest.schema.json](manifest.schema.json).

## Skills

Every unifold project carries three skills in its root unit:

| Skill | Purpose |
|---|---|
| [read-docs](../../skills/read-docs/SKILL.md) | Find your way through a unifold project |
| [write-docs](../../skills/write-docs/SKILL.md) | Create and change units, decisions, references and skills |
| [check-docs](../../skills/check-docs/SKILL.md) | Enforce the ruleset with the checker and by review |

## Conformance

The words MUST, MUST NOT, SHOULD and MAY are used as in BCP 14: MUST marks a
rule, SHOULD the normal case from which you deviate only with a reason you can
state, MAY an option. The rules with IDs in [rules-tool.md](rules-tool.md) and
[rules-review.md](rules-review.md) are the normative core. Examples are not
normative.

A project follows the standard at one of two levels, named in its root
manifest:

| Level | What applies | Copied into the repository |
|---|---|---|
| `core` | The ten rules of [core.md](core.md): manifests, wiring, generated diagrams | Nothing |
| `full` (default) | Everything in this standard | The chapters and the three skills |

At either level a project can make two claims:

| Claim | Meaning | Who can verify it |
|---|---|---|
| **checked** | The checker reports no error for the level | Anyone, by running the tool |
| **reviewed** | Checked, and the review rules were applied to every change | The project, by its own review process |

Warnings do not break conformance. They mark what a human should look at.

## Size of a project

The smallest project is one unit. At level `core` that is a `unit.yaml` and
a `README.md`. At level `full` it is a manifest, `README.md`, `AGENTS.md` and
the copy of the standard, about 30 files. Every further unit adds two or
three small files; everything else is written only when there is something
to say. Adoption can proceed one folder at a time
([workflow.md](workflow.md)).

How much to write is a judgement. A unit whose documents are longer than its
code deserves a second look. `unifold stats` counts files and words per
unit ([checker.md](checker.md)).

## The copy of the standard

Each project keeps a copy of this folder in `doc/references/unifold/` of its
root unit, together with the three skills, so that agents can read the
standard without network access. The root manifest names the version the copy
belongs to. Do not edit the copy; replace it as a whole.

## Licence

The text in this folder, the three skills and the tool are licensed under MIT
or Apache-2.0, at your option. The licence texts are in this folder. The
templates of the `write-docs` skill, the wording this standard asks you to
use, and everything the tool generates may be used, copied and changed
without attribution or notice. The documents of your project are yours.
