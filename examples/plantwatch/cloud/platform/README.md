# platform

`platform` operates the two pieces of infrastructure that several services share: an event bus and a relational database. It runs them as containers, declares topics, schemas and roles, and looks after their data. It contains configuration and operating procedures, no service logic.

## Why

A message bus and a database are used by several services and belong to none of them. If each service configured its share, no one could say what the bus guarantees, who may read which schema, or what is backed up. This unit is the one place where the infrastructure is chosen, configured and operated, and where its guarantees are written down. It changes when a guarantee of the bus or the database changes, when a service needs a new topic or schema, or when a product behind a capability is replaced.

Bus and database stay in one unit because they share their operator, their host and their backup routine. Two units would hold the same reasons twice.

The main trade-off is weight against guarantees. A database alone could carry the small load of version 1 as a queue. A real broker is chosen because order per key, replay and durable subscriptions then come ready-made ([0001](docs/decisions/0001-postgresql-and-a-kafka-compatible-broker.md)).

What must stay true: a service relies on the two contracts without knowing the products behind them, and the database itself enforces the isolation between schemas.

## Capabilities

### `event-bus`

A message broker with named topics. A publisher gets an acknowledgement when its message is stored. A named subscription receives every message of a topic at least once and, for messages with the same key, in the order in which they were published. A subscriber that was down continues where it stopped.

- A message can arrive more than once. It never arrives out of order within its key, and the bus never skips one.
- A topic keeps its messages for 7 days, whether they were consumed or not. A topic of the kind keep-latest keeps the latest message per key without a time limit.
- Topics exist only when they are declared in this unit.
- The bus runs as one instance. During a restart of up to 1 minute it accepts nothing; clients reconnect by themselves.
- The bus has no backup. If its volume is lost, messages that were not yet consumed are lost.

Example: a subscriber confirms the messages 1 to 7 of a key, handles message 8 and stops before it confirms. After its restart it receives message 8 again, then 9.

Contract: [event bus](../docs/references/event-bus.md).

### `sql-db`

A relational database server with ACID transactions. Every service gets a schema of its own and a role that can use this schema and no other. The service creates and changes the tables in its schema itself.

- A committed transaction survives a restart.
- A backup allows the state of at most 5 minutes before a loss of the volume to be restored.
- The database runs as one instance. During a restart of up to 1 minute it refuses connections; clients reconnect by themselves.
- A role may hold at most 20 connections.

Example: a service named `greenhouse` connects with the role `greenhouse` and creates the table `greenhouse.pot`. Its `SELECT` on a table of another schema fails with a permission error.

Contract: [SQL database](../docs/references/sql-db.md).

## Needs

### `container-host`

`platform` expects a host that runs its containers, restarts one that stops, and gives each a network name under which the other containers of the same private network reach it. It expects three volumes that survive restart and replacement of a container: one for the bus, one for the database and one for database backups. The backup volume lies on other storage than the database volume. Nothing of `platform` is reachable from outside the private network.

## Out of scope

- Tables, indexes and migrations. They belong to the service that owns the schema.
- The content and the meaning of messages. `platform` knows topic names and nothing about the events in them.
- Redundancy. Version 1 runs one instance of each.
- Logs and metrics of services.

## Read next

1. [event bus](../docs/references/event-bus.md): contract of `event-bus`
2. [SQL database](../docs/references/sql-db.md): contract of `sql-db`
3. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
4. [Context diagram](docs/diagrams/context.md), [decisions](docs/decisions/index.md)
