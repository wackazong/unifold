---
name: sync-change-the-local-store
description: Change what the local store of sync keeps or how it keeps it, with a migration that loses nothing. Use it when a field, a kept thing, a state or a retention rule of the store on the phone shall change.
---

# Change the local store

The store on a phone holds readings that exist nowhere else until the server has confirmed them. The result of this procedure is a new layout version that every phone in use reaches without losing one of them.

## Steps

1. **Describe the change in the reference first.** Edit [local-store.md](../../references/local-store.md): the table "What is kept", the state diagram or the retention table. If the change adds a state, say for every state when a thing enters and leaves it.
2. **Check where the fact belongs.** If the change adds a field that readers of the data see, it is part of the data model cited in [context.md](../../explanation/context.md) and of [plant-data.md](../../../../docs/references/plant-data.md). A field of the data model is not decided in this unit: stop and tell the human. A field only the store needs stays here.
3. **Check the size.** Recompute the table "Size" in [local-store.md](../../references/local-store.md) for the upper bound.
4. **Raise the layout version** by one and write the migration from the previous version. A migration
   - runs in one transaction, so a phone that is switched off in the middle starts it again from the old layout,
   - never deletes a reading in the state `fetched`,
   - never deletes a waiting change of a plant,
   - computes new fields from existing data or leaves them absent; it does not ask the server.
5. **Test the migration chain.** For every layout version that was ever released, start from a store of that version, filled to the upper bound and containing `fetched` readings and waiting changes, and migrate to the new version. Compare the number of `fetched` readings and waiting changes before and after.
6. **Test the time.** Measure the migration of a full store on the slowest supported phone. A migration runs before the first query is answered and also when the program was started in the background; if it takes longer than a few seconds, split the work so that the store answers queries while the rest follows.
7. **Change the exchange if needed.** If the new field travels to or from the server, update [exchange.md](../../references/exchange.md) and check the expectations under `cloud-api` in [README.md](../../../README.md).
8. **Record a decision** in [decisions](../../decisions/index.md) with status `proposed` if the change had an alternative, for example a different retention.
9. **Finish.** Run the generator and the checker of the project and review the files you changed.

## Checks

- A store of every released layout version opens with the new version.
- No migration test lost a `fetched` reading or a waiting change.
- A store written by the new version is refused by the previous version with `store unusable` instead of being read wrongly.
- [local-store.md](../../references/local-store.md) describes the new layout and nothing of the old one.

## Reference

- [local-store.md](../../references/local-store.md)
- [plant-data.md](../../../../docs/references/plant-data.md)
- [exchange.md](../../references/exchange.md)
