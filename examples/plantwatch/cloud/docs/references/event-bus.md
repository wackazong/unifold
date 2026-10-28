# event-bus

Contract of `platform.event-bus`: what a service that publishes or subscribes can rely on. The product behind it is chosen in decision 0001 of `platform`. The bus does not look into a value. Notation: the operations of a Kafka client, written as text.
Sources: decision 0001 of `platform`, the event conventions of `cloud`.

## Access

| Item | Value |
|---|---|
| wire protocol | Apache Kafka protocol, as spoken by clients of version 3.0 or newer |
| address | host `event-bus`, port 9092, inside the private network |
| authentication | none; the private network is the boundary |
| encryption | none |

## What can go wrong

| Event | Effect for a service |
|---|---|
| restart of the bus, up to 1 minute | publishing and receiving fail; clients reconnect by themselves; nothing acknowledged is lost |
| a subscriber is down for less than 7 days | it continues where it stopped |
| a subscriber is down for more than 7 days | messages older than 7 days are gone for it |
| loss of the volume | all messages and positions are lost; the bus has no backup; topics are declared again, empty |

The bus is planned for 200 messages per second over all topics, averaged over a minute, and for 10 GB of stored messages.

## Parts

### publish

Kind: command

```text
publish(topic, message) -> acknowledged
```

Pre: the topic is declared with the skill `platform-add-a-topic` of `platform`; the message has a key of 1 to 256 bytes and a value of at most 64 kB.
Result: the bus acknowledges the message after it has written the message to its volume; an acknowledged message survives a restart. The key selects the partition. Messages that one publisher sends with the same key are stored in the order in which it sent them, provided the publisher waits for each acknowledgement or uses the idempotent mode of its client. The bus acknowledges a burst of 1 000 messages of one publisher within 1 second.
Errors: the publish fails for a topic that is not declared, and no topic is created. A message that was not acknowledged may or may not be stored; a publisher that sends it again can cause a second copy.
Examples:

| Case | Action | Result |
|---|---|---|
| undeclared topic | publish to `greenhouse.pots.v1`, which is not declared | the publish fails; no topic is created |
| order within a key | publish A, then B, both with key `k`, each after the acknowledgement of the one before | every subscription receives A before B |
| remove a key | publish an empty value with key `k` to a keep-latest topic | the key is removed |

### subscribe

Kind: command

```text
subscribe(topic, subscription-name) -> stream of messages
```

Pre: the topic is declared.
Result: the instance joins the consumer group with that name. A subscription that is used for the first time starts with the oldest message that the topic still keeps. All connected instances that use the same subscription name share the partitions; one partition is read by one instance at a time, and when an instance joins or leaves, the bus assigns the partitions anew. After a restart or a new assignment, delivery continues behind the last confirmed position; messages behind it that were already handled are delivered again. Within a partition, messages are delivered in stored order; the bus never skips a message, and a subscriber that does not confirm stays where it is. A connected subscriber receives a new message within 1 second. The bus forgets the position of a subscription that no instance has used for 7 days.
Errors: subscribing to a topic that is not declared fails.
Examples:

| Case | Action | Result |
|---|---|---|
| two instances | two instances use the subscription `greenhouse` | each message of key `k` goes to one of them; both never read the same partition at once |
| new subscription | a subscription is used for the first time on a topic with messages of the last 3 days | it receives all of them, oldest first |
| long absence | a subscriber returns after 8 days | messages older than 7 days are gone; delivery starts with the oldest one kept |

### deliver

Kind: event

```text
deliver(subscription-name, partition, message)
```

### commit

Kind: command

```text
commit(subscription-name, partition, position)
```

Pre: the instance holds the partition.
Result: the bus remembers for the subscription and partition the position up to which messages are confirmed; a subscriber confirms a message by committing the position behind it.
Errors: none beyond a lost connection, after which the instance subscribes again.
Examples:

| Case | Action | Result |
|---|---|---|
| repeat after a restart | a subscriber handles a message, does not confirm it and reconnects | it receives the same message again |

### read-from-beginning

Kind: query

```text
read-from-beginning(topic) -> every message the topic keeps, oldest first
```

Pre: the topic is declared.
Result: every message the topic still keeps, without a subscription, for example to load a keep-latest topic. The bus keeps no position for such a reader.
Errors: reading a topic that is not declared fails.
Examples:

| Case | Action | Result |
|---|---|---|
| keep-latest | publish `v1`, then `v2` with key `k` to a keep-latest topic; read from the beginning a day later | the reader gets `v2` for `k`, and possibly `v1` before it |

### message

Kind: type

```text
message { key: 1 to 256 bytes, required; value: at most 64 kB; headers: not used }
```

### topic

Kind: type

```text
topic { name, kind: stream | keep-latest, partitions: 12 }
```

| Kind | Keeps | Meant for |
|---|---|---|
| stream | every message for 7 days, consumed or not | events |
| keep-latest | at least the latest message per key, without a time limit | a small state per key that a service writes and reads back |

Every topic has 12 partitions; the number never changes. Messages with the same key lie in the same partition, in the order in which the bus stored them. In a keep-latest topic, a message with an empty value removes its key.

## Fake

A bus in memory: topics as lists per partition, subscriptions with positions, the same order and repeat rules. Faults it can inject: a restart, during which publishing and receiving fail; a lost acknowledgement, so that a repeated publish stores a second copy; a new assignment of partitions, which delivers unconfirmed messages again.
