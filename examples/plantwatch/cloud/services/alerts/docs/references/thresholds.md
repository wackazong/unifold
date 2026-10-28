# thresholds

Contract of `plant-lookup.thresholds`: the function `lookup`, how `plant-lookup` turns the answers of whoever provides `plants-api` into its three answers, and how long it keeps them. The rules for calls that it follows are cited in [context](../explanation/context.md). Notation: wit.
Sources: the lookup by sensor id of `plants-api`; decision 0001 of `plant-lookup`.

## Parts

### lookup

Kind: query

```wit
lookup: func(sensor-id: string) -> lookup-answer;
```

Pre: none; a `sensor_id` that is not 16 lower-case hex digits gets `unattached` without a request.
Result: one of `attached`, `unattached` and `unavailable`, from memory or from one request, a `GET` of the lookup by sensor id without an owner header. Quantity names and numbers in `thresholds` are passed on unchanged. `lookup` has no effect that its caller can observe.

| What comes back | Answer | Kept |
|---|---|---|
| `200` with a plant | `attached` | 60 seconds |
| `404` with the code `not_found` | `unattached` | 60 seconds |
| `503`, no connection, or no response within 5 seconds | repeat, see below | no |
| any other status, or a body that cannot be read | `unavailable` | no |

A failed request is repeated at most twice, after 0.2 and after 1 second; after the third failure the answer is `unavailable`. An answer is kept per sensor id, in the memory of the instance, with the time at which the request for it was sent. A call within 60 seconds after that time is answered from memory; a later call sends a new request, and the old answer is not used again. At most 10 000 answers are kept; beyond that the oldest is dropped. Two calls for the same sensor id at the same moment share one request.

| Situation | `lookup` returns within |
|---|---|
| answer from memory | 1 ms |
| the registry answers | the time of one request, at most 5 seconds |
| the registry does not answer | 17 seconds: three waits of 5 seconds and the pauses |

Errors: none; `lookup` raises no error. `unavailable` is an answer.
Examples: the registry holds the plant P of owner A with the sensor stick `00a1b2c3d4e5f607` and the lower threshold 30.0 for soil moisture.

| Case | Call | Requests sent | Answer |
|---|---|---|---|
| first call | `lookup("00a1b2c3d4e5f607")` at 09:00:00 | 1 | `attached`, P, A, `{soil_moisture: {min: 30.0}}` |
| again soon | the same at 09:00:59 | 0 | the same |
| after a change | the threshold is set to 35.0 at 09:00:10; call at 09:01:01 | 1 | `attached` with `min` 35.0 |
| no thresholds | a plant without thresholds | 1 | `attached` with `{}` |
| not attached | `lookup("ffffffffffffffff")` | 1 | `unattached` |
| malformed id | `lookup("00A1")` | 0 | `unattached` |
| short outage | `503`, then `200` | 2 | `attached`, after about 0.2 seconds |
| outage | the registry refuses connections; an answer from 09:00:00 exists; call at 09:02:00 | 3 | `unavailable` |
| unknown quantity | the plant has thresholds for `soil_ph` | 1 | `attached`; `thresholds` contains `soil_ph` |

### lookup-answer

Kind: type

```wit
variant lookup-answer {
  attached(attached-plant),
  unattached,
  unavailable,
}
```

### attached-plant

Kind: type

```wit
record attached-plant { plant-id: string, owner-id: string, name: string, thresholds: list<tuple<string, bounds>> }
record bounds { min: option<f64>, max: option<f64> }
```

| Field | Content |
|---|---|
| plant-id, owner-id | UUIDs in lower-case text form |
| name | the name of the plant, 1 to 60 characters |
| thresholds | per quantity name an object with `min`, `max` or both, as numbers in the unit of the quantity; a quantity without thresholds is absent; a plant without thresholds has an empty object |

## Fake

Answers per sensor id what a test has scripted, `unattached` by default, and replays the examples. Faults it can inject: `unavailable` for the next call, a delay of up to 17 seconds.
