# Reading events

The contract of the capability `reading-events`: the stream on which
`ingest` announces accepted readings. The envelope and the naming rules are
defined above this unit and cited in [context](../explanation/context.md).

## Topic

| Item | Value |
|---|---|
| Topic | `ingest.readings.v1` |
| Kind | A topic that keeps every event for 7 days, consumed or not |
| Publisher | `ingest`, and nobody else |
| Event types | `reading.accepted` |
| Key | The sensor id |

## The event `reading.accepted`

```json
{
  "id": "00a1b2c3d4e5f607-4711",
  "type": "reading.accepted",
  "source": "ingest",
  "time": "2026-10-06T09:00:03Z",
  "key": "00a1b2c3d4e5f607",
  "data": {
    "sensor_id": "00a1b2c3d4e5f607",
    "sequence_number": 4711,
    "time": "2026-10-06T08:45:00Z",
    "time_estimated": false,
    "values": {
      "soil_moisture": 41.9,
      "light": 1250,
      "temperature": 21.6
    },
    "reading": { "...": "the reading as it was uploaded" }
  }
}
```

| Field | Content |
|---|---|
| `id` | Sensor id, a hyphen, the sequence number in decimal digits |
| `time` (envelope) | When `ingest` published the event |
| `key` | The sensor id |
| `data.sensor_id` | The sensor stick that took the reading |
| `data.sequence_number` | The sequence number of the reading |
| `data.time` | The time of the reading |
| `data.time_estimated` | `true` if the time of the reading was estimated |
| `data.values` | The measured values. A quantity that was not measured is absent. |
| `data.reading` | The uploaded reading as a JSON object, unchanged, including fields that `ingest` does not know |

| Name in `values` | Quantity |
|---|---|
| `soil_moisture` | Soil moisture |
| `light` | Light |
| `temperature` | Temperature |

Units, ranges and resolutions are those of the project conventions
([context](../explanation/context.md)).

## Key, order, delivery

| Aspect | Guarantee |
|---|---|
| Key | The sensor id. All events of one sensor stick have the same key. |
| Order | Events with the same key reach a subscriber in the order in which `ingest` accepted the readings. Readings of one batch are published in ascending order of sequence number. No order holds between different keys. |
| Delivery | At least once. `ingest` publishes an event for every reading that `ingest-api` reports as `new`, before it reports it. |
| Retention | An event stays on the topic for 7 days, consumed or not. |
| Repeats | Possible. A repeat has the same `id`. |

## Further guarantees

- All values in `values` are within their range. `data.time` is neither
  more than 24 hours after nor more than 90 days before the envelope
  `time`.
- Two events with the same `id` describe the same reading.

## What a subscriber must expect

- **Repeats.** The same event can be published more than once: after a
  failure of `ingest`, and when the same reading is uploaded at two places
  at once. A repeat has the same `id`. It may carry a different envelope
  `time`.
- **Old readings after new ones.** Sequence numbers and times of one
  sensor stick do not always rise from event to event. A batch that is
  uploaded late brings older readings.
- **Gaps.** Sequence numbers of a sensor stick can be missing for good,
  because the sensor stick overwrote readings that nobody fetched.
- **Unknown sensor sticks.** `ingest` publishes readings of every sensor
  id, also of one that belongs to no plant.
- **More quantities.** A later version adds names to `values`. A
  subscriber ignores names it does not know.

## Examples

| Case | What happens | Events on the topic, in order |
|---|---|---|
| One batch | Readings 4713, 4711, 4712 of one sensor stick are accepted | `…-4711`, `…-4712`, `…-4713` |
| Repeated batch | The same batch is uploaded again | none |
| Late batch | Readings 4800 to 4810 are accepted, then 4700 to 4710 | `…-4800` to `…-4810`, then `…-4700` to `…-4710` |
| Failure before the answer | `ingest` stops after publishing 4711 and before recording it; the batch is uploaded again | `…-4711` twice, with different envelope `time` |
| Not measured | A reading without light is accepted | One event whose `values` has no `light` |
| Rejected reading | A reading with `soil_moisture` 104.2 is uploaded | none |

## Versions

A change that removes or renames a field, or changes a unit, leads to a
topic `ingest.readings.v2`. `ingest` then publishes to both topics until
the old one has no subscriber.
