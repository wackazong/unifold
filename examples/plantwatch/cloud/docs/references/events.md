# Events between services

The envelope, the topic names and the rules that every service of `cloud`
follows when it publishes or consumes events. The terms are in the
[glossary](glossary.md), the reasons in
[0001](../decisions/0001-services-learn-about-readings-through-events.md)
and [0004](../decisions/0004-every-event-consumer-is-idempotent.md).

## Envelope

Every event is one JSON object in UTF-8:

```json
{
  "id": "<derived from data>",
  "type": "thing.happened",
  "source": "<service>",
  "time": "2026-10-06T09:00:03Z",
  "key": "00a1b2c3d4e5f607",
  "data": {}
}
```

| Field | Content |
|---|---|
| `id` | Identifies what the event describes, within its `type`. The publisher derives it from the content, so an event that is published again has the same `id`. At most 100 characters. |
| `type` | What happened: a noun and a past participle, lower-case, joined by a dot |
| `source` | The unit name of the service that published the event |
| `time` | When the service published the event. Not the time of what the event describes. |
| `key` | The ordering key. Events with the same `key` reach a subscriber in the order in which they were published. The publisher also uses it as the key of the message on the event bus. |
| `data` | The content. Each event type has its own form, defined by the publishing service in the contract of its event capability. That contract also states key, order and delivery of the stream. |

Rules for `data`:

- Field names, identifiers and times follow the project conventions
  ([context](../explanation/context.md)).
- Within one topic a publisher only adds optional fields. A consumer
  ignores fields it does not know.
- An event states facts that were true when it was published. It carries no
  commands.
- An event is at most 16 kB long.

## Topics

A topic is named `<service>.<stream>.v<major>`.

| Part | Content |
|---|---|
| `<service>` | The unit name of the service that publishes to the topic. Exactly one service publishes to a topic. |
| `<stream>` | A plural noun for what the events are about |
| `<major>` | The version of the stream, starting at 1 |

- A topic carries one or several event types about the same kind of thing.
  All of them use the same kind of `key`.
- A change that would break a subscriber gets a new topic with the next
  major version. The publisher fills both topics until no subscriber is
  left on the old one.
- A service may keep topics that only it reads. They follow the same naming
  and are not part of any capability.

## Subscriptions

A subscription is named after the service that consumes: `<service>`, or
`<service>.<purpose>` if a service needs more than one on the same topic.
All instances of a service share its subscription.

A service that subscribes states what it relies on in a contract of its
need: the fields it reads, the key, the order and the delivery.

## Rules for a publisher

- It publishes only to topics that carry its own name.
- If an event is the result of a request, it answers the request with
  success only after the event bus has stored the event.
- After a failure it publishes again. The repeated event has the same `id`.

## Rules for a consumer

- Its result is the same when an event arrives again
  ([0004](../decisions/0004-every-event-consumer-is-idempotent.md)).
- It confirms an event only after its own change is durable.
- It handles the events of one `key` in the order of delivery. It may
  handle events of different keys at the same time.
- It leaves an event unconfirmed when it cannot handle it for a reason that
  passes, such as a database that is down. The event bus delivers it again.
- It confirms an event that it can never handle, such as one of an unknown
  `type` or with unusable `data`, and counts it. One bad event does not
  block the events behind it.
- It does not use `time` to order events.
