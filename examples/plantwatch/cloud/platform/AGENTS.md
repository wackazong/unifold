# AGENTS.md: platform

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show cloud/platform`
prints this unit with its neighbours.

## Why

A message bus and a database are used by several services and belong to
none of them. If each service configured its share, no one could say what
the bus guarantees, who may read which schema, or what is backed up. This
unit is the one place where the infrastructure is chosen, configured and
operated, and where its guarantees are written down. It changes when a
guarantee of the bus or the database changes, when a service needs a new
topic or schema, or when a product behind a port is replaced.

Bus and database stay in one unit because they share their operator, their
host and their backup routine. Two units would hold the same reasons twice.

The main trade-off is weight against guarantees. A database alone could
carry the small load of version 1 as a queue. A real broker is chosen
because order per key, replay and durable subscriptions then come
ready-made
([0001](doc/decisions/0001-postgresql-and-a-kafka-compatible-broker.md)).

What must stay true: a service relies on the two contracts without knowing
the products behind them, and the database itself enforces the isolation
between schemas.

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit among the
   services
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/event-bus.md](doc/references/event-bus.md): contract of
   `event-bus`
6. [doc/references/sql-db.md](doc/references/sql-db.md): contract of
   `sql-db`

## Skills

| Skill | Use it when |
|---|---|
| [platform-add-a-topic](doc/skills/platform-add-a-topic/SKILL.md) | A service needs a topic that does not exist yet |
| [platform-add-a-schema](doc/skills/platform-add-a-schema/SKILL.md) | A service that stores data is added |

## Rules for work here

- The two contracts are technology-neutral where a service relies on them
  and name the product only where a client must know the wire protocol. Do
  not promise a feature of the product that is not in the contract.
- Never create a table, a view or a function inside a service's schema.
- Never grant a role rights on a schema other than its own, not even
  read-only and not "for a moment". A report across schemas is a new port
  of a service, not a grant.
- Topics are not created on first use. A topic that is not declared here
  does not exist, in every environment.
- Changing the number of partitions of a topic breaks the order within a
  key. A topic that needs more partitions is replaced by a new topic.
- A product upgrade that changes a guarantee in a contract is a decision,
  not maintenance.
