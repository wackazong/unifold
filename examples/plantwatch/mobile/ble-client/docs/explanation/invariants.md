# Invariants of ble-client

What is true of the client at every moment. These lines keep a reading on the sensor stick until the consumer has it, and the client small.

- The order "deliver, wait for the acknowledgement, confirm" holds for every reading. It is not an optimisation target; the client never confirms early to save a round trip.
- Platform code implements one common interface. A capability that only one platform has is not part of a provided capability.
- A background slot is short ([context.md](context.md)). Work that is not needed to fetch, deliver and confirm does not run in it.
- The client's own state is the pairings and the time anchors ([0002](../decisions/0002-keep-a-time-anchor-per-boot.md)), and nothing more. There is no cache of readings.
