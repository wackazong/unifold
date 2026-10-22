<!-- unifold:generated - do not edit; run `unifold generate` -->
# AGENTS.md: platform

unifold unit; run `unifold show` here. Read [README.md](README.md) first: it
says what the unit is for and why it is built this way. Everything else is in
`docs/`.

## Documents

| Kind | Files |
|---|---|
| Look up | [conventions](docs/references/conventions.md), [event-bus](docs/references/event-bus.md), [sql-db](docs/references/sql-db.md) |
| Understand | [context](docs/explanation/context.md), [invariants](docs/explanation/invariants.md), [decisions](docs/decisions/index.md) |

## Skills

| Skill | Description |
|---|---|
| [platform-add-a-schema](docs/skills/platform-add-a-schema/SKILL.md) | Give a service its own schema and role in the shared database. Use it when a service that stores data is added. |
| [platform-add-a-topic](docs/skills/platform-add-a-topic/SKILL.md) | Declare a new topic on the event bus that the platform unit operates. Use it when a service asks for a topic that does not exist yet, for events or for its own keep-latest state. |
