# AGENTS.md: youmedoc

This folder is a [youmedoc](https://youmedoc.example) unit and the home of
the standard. Use the [read-docs](doc/skills/read-docs/SKILL.md) skill before
anything else.

## Why

The standard is written with its own rules, so that every rule is tried on a
real text before a project has to follow it.

The repository is a single unit. The chapters, the skills and the tool are
not separate parts with interfaces between them; they are one product that
changes together.

The normative text sits in `doc/references/youmedoc/` and the tool sits
inside the `check-docs` skill for one reason: these folders are copied into
every project that uses the standard. A project then carries the text, the
procedures and the tool without network access, and an agent finds them at
the same paths everywhere.

The example is a nested project. It has its own root manifest, is checked on
its own, and can be copied out as a starting point.

The reasoning in full is in [doc/architecture.md](doc/architecture.md).

## Read next

1. [README.md](README.md): what this repository provides
2. [doc/references/youmedoc/index.md](doc/references/youmedoc/index.md): the standard
3. [doc/architecture.md](doc/architecture.md): where the ideas come from and what the limits are
4. [doc/decisions/index.md](doc/decisions/index.md): the design decisions
5. [examples/plantwatch](examples/plantwatch/README.md): a worked example

## Skills

| Skill | Use it when |
|---|---|
| [read-docs](doc/skills/read-docs/SKILL.md) | You enter this or any other youmedoc project |
| [write-docs](doc/skills/write-docs/SKILL.md) | You create or change documents |
| [check-docs](doc/skills/check-docs/SKILL.md) | You have changed something, or review a change |

## Rules for work here

- `doc/references/youmedoc/` and the three skills are copied into other
  projects. Links inside them MUST stay within these four folders. They must
  not link to `doc/decisions/`, `doc/architecture.md` or `examples/`.
- A rule exists in three places that must agree: the chapter that states it,
  the rule table in `rules-tool.md` or `rules-review.md`, and, for tool
  rules, `youmedoc.py`. Change them together.
- Every change to a rule is recorded as a decision with status `proposed`.
- After a change, run the checker on this project and on the example, and
  refresh the example's copy of the standard with `youmedoc.py init`.
- The address `https://youmedoc.example` is a placeholder for the place where
  the standard is published. Replace it everywhere at once.
