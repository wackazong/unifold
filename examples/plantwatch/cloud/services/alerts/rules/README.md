# rules

`rules` is a library that judges readings. Given one reading of a sensor stick and what it concluded from the earlier readings of that sensor stick, it says which alerts open and which close. It asks for the plant and its thresholds through a function it is given. It stores nothing; what it must remember, it returns to its caller.

## Why

When an alert opens and closes is the part of the product that owners feel and that changes most. This unit holds exactly that logic and nothing else, so that it can be read in one sitting and tested with a table of readings and expected alerts. It changes when the rules of judging change: a new quantity, a different margin, another way to look at light.

To stay testable it has no state and knows no technology. What it concluded from earlier readings travels in a value that the caller keeps. Plant and thresholds come through a need that it states in its own words; a test meets that need with a table ([context](docs/explanation/context.md)).

An alert must not flap when a value hovers at its threshold, and it must not wait when a plant runs dry. Both are met by opening at the threshold and closing only beyond a margin
([0001](docs/decisions/0001-flapping-is-prevented-by-a-margin-on-closing.md)).

Light shows why judging needs memory: a reading at night is dark for every plant, so light is judged by the brightest reading of a day.

What must stay true: the function is deterministic, and it never asks to open what is open.

## Capabilities

### `evaluation`

One function, `evaluate(reading, state)`. `reading` carries sensor id, sequence number, time, the flag for an estimated time and the measured values. `state` is the value that the previous call for the same sensor stick returned, or nothing for the first call. The function returns the plant of the reading, a list of changes ("open" or "close" an alert for a quantity and a bound) and the new state. If `thresholds` answers `unavailable`, it returns "cannot decide now" and nothing else.

A caller can rely on this:

- **No flapping.** An alert opens when the judged value is beyond the threshold and closes as recovered only when it is back by a margin: 5.0 percent soil moisture, 1.0 °C, or 10 percent of a light threshold and at least 50 lux.
- **No second opening.** `evaluation` never returns "open" for a quantity and bound that are open according to `state`, and "close" only for one that is open.
- **Order is handled inside.** A reading that is not newer than the last judged one, and a reading with an estimated time, returns no changes and the unchanged state. A caller may pass a reading twice.
- **Deterministic.** The same reading, the same state and the same answer of `thresholds` give the same result. `evaluation` uses no clock, no random value and no memory between calls.
- **No side effects.** It calls `thresholds` at most once per reading and does nothing else outside its return value.
- **Bounded time.** It returns within 10 ms plus the time `thresholds` takes, that is within 19 seconds.
- `state` is plain data of at most 4 kB that survives being written as JSON and read back.

Limits:

- The caller must hand back the state exactly as returned, per sensor stick, and must pass the readings of one sensor stick one after the other. `evaluation` cannot detect a state that belongs to another sensor stick.
- A lost state makes `evaluation` start afresh: an alert that was open can open again.

Example, with a lower threshold of 30.0 for soil moisture:

```text
evaluate({sensor 00a1b2c3d4e5f607, 14:15, soil_moisture 28.4}, state)
  -> plant "Monstera in the hall",
     [open soil_moisture/min, value 28.4, threshold 30.0],
     state'
evaluate({sensor 00a1b2c3d4e5f607, 14:30, soil_moisture 31.0}, state')
  -> plant "Monstera in the hall", [], state''     (inside the margin)
```

Contract: [evaluation](../docs/references/evaluation.md).

## Needs

### `thresholds`

A function `lookup(sensor_id)` with three answers. `attached` names the plant to which the sensor stick is attached, with plant id, owner id and name, and gives its thresholds: per quantity a `min`, a `max` or both. `unattached` says that the sensor stick is attached to no plant. `unavailable` says that no answer can be had now.

`rules` expects an answer that is at most 60 seconds old, within 18 seconds, and never an error. Where the answer comes from is not its business.

Contract:
[thresholds lookup as rules expects it](../docs/references/thresholds.md).

## Out of scope

- Storing anything, including its own state.
- Closing an alert because time has passed. `rules` acts only when it is given a reading.
- Telling anybody about an alert.
- Deciding what a good threshold is.
- Fetching thresholds over a network, repeating a failed lookup or keeping an answer. That is the part of whoever provides `thresholds`.

## Read next

1. [docs/references/evaluation.md](../docs/references/evaluation.md): the function, the rules, the margins, the state
2. [docs/references/thresholds.md](../docs/references/thresholds.md): the lookup that the unit expects to be given
3. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
4. [Context diagram](docs/diagrams/context.md),
   [decisions](docs/decisions/index.md)
