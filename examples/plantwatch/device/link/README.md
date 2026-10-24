# link

`link` makes the board a BLE peripheral that speaks the profile of a sensor stick. It advertises, accepts a central, and answers its requests: who am I, what is my state, what is the newest reading, give me the stored readings, I have them. `link` holds no readings itself. It translates between GATT operations and the sources of readings it is given.

## Why

Everything that knows the profile is in this unit: UUIDs, byte layouts, op codes, the state of a running procedure. `link` exists so that a change of the profile changes one unit, and a change of the profile is the only thing that makes it change. Nothing else in the program sees a GATT attribute.

`link` owns no data. It reads stored readings where they are kept and has them marked there. So there is one owner of "what is delivered", and a connection that breaks leaves nothing behind in `link` that could disagree with it. The only state `link` has is the state of the current connection, and that is meant to vanish with the connection.

The price is that `link` has three needs and is mostly a state machine between them. Its correctness is its agreement with a text it does not own.

What must stay true: a fetch changes nothing; a confirm result goes out only after the mark is durable; and nothing outside `link` builds or parses a record of the profile.

## Capabilities

### `ble-link`

Where the BLE profile leaves a choice or sets only a bound, a central can rely on this:

- **Advertising.** While no central is connected, `link` advertises every 1285 ms. The advertising data shows the newest sequence number and whether stored readings wait, and follows a change within 2 s.
- **Connections.** `link` closes a connection that has carried no request for 30 s, and any connection after 10 minutes.
- **Fetch.** `link` sends the stored readings exactly as `reading-log` returns them, in ascending order. A fetch changes nothing.
- **Confirm.** `link` has the readings marked as delivered before it indicates the result. When a central sees `success`, the mark survives power loss.
- **Live readings.** `link` notifies a subscribed central of every new reading within one connection interval after it gets the reading.
- **Time reference.** The tick count in Status is the tick count of the read request itself, not a stored value.

What `link` does not add: how many readings are available, how long they are kept and what happens when memory is full are properties of whatever provides `reading-log`. `link` has no buffer of its own.

Limits: at the default ATT MTU, `link` sends one reading per notification. To a central that takes 4 notifications per connection event at an interval of 100 ms or less, `link` sends at least 40 readings per second: 2 880 readings in at most 72 s.

## Needs

### `radio`

`link` takes all time from the tick counts of the radio events. It has no other source of time.

## Out of scope

- Measuring and storing. `link` serves what it is given.
- The role of a central: `link` never scans and never connects.
- Deciding what the profile should say.
- Anything a central does with a reading.

## Read next

1. [radio](../docs/references/radio.md): what `link` expects of the radio
2. [docs/explanation/context.md](docs/explanation/context.md): what `link` inherits from above
3. [Context diagram](docs/diagrams/context.md)
4. [Decisions](docs/decisions/index.md)
