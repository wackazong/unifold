<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: handle-a-reading

[plantwatch](../../../../../docs/diagrams/component.md) / [cloud](../../../../docs/diagrams/component.md) / **alerts** · [README](../../README.md) · [context](context.md) · [component](component.md)

**One reading event is judged, the alerts it causes are stored, and an opened alert is notified**
Source: decisions 0001 and 0002 of alerts
Expect: the alerts to open and close and the new evaluation state are stored in one transaction, then the event is confirmed; for an opened alert one notification is handed to the push service and the alert's notification becomes `sent`, also after a restart, since the delivery step is not tied to the event

A unit is named by its path from `alerts`; a capability or need of `alerts` is named bare. Every hop is a call along one connection of the map.

```mermaid
---
config:
  sequence:
    height: 124
---
sequenceDiagram
  participant pserver as server<br/>«app»<br/>Process that consumes readings,<br/>stores the alerts they lead to<br/>and answers queries about them
  participant pevent_dbus as event-bus<br/>«queue»<br/>A durable subscription that<br/>keeps the order per key and<br/>delivers again what was not<br/>confirmed
  participant preading_devents as reading-events<br/>«events»<br/>One event per accepted reading,<br/>at least once, in order of<br/>acceptance per sensor stick
  participant psql_ddb as sql-db<br/>«db»<br/>A schema of its own in a<br/>relational database with<br/>transactions and row locks
  participant prules as rules<br/>«library»<br/>Evaluates readings against the<br/>thresholds of a plant
  participant pplant_dlookup as plant-lookup<br/>«adapter»<br/>Looks up the plant a sensor<br/>stick is attached to, with owner<br/>and thresholds, in the registry<br/>of plants
  participant pplants_dapi as plants-api<br/>«http»<br/>An HTTP lookup that returns the<br/>plant a sensor stick is attached<br/>to, with owner and thresholds
  participant pnotifier as notifier<br/>«adapter»<br/>Turns an opened alert into one<br/>notification to the owner
  participant ppush as push<br/>«http»<br/>Takes one notification for an<br/>owner, with a collapse<br/>identifier, and delivers it to<br/>that owner's phones
  pserver->>pevent_dbus: 1 · deliver
  pserver->>preading_devents: 2 · reading-accepted
  pserver->>psql_ddb: 3 · transaction
  pserver->>prules: 4 · evaluate
  prules->>pplant_dlookup: 5 · lookup
  pplant_dlookup->>pplants_dapi: 6 · lookup-by-sensor
  pserver->>pevent_dbus: 7 · commit
  pserver->>pnotifier: 8 · notify
  pnotifier->>ppush: 9 · send
  Note over pserver,ppush: wrap: Expect: the alerts to open and close and the new evaluation state are stored in one transaction, then the event is confirmed#59; for an opened alert one notification is handed to the push service and the alert's notification becomes `sent`, also after a restart, since the delivery step is not tied to the event
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `server` | `event-bus` | `deliver` | [event-bus](../../../../docs/references/event-bus.md) |
| 2 | `server` | `reading-events` | `reading-accepted` | [reading-events](../../../../docs/references/reading-events.md) |
| 3 | `server` | `sql-db` | `transaction` | [sql-db](../../../../docs/references/sql-db.md) |
| 4 | `server` | `rules` | `evaluate` | [evaluation](../references/evaluation.md) |
| 5 | `rules` | `plant-lookup` | `lookup` | [thresholds](../references/thresholds.md) |
| 6 | `plant-lookup` | `plants-api` | `lookup-by-sensor` | [plants-api](../../../../docs/references/plants-api.md) |
| 7 | `server` | `event-bus` | `commit` | [event-bus](../../../../docs/references/event-bus.md) |
| 8 | `server` | `notifier` | `notify` | [notification](../references/notification.md) |
| 9 | `notifier` | `push` | `send` | [push-service](../../../../../docs/references/push-service.md) |
