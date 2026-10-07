# Contract of `sensor-readings`

The operations, data and guarantees of the port through which the client
hands fetched readings to its consumer. The description is independent of a
programming language. The fields of a reading and of a paired sensor stick
are those cited in [context.md](../context.md); the unit's own terms are in
the [glossary](glossary.md).

## Operations

| Operation | Input | Output | Effect |
|---|---|---|---|
| Attach consumer | A receiver for batches | Nothing | From now on the client delivers batches to this receiver. A second attach replaces the first. |
| Detach consumer | Nothing | Nothing | The client stops fetching. Readings stay on their sensor sticks. |
| Acknowledge | Batch id | Nothing | The consumer states that it has stored the batch. The client confirms the readings to the sensor stick. |
| Fetch now | Nothing, or one sensor id | One outcome per paired sensor stick | The client starts within 1 second to connect to the named, or to every, paired sensor stick. |
| Observe status | Nothing | The status of every paired sensor stick, again whenever one changes | None |

The consumer attaches when the program starts, also when the operating
system has started the program in the background. Without a consumer the
client connects to no sensor stick.

## Batch

| Field | Content |
|---|---|
| Batch id | Identifies this delivery. It is not stable across deliveries of the same readings. |
| Sensor id | The sensor stick all readings of the batch come from |
| Readings | 1 to 200 readings in ascending sequence number |
| More to come | Yes if the sensor stick holds further unconfirmed readings |

## Outcome of "fetch now"

| Outcome | Meaning |
|---|---|
| `fetched` | All unconfirmed readings were delivered and confirmed; with their number, which may be 0 |
| `partly fetched` | Some readings were confirmed, then the fetch ended; with their number and the reason |
| `not in range` | The sensor stick did not answer within the connect timeout |
| `failed` | Nothing was confirmed; with a reason from the table of failures |

## Status of a paired sensor stick

| Field | Content |
|---|---|
| Sensor id | The sensor stick |
| State | `idle`, `connecting`, `fetching` or `failing` |
| Last fetch | UTC time of the last fetch that ended as `fetched`, or none |
| Last failure | Reason and UTC time, or none; cleared by the next `fetched` |
| Invalid readings | Number of readings dropped since pairing because a value was outside its range |

## Guarantees

- **Nothing is lost.** Every reading a paired sensor stick holds unconfirmed
  is delivered, provided the sensor stick comes into range and the consumer
  acknowledges.
- **Confirmation follows acknowledgement.** The client confirms a reading
  to the sensor stick only after the consumer has acknowledged the batch
  that contains it.
- **Once, with one exception.** A reading is delivered once. It is delivered
  again if the acknowledgement was missing or late, or if the connection
  broke between acknowledgement and confirmation.
- **Order.** Within one sensor stick, readings arrive in ascending sequence
  number, across batches as well. Sequence numbers may have gaps. There is
  no order between sensor sticks.
- **Tick count.** Every reading carries its tick count exactly as the
  sensor stick sent it.
- **Time.** Every reading has a UTC time. The estimated flag is set exactly
  when the time was not computed from a known anchor. A second delivery of a
  reading may carry a time up to 2 seconds different from the first, and
  never a different flag.
- **Valid values.** Every delivered value lies in the range of its
  quantity. A quantity the sensor stick did not measure is absent.
- **Only paired sensor sticks.** The client delivers nothing from a sensor
  stick that is not paired with this phone.

## What the consumer must do

- Recognise a reading by sensor id and sequence number and keep the one it
  stored first.
- Acknowledge a batch only after storing it durably.
- Acknowledge within 5 seconds. A later acknowledgement is ignored and the
  batch is delivered again at the next fetch.

## Examples

Each case is a "fetch now" for one paired sensor stick in range, with an
attached consumer that acknowledges within 1 second, unless the case says
otherwise.

| Case | Given | Expected |
|---|---|---|
| Backlog | 450 unconfirmed readings | Batches of 200, 200 and 50; "more to come" yes, yes, no; outcome `fetched` with 450 |
| Nothing to fetch | No unconfirmed reading | No batch; outcome `fetched` with 0 |
| Connection lost | 450 readings; the connection breaks for good during the second batch | First batch confirmed; outcome `partly fetched` with 200 and `connection lost`; the next fetch starts with reading 201 |
| Late acknowledgement | The consumer acknowledges the first batch after 6 seconds | Nothing confirmed; outcome `failed` with `not acknowledged`; the next fetch delivers the same readings under a new batch id |
| Invalid value | 10 readings, the fourth with a soil moisture of 120 percent | One batch of 9 readings; "invalid readings" rises by 1; all 10 confirmed to the sensor stick |
| Unknown boot | 4 readings of a boot the client holds no anchor for, then 4 of the current boot | 8 readings in ascending sequence number; the first 4 flagged as estimated, the last 4 not |
| Newer major version | The sensor stick states protocol version 2.0 | No batch; outcome `failed` with `unsupported version`; nothing written to the sensor stick |
| No consumer | The consumer has detached | The client connects to no sensor stick |

## Failures

A failure never surfaces as an error of an operation. It appears as the
reason of an outcome and as the last failure in the status.

| Reason | Meaning | The client then |
|---|---|---|
| `bluetooth off` | Bluetooth is switched off on the phone | Waits until it is switched on |
| `permission missing` | The program lacks a permission for Bluetooth | Waits until the program is on the screen again |
| `connection lost` | The connection broke during a fetch | Reconnects as described in [fetch-session.md](fetch-session.md) |
| `not acknowledged` | The consumer did not acknowledge in time | Ends the fetch without confirming the batch |
| `unsupported version` | The sensor stick states a major protocol version other than 1 | Does not fetch from this sensor stick |
| `not paired any more` | The sensor stick refuses this phone | Does not fetch; the pairing stays listed until it is removed |
| `profile violation` | The sensor stick answers in a way `link-profile` does not allow | Ends the fetch without confirming |
