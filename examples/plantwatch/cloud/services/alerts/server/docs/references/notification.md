# Notification as server expects it

The contract of the need `notification`: the function that `server` calls
for every alert whose notification is owed. `server` defines the interface
it expects; whoever provides the function is held to it.

## The function

`notify(alert)` returns `sent`, `retry` or `failed`.

| Field of `alert` | Content |
|---|---|
| `alert_id`, `owner_id`, `plant_id` | UUIDs of the alert, of the owner to tell and of the plant |
| `plant_name` | The name of the plant when the alert opened |
| `quantity`, `bound` | What the alert is about |
| `value`, `threshold` | The judged value and the threshold of the opening |
| `opened_at` | The time of the reading that opened the alert |

| Outcome | Meaning | What `server` does |
|---|---|---|
| `sent` | The notification is on its way to the owner | Stores `sent` and never calls again for this alert |
| `retry` | The attempt failed for a reason that may pass | Calls again after the next waiting time |
| `failed` | This notification can never be delivered | Stores `failed` and does not call again |

## Requirements

- One call is one attempt. The function returns within 10 seconds and does
  not repeat by itself.
- `sent` is returned only when the notification was taken, never on a
  guess.
- The function may be called again for the same alert, also after an
  earlier call returned `sent` that `server` could not store. A second call
  replaces the first notification on a phone; it does not add one.
- The function keeps nothing between calls and needs nothing but `alert`.
- Every quantity and bound gets a notification, also one that the function
  has no special words for.

## Examples

| Case | Calls | Expected |
|---|---|---|
| Normal | `notify(A)` | `sent`; the owner's phones show one notification that names the plant |
| Outcome lost | `notify(A)` returns `sent`, `server` stops before storing it and calls `notify(A)` again | `sent`; the phones still show one notification for A |
| Passing failure | `notify(A)` while the way to the owner is blocked | `retry` within 10 seconds |
| Owner cannot be reached at all | `notify(A)` for an owner without a registered phone | `failed` |
| New quantity | `notify(B)` with a quantity added last week | `sent` |
