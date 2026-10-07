# AGENTS.md: protocol

This folder is a [youmedoc](https://youmedoc.example) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `youmedoc`. From
there, `python3 doc/skills/check-docs/scripts/youmedoc.py show protocol`
prints this unit with its neighbours.

## Why

The radio link and the reading are each implemented more than once, by
parts that are built and released separately; this unit exists so that
their definition belongs to none of them. It changes when what a sensor
stick and a central exchange changes, or what a reading contains, and
never because an implementation changed.

Both definitions are in one unit because the record on the radio link is
an encoding of the reading. Defined apart, the two would drift.

Two forces shape the text. It must be exact enough that two implementers
who never talk build parts that work together, so it uses byte tables,
numbered procedures and worked examples. And it must be changeable without
replacing all parts at once, so each contract has a version and rules for
what a minor version may do.

The trade-off: prose and tables are easy to review, but no tool checks
code against them. What must stay true: the text never depends on an
implementation, and behaviour that is not in the text is undefined.

## Read next

1. [README.md](README.md): what the two definitions guarantee
2. [doc/context.md](doc/context.md): the project decisions the definitions carry out
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): why the record and the confirm look as they do
5. [doc/references/glossary.md](doc/references/glossary.md): the terms of both contracts
6. [doc/references/ble-profile/index.md](doc/references/ble-profile/index.md): the BLE profile
7. [doc/references/reading-schema.md](doc/references/reading-schema.md): the reading schema

## Skills

| Skill | Use it when |
|---|---|
| [protocol-change-a-definition](doc/skills/protocol-change-a-definition/SKILL.md) | A field, a characteristic, an op code or a rule of the profile or the schema shall change |

## Rules for work here

- Every change to a contract changes its version number in the same change.
- When two implementations disagree, the question is what the text says.
  If the text allows both, the text is at fault. Correct the text first.
- Name roles, not implementations. The roles are "sensor stick" and
  "central". Do not name a platform, a library or a product part.
- Use the terms of the [glossary](doc/references/glossary.md) unchanged.
  In particular, the BLE step is "bonding", never "pairing".
- Layouts are tables with offset and size. The byte examples in
  [README.md](README.md), in the
  [reading schema](doc/references/reading-schema.md) and in the
  [procedures](doc/references/ble-profile/procedures.md) are computed from
  the tables. Recompute them when a layout changes.
- The UUID base and the company identifier are placeholders. They must be
  replaced before a product ships with them.
