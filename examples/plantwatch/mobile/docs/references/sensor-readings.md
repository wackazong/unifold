# sensor-readings

Contract of `ble-client.sensor-readings`: the operations, data and guarantees of the capability through which the client hands fetched readings to its consumer. The fields of a reading and of a paired sensor stick are those of the [data model](data-model.md). The consumer is the one receiver attached to the capability; it acknowledges a batch once it has stored it. An anchor is a time reference that the client keeps for one boot of a sensor stick. Notation: wit.
Sources: the BLE profile and the reading schema of plantwatch.
Binding: in-process

## Use

The consumer attaches when the program starts and detaches when the phone leaves its owner. From then on the client fetches from every paired sensor stick in range by itself and delivers the readings as batches. The consumer stores each batch durably and then acknowledges it, within 5 seconds; the client confirms the readings to the sensor stick only after that acknowledgement. The consumer recognises a reading by sensor id and sequence number and keeps the one it stored first. The client fetches by itself when the operating system reports a paired sensor stick, when the program comes onto the screen, and when the consumer asks with `fetch-now`. After `detach-consumer` the client stops fetching and connects to no sensor stick until a consumer attaches again. `fetch-now` asks for a fetch from one sensor stick at once; its readings arrive as batches, and every batch but the last has `more-to-come` set.

## States

Start: detached.

| State | Part | Result | Next |
|---|---|---|---|
| detached | `attach-consumer` | | attached |
| detached | `detach-consumer` | | detached |
| attached | `attach-consumer` | | attached |
| attached | `detach-consumer` | | detached |
| attached | `fetch-now` | | attached |
| attached | `batch` | | attached |
| attached | `acknowledge` | | attached |

## Qualities

| Aspect | Guarantee |
|---|---|
| delivery | nothing is lost: every reading a paired sensor stick holds unconfirmed is delivered, provided the sensor stick comes into range and the consumer acknowledges; a reading is delivered once, and again only if the acknowledgement was missing or late or the connection broke between acknowledgement and confirmation |
| ordering | within one sensor stick, readings arrive in ascending sequence number, across batches as well; sequence numbers may have gaps; there is no order between sensor sticks |
| fidelity | every reading carries its tick count exactly as the sensor stick sent it and has a UTC time; the estimated flag is set exactly when the time was not computed from a known anchor; a second delivery of a reading may carry a time up to 2 seconds different from the first, and never a different flag; every delivered value lies in the range of its quantity, and a quantity the sensor stick did not measure is absent |
| security | the client delivers nothing from a sensor stick that is not paired with this phone |
| timeout | an acknowledgement counts within 5 seconds after the delivery |
| latency | `fetch-now` starts to connect within 1 second |
| limits | 1 to 200 readings per batch; in the background each sensor stick is fetched at most 4 times a day |
| concurrency | one fetch at a time |

## Parts

### attach-consumer

Kind: operation

```wit
attach-consumer: func(receiver: batch-receiver);
```

Pre: none; the consumer attaches when the program starts, also when the operating system has started the program in the background.
Result: from now on the client delivers batches to this receiver. A second attach replaces the first.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| attach | the program has started | `attach-consumer(receiver)` | batches go to this receiver |
| second attach | a receiver is attached | `attach-consumer(other)` | batches go to the other receiver |

### detach-consumer

Kind: operation

```wit
detach-consumer: func();
```

Pre: none.
Result: the client stops fetching. Readings stay on their sensor sticks.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| no consumer | | `detach-consumer()` | the client connects to no sensor stick until a consumer attaches again |
| detach during a fetch | a fetch runs | `detach-consumer()` | nothing more is confirmed; the readings stay on the sensor stick |

### batch

Kind: event

```wit
batch: func(batch: batch);
record batch { batch-id: string, sensor-id: string, readings: list<reading>, more-to-come: bool }
```

When: the client has fetched readings from a paired sensor stick, up to 200 at a time.
Delivery: at least once; in ascending sequence number within one sensor stick, across batches as well; no order between sensor sticks.

| Field | Content |
|---|---|
| batch-id | identifies this delivery; not stable across deliveries of the same readings |
| sensor-id | the sensor stick all readings of the batch come from |
| readings | 1 to 200 readings in ascending sequence number, in the form of the reading schema |
| more-to-come | yes if the sensor stick holds further unconfirmed readings |

### acknowledge

Kind: operation

```wit
acknowledge: func(batch-id: string);
```

Pre: the batch was delivered less than 5 seconds ago and the consumer has stored it durably.
Result: the client confirms the readings of the batch to the sensor stick, and only then.
Errors: none; a late acknowledgement is ignored and the batch is delivered again at the next fetch.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| in time | a batch was delivered 1 second ago | `acknowledge(batch-id)` | the readings are confirmed to the sensor stick |
| late | the first batch was delivered 6 seconds ago | `acknowledge(batch-id)` | nothing confirmed; outcome `failed` with `not acknowledged`; the next fetch delivers the same readings under a new batch id |

### fetch-now

Kind: operation

```wit
fetch-now: func(sensor-id: option<string>) -> list<tuple<string, fetch-outcome>>;
```

Pre: none.
Result: the client starts to connect to the named, or to every, paired sensor stick, and returns one outcome per sensor stick: `fetched` when all unconfirmed readings were delivered and confirmed, with their number, which may be 0; `partly fetched` when some readings were confirmed and then the fetch ended, with their number and the reason; `not in range` when the sensor stick did not answer within the connect timeout; `failed` when nothing was confirmed, with a reason.
Errors: none; a failure never surfaces as an error of an operation but as the reason of an outcome and as the last failure that `list-paired` of [pairing](pairing.md) reports. The reasons, and what the client then does:

| Reason | Meaning | The client then |
|---|---|---|
| `bluetooth off` | Bluetooth is switched off on the phone | waits until it is switched on |
| `permission missing` | the program lacks a permission for Bluetooth | waits until the program is on the screen again |
| `connection lost` | the connection broke during a fetch | reconnects and starts over at the oldest unconfirmed reading |
| `not acknowledged` | the consumer did not acknowledge in time | ends the fetch without confirming the batch |
| `unsupported version` | the sensor stick states a major protocol version other than 1 | does not fetch from this sensor stick |
| `not paired any more` | the sensor stick refuses this phone | does not fetch; the pairing stays listed until it is removed |
| `profile violation` | the sensor stick answers in a way the BLE profile does not allow | ends the fetch without confirming |

Examples: each case is a `fetch-now` for one paired sensor stick S in range, with an attached consumer that acknowledges within 1 second, unless the case says otherwise.

| Case | Given | Input | Expected |
|---|---|---|---|
| backlog | 450 unconfirmed readings | `fetch-now(S)` | batches of 200, 200 and 50; `more-to-come` yes, yes, no; outcome `fetched` with 450 |
| nothing to fetch | no unconfirmed reading | `fetch-now(S)` | no batch; outcome `fetched` with 0 |
| connection lost | 450 readings; the connection breaks for good during the second batch | `fetch-now(S)` | first batch confirmed; outcome `partly fetched` with 200 and `connection lost`; the next fetch starts with reading 201 |
| invalid value | 10 readings, the fourth with a soil moisture of 120 percent | `fetch-now(S)` | one batch of 9 readings; the `invalid-readings` that `list-paired` of pairing reports rises by 1; all 10 confirmed to the sensor stick |
| unknown boot | 4 readings of a boot the client holds no anchor for, then 4 of the current boot | `fetch-now(S)` | 8 readings in ascending sequence number; the first 4 flagged as estimated, the last 4 not |
| newer major version | the sensor stick states protocol version 2.0 | `fetch-now(S)` | no batch; outcome `failed` with `unsupported version`; nothing written to the sensor stick |

### fetch-outcome

Kind: type

```wit
variant fetch-outcome { fetched(u32), partly-fetched(tuple<u32, string>), not-in-range, failed(string) }
```

## Fake

A client in memory that a test loads with readings per sensor stick: `fetch-now` delivers them in batches of 200 and confirms on acknowledgement. Faults it can inject: every reason of the table, a lost connection after any batch, a late acknowledgement.
