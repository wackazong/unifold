---
name: mobile-add-a-screen
description: Add a screen, or a new thing the owner can see or do, to the phone app. Use it when a feature needs a new screen or new data on an existing screen, before any work inside a single part of the app.
---

# Add a screen to the app

A new screen is finished when the owner can rely on it offline. The order below starts with the promise and the data, so that the screen itself is the last and smallest step.

## Steps

1. **State the promise.** Add a row to "What the owner can do" in [app-ui.md](../../references/app-ui.md): what the owner wants, and what the app guarantees. If you cannot write the guarantee without the words "when online", rethink the feature ([0001](../../decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)).
2. **Name the data.** Check the [data model](../../references/data-model.md). If the screen shows or changes something that is not there, add it with its origin and with who may change it. A new thing the owner may change offline needs a change state.
3. **Check the server.** If the data comes from the server or goes to it, check that the expectations under `cloud-api` in [README.md](../../../README.md) cover it. If they do not, the change is larger than this unit: change the need, tell the human, and stop here until whoever provides `cloud-api` offers it.
4. **Make the data available.** In [sync](../../../sync/README.md), check that the capability the screens read from offers the data and the commands. If not, extend it there first. Use that unit's own skills.
5. **If the screen needs the radio,** for example to show something about a paired sensor stick, extend [ble-client](../../../ble-client/README.md) in the same way. A screen never calls the radio for readings.
6. **Record the decision** if a capability changed and there was an alternative: a new record in [decisions](../../decisions/index.md) with status `proposed`.
7. **Build the screen.** In [ui](../../../ui/README.md), follow that unit's own skill for a screen.
8. **Check both platforms** on real phones, with the network switched off and with data that is a week old.
9. **Finish.** Run the generator and the checker of the project and review the files you changed.

## Checks

- The new row in [app-ui.md](../../references/app-ui.md) is true with the phone in flight mode.
- The screens gained no need through which data would reach them from the server or from a sensor stick.
- Every new thing in the data model has one origin.
- The checker reports no error and no new warning.

## Reference

- [app-ui.md](../../references/app-ui.md): the promises
- [data-model.md](../../references/data-model.md): the things the app handles
- [invariants.md](../../explanation/invariants.md): the invariants the new screen must keep
