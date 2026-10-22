# Runtime of plantwatch

Scenarios that cross several parts and that no single part can tell. Which parts exist is in the [component diagram](../diagrams/component.md).

## The path of a reading

This sequence crosses several parts and is therefore drawn here. It shows only the parts directly inside plantwatch and the outside world.

```mermaid
sequenceDiagram
    participant S as device (or emulator)
    participant P as mobile
    participant C as cloud
    participant N as push service
    loop every sampling interval
        S->>S: take a reading, store it
    end
    Note over S,P: phone comes into range
    P->>S: connect, ask for stored readings
    S-->>P: readings with tick counts
    P->>P: convert ticks to UTC, store
    P->>S: confirm up to sequence number n
    S->>S: delete confirmed readings
    Note over P,C: phone has a network connection
    P->>C: upload batch
    C-->>P: accepted, including duplicates
    C->>C: evaluate against thresholds
    opt plant needs attention, no open alert yet
        C->>N: notify the owner's phones
        N-->>P: notification
    end
    P->>C: fetch plants, history, alerts
```
