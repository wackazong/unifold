<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: end-to-end-alert-test

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The rig drives the simulated sensor stick through a dry spell and sees one alert**
Source: test catalogue of test-rig, ALERT-01
Expect: no alert 60 seconds after the first upload; within 60 seconds after the second, one open alert for the plant with soil moisture below the limit and its notification reported as handed on; after the third, the same alert and no other; the report has ALERT-01 passed and the exit status is 0

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one.

```mermaid
---
config:
  sequence:
    height: 124
---
sequenceDiagram
  participant ptest_dreport as test-report<br/>«file»<br/>Result of the automated end-to-<br/>end tests, for developers and CI
  participant ptest_drig as test-rig<br/>«test»<br/>Runs end-to-end tests from the<br/>sensor link to the alert,<br/>against real or simulated<br/>hardware
  participant pemulator as emulator<br/>«tool»<br/>Desktop program that behaves<br/>like a sensor stick and is<br/>driven by a scenario instead of<br/>hardware
  participant pcloud__services__gateway as cloud/services/gateway<br/>«service»<br/>Single entry point of the server<br/>side that authenticates callers<br/>and routes requests
  ptest_dreport->>ptest_drig: 1 · run
  activate ptest_drig
  ptest_drig->>pemulator: 2 · put-scenario
  ptest_drig->>pcloud__services__gateway: 3 · put-plant
  ptest_drig->>pemulator: 4 · put-time
  ptest_drig->>pemulator: 5 · open-session
  ptest_drig->>pemulator: 6 · fetch
  ptest_drig->>pemulator: 7 · confirm
  ptest_drig->>pcloud__services__gateway: 8 · upload-batch
  ptest_drig->>pcloud__services__gateway: 9 · list-alerts
  activate pcloud__services__gateway
  pcloud__services__gateway-->>ptest_drig: ↩ 9
  deactivate pcloud__services__gateway
  deactivate ptest_drig
  Note over ptest_dreport,pcloud__services__gateway: wrap: Expect: no alert 60 seconds after the first upload#59; within 60 seconds after the second, one open alert for the plant with soil moisture below the limit and its notification reported as handed on#59; after the third, the same alert and no other#59; the report has ALERT-01 passed and the exit status is 0
```

| # | Caller | Target | Part | Kind | Contract |
|---|---|---|---|---|---|
| 1 | `test-report` | `test-rig` | `run` | command | [test-report](../references/test-report.md) |
| 2 | `test-rig` | `emulator` | `put-scenario` | command | [index](../references/scenario-control/index.md) |
| 3 | `test-rig` | `cloud/services/gateway` | `put-plant` | command | [index](../references/public-api/index.md) |
| 4 | `test-rig` | `emulator` | `put-time` | command | [index](../references/scenario-control/index.md) |
| 5 | `test-rig` | `emulator` | `open-session` | command | [index](../references/ble-profile/index.md) |
| 6 | `test-rig` | `emulator` | `fetch` | command | [index](../references/ble-profile/index.md) |
| 7 | `test-rig` | `emulator` | `confirm` | command | [index](../references/ble-profile/index.md) |
| 8 | `test-rig` | `cloud/services/gateway` | `upload-batch` | command | [index](../references/public-api/index.md) |
| 9 | `test-rig` | `cloud/services/gateway` | `list-alerts` | query | [index](../references/public-api/index.md) |
