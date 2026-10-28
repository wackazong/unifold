# ble-client

`ble-client` is the central for sensor sticks, as a library for iOS and Android. It finds sensor sticks, pairs them with the phone, fetches their stored readings whenever a paired one is in range, and gives every reading a UTC time. Whoever uses it sees readings and sensor ids, never BLE.

## Why

The radio is the part of a phone program that fails most often and differs most between iOS and Android: sensor sticks go out of range in the middle of a transfer, the operating system suspends the program after seconds, the owner switches Bluetooth off. This library exists so that all of that stays in one place. Its consumer gets a plain promise: here is a batch of readings, tell me when you have stored it.

The unit changes for two reasons that both come from the radio: the BLE profile gets a new version, or iOS or Android change what a program may do with BLE in the background. Nothing else should reach it.

The main trade-off: the client stores no readings. A reading exists on the sensor stick until the consumer has acknowledged it, so there is no third place where readings could wait or get lost. The price is that a fetch depends on a consumer that answers within seconds, and that an interrupted fetch repeats work ([0001](docs/decisions/0001-confirm-in-chunks-and-resume-at-the-oldest-unconfirmed-reading.md)).

What must stay true: the client never confirms a reading to a sensor stick before the consumer has acknowledged it.

## Capabilities

### `sensor-readings`

The client fetches by itself: when the operating system reports a paired sensor stick, when the program comes onto the screen, and when the consumer asks. In the background it fetches each sensor stick at most 4 times a day. It runs one fetch at a time.

## Read next

1. [docs/references/fetch-session.md](docs/references/fetch-session.md): a fetch as a state machine, with sizes and timeouts
2. [sensor readings](../docs/references/sensor-readings.md) and [pairing](../docs/references/pairing.md): the contracts
3. [docs/references/glossary.md](docs/references/glossary.md): acknowledge and confirm, chunk, session, anchor
4. [Context diagram](docs/diagrams/context.md)
5. [docs/explanation/context.md](docs/explanation/context.md): what the client inherits from above
6. [Decisions](docs/decisions/index.md)
