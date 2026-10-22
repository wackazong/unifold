# Notification

The contract of the capability `notification`: the function `notify`, what it sends to whoever provides `push`, and the texts. What a notification is for a client of the product is cited in [context](../explanation/context.md).

## The function

`notify(alert)` returns `sent`, `retry` or `failed`.

| Field of `alert` | Content | Used for |
|---|---|---|
| `alert_id` | UUID of the alert | Collapse identifier, data |
| `owner_id` | UUID of the owner | Addressee |
| `plant_id` | UUID of the plant | Data |
| `plant_name` | Name of the plant when the alert opened | Title |
| `quantity`, `bound` | What the alert is about | Choice of the text |
| `value` | The judged value | Text |
| `threshold` | The threshold | Text |
| `opened_at` | Time of the reading that opened the alert | Data |

One call makes one request to the push service and waits at most 5 seconds for the answer.

## The request to the push service

| Part | Value |
|---|---|
| Addressee | The owner id |
| Collapse identifier | The alert id, in lower-case text form |
| Time to live | 24 hours |
| Title | `plant_name`, cut to 60 characters |
| Body | The text for `quantity` and `bound`, see below |
| Data `alert_id`, `plant_id`, `opened_at` | From the alert |
| Data `quantity`, `bound` | From the alert |

Two calls with the same `alert` produce requests that are equal in every part.

## Outcomes

| Answer of the push service | Outcome |
|---|---|
| Taken | `sent` |
| Refused: the request is malformed or too large | `failed` |
| Refused: nobody is registered for the addressee | `failed` |
| Refused: too many requests | `retry` |
| An error of the service itself | `retry` |
| No connection, or no answer within 5 seconds | `retry` |
| An answer `notifier` does not understand | `retry` |

## Examples

The alert `7d2c1c1e-…` of the plant "Monstera in the hall".

| Case | Call and answer of the push service | Outcome and request |
|---|---|---|
| Dry soil | `soil_moisture`/`min`, value 28.4, threshold 30.0; taken | `sent`; body "Needs water. Soil moisture is 28.4 %, below 30.0 %." |
| Dark | `light`/`min`, value 640, threshold 800; taken | `sent`; body "Needs more light. The brightest reading of the last day was 640 lux, below 800 lux." |
| Frost | `temperature`/`min`, value -3.5, threshold 5.0; taken | `sent`; body "Too cold. It is -3.5 °C, below 5.0 °C." |
| Called again | The first case once more | `sent`; a request equal to the first in every part, collapse identifier `7d2c1c1e-…` |
| Busy | Any alert; refused with "too many requests" | `retry` |
| Silence | Any alert; no answer within 5 seconds | `retry`, returned within 6 seconds |
| Nobody registered | Any alert; refused, no phone for the owner | `failed` |
| Long name | A plant name of 80 characters; taken | `sent`; the title is its first 60 characters |
| Unknown quantity | `soil_ph`/`min`; taken | `sent`; body "Needs attention." |

## Texts

The title is the name of the plant. The body is chosen by quantity and bound. `{value}` and `{threshold}` are written with the number of decimals of the resolution of the quantity and a decimal point.

| `quantity` | `bound` | Body |
|---|---|---|
| `soil_moisture` | `min` | Needs water. Soil moisture is {value} %, below {threshold} %. |
| `soil_moisture` | `max` | Too wet. Soil moisture is {value} %, above {threshold} %. |
| `light` | `min` | Needs more light. The brightest reading of the last day was {value} lux, below {threshold} lux. |
| `light` | `max` | Gets too much light. The brightest reading of the last day was {value} lux, above {threshold} lux. |
| `temperature` | `min` | Too cold. It is {value} °C, below {threshold} °C. |
| `temperature` | `max` | Too warm. It is {value} °C, above {threshold} °C. |
| any other | any | Needs attention. |

- A body is at most 120 characters long after the numbers are filled in.
- The texts are English. The data fields allow a receiver to word the message itself.
- The text does not say when the reading was taken. `opened_at` is in the data.
