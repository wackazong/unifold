<!-- unifold:generated - do not edit; run `unifold generate` -->
# Context diagram: transport

[serial-line](../../../docs/diagrams/component.md) / **transport** · [README](../../README.md) · [component](component.md)

`transport` inside `serial-line`, with the units it is connected to. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["serial-line"]
    u_codec["codec (logic)"]
    u_session["session (stateful)"]
    u_transport["transport (adapter)"]
  end
  n_root___uart{{"uart"}}
  u_session -->|"transport"| u_transport
  u_transport -->|"frames"| u_codec
  u_transport -->|"uart"| n_root___uart
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_codec,u_session,u_transport planned
  class u_transport focus
```

| Unit | Kind | Responsibility | Status | Diagram |
|---|---|---|---|---|
| [codec](../../../codec/README.md) | logic | Encodes a payload into the bytes of a frame and decodes a frame from bytes | **planned** |  |
| [session](../../../session/README.md) | stateful | Runs the host side of a session through its states and timeouts | **planned** |  |
| [transport](../../README.md) | adapter | Sends and receives frames over the serial line | **planned** | [component](component.md) |

### Who provides what this unit needs

| Need | Kind | Contract | Provided by | Capability |
|---|---|---|---|---|
| frames |  | [contract](../../../docs/references/frames.md) | [codec](../../../codec/README.md) (planned) | frames |
| uart |  | [contract](../../../docs/references/uart.md) | outside the project, as need `uart` of the root | |

### Who uses what this unit provides

| Capability | Kind | Contract | Used by | As need |
|---|---|---|---|---|
| transport |  | [contract](../../../docs/references/transport.md) | [session](../../../session/README.md) (planned) | transport |
