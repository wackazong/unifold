# Runtime of <folder-name>

<How this unit behaves while it runs. A story that walks through several units is a scenario in the manifest, where it is checked and drawn; here is what one unit does over time.>

## States

| State | Enters when | Leaves when | To |
|---|---|---|---|
| <state> | <event> | <event> | <state> |

```mermaid
stateDiagram-v2
    [*] --> <state>
    <state> --> <other-state>: <event>
```

## Start and stop

<What happens at start, in order, and what a stop leaves behind.>

## Timing and limits

<Timeouts and deadlines by constant name, concurrency, how much the unit holds at most.>

## Failure

<What the unit does when something fails: which state it falls back to, what it reports.>
