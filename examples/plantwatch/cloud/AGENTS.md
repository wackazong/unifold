# AGENTS.md: cloud

This folder is a [youmedoc](https://youmedoc.example) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `youmedoc`. From
there, `python3 doc/skills/check-docs/scripts/youmedoc.py show cloud`
prints this unit with its neighbours.

## Why

`cloud` exists so that readings become history and alerts while no client is
online. It changes when the public API changes or when readings get a new
use on the server side.

Its three jobs load and fail differently. Accepting an upload must work
whenever a client finally has a connection, also while history or evaluation
is down. Evaluation must react within a minute. Queries are read-heavy and
may be slow without harm. Each job is therefore a service of its own that
can be deployed, scaled and restarted alone.

What joins them is chosen so that a failure does not spread. Readings travel
as events, and the service that accepts them knows no receiver
([0001](doc/decisions/0001-services-learn-about-readings-through-events.md)).
Every service keeps its own data
([0002](doc/decisions/0002-each-service-owns-its-data.md)). One entry point
authenticates
([0003](doc/decisions/0003-one-gateway-is-the-only-public-entry.md)). The
event bus and the database belong to no service and are a unit of their own.
The price is eventual consistency and repeated deliveries
([0004](doc/decisions/0004-every-event-consumer-is-idempotent.md)).

## Read next

1. [README.md](README.md): what the server side provides and needs
2. [doc/context.md](doc/context.md): what it inherits from the project
3. [doc/architecture.md](doc/architecture.md): invariants, the path of an
   upload, where things run
4. [doc/diagrams/component.md](doc/diagrams/component.md): the services and
   their wiring
5. [doc/decisions/index.md](doc/decisions/index.md): decisions
6. [doc/references/public-api/index.md](doc/references/public-api/index.md):
   the contract with clients
7. [doc/references/events.md](doc/references/events.md): event envelope and
   topic names
8. [doc/references/service-calls.md](doc/references/service-calls.md): rules
   for HTTP calls between services
9. [doc/references/glossary.md](doc/references/glossary.md): the terms of
   the server side

## Skills

| Skill | Use it when |
|---|---|
| [cloud-add-a-service](doc/skills/cloud-add-a-service/SKILL.md) | A new job does not fit into an existing service |
| [cloud-add-an-event-type](doc/skills/cloud-add-an-event-type/SKILL.md) | A service shall announce something that other services react to |

## Rules for work here

- The [public API](doc/references/public-api/index.md) is the contract with
  clients. Change it there first. The services that serve a part of it
  follow.
- An interface between two services is decided in this unit, never in one of
  the two. That holds for every event type and every call.
- After a change to a child's port, read both ends of every wiring line that
  touches it: the need of one child and the port of the other must still
  say the same.
- Do not add a synchronous call to the path of an upload. An upload succeeds
  when the reading is accepted, whatever else is down.
- A new measured quantity changes the public API first, then every service
  that validates, stores or evaluates readings. Each of them has a skill for
  its part.
- A change that breaks clients gets a new path prefix in the public API. A
  change that breaks subscribers gets a new topic.
