<!-- unifold:generated - do not edit; run `unifold generate` -->
# AGENTS.md: device

unifold unit; run `unifold show` here. Read [README.md](README.md) first: it says what the unit is for and why it is built this way. Everything else is in `docs/`.

## Documents

| Kind | Files |
|---|---|
| Look up | [conventions](docs/references/conventions.md), [energy-budget](docs/references/energy-budget.md), [flash](docs/references/flash.md), [glossary](docs/references/glossary.md), [radio](docs/references/radio.md), [reading-log](docs/references/reading-log.md), [readings](docs/references/readings.md), [sensor-io](docs/references/sensor-io.md), [timer](docs/references/timer.md) |
| Understand | [context](docs/explanation/context.md), [reasoning](docs/explanation/reasoning.md), [invariants](docs/explanation/invariants.md), [runtime](docs/explanation/runtime.md), [decisions](docs/decisions/index.md) |

## Skills

| Skill | Description |
|---|---|
| [device-add-a-sensor-driver](docs/skills/device-add-a-sensor-driver/SKILL.md) | Add a driver for a sensor part to the sensor stick firmware, or replace the part behind an existing quantity. Use it when the board gets a new or a different sensor. |
| [device-check-the-energy-budget](docs/skills/device-check-the-energy-budget/SKILL.md) | Check a change to the sensor stick firmware against its energy budget, first by calculation and then by measurement on a board. Use it when a change makes the board wake more often, stay awake longer, use the radio more or power another part. |
