# Runtime of cloud

Scenarios that cross several services and that no single service can tell. Which services exist is in the [component diagram](../diagrams/component.md).

## An upload that leads to an alert

The sequence crosses several services and is therefore drawn here. It shows the direct children of `cloud` and the outside world.

```mermaid
sequenceDiagram
    participant C as client
    participant G as gateway
    participant I as ingest
    participant B as platform (event bus)
    participant P as plants
    participant A as alerts
    participant N as push service
    C->>G: upload batch, with token
    G->>G: verify token
    G->>I: batch, with owner id
    I->>I: validate, recognise duplicates
    I->>B: publish one event per new reading
    B-->>I: stored
    I-->>G: result per reading
    G-->>C: result per reading
    par history
        B->>P: reading event
        P->>P: add to history of the plant
    and evaluation
        B->>A: reading event
        A->>P: plant and thresholds of this sensor stick
        P-->>A: plant, owner, thresholds
        A->>A: evaluate, open or close alerts
        opt an alert has opened
            A->>N: one notification for the owner
        end
    end
    C->>G: query alerts and history
    G->>A: alerts of the owner
    G->>P: history of a plant
```

The upload is answered before history and evaluation have seen the reading. The two branches run independently and in any order.
