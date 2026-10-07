# Context of platform

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From cloud

### [cloud/0001 Services learn about readings through events, not calls](../../doc/decisions/0001-services-learn-about-readings-through-events.md)

Says: each accepted reading is announced as an event on a durable bus.
Subscribers that were down catch up from the bus.

Here: `event-bus` stores a message before it acknowledges it and keeps
messages for subscribers that are not connected.

### [cloud/0002 Each service owns its data and nobody else reads it](../../doc/decisions/0002-each-service-owns-its-data.md)

Says: one schema per service on one database server, enforced by database
roles.

Here: `sql-db` gives each service one schema and one role, and the role has
no rights elsewhere.

### [cloud/0004 Every event consumer is idempotent](../../doc/decisions/0004-every-event-consumer-is-idempotent.md)

Says: delivery is at least once. A consumer produces the same result when an
event arrives again.

Here: `event-bus` may deliver a message more than once. It never loses one
and never reorders the messages of a key.

### [cloud: events between services](../../doc/references/events.md)

Says: a topic is named `<service>.<stream>.v<major>`, a subscription
`<service>`. Events of one key arrive in order. An event is at most 16 kB.

Here: topic and subscription names follow this form. The bus orders by
message key. Its limit for a message, 64 kB, lies above 16 kB.

### [cloud: calls between services](../../doc/references/service-calls.md)

Says: a service is reachable only from the private network and therefore
trusts its callers.

Here: bus and database are reachable only inside the private network and
rely on it instead of encrypting connections.

## From plantwatch

### [plantwatch: conventions, time](../../../doc/references/conventions.md)

Says: outside the sensor stick, every time is UTC.

Here: the database server runs in UTC.

### [plantwatch: product parameters](../../../doc/references/product-parameters.md)

Says: upload to notification takes under 1 minute. The server keeps 2 years
of history per plant. A sensor stick takes a reading every 5 to 60 minutes.

Here: the bus delivers a message to a connected subscriber within 1 second.
The 2 years set the planned size of the database volume and its backups. A
sensor stick causes at most 288 messages per day, so one instance of each
product suffices.
