# youmedoc

Version 0.1 (draft). Canonical location: <https://youmedoc.example>.

youmedoc is a convention for keeping the knowledge about a software project in
Markdown files that sit next to the code they describe. The files are written
mainly by AI agents and are read and corrected by humans. Both read the same
files.

## Goals

1. **Local knowledge.** What you need to know about a folder is in that folder.
2. **Information hiding.** A parent knows its children only through their
   interfaces. The top of the tree stays small.
3. **Comprehension portability.** Everything needed to *understand* a unit sits
   inside its folder. Copying the folder does not give you working software,
   but it gives you the full explanation.
4. **Design first.** The folder tree and its documents can exist before any
   code is written.
5. **Declared once.** Structure is declared in one place, the manifest.
   Diagrams and indexes are generated from it.
6. **Checkable.** A tool checks the mechanical rules. An agent checks the rest
   against a written ruleset.

## What it is not

- Not a build system and not a package manager.
- Not a proof that the code matches the documents. The checker checks the
  documents against each other.
- Not a replacement for API reference documentation produced from code.
- Not tied to a language, a framework or a kind of system. It works for a
  library, an application, a set of microservices, or a product made of
  firmware, an emulator, a test rig and a mobile app.

## The idea in one minute

Some folders are **units**. A unit is a folder whose `README.md` starts with a
manifest:

```yaml
---
unit: storage
summary: Durable key-value storage with a write-ahead log
provides:
  kv-api:
    kind: library
    summary: Read and write keys in transactions
needs:
  clock:
    kind: library
    summary: A monotonic time source
---
```

The unit says what it **provides** and what it **needs**. It never says who
uses it or who supplies its needs. The parent unit connects needs to providers:

```yaml
wiring:
  storage.clock: platform.time-api
  api.store: storage.kv-api
```

Every unit has two required files and an optional `doc/` folder:

```text
storage/
├── README.md         interface: manifest + what the unit provides and needs
├── AGENTS.md         why the unit is built this way + pointers for agents
└── doc/
    ├── context.md        what the unit inherits from the levels above
    ├── architecture.md   longer explanation of the design
    ├── decisions/        decision records (MADR)
    ├── references/       facts: contracts, formats, glossary
    ├── skills/           procedures for agents and humans
    └── diagrams/         generated from the manifests
```

Units nest. A folder between two units that is not a unit itself is a plain
folder and is ignored.

## Chapters

| Chapter | Content | Read it when |
|---|---|---|
| [concepts.md](concepts.md) | Terms and the three principles | First |
| [unit-files.md](unit-files.md) | `README.md` and `AGENTS.md` of a unit | You write or review a unit |
| [doc-folder.md](doc-folder.md) | Everything inside `doc/` | You add context, decisions, references or skills |
| [manifest.md](manifest.md) | The manifest fields | You declare or change an interface |
| [wiring.md](wiring.md) | How needs are connected to providers | You compose units |
| [diagrams.md](diagrams.md) | The three generated diagrams | You read or regenerate diagrams |
| [markdown.md](markdown.md) | Writing rules: 200 lines, links, style | You write any file |
| [rules.md](rules.md) | The ruleset and the reference-direction rules | You check a project |
| [rules-tool.md](rules-tool.md) | Rules the checker enforces | The checker reports a rule ID |
| [rules-review.md](rules-review.md) | Rules an agent or human enforces | You review a change |
| [workflow.md](workflow.md) | Design first, change, adopt, copy | You start or change a project |
| [checker.md](checker.md) | The reference checker and generator | You run the tool |

The machine-readable form of the manifest is
[manifest.schema.json](manifest.schema.json).

## Skills

The standard ships three skills. Every youmedoc project carries them in its
root unit:

| Skill | Purpose |
|---|---|
| [read-docs](../../skills/read-docs/SKILL.md) | Find your way through a youmedoc project |
| [write-docs](../../skills/write-docs/SKILL.md) | Create and change units, decisions, references and skills |
| [check-docs](../../skills/check-docs/SKILL.md) | Enforce the ruleset with the checker and by review |

## Conformance

A project conforms to youmedoc 0.1 when:

1. its root manifest declares `youmedoc: "0.1"`,
2. the checker reports no errors ([rules-tool.md](rules-tool.md)), and
3. the review rules hold ([rules-review.md](rules-review.md)).

Warnings do not break conformance. They mark things a human should look at.

## Words used in this standard

- **MUST** and **MUST NOT** mark a rule. Breaking it breaks conformance.
- **SHOULD** marks the normal case. Deviate only with a reason you can state.
- **MAY** marks an option.

## Version and copies

Each project keeps a copy of this folder in `doc/references/youmedoc/` of its
root unit, so that agents can read the standard without network access. The
copy belongs to the version named in the root manifest. Do not edit the copy.
To move to a newer version, replace the folder and the three skills as a whole
and update the `youmedoc` key. See [workflow.md](workflow.md).
