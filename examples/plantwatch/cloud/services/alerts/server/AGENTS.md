# AGENTS.md: server

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show cloud/services/alerts/server`
prints this unit with its neighbours.

## Why

Something must run: hold the subscription, own the database schema,
listen on a port. This unit is that program, and it is kept free of
everything that is not running. It does not know what makes a reading
alarming and not how an owner is reached. It asks for both through needs
whose contracts it writes itself. It changes when what is stored about an
alert, the order of the steps or the queries change.

What it does know is order and durability. It is the one place that
decides what is written together and what may repeat: a reading's
outcome, the evaluation state and the owed notification are stored in one
transaction; the event is confirmed afterwards; notifying is a second
step that can run again. Every guarantee about "once" rests on these
few rules, so they are concentrated here instead of being
spread over the logic.

The trade-off: `server` treats the evaluation state as a value it cannot
read. It cannot repair or inspect it, only store it, hand it back or
drop it.

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its
   surroundings
4. [doc/references/processing.md](doc/references/processing.md): what is
   stored, the handling of an event, delivery of notifications, expiry
5. [doc/references/evaluation.md](doc/references/evaluation.md),
   [doc/references/notification.md](doc/references/notification.md),
   [doc/references/reading-events.md](doc/references/reading-events.md):
   the interfaces that the unit expects of its needs

## Rules for work here

- Never write an `if` on a measured value or a threshold in this unit.
  If a case seems to need it, the case belongs to whoever provides
  `evaluation`.
- Never call `notification` inside the transaction that stores an alert,
  and never before it commits.
- Confirm an event only after the transaction for it is committed. Leave
  it unconfirmed when `evaluation` cannot decide.
- Do not read or change the evaluation state. Store what you get, return
  what you stored.
- The unique index on open alerts is the last line of defence, not the
  mechanism. A violation of it is a bug to report, not an error to
  swallow.
- Queries and event handling use the same database. Keep queries on
  indexes; a slow query delays alerts.
