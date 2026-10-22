<!-- unifold:generated - do not edit; run `unifold generate` -->
# AGENTS.md: test-rig

unifold unit; run `unifold show` here. Read [README.md](README.md) first: it says what the unit is for and why it is built this way. Everything else is in `docs/`.

## Documents

| Kind | Files |
|---|---|
| Look up | [configurations](docs/references/configurations.md), [conventions](docs/references/conventions.md), [glossary](docs/references/glossary.md), [test-catalogue](docs/references/test-catalogue.md), [test-report](docs/references/test-report.md) |
| Understand | [context](docs/explanation/context.md), [invariants](docs/explanation/invariants.md), [decisions](docs/decisions/index.md) |

## Skills

| Skill | Description |
|---|---|
| [test-rig-add-an-end-to-end-test](docs/skills/test-rig-add-an-end-to-end-test/SKILL.md) | Add an end-to-end test to the test rig, or change one because its promise changed. Use it when a promise that spans the sensor link and the public API shall be guarded, not for behaviour that one part can test alone. |
| [test-rig-run-against-real-hardware](docs/skills/test-rig-run-against-real-hardware/SKILL.md) | Run the end-to-end tests of the test rig against a real sensor stick instead of a simulated device, and read the result correctly. Use it before a release, after a real sensor stick has changed, or when a simulated run and reality seem to disagree. |
