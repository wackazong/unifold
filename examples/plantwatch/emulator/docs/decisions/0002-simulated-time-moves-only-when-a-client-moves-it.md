---
status: proposed
date: 2026-10-06
---
# Simulated time moves only when a client moves it

## Context and Problem Statement

A sensor stick takes a reading every 15 minutes and fills its memory in 30
days. Nobody can wait that long for a check, so the program has a simulated
clock. What makes that clock advance?

## Decision Drivers

- A run gives the same readings every time, on a fast and on a slow
  machine.
- A client knows when the readings it asked for exist.
- The control API follows the convention that a repeated request succeeds
  again, cited in [context](../explanation/context.md).

## Considered Options

- The clock runs by itself, faster than real time by a factor
- The clock stands still; a client asks for a step forward ("advance one
  hour")
- The clock stands still; a client names the time to reach ("be at hour
  72")

## Decision Outcome

Chosen option: "a client names the time to reach", because it is
reproducible and a repeated request cannot move time twice.

The request returns when all readings up to that time exist. For work by
hand, a client may switch on a rate; this is the first option as an opt-in,
and a run with a rate is not reproducible.

### Consequences

- Good: the readings of a run depend only on the scenario and the requests.
- Good: no waiting and no polling: after the response, the readings are
  there.
- Good: a client that repeats a request after a timeout does no harm.
- Bad: a client has to keep track of the time it has reached, or ask for
  the state first.
- Bad: time cannot go back. A client that wants an earlier state loads the
  scenario again.
- Bad: nothing happens between two requests, so behaviour "while a
  transfer runs" needs its own switch in the API.
