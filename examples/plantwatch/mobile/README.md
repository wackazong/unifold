---
unit: mobile
summary: Phone app that collects readings from sensor sticks, shows the plants and relays data to the server
kind: app
status: planned
provides:
  app-ui:
    kind: ui
    summary: Shows the state of each plant and tells the user when to water it
    contract: doc/references/app-ui.md
needs:
  sensor-link:
    kind: protocol
    summary: A sensor stick in radio range that serves its readings over BLE
  cloud-api:
    kind: http
    summary: Stores readings and returns plants, history and alerts
  link-profile:
    kind: specification
    summary: The definition of the BLE services of a sensor stick
  reading-format:
    kind: specification
    summary: The format in which readings are stored and uploaded
  push-service:
    kind: http
    summary: Registers this phone for the notifications of an owner and delivers them to it
wiring:
  app-ui: ui.app-ui
  ble-client.sensor-link: sensor-link
  ble-client.link-profile: link-profile
  sync.sensor-readings: ble-client.sensor-readings
  sync.cloud-api: cloud-api
  sync.reading-format: reading-format
  ui.plant-data: sync.plant-data
  ui.pairing: ble-client.pairing
  ui.push-service: push-service
---
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
- It shows all of this without a network connection, and it says how old the
  data is.
- It collects readings without being opened, as far as the phone's operating
  system lets an app run in the background. Opening the app near a paired
  sensor stick always starts a fetch.
- The owner pairs up to 20 sensor sticks and keeps up to 50 plants.
- A change to a plant that the owner makes without a network connection is
  kept and reaches the server later.
- The app shows alerts; it does not raise them. Tapping a notification opens
  the plant it is about.

Limits: background collection stops when the owner force-quits the app,
switches Bluetooth off or withdraws a permission. It resumes when the owner
opens the app again. A reading reaches the phone only while the phone is in
radio range of the sensor stick.

Example: the owner comes home after three days away. Without the phone being
touched, the readings of those three days arrive on it, usually within
minutes. As soon as the phone has a network connection they go on to the
server.

Contract: [app-ui](doc/references/app-ui.md).

## Needs

### `sensor-link`

A sensor stick in radio range that behaves as `link-profile` defines. The app
expects that it

- advertises, so that a central finds it without the owner doing anything,
- accepts pairing with this phone while it is open for pairing, and says in
  its advertising whether it is,
- serves its stored readings in ascending sequence number, each with its
  tick count, and tells its current tick count,
- keeps every reading until a central has confirmed it, and
- states the version of the radio protocol it speaks.

### `cloud-api`

The server. The app expects that it

- creates an owner on request and gives out a token that stands for this
  owner, and a further token for the same owner, so that a second phone can
  join,
- accepts batches of readings in the `reading-format`, accepts a batch that
  it has received before, and says for each reading whether it is accepted,
  known already or refused,
- returns the owner's plants, the history of a plant and the alerts,
- accepts a plant under an id the app has chosen, creating or replacing it,
  and removes a plant on request, and
- decides which alerts are open; the app takes them as they come.

### `link-profile`

The definition of the BLE services, characteristics and procedures of a
sensor stick: finding, pairing, fetching stored readings, confirming them,
reading the tick count. It carries a version. The app supports major
version 1.

### `reading-format`

The definition of the fields, units and identity of a reading as the app
stores and uploads it. It carries a version.

### `push-service`

The push service of the phone's platform. The app expects that it

- accepts the registration of this phone for one owner and tells the app
  when the phone's address has changed, so that the app can register again,
- delivers a notification that was sent to an owner to every phone
  registered for that owner, and
- hands a tapped notification to the app with the alert it belongs to.

The app works without it. Alerts then show only when the app is opened.

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
  [platform limits](doc/references/platform-limits.md)
