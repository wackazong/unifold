---
status: proposed
date: 2026-10-06
---
# Raw readings are kept for 90 days, hourly aggregates for 2 years

## Context and Problem Statement

`plants` must answer history queries over 2 years per plant. At the
shortest sampling interval a plant has 105 120 readings per year. The
contract that `plants` serves offers raw readings only for the last 90
days and aggregates per hour and day for the whole period
([context](../context.md)). How is the history stored so that a query
over 2 years is fast, and so that repeated and late events do no harm?

## Considered Options

- Keep every raw reading for 2 years and aggregate at query time
- Keep raw readings for 90 days and maintain hourly aggregates when a
  reading is stored; compute days from hours at query time
- Keep raw readings for 90 days and build aggregates with a nightly job
- Use a time-series extension of the database that aggregates by itself

## Decision Outcome

Chosen option: "raw for 90 days, hourly aggregates maintained on write",
because a query over 2 years then reads at most 17 520 rows per plant, the
aggregate is current as soon as the reading is, and nothing beyond a plain
relational database is needed.

The aggregate of an hour is always recomputed from the raw readings of
that hour, in the transaction that stores a reading. It is never
incremented. The tables are in
[data model](../references/data-model.md).

### Consequences

- Good: storage per plant is bounded at about 26 000 raw and 17 520
  aggregate rows.
- Good: a repeated event changes nothing, and a late reading corrects its
  hour, because recomputing is idempotent.
- Good: one hour holds at most 12 readings, so recomputing is cheap.
- Bad: after 90 days an aggregate is final. A new kind of aggregate, such
  as a median, can be filled only for the last 90 days.
- Bad: a reading older than 90 days cannot enter history.
- Bad: every stored reading costs a second write for its hour.

## Pros and Cons of the Options

### Raw for 2 years, aggregate at query time

- Good: one table, any aggregate at any time.
- Bad: a 2-year query scans up to 210 240 rows per plant on every
  request.
- Bad: about four times the storage.

### Nightly job

- Good: no second write per reading.
- Bad: the current day has no aggregates, or a second code path computes
  them at query time.

### Time-series extension

- Good: aggregation and retention are built in.
- Bad: needs an extension that the database this unit is given does not
  offer, for a data volume that plain tables carry easily.
