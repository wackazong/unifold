<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: garbage-before-frame

**serial-line** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**Bytes that are not part of a frame arrive before the ACK**
Source: proto §4.3
Expect: the bytes `00 FF 1E` before the frame `1F 01 81 9B` are dropped and receive returns the payload `81`

A unit is named by its path from `serial-line`; a capability or need of `serial-line` is named bare. Every hop is a call along one connection of the map.

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
  ptransport__serial->>puart: 2 · read
  ptransport__serial->>ptransport__framing: 3 · feed
  ptransport__framing->>pcodec: 4 · decode
  Note over psession,pcodec: wrap: Expect: the bytes `00 FF 1E` before the frame `1F 01 81 9B` are dropped and receive returns the payload `81`
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `session` | `transport` | `receive` | [transport](../references/transport.md) |
| 2 | `transport/serial` | `uart` | `read` | [uart](../references/uart.md) |
| 3 | `transport/serial` | `transport/framing` | `feed` | [framing](../../transport/docs/references/framing.md) |
| 4 | `transport/framing` | `codec` | `decode` | [frames](../references/frames.md) |
