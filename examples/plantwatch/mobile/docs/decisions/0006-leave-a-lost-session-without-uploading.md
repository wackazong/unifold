---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Leave a lost session without uploading

## Context and Problem Statement

`leave` uploads what is waiting before it removes the owner's data from the phone. In the session `lost`, the server refuses the token, so the upload can never succeed. A refused token usually means that it has expired, and an expired token cannot be renewed. What does `leave` do in a lost session?

## Considered Options

- Remove everything without uploading; readings the server has not confirmed are lost
- Fail with `token not accepted`, and keep everything until the phone joins again

## Decision Outcome

Chosen option: "remove everything without uploading", because keeping an owner's data on a phone that can no longer act for the owner is the bigger risk. A user who wants to save the waiting readings joins again first; `readings-waiting` of the exchange state shows how many there are.

### Consequences

- Good: a phone whose token is refused can always be cleared, also without a network connection.
- Bad: readings that only this phone held are lost when the user leaves without joining first.

## More Information

The part [`leave`](../references/plant-data/leave.md) of the contract [`plant-data`](../references/plant-data/index.md) states the result.
