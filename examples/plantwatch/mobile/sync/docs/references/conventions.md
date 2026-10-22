# Conventions of sync

How work on the store and the exchange is done. What must hold at every moment is in [invariants.md](../explanation/invariants.md).

- A change to the layout of the store ships with a migration from every released layout. A phone may skip versions; a migration that loses readings the server has not confirmed is a defect, not a trade-off.
- Field names in requests and stored documents come from the reading schema and from `cloud-api`. Do not restate them in the documents of this unit.
- The pauses and sizes in [exchange.md](exchange.md) protect the phone's battery and the server. Change them there first, with a reason, and then in code.
