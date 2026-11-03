---
status: proposed
date: 2026-11-03
---

# Name the lost session as an event, and let `join` end it

## Context and Problem Statement

A session of [plant-data](../references/plant-data/index.md) becomes `lost` when the server refuses the token at an exchange. The provider runs exchanges by itself, so no call leads into `lost`; a consumer saw it only in `exchange-state`. The way out contradicted itself: `exchange-state` said that nothing is exchanged "until the phone joins the owner again", while `join` required the session `none` and failed with `session exists` otherwise. How does a consumer learn that a session is lost, and how does the phone get out of it?

## Considered Options

- Keep `lost` visible only in `exchange-state`, and leave the way out to `leave`
- An event `session-lost`, and `join` from `lost` with the data that is on the phone
- An error `token not accepted` on the next command

## Decision Outcome

Chosen option: "an event `session-lost`, and `join` from `lost`", because the event names what happens at the moment it happens, and `join` from `lost` is the way out that `exchange-state` already describes. The phone keeps its plants, readings and waiting changes, and the next exchange uploads them with the new token.

### Consequences

- Good: the states of `plant-data` lead into `lost` and out of it, so the screens and their tests can follow a lost session.
- Bad: `join` now has two meanings: a first join, and a rejoin that keeps local data.

## More Information

The contract [`plant-data`](../references/plant-data/index.md), its parts [`session-lost`](../references/plant-data/session-lost.md) and [`join`](../references/plant-data/join.md) state the result.
