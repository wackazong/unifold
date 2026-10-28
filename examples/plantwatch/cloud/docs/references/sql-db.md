# sql-db

Contract of `platform.sql-db`: what a service that stores data can rely on. The product behind it is chosen in decision 0001 of `platform`. Notation: SQL and the connection parameters, written as text.
Sources: decision 0001 of `platform`, decision 0002 of `cloud`.

## Access

| Item | Value |
|---|---|
| wire protocol and SQL dialect | PostgreSQL 16 |
| address | host `sql-db`, port 5432, database `main`, inside the private network |
| authentication | role name and password; the deployment gives both to the containers of the service and to nobody else |
| encryption | none; the private network is the boundary |
| time zone | UTC |

## Limits, backup and failures

| Item | Limit |
|---|---|
| connections per role | 20 |
| duration of one statement | 30 seconds, then the database cancels it |
| idle time inside an open transaction | 60 seconds, then the database ends the connection |
| planned size of all schemas together | 50 GB; the operator is warned at 80 percent |

- The database is backed up in full once a day. Its transaction log is copied to the backup volume continuously. Backups are kept for 14 days.
- After a loss of the database volume, the state of at most 5 minutes before the loss is restored. The restore is done by hand and takes up to 1 hour. A restore brings back all schemas to the same moment; a single schema cannot be restored alone.

| Event | Effect for a service |
|---|---|
| restart of the database, up to 1 minute | connections break and new ones are refused; the service reconnects and repeats the open transaction |
| loss of the volume | up to 1 hour without database, then data as of at most 5 minutes before the loss; changes of these minutes are gone |
| the planned size is exceeded | nothing at once |

## Parts

### connect

Kind: command

```text
connect(host sql-db, port 5432, database main, role, password) -> connection
```

Pre: the role exists; the role has fewer than 20 connections open.
Result: a connection whose search path is the schema of the role.
Errors: the connection is refused at the 21st connection of a role, and while the database restarts.
Examples:

| Case | Action | Result |
|---|---|---|
| too many connections | the role opens a 21st connection | the connection is refused |

### transaction

Kind: command

```text
BEGIN [ISOLATION LEVEL READ COMMITTED | REPEATABLE READ | SERIALIZABLE]; ...; COMMIT
```

Pre: a connection is open.
Result: transactions are atomic, consistent, isolated and durable; a committed transaction survives a restart of the database. The default isolation level is read committed. A transaction covers one schema; nothing spans two services.
Errors: a transaction at repeatable read or serializable can fail with a serialization error and is then repeated by the service; the database ends the connection after 60 seconds idle inside an open transaction.
Examples:

| Case | Action | Result |
|---|---|---|
| restart | a transaction is committed, then the database restarts | the change is there after the restart |
| idle | a transaction stays open without a statement for 61 seconds | the connection is ended |

### statement

Kind: command

```text
<any statement of the PostgreSQL 16 dialect, inside a transaction>
```

Pre: the statement touches only the schema of the role.
Result: the statement is carried out. A service may rely on these features of the dialect: unique indexes that are limited by a condition, row locks that a second reader can skip, and columns of the type `jsonb`.
Errors: a permission error for any other schema; the database cancels a statement after 30 seconds and the transaction fails.
Examples:

| Case | Action | Result |
|---|---|---|
| own schema | the role `greenhouse` creates the table `greenhouse.pot` | success |
| foreign schema | the role `greenhouse` reads a table of another schema | permission error |
| long statement | a statement runs for 31 seconds | the database cancels it; the transaction fails |

### schema

Kind: type

```text
schema <service>, role <service>: own schema, empty at hand-over; the service creates its tables and applies its own migrations
```

A service gets a schema and a role, both named after the service, with the skill `platform-add-a-schema` of `platform`. All instances of a service use the same role.

| The role of a service | Allowed |
|---|---|
| create, change and drop tables, indexes, views, sequences and functions in its own schema | yes |
| read and write the data in its own schema | yes |
| see or use any other schema | no |
| create schemas, roles, databases or extensions | no |

## Fake

The real product in a throwaway container on the developer machine, with one empty schema and role per test, since no fake speaks the dialect. Faults it can inject: a restart that breaks the connections; a refused connection.
