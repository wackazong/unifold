# Context of platform

What this unit takes over from the units above, and what each item means here.

## From cloud

### [cloud/0001 Services learn about readings through events, not calls](../../../docs/decisions/0001-services-learn-about-readings-through-events.md)

Each accepted reading is announced as an event on a durable bus. Subscribers that were down catch up from the bus. So `event-bus` stores a message before it acknowledges it and keeps messages for subscribers that are not connected.

### [cloud/0002 Each service owns its data and nobody else reads it](../../../docs/decisions/0002-each-service-owns-its-data.md)

Each service has one schema on one database server, enforced by database roles. `sql-db` gives each service one schema and one role, and the role has no rights elsewhere.

### [cloud/0004 Every event consumer is idempotent](../../../docs/decisions/0004-every-event-consumer-is-idempotent.md)

Delivery is at least once. A consumer produces the same result when an event arrives again. So `event-bus` may deliver a message more than once. It never loses one and never reorders the messages of a key.

### [cloud: events between services](../../../docs/references/events.md)

A topic is named `<service>.<stream>.v<major>`, a subscription `<service>`. Events of one key arrive in order. An event is at most 16 kB.

Topic and subscription names follow this form. The bus orders by message key. Its limit for a message, 64 kB, lies above 16 kB.

### [cloud: calls between services](../../../docs/references/service-calls.md)

A service is reachable only from the private network and therefore trusts its callers. Bus and database are reachable only inside the private network and rely on it instead of encrypting connections.

## From plantwatch

### [plantwatch: conventions, time](../../../../docs/references/conventions.md#time)

Outside the sensor stick, every time is UTC. The database server runs in UTC.

### [plantwatch: product parameters](../../../../docs/references/product-parameters.md)

Upload to notification takes under 1 minute. The server keeps 2 years of history per plant. A sensor stick takes a reading every 5 to 60 minutes.

The bus delivers a message to a connected subscriber within 1 second. The 2 years set the size of the database volume and its backups. A sensor stick causes at most 288 messages per day, so one instance of each product suffices.
