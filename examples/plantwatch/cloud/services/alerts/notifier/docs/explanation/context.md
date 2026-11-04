# Context of notifier

What this unit takes over from the units above, and what each item means here.

## From alerts

### [alerts/0001 Evaluation and notification are libraries beside one process](../../../docs/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)

Notifying is a library without state and without database access, called by the process of the service. So `notifier` keeps nothing between calls and reports its outcome to the caller.

### [alerts/0002 The alert row is the outbox of its notification](../../../docs/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)

An alert is stored as owing a notification. Delivery repeats for at most 24 hours. Whatever notifies makes a repeat harmless for the owner.

`notify` is called more than once for the same alert. Making the repeat harmless is the duty of this unit, see [0001](../decisions/0001-once-means-repeatable-with-a-collapse-identifier.md). The time to live of a notification is the same 24 hours.

## From cloud

### [cloud: public API, alerts](../../../../../../docs/references/public-api/alert.md)

This unit implements the following part of the contract. Each alert leads to one notification to the owner, sent when the alert opens. It carries the alert `id` and the `plant_id`. `sent` means that the push service has taken it, `failed` that it refused for good. An alert has a `quantity` and a `bound`; light is judged by the highest value of a day.

The reference gives the data fields of a notification, the meaning of the outcomes, and the cases that the texts must cover.

### [cloud: glossary](../../../../../docs/references/glossary.md)

A collapse identifier is a value sent with a notification. Two notifications with the same value show on a phone as one. The collapse identifier is the means by which a repeated call stays harmless.

## From plantwatch

### [plantwatch: push service, for a sender](../../../../../../docs/references/push-service.md)

A sender hands the service a notification for an owner, with an identifier under which a repeat replaces the earlier one. Delivery is not guaranteed.

The push service is what stands behind the need `push`. `notifier` promises handing over, not delivery.

### [plantwatch: conventions, measured quantities](../../../../../../docs/references/conventions.md#measured-quantities)

Soil moisture is given in percent in steps of 0.1, light in lux in steps of 1, and temperature in °C in steps of 0.1. These steps set the units and the number of decimals in the texts.

### [plantwatch: glossary](../../../../../../docs/references/glossary.md)

A notification is a message to the owner about an alert that has opened, one per alert. The owner is the user a plant belongs to. These terms say what `notify` produces and whom it addresses.
