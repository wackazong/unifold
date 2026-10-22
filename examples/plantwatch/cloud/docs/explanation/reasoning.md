# Reasoning of cloud

The long form of the why in [README.md](../../README.md). Which services exist and how they are wired is shown in the
[component diagram](../diagrams/component.md).

**Accepting is separated from using.** A client is online rarely and briefly. The moment it uploads is the only chance to take its readings, so that path has as few dependencies as possible. The service that accepts readings validates them, recognises duplicates and announces each reading as an event. It calls nobody
([0001](../decisions/0001-services-learn-about-readings-through-events.md)).
It is also the only service that depends on the format of an uploaded reading. The others see readings only as events.

**History and alerts are separate consumers.** Both follow the same events and neither waits for the other. A slow history query does not delay an alert, and a fault in evaluation does not lose history. Each consumer keeps its own position on the event stream and catches up after a restart.

**Evaluation asks for thresholds instead of copying them.** Thresholds change rarely and must be current when a reading is judged. A call for the plant of a reading is simpler than a second event stream for plant changes, and a short outage of the registry only delays evaluation, because the reading waits on the event bus.

**Data is private to a service.** Two services never share a table. What one needs from another is a capability ([0002](../decisions/0002-each-service-owns-its-data.md)). This keeps a schema change inside one service.

**One door.** Authentication happens once, at the only service that is reachable from outside ([0003](../decisions/0003-one-gateway-is-the-only-public-entry.md)). The services behind it stay free of token handling and are told the owner they act for ([service calls](../references/service-calls.md)).

**Shared infrastructure has an owner.** The event bus and the database are operated in one place, [platform](../../platform/README.md). The services state what they need from it and do not configure it themselves.

## Trade-offs

| Chosen | Given up | Decision |
|---|---|---|
| Readings travel as events; an upload is answered before history and evaluation have seen the reading | A query does not see a reading at the moment the upload returns. The public API states this limit. | [0001](../decisions/0001-services-learn-about-readings-through-events.md) |
| Evaluation asks for thresholds with a synchronous call | A call stands between an event and its alert. The alternative, a copy of the thresholds kept current through events, is rejected for version 1. | [0001](../decisions/0001-services-learn-about-readings-through-events.md) |
| Every event consumer tolerates repeats | Each consumer carries its own safeguard against handling an event twice | [0004](../decisions/0004-every-event-consumer-is-idempotent.md) |
| Five deployable parts for a small product | More operation than one program. The gain is that the upload path stays up while the rest changes. | none; see the forces above |
