---
status: proposed
date: 2026-10-06
---
# Upload in batches per sensor stick and retry with growing pauses

## Context and Problem Statement

Readings arrive in the store in bursts, up to 2 880 at once after a long
absence, and often while the phone has no network. They must reach the
server completely, soon enough for an alert to be useful, and without
draining the battery when the server or the network is unavailable. The
program may be suspended in the middle of a request. How does sync upload,
and what does it do after a failure?

## Decision Drivers

- No reading is dropped, whatever fails
- A request finishes within a short background slot
- A server that is down is not hit by every phone at once
- The owner who looks at the screen gets a fresh attempt at once

## Considered Options

- One request per reading
- One request with everything that is waiting
- Batches of bounded size per sensor stick, oldest first; after a failure,
  pauses that double up to a limit and end early when circumstances change

## Decision Outcome

Chosen option: "bounded batches per sensor stick with growing pauses",
because a bounded batch fits a short slot, a batch is by definition a
group of readings of one sensor stick ([context.md](../context.md)), and
growing pauses cost nothing while the phone is offline anyway.

sync marks a reading as confirmed only on the server's answer for that
reading. A batch without a complete answer is sent again unchanged; the
server accepts readings it already has. The values are in
[exchange.md](../references/exchange.md).

Within an exchange, waiting changes of plants go first and readings
directly after them. The server puts a reading into the history of the
plant its sensor stick is attached to when the reading arrives, so the binding
has to be there first. Everything the phone only downloads comes after the
readings, because only readings can lead to an alert. A batch the server
rejects as a whole is kept and tried again, because a reading is not
dropped on a doubt.

A pause ends early when the program comes onto the screen, when a network
connection appears, or on "refresh". These are the moments at which the
last failure says least about the next attempt.

### Consequences

- Good: an interrupted upload costs at most one batch of repeated transfer.
- Good: oldest first keeps the server's history without holes behind the
  newest reading, so an alert is not raised on a newer reading while older
  ones are still missing.
- Good: while the server is down, a phone sends at most one request an
  hour.
- Bad: after a long outage, readings can wait up to an hour longer than
  necessary on a phone nobody looks at.
- Bad: a backlog of several sensor sticks needs several requests in a row;
  the newest reading of the last sensor stick arrives last.
- Bad: a batch the server rejects as a whole is repeated forever. sync
  reports it in the exchange state; a human has to look.

## Pros and Cons of the Options

### One request per reading

- Good: simplest bookkeeping.
- Bad: 2 880 requests after a long absence; far beyond a background slot.

### One request with everything

- Good: fewest requests.
- Bad: a large request is the most likely to be cut off, and then nothing
  is confirmed.
