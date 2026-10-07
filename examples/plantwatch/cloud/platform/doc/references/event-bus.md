# Event bus

The contract of the port `event-bus`: what a service that publishes or
subscribes can rely on. The product behind it is chosen in
[0001](../decisions/0001-postgresql-and-a-kafka-compatible-broker.md).

## Access

| Item | Value |
|---|---|
| Wire protocol | Apache Kafka protocol, as spoken by clients of version 3.0 or newer |
| Address | Host `event-bus`, port 9092, inside the private network |
| Authentication | None. The private network is the boundary. |
| Encryption | None |

## Topics

A topic exists when it is declared in this unit, with the skill
[platform-add-a-topic](../skills/platform-add-a-topic/SKILL.md). Publishing
or subscribing to a topic that is not declared fails.

| Kind | Keeps | Meant for |
|---|---|---|
| stream | every message for 7 days, consumed or not | events |
| keep-latest | at least the latest message per key, without a time limit | a small state per key that a service writes and reads back |

- Every topic has 12 partitions. The number never changes.
- The key of a message selects the partition. Messages with the same key
  lie in the same partition, in the order in which the bus stored them.
- In a keep-latest topic, a message with an empty value removes its key.

## Messages

| Item | Limit |
|---|---|
| Key | 1 to 256 bytes, required |
| Value | at most 64 kB |
| Headers | not used |

The bus does not look into a value.

## Publishing

- The bus acknowledges a message after it has written the message to its
  volume. An acknowledged message survives a restart.
- A message that was not acknowledged may or may not be stored. A
  publisher that sends it again can cause a second copy.
- Messages that one publisher sends with the same key are stored in the
  order in which it sent them, provided the publisher waits for each
  acknowledgement or uses the idempotent mode of its client.

## Subscribing

A subscription is a consumer group with a name.

- A subscription that is used for the first time starts with the oldest
  message that the topic still keeps.
- The bus remembers for each subscription and partition the position up to
  which messages are confirmed. A subscriber confirms a message by
  committing the position behind it.
- All connected instances that use the same subscription name share the
  partitions. One partition is read by one instance at a time. When an
  instance joins or leaves, the bus assigns the partitions anew.
- After a restart or a new assignment, delivery continues behind the last
  confirmed position. Messages behind it that were already handled are
  delivered again.
- Within a partition, messages are delivered in stored order. The bus
  never skips a message; a subscriber that does not confirm stays where it
  is.
- The bus forgets the position of a subscription that no instance has
  used for 7 days.
- A connected subscriber receives a new message within 1 second.
- A client may also read a topic from its beginning without a
  subscription, for example to load a keep-latest topic. The bus keeps no
  position for such a reader.

## What can go wrong

| Event | Effect for a service |
|---|---|
| Restart of the bus, up to 1 minute | Publishing and receiving fail. Clients reconnect by themselves. Nothing acknowledged is lost. |
| A subscriber is down for less than 7 days | It continues where it stopped. |
| A subscriber is down for more than 7 days | Messages older than 7 days are gone for it. |
| Loss of the volume | All messages and positions are lost. The bus has no backup. Topics are declared again, empty. |

## Sizing

The bus is planned for 200 messages per second over all topics, averaged
over a minute, and for 10 GB of stored messages. It acknowledges a burst of
1 000 messages of one publisher within 1 second.

## Examples

| Case | Action | Result |
|---|---|---|
| Undeclared topic | Publish to `greenhouse.pots.v1`, which is not declared | The publish fails. No topic is created. |
| Order within a key | Publish A, then B, both with key `k`, each after the acknowledgement of the one before | Every subscription receives A before B |
| Repeat after a restart | A subscriber handles a message, does not confirm it and reconnects | It receives the same message again |
| Two instances | Two instances use the subscription `greenhouse` | Each message of key `k` goes to one of them; both never read the same partition at once |
| New subscription | A subscription is used for the first time on a topic with messages of the last 3 days | It receives all of them, oldest first |
| Long absence | A subscriber returns after 8 days | Messages older than 7 days are gone; delivery starts with the oldest one kept |
| Keep-latest | Publish `v1`, then `v2` with key `k` to a keep-latest topic; read from the beginning a day later | The reader gets `v2` for `k`, and possibly `v1` before it |
