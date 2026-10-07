---
name: cloud-add-an-event-type
description: Introduce a new event type or a new event stream between the services of the server side. Use it when a service shall announce something that other services react to.
---
# Add an event type

The result is an event type that one service publishes and others may
consume, declared in the manifests and wired in `cloud`. An event is an
interface between services, so it is agreed in `cloud` before any service
changes.

## Steps

1. **Check that an event is the right means.** An event announces a fact
   that has happened. If a service needs an answer, or the current state of
   something, it needs a call instead
   ([0001](../../decisions/0001-services-learn-about-readings-through-events.md)).
2. **Name it.** Choose the `type`, the `key` that orders the events, and
   what the `id` is derived from, by the rules in
   [events](../../references/events.md). Decide whether the type joins an
   existing topic of the publisher or starts a new one.
3. **Record the choice** as a decision of `cloud` with status `proposed` if
   there were alternatives, for example between an event and a call.
4. **Change the publisher.** In the publishing service, add the type to the
   contract of the event port it belongs to, or add a new provided port of
   kind `events` with a contract. Use that unit's own skills.
5. **Have the topic created**, if it is new, in
   [platform](../../../platform/README.md) with the skills of that unit.
6. **Change each subscriber.** In every service that shall react, add a
   need of kind `events` that says in the subscriber's own words what it
   expects, with a contract that states the fields it reads, the key, the
   order and the delivery it relies on. Do not name the publisher there.
7. **Wire it.** In `wiring` of [README.md](../../../README.md), connect
   each new need to the publisher's port. A subscriber also needs the
   event bus; add that line if it is missing. Compare the contract of each
   need with the contract of the publisher's port.
8. **Regenerate and check** with the generator and the checker of
   [youmedoc](https://youmedoc.example).

## Checks

- The event has an `id` that stays the same when it is published again.
- The contract of the event port states key, order and delivery, and has
  an example event.
- Every subscriber states how it stays idempotent
  ([0004](../../decisions/0004-every-event-consumer-is-idempotent.md)).
- Exactly one service publishes to the topic.
- The component diagram of `cloud` shows an arrow from each subscriber to
  the publisher, labelled with the need.
- A subscriber that is not yet updated is not disturbed: an added type on
  an existing topic is ignored by consumers that do not know it.

## Reference

- [events](../../references/events.md): envelope, topics, subscriptions,
  rules for publishers and consumers
