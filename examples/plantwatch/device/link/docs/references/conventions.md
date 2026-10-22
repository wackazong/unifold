# Conventions of link

How work on the profile implementation is done. What must hold at every moment is in [invariants.md](../explanation/invariants.md).

- The BLE profile wins. If the code disagrees with it, the code is wrong. If the definition is unclear, do not settle the question here; the definition is not owned by this unit ([context](../explanation/context.md)).
- Bonded centrals remember attribute handles. Add a characteristic at the end of the service, never in the middle, and never reorder.
- Never compute a count from two sequence numbers. Ask `reading-log`.
