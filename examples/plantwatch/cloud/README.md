# cloud

`cloud` is the server side. It accepts uploaded readings, keeps the registry of plants with their thresholds and their history, decides when a plant needs attention, and notifies the owner once per alert. It runs as a set of containers and is reached through one HTTP API.

## Why

`cloud` exists so that readings become history and alerts while no client is online. It changes when the public API changes or when readings get a new use on the server side.

Its three jobs load and fail differently. Accepting an upload must work whenever a client finally has a connection, also while history or evaluation is down. Evaluation must react within a minute. Queries are read-heavy and may be slow without harm. Each job is therefore a service of its own that can be deployed, scaled and restarted alone.

What joins them is chosen so that a failure does not spread. Readings travel as events, and the service that accepts them knows no receiver ([0001](docs/decisions/0001-services-learn-about-readings-through-events.md)). Every service keeps its own data ([0002](docs/decisions/0002-each-service-owns-its-data.md)). One entry point authenticates ([0003](docs/decisions/0003-one-gateway-is-the-only-public-entry.md)). The event bus and the database belong to no service and are a unit of their own. The price is eventual consistency and repeated deliveries ([0004](docs/decisions/0004-every-event-consumer-is-idempotent.md)).

## Read next

1. [docs/explanation/invariants.md](docs/explanation/invariants.md), [runtime.md](docs/explanation/runtime.md), [deployment.md](docs/explanation/deployment.md): invariants, the path of an upload, where things run
2. [public API](../docs/references/public-api/index.md): the contract with clients
3. [docs/references/events.md](docs/references/events.md): event envelope and topic names
4. [docs/references/service-calls.md](docs/references/service-calls.md): rules for HTTP calls between services
5. [docs/references/glossary.md](docs/references/glossary.md): the terms of the server side
6. [docs/explanation/context.md](docs/explanation/context.md): what it inherits from the project
7. [Context diagram](docs/diagrams/context.md), [component diagram](docs/diagrams/component.md), [architecture diagram](docs/diagrams/architecture.md), [decisions](docs/decisions/index.md)
