# Invariants of store

What is true of the log at every moment. These lines keep recovery possible after any power loss.

- There are two erase paths: the oldest ring block when the ring needs room, and the idle journal block when the journal is full. There is no third.
- The journal entry is written first, then the state in RAM changes, then the call returns. Never the other way round.
- The slot layout resembles other encodings of a reading by coincidence. It is private; no slot leaves `store` as bytes.
