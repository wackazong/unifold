# plant-data

Contract of `sync.plant-data`: the queries, commands and guarantees of the capability through which the data on the phone is read and changed. The description is independent of a programming language. Reading, plant, thresholds, change state, alert, session and the ages of data are the things cited in [context.md](../../explanation/context.md). Notation: wit.
Sources: the public API and the reading schema of plantwatch.
Binding: in-process

## Use

The caller lets the phone act for an owner: for a new one with `start`, or for an existing one with `join`. While the session is `active`, it reads and observes plants, history, alerts and the exchange state, changes plants and asks for a refresh. A query never uses the network. A command works without a network connection, except where its part asks for one. `leave` ends the session and removes the owner's data from the phone. When the server refuses the token at an exchange, the provider raises `session-lost`; the data then stays readable, no command changes it, and the phone either joins the owner again with `join` or leaves it with `leave`.

1. When `leave` fails with `network needed`, the session stays `active`, and `start` fails with `session exists`. The caller calls `leave` again once the phone has a network connection.
2. After `session-lost`, the queries still answer. `join` with a new token of the same owner makes the session `active` again; `leave` ends it, also without a network connection.

The exchange with the server runs by itself: after new readings, after a command, when a network connection appears, and when `refresh` asks for it. Readings of a sensor stick that is attached to no plant wait on the phone and are not uploaded.

Every query has two forms: "get" returns the answer once; "observe" returns it and returns it again whenever it changes. Every time is UTC; the capability converts neither times nor units of measure. Each case of a part starts with an `active` session and one plant, "Monstera", that is `in step` and has a sensor stick, unless the case says otherwise. The screens of `ui` are tested with these cases.

## States

Start: none.

| State | Part | Result | Next |
|---|---|---|---|
| none | `start` | ok | active |
| none | `join` | ok | active |
| none | `exchange-state` | | none |
| none | `plants` | `no session` | none |
| none | `plant` | `no session` | none |
| none | `history` | `no session` | none |
| none | `alerts` | `no session` | none |
| none | `create-plant` | `no session` | none |
| none | `change-plant` | `no session` | none |
| none | `remove-plant` | `no session` | none |
| none | `dismiss-refusal` | `no session` | none |
| none | `token-for-another-phone` | `no session` | none |
| none | `leave` | `no session` | none |
| active | `plants` | | active |
| active | `plant` | | active |
| active | `history` | | active |
| active | `alerts` | | active |
| active | `exchange-state` | | active |
| active | `token-for-another-phone` | | active |
| active | `create-plant` | | active |
| active | `change-plant` | | active |
| active | `remove-plant` | | active |
| active | `dismiss-refusal` | | active |
| active | `refresh` | | active |
| active | `leave` | ok | none |
| active | `leave` | `network needed` | active |
| active | `start` | `session exists` | active |
| active | `join` | `session exists` | active |
| active | `session-lost` | | lost |
| lost | `plants` | | lost |
| lost | `plant` | | lost |
| lost | `history` | | lost |
| lost | `alerts` | | lost |
| lost | `exchange-state` | | lost |
| lost | `refresh` | | lost |
| lost | `start` | `session exists` | lost |
| lost | `join` | ok | active |
| lost | `leave` | ok | none |

## Qualities

| Aspect | Guarantee |
|---|---|
| latency | a query never uses the network and never waits for a running exchange; within the limits of this contract, "get" answers within 100 milliseconds; after a change, an observer receives the new answer within 1 second, and changes in quick succession may arrive as one answer |
| durability | when a command returns, its effect survives a crash and a restart, and it reaches the server without further calls |
| ordering | changes to one plant reach the server in the order they were made |
| visibility | a reading that has been taken in from a sensor stick appears in "plants" and "history" from the moment its batch is acknowledged; when the server refuses a change, the plant shows the server's values, the state `refused` and the reason, until "dismiss refusal" or the next change |
| immutability | a reading that a query has returned is returned with the same values, time and flag for as long as it is kept |
| alerts | the answer contains exactly the alerts the server sent at the last exchange; the capability derives none from readings and thresholds |
| limits | 50 plants, 90 days of history per plant, one owner at a time; an upper limit of a plant that was set elsewhere survives every change made through this capability |

## Parts

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
| [session-lost](session-lost.md) | the server no longer accepts the token |
| [create-plant](create-plant.md), [change-plant](change-plant.md), [remove-plant](remove-plant.md) | the plants of the owner |
| [dismiss-refusal](dismiss-refusal.md) | a refused change is dismissed |
| [refresh](refresh.md) | a fetch from sensor sticks in range and an exchange now |
| [command-failure](command-failure.md) | the failures of commands |
| [refusal-reason](refusal-reason.md) | the reasons of a refusal by the server |

## Fake

A store in memory that a test loads with plants, readings and alerts; commands change it as the parts say and mark the plant `waiting`; "observe" delivers the new answer at once. Faults it can inject: a refusal by the server with any reason of `refusal-reason`, `session-lost`, `store unusable`.
