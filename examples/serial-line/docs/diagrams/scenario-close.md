<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: close

**serial-line** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The host closes the session and the device acknowledges**
Source: proto §5.2
Expect: one frame `1F 01 02 1B` on the line; after the device's `1F 01 82 92`, close returns ok and the state is closed

A unit is named by its path from `serial-line`; a capability or need of `serial-line` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it.

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
  phost->>psession: 1 · close
  activate psession
  psession->>pclock: 2 · now
  activate pclock
  pclock-->>psession: ↩ 2
  deactivate pclock
  psession->>ptransport: 3 · send
  activate ptransport
  ptransport__serial->>pcodec: 4 · encode
  activate pcodec
  pcodec-->>ptransport__serial: ↩ 4
  deactivate pcodec
  ptransport__serial->>puart: 5 · write
  activate puart
  deactivate puart
  deactivate ptransport
  psession->>ptransport: 6 · receive
  activate ptransport
  ptransport__serial->>puart: 7 · read
  activate puart
  puart-->>ptransport__serial: ↩ 7
  deactivate puart
  ptransport__serial->>ptransport__framing: 8 · feed
  activate ptransport__framing
  ptransport__framing->>pcodec: 9 · decode
  activate pcodec
  pcodec-->>ptransport__framing: ↩ 9
  deactivate pcodec
  ptransport__framing-->>ptransport__serial: ↩ 8
  deactivate ptransport__framing
  ptransport-->>psession: ↩ 6
  deactivate ptransport
  deactivate psession
  Note over phost,ptransport__framing: wrap: Expect: one frame `1F 01 02 1B` on the line#59; after the device's `1F 01 82 92`, close returns ok and the state is closed
```

| # | Caller | Target | Part | Kind | Contract |
|---|---|---|---|---|---|
| 1 | `host` | `session` | `close` | command | [host](../references/host.md) |
| 2 | `session` | `clock` | `now` | query | [clock](../references/clock.md) |
| 3 | `session` | `transport` | `send` | command | [transport](../references/transport.md) |
| 4 | `transport/serial` | `codec` | `encode` | query | [frames](../references/frames.md) |
| 5 | `transport/serial` | `uart` | `write` | command | [uart](../references/uart.md) |
| 6 | `session` | `transport` | `receive` | query | [transport](../references/transport.md) |
| 7 | `transport/serial` | `uart` | `read` | query | [uart](../references/uart.md) |
| 8 | `transport/serial` | `transport/framing` | `feed` | query | [framing](../../transport/docs/references/framing.md) |
| 9 | `transport/framing` | `codec` | `decode` | query | [frames](../references/frames.md) |
