<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# States: host

The states of the contract [host](../references/host.md): what a consumer can see of the connection, and the parts that move it from one state to the next. A part that a state does not list must not be called in it. A failure that the table does not name leaves the state as it is.

```mermaid
stateDiagram-v2
  state "closed" as sclosed
  state "open" as sopen
  [*] --> sclosed
  sclosed --> sopen: open · ok
  sclosed --> sclosed: send · not-open
  sclosed --> sclosed: close · not-open
  sopen --> sopen: open · already-open
  sopen --> sopen: send · ok
  sopen --> sclosed: send · line-error
  sopen --> sclosed: close
```

| State | Part | Result | Next |
|---|---|---|---|
| closed | `open` | ok | open |
| closed | `send` | not-open | closed |
| closed | `close` | not-open | closed |
| open | `open` | already-open | open |
| open | `send` | ok | open |
| open | `send` | line-error | closed |
| open | `close` |  | closed |
