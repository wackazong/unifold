# ble-client

ble-client is the central for sensor sticks, as a library for iOS and
Android. It finds sensor sticks, pairs them with the phone, fetches their
stored readings whenever a paired one is in range, and gives every reading a
UTC time. Whoever uses it sees readings and sensor ids, never BLE.

## Provides

### `sensor-readings`

Batches of readings from the paired sensor sticks, handed to one consumer.

- The client fetches by itself: when the operating system reports a paired
  sensor stick, when the program comes onto the screen, and when the
  consumer asks. In the last two cases it starts to connect within
  1 second.
- A batch holds up to 200 readings of one sensor stick in ascending sequence
  number. Each reading has its tick count as the sensor stick sent it, a
  UTC time, and a flag that says whether the time is estimated.
- The consumer acknowledges a batch when it has stored it, within
  5 seconds. Only then does the client confirm the readings to the sensor
  stick.
- In normal operation each reading is delivered once. After an interruption
  between delivery and confirmation it is delivered again. The consumer
  recognises it by sensor id and sequence number.
- A reading with a value outside its valid range is not delivered. The
  client counts it and confirms it to the sensor stick.
- The client reports per sensor stick the time of its last complete fetch
  and the reason of its last failure.

Limits: one fetch at a time; one consumer; up to 20 paired sensor sticks.
The time of a reading that is delivered twice may differ by up to 2 seconds
between the two deliveries.

Example: a sensor stick holds 450 unconfirmed readings. The consumer
receives three batches of 200, 200 and 50 readings and acknowledges each.
If the connection drops during the second batch, the next fetch starts with
reading 201.

Contract: [sensor-readings](doc/references/sensor-readings.md), with
example cases.

### `pairing`

Finding sensor sticks that are not yet paired with this phone, and binding
one to it.

- A search lists the sensor sticks in range that are open for pairing and
  not yet paired with this phone, with sensor id and signal strength, and
  updates the list while it runs.
- Pairing binds one of them to this phone. From then on the client fetches
  its readings. The binding survives restarts of the program and the phone.
- Pairing answers `paired` or one of seven stated failures. After a
  failure the sensor stick is not listed as paired and is not fetched.
- The port lists the paired sensor sticks and unpairs one on request.

Limits: a search runs only while the program is on the screen and ends by
itself after 60 seconds. A sensor stick is open for pairing only at the
times `link-profile` defines; outside them the search does not show it.
This port binds a sensor stick to the phone. Which plant the sensor stick
belongs to is not its business.

Contract: [pairing](doc/references/pairing.md), with example cases.

## Needs

The client defines neither interface. It takes both as their provider
defines them and states here what it relies on.

### `sensor-link`

A sensor stick in radio range that behaves as `link-profile` defines. The
client relies on that it

- advertises whenever no central is connected, in a way that says whether
  it is open for pairing and that lets the operating system recognise it
  without the client running,
- states its sensor id, the version of the radio protocol it speaks and
  its sampling interval,
- serves its unconfirmed readings in ascending sequence number, each with
  its tick count,
- tells its current tick count,
- deletes readings only up to the sequence number the client has confirmed
  or, when its memory is full, the oldest ones, and reports that it did,
  and serves everything after it again at the next connection, and
- accepts a connection as often as once per sampling interval and keeps
  it for at least 2 minutes while the client sends requests.

### `link-profile`

The definition of the services, characteristics and procedures behind these
expectations and of the record that carries a reading, with a version
number. The client implements the central side of major version 1 and takes
every identifier, format and timing from it.

## Out of scope

- Storing readings. The client holds a reading only between receiving it and
  the consumer's acknowledgement.
- Binding a sensor stick to a plant.
- Judging values beyond their valid range. The client knows no thresholds.
- Live values. The client fetches stored readings only.
- Updating or configuring a sensor stick.

## More

- [AGENTS.md](AGENTS.md): why the client is built this way
- [Context diagram](doc/diagrams/context.md)
- [doc/context.md](doc/context.md): what the client inherits from above
- [Fetch session](doc/references/fetch-session.md): states, sizes and
  timeouts of a fetch
- [Decisions](doc/decisions/index.md)
- [Glossary](doc/references/glossary.md): the client's own terms
