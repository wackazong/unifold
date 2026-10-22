---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The emulator implements the profile independently of the firmware

## Context and Problem Statement

A simulated sensor stick is needed to develop the phone app and to run end-to-end tests without hardware. It could reuse the firmware's upper layers on top of a simulated board, or it could be written separately.

## Considered Options

- Build the firmware for the desktop with a simulated hardware layer
- Write the emulator separately, from the protocol definition alone

## Decision Outcome

Chosen option: "write it separately", because two implementations made from the same text reveal where the text is ambiguous, and the emulator stays usable when the firmware is broken.

### Consequences

- Good: the emulator can be finished before the firmware.
- Good: a difference in behaviour between the two points to a gap in the protocol definition or a fault in one of them.
- Bad: every protocol change is implemented twice.
- Bad: the emulator says nothing about firmware-only behaviour such as energy use, flash wear or timing on the real radio.
