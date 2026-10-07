# AGENTS.md: sync

This folder is a [youmedoc](https://youmedoc.example) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `youmedoc`. From
there, `python3 doc/skills/check-docs/scripts/youmedoc.py show mobile/sync`
prints this unit with its neighbours.

## Why

A phone is offline in cellars and stairwells and comes online at moments
nobody controls. This library exists so that neither fact reaches a reader
of the data. It owns the one store on the phone, and it alone speaks to the
server. A reader asks the store; the exchange with the server runs behind
the store, on its own schedule.

The unit changes when the phone shall keep something new or keep it
differently, or when `cloud-api` changes. A change of wording or of the
radio does not reach it.

Readings and plant settings flow in opposite directions and are kept apart
on purpose. Readings are immutable and only ever travel towards the server,
so repeating a transfer is always safe. Plant settings can change at both
ends, so they need a rule for collisions
([0002](doc/decisions/0002-the-change-that-reaches-the-server-last-wins.md)).

The main trade-off: the phone holds a copy that can be days behind the
server. sync does not hide this; it reports the age of what it holds.

What must stay true: sync acknowledges a batch only after it is stored
durably, and a reading in the store never changes.

## Read next

1. [README.md](README.md): what sync provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): sync among its
   neighbours
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/local-store.md](doc/references/local-store.md): what is
   kept and in which states
6. [doc/references/exchange.md](doc/references/exchange.md): the exchange
   with the server
7. [doc/references/plant-data.md](doc/references/plant-data.md): the
   contract of the provided port
8. [doc/references/glossary.md](doc/references/glossary.md): query and
   command, upload state, waiting change, pause

## Skills

| Skill | Use it when |
|---|---|
| [sync-change-the-local-store](doc/skills/sync-change-the-local-store/SKILL.md) | The store shall keep something new or keep something differently |

## Rules for work here

- Acknowledge a batch after the write to the store has reached durable
  storage, not after it has been queued.
- A change to the layout of the store ships with a migration from every
  released layout. A phone may skip versions; a migration that loses
  readings the server has not confirmed is a defect, not a trade-off.
- Never compute an alert or a "needs water" state here, not even as a
  preview. The reason is cited in [doc/context.md](doc/context.md).
- No query may touch the network, and no query may wait for a running
  exchange.
- Field names in requests and stored documents come from `reading-format`
  and from `cloud-api`. Do not restate them in the documents of this unit.
- The pauses and sizes in [exchange.md](doc/references/exchange.md) protect
  the phone's battery and the server. Change them there first, with a
  reason, and then in code.
