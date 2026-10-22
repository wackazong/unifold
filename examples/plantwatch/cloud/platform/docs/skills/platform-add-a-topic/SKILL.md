---
name: platform-add-a-topic
description: Declare a new topic on the event bus that the platform unit operates. Use it when a service asks for a topic that does not exist yet, for events or for its own keep-latest state.
---

# Add a topic to the event bus

Topics are not created on first use. The result of this procedure is a declared topic that exists in every environment after the next deployment of `platform`.

## Steps

1. **Get the request.** You need the topic name, the kind (stream or keep-latest) and what the message key is. The requester is the service that will publish to the topic.
2. **Check the name.** It has the form `<service>.<stream>.v<major>` ([context](../../explanation/context.md)). The first part is the name of the requesting service. A topic with the same name except for the major version may exist; that is a new version, not a conflict.
3. **Check the kind.** A stream topic is the normal case. A keep-latest topic is right only if the service reads the topic back as its own state and one message per key is enough ([event bus](../../../../docs/references/event-bus.md), topics).
4. **Declare it.** Add the topic to the topic declarations of this unit with its name and kind. Do not set a number of partitions or a retention of its own; the contract fixes both.
5. **Do not add access rules.** The bus has none. Who may publish follows from the name.
6. **Deploy** `platform` to the test environment and check (below), then to production.

## Checks

- The topic is listed by the bus with 12 partitions and the retention of its kind.
- A test message with a key can be published and is received by a test subscription. Remove the test subscription afterwards.
- Publishing to a misspelt topic name still fails. If it succeeds, topic creation on first use has been switched on by mistake.

## Removing a topic

Remove a declaration only when the publishing service has stopped publishing and no subscription has read the topic for 7 days. A removed stream topic cannot be brought back with its messages.

## Reference

- [event bus](../../../../docs/references/event-bus.md): kinds of topics, limits, guarantees
- [context](../../explanation/context.md): the naming rule for topics and subscriptions
