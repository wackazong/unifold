# Invariants of sync

What is true of the store and the exchange at every moment. These lines
keep a reader of the store unaware of the network.

- A batch is acknowledged after the write to the store has reached durable
  storage, not after it has been queued.
- sync computes no alert and no "needs water" state, not even as a
  preview. The reason is cited in [context.md](context.md).
- No query touches the network, and no query waits for a running exchange.
