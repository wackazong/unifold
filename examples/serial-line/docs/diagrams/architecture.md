<!-- unifold:generated - do not edit; run `unifold generate` -->
# Architecture diagram: serial-line

**serial-line** · [README](../../README.md) · [component](component.md)

`serial-line` opened up 3 levels deep. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["serial-line"]
    u_codec["codec (logic)"]
    u_session["session (stateful)"]
    subgraph u_transport["transport (adapter)"]
      u_transport__framing["framing (logic)"]
      u_transport__serial["serial (adapter)"]
    end
  end
  n_root___clock{{"clock"}}
  n_root___uart{{"uart"}}
  p_root___host(["host"])
  u_session -->|"transport"| u_transport__serial
  u_session -->|"clock"| n_root___clock
  u_transport__serial -->|"frames"| u_codec
  u_transport__framing -->|"frames"| u_codec
  u_transport__serial -->|"uart"| n_root___uart
  p_root___host --> u_session
  u_transport__serial -->|"framing"| u_transport__framing
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
  class u_codec,u_session,u_transport,u_transport__framing,u_transport__serial planned
```

| Unit | Kind | Responsibility | Status | Diagram |
|---|---|---|---|---|
| [codec](../../codec/README.md) | logic | Encodes a payload into the bytes of a frame and decodes a frame from bytes | **planned** |  |
| [session](../../session/README.md) | stateful | Runs the host side of a session through its states and timeouts | **planned** |  |
| [transport](../../transport/README.md) | adapter | Sends and receives frames over the serial line | **planned** | [component](../../transport/docs/diagrams/component.md) |
| [framing](../../transport/framing/README.md) | logic | Cuts the byte stream from the line into frames | **planned** |  |
| [serial](../../transport/serial/README.md) | adapter | Moves frames through the serial port with deadlines | **planned** |  |
