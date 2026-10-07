# AGENTS.md: protocol

This folder is a [youmedoc](https://youmedoc.example) unit.

## Why

The radio link and the reading are each implemented more than once, by
parts that are built and released separately. A definition that lived with
one implementer would follow that implementer's code. So the definition
has a folder of its own, contains no code, and its text is the only
authority.

Both definitions are in one unit because the record on the radio link is
an encoding of the reading. Defined apart, the two would drift, which is
what the unit exists to prevent.

Two forces shape the text. It must be exact enough that two implementers
who never talk build parts that work together, so it uses byte tables and
numbered procedures. And it must be changeable without replacing all parts
at once, so every contract has a version and rules for what a minor version
may do.

The trade-off: prose and tables are easy to review, but no tool checks
code against them. What must stay true: the text never depends on an
implementation, and behaviour that is not in the text is undefined.

## Read next

1. [README.md](README.md): what the two definitions guarantee
2. [doc/context.md](doc/context.md): the project decisions the definitions carry out
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): why the record and the confirm look as they do
5. [doc/references/ble-profile/index.md](doc/references/ble-profile/index.md): the BLE profile
6. [doc/references/reading-schema.md](doc/references/reading-schema.md): the reading schema

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
- Layouts are tables with offset and size. The byte examples in
  [README.md](README.md), in the
  [reading schema](doc/references/reading-schema.md) and in the
  [procedures](doc/references/ble-profile/procedures.md) are computed from
  the tables. Recompute them when a layout changes.
- BLE calls it "pairing"; the glossary cited in
  [doc/context.md](doc/context.md) uses that word for something wider.
  Write "bonding" for the BLE step.
- The UUID base and the company identifier are placeholders. They must be
  replaced before a product ships with them.
