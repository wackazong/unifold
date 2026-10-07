---
unit: platform
summary: Shared infrastructure of the services - message bus and database
kind: infrastructure
status: planned
provides:
  event-bus:
    kind: queue
    summary: Durable publish and subscribe with at-least-once delivery
    contract: doc/references/event-bus.md
  sql-db:
    kind: db
    summary: Relational database with transactions, one schema per service
    contract: doc/references/sql-db.md
needs:
  container-host:
    kind: infrastructure
    summary: Runs containers, gives them a private network and persistent volumes
---
# platform

`platform` operates the two pieces of infrastructure that several services
share: an event bus and a relational database. It runs them as containers,
declares topics, schemas and roles, and looks after their data. It contains
configuration and operating procedures, no service logic.

## Provides

### `event-bus`

A message broker with named topics. A publisher gets an acknowledgement
when its message is stored. A named subscription receives every message of
a topic at least once and, for messages with the same key, in the order in
which they were published. A subscriber that was down continues where it
stopped.

- A message can arrive more than once. It never arrives out of order
  within its key, and the bus never skips one.
- A topic keeps its messages for 7 days, whether they were consumed or not.
  A topic of the kind keep-latest keeps the latest message per key without
  a time limit.
- Topics exist only when they are declared in this unit.
- The bus runs as one instance. During a restart of up to 1 minute it
  accepts nothing; clients reconnect by themselves.
- The bus has no backup. If its volume is lost, messages that were not yet
  consumed are lost.

Contract: [event bus](doc/references/event-bus.md).

### `sql-db`

A relational database server with ACID transactions. Every service gets a
schema of its own and a role that can use this schema and no other. The
service creates and changes the tables in its schema itself.

- A committed transaction survives a restart.
- A backup allows the state of at most 5 minutes before a loss of the
  volume to be restored.
- The database runs as one instance. During a restart of up to 1 minute it
  refuses connections; clients reconnect by themselves.
- A role may hold at most 20 connections.

Contract: [SQL database](doc/references/sql-db.md).

## Needs

### `container-host`

`platform` expects a host that runs its containers, restarts one that
stops, and gives each a network name under which the other containers of
the same private network reach it. It expects three volumes that survive
restarts and removal of a container: one for the bus, one for the database
and one for database backups. The backup volume lies on other storage than
the database volume. Nothing of `platform` is reachable from outside the
private network.

## Out of scope

- Tables, indexes and migrations. They belong to the service that owns the
  schema.
- The content and the meaning of messages. `platform` knows topic names and
  nothing about the events in them.
- Redundancy. Version 1 runs one instance of each.
- Logs and metrics of services.

## More

- [AGENTS.md](AGENTS.md): why shared infrastructure is a unit
- [doc/context.md](doc/context.md): what the unit inherits
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- References: [event bus](doc/references/event-bus.md),
  [SQL database](doc/references/sql-db.md)
