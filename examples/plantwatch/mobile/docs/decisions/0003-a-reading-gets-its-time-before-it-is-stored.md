---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# A reading gets its UTC time before it is stored

## Context and Problem Statement

A sensor stick delivers readings with tick counts. A tick count becomes a time only together with the sensor stick's current tick count and the phone's clock at the moment of the fetch. Several parts of the app handle readings: one fetches them, one stores and uploads them, one shows them. Which part converts, and what do the others see?

## Considered Options

- Store readings with tick counts and convert when they are shown or uploaded
- Store readings with tick counts and let a later fetch improve the times
- Convert at the moment of the fetch, in the part that fetches; every reading that leaves this part carries a UTC time and an estimated flag

## Decision Outcome

Chosen option: "convert at the moment of the fetch", because the two facts the conversion needs exist only then, and because a reading must not change after it has been stored.

The part that fetches is also the only part that computes with tick counts. The tick count stays in the reading, because the reading schema carries it, and nothing else interprets it. The store, the upload and the screens work with the time and the flag.

A time that cannot be computed is estimated and flagged. The flag stays with the reading for good: it is stored, uploaded and shown.

### Consequences

- Good: one place computes with tick counts. In the [data model](../references/data-model.md) the tick count is a field that is carried along.
- Good: a stored reading is final. Showing it and uploading it need no further computation.
- Bad: an estimate is never improved, even if a later fetch would allow a better one.
- Bad: a wrong phone clock at the moment of the fetch gives wrong times that stay wrong.
- Bad: the same reading, fetched twice after an interruption, can get two times that differ by a second or two. The store keeps the first.
