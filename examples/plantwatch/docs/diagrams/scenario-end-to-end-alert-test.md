<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: end-to-end-alert-test

**plantwatch** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

**The rig drives the simulated sensor stick through a dry spell and sees one alert**
Source: test catalogue of test-rig, ALERT-01
Expect: no alert 60 seconds after the first upload; within 60 seconds after the second, one open alert for the plant with soil moisture below the limit and its notification reported as handed on; after the third, the same alert and no other; the report has ALERT-01 passed and the exit status is 0

A unit is named by its path from `plantwatch`; a capability or need of `plantwatch` is named bare. Every hop is a call along one connection of the map.

```mermaid
sequenceDiagram
  participant ptest_dreport as test-report
  participant ptest_drig as test-rig
  participant pemulator as emulator
  participant pcloud__services__gateway as cloud/services/gateway
  ptest_dreport->>ptest_drig: 1 · run
  ptest_drig->>pemulator: 2 · put-scenario
  ptest_drig->>pcloud__services__gateway: 3 · put-plant
  ptest_drig->>pemulator: 4 · put-time
  ptest_drig->>pemulator: 5 · open-session
  ptest_drig->>pemulator: 6 · fetch
  ptest_drig->>pemulator: 7 · confirm
  ptest_drig->>pcloud__services__gateway: 8 · upload-batch
  ptest_drig->>pcloud__services__gateway: 9 · list-alerts
  Note over ptest_dreport,pcloud__services__gateway: Expect: no alert 60 seconds after the first upload; within 60 seconds after the second, one open alert for the plant with soil moisture below the limit and its notification reported as handed on; after the third, the same alert and no other; the report has ALERT-01 passed and the exit status is 0
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `test-report` | `test-rig` | `run` | [test-report](../references/test-report.md) |
| 2 | `test-rig` | `emulator` | `put-scenario` | [index](../references/scenario-control/index.md) |
| 3 | `test-rig` | `cloud/services/gateway` | `put-plant` | [index](../references/public-api/index.md) |
| 4 | `test-rig` | `emulator` | `put-time` | [index](../references/scenario-control/index.md) |
| 5 | `test-rig` | `emulator` | `open-session` | [index](../references/ble-profile/index.md) |
| 6 | `test-rig` | `emulator` | `fetch` | [index](../references/ble-profile/index.md) |
| 7 | `test-rig` | `emulator` | `confirm` | [index](../references/ble-profile/index.md) |
| 8 | `test-rig` | `cloud/services/gateway` | `upload-batch` | [index](../references/public-api/index.md) |
| 9 | `test-rig` | `cloud/services/gateway` | `list-alerts` | [index](../references/public-api/index.md) |
