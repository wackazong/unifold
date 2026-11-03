---
status: proposed
date: 2026-11-03
---

# Leave a lost session without uploading

## Context and Problem Statement

`leave` uploads what is waiting before it removes the owner's data from the phone. In the session `lost`, the server refuses the token, so the upload can never succeed. A refused token usually means that the owner withdrew this phone. What does `leave` do in a lost session?

## Considered Options

- Remove everything without uploading; readings the server has not confirmed are lost
- Fail with `token not accepted`, and keep everything until the phone joins again

## Decision Outcome

Chosen option: "remove everything without uploading", because keeping an owner's data on a phone that the owner no longer trusts is the bigger risk. A user who wants to save the waiting readings joins again first; `readings-waiting` of the exchange state shows how many there are.

### Consequences

- Good: a withdrawn phone can always be cleared, also without a network connection.
- Bad: readings that only this phone held are lost when the user leaves without joining first.

## More Information

The part [`leave`](../references/plant-data/leave.md) of the contract [`plant-data`](../references/plant-data/index.md) states the result.
