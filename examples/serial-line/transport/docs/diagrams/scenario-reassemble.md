<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# Scenario: reassemble

[serial-line](../../../docs/diagrams/component.md) / **transport** · [README](../../README.md) · [context](context.md) · [component](component.md)

**Two frames arrive in one read**
Source: proto §4.3
Expect: receive returns the first payload; the second frame waits in the buffer for the next call

A unit is named by its path from `transport`; a capability or need of `transport` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one. A step shows its result; a note on a provider's lifeline shows the state of a connection whose contract has states.

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
  ptransport->>pserial: 1 · receive(OPEN_TIMEOUT_MS)
  activate pserial
  pserial->>pframing: 2 · feed([], [1F, 01, 81, 9B, 1F, 00, 00])
  activate pframing
  pframing-->>pserial: ↩ 2 · frames [[81], []], rest [], dropped 0
  deactivate pframing
  pserial-->>ptransport: ↩ 1 · [81]
  deactivate pserial
  Note over ptransport,pframing: wrap: Expect: receive returns the first payload#59; the second frame waits in the buffer for the next call
```

| # | Caller | Target | Call | Kind | Result | State | Contract |
|---|---|---|---|---|---|---|---|
| 1 | `transport` | `serial` | `receive(OPEN_TIMEOUT_MS)` | query | [81] |  | [transport](../../../docs/references/transport.md) |
| 2 | `serial` | `framing` | `feed([], [1F, 01, 81, 9B, 1F, 00, 00])` | query | frames [[81], []], rest [], dropped 0 |  | [framing](../references/framing.md) |
