<!-- unifold:generated - do not edit; run `unifold generate` -->
# AGENTS.md: cloud

unifold unit; run `unifold show` here. Read [README.md](README.md) first: it
says what the unit is for and why it is built this way. Everything else is in
`docs/`.

## Documents

| Kind | Files |
|---|---|
| Look up | [conventions](docs/references/conventions.md), [events](docs/references/events.md), [glossary](docs/references/glossary.md), [public-api](docs/references/public-api/index.md), [service-calls](docs/references/service-calls.md) |
| Understand | [context](docs/explanation/context.md), [requirements](docs/explanation/requirements.md), [reasoning](docs/explanation/reasoning.md), [invariants](docs/explanation/invariants.md), [runtime](docs/explanation/runtime.md), [deployment](docs/explanation/deployment.md), [risks](docs/explanation/risks.md), [decisions](docs/decisions/index.md) |

## Skills

| Skill | Description |
|---|---|
| [cloud-add-a-service](docs/skills/cloud-add-a-service/SKILL.md) | Add a new service to the server side, from the folder to the wiring and the deployment view. Use it when a new job does not fit into one of the existing services. |
| [cloud-add-an-event-type](docs/skills/cloud-add-an-event-type/SKILL.md) | Introduce a new event type or a new event stream between the services of the server side. Use it when a service shall announce something that other services react to. |
