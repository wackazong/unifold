---
status: proposed
date: 2026-10-06
---
# Sleep with the low-frequency clock running and never switch the system off

## Context and Problem Statement

Between two events the board has nothing to do, for seconds or for
minutes. The microcontroller has two ways to wait: a sleep in which a
low-frequency clock and a counter keep running, at about 2 µA, and a
switched-off state at about 0.3 µA from which only a pin or a reset wakes
it and after which the program starts from the beginning. `timer` has to
count seconds without interruption, and `radio` has to advertise every one
to two seconds. Which state does `hal` use?

## Considered Options

- Switch the system off between readings; wake it with an external
  low-power timer chip
- Sleep with the low-frequency crystal and the real-time counter running
- Sleep with the internal RC oscillator instead of the crystal

## Decision Outcome

Chosen option: "sleep with the low-frequency crystal and the real-time
counter running", because the seconds since start then come from one
counter that never stops, and the radio stack needs the same clock for
advertising anyway.

### Consequences

- Good: the tick count is continuous. A wake-up is not a start, so the
  boot counter rises only on a real start.
- Good: no extra timer chip on the board.
- Good: the crystal keeps the error of the seconds below 50 ppm, about
  2 minutes in 30 days.
- Bad: 2 µA flow all the time. That is a tenth of the average current the
  board may draw.
- Bad: RAM content is kept, so a fault in RAM lasts until the next start.
  `hal` has to restart the board deliberately on a failed self-check.

## Pros and Cons of the Options

### Switch off, external timer

- Good: lowest current between readings.
- Bad: advertising every 1 to 2 seconds makes the saving void; the board
  would be woken all the time.
- Bad: every wake-up is a start. Seconds since start would have to be
  reconstructed from the external chip.

### Internal RC oscillator

- Good: one crystal less.
- Bad: an error of 500 ppm after calibration, 20 minutes in 30 days, and
  the calibration itself costs energy.
