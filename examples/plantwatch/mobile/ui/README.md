# ui

`ui` is everything the owner sees and touches on the phone: the list of plants, the state and history of one plant, the forms for a plant and its thresholds, and the steps that put a sensor stick to a plant. It shows what it is given and passes on what the owner does. It holds no data of its own.

## Why

The screens are the part that changes most often and for reasons that have nothing to do with radios or servers: wording, layout, a new chart, a new thing the owner can do. They are a unit of their own so that such a change touches nothing else, and so that they can be built and tested against prepared data alone.

The screens are deliberately dumb. They draw what `plant-data` holds and hand the owner's actions to `plant-data` and `pairing`. They keep no copy, compute no state of a plant and wait for nothing. This is what makes them behave the same with and without a network connection. Notifications are no exception: `ui` registers the phone and follows a tap to a plant, takes nothing else from a notification, and shows what `plant-data` holds.

The main trade-off: the screens cannot be cleverer than their data. A reading far below a threshold is not shown as a problem until an alert exists. The owner gets one consistent answer to "does this plant need me", and the price is that the answer can be late. The screens make up for it by always saying how old their data is. The navigation follows from the same question ([0001](docs/decisions/0001-the-plant-list-is-home-and-alerts-have-no-screen-of-their-own.md)).

## Capabilities

### `app-ui`

The screens, in English and German, in portrait orientation.

- The first screen is the list of plants. Plants with an open alert come first and show the reason, for example "needs water", "needs more light" or "needs a warmer place".
- A plant's screen shows the latest reading, the open alerts and the history of up to 90 days as a chart.
- A screen shows what the phone holds within 1 second after it opens. No screen shows a loading state for data that is on the phone.
- Every screen that shows readings or alerts says how old they are. When the newest reading of a plant is older than 24 hours, it says "No readings since" with the time.
- A change the owner makes is visible within 1 second and carries a mark until it is confirmed. A refused change is shown with the reason.
- A reading whose time is estimated is shown with "about" before the time.
- No state is shown by colour alone. Every control has a label for screen readers. Text follows the text size of the system.
- Once the owner has allowed notifications, `ui` keeps the phone registered for the owner's notifications. A tap on one opens the plant it is about.
- The screens ask for no account. A second phone joins by scanning a code that the first phone shows.

Limits: the screens show an alert only when `plant-data` contains one; a low value in the history is not marked as a problem by itself. Temperatures are shown in degrees Celsius only.

Example: the owner taps "Monstera" in the list. The plant's screen shows "Soil moisture 23 %, 2 hours ago", the alert "Needs water since Tuesday", and the chart of the last week.

Contract: [app UI](../docs/references/app-ui.md). Every screen, its states and the ways between the screens are in [screens](docs/references/screens.md).

## Needs

### `plant-data`

The owner's plants, history and alerts, and the commands that change a plant. Its contract, which both sides name, is [plant data](../docs/references/plant-data.md). In short, `ui` expects that

- every query answers from data on the phone within 100 milliseconds, with or without a network connection, and can be observed,
- plants come with their newest reading, open alerts and the age of their readings, and the history comes by reading, by hour and by day, so that a chart of 90 days needs no arithmetic on a screen,
- a command has taken effect when it returns and lasts, and each plant says whether a change is waiting or was refused, and why,
- it tells whether the phone acts for an owner or has lost its access, gives the owner's id, and says when data was last exchanged, and
- it provides "start", "join", "leave", a token for another phone, and a way to ask for fresh data now.

### `pairing`

A way to find and bind a sensor stick, with the failure reasons and the measure of signal strength of its contract, [pairing](../docs/references/pairing.md). `ui` relies on that it

- lists the sensor sticks in range that can be paired, with a signal strength, strongest first, while a search runs,
- pairs one of them and answers with success or with a reason that `ui` can turn into an instruction for the owner,
- lists the paired sensor sticks with the time of their last fetch, and
- unpairs one.

### `push-service`

The push service of the phone's platform, taken as it is. `ui` relies on that it

- registers this phone for one owner's notifications, ends the registration when `ui` asks, and reports a changed address of the phone,
- delivers a notification that was sent to that owner to this phone, and
- hands a tapped notification to `ui` with the ids of the plant and the alert it is about.

Notifications that are not allowed or not delivered cost nothing else: `ui` shows every alert that `plant-data` contains on its screens.

## Out of scope

- Fetching readings, storing data, exchanging data with a server.
- Deciding whether a plant needs attention.
- Composing or delivering notifications.
- Layouts for landscape, tablets or watches.
- Units other than percent, lux and degrees Celsius.

## Read next

1. [screens](docs/references/screens.md): the screens, the ways between them, and the states every screen has
2. [plant data](../docs/references/plant-data.md): the contract of `plant-data`, with the examples the screens are tested with
3. [docs/references/presets.md](docs/references/presets.md): threshold presets
4. [docs/references/glossary.md](docs/references/glossary.md): screen, state, mark, bar, span
5. [Context diagram](docs/diagrams/context.md)
6. [docs/explanation/context.md](docs/explanation/context.md): what `ui` inherits from above
7. [Decisions](docs/decisions/index.md)
