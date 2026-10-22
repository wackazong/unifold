---
status: proposed
date: 2026-10-06
---
# Readings are immutable and identified by sensor id and sequence number

## Context and Problem Statement

A reading passes through several places: the sensor stick, the phone, the
server. Connections break in the middle of a transfer. A reading must neither
be lost nor counted twice.

## Considered Options

- Exactly-once transfer on every hop
- At-least-once transfer on every hop, with readings that can be recognised
  when they arrive again

## Decision Outcome

Chosen option: "at-least-once with recognisable readings", because
exactly-once transfer over BLE and mobile networks is not achievable with
reasonable effort.

A reading is identified by the pair of sensor id and sequence number. The
sensor stick assigns sequence numbers in strictly increasing order and never
reuses one. A reading is never changed after it has been taken. Every
receiver accepts a reading it already has without storing it again.

### Consequences

- Good: every sender may simply repeat a transfer after a failure.
- Good: a place may delete a reading as soon as the next place confirms it.
- Bad: every receiver must keep enough state to recognise duplicates.
- Bad: a correction of a wrong reading is impossible; it can only be
  ignored downstream.
