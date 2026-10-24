<!-- unifold:generated - do not edit; run `unifold generate` -->
# AGENTS.md: plantwatch

unifold unit; run `unifold show` here. Read [README.md](README.md) first: it says what the unit is for and why it is built this way. Everything else is in `docs/`.

## Documents

| Kind | Files |
|---|---|
| Look up | 14 files in docs/references/ |
| Understand | [requirements](docs/explanation/requirements.md), [reasoning](docs/explanation/reasoning.md), [invariants](docs/explanation/invariants.md), [runtime](docs/explanation/runtime.md), [deployment](docs/explanation/deployment.md), [risks](docs/explanation/risks.md), [decisions](docs/decisions/index.md) |

## Skills

| Skill | Description |
|---|---|
| [add-a-measured-quantity](docs/skills/add-a-measured-quantity/SKILL.md) | Add a new measured quantity, such as air humidity, to plantwatch from the sensor to the alert. Use it when the sensor stick shall measure something it does not measure yet. |
| [change-a-shared-definition](docs/skills/change-a-shared-definition/SKILL.md) | Change the BLE profile or the reading schema so that parts built for the previous version keep working. Use it when a field, a quantity, a characteristic, an op code or a rule of one of the two contracts shall be added or changed. |

<!-- unifold:begin - generated block; run `unifold generate` to refresh -->
## unifold

This repository has a [unifold](https://unifold.md) map. A folder with a `unifold.yaml` is a unit: the file says what the unit provides and needs, and the unit above connects needs to providers. Read the map before you change an interface; keep it true after.

- `unifold show PATH`: a unit, its capabilities and needs, and who is on the other side
- `unifold capability PATH NAME`: both ends of one connection, with contracts
- `unifold check`: is the map consistent (`--fix` rewrites generated files)

| Unit | Path | Summary |
|---|---|---|
| cloud | `cloud` | Server side that turns uploaded readings into plant history and alerts (planned) |
| platform | `cloud/platform` | Shared infrastructure of the services - message bus and database (planned) |
| alerts | `cloud/services/alerts` | Decides when a plant needs attention and notifies its owner once (planned) |
| notifier | `cloud/services/alerts/notifier` | Turns an opened alert into one notification to the owner (planned) |
| plant-lookup | `cloud/services/alerts/plant-lookup` | Looks up the plant a sensor stick is attached to, with owner and thresholds, in the registry of plants (planned) |
| rules | `cloud/services/alerts/rules` | Evaluates readings against the thresholds of a plant (planned) |
| server | `cloud/services/alerts/server` | Process that consumes readings, stores the alerts they lead to and answers queries about them (planned) |
| gateway | `cloud/services/gateway` | Single entry point of the server side that authenticates callers and routes requests (planned) |
| ingest | `cloud/services/ingest` | Accepts uploaded readings and announces each accepted one as an event (planned) |
| plants | `cloud/services/plants` | Registry of plants with their sensors, thresholds and reading history (planned) |
| device | `device` | Firmware of the sensor stick that measures soil and surroundings and serves the readings over BLE (planned) |
| hal | `device/hal` | Hardware abstraction of the sensor stick board (planned) |
| link | `device/link` | Implements the BLE profile on top of the radio (planned) |
| sampling | `device/sampling` | Takes a calibrated reading at every sampling interval (planned) |
| store | `device/store` | Keeps readings on the sensor stick until they have been delivered (planned) |
| emulator | `emulator` | Desktop program that behaves like a sensor stick and is driven by a scenario instead of hardware (planned) |
| mobile | `mobile` | Phone app that collects readings from sensor sticks, shows the plants and relays data to the server (planned) |
| ble-client | `mobile/ble-client` | Finds sensor sticks and fetches their readings over BLE (planned) |
| sync | `mobile/sync` | Keeps plants, history and alerts on the phone and in step with the server (planned) |
| ui | `mobile/ui` | Screens of the phone app (planned) |
| test-rig | `test-rig` | Runs end-to-end tests from the sensor link to the alert, against real or simulated hardware (planned) |
<!-- unifold:end -->
