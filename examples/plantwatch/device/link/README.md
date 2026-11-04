# link

`link` makes the board a BLE peripheral that speaks the profile of a sensor stick. It advertises, accepts a central, and answers its requests: who am I, what is my state, what is the newest reading, give me the stored readings, I have them. `link` holds no readings itself. It translates between GATT operations and the sources of readings it is given.

## Why

What this unit hides is how the procedures of the profile are served from the log and the radio ([0001](docs/decisions/0001-serve-a-fetch-from-the-log-on-demand.md)). Everything that knows the profile is in this unit: UUIDs, byte layouts, op codes, the state of a running procedure. `link` exists so that a change of the profile changes one unit, and a change of the profile is the only thing that makes it change. Nothing else in the program sees a GATT attribute.

`link` owns no data. It reads stored readings where they are kept and has them marked there. So there is one owner of "what is delivered", and a connection that breaks leaves nothing behind in `link` that could disagree with it. The only state `link` has is the state of the current connection, and that is meant to vanish with the connection.

The price is that `link` has three needs and is mostly a state machine between them. Its correctness is its agreement with a text it does not own.

What must stay true: a fetch changes nothing; a confirm result goes out only after the mark is durable; and nothing outside `link` builds or parses a record of the profile.

## Read next

1. [radio](../docs/references/radio.md): what `link` expects of the radio
2. [docs/explanation/context.md](docs/explanation/context.md): what `link` inherits from above
3. [Decisions](docs/decisions/index.md)
