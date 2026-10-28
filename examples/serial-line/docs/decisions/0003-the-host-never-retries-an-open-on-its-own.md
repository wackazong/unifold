---
status: derived
date: 2026-10-27
derived-from: proto §5.1
---

# The host never retries an open on its own

## Source says

Proto §5.1: when no ACK arrives within 500 ms of sending OPEN, the open has failed and the host reports this to its caller. "The host does not send OPEN again on its own."

## Context and Problem Statement

A failed open could be retried inside the host, which would hide line glitches from the caller.

## Decision Outcome

Chosen option: "report, never retry", because the source settles it. `open` returns `timeout` and the caller decides.

### Consequences

- Good: a test of `open` needs no retry logic, and the state after a failure is always closed.
- Bad: a caller that wants retries writes them.
