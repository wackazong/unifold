# AGENTS.md: plantwatch

This folder is a [unifold](https://unifold.md) unit and the root of the
project. Use the [read-docs](doc/skills/read-docs/SKILL.md) skill before
anything else.

## Why

The system is cut along the lines where things are built, shipped and run
separately: firmware on the sensor stick, an app on the phone, services on a
server. Each of the three has its own toolchain, its own release rhythm and
its own failure modes, so each is a unit.

Three more units exist because of what lies between those three:

- The radio protocol and the reading format are shared by several parts and
  owned by none, so they are a unit of their own
  ([0002](doc/decisions/0002-define-the-profile-and-the-reading-format-once.md)).
- A simulated sensor stick makes tests fast. It is written independently of
  the firmware, so that it also tests the protocol definition
  ([0003](doc/decisions/0003-the-emulator-implements-the-profile-independently.md)).
- The promise "a dry plant leads to one notification" spans all parts. One
  unit owns the tests of that promise.

The decision that shapes everything else is that the sensor stick talks only
to a phone ([0001](doc/decisions/0001-the-phone-relays-between-sensor-and-server.md)).

## Read next

1. [README.md](README.md): what plantwatch provides and needs
2. [doc/architecture.md](doc/architecture.md): invariants, the path of a reading, where things run
3. [doc/diagrams/component.md](doc/diagrams/component.md): the six parts and their wiring
4. [doc/decisions/index.md](doc/decisions/index.md): decisions that hold for the whole project
5. [doc/references/glossary.md](doc/references/glossary.md): terms
6. [doc/references/conventions.md](doc/references/conventions.md): units of measure, identifiers, time, delivery
7. [doc/references/product-parameters.md](doc/references/product-parameters.md): the numbers version 1 is designed for

## Skills

| Skill | Use it when |
|---|---|
| [read-docs](doc/skills/read-docs/SKILL.md) | You enter this repository or a folder you do not know |
| [write-docs](doc/skills/write-docs/SKILL.md) | You create or change units, decisions, references or skills |
| [check-docs](doc/skills/check-docs/SKILL.md) | You have changed documents, or review a change |
| [add-a-measured-quantity](doc/skills/add-a-measured-quantity/SKILL.md) | The sensor stick shall measure something new, end to end |

## Commands

```sh
python3 doc/skills/check-docs/scripts/unifold.py show PATH        # a unit and its neighbours
python3 doc/skills/check-docs/scripts/unifold.py port PATH NAME   # both ends of a port
python3 doc/skills/check-docs/scripts/unifold.py generate         # diagrams and indexes
python3 doc/skills/check-docs/scripts/unifold.py check            # the tool rules
```

## Rules for work here

- The project is in its design phase. Do not write product code for a unit
  before a human has accepted the decisions that unit depends on.
- A change to the radio protocol or to the reading format follows
  "Changing a shared definition" in the
  [conventions](doc/references/conventions.md).
- Use the terms of the [glossary](doc/references/glossary.md) unchanged.
  In particular: a "reading" is one measurement set, never a single value.
- Do not edit `doc/references/unifold/` or the three skills of the
  standard. They are a copy of unifold 0.1.
