# Runtime of alerts

Scenarios that cross the children of this unit and that no single child can tell. Which children exist is in the [component diagram](../diagrams/component.md).

## The life of an alert

An alert has two things that change: its state and the state of its notification. They are independent; an alert can close while its notification is still owed. The notification is sent all the same.

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

The first diagram is the state of the alert, the second the state of its notification. The three ways to close set `closed_reason` to `recovered`, `threshold_changed` and `expired`.

| Transition | Decided by | Stored by |
|---|---|---|
| open, closed with `recovered` or `threshold_changed` | [rules](../../rules/README.md), when a reading is judged | [server](../../server/README.md) |
| closed with `expired` | [server](../../server/README.md), by time | [server](../../server/README.md) |
| `pending` to `sent` or `failed` | the answer of [notifier](../../notifier/README.md), or 24 hours | [server](../../server/README.md) |

## Handling one reading

The scenario [handle-a-reading](../diagrams/scenario-handle-a-reading.md) follows one reading event through the direct children of `alerts` and its needs: `server` reads the evaluation state, `rules` judges the reading with the thresholds that `plant-lookup` fetches, `server` stores the alerts and the new state in one transaction and confirms the event, and `notifier` hands the notification of an opened alert to the push service.

The last step, notifying, is not tied to the event. It runs for every stored alert whose notification is pending, also after a restart.
