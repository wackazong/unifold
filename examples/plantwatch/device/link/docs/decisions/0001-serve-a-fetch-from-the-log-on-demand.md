---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Serve a fetch from the log on demand, paced by the radio

## Context and Problem Statement

A fetch can cover up to several thousand readings. The radio sends a few packets per connection event and then has no room until the next one. Stored readings come from `reading-log` one at a time, each within milliseconds. The board has 64 kB of RAM for everything. How does `link` get the readings from the log to the radio?

## Considered Options

- Copy all requested readings into a buffer in RAM, then send from the buffer
- A queue between log and radio that a separate step keeps filled
- Take one notification's worth of readings from the log each time the radio reports room

## Decision Outcome

Chosen option: "take one notification's worth each time the radio reports room", because `link` then needs a position in the log and nothing else.

The state of a running fetch is: the next sequence number to read, the number of records sent, the last sequence number sent, the limit. A connection that breaks takes this state with it.

### Consequences

- Good: RAM use is one notification, whatever the size of the fetch.
- Good: nothing in `link` can disagree with the log. What is sent is what the log returns at that moment.
- Good: a reading that arrives during a fetch is simply found when the position reaches it.
- Bad: the speed of a fetch depends on how fast `reading-log` answers. A slow read lowers the throughput directly.
- Bad: the log can change during a fetch, by overflow. `link` then sees a jump in the sequence numbers and sends on from the oldest stored reading.
