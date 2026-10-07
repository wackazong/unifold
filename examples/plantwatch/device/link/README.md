---
unit: link
summary: Implements the BLE profile on top of the radio
kind: library
status: planned
provides:
  ble-link:
    kind: protocol
    summary: Serves live and stored readings to a nearby central over BLE
needs:
  radio:
    kind: library
    summary: BLE peripheral role with GATT server primitives
  reading-log:
    kind: library
    summary: Stored readings in order, with a way to mark them as delivered
  live-readings:
    kind: library
    summary: The newest reading as soon as it exists
  link-profile:
    kind: specification
    summary: The definition of the BLE services to implement
---
# link

link makes the board a BLE peripheral that speaks the profile of a sensor
stick. It advertises, accepts a central, and answers its requests: who am
I, what is my state, what is the newest reading, give me the stored
readings, I have them. link holds no readings itself. It translates
between GATT operations and the sources of readings it is given.

## Provides

### `ble-link`

What a central can rely on:

- **Conformance.** link implements the sensor stick's side of the
  definition it gets through `link-profile`, version 1.0: the advertising
  data, the service with all characteristics, every procedure, every
  result code.
- **Advertising.** While no central is connected, link advertises every
  1285 ms. The advertising data shows the newest sequence number and
  whether stored readings wait, and follows a change within 2 s.
- **One central at a time.** link closes a connection that has carried no
  request for 30 s, and any connection after 10 minutes.
- **Fetch.** link sends the stored readings exactly as `reading-log`
  returns them, in ascending order. A fetch changes nothing.
- **Confirm.** link has the readings marked as delivered before it
  indicates the result. When a central sees `success`, the mark survives
  power loss.
- **Live readings.** link notifies a subscribed central of every new
  reading within one connection interval after it gets the reading.
- **Bonding** is open for 5 minutes after every start.
- **Time reference.** The tick count in Status is the tick count of the
  read request itself, not a stored value.

What link does not add: how many readings are available, how long they
are kept and what happens when memory is full are properties of whatever
provides `reading-log`. link has no buffer of its own.

Limits: at the default ATT MTU, link sends one reading per notification.
A fetch of 2 880 readings takes about one minute, less with a larger MTU.

## Needs

### `radio`

A BLE peripheral with a GATT server for one central. link expects:

- advertising with data and interval of link's choice, replaceable while
  advertising;
- a table of characteristics that link declares at start, each with a
  128-bit UUID, its properties, and whether an encrypted connection is
  required;
- every read and write as an event that link answers, also with an ATT
  error;
- notifications and indications with back-pressure: "no room now" and
  "room again";
- the subscription state of each characteristic, reset at every
  connection;
- bonding without user interaction, with at least 4 bonds kept across
  power loss, accepted only for a duration that link names;
- closing a connection on request, after a time without requests and
  after a longest duration, both set by link;
- an 8-byte identifier that is unique per board and never changes; link
  reports it as the sensor id;
- the tick count of every event. link has no other source of time.

### `reading-log`

The stored readings and their state:

- a summary: number of stored readings, oldest and newest stored sequence
  number, the newest sequence number ever taken, the capacity, and whether
  stored readings have been discarded;
- the stored readings one after another in ascending order, starting at a
  sequence number link names, each within a few milliseconds;
- "mark as delivered up to n", which is durable when it returns, succeeds
  when repeated, and is refused for an n above the newest reading taken.

### `live-readings`

Every new reading at the moment it exists, in order: sequence number, tick
count, and soil moisture, light and temperature, each present or absent.

### `link-profile`

The definition of what a sensor stick advertises, of the GATT service and
its characteristics, of the record that carries a reading, of the
procedures and of the behaviour on failures, for major version 1.

## Out of scope

- Measuring and storing. link serves what it is given.
- The role of a central: link never scans and never connects.
- Deciding what the profile should say.
- Anything a central does with a reading.

## More

- [AGENTS.md](AGENTS.md): why the profile lives in one unit that owns no data
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
