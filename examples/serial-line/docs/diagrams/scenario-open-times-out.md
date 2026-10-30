<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: open-times-out

**serial-line** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The host opens a session and the device stays silent**
Source: proto §5.1, §5.4
Expect: one frame `1F 01 01 12` on the line; once `OPEN_TIMEOUT_MS` have passed, open fails with `timeout` and the state is closed

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
  participant pclock as clock<br/>The current time in milliseconds
  participant ptransport as transport<br/>«adapter»<br/>Sends and receives frames over<br/>the serial line
  participant ptransport__serial as transport/serial<br/>«adapter»<br/>Moves frames through the serial<br/>port with deadlines
  participant pcodec as codec<br/>«logic»<br/>Encodes a payload into the bytes<br/>of a frame and decodes a frame<br/>from bytes
  participant puart as uart<br/>The serial port of the host<br/>computer, as a byte stream
  phost->>psession: 1 · open
  psession->>pclock: 2 · now
  psession->>ptransport: 3 · send
  ptransport__serial->>pcodec: 4 · encode
  ptransport__serial->>puart: 5 · write
  psession->>ptransport: 6 · receive
  ptransport__serial->>puart: 7 · read
  Note over phost,puart: wrap: Expect: one frame `1F 01 01 12` on the line#59; once `OPEN_TIMEOUT_MS` have passed, open fails with `timeout` and the state is closed
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `host` | `session` | `open` | [host](../references/host.md) |
| 2 | `session` | `clock` | `now` | [clock](../references/clock.md) |
| 3 | `session` | `transport` | `send` | [transport](../references/transport.md) |
| 4 | `transport/serial` | `codec` | `encode` | [frames](../references/frames.md) |
| 5 | `transport/serial` | `uart` | `write` | [uart](../references/uart.md) |
| 6 | `session` | `transport` | `receive` | [transport](../references/transport.md) |
| 7 | `transport/serial` | `uart` | `read` | [uart](../references/uart.md) |
