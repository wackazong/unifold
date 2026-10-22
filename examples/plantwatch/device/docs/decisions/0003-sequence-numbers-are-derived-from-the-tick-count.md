---
status: proposed
date: 2026-10-06
---
# Sequence numbers are derived from the tick count

## Context and Problem Statement

Every reading needs a sequence number that rises strictly and is never
used twice in the life of a sensor stick, also after the cell was out. A
plain counter would have to be stored at every reading. The part that
makes readings has no durable memory; the part that has durable memory
receives a reading after it was made, at the same moment as the part that
shows it to a connected central. Where does the number come from?

## Considered Options

- The part that stores readings assigns the number when it stores
- The part that makes readings keeps a counter in durable memory of its
  own
- The number is computed from the tick count: boot counter and count of
  readings since that start

## Decision Outcome

Chosen option: "computed from the tick count", because the reading then
has its identity from the first moment and no additional durable state
exists.

```text
sequence number = boot counter × 262 144 + n
```

`n` is the count of readings since the start, beginning with 1. The boot
counter takes 14 bits, `n` takes 18 bits. The only durable state is the
boot counter, which exists anyway for the tick count.

### Consequences

- Good: a reading is numbered where it is made. Every receiver of it sees
  the same number, whether it stores the reading or shows it.
- Good: no write to durable memory per reading for the number.
- Good: the number survives the loss of all stored readings.
- Bad: sequence numbers jump at every start. Nobody can count readings by
  subtracting two numbers. The definition the firmware implements allows
  gaps; the firmware makes use of that.
- Bad: a sensor stick ends after 16 383 starts. A fault that restarts the
  board in a loop would use them up; the hardware layer must not start
  the board below the voltage at which it can run.
- Bad: one start carries at most 262 143 readings. At the shortest
  sampling interval that is 2.5 years, longer than any cell lasts.

## Pros and Cons of the Options

### Assigned when stored

- Good: consecutive numbers; the counter is recovered from the stored
  readings.
- Bad: a reading has no number until it is stored. A reading shown live
  would carry no identity, or the storing part would have to hand it
  back.
- Bad: after an overflow that discards everything, the highest number has
  to be kept elsewhere.

### A durable counter in the part that makes readings

- Good: consecutive numbers.
- Bad: a second user of durable memory, with its own wear and its own
  behaviour on power loss, for one number.
