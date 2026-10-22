# Runtime of alerts

Scenarios that cross the children of this unit and that no single child
can tell. Which children exist is in the
[component diagram](../diagrams/component.md).

## The life of an alert

An alert has two things that change: its state and the state of its
notification. They are independent; an alert can close while its
notification is still owed. The notification is sent all the same.

```mermaid
stateDiagram-v2
    [*] --> open: judged value beyond threshold and no open alert
    open --> open: further readings beyond threshold
    open --> closed: recovered by a margin
    open --> closed: threshold gone or moved
    open --> closed: no reading judged for 30 days
    closed --> [*]: deleted 2 years after closing
```

```mermaid
stateDiagram-v2
    [*] --> pending: alert stored
    pending --> pending: push service says try again
    pending --> sent: push service took it
    pending --> failed: refused for good or 24 hours passed
    sent --> [*]
    failed --> [*]
```

The first diagram is the state of the alert, the second the state of its
notification. The three ways to close set `closed_reason` to `recovered`,
`threshold_changed` and `expired`.

| Transition | Decided by | Stored by |
|---|---|---|
| open, closed with `recovered` or `threshold_changed` | [rules](../../rules/README.md), when a reading is judged | [server](../../server/README.md) |
| closed with `expired` | [server](../../server/README.md), by time | [server](../../server/README.md) |
| `pending` to `sent` or `failed` | the answer of [notifier](../../notifier/README.md), or 24 hours | [server](../../server/README.md) |

## Handling one reading

The sequence shows the direct children of `alerts` and its needs.

```mermaid
sequenceDiagram
    participant B as event-bus
    participant S as server
    participant R as rules
    participant L as plant-lookup
    participant P as plants-api
    participant D as sql-db
    participant N as notifier
    participant U as push
    B->>S: reading event
    S->>D: read evaluation state of the sensor stick
    S->>R: evaluate(reading, state)
    R->>L: lookup(sensor id)
    opt plant-lookup has to ask the registry
        L->>P: lookup by sensor id
        P-->>L: plant, owner, thresholds
    end
    L-->>R: attached, with plant, owner, thresholds
    R-->>S: plant, alerts to open or close, new state
    S->>D: store alerts and new state in one transaction
    D-->>S: committed
    S->>B: confirm event
    opt an alert was opened
        S->>N: notify(alert)
        N->>U: notification
        U-->>N: taken
        N-->>S: sent
        S->>D: notification = sent
    end
```

The last block, notifying, is not tied to the event. It runs for every
stored alert whose notification is pending, also after a restart.
