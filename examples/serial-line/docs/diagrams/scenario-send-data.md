<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: send-data

**serial-line** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The host sends data inside an open session**
Source: proto §5.3
Expect: one frame `1F 03 03 68 69 C2` on the line for the data `68 69`; nothing is read

A unit is named by its path from `serial-line`; a capability or need of `serial-line` is named bare. Every hop is a call along one connection of the map.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant phost as host<br/>Open a session, send data, close
  participant psession as session<br/>«stateful»<br/>Runs the host side of a session<br/>through its states and timeouts
  participant ptransport as transport<br/>«adapter»<br/>Sends and receives frames over<br/>the serial line
  participant ptransport__serial as transport/serial<br/>«adapter»<br/>Moves frames through the serial<br/>port with deadlines
  participant pcodec as codec<br/>«logic»<br/>Encodes a payload into the bytes<br/>of a frame and decodes a frame<br/>from bytes
  participant puart as uart<br/>The serial port of the host<br/>computer, as a byte stream
  phost->>psession: 1 · send
  psession->>ptransport: 2 · send
  ptransport__serial->>pcodec: 3 · encode
  ptransport__serial->>puart: 4 · write
  Note over phost,puart: wrap: Expect: one frame `1F 03 03 68 69 C2` on the line for the data `68 69`#59; nothing is read
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `host` | `session` | `send` | [host](../references/host.md) |
| 2 | `session` | `transport` | `send` | [transport](../references/transport.md) |
| 3 | `transport/serial` | `codec` | `encode` | [frames](../references/frames.md) |
| 4 | `transport/serial` | `uart` | `write` | [uart](../references/uart.md) |
