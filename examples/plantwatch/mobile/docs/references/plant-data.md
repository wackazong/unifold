# Contract of `plant-data`

The queries, commands and guarantees of the capability through which the data on the phone is read and changed. The description is independent of a programming language. Reading, plant, thresholds, change state, alert, session and the ages of data are the things cited in [context.md](../explanation/context.md).

## Queries

Every query has two forms: "get" returns the answer once; "observe" returns it and returns it again whenever it changes.

| Query | Input | Answer |
|---|---|---|
| Plants | Nothing | Every plant, each with its newest reading or none, its open alerts and the age of its readings. Plants with an open alert come first, then by name. |
| Plant | Plant id | The same for one plant, or `unknown plant` |
| History | Plant id, span of time, resolution | The readings of the plant in ascending time |
| Alerts | Optionally a plant id | Open alerts, and alerts closed within the last 90 days, newest first |
| Exchange state | Nothing | See below |

### History

The history of a plant consists of the readings its sensor stick took while it was attached to the plant.

| Resolution | One entry per | Each entry holds |
|---|---|---|
| `raw` | Reading | The reading |
| `hourly` | Hour that has at least one reading | Minimum, mean and maximum of each measured quantity; whether any time in it is estimated |
| `daily` | Day in UTC that has at least one reading | The same |

A span reaches back at most 90 days. A `raw` span is at most 7 days long.

### Exchange state

| Field | Content |
|---|---|
| Session | `none`, `active` or `lost` |
| Owner id | The owner the phone acts for; none until the server has created the owner |
| Last exchange | UTC time of the last exchange with the server that succeeded, or none |
| Running | Whether an exchange is running now |
| Readings waiting | Number of readings the server has not confirmed |
| Changes waiting | Number of plants in the state `waiting` |
| Last failure | `no network`, `server unavailable`, `token not accepted` or none |

`none`: the phone acts for no owner yet; every other command fails. `lost`: the server no longer accepts the token. The data stays on the phone and stays readable; nothing is exchanged until the phone joins the owner again.

## Commands

| Command | Input | Result | Effect |
|---|---|---|---|
| Start | Nothing | Nothing | The phone acts for a new owner. The server creates the owner at the first exchange. Needs no network connection. |
| Join | A token of an existing owner | Nothing | The phone acts for that owner. The first exchange brings the owner's plants, alerts and history. |
| Token for another phone | Nothing | A token, or a failure | Obtains a further token for the same owner from the server. Needs a network connection. |
| Leave | Nothing | `left` or a failure | Uploads what is waiting, then removes plants, readings, alerts and the token from the phone |
| Create plant | Name, lower limits, optionally a sensor id | The plant id | The plant exists on the phone, `waiting` |
| Change plant | Plant id and any of name, lower limits, sensor id | Nothing | The plant has the new values, `waiting` |
| Remove plant | Plant id | Nothing | The plant, its alerts and its history are gone from the queries when the command returns |
| Dismiss refusal | Plant id | Nothing | A plant in the state `refused` becomes `in step` |
| Refresh | Nothing | The exchange state after the attempt | Asks for a fetch from sensor sticks in range and runs an exchange now |

"Change plant" with "sensor id: none" releases the sensor stick from the plant. Readings already in the history stay.

## Guarantees

- **Queries are local.** A query never uses the network and never waits for a running exchange. Within the limits of this contract, "get" answers within 100 milliseconds.
- **Observers see every final state.** After a change, an observer receives the new answer within 1 second. Changes in quick succession may arrive as one answer.
- **Commands are durable.** When a command returns, its effect survives a crash and a restart, and it reaches the server without further calls.
- **Commands keep their order.** Changes to one plant reach the server in the order they were made.
- **Readings are visible before upload.** A reading that has been taken in from a sensor stick appears in "plants" and "history" from the moment its batch is acknowledged.
- **Readings do not change.** A reading that a query has returned is returned with the same values, time and flag for as long as it is kept.
- **Alerts are the server's.** The answer contains exactly the alerts the server sent at the last exchange. The capability derives none from readings and thresholds.
- **A refusal is visible.** When the server refuses a change, the plant shows the server's values, the state `refused` and the reason, until "dismiss refusal" or the next change.
- **Limits it does not show are kept.** An upper limit of a plant that was set elsewhere survives every change made through this capability.

## Examples

Each case starts with an `active` session and one plant, "Monstera", that is `in step` and has a sensor stick.

| Case | Given | Expected |
|---|---|---|
| Offline read | No network connection; "get plants" | The plant with its newest reading, within 100 milliseconds |
| Reading taken in | A batch of 96 readings is stored; no exchange yet | "History" contains the 96 readings; "readings waiting" is 96 |
| Offline change | No network; "change plant" sets the lower limit of soil moisture to 25 | The command returns; "get plant" shows 25 and `waiting`; an observer of "plants" gets the plant within 1 second |
| Change confirmed | The next exchange succeeds | The plant is `in step`; "changes waiting" is 0 |
| Change refused | The server no longer has the plant | The plant is `refused` with `removed elsewhere` |
| Limit out of range | "Change plant" with a lower limit of 120 for soil moisture | `invalid`, naming the limit; nothing changes |
| 51st plant | 50 plants exist; "create plant" | `limit reached` |
| Hourly history | Four readings in one hour with soil moisture 41.2, 41.8, 42.1 and 42.5 | One entry: minimum 41.2, mean 41.9, maximum 42.5 |
| Before "start" | The session is `none`; "create plant" | `no session` |

## Failures of commands

| Failure | Commands | Meaning |
|---|---|---|
| `no session` | All but "start" and "join" | The session is `none` |
| `session exists` | Start, join | The phone already acts for an owner; "leave" comes first |
| `network needed` | Token for another phone, leave | No answer from the server |
| `invalid` | Create plant, change plant | Name empty or longer than 60 characters, or a limit outside the range of its quantity; with the field |
| `limit reached` | Create plant | The owner has 50 plants |
| `unknown plant` | Change, remove, dismiss | No plant with this id on the phone |
| `sensor stick in use` | Create plant, change plant | The sensor id is attached to another plant on this phone |
| `store unusable` | All, and all queries | The store on the phone was written by a newer version of the program |

A token that the server does not accept does not fail "join". It shows after the first exchange as the session `lost`.

## Reasons of a refusal by the server

| Reason | Meaning |
|---|---|
| `removed elsewhere` | The plant no longer exists on the server; it disappears from the phone as well |
| `sensor stick in use` | The server knows the sensor stick as attached to another plant |
| `limit reached` | The owner has 50 plants on the server |
| `not accepted` | Any other refusal; with the message the server gave |

## Limits

- 50 plants, 90 days of history per plant.
- One owner at a time.
- Every time is UTC. The capability converts neither times nor units of measure.
