# Context of notifier

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

| Source | What it says | What it means here |
|---|---|---|
| [alerts/0001 Evaluation and notification are libraries beside one process](../../doc/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md) | Notifying is a library without state and without database access, called by the process of the service. | `notifier` keeps nothing between calls and reports its outcome to the caller. |
| [alerts/0002 The alert row is the outbox of its notification](../../doc/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md) | An alert is stored as owing a notification. Delivery repeats until it succeeds, for at most 24 hours. Whatever notifies must make a second notification for the same alert harmless for the owner. | `notify` is called more than once for the same alert. Making the repeat harmless is the duty of this unit, see [0001](decisions/0001-once-means-repeatable-with-a-collapse-identifier.md). The time to live of a notification is the same 24 hours. |
| [cloud/0004 Every event consumer is idempotent](../../../../doc/decisions/0004-every-event-consumer-is-idempotent.md) | Delivery inside the server side is at least once. An effect outside the databases, such as a notification, cannot take part in a transaction and needs its own way to make a repeat harmless. | The reason for [0001](decisions/0001-once-means-repeatable-with-a-collapse-identifier.md). |
| [cloud: public API, alerts](../../../../doc/references/public-api/alerts.md) | Each alert leads to one notification to the owner, sent when the alert opens. It carries the alert `id` and the `plant_id`. `sent` means the push service has taken it; `failed` that it refused for good. An alert has a `quantity` (`soil_moisture`, `light`, `temperature`) and a `bound` (`min`, `max`); light is judged by the highest value of a day. | The data fields of a notification, the meaning of the outcomes, and the cases the texts must cover. |
| [plantwatch: push-service](../../../../../README.md) | A service that delivers a short notification to a phone that has registered with it, such as APNs or FCM. Delivery may be delayed and is not guaranteed. | What stands behind the need `push`. `notifier` promises handing over, not delivery. |
| [plantwatch: measured quantities](../../../../../doc/references/conventions.md) | Soil moisture in percent with resolution 0.1, light in lux with resolution 1, temperature in degrees Celsius with resolution 0.1. | The units and the number of decimals in the texts. |
| [plantwatch: notification, owner](../../../../../doc/references/glossary.md) | A notification is a message to the owner about an alert that has opened, one per alert. The owner is the user a plant belongs to. | What `notify` produces and whom it addresses. |
