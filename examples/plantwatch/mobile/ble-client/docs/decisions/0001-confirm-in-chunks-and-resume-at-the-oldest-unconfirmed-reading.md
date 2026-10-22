---
status: proposed
date: 2026-10-06
---
# Confirm in chunks and resume at the oldest unconfirmed reading

## Context and Problem Statement

A sensor stick can hold 2 880 unconfirmed readings. A connection breaks
often: the owner walks on, or the operating system suspends the program
when a background slot ends. The sensor stick deletes readings only up to
the sequence number the client has confirmed, and serves everything after
it again. How does a fetch continue after a dropped connection without
losing or piling up work?

## Decision Drivers

- No reading is lost, whatever the moment of the interruption
- A short background slot makes lasting progress
- The client keeps no readings of its own
- Nothing is required of the sensor stick beyond `link-profile`

## Considered Options

- Fetch everything, deliver it, confirm once at the end
- Fetch everything, keep it in a buffer of the client that survives
  interruptions, deliver and confirm later
- Fetch, deliver and confirm in chunks; after an interruption start again at
  the oldest reading the sensor stick still holds unconfirmed

## Decision Outcome

Chosen option: "fetch, deliver and confirm in chunks", because every
confirmed chunk is progress that no interruption undoes, and because the
client needs no memory of an interrupted fetch: the sensor stick's own
record of what is confirmed is the resume point.

The size of a chunk and the timeouts are in
[fetch-session.md](../references/fetch-session.md).

### Consequences

- Good: an interruption costs at most one chunk of repeated transfer.
- Good: a backlog of 30 days is worked off over several short slots.
- Good: the client has no state to repair after a crash.
- Bad: one confirmation round trip per chunk instead of one per fetch.
- Bad: a chunk that was delivered but not confirmed is delivered again. The
  consumer must recognise readings it already has.
- Bad: the consumer has to store a chunk within seconds, or the slot ends
  without progress.

## Pros and Cons of the Options

### Confirm once at the end

- Good: least radio traffic when nothing goes wrong.
- Bad: a fetch of a long backlog that never finishes in one slot never
  confirms anything and starts over every time.

### Buffer in the client

- Good: the consumer may be slow or absent.
- Bad: a second store of readings on the phone, with its own rules for loss
  and duplicates, in a unit whose point is to have none.
