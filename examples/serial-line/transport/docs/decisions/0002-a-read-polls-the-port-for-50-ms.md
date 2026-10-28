---
status: proposed
date: 2026-10-27
---

# A read polls the port for 50 ms

## Context and Problem Statement

`receive` waits for a complete frame until a deadline. The port's `read` takes a timeout. The sources say nothing about how long one read may block.

## Considered Options

- One read with the whole remaining deadline
- Reads of `READ_POLL_MS` until the deadline

## Decision Outcome

Chosen option: "reads of 50 ms", because a read that blocks for the whole deadline cannot be stopped when a frame completes early from bytes already in the buffer, and 50 ms keeps the loop cheap.

### Consequences

- Good: `receive` returns within 50 ms of a complete frame.
- Bad: up to ten reads per `OPEN_TIMEOUT_MS`.
