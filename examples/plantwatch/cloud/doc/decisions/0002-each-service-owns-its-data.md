---
status: proposed
date: 2026-10-06
---
# Each service owns its data and nobody else reads it

## Context and Problem Statement

Several services store data in one relational database server. They could
share tables, which makes joins easy, or keep their data apart. Shared
tables tie the services together: a column cannot change without changing
every reader, and no service can be understood or replaced alone.

## Considered Options

- One schema for all services, tables shared where convenient
- One schema per service on one database server, enforced by database roles
- One database server per service

## Decision Outcome

Chosen option: "one schema per service on one server", because it gives the
isolation that matters, which is that no service depends on the tables of
another, at the cost of operating a single database.

Each service connects with a role that has rights on its own schema only.
A service that needs data of another service gets it through a port of that
service: a call or an event stream.

### Consequences

- Good: a schema change stays inside one service.
- Good: a broken rule fails at once with a permission error instead of
  growing unnoticed.
- Good: a service can move to a database server of its own without a change
  to any other service.
- Bad: no joins across services. An answer that combines data of two
  services is assembled by the caller.
- Bad: no transaction spans two services. Consistency between them is
  eventual.
- Bad: all services still share the load and the availability of one
  server.
