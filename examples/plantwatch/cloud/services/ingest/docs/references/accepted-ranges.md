# Accepted ranges

The state with which `ingest` recognises a reading it has accepted before.
It is internal: no capability exposes it. The reasons are in
[0001](../decisions/0001-accepted-ranges-are-kept-on-the-event-bus.md).

## Content

For every sensor id `ingest` keeps the set of accepted sequence numbers as
a list of closed ranges, in ascending order, without overlap and without
two ranges that touch.

```json
{
  "sensor_id": "00a1b2c3d4e5f607",
  "ranges": [[1, 2880], [2913, 4711]]
}
```

The example says: the readings 1 to 2 880 and 2 913 to 4 711 are accepted.
The readings 2 881 to 2 912 have not arrived.

## Where it lives

| Item | Value |
|---|---|
| Topic | `ingest.accepted-ranges.v1` |
| Kind | A topic that keeps the latest message per key without a time limit |
| Key | The sensor id |
| Value | The JSON object above, without envelope |
| Readers and writers | The instances of `ingest`, and nobody else |

- Every instance reads the whole topic when it starts and keeps the state
  in memory. Until it has reached the end it answers uploads with `503`.
- Every instance keeps reading the topic while it runs, and so learns
  what other instances accepted.
- After the events of a batch are acknowledged, the instance publishes
  the new list for the sensor id and waits for the acknowledgement.

## Limits

| Item | Value |
|---|---|
| Ranges per sensor id | At most 1 000 |
| Size of one value | At most 32 kB |

When a list would get its 1 001st range, `ingest` joins the two lowest
ranges into one. The sequence numbers between them then count as
accepted.

## What the state does not guarantee

| Situation | Effect |
|---|---|
| Two instances accept readings of the same sensor stick at the same moment | Both may publish an event for the same reading. One of the two lists may overwrite the other, so that readings of the lost list are accepted once more when they are uploaded again. |
| An instance stops after publishing events and before publishing the list | The repeated batch is accepted once more. |
| The topic is lost | Every reading that is uploaded again is accepted once more. |
| Two of the lowest ranges were joined | A reading in the gap between them is reported as `duplicate` although it was never accepted. |

In the first three cases the result is a repeated event with the same
`id`, which subscribers tolerate ([context](../explanation/context.md)). Only the last
case loses a reading.
