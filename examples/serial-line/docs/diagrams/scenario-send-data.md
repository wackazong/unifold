<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# Scenario: send-data

**serial-line** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The host sends data inside an open session**
Source: proto §5.3
Given: `session.host` is open
Expect: one frame `1F 03 03 68 69 C2` on the line for the data `68 69`; nothing is read

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
  participant ptransport as transport<br/>«adapter»<br/>Sends and receives frames over<br/>the serial line
  participant ptransport__serial as transport/serial<br/>«adapter»<br/>Moves frames through the serial<br/>port with deadlines
  participant pcodec as codec<br/>«logic»<br/>Encodes a payload into the bytes<br/>of a frame and decodes a frame<br/>from bytes
  participant puart as uart<br/>The serial port of the host<br/>computer, as a byte stream
  Note over psession: open
  phost->>psession: 1 · send([68, 69]) → ok
  activate psession
  psession->>ptransport: 2 · send([03, 68, 69]) → ok
  activate ptransport
  ptransport__serial->>pcodec: 3 · encode([03, 68, 69])
  activate pcodec
  pcodec-->>ptransport__serial: ↩ 3 · 1F 03 03 68 69 C2
  deactivate pcodec
  ptransport__serial->>puart: 4 · write([1F, 03, 03, 68, 69, C2]) → ok
  deactivate ptransport
  deactivate psession
  Note over phost,puart: wrap: Expect: one frame `1F 03 03 68 69 C2` on the line for the data `68 69`#59; nothing is read
```

| # | Caller | Target | Call | Kind | Result | State | Contract |
|---|---|---|---|---|---|---|---|
| 1 | `host` | `session` | `send([68, 69])` | command | ok | open | [host](../references/host.md) |
| 2 | `session` | `transport` | `send([03, 68, 69])` | command | ok |  | [transport](../references/transport.md) |
| 3 | `transport/serial` | `codec` | `encode([03, 68, 69])` | query | 1F 03 03 68 69 C2 |  | [frames](../references/frames.md) |
| 4 | `transport/serial` | `uart` | `write([1F, 03, 03, 68, 69, C2])` | command | ok |  | [uart](../references/uart.md) |
