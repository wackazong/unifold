---
status: proposed
date: 2026-10-06
---
# PostgreSQL as database and a Kafka-compatible broker as event bus

## Context and Problem Statement

`platform` provides a relational database with one schema per service and
an event bus with durable subscriptions. Which products stand behind the
two ports? The load of version 1 is small: a sensor stick produces at most
288 messages per day. The host is a plain container host with volumes.

## Decision Drivers

- Messages with the same key reach a subscription in order, also when a
  service runs several instances.
- A subscriber that was down, or that is new, can read messages published
  earlier.
- A service can keep a small state per key on the bus and read it back.
- Schemas are isolated by the database itself.
- As little as possible is written and tested in this unit.
- As few products as possible are operated.

## Considered Options

- PostgreSQL for both: the bus is a set of tables that subscribers poll
- PostgreSQL and RabbitMQ
- PostgreSQL and NATS JetStream
- PostgreSQL and Apache Kafka, one broker without ZooKeeper

## Decision Outcome

Chosen option: "PostgreSQL and Apache Kafka", because partitions and
consumer groups give order per key with several consumer instances,
retention gives replay, and log compaction gives the keep-latest topics.
All three come ready-made and are widely known.

The ports keep their neutral names `event-bus` and `sql-db`. The contracts
name the wire protocols, because a client must speak them. Another broker
that speaks the Kafka protocol can replace Apache Kafka without a change to
a contract.

### Consequences

- Good: no bus logic is written in this unit.
- Good: client libraries for both protocols exist in every common
  language.
- Good: the contract of `event-bus` maps one to one to features of the
  product.
- Bad: Kafka is the heaviest of the considered brokers. It needs about
  1 GB of memory for a load that a table could carry.
- Bad: two products to operate, upgrade and monitor instead of one.
- Bad: one broker gives no redundancy. Redundancy needs three brokers and
  is left out of version 1.

## Pros and Cons of the Options

### PostgreSQL for both

- Good: one product, one backup.
- Good: an event can be published in the same transaction as a data
  change.
- Bad: ordering per key, competing instances, positions and retention must
  be built and tested here.
- Bad: every service would depend on the database, also the one that only
  accepts uploads. The services would be coupled through shared tables,
  against the rule that each owns its data
  ([context](../explanation/context.md)).

### PostgreSQL and RabbitMQ

- Good: light, simple to operate.
- Bad: a classic queue deletes a message once it is consumed. Replay and
  order per key with several consumer instances need its streams with
  partitions and single active consumers, a part of the product that few
  people know.

### PostgreSQL and NATS JetStream

- Good: lightest broker; durable consumers and replay are built in.
- Bad: order per key with several consumer instances needs subjects that
  are partitioned by hand and one consumer per partition. Nothing assigns
  the partitions to the instances of a service.
