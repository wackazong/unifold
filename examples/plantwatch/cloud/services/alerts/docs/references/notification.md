# notification

Contract of `notifier.notification`: the function `notify`, what it sends to whoever provides `push`, and the texts. What a notification is for a client of the product is cited in [context](../explanation/context.md). Notation: wit.
Sources: the push service contract of plantwatch.
Binding: in-process

## Use

The caller calls `notify` for an opened alert and reads the outcome. Two calls with the same alert produce equal requests, so the caller may call again after `retry`. A repeat that reaches a phone after the owner has dismissed the first notification is shown again; a caller keeps repeats rare by not calling `notify` again after `sent`. Every data field of the request is at most 40 characters. The connection has no state: `notify` may be called at any time.

## Qualities

| Aspect | Guarantee |
|---|---|
| timeout | the caller waits up to 10 seconds for an outcome; `notify` returns within 6 seconds; a push service that has not answered within 5 seconds counts as `retry` |
| idempotency | two calls with the same `alert` produce requests that are equal in every part, with the alert id as the collapse identifier |
| limits | the title is at most 60 characters, the body at most 120 characters after the numbers are filled in |

## Parts

### notify

Kind: operation

```wit
notify: func(alert: opened-alert) -> outcome;
```

Pre: none.
Result: one request to the push service, and the answer. The request:

| Part | Value |
|---|---|
| addressee | the owner id |
| collapse identifier | the alert id, in lower-case text form |
| time to live | 24 hours |
| title | `plant_name`, cut to 60 characters |
| body | the text for `quantity` and `bound`, see below |
| data `alert_id`, `plant_id`, `opened_at` | from the alert |
| data `quantity`, `bound` | from the alert |

The title is the name of the plant. The body is chosen by quantity and bound; `{value}` and `{threshold}` are written with the number of decimals of the resolution of the quantity and a decimal point. The texts are English; the data fields allow a receiver to word the message itself. The text does not say when the reading was taken; `opened_at` is in the data.

| `quantity` | `bound` | Body |
|---|---|---|
| `soil_moisture` | `min` | Needs water. Soil moisture is {value} %, below {threshold} %. |
| `soil_moisture` | `max` | Too wet. Soil moisture is {value} %, above {threshold} %. |
| `light` | `min` | Needs more light. The brightest reading of the last day was {value} lux, below {threshold} lux. |
| `light` | `max` | Gets too much light. The brightest reading of the last day was {value} lux, above {threshold} lux. |
| `temperature` | `min` | Too cold. It is {value} °C, below {threshold} °C. |
| `temperature` | `max` | Too warm. It is {value} °C, above {threshold} °C. |
| any other | any | Needs attention. |

Errors: none as a failure of the call; the outcome says what happened. `sent` when the push service took the request. `failed` when it refused the request as malformed or too large, or because nobody is registered for the addressee. `retry` when it refused for too many requests, on an error of the service itself, with no connection or no answer within 5 seconds, or on an answer `notifier` does not understand.
Examples: the alert `7d2c1c1e-…` of the plant "Monstera in the hall"; `Given` is the answer of the push service.

| Case | Given | Input | Expected |
|---|---|---|---|
| dry soil | the request is taken | `soil_moisture`/`min`, value 28.4, threshold 30.0 | `sent`; body "Needs water. Soil moisture is 28.4 %, below 30.0 %." |
| dark | the request is taken | `light`/`min`, value 640, threshold 800 | `sent`; body "Needs more light. The brightest reading of the last day was 640 lux, below 800 lux." |
| frost | the request is taken | `temperature`/`min`, value -3.5, threshold 5.0 | `sent`; body "Too cold. It is -3.5 °C, below 5.0 °C." |
| called again | the request is taken | the alert of `dry soil` once more | `sent`; a request equal to the first in every part, collapse identifier `7d2c1c1e-…` |
| busy | refused with "too many requests" | any alert | `retry` |
| silence | no answer within 5 seconds | any alert | `retry`, returned within 6 seconds |
| nobody registered | refused, no phone for the owner | any alert | `failed` |
| long name | the request is taken | an alert of a plant whose name has 60 characters | `sent`; the title is the whole name |
| unknown quantity | the request is taken | `soil_ph`/`min` | `sent`; body "Needs attention." |

### opened-alert

Kind: type

```wit
record opened-alert {
  alert-id: string,
  owner-id: string,
  plant-id: string,
  plant-name: string,
  quantity: string,
  bound: string,
  value: f64,
  threshold: f64,
  opened-at: string,
}
```

| Field | Content | Used for |
|---|---|---|
| alert-id | UUID of the alert | collapse identifier, data |
| owner-id | UUID of the owner | addressee |
| plant-id | UUID of the plant | data |
| plant-name | name of the plant when the alert opened | title |
| quantity, bound | what the alert is about | choice of the text |
| value | the judged value | text |
| threshold | the threshold | text |
| opened-at | time of the reading that opened the alert | data |

### outcome

Kind: type

```wit
enum outcome { sent, retry, failed }
```

## Fake

Records every call and answers `sent`; a test reads the requests it would have made. Faults it can inject: `retry` or `failed` for the next call.
