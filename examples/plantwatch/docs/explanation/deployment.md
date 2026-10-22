# Deployment of plantwatch

Where each part runs and how it is released; the folder tree cannot say this.

| Part | Runs on | Released as |
|---|---|---|
| [device](../../device/README.md) | The sensor stick's microcontroller | Firmware image, updated by hand in version 1 |
| [mobile](../../mobile/README.md) | The user's phone | App store release |
| [cloud](../../cloud/README.md) | A container host | Container images |
| [emulator](../../emulator/README.md) | A developer machine or CI runner | Not released |
| [test-rig](../../test-rig/README.md) | A developer machine or CI runner, optionally next to real hardware | Not released |

Consequences:

- The three released parts have three release rhythms. Within one major version of the radio protocol a newer part works with an older one ([invariants](invariants.md)), so they need not be released together. The protocol itself is not deployed: it is a reference of this unit, versioned with it.
- A firmware image reaches a sensor stick only by hand. A fault in it is corrected one stick at a time ([risks](risks.md)).
