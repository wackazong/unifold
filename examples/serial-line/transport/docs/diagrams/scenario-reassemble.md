<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: reassemble

[serial-line](../../../docs/diagrams/component.md) / **transport** · [README](../../README.md) · [context](context.md) · [component](component.md)

**Two frames arrive in one read**
Source: proto §4.3
Expect: receive returns the first payload; the second frame waits in the buffer for the next call

A unit is named by its path from `transport`; a capability or need of `transport` is named bare. Every hop is a call along one connection of the map.

```mermaid
---
config:
  sequence:
    height: 92
---
sequenceDiagram
  participant ptransport as transport<br/>Send one payload as a frame#59;<br/>receive the next frame's payload
  participant pserial as serial<br/>«adapter»<br/>Moves frames through the serial<br/>port with deadlines
  participant pframing as framing<br/>«logic»<br/>Cuts the byte stream from the<br/>line into frames
  ptransport->>pserial: 1 · receive
  pserial->>pframing: 2 · feed
  Note over ptransport,pframing: wrap: Expect: receive returns the first payload#59; the second frame waits in the buffer for the next call
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `transport` | `serial` | `receive` | [transport](../../../docs/references/transport.md) |
| 2 | `serial` | `framing` | `feed` | [framing](../references/framing.md) |
