<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: garbage-before-frame

**serial-line** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**Bytes that are not part of a frame arrive before the ACK**
Source: proto §4.3
Expect: the bytes `00 FF 1E` before the frame `1F 01 81 9B` are dropped and receive returns the payload `81`

A unit is named by its path from `serial-line`; a capability or need of `serial-line` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant psession as session<br/>«stateful»<br/>Runs the host side of a session<br/>through its states and timeouts
  participant ptransport as transport<br/>«adapter»<br/>Sends and receives frames over<br/>the serial line
  participant ptransport__serial as transport/serial<br/>«adapter»<br/>Moves frames through the serial<br/>port with deadlines
  participant puart as uart<br/>The serial port of the host<br/>computer, as a byte stream
  participant ptransport__framing as transport/framing<br/>«logic»<br/>Cuts the byte stream from the<br/>line into frames
  participant pcodec as codec<br/>«logic»<br/>Encodes a payload into the bytes<br/>of a frame and decodes a frame<br/>from bytes
  psession->>ptransport: 1 · receive
  activate ptransport
  ptransport__serial->>puart: 2 · read
  activate puart
  puart-->>ptransport__serial: ↩ 2
  deactivate puart
  ptransport__serial->>ptransport__framing: 3 · feed
  activate ptransport__framing
  ptransport__framing->>pcodec: 4 · decode
  activate pcodec
  pcodec-->>ptransport__framing: ↩ 4
  deactivate pcodec
  ptransport__framing-->>ptransport__serial: ↩ 3
  deactivate ptransport__framing
  ptransport-->>psession: ↩ 1
  deactivate ptransport
  Note over psession,pcodec: wrap: Expect: the bytes `00 FF 1E` before the frame `1F 01 81 9B` are dropped and receive returns the payload `81`
```

| # | Caller | Target | Part | Kind | Contract |
|---|---|---|---|---|---|
| 1 | `session` | `transport` | `receive` | query | [transport](../references/transport.md) |
| 2 | `transport/serial` | `uart` | `read` | query | [uart](../references/uart.md) |
| 3 | `transport/serial` | `transport/framing` | `feed` | query | [framing](../../transport/docs/references/framing.md) |
| 4 | `transport/framing` | `codec` | `decode` | query | [frames](../references/frames.md) |
