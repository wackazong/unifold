# ui

`ui` is everything the owner sees and touches on the phone: the list of plants, the state and history of one plant, the forms for a plant and its thresholds, and the steps that put a sensor stick to a plant. It shows what it is given and passes on what the owner does. It holds no data of its own.

## Why

The screens are the part that changes most often and for reasons that have nothing to do with radios or servers: wording, layout, a new chart, a new thing the owner can do. They are a unit of their own so that such a change touches nothing else, and so that they can be built and tested against prepared data alone.

The screens are deliberately dumb. They draw what `plant-data` holds and hand the owner's actions to `plant-data` and `pairing`. They keep no copy, compute no state of a plant and wait for nothing. This is what makes them behave the same with and without a network connection. Notifications are no exception: `ui` registers the phone and follows a tap to a plant, takes nothing else from a notification, and shows what `plant-data` holds.

The main trade-off: the screens cannot be cleverer than their data. A reading far below a threshold is not shown as a problem until an alert exists. The owner gets one consistent answer to "does this plant need me", and the price is that the answer can be late. The screens make up for it by always saying how old their data is. The navigation follows from the same question ([0001](docs/decisions/0001-the-plant-list-is-home-and-alerts-have-no-screen-of-their-own.md)).

## Capabilities

### `app-ui`

The screens add this to the contract:

- A screen shows what the phone holds within 1 second after it opens. No screen shows a loading state for data that is on the phone.
- The reason of an alert is worded "needs water", "needs more light" or "needs a warmer place".
- When the newest reading of a plant is older than 24 hours, the screen says "No readings since" with the time.
- A change that the server refuses is shown with the reason.
- A reading whose time is estimated is shown with "about" before the time.
- The history is a chart of up to 90 days.

Limits: a low value in the history is not marked as a problem by itself. Temperatures are shown in degrees Celsius only.

Every screen, its states and the ways between the screens are in [screens](docs/references/screens.md).

## Needs

### `push-service`

Notifications that are not allowed or not delivered cost nothing else: `ui` shows every alert that `plant-data` contains on its screens.

## Read next

1. [screens](docs/references/screens.md): the screens, the ways between them, and the states every screen has
2. [plant data](../docs/references/plant-data/index.md): the contract of `plant-data`, with the examples the screens are tested with
3. [docs/references/presets.md](docs/references/presets.md): threshold presets
4. [docs/references/glossary.md](docs/references/glossary.md): screen, state, mark, bar, span
5. [Context diagram](docs/diagrams/context.md)
6. [docs/explanation/context.md](docs/explanation/context.md): what `ui` inherits from above
7. [Decisions](docs/decisions/index.md)
