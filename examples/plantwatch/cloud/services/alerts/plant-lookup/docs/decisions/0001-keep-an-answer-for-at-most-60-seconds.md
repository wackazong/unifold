---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Keep an answer for at most 60 seconds and never use an older one

## Context and Problem Statement

Every reading that is judged needs the plant and the thresholds of its sensor stick. Readings come in batches: one upload can bring hundreds of readings of the same sensor stick within a second. The registry of plants is reached over a network and can be down. A changed threshold may take up to 60 seconds to apply ([context](../explanation/context.md)). What does `plant-lookup` do between asking the registry on every call and answering from memory?

## Considered Options

- Ask the registry on every call
- Keep each answer for at most 60 seconds; answer `unavailable` when the registry cannot be reached and no answer of that age exists
- Keep the last answer without a limit of age and use it while the registry cannot be reached
- Keep a copy of all thresholds that is updated when a plant changes

## Decision Outcome

Chosen option: "keep for at most 60 seconds, then `unavailable`", because a batch of one sensor stick then costs one request, the 60 seconds that a change may take are kept, and a reading that waits is judged correctly later, while a reading judged by old thresholds can open an alert that nobody can take back.

`unattached` is kept like `attached`. `unavailable` is never kept.

### Consequences

- Good: at most one request per sensor stick in 60 seconds.
- Good: an outage of the registry delays alerts and never falsifies one.
- Good: no alert reaches a former owner more than 60 seconds after a sensor stick was moved to a plant of another owner.
- Bad: an outage of more than 60 seconds stops all judging, although most thresholds did not change in that time.
- Bad: the kept answers are state in memory, per instance and lost at a restart.
- Bad: a change shows up to 60 seconds late.

## Pros and Cons of the Options

### Ask on every call

- Good: always current, no state.
- Bad: a batch of 500 readings causes 500 requests for the same answer.

### Keep the last answer without a limit

- Good: judging goes on while the registry is down.
- Bad: an alert can be opened by a threshold that the owner removed, or be sent to the owner a sensor stick no longer belongs to.

### A copy that is updated when a plant changes

- Good: no request per reading at all.
- Bad: needs a stream of plant changes, which is ruled out above this unit
  ([context](../explanation/context.md)).
