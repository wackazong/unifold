# AGENTS.md: alerts

This folder is a [youmedoc](https://youmedoc.example) unit.

## Why

The promise of the product is "one notification when a plant needs
attention". This unit owns that promise. It is the only place that
compares a reading with a threshold and the only place that talks to the
push service.

Inside, three things change for different reasons and are tested in
different ways. The rules by which a reading is judged are pure logic that
changes with every new quantity and is best tested with tables of
readings. Notifying depends on the push service and on wording. Consuming
events, storing alerts and answering queries is plumbing with
transactions. They are three children: one process and two libraries it
calls
([0001](doc/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)).
One deployable stays, so that an alert and what led to it are stored in
one transaction
([0002](doc/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)).

What must stay true: an alert opens once, and an opened alert leads to one
notification, although events and calls can repeat. The long form is in
[doc/architecture.md](doc/architecture.md).

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

## Skills

| Skill | Use it when |
|---|---|
| [alerts-add-a-quantity](doc/skills/alerts-add-a-quantity/SKILL.md) | A new measured quantity shall be able to cause an alert |

## Rules for work here

- The three children do not know each other. What the process wants from
  a library is a need of the process; never let one library call the
  other.
- Only the process has state. A library that wants to remember something
  returns it to its caller.
- Do not send a notification from the handling of an event. Handling
  stores the alert with a pending notification; delivery is a separate
  step that can repeat
  ([0002](doc/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)).
- Judge by the time of the reading, never by the clock. The same events
  in the same order must give the same alerts on any day.
- A change to when an alert opens or closes changes what clients see.
  Check it against the contract cited in [doc/context.md](doc/context.md)
  before you change a rule.
