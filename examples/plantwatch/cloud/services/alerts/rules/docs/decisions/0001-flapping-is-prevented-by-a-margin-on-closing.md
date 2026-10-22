---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Flapping is prevented by a margin on closing, not by counting readings

## Context and Problem Statement

A measured value that hovers around a threshold crosses it again and again. Without care, every crossing would open or close an alert, and every opening would notify the owner. `rules` must keep an alert steady. At the same time the first sign of a dry plant shall lead to an alert at once, and readings arrive anything from 5 to 60 minutes apart.

## Considered Options

- No damping: open and close exactly at the threshold
- Counting: open only after several readings in a row beyond the threshold, close after several on the good side
- A margin on closing: open at the threshold, close only when the value is back beyond the threshold by a fixed margin
- Both counting and a margin

## Decision Outcome

Chosen option: "a margin on closing", because it keeps an alert steady without delaying its opening, and it does not depend on how often a sensor stick measures.

The margins are fixed per quantity and listed in [evaluation](../../../docs/references/evaluation.md). A margin is several times the resolution of its quantity, so that noise of the sensor does not cross it.

### Consequences

- Good: the first reading beyond a threshold opens the alert. Nothing waits for a second reading, which could be an hour away.
- Good: one number per quantity, easy to state and to test.
- Good: the state stays small: no counters.
- Bad: a single wrong reading opens an alert and notifies the owner.
- Bad: a value that settles inside the margin keeps the alert open although the plant is back above its threshold.
- Bad: the margins are the same for every plant. A plant with a threshold close to the end of the range may never reach the closing value; its alert then ends only when the threshold is changed.

## Pros and Cons of the Options

### No damping

- Good: nothing to explain.
- Bad: a value at the threshold produces an alert and a notification per crossing.

### Counting

- Good: a single wrong reading has no effect.
- Bad: the delay depends on the sampling interval: three readings are 15 minutes for one sensor stick and 3 hours for another.
- Bad: readings arrive in batches and with gaps, so "in a row" needs a definition of its own.

### Both

- Good: steady and robust against single wrong readings.
- Bad: two mechanisms to explain, and the delay of counting remains.
