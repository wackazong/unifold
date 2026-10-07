# AGENTS.md: alerts

This folder is a [youmedoc](https://youmedoc.example) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `youmedoc`. From
there, `python3 doc/skills/check-docs/scripts/youmedoc.py show cloud/services/alerts`
prints this unit with its neighbours.

## Why

The promise of the product is "one notification when a plant needs
attention". This unit owns that promise. It is the only place that
compares a reading with a threshold and the only place that talks to the
push service. It changes when that promise changes: what counts as needing
attention, and how and when the owner is told.

Inside, four things change for different reasons, and each is a child. The
rules by which a reading is judged are pure logic, tested with tables of
readings ([rules](rules/README.md)). The registry of plants and the push
service are technologies behind a network; each has an adapter, so that
the logic names neither
([0003](doc/decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md)).
Consuming events, storing alerts and answering queries is plumbing with
transactions ([server](server/README.md)). All are built into one program
([0001](doc/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)),
so that an alert and what led to it are stored in one transaction
([0002](doc/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)).

What must stay true: an alert opens once, and an opened alert leads to one
notification, although events and calls can repeat.

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/architecture.md](doc/architecture.md): invariants, the life of an
   alert, the handling of one reading
4. [doc/diagrams/component.md](doc/diagrams/component.md): the children
   and their wiring
5. [doc/decisions/index.md](doc/decisions/index.md): decisions
6. [doc/references/alerts-api.md](doc/references/alerts-api.md): how the
   API is served
7. [doc/references/glossary.md](doc/references/glossary.md): the terms of
   this unit

## Skills

| Skill | Use it when |
|---|---|
| [alerts-add-a-quantity](doc/skills/alerts-add-a-quantity/SKILL.md) | A new measured quantity shall be able to cause an alert |

## Rules for work here

- The children do not know each other. What one wants from another is a
  need with a contract of its own; only the wiring of this unit connects
  them. After a change to a child's port, read both ends of its wiring
  lines again.
- A need of the judging logic is of kind `library`. Whatever lives behind
  a network gets an adapter.
- Only the process stores anything. A library that must remember something
  between two calls returns it to its caller. The one exception is
  recorded in
  [0003](doc/decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md).
- Do not send a notification from the handling of an event. Handling
  stores the alert with a pending notification; delivery is a separate
  step that can repeat
  ([0002](doc/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)).
- Judge by the time of the reading, never by the clock. The same events
  in the same order must give the same alerts on any day.
- A change to when an alert opens or closes changes what clients see.
  Check it against the contract cited in [doc/context.md](doc/context.md)
  before you change a rule.
