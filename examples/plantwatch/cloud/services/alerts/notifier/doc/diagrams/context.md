<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: notifier

[notifier](../../README.md)

`notifier` among its siblings inside `alerts`. Only connections that touch `notifier` are drawn. Arrows point from the side that needs something to the side that provides it. Rounded nodes are ports the framing unit provides, hexagons are its needs. Dashed arrows are alternative providers; dashed borders mark planned units.

```mermaid
flowchart LR
  subgraph u_cloud_services_alerts["alerts"]
    u_cloud_services_alerts_notifier["notifier"]
    u_cloud_services_alerts_rules["rules"]
    u_cloud_services_alerts_server["server"]
  end
  n_cloud_services_alerts_push{{"push"}}
  u_cloud_services_alerts_server -->|"notification"| u_cloud_services_alerts_notifier
  u_cloud_services_alerts_notifier -->|"push"| n_cloud_services_alerts_push
  click u_cloud_services_alerts_notifier href "../../README.md"
  click u_cloud_services_alerts_rules href "../../../rules/README.md"
  click u_cloud_services_alerts_server href "../../../server/README.md"
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  class u_cloud_services_alerts,u_cloud_services_alerts_notifier,u_cloud_services_alerts_rules,u_cloud_services_alerts_server planned
  class u_cloud_services_alerts_notifier focus
```

| Unit | Summary | Status | Diagram |
|---|---|---|---|
| [alerts](../../../README.md) | Decides when a plant needs attention and notifies its owner once | planned | [component](../../../doc/diagrams/component.md) |
| [notifier](../../README.md) | Turns an opened alert into one notification to the owner | planned | [context](context.md) |
| [rules](../../../rules/README.md) | Evaluates readings against the thresholds of a plant | planned | [context](../../../rules/doc/diagrams/context.md) |
| [server](../../../server/README.md) | Process of the alerts service - consumes readings, stores alerts and answers queries | planned | [context](../../../server/doc/diagrams/context.md) |
