# mobile

`mobile` is the phone app. It collects readings from the owner's sensor sticks whenever the phone is near them, keeps plants, history and alerts on the phone, shows them to the owner, and passes the readings on to a server. It runs on iOS and Android.

## Why

The app exists because a sensor stick reaches nothing but a phone: the app carries its readings on and is the owner's window on their plants. It changes when what the owner can see or do on the phone changes, or when iOS or Android change what an app may do in the background.

It does three jobs that run at different moments and fail for different reasons. The radio works only while a sensor stick is near and the operating system lets the app run. The exchange with the server works only while there is a network. The screens work whenever the owner looks. The app is cut along these three rhythms, so that each job runs, fails and is tested without the other two.

The main trade-off: everything the owner sees comes from a store on the phone, never straight from the radio or the network ([0001](docs/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)). The screens are fast and work offline. The price is a second copy of the server's data, and rules for the case that the two copies differ.

What must stay true: a reading is stored on the phone before the sensor stick is told to forget it, and it stays there until the server has it.

## Capabilities

### `app-ui`

In the background the app fetches each sensor stick at most 4 times a day. After a force-quit, with Bluetooth off or without a permission, background collection resumes when the owner opens the app again.

## Needs

### `push-service`

The app does not depend on delivery. Every alert that a notification announces is on the screens after the next exchange with the server.

## Out of scope

- Deciding whether a plant needs attention. The app shows the alerts it receives through `cloud-api`.
- Delivering and displaying notifications. Whoever provides `push-service` delivers them and the operating system shows them.
- Accounts with passwords. An owner is whoever holds a token of that owner; a second phone joins through a code shown on the first.
- History older than 90 days.
- Updating the software of a sensor stick.
- Layouts for tablets, watches or desktop computers.

## Read next

1. [docs/tutorials/first-plant.md](docs/tutorials/first-plant.md): for an owner with a new sensor stick, up to the first reading on the screen
2. [docs/explanation/reasoning.md](docs/explanation/reasoning.md): why the app is cut this way
3. [docs/explanation/invariants.md](docs/explanation/invariants.md): what holds at every moment
4. [docs/explanation/runtime.md](docs/explanation/runtime.md): background fetching, the way of a reading through the app
5. [docs/references/data-model.md](docs/references/data-model.md): the things the app handles and who may change them
6. [docs/references/platform-limits.md](docs/references/platform-limits.md): what iOS and Android allow in the background
7. [app-ui.md of plantwatch](../docs/references/app-ui.md): what the owner can rely on
8. [docs/references/glossary.md](docs/references/glossary.md): the app's own terms
9. [docs/explanation/context.md](docs/explanation/context.md): what the app inherits from above
10. [Context diagram](docs/diagrams/context.md), [component diagram](docs/diagrams/component.md)
11. [Decisions](docs/decisions/index.md)
