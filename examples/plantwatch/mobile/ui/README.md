---
unit: ui
summary: Screens of the phone app
kind: library
status: planned
provides:
  app-ui:
    kind: ui
    summary: Shows the state of each plant and tells the user when to water it
    contract: doc/references/app-ui.md
needs:
  plant-data:
    kind: library
    summary: Plants, history and alerts, readable offline and updated when they change
  pairing:
    kind: library
    summary: Finds a new sensor stick nearby and binds it to this phone
  push-service:
    kind: http
    summary: Registers this phone for the notifications of an owner and delivers them to it
---
# ui

ui is everything the owner sees and touches on the phone: the list of
plants, the state and history of one plant, the forms for a plant and its
thresholds, and the steps that put a sensor stick to a plant. It shows what
it is given and passes on what the owner does. It holds no data of its own.

## Provides

### `app-ui`

The screens, in English and German, in portrait orientation.

- The first screen is the list of plants. Plants with an open alert come
  first and show the reason, for example "needs water", "needs more light"
  or "needs a warmer place".
- A plant's screen shows the latest reading, the open alerts and the
  history of up to 90 days as a chart.
- Every screen shows what the phone holds, at once. No screen shows a
  loading state for data that is on the phone.
- Every screen that shows readings or alerts says how old they are, and
  says so more prominently when they are older than a day.
- A change the owner makes is visible at once and carries a mark until it
  is confirmed. A refused change is shown with the reason.
- A reading whose time is estimated is shown with "about" before the time.
- No state is shown by colour alone. Every control has a label for screen
  readers. Text follows the text size of the system.
- A tap on a notification leads to the plant it is about.
- The screens ask for no account. A second phone joins by scanning a code
  that the first phone shows.

Limits: the screens show an alert only when `plant-data` contains one; a
low value in the history is not marked as a problem by itself. Temperatures
are shown in degrees Celsius only.

Example: the owner taps "Monstera" in the list. The plant's screen shows
"Soil moisture 23 %, 2 hours ago", the alert "Needs water since Tuesday",
and the chart of the last week.

Contract: [app-ui](doc/references/app-ui.md).

## Needs

### `plant-data`

The owner's plants, history and alerts, and the commands that change a
plant. ui expects that

- every query answers at once from data on the phone, with or without a
  network connection,
- a query can be observed, so that a screen changes when the data changes,
- the list of plants comes with the newest reading, the open alerts and the
  age of the readings of each plant,
- the history of a plant is available by hour and by day with minimum, mean
  and maximum, so that a chart of 90 days needs no arithmetic on the screen,
- a command takes effect at once, and each plant says whether a change is
  waiting or was refused, and why,
- it reports when data was last exchanged with the server and whether the
  phone has lost its access to the owner's data,
- it starts without an account, gives out a token for another phone, takes
  such a token to join an owner, and lets the phone leave its owner, and
- it offers a way to ask for fresh data now.

### `pairing`

A way to find and bind a sensor stick. ui expects that it

- lists the sensor sticks in range that can be paired, with a signal
  strength, nearest first, while a search runs,
- pairs one of them and answers `paired` or a reason the owner can act on,
- lists the paired sensor sticks with the time of their last fetch, and
- unpairs one.

### `push-service`

The push service of the phone's platform. ui expects that it

- registers this phone for the owner once the owner has allowed
  notifications, and reports when the phone's address has changed,
- delivers a notification sent to that owner to this phone, and
- hands a tapped notification to ui with the alert it belongs to, so that
  ui opens the plant of that alert.

Without it, ui shows alerts only on its screens.

## Out of scope

- Fetching readings, storing data, talking to a server.
- Deciding whether a plant needs attention.
- Composing or delivering notifications.
- Layouts for landscape, tablets or watches.
- Units other than percent, lux and degrees Celsius.

## More

- [AGENTS.md](AGENTS.md): why the screens are built this way
- [Context diagram](doc/diagrams/context.md)
- [doc/context.md](doc/context.md): what ui inherits from above
- [Presets](doc/references/presets.md): the threshold presets the plant
  form offers
- [Decisions](doc/decisions/index.md)
