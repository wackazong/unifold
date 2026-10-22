# mobile

`mobile` is the phone app. It collects readings from the owner's sensor sticks whenever the phone is near them, keeps plants, history and alerts on the phone, shows them to the owner, and passes the readings on to a server. It runs on iOS and Android.

## Why

The app exists because a sensor stick reaches nothing but a phone: the app carries its readings on and is the owner's window on their plants. It changes when what the owner can see or do on the phone changes, or when iOS or Android change what an app may do in the background.

It does three jobs that run at different moments and fail for different reasons. The radio works only while a sensor stick is near and the operating system lets the app run. The exchange with the server works only while there is a network. The screens work whenever the owner looks. The app is cut along these three rhythms, so that each job runs, fails and is tested without the other two.

The main trade-off: everything the owner sees comes from a store on the phone, never straight from the radio or the network ([0001](docs/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)). The screens are fast and work offline. The price is a second copy of the server's data, and rules for the case that the two copies differ.

What must stay true: a reading is stored on the phone before the sensor stick is told to forget it, and it stays there until the server has it.

## Capabilities

### `app-ui`

The app as its owner sees it.

- For each plant it shows the latest reading, the history of the last 90 days, and every open alert with its reason.
- It shows all of this without a network connection, together with the age of the readings and the time of the last exchange with the server.
- It collects readings without being opened, at most 4 times a day per sensor stick, as far as the phone's operating system lets an app run in the background. When the owner opens the app near a paired sensor stick, a fetch starts within 5 seconds.
- The owner pairs up to 20 sensor sticks and keeps up to 50 plants.
- A change to a plant that the owner makes without a network connection shows within 1 second, marked "not yet sent", and goes to the server with the next exchange.
- The app shows alerts; it does not raise them. Tapping a notification opens the plant it is about.

Limits: background collection stops when the owner force-quits the app, switches Bluetooth off or withdraws a permission. It resumes when the owner opens the app again. A reading reaches the phone only while the phone is in radio range of the sensor stick.

Example: the owner comes home after three days away. Without the phone being touched, the operating system wakes the app and the 288 readings of those three days arrive on the phone. They are in the history before any upload and go to the server with the next network connection.

Contract: [app-ui](docs/references/app-ui.md), with example cases.

## Needs

Each need names the same contract as its provider; the lists say what the app as a whole relies on.

### `sensor-link`

A sensor stick in radio range that behaves as the BLE profile defines. The app relies on that it

- advertises whenever no central is connected and says there whether it is open for pairing, so that the phone finds it without the owner's help,
- keeps every reading until a central has confirmed it or, when its memory is full, discards the oldest and reports that it did, and serves the unconfirmed ones in ascending sequence number with their tick counts,
- tells its current tick count, its sampling interval and the version of the radio protocol it speaks, and
- accepts a connection up to 4 times a day in the background, and whenever the owner opens the app near it.

### `cloud-api`

The server. The app relies on that it

- creates an owner on request and gives out a token for this owner, and a further token for the same owner, so that a second phone can join,
- accepts batches of up to 500 readings in the reading schema, also a batch it has received before, and answers for each reading whether it is new, known already or refused,
- returns the owner's plants, the history of a plant and the alerts,
- accepts a plant under an id the app has chosen, creating or replacing it, and removes a plant on request, and
- decides which alerts are open; the app takes them as they come.

### `push-service`

The push service of the phone's platform. The app relies on that it

- registers this phone for the notifications of one owner, ends the registration on request, and tells the app when the phone's address has changed, so that the app registers again, and
- delivers a notification that was sent to that owner to this phone, together with the ids of the alert and of its plant that the sender attached.

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
7. [docs/references/app-ui.md](docs/references/app-ui.md): what the owner can rely on
8. [docs/references/glossary.md](docs/references/glossary.md): the app's own terms
9. [docs/explanation/context.md](docs/explanation/context.md): what the app inherits from above
10. [Context diagram](docs/diagrams/context.md), [component diagram](docs/diagrams/component.md)
11. [Decisions](docs/decisions/index.md)
