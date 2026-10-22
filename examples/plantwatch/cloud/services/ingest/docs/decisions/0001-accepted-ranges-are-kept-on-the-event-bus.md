---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Duplicates are recognised by accepted ranges kept on the event bus

## Context and Problem Statement

`ingest` must tell a client which readings of a batch are new and must not announce an accepted reading again. For that it has to remember, per sensor stick, what it accepted. Readings do not always arrive in rising order: two clients can hold readings of the same sensor stick and upload them in any order. `ingest` shall depend on as little as possible.

## Considered Options

- Remember only the highest accepted sequence number per sensor stick
- Store every accepted reading identity in a database table with a unique key
- Remember the accepted sequence numbers per sensor stick as ranges, in memory, and persist them in a keep-latest topic on the event bus
- Do not recognise duplicates; announce everything and leave it to the subscribers

## Decision Outcome

Chosen option: "ranges in a keep-latest topic", because it recognises readings that arrive out of order and adds no dependency: `ingest` needs the event bus anyway.

The form of the state and its limits are in
[accepted ranges](../references/accepted-ranges.md).

### Consequences

- Good: an upload works while every database is down.
- Good: the state is small. Sequence numbers are dense, so a sensor stick normally has one or a few ranges.
- Good: a new instance has the full state after reading one topic.
- Bad: publishing the events and recording the range are two steps. A failure between them, or two instances that work on the same sensor stick, lead to repeated events. Subscribers must tolerate them.
- Bad: the client is then told `new` for a reading that was accepted before. That is harmless for the client.
- Bad: the number of ranges per sensor stick is limited. Beyond the limit a reading in an old gap is taken for a duplicate and lost. This needs more than 1 000 gaps in the sequence numbers of one sensor stick.
- Bad: an instance needs the whole state in memory and is not ready until it has read it.

## Pros and Cons of the Options

### Highest accepted sequence number

- Good: one number per sensor stick.
- Bad: a batch with older readings that arrives after a newer batch would be taken for duplicates and lost.

### Database table with a unique key

- Good: exact, also with several instances.
- Bad: the upload path would depend on a database. Its outage would stop uploads.
- Bad: one row per reading for a fact that a range states for thousands.

### No recognition

- Good: nothing to remember.
- Bad: the client could not be told what was new, and every repeated upload would flood the subscribers.
