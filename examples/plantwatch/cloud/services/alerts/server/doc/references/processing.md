# Processing in server

What `server` stores and what it does in each of its four activities. It
is internal to this unit. The alert and its life as a caller sees them are
cited in [context](../context.md).

## What is stored

| Table | One row per | Key | Content |
|---|---|---|---|
| `alert` | alert | `alert_id` | The fields of the alert, the owner id, the plant name at opening, the sensor id, `checked_at`, and the time of the next delivery attempt |
| `evaluation_state` | sensor stick | `sensor_id` | The state that `evaluation` returned last, as JSON, the plant id it named, and a version counter |

A unique index on `alert` over plant id, quantity and bound, limited to
rows with state `open`, allows one open alert per plant, quantity and
bound.

## Handling an event

For one event of an accepted reading:

| Step | Action |
|---|---|
| 1 | Read the row of `evaluation_state` for the sensor id, if any |
| 2 | Call `evaluation` with the reading and the stored state. No transaction is open during the call. |
| 3 | If the answer is "cannot decide now": stop. The event stays unconfirmed and is delivered again. |
| 4 | In one transaction: check that the version of the state row is the one read in step 1; insert an alert with `notification` = `pending` for every "open"; close the open alert for every "close"; set `checked_at` of all open alerts of the plant to now; write the new state with the next version |
| 5 | If the version check fails: roll back and start again at step 1 |
| 6 | Confirm the event |
| 7 | If an alert was inserted: wake the delivery of notifications |

- If no plant is returned, step 4 writes only the state.
- A "close" for which no open alert exists is ignored.
- An "open" that violates the unique index is a fault of `evaluation` or
  of the stored state. `server` rolls back, reports it, drops the state
  row of the sensor stick and confirms the event.

## Delivering notifications

A loop takes alerts with `notification` = `pending` whose next attempt is
due, one at a time under a row lock, so that two instances do not notify
the same alert at the same moment.

| Answer of `notification` | Change |
|---|---|
| done | `notification` = `sent` |
| failed for good | `notification` = `failed` |
| try again later, or no answer within 10 seconds | Next attempt after the next waiting time |

| Attempt | Waiting time before it |
|---|---|
| 1 | none: right after the alert is stored |
| 2 | 10 seconds |
| 3 | 1 minute |
| 4 | 5 minutes |
| 5 and later | 15 minutes |

An alert whose notification is still `pending` 24 hours after the alert
was stored gets `failed`. An alert that has closed in the meantime is
notified all the same.

## Expiry and retention

A job runs once per hour.

| Rows | Action |
|---|---|
| Open alerts with `checked_at` more than 30 days ago | Close with `expired` and `closed_at` = now. Delete the `evaluation_state` rows that name the plant. |
| Closed alerts with `closed_at` more than 2 years ago | Delete |
| `evaluation_state` rows not written for 30 days | Delete |

## Answering queries

Every query has the owner id from `X-Owner-Id` in its condition. Lists
are read in descending order of `opened_at` through an index on owner id
and `opened_at`; the cursor is the `opened_at` and `id` of the last item.
