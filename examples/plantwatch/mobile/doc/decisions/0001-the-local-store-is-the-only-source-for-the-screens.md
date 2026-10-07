---
status: proposed
date: 2026-10-06
---
# The local store is the only source for the screens

## Context and Problem Statement

The owner opens the app next to a plant: in a cellar, on a balcony, in a
stairwell. A network connection is often missing there, and the server may
not have the newest readings yet because the phone has just fetched them.
Where do the screens get their data from?

## Considered Options

- The screens ask the server and cache the last answer
- The screens ask the server and, in addition, show readings that are still
  waiting on the phone
- The screens read only from a store on the phone; fetched readings and
  server data both flow into this store

## Decision Outcome

Chosen option: "the screens read only from a store on the phone", because it
is the only option in which a screen looks and behaves the same with and
without a network connection, and in which a reading is visible the moment
it has been fetched.

The store holds every item of the
[data model](../references/data-model.md). Changes that the owner makes go
into the store first and to the server afterwards.

### Consequences

- Good: no screen waits for the network or shows a loading state for data
  the phone already has.
- Good: a fetched reading appears in the history before it is uploaded.
- Good: the screens can be developed and tested against a filled store
  alone.
- Bad: the phone holds a copy of server data that can be days old. Every
  screen must show the age of its data.
- Bad: a change made offline can collide with a change made elsewhere. The
  part that talks to the server needs a rule for that.
- Bad: the store has a layout that must be migrated when it changes.
