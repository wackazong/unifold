---
unit: rules
summary: Evaluates readings against the thresholds of a plant
kind: library
status: planned
provides:
  evaluation:
    kind: library
    summary: Decides for a reading whether an alert opens, stays or closes
    contract: doc/references/evaluation.md
needs:
  thresholds:
    kind: http
    summary: The thresholds of the plant a reading belongs to
---
# rules

`rules` is a library that judges readings. Given one reading of a sensor
stick and what it concluded from the earlier readings of that sensor
stick, it says which alerts open and which close. It finds out the plant
and its thresholds itself. It stores nothing; what it must remember, it
returns to its caller.

## Provides

### `evaluation`

One function, `evaluate(reading, state)`. `reading` carries sensor id,
sequence number, time, the flag for an estimated time and the measured
values. `state` is the value that the previous call for the same sensor
stick returned, or nothing for the first call. The function returns the
plant of the reading, a list of changes ("open" or "close" an alert for a
quantity and a bound) and the new state. If it cannot get the thresholds
it returns "cannot decide now" and nothing else.

A caller can rely on this:

- **No flapping.** An alert opens when the judged value is beyond the
  threshold and closes only when it is back by a margin.
- **No second opening.** `evaluation` never returns "open" for a quantity
  and bound that are open according to `state`, and "close" only for one
  that is open.
- **Order is handled inside.** A reading that is not newer than the last
  judged one, and a reading with an estimated time, returns no changes
  and the unchanged state. A caller may pass a reading twice.
- **Deterministic.** The same reading, state and thresholds give the same
  result. `evaluation` uses no clock and no random value.
- **No side effects** apart from asking for thresholds.
- `state` is plain data of at most 4 kB that survives being written as
  JSON and read back.
- Thresholds are at most 60 seconds old when they are used.

Limits:

- The caller must hand back the state exactly as returned, per sensor
  stick, and must pass the readings of one sensor stick one after the
  other. `evaluation` cannot detect a state that belongs to another
  sensor stick.
- A lost state makes `evaluation` start afresh: an alert that was open
  can open again.

Example, with a lower threshold of 30.0 for soil moisture:

```text
evaluate({sensor 00a1b2c3d4e5f607, 14:15, soil_moisture 28.4}, state)
  -> plant "Monstera in the hall",
     [open soil_moisture/min, value 28.4, threshold 30.0],
     state'
evaluate({sensor 00a1b2c3d4e5f607, 14:30, soil_moisture 31.0}, state')
  -> plant "Monstera in the hall", [], state''     (inside the margin)
```

Contract: [evaluation](doc/references/evaluation.md).

## Needs

### `thresholds`

A lookup over HTTP by sensor id. `rules` expects the answer to name the
plant to which the sensor stick is attached, with plant id, owner id and
name, and to give its thresholds: per quantity a `min`, a `max` or both.
It expects a distinct answer when the sensor stick is attached to no
plant. It expects the current state, not a cached one, and an answer
within 5 seconds. JSON bodies and error bodies follow the conventions
cited in [doc/context.md](doc/context.md).

## Out of scope

- Storing anything, including its own state.
- Closing an alert because time has passed. `rules` acts only when it is
  given a reading.
- Telling anybody about an alert.
- Deciding what a good threshold is.

## More

- [AGENTS.md](AGENTS.md): why judging is a library without state
- [doc/context.md](doc/context.md): what the unit inherits
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- References: [evaluation](doc/references/evaluation.md)
