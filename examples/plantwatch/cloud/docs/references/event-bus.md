# event-bus

Contract of `platform.event-bus`: what a service that publishes or subscribes can rely on. The bus does not look into a value. Notation: the operations of a Kafka client, written as text.
Sources: the event conventions of `cloud`.
Binding: message

## Use

A publisher publishes messages to a declared topic. When the order of its messages with one key matters, it waits for each acknowledgement or uses the idempotent mode of its client. A subscriber subscribes once per topic and subscription name and then receives the messages as `deliver`. It confirms a message by committing the position behind it, for a partition that it holds. After a lost connection the instance subscribes again. `read-from-beginning` needs no subscription and may be called at any time.

The bus speaks the Apache Kafka protocol, as clients of version 3.0 or newer speak it, at host `event-bus`, port 9092, inside the private network. A topic is declared with the skill `platform-add-a-topic` of `platform`.

## Qualities

| Aspect | Guarantee |
|---|---|
| security | no authentication and no encryption; the private network is the boundary |
| throughput | 200 messages per second over all topics, averaged over a minute |
| latency | a burst of 1 000 messages of one publisher is acknowledged within 1 second; a connected subscriber receives a new message within 1 second |
| ordering | messages with the same key lie in the same partition and are delivered in the order in which the bus stored them; no order holds between keys |
| delivery | at least once: after a restart or a new assignment of partitions, delivery continues behind the last confirmed position, and messages behind it that were already handled are delivered again; the bus never skips a message |
| durability | an acknowledged message survives a restart of the bus; a message that was not acknowledged may or may not be stored, so a publisher that sends it again can cause a second copy |
| retention | a stream topic keeps every message for 7 days, consumed or not: a subscriber that is down for less than 7 days continues where it stopped, one that is down longer finds the older messages gone; the position of a subscription that no instance has used for 7 days is forgotten |
| limits | 10 GB of stored messages; a key of 1 to 256 bytes; a value of at most 64 kB; 12 partitions per topic |
| availability | a restart of the bus takes up to 1 minute, during which publishing and receiving fail; clients reconnect by themselves, and nothing acknowledged is lost |
| backup | none: a loss of the volume loses all messages and positions, and topics are declared again, empty |

## Parts

### publish

Kind: command

```text
publish(topic, message) -> acknowledged
```

Pre: the topic is declared; the message has a key of 1 to 256 bytes and a value of at most 64 kB.
Result: the bus acknowledges the message after it has written the message to its volume. The key selects the partition. Messages that one publisher sends with the same key are stored in the order in which it sent them, provided the publisher waits for each acknowledgement or uses the idempotent mode of its client.
Errors: the publish fails for a topic that is not declared, and no topic is created.
Examples:

| Case | Input | Expected |
|---|---|---|
| undeclared topic | `publish("greenhouse.pots.v1", m)`, the topic not declared | the publish fails; no topic is created |
| order within a key | publish A, then B, both with key `k`, each after the acknowledgement of the one before | acknowledged; every subscription receives A before B |
| remove a key | publish an empty value with key `k` to a keep-latest topic | acknowledged; the key is removed |

### subscribe

Kind: command

```text
subscribe(topic, subscription-name) -> stream of messages
```

Pre: the topic is declared.
Result: the instance joins the consumer group with that name. A subscription that is used for the first time starts with the oldest message that the topic still keeps. All connected instances that use the same subscription name share the partitions; one partition is read by one instance at a time, and when an instance joins or leaves, the bus assigns the partitions anew. Within a partition, messages are delivered in stored order, and a subscriber that does not confirm stays where it is.
Errors: subscribing to a topic that is not declared fails.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| two instances | | two instances call `subscribe(topic, "greenhouse")` | each message of key `k` goes to one of them; both never read the same partition at once |
| new subscription | the topic holds messages of the last 3 days | `subscribe` with a name that is used for the first time | it receives all of them, oldest first |
| long absence | the only subscriber of a name was away for 8 days | `subscribe` with that name | messages older than 7 days are gone; delivery starts with the oldest one kept |

### deliver

Kind: event

```text
deliver(subscription-name, partition, message)
```

When: a message is stored in a partition that the instance holds and every earlier message of the partition has been delivered to it.
Delivery: at least once, in stored order per partition; a message that was not confirmed is delivered again after a restart or a new assignment of partitions.

### commit

Kind: command

```text
commit(subscription-name, partition, position)
```

Pre: the instance holds the partition.
Result: the bus remembers for the subscription and partition the position up to which messages are confirmed; a subscriber confirms a message by committing the position behind it.
Errors: none beyond a lost connection, after which the instance subscribes again.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| repeat after a restart | a subscriber handled a message and did not commit the position behind it | the subscriber reconnects and subscribes again | it receives the same message again |

### read-from-beginning

Kind: query

```text
read-from-beginning(topic) -> every message the topic keeps, oldest first
```

Pre: the topic is declared.
Result: every message the topic still keeps, without a subscription, for example to load a keep-latest topic. The bus keeps no position for such a reader.
Errors: reading a topic that is not declared fails.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| keep-latest | `v1`, then `v2` with key `k` were published to a keep-latest topic a day ago | `read-from-beginning(topic)` | `v2` for `k`, and possibly `v1` before it |

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
