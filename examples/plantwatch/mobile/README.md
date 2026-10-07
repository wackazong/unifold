# mobile

mobile is the phone app. It collects readings from the owner's sensor sticks
whenever the phone is near them, keeps plants, history and alerts on the
phone, shows them to the owner, and passes the readings on to a server. It
runs on iOS and Android.

## Provides

### `app-ui`

The app as its owner sees it.

- For each plant it shows the latest reading, the history of the last 90
  days, and every open alert with its reason.
- It shows all of this without a network connection, together with the age
  of the readings and the time of the last exchange with the server.
- It collects readings without being opened, as far as the phone's operating
  system lets an app run in the background. When the owner opens the app
  near a paired sensor stick, a fetch starts within 5 seconds.
- The owner pairs up to 20 sensor sticks and keeps up to 50 plants.
- A change to a plant that the owner makes without a network connection
  shows within 1 second, marked "not yet sent", and goes to the server with
  the next exchange.
- The app shows alerts; it does not raise them. Tapping a notification opens
  the plant it is about.

Limits: background collection stops when the owner force-quits the app,
switches Bluetooth off or withdraws a permission. It resumes when the owner
opens the app again. A reading reaches the phone only while the phone is in
radio range of the sensor stick.

Example: the owner comes home after three days away. Without the phone being
touched, the operating system wakes the app and the 288 readings of those
three days arrive on the phone. They are in the history before any upload
and go to the server with the next network connection.

Contract: [app-ui](doc/references/app-ui.md), with example cases.

## Needs

The app defines none of these interfaces. It takes each as whoever provides
it defines it; the lists say what the app as a whole relies on.

### `sensor-link`

A sensor stick in radio range that behaves as `link-profile` defines. The
app relies on that it

- advertises whenever no central is connected and says there whether it is
  open for pairing, so that the phone finds it without the owner's help,
- keeps every reading until a central has confirmed it or, when its memory
  is full, discards the oldest and reports that it did, and serves the
  unconfirmed ones in ascending sequence number with their tick counts,
- tells its current tick count, its sampling interval and the version of
  the radio protocol it speaks, and
- accepts a connection as often as once per sampling interval.

### `cloud-api`

The server. The app relies on that it

- creates an owner on request and gives out a token for this owner, and a
  further token for the same owner, so that a second phone can join,
- accepts batches of up to 500 readings in the `reading-format`, also a
  batch it has received before, and answers for each reading whether it is
  new, known already or refused,
- returns the owner's plants, the history of a plant and the alerts,
- accepts a plant under an id the app has chosen, creating or replacing it,
  and removes a plant on request, and
- decides which alerts are open; the app takes them as they come.

### `link-profile`

The definition of the BLE services, characteristics and procedures of a
sensor stick: finding, pairing, fetching stored readings, confirming them,
reading the tick count. It carries a version. The app implements the
central side of major version 1.

### `reading-format`

The definition of the fields, units and identity of a reading as the app
stores and uploads it. It carries a version. The app writes and reads major
version 1.

### `push-service`

The push service of the phone's platform. The app relies on that it

- registers this phone for the notifications of one owner, ends the
  registration on request, and tells the app when the phone's address has
  changed, so that the app registers again, and
- delivers a notification that was sent to that owner to this phone,
  together with the ids of the alert and of its plant that the sender
  attached.

The app does not depend on delivery. Every alert that a notification
announces is on the screens after the next exchange with the server.

## Out of scope

- Deciding whether a plant needs attention. The app shows the alerts it
  receives through `cloud-api`.
- Delivering and displaying notifications. Whoever provides `push-service`
  delivers them and the operating system shows them.
- Accounts with passwords. An owner is whoever holds a token of that owner;
  a second phone joins through a code shown on the first.
- History older than 90 days.
- Updating the software of a sensor stick.
- Layouts for tablets, watches or desktop computers.

## More

- [AGENTS.md](AGENTS.md): why the app is cut this way
- [doc/context.md](doc/context.md): what the app inherits from above
- [doc/architecture.md](doc/architecture.md): invariants and behaviour over
  time
- [Context diagram](doc/diagrams/context.md),
  [component diagram](doc/diagrams/component.md),
  [architecture diagram](doc/diagrams/architecture.md)
- [Decisions](doc/decisions/index.md)
- References: [what the owner can do](doc/references/app-ui.md),
  [data model](doc/references/data-model.md),
  [platform limits](doc/references/platform-limits.md),
  [glossary](doc/references/glossary.md)
