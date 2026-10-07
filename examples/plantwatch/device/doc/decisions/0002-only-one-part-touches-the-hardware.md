---
status: proposed
date: 2026-10-06
---
# Only one part of the firmware touches the hardware

## Context and Problem Statement

The firmware reads two sensors, writes flash memory, runs a radio and
keeps time while it sleeps. Each of these needs registers, pins and, for
the radio and the flash, the vendor's radio stack. Most of the firmware's
logic has nothing to do with hardware: calibration, a log that survives
power loss, the state machine of a BLE profile. Faults in that logic are
costly to find on a board that sleeps 99 % of the time. Where does
hardware access live?

## Considered Options

- Each part drives the hardware it needs: the measuring part the
  converter, the memory part the flash controller, the profile part the
  radio stack
- One part owns all hardware access and offers it as libraries without
  hardware types
- A real-time operating system with its driver model

## Decision Outcome

Chosen option: "one part owns all hardware access", because every other
part can then be built and tested on a development machine, and the
power state of the board has a single owner. The part is
[hal](../../hal/README.md).

### Consequences

- Good: calibration, memory layout and profile are tested without a
  board, including power loss at every write.
- Good: no two parts can disagree about whether the board may sleep.
- Good: a new board revision changes one part.
- Bad: the interface of that part has to be designed, and it can be
  wrong: too low and hardware leaks upward, too high and logic sinks into
  the part that cannot be tested on a development machine.
- Bad: a test with substitutes says nothing about timing and current.
  Those are measured on a board
  ([device-check-the-energy-budget](../skills/device-check-the-energy-budget/SKILL.md)).

## Pros and Cons of the Options

### Each part drives its hardware

- Good: no extra layer.
- Bad: every part needs a board to run. The radio stack's rules on when
  flash may be written leak into the memory part.

### Real-time operating system

- Good: drivers and scheduling exist.
- Bad: its idle and tick behaviour has to be tuned to reach 2 µA, and the
  firmware has no concurrent tasks that would need a scheduler.
