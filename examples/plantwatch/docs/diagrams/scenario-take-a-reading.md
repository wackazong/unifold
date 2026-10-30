<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: take-a-reading

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The sensor stick wakes at the sampling time, takes a reading and stores it**
Source: runtime of device, the sleep and wake cycle
Expect: one reading with the next sequence number and the tick count of the measurement is in the log and survives power loss; a connected central is notified of it as Live reading and of the new Status; the board sleeps until the next alarm

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant pdevice__sampling as device/sampling<br/>«library»<br/>Takes a calibrated reading at<br/>every sampling interval
  participant pdevice__hal as device/hal<br/>«adapter»<br/>Hardware abstraction of the<br/>sensor stick board
  participant psoil_dprobe as soil-probe<br/>«hardware»<br/>Capacitive soil moisture probe<br/>with an analogue output
  participant pambient_dsensor as ambient-sensor<br/>«hardware»<br/>Light and temperature sensor on<br/>an I2C bus
  participant pdevice__store as device/store<br/>«library»<br/>Keeps readings on the sensor<br/>stick until they have been<br/>delivered
  participant pdevice__link as device/link<br/>«library»<br/>Implements the BLE profile on<br/>top of the radio
  pdevice__hal-)pdevice__sampling: 1 · alarm
  activate pdevice__sampling
  pdevice__sampling->>pdevice__hal: 2 · ticks
  activate pdevice__hal
  pdevice__hal-->>pdevice__sampling: ↩ 2
  deactivate pdevice__hal
  pdevice__sampling->>pdevice__hal: 3 · measure
  activate pdevice__hal
  pdevice__hal->>psoil_dprobe: 4 · output
  activate psoil_dprobe
  psoil_dprobe-->>pdevice__hal: ↩ 4
  deactivate psoil_dprobe
  pdevice__hal->>pambient_dsensor: 5 · read
  activate pambient_dsensor
  pambient_dsensor-->>pdevice__hal: ↩ 5
  deactivate pambient_dsensor
  pdevice__hal-->>pdevice__sampling: ↩ 3
  deactivate pdevice__hal
  pdevice__sampling-)pdevice__store: 6 · new-reading
  activate pdevice__store
  pdevice__store->>pdevice__hal: 7 · write
  activate pdevice__hal
  deactivate pdevice__hal
  deactivate pdevice__store
  pdevice__sampling-)pdevice__link: 8 · new-reading
  activate pdevice__link
  pdevice__link->>pdevice__hal: 9 · send
  activate pdevice__hal
  deactivate pdevice__hal
  deactivate pdevice__link
  pdevice__sampling->>pdevice__hal: 10 · set-alarm
  activate pdevice__hal
  deactivate pdevice__hal
  deactivate pdevice__sampling
  Note over pdevice__sampling,pdevice__link: wrap: Expect: one reading with the next sequence number and the tick count of the measurement is in the log and survives power loss#59; a connected central is notified of it as Live reading and of the new Status#59; the board sleeps until the next alarm
```

| # | Caller | Target | Part | Kind | Contract |
|---|---|---|---|---|---|
| 1 | `device/sampling` | `device/hal` | `alarm` | event | [timer](../../device/docs/references/timer.md) |
| 2 | `device/sampling` | `device/hal` | `ticks` | query | [timer](../../device/docs/references/timer.md) |
| 3 | `device/sampling` | `device/hal` | `measure` | query | [sensor-io](../../device/docs/references/sensor-io.md) |
| 4 | `device/hal` | `soil-probe` | `output` | query | [soil-probe](../references/soil-probe.md) |
| 5 | `device/hal` | `ambient-sensor` | `read` | query | [ambient-sensor](../references/ambient-sensor.md) |
| 6 | `device/store` | `device/sampling` | `new-reading` | event | [readings](../../device/docs/references/readings.md) |
| 7 | `device/store` | `device/hal` | `write` | command | [flash](../../device/docs/references/flash.md) |
| 8 | `device/link` | `device/sampling` | `new-reading` | event | [readings](../../device/docs/references/readings.md) |
| 9 | `device/link` | `device/hal` | `send` | command | [radio](../../device/docs/references/radio.md) |
| 10 | `device/sampling` | `device/hal` | `set-alarm` | command | [timer](../../device/docs/references/timer.md) |
