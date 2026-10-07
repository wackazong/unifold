---
name: cloud-add-a-service
description: Add a new service to the server side, from the folder to the wiring and the deployment view. Use it when a new job does not fit into one of the existing services.
---
# Add a service to cloud

The result is a new child unit of `cloud` with `status: planned`, wired to
the other children, and visible in the generated diagrams. The procedure
keeps the rules that make services independent of each other.

## Steps

1. **Check that it is a service.** A new service is justified when the job
   has its own load, its own failure behaviour or its own data. Otherwise
   extend an existing service inside that service.
2. **Create the unit.** Add the folder below the plain folder `services/`
   of this unit, with a `README.md` that carries the manifest and an
   `AGENTS.md`. The folder name is the unit name and becomes the `source`
   of its events and the prefix of its topics
   ([events](../../references/events.md)).
3. **Declare ports without looking at the other services.** State what the
   service provides. State as needs what it requires: an event stream it
   consumes, an API it calls, the database, the event bus. Name each need
   after what is needed.
4. **Wire it.** Add one line per need to `wiring` in
   [README.md](../../../README.md). If no child provides what is needed,
   either add a port to the child that should provide it, using that
   child's own skills, or add a need to `cloud` and pass it up.
5. **Make it reachable, if clients shall use it.** Describe the new
   operations in the [public API](../../references/public-api/index.md)
   first. Then let [gateway](../../../services/gateway/README.md) state a
   need for the new port and wire that need. Follow the skills of that
   unit.
6. **Give it infrastructure.** If the service stores data, it needs a
   schema of its own
   ([0002](../../decisions/0002-each-service-owns-its-data.md)). If it
   publishes events, its topics must exist. Both are set up in
   [platform](../../../platform/README.md) with the skills of that unit.
7. **Write its context.** In the new unit's `doc/context.md`, cite the
   decisions of `cloud` and the references
   [events](../../references/events.md) and
   [service calls](../../references/service-calls.md) as far as they apply.
8. **Update the deployment view.** Add a row to the table "Where things
   run" in [architecture.md](../../architecture.md). If the service changes
   the path of an upload, record a decision first.
9. **Regenerate and check.** Run the generator and the checker of
   [youmedoc](https://youmedoc.example) and fix what they report for
   `cloud` and the new unit.

## Checks

- The checker reports no `W2` (unwired need) and no `W3` (unused port) for
  `cloud`.
- The component diagram of `cloud` shows the new service with every arrow
  you expect and no arrow you do not.
- No file of the new unit names another service.
- The path of an upload still contains no call other than the one to the
  service that accepts readings
  ([architecture.md](../../architecture.md), invariants).

## Reference

- [events](../../references/events.md): envelope, topic and subscription
  names
- [service calls](../../references/service-calls.md): headers, paths, time
  limits
- [0001](../../decisions/0001-services-learn-about-readings-through-events.md),
  [0002](../../decisions/0002-each-service-owns-its-data.md),
  [0003](../../decisions/0003-one-gateway-is-the-only-public-entry.md),
  [0004](../../decisions/0004-every-event-consumer-is-idempotent.md)
