# AGENTS.md: plants

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show cloud/services/plants`
prints this unit with its neighbours.

## Why

Somebody has to own the answer to "which plant is this, and whose". This
unit does, and it changes when what is known about a plant changes: its
fields, its thresholds, its history. Names, attached sensor sticks and
thresholds are entered rarely and read often, and they must be correct at
once, so they live in one place with one schema and are served by calls.

History is kept in the same service because the registry decides where a
reading belongs: the attachment of a sensor stick to a plant is the join
between the two. A separate history service would need that attachment
for every single reading
([0002](doc/decisions/0002-a-reading-joins-the-plant-at-the-time-it-is-handled.md)).

History is a projection of the reading events, not a second truth. It is
built so that handling an event twice changes nothing and that the order
of events does not matter. Raw readings are kept only as long as a client
can still ask for them; beyond that, hourly aggregates carry the two
years
([0001](doc/decisions/0001-raw-readings-for-90-days-hourly-aggregates-for-2-years.md)).

The trade-off: queries and event handling share one service and one
database. A heavy history query can slow down the intake of events. That
is accepted for version 1.

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its
   surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/plants-api.md](doc/references/plants-api.md): the
   operations and their guarantees
6. [doc/references/reading-events.md](doc/references/reading-events.md):
   what the unit requires of the stream of readings
7. [doc/references/data-model.md](doc/references/data-model.md): what is
   stored and for how long

## Skills

| Skill | Use it when |
|---|---|
| [plants-add-a-quantity](doc/skills/plants-add-a-quantity/SKILL.md) | Readings carry a measured quantity that shall get thresholds and a history |

## Rules for work here

- Handle an event in one database transaction: the reading, the aggregate
  of its hour and the latest reading of the plant change together or not
  at all. Confirm the event after the commit.
- Never add to an aggregate. Always recompute the hour from its raw
  readings. Adding counts a repeated event twice.
- Do not cache plants or thresholds. Whoever looks up a sensor stick
  relies on the current state.
- Every query carries the owner id in its condition. There is no code
  path that reads a plant by id alone, except the lookup by sensor id.
- The field `reading` of an event is stored and returned untouched. Code
  in this unit reads `values`, never `reading`.
- A schema change is a migration that works while the previous version of
  the service still runs.
