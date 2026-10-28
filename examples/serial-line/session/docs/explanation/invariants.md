# Invariants of session

What is true of the session at every moment.

- The state is one of closed, opening, open, closing, and only a transition of `runtime.md` changes it.
- No payload is sent in the state closed except `OP_OPEN`, and none in the state open except `OP_DATA` and `OP_CLOSE`.
- The unit never sleeps; every wait is a `receive` with a deadline computed from the clock.
