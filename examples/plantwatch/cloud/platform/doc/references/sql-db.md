# SQL database

The contract of the port `sql-db`: what a service that stores data can rely
on. The product behind it is chosen in
[0001](../decisions/0001-postgresql-and-a-kafka-compatible-broker.md).

## Access

| Item | Value |
|---|---|
| Wire protocol and SQL dialect | PostgreSQL 16 |
| Address | Host `sql-db`, port 5432, database `main`, inside the private network |
| Authentication | Role name and password. The deployment gives both to the containers of the service and to nobody else. |
| Encryption | None. The private network is the boundary. |
| Time zone | UTC |

## Schemas and roles

A service gets a schema and a role, both named after the service, with the
skill [platform-add-a-schema](../skills/platform-add-a-schema/SKILL.md).

| The role of a service | Allowed |
|---|---|
| Create, change and drop tables, indexes, views, sequences and functions in its own schema | yes |
| Read and write the data in its own schema | yes |
| See or use any other schema | no |
| Create schemas, roles, databases or extensions | no |

- The search path of a role is its own schema.
- A service may rely on these features of the dialect: unique indexes that
  are limited by a condition, row locks that a second reader can skip, and
  columns of the type `jsonb`.
- The schema is empty when the service gets it. The service creates its
  tables and applies its own migrations.
- All instances of a service use the same role.

## Transactions

- Transactions are atomic, consistent, isolated and durable.
- The default isolation level is read committed. Repeatable read and
  serializable are available; a transaction at these levels can fail with
  a serialization error and is then repeated by the service.
- A transaction covers one schema. Nothing spans two services.
- A committed transaction survives a restart of the database.

## Limits

| Item | Limit |
|---|---|
| Connections per role | 20 |
| Duration of one statement | 30 seconds, then the database cancels it |
| Idle time inside an open transaction | 60 seconds, then the database ends the connection |
| Planned size of all schemas together | 50 GB |

## Backup and restore

- The database is backed up in full once a day. Its transaction log is
  copied to the backup volume continuously.
- After a loss of the database volume, the state of at most 5 minutes
  before the loss is restored. The restore is done by hand and takes up to
  1 hour.
- A restore brings back all schemas to the same moment. A single schema
  cannot be restored alone.
- Backups are kept for 14 days.

## Examples

| Case | Action | Result |
|---|---|---|
| Own schema | The role `greenhouse` creates the table `greenhouse.pot` | Success |
| Foreign schema | The role `greenhouse` reads a table of another schema | Permission error |
| Too many connections | The role opens a 21st connection | The connection is refused |
| Long statement | A statement runs for 31 seconds | The database cancels it; the transaction fails |
| Restart | A transaction is committed, then the database restarts | The change is there after the restart |

## What can go wrong

| Event | Effect for a service |
|---|---|
| Restart of the database, up to 1 minute | Connections break and new ones are refused. The service reconnects and repeats the open transaction. |
| Loss of the volume | Up to 1 hour without database, then data as of at most 5 minutes before the loss. Changes of these minutes are gone. |
| The planned size is exceeded | Nothing at once. The operator is warned at 80 percent. |
