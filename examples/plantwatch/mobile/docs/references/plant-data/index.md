# plant-data

Contract of `sync.plant-data`: the queries, commands and guarantees of the capability through which the data on the phone is read and changed. The description is independent of a programming language. Reading, plant, thresholds, change state, alert, session and the ages of data are the things cited in [context.md](../../explanation/context.md). Notation: wit.
Sources: the public API and the reading schema of plantwatch, decisions 0001 and 0003 of `mobile`, decisions 0001 and 0002 of `sync`.

## Parts

Every query has two forms: "get" returns the answer once; "observe" returns it and returns it again whenever it changes.

| Part | What it is |
|---|---|
| [plants](plants.md) | every plant with its newest reading, open alerts and the age of its readings |
| [plant](plant.md) | the same for one plant |
| [history](history.md) | the readings of a plant in a span of time, raw or aggregated |
| [alerts](alerts.md) | open alerts, and alerts closed within the last 90 days |
| [exchange-state](exchange-state.md) | session, owner, last exchange, what is waiting |
| [start](start.md) | the phone acts for a new owner |
| [join](join.md) | the phone acts for an existing owner |
| [token-for-another-phone](token-for-another-phone.md) | a further token for the same owner |
| [leave](leave.md) | the phone leaves its owner |
| [create-plant](create-plant.md), [change-plant](change-plant.md), [remove-plant](remove-plant.md) | the plants of the owner |
| [dismiss-refusal](dismiss-refusal.md) | a refused change is dismissed |
| [refresh](refresh.md) | a fetch from sensor sticks in range and an exchange now |
| [command-failure](command-failure.md) | the failures of commands |
| [refusal-reason](refusal-reason.md) | the reasons of a refusal by the server |

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

## Limits

- 50 plants, 90 days of history per plant.
- One owner at a time.
- Every time is UTC. The capability converts neither times nor units of measure.

## Examples

Each case of a part starts with an `active` session and one plant, "Monstera", that is `in step` and has a sensor stick, unless the case says otherwise. The screens of `ui` are tested with these cases.

## Fake

A store in memory that a test loads with plants, readings and alerts; commands change it as the parts say and mark the plant `waiting`; "observe" delivers the new answer at once. Faults it can inject: a refusal by the server with any reason of `refusal-reason`, a session `lost`, `store unusable`.
