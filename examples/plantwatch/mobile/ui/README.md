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
- A screen shows what the phone holds within 1 second after it opens. No
  screen shows a loading state for data that is on the phone.
- Every screen that shows readings or alerts says how old they are. When
  the newest reading of a plant is older than 24 hours, it says "No
  readings since" with the time.
- A change the owner makes is visible within 1 second and carries a mark
  until it is confirmed. A refused change is shown with the reason.
- A reading whose time is estimated is shown with "about" before the time.
- No state is shown by colour alone. Every control has a label for screen
  readers. Text follows the text size of the system.
- Once the owner has allowed notifications, ui keeps the phone registered
  for the owner's notifications. A tap on one opens the plant it is about.
- The screens ask for no account. A second phone joins by scanning a code
  that the first phone shows.

Limits: the screens show an alert only when `plant-data` contains one; a
low value in the history is not marked as a problem by itself. Temperatures
are shown in degrees Celsius only.

Example: the owner taps "Monstera" in the list. The plant's screen shows
"Soil moisture 23 %, 2 hours ago", the alert "Needs water since Tuesday",
and the chart of the last week.

Contract: [app-ui](doc/references/app-ui.md): every screen, its states
and the ways between the screens.

## Needs

### `plant-data`

The owner's plants, history and alerts, and the commands that change a
plant. ui defines this interface itself, as the customer of whoever
provides it: [what the screens expect](doc/references/plant-data.md). In
short, ui expects that

- every query answers from data on the phone within 100 milliseconds, with
  or without a network connection, and can be observed,
- plants come with their newest reading, open alerts and the age of their
  readings, and the history comes by reading, by hour and by day, so that
  a chart of 90 days needs no arithmetic on a screen,
- a command has taken effect when it returns and lasts, and each plant
  says whether a change is waiting or was refused, and why,
- it tells whether the phone acts for an owner or has lost its access,
  gives the owner's id, and says when data was last exchanged, and
- it offers "start", "join", "leave", a token for another phone, and a way
  to ask for fresh data now.

### `pairing`

A way to find and bind a sensor stick. ui takes this interface as its
provider defines it, with its failure reasons and its measure of signal
strength. ui relies on that it

- lists the sensor sticks in range that can be paired, with a signal
  strength, strongest first, while a search runs,
- pairs one of them and answers with success or with a reason that ui can
  turn into an instruction for the owner,
- lists the paired sensor sticks with the time of their last fetch, and
- unpairs one.

### `push-service`

The push service of the phone's platform, taken as it is. ui relies on
that it

- registers this phone for one owner's notifications, ends the
  registration when ui asks, and reports a changed address of the phone,
- delivers a notification that was sent to that owner to this phone, and
- hands a tapped notification to ui with the ids of the plant and the
  alert it is about.

Notifications that are not allowed or not delivered cost nothing else: ui
shows every alert that `plant-data` contains on its screens.

## Out of scope

- Fetching readings, storing data, exchanging data with a server.
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
- [Glossary](doc/references/glossary.md): ui's own terms
