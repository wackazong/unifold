# AGENTS.md: ingest

This folder is a [youmedoc](https://youmedoc.example) unit.

## Why

The moment a client uploads is the only chance to take its readings. This
unit exists to make that moment as hard to fail as possible: it does the
least that makes a reading safe, which is to check it, to store it durably
as an event, and to say so.

Everything else is left out on purpose. `ingest` has no database, calls
no other service and does not know what a plant is. Its only dependency is
the event bus, which it needs anyway to publish. Even the memory of which
readings it has accepted lives there
([0001](doc/decisions/0001-accepted-ranges-are-kept-on-the-event-bus.md)).

`ingest` is also the border for the format of readings. It is the only
place that reads an uploaded reading. Its events carry the values under
names of their own, so that a new version of the upload format changes
this unit and nothing behind it.

The trade-off: recognition of duplicates is exact in normal operation and
only best effort after a failure or under concurrent uploads of the same
sensor stick. That is acceptable because every subscriber must tolerate
repeated events anyway ([context](doc/context.md)).

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its
   surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/ingest-api.md](doc/references/ingest-api.md): the
   upload operation and the checks
6. [doc/references/reading-events.md](doc/references/reading-events.md):
   topic and content of the events
7. [doc/references/accepted-ranges.md](doc/references/accepted-ranges.md):
   the state with which duplicates are recognised

## Skills

| Skill | Use it when |
|---|---|
| [ingest-add-a-quantity](doc/skills/ingest-add-a-quantity/SKILL.md) | Readings carry a measured quantity that `ingest` does not check and publish yet |

## Rules for work here

- Do not add a dependency. A database, a cache or a call to another
  service on the upload path defeats the purpose of this unit.
- Answer only after the event bus has acknowledged every event of the
  batch and the new state. An answer before that can lose readings.
- Publish first, record the accepted range second. The other order turns
  a failure into a lost reading instead of a repeated event.
- Never change a reading. The `reading` field of an event is what was
  uploaded, including fields that `ingest` does not know.
- A rejection is final for the client: it will not send the reading
  again. Reject only what can never become valid. Answer `503` for
  everything that might work later.
