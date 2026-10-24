# platform

`platform` operates the two pieces of infrastructure that several services share: an event bus and a relational database. It runs them as containers, declares topics, schemas and roles, and looks after their data. It contains configuration and operating procedures, no service logic.

## Why

A message bus and a database are used by several services and belong to none of them. If each service configured its share, no one could say what the bus guarantees, who may read which schema, or what is backed up. This unit is the one place where the infrastructure is chosen, configured and operated, and where its guarantees are written down. It changes when a guarantee of the bus or the database changes, when a service needs a new topic or schema, or when a product behind a capability is replaced.

Bus and database stay in one unit because they share their operator, their host and their backup routine. Two units would hold the same reasons twice.

The main trade-off is weight against guarantees. A database alone could carry the small load of version 1 as a queue. A real broker is chosen because order per key, replay and durable subscriptions then come ready-made ([0001](docs/decisions/0001-postgresql-and-a-kafka-compatible-broker.md)).

What must stay true: a service relies on the two contracts without knowing the products behind them, and the database itself enforces the isolation between schemas.

## Needs

### `container-host`

`platform` asks for three volumes: one for the bus, one for the database and one for database backups. The backup volume lies on other storage than the database volume. `platform` publishes no port.

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
