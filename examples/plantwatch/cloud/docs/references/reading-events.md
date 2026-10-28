# reading-events

Contract of `ingest.reading-events`: the stream on which `ingest` announces accepted readings. The envelope and the naming rules of events are defined by `cloud` ([events](events.md)) and cited in [context](../explanation/context.md). Units, ranges and resolutions are those of the project conventions. Notation: JSON, one object per event.
Sources: the reading schema of plantwatch, the public API of plantwatch, the event conventions of `cloud`.

## Topic

| Item | Value |
|---|---|
| topic | `ingest.readings.v1` |
| kind | a topic that keeps every event for 7 days, consumed or not |
| publisher | `ingest`, and nobody else |
| event types | `reading.accepted` |
| key | the sensor id |

A change that removes or renames a field, or changes a unit, leads to a topic `ingest.readings.v2`. `ingest` then publishes to both topics until the old one has no subscriber.

## Parts

### reading-accepted

Kind: event

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
| `id` | sensor id, a hyphen, the sequence number in decimal digits |
| `time` (envelope) | when `ingest` published the event |
| `key` | the sensor id |
| `data.sensor_id` | the sensor stick that took the reading |
| `data.sequence_number` | the sequence number of the reading |
| `data.time` | the time of the reading |
| `data.time_estimated` | `true` if the time of the reading was estimated |
| `data.values` | the measured values, named `soil_moisture`, `light` and `temperature`; a quantity that was not measured is absent |
| `data.reading` | the uploaded reading as a JSON object, unchanged, including fields that `ingest` does not know |

What the stream guarantees:

| Aspect | Guarantee |
|---|---|
| key | the sensor id; all events of one sensor stick have the same key |
| order | events with the same key reach a subscriber in the order in which `ingest` accepted the readings; readings of one batch are published in ascending order of sequence number; no order holds between different keys |
| delivery | at least once; `ingest` publishes an event for every reading that `ingest-api` reports as `new`, before it reports it |
| retention | an event stays on the topic for 7 days, consumed or not |
| repeats | possible; a repeat has the same `id` |
| values | all values in `values` are within their range; `data.time` is neither more than 24 hours after nor more than 90 days before the envelope `time`; two events with the same `id` describe the same reading |

What a subscriber must expect:

- **Repeats.** The same event can be published more than once: after a failure of `ingest`, and when the same reading is uploaded at two places at once. A repeat has the same `id`. It may carry a different envelope `time`.
- **Old readings after new ones.** Sequence numbers and times of one sensor stick do not always rise from event to event. A batch that is uploaded late brings older readings.
- **Gaps.** Sequence numbers of a sensor stick can be missing for good, because the sensor stick overwrote readings that nobody fetched.
- **Unknown sensor sticks.** `ingest` publishes readings of every sensor id, also of one that belongs to no plant.
- **More quantities.** A later version adds names to `values`. A subscriber ignores names it does not know.

Examples:

| Case | What happens | Events on the topic, in order |
|---|---|---|
| one batch | readings 4713, 4711, 4712 of one sensor stick are accepted | `…-4711`, `…-4712`, `…-4713` |
| repeated batch | the same batch is uploaded again | none |
| late batch | readings 4800 to 4810 are accepted, then 4700 to 4710 | `…-4800` to `…-4810`, then `…-4700` to `…-4710` |
| failure before the answer | `ingest` stops after publishing 4711 and before recording it; the batch is uploaded again | `…-4711` twice, with different envelope `time` |
| not measured | a reading without light is accepted | one event whose `values` has no `light` |
| rejected reading | a reading with `soil_moisture` 104.2 is uploaded | none |

## Fake

A scripted stream: the test publishes the events of the examples, in the order it chooses, on the fake of `event-bus`, repeats included. Faults it can inject: a repeat of any event, a gap in the sequence numbers.
