# Invariants of rules

What is true of `evaluate` at every moment. These lines keep the judging
logic testable with a table of readings.

- The function is deterministic, and it never asks to open what is open.
- There is no clock. "Now" does not exist in this unit; the only times are
  those of readings. A rule that needs the current time belongs to the
  caller.
- There is no storage, no global and no network. Nothing is remembered
  between two calls, not even an answer of `thresholds`.
