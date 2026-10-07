# Context of platform

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

| Source | What it says | What it means here |
|---|---|---|
| [cloud/0001 Services learn about readings through events, not calls](../../doc/decisions/0001-services-learn-about-readings-through-events.md) | A service announces each accepted reading as an event on a durable bus. Subscribers that were down catch up from the bus. | `event-bus` stores a message before it acknowledges it and keeps messages for subscribers that are not connected. |
| [cloud/0002 Each service owns its data and nobody else reads it](../../doc/decisions/0002-each-service-owns-its-data.md) | One schema per service on one database server, enforced by database roles. | `sql-db` gives each service one schema and one role, and the role has no rights elsewhere. |
| [cloud/0004 Every event consumer is idempotent](../../doc/decisions/0004-every-event-consumer-is-idempotent.md) | Consumers produce the same result when an event arrives again. | `event-bus` may deliver a message more than once. It must never lose or reorder one. |
| [cloud: events between services](../../doc/references/events.md) | A topic is named `<service>.<stream>.v<major>`, a subscription `<service>` or `<service>.<purpose>`. Events with the same key are delivered in order. An event is at most 16 kB long. | Topic and subscription names follow this form. The bus orders by message key. Its size limit lies above 16 kB. |
| [cloud: calls between services](../../doc/references/service-calls.md) | Services reach each other by name inside a private network; nothing but one entry is reachable from outside. | Bus and database are reachable only inside the private network and rely on it instead of encrypting connections. |
| [plantwatch: time](../../../doc/references/conventions.md) | Every time is UTC. | The database server runs in UTC. |
| [plantwatch: time from upload to notification](../../../doc/references/product-parameters.md) | Under 1 minute. | The bus delivers a message to a connected subscriber within 1 second. |
| [plantwatch: history kept on the server](../../../doc/references/product-parameters.md) | 2 years per plant. | Sets the size the database volume and the backups are planned for. |
| [plantwatch: sampling interval](../../../doc/references/product-parameters.md) | 5 to 60 minutes, 15 by default. | One sensor stick produces at most 288 messages per day. The load is small; one instance of each product suffices. |
