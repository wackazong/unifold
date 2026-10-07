# AGENTS.md: unifold

This folder is a [unifold](https://unifold.md) unit, the root of the
project and the home of the standard. Use the
[read-docs](doc/skills/read-docs/SKILL.md) skill before anything else.

## Why

The standard is written with its own rules, so that every rule is tried on a
real text before a project has to follow it. It changes when a rule proves
wrong or missing in use.

The repository is a single unit. The chapters, the skills and the tool are
not separate parts with interfaces between them; they are one product that
changes together.

The normative text sits in `doc/references/unifold/` and the tool sits
inside the `check-docs` skill for one reason: these folders are copied into
every project that uses the standard. A project then carries the text, the
procedures and the tool without network access, and an agent finds them at
the same paths everywhere.

The examples are nested projects. Each has its own root manifest, is checked
on its own, and can be copied out as a starting point.

## Read next

1. [README.md](README.md): what this repository provides
2. [doc/references/unifold/index.md](doc/references/unifold/index.md): the standard, with the rules in brief
3. [doc/architecture.md](doc/architecture.md): where the ideas come from and what the limits are
4. [doc/decisions/index.md](doc/decisions/index.md): the design decisions
5. [examples/slugline](examples/slugline/README.md): a small example at level `core`
6. [examples/plantwatch](examples/plantwatch/README.md): a large example of the full standard
7. [CONTRIBUTING.md](CONTRIBUTING.md): how a change to the standard is made

## Skills

| Skill | Use it when |
|---|---|
| [read-docs](doc/skills/read-docs/SKILL.md) | You enter this or any other unifold project |
| [write-docs](doc/skills/write-docs/SKILL.md) | You create or change documents |
| [check-docs](doc/skills/check-docs/SKILL.md) | You have changed something, or review a change |

## Commands

```sh
python3 tests/conformance.py                                         # test the tool
python3 doc/skills/check-docs/scripts/unifold.py generate           # this project
python3 doc/skills/check-docs/scripts/unifold.py check --strict
python3 doc/skills/check-docs/scripts/unifold.py init examples/plantwatch   # refresh the example's copy
```

## Rules for work here

- `doc/references/unifold/` and the three skills are copied into other
  projects. Links inside them MUST stay within these four folders. They must
  not link to `doc/decisions/`, `doc/architecture.md` or `examples/`.
- A rule exists in three places that must agree: the chapter that states it,
  the rule table in `rules-tool.md` or `rules-review.md`, and, for tool
  rules, `unifold.py` with a case in `tests/conformance.py`.
- Every change to a rule is recorded as a decision with status `proposed`.
- A claim about a tool, a study or a product carries a link to its source.
- The standard is published at `https://unifold.md`. The schema of the
  manifest must be served at the path that manifests name in their modeline,
  `/0.1/manifest.schema.json`.
