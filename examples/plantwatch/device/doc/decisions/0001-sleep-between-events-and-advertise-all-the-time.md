---
status: proposed
date: 2026-10-06
---
# Sleep between events and advertise all the time at a long interval

## Context and Problem Statement

The cell allows an average of 19.4 µA. A central comes into range at
times the firmware cannot know, and it has to find the sensor stick while
it is there, possibly for less than a minute and with a radio that scans
only now and then. Advertising is what makes the sensor stick findable,
and it is also the activity that repeats most often. When does the
firmware advertise, and what does it do in between?

## Decision Drivers

- The average current stays within the
  [energy budget](../references/energy-budget.md).
- A central in range finds the sensor stick within seconds, at any time
  of the day.
- A person who stands next to the plant with a central gets a connection
  without touching the sensor stick.

## Considered Options

- Advertise only in a window of 10 s after each reading
- Advertise only while unconfirmed readings wait
- Advertise all the time at a short interval of 100 ms to 250 ms
- Advertise all the time at a long interval of 1285 ms

## Decision Outcome

Chosen option: "advertise all the time at 1285 ms", because it is the
only option that is findable at any moment and still fits the budget.

Between events the firmware sleeps. It has no loop that waits. Every
activity is a reaction to a timer or to the radio and ends by returning.
A connection that carries no request is closed after 30 s, and every
connection after 10 minutes.

1285 ms is one of the advertising intervals that makers of common
centrals recommend to accessories that want to be found by a central that
scans only now and then to save its own energy.

### Consequences

- Good: a central that scans continuously sees the sensor stick within
  about 3 s.
- Good: no button, no user action to wake the sensor stick.
- Bad: advertising takes 9.3 µA, three quarters of the planned
  consumption. It is the first place to look when the cell life is short.
- Bad: a central that scans in short bursts needs several of them to hit
  an advertising event.
- Bad: with no loop, every sequence that spans time is a state machine.

## Pros and Cons of the Options

### Window after each reading

- Good: about 0.1 µA for advertising.
- Bad: findable for 10 s in 15 minutes. A central that passes by misses
  the sensor stick most of the time.

### Only while readings wait

- Good: no advertising after a fetch until the next reading.
- Bad: saves at most one sampling interval in which nothing waits, that
  is almost nothing.
- Bad: no live readings when nothing is stored.

### Short interval

- Good: found within a fraction of a second.
- Bad: 48 µA to 120 µA. The cell lasts two to five months.
