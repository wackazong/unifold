# Runtime of mobile

The scenarios that cross several parts and that no single part can tell. The diagrams show the app's parts [ble-client](../../ble-client/README.md), [sync](../../sync/README.md) and [ui](../../ui/README.md) as participants, next to the outside world.

## A paired sensor stick comes into range while the app is closed

The way of a reading from the sensor stick into the store, and on to the server when there is time. The operating system, `ble-client` and `sync` appear.

```mermaid
sequenceDiagram
    participant S as sensor stick
    participant O as operating system
    participant B as ble-client
    participant Y as sync
    participant C as server
    S-->>O: advertises
    O->>B: wakes the app: paired sensor stick present
    B->>S: connect, read current tick count
    loop per chunk, while the system lets the app run
        B->>S: ask for stored readings
        S-->>B: readings with tick counts
        B->>B: compute UTC time, drop invalid readings
        B->>Y: batch of readings
        Y->>Y: store durably
        Y-->>B: stored
        B->>S: confirm up to the last sequence number
    end
    B->>S: disconnect
    opt network available and run time left
        Y->>C: upload batch
        C-->>Y: accepted
    end
    Note over Y,C: otherwise the upload waits for the next opportunity
```

## Background fetching as the system sees the app

The states of the whole app between "nothing to do" and "fetching", as the operating system drives them.

```mermaid
stateDiagram-v2
    [*] --> Watching: first sensor stick paired
    Watching --> Fetching: system reports a paired sensor stick
    Watching --> Fetching: owner opens the app
    Fetching --> Fetching: next chunk
    Fetching --> Watching: all readings confirmed
    Fetching --> Watching: connection lost or run time over
    Watching --> Stopped: force-quit, Bluetooth off or permission withdrawn
    Stopped --> Watching: owner opens the app and the cause is gone
    Watching --> [*]: last sensor stick unpaired
```

In `Watching` the app does not run. The operating system holds the request and starts the app when a paired sensor stick appears. A fetch that ends early loses nothing: the sensor stick still holds every unconfirmed reading.

## The owner changes a threshold without a network connection

A change of the owner on its way through `ui` and `sync` to the server, and what the owner sees meanwhile.

```mermaid
sequenceDiagram
    actor U as owner
    participant I as ui
    participant Y as sync
    participant C as server
    U->>I: sets a new threshold
    I->>Y: change plant settings
    Y->>Y: store the change, mark it as waiting
    Y-->>I: plant with the new threshold, marked as waiting
    I-->>U: shows the new value and "not yet sent"
    Note over Y,C: later, with a network connection
    Y->>C: send the change
    C-->>Y: plant as the server holds it now
    Y->>Y: replace the plant, clear the mark
    Y-->>I: plant changed
    I-->>U: shows the value without the mark
```

Until the server has the new threshold, alerts follow the old one. The screen says so through the mark.
