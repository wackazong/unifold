---
status: proposed
date: 2026-10-06
---
# Define the BLE profile and the reading format once, in a unit of their own

## Context and Problem Statement

The firmware, the emulator, the phone app and the test rig all speak the same
radio protocol. The phone app and the server side exchange readings in one
format. If each part carried its own description, they would drift apart.

## Considered Options

- The firmware owns the protocol definition; the others follow it
- Each part documents the protocol as it understands it
- A separate unit owns both definitions; every part that uses one states it
  as a need

## Decision Outcome

Chosen option: "a separate unit", because no part then depends on another
part's documents, and a change has one place to start.

Both definitions carry a version. A change within a major version must keep
older counterparts working.

### Consequences

- Good: one text to review when the protocol changes.
- Good: the emulator and the firmware are judged against the same text.
- Bad: a protocol change touches the definition first and the
  implementations afterwards, in several steps.
- Bad: the definition is prose and tables. Nothing derives code from it in
  version 1.
