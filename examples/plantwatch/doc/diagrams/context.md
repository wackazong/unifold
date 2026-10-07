<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: plantwatch

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

`plantwatch` and the outside world: the ports it provides (rounded) and the things it needs from outside (hexagons).

```mermaid
flowchart LR
  u_root["plantwatch"]
  p_root___app_dui(["app-ui"])
  p_root___app_dui --> u_root
  p_root___test_dreport(["test-report"])
  p_root___test_dreport --> u_root
  n_root___soil_dprobe{{"soil-probe"}}
  u_root --> n_root___soil_dprobe
  n_root___ambient_dsensor{{"ambient-sensor"}}
  u_root --> n_root___ambient_dsensor
  n_root___push_dservice{{"push-service"}}
  u_root --> n_root___push_dservice
  n_root___container_dhost{{"container-host"}}
  u_root --> n_root___container_dhost
  classDef focus stroke-width:4px
  class u_root focus
```

| Port | Direction | Kind | Summary |
|---|---|---|---|
| app-ui | provided | ui | Shows the state of each plant and tells the user when to water it |
| test-report | provided | file | Result of the automated end-to-end tests, for developers and CI |
| soil-probe | needed | hardware | Capacitive soil moisture probe with an analogue output |
| ambient-sensor | needed | hardware | Light and temperature sensor on an I2C bus |
| push-service | needed | http | Registers phones for an owner and delivers a notification to them, for example APNs or FCM |
| container-host | needed | infrastructure | Runs containers, gives them a private network and persistent volumes |
