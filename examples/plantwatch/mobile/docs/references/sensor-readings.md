# sensor-readings

Contract of `ble-client.sensor-readings`: the operations, data and guarantees of the capability through which the client hands fetched readings to its consumer. The description is independent of a programming language. The fields of a reading and of a paired sensor stick are those cited in [context.md](../explanation/context.md). The consumer is the one receiver attached to the capability; it acknowledges a batch once it has stored it. An anchor is a time reference that the client keeps for one boot of a sensor stick. Notation: wit.
Sources: the BLE profile and the reading schema of plantwatch, decisions 0001 and 0002 of `ble-client`.

## What the consumer must do

- Recognise a reading by sensor id and sequence number and keep the one it stored first.
- Acknowledge a batch only after storing it durably.
- Acknowledge within 5 seconds. A later acknowledgement is ignored and the batch is delivered again at the next fetch.

## Parts

### attach-consumer

Kind: command

```wit
attach-consumer: func(receiver: batch-receiver);
```

Pre: none; the consumer attaches when the program starts, also when the operating system has started the program in the background.
Result: from now on the client delivers batches to this receiver. A second attach replaces the first. Without a consumer the client connects to no sensor stick.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| no consumer | the consumer has detached | the client connects to no sensor stick |

### detach-consumer

Kind: command

```wit
detach-consumer: func();
```

Pre: none.
Result: the client stops fetching. Readings stay on their sensor sticks.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| detach during a fetch | a fetch runs | nothing more is confirmed; the readings stay on the sensor stick |

### batch

Kind: event

```wit
batch: func(batch: batch);
record batch { batch-id: string, sensor-id: string, readings: list<reading>, more-to-come: bool }
```

| Field | Content |
|---|---|
| batch-id | identifies this delivery; not stable across deliveries of the same readings |
| sensor-id | the sensor stick all readings of the batch come from |
| readings | 1 to 200 readings in ascending sequence number, in the form of the reading schema |
| more-to-come | yes if the sensor stick holds further unconfirmed readings |

What every delivery guarantees: nothing is lost, as every reading a paired sensor stick holds unconfirmed is delivered, provided the sensor stick comes into range and the consumer acknowledges. A reading is delivered once; it is delivered again if the acknowledgement was missing or late, or if the connection broke between acknowledgement and confirmation. Within one sensor stick, readings arrive in ascending sequence number, across batches as well; sequence numbers may have gaps; there is no order between sensor sticks. Every reading carries its tick count exactly as the sensor stick sent it. Every reading has a UTC time; the estimated flag is set exactly when the time was not computed from a known anchor; a second delivery of a reading may carry a time up to 2 seconds different from the first, and never a different flag. Every delivered value lies in the range of its quantity; a quantity the sensor stick did not measure is absent. The client delivers nothing from a sensor stick that is not paired with this phone.

### acknowledge

Kind: command

```wit
acknowledge: func(batch-id: string);
```

Pre: the batch was delivered less than 5 seconds ago and the consumer has stored it durably.
Result: the client confirms the readings of the batch to the sensor stick, and only then.
Errors: none; a late acknowledgement is ignored and the batch is delivered again at the next fetch.
Examples:

| Case | Given | Expected |
|---|---|---|
| in time | the consumer acknowledges within 1 second | the readings are confirmed to the sensor stick |
| late | the consumer acknowledges the first batch after 6 seconds | nothing confirmed; outcome `failed` with `not acknowledged`; the next fetch delivers the same readings under a new batch id |

### fetch-now

Kind: command

```wit
fetch-now: func(sensor-id: option<string>) -> list<tuple<string, fetch-outcome>>;
```

Pre: a consumer is attached.
Result: the client starts within 1 second to connect to the named, or to every, paired sensor stick, and returns one outcome per sensor stick: `fetched` when all unconfirmed readings were delivered and confirmed, with their number, which may be 0; `partly fetched` when some readings were confirmed and then the fetch ended, with their number and the reason; `not in range` when the sensor stick did not answer within the connect timeout; `failed` when nothing was confirmed, with a reason.
Errors: none; a failure never surfaces as an error of an operation but as the reason of an outcome and as the last failure in the status. The reasons, and what the client then does:

| Reason | Meaning | The client then |
|---|---|---|
| `bluetooth off` | Bluetooth is switched off on the phone | waits until it is switched on |
| `permission missing` | the program lacks a permission for Bluetooth | waits until the program is on the screen again |
| `connection lost` | the connection broke during a fetch | reconnects and starts over at the oldest unconfirmed reading |
| `not acknowledged` | the consumer did not acknowledge in time | ends the fetch without confirming the batch |
| `unsupported version` | the sensor stick states a major protocol version other than 1 | does not fetch from this sensor stick |
| `not paired any more` | the sensor stick refuses this phone | does not fetch; the pairing stays listed until it is removed |
| `profile violation` | the sensor stick answers in a way the BLE profile does not allow | ends the fetch without confirming |

Examples: each case is a `fetch-now` for one paired sensor stick in range, with an attached consumer that acknowledges within 1 second, unless the case says otherwise.

| Case | Given | Expected |
|---|---|---|
| backlog | 450 unconfirmed readings | batches of 200, 200 and 50; `more-to-come` yes, yes, no; outcome `fetched` with 450 |
| nothing to fetch | no unconfirmed reading | no batch; outcome `fetched` with 0 |
| connection lost | 450 readings; the connection breaks for good during the second batch | first batch confirmed; outcome `partly fetched` with 200 and `connection lost`; the next fetch starts with reading 201 |
| invalid value | 10 readings, the fourth with a soil moisture of 120 percent | one batch of 9 readings; `invalid readings` rises by 1; all 10 confirmed to the sensor stick |
| unknown boot | 4 readings of a boot the client holds no anchor for, then 4 of the current boot | 8 readings in ascending sequence number; the first 4 flagged as estimated, the last 4 not |
| newer major version | the sensor stick states protocol version 2.0 | no batch; outcome `failed` with `unsupported version`; nothing written to the sensor stick |

### observe-status

Kind: query

```wit
observe-status: func(observer: status-observer);
```

Pre: none.
Result: the status of every paired sensor stick, again whenever one changes.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| after a fetch | a fetch ended as `fetched` | the status of the sensor stick has state `idle` and that time as last fetch |

### sensor-stick-status

Kind: type

```wit
record sensor-stick-status {
  sensor-id: string,
  state: string,
  last-fetch: option<string>,
  last-failure: option<tuple<string, string>>,
  invalid-readings: u32,
}
```

| Field | Content |
|---|---|
| sensor-id | the sensor stick |
| state | `idle`, `connecting`, `fetching` or `failing` |
| last-fetch | UTC time of the last fetch that ended as `fetched`, or none |
| last-failure | reason and UTC time, or none; cleared by the next `fetched` |
| invalid-readings | number of readings dropped since pairing because a value was outside its range |

### fetch-outcome

Kind: type

```wit
variant fetch-outcome { fetched(u32), partly-fetched(tuple<u32, string>), not-in-range, failed(string) }
```

## Fake

A client in memory that a test loads with readings per sensor stick: `fetch-now` delivers them in batches of 200 and confirms on acknowledgement. Faults it can inject: every reason of the table, a lost connection after any batch, a late acknowledgement.
