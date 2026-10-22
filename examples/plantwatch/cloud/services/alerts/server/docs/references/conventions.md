# Conventions of server

How work in this unit is done. What must hold at every moment is in the [invariants](../explanation/invariants.md).

- The unique index on open alerts is the last line of defence, not the mechanism. A violation of it is a bug to report, not an error to swallow.
- Queries and event handling use the same database. Queries stay on indexes; a slow query delays alerts.
