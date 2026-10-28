---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The change that reaches the server last wins, setting by setting

## Context and Problem Statement

The owner changes a plant's name or a limit on the phone without a network connection. Before the change reaches the server, the same plant may have been changed from another phone of the same owner. `cloud-api` takes a plant only as a whole: what is written replaces what was there. Which values does the plant end up with, and what does the owner get to see?

## Decision Drivers

- A change made offline is not lost silently
- The owner is not asked questions about conflicts with themselves
- Nothing is demanded of the server beyond reading and writing a plant

## Considered Options

- The server's values always win; an offline change to a plant that has changed meanwhile is discarded
- Write the phone's copy of the plant; the plant that arrives last replaces the server's as a whole
- Remember which settings the owner changed; read the server's plant, lay these settings over it, write the result
- Have the server compare versions and refuse a change that was based on an outdated plant; the owner decides

## Decision Outcome

Chosen option: "remember the changed settings, read, lay over, write", because one owner who changes two different settings on two phones keeps both changes, and a true collision on one setting between an owner and themselves does not justify a question.

For a single setting the value that reaches the server last wins. sync takes the server's answer to the write as the new state of the plant, so the phone shows the outcome at once, including settings that were changed elsewhere.

While a change waits, values that arrive from the server for the same plant do not overwrite the waiting settings on the phone.

A change to a plant that the server no longer has is not written, because writing would create the plant again. The plant becomes `refused`. The states and reasons are in [plant-data.md](../../../docs/references/plant-data/index.md).

### Consequences

- Good: changes to different settings do not collide, except in the moment between reading and writing.
- Good: settings the phone does not know or show pass through untouched.
- Good: no version numbers on the phone and no question to the owner.
- Bad: two requests per changed plant instead of one.
- Bad: a change that another phone writes between this phone's read and its write is overwritten unseen. The window is a fraction of a second.
- Bad: "last" means last to arrive, not last made. A change made offline a week ago overwrites a newer one when the phone finally comes online.
- Bad: the owner is not told that a value was overwritten. They see the resulting value only.

## Pros and Cons of the Options

### The server's values always win

- Good: simplest rule.
- Bad: discards what the owner did offline, which is the case this library exists for.

### Write the phone's copy as a whole

- Good: one request.
- Bad: a change of the name on one phone undoes a change of a limit on the other, and a setting the phone does not know is deleted.

### Versions and refusal

- Good: nothing is ever overwritten unseen.
- Bad: `cloud-api` would have to offer conditional writes, and the owner would be asked about a conflict that one owner rarely has.
