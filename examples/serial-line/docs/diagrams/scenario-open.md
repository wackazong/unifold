<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# Scenario: open

**serial-line** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The host opens a session and the device acknowledges**
Source: proto §5.1
Expect: one frame `1F 01 01 12` on the line; after the device's `1F 01 81 9B`, open returns ok and the state is open

A unit is named by its path from `serial-line`; a capability or need of `serial-line` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one. A step shows its result; a note on a provider's lifeline shows the state of a connection whose contract has states.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant phost as host<br/>Open a session, send data, close
  participant psession as session<br/>«stateful»<br/>Runs the host side of a session<br/>through its states and timeouts
  participant pclock as clock<br/>The current time in milliseconds
  participant ptransport as transport<br/>«adapter»<br/>Sends and receives frames over<br/>the serial line
  participant ptransport__serial as transport/serial<br/>«adapter»<br/>Moves frames through the serial<br/>port with deadlines
  participant pcodec as codec<br/>«logic»<br/>Encodes a payload into the bytes<br/>of a frame and decodes a frame<br/>from bytes
  participant puart as uart<br/>The serial port of the host<br/>computer, as a byte stream
  participant ptransport__framing as transport/framing<br/>«logic»<br/>Cuts the byte stream from the<br/>line into frames
  Note over psession: closed
  phost->>psession: 1 · open() → ok
  activate psession
  Note over psession: open
  psession->>pclock: 2 · now()
  activate pclock
  pclock-->>psession: ↩ 2 · 1000
  deactivate pclock
  psession->>ptransport: 3 · send([01]) → ok
  activate ptransport
  ptransport__serial->>pcodec: 4 · encode([01])
  activate pcodec
  pcodec-->>ptransport__serial: ↩ 4 · 1F 01 01 12
  deactivate pcodec
  ptransport__serial->>puart: 5 · write([1F, 01, 01, 12]) → ok
  deactivate ptransport
  psession->>ptransport: 6 · receive(OPEN_TIMEOUT_MS)
  activate ptransport
  ptransport__serial->>puart: 7 · read(64, 50)
  activate puart
  puart-->>ptransport__serial: ↩ 7 · [1F, 01, 81, 9B]
  deactivate puart
  ptransport__serial->>ptransport__framing: 8 · feed([], [1F, 01, 81, 9B])
  activate ptransport__framing
  ptransport__framing->>pcodec: 9 · decode([1F, 01, 81, 9B])
  activate pcodec
  pcodec-->>ptransport__framing: ↩ 9 · payload [81], used 4
  deactivate pcodec
  ptransport__framing-->>ptransport__serial: ↩ 8 · frames [[81]], rest [], dropped 0
  deactivate ptransport__framing
  ptransport-->>psession: ↩ 6 · [81]
  deactivate ptransport
  deactivate psession
  Note over phost,ptransport__framing: wrap: Expect: one frame `1F 01 01 12` on the line#59; after the device's `1F 01 81 9B`, open returns ok and the state is open
```

| # | Caller | Target | Call | Kind | Result | State | Contract |
|---|---|---|---|---|---|---|---|
| 1 | `host` | `session` | `open()` | command | ok | open | [host](../references/host.md) |
| 2 | `session` | `clock` | `now()` | query | 1000 |  | [clock](../references/clock.md) |
| 3 | `session` | `transport` | `send([01])` | command | ok |  | [transport](../references/transport.md) |
| 4 | `transport/serial` | `codec` | `encode([01])` | query | 1F 01 01 12 |  | [frames](../references/frames.md) |
| 5 | `transport/serial` | `uart` | `write([1F, 01, 01, 12])` | command | ok |  | [uart](../references/uart.md) |
| 6 | `session` | `transport` | `receive(OPEN_TIMEOUT_MS)` | query | [81] |  | [transport](../references/transport.md) |
| 7 | `transport/serial` | `uart` | `read(64, 50)` | query | [1F, 01, 81, 9B] |  | [uart](../references/uart.md) |
| 8 | `transport/serial` | `transport/framing` | `feed([], [1F, 01, 81, 9B])` | query | frames [[81]], rest [], dropped 0 |  | [framing](../../transport/docs/references/framing.md) |
| 9 | `transport/framing` | `codec` | `decode([1F, 01, 81, 9B])` | query | payload [81], used 4 |  | [frames](../references/frames.md) |
