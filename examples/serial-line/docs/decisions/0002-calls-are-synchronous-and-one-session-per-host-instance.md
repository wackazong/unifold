---
status: proposed
date: 2026-10-27
---

# Calls are synchronous, and one host instance runs one session

## Context and Problem Statement

The sources say nothing about threads, callbacks or several sessions at once. The code needs a rule before the first contract is written.

## Considered Options

- Synchronous calls that block until the protocol step is done; one session per host instance
- Asynchronous calls with callbacks
- Several sessions multiplexed over one line

## Decision Outcome

Chosen option: "synchronous, one session", because the protocol itself is a strict request and answer on one line, and nothing in the sources asks for more.

### Consequences

- Good: every contract is a plain function; tests need no scheduler.
- Bad: a caller that wants two lines creates two host instances.
