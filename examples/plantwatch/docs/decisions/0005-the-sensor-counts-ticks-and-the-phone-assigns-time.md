---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The sensor stick counts ticks and the phone assigns UTC time

## Context and Problem Statement

A reading needs a time. The sensor stick has no network and no battery-backed clock that survives a cell change.

## Considered Options

- The phone sets a wall clock on the sensor stick at every connection
- The sensor stick stamps readings with a tick count; the phone converts to UTC when it fetches them

## Decision Outcome

Chosen option: "tick count, converted by the phone", because the sensor stick then never holds a time that could be wrong, and a restart cannot produce readings with a false date.

A reading carries a boot counter and the number of seconds since that boot. At fetch time the phone reads the stick's current tick and computes the UTC time of each reading of the current boot. Readings from an earlier boot whose time cannot be computed are kept and marked as having an estimated time.

### Consequences

- Good: no time setting protocol and no drift correction on the stick.
- Bad: after a restart of the stick, older unfetched readings have only an estimated time.
- Bad: the phone's clock becomes the time source for all history.
