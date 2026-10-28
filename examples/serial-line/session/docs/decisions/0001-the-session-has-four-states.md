---
status: derived
date: 2026-10-27
derived-from: proto §5.4, Table 5
---

# The session has four states

## Source says

Proto §5.4, Table 5: the host side is closed, opening, open or closing. Closed is entered at start, after a close completes and after an open fails. Opening is entered when OPEN was sent and left when the ACK arrives or 500 ms pass. Open is entered when the ACK of OPEN arrived and left when the caller closes. Closing is entered when CLOSE was sent and left when the ACK arrives or 500 ms pass. A caller that opens while not closed, or sends while not open, has made an error; the host reports it and changes no state.

## Context and Problem Statement

The unit needs a state machine; the source gives one.

## Decision Outcome

Chosen option: "the four states of Table 5, as written", because the source settles it. The table in `docs/explanation/runtime.md` is a restatement for the code.

### Consequences

- Good: every transition has a test named after a row of the table.
- Bad: none.
