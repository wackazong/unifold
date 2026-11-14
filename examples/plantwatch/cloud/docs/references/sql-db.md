# sql-db

Contract of `platform.sql-db`: what a service that stores data can rely on. Notation: SQL and the connection parameters, written as text.
Sources: none.
Binding: sql

## Use

A service connects with its role and runs its statements inside transactions on that connection. A transaction covers the schema of the role and nothing else. When the connection breaks or is refused, the service connects again and repeats the open transaction. The database speaks the wire protocol and the SQL dialect of PostgreSQL 16 at host `sql-db`, port 5432, database `main`, inside the private network; its time zone is UTC.

## Qualities

| Aspect | Guarantee |
|---|---|
| security | role name and password; the deployment gives both to the containers of the service and to nobody else; no encryption, the private network is the boundary |
| concurrency | at most 20 connections per role |
| timeout | a statement is cancelled after 30 seconds; a connection that is idle inside an open transaction for 60 seconds is ended |
| limits | 50 GB for all schemas together; the operator is warned at 80 percent; exceeding the limit does nothing at once |
| durability | a committed transaction survives a restart of the database |
| backup | a full backup once a day, the transaction log copied to the backup volume continuously, backups kept for 14 days |
| recovery | after a loss of the database volume, the state of at most 5 minutes before the loss is restored, by hand, within 1 hour; a restore brings back all schemas to the same moment, and a single schema cannot be restored alone; the changes of these minutes are gone |
| availability | a restart of the database takes up to 1 minute, during which connections break and new ones are refused; the service reconnects and repeats the open transaction |

## Parts

### connect

Kind: operation

```text
connect(host sql-db, port 5432, database main, role, password) -> connection, search path: the schema of the role
```

Pre: the role exists; the role has fewer than 20 connections open.
Result: a connection whose search path is the schema of the role.
Errors: the connection is refused at the 21st connection of a role, and while the database restarts.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| too many connections | the role has 20 connections open | `connect` with that role | the connection is refused |

### transaction

Kind: operation

```text
BEGIN [ISOLATION LEVEL READ COMMITTED | REPEATABLE READ | SERIALIZABLE]; ...; COMMIT
```

Pre: a connection is open.
Result: transactions are atomic, consistent, isolated and durable. The default isolation level is read committed. A transaction covers one schema; nothing spans two services.
Errors: a transaction at repeatable read or serializable can fail with a serialization error and is then repeated by the service; the database ends the connection after 60 seconds idle inside an open transaction.
Examples:

| Case | Input | Expected |
|---|---|---|
| restart | a transaction is committed, then the database restarts | the change is there after the restart |
| idle | a transaction stays open without a statement for 61 seconds | the connection is ended |

### statement

Kind: operation

```text
<any statement of the PostgreSQL 16 dialect, inside a transaction>
```

Pre: the statement touches only the schema of the role.
Result: the statement is carried out. A service may rely on these features of the dialect: unique indexes that are limited by a condition, row locks that a second reader can skip, and columns of the type `jsonb`.
Errors: a permission error for any other schema; the database cancels a statement after 30 seconds and the transaction fails.
Examples:

| Case | Input | Expected |
|---|---|---|
| own schema | the role `greenhouse` creates the table `greenhouse.pot` | ok |
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
