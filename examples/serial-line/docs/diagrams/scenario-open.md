<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: open

**serial-line** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The host opens a session and the device acknowledges**
Source: proto §5.1
Expect: one frame `1F 01 01 12` on the line; after the device's `1F 01 81 9B`, open returns ok and the state is open

A unit is named by its path from `serial-line`; a capability or need of `serial-line` is named bare. Every hop is a call along one connection of the map.

```mermaid
sequenceDiagram
  participant phost as host
  participant psession as session
  participant pclock as clock
  participant ptransport as transport
  participant ptransport__serial as transport/serial
  participant pcodec as codec
  participant puart as uart
  participant ptransport__framing as transport/framing
  phost->>psession: 1 · open
  psession->>pclock: 2 · now
  psession->>ptransport: 3 · send
  ptransport__serial->>pcodec: 4 · encode
  ptransport__serial->>puart: 5 · write
  psession->>ptransport: 6 · receive
  ptransport__serial->>puart: 7 · read
  ptransport__serial->>ptransport__framing: 8 · feed
  ptransport__framing->>pcodec: 9 · decode
  Note over phost,ptransport__framing: Expect: one frame `1F 01 01 12` on the line; after the device's `1F 01 81 9B`, open returns ok and the state is open
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
| 8 | `transport/serial` | `transport/framing` | `feed` | [framing](../../transport/docs/references/framing.md) |
| 9 | `transport/framing` | `codec` | `decode` | [frames](../references/frames.md) |
