# AGENTS.md: <unit-name>

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show <path of this folder>`
prints this unit with its neighbours.
<!-- Root unit instead: "This folder is a unifold unit and the root of the project.
     Use the [read-docs](doc/skills/read-docs/SKILL.md) skill before anything else." -->

## Why

<Why this unit exists and what makes it change. Why it is cut this way: the forces,
the main trade-off, what must stay true. At most about 15 lines of prose.
No list of children, ports or wiring.>

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/architecture.md](doc/architecture.md): the design in detail
4. [doc/diagrams/component.md](doc/diagrams/component.md): the children and their wiring
5. [doc/decisions/index.md](doc/decisions/index.md): decisions
6. [doc/references/<topic>.md](doc/references/<topic>.md): <the main reference>
<!-- Keep only the lines whose target exists. -->

## Skills

| Skill | Use it when |
|---|---|
| [<skill-name>](doc/skills/<skill-name>/SKILL.md) | <situation> |

## Commands

<!-- Optional, at most ten lines: build, test, run. Longer procedures are skills. -->

## Rules for work here

- <A constraint or pitfall that holds in this unit and cannot be derived from code.>
