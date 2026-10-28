# Context of notifier

What this unit inherits from the units above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

## From alerts

### [alerts/0001 Evaluation and notification are libraries beside one process](../../../docs/decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)
<!-- unifold:cites sha=83b74117 -->

Says: notifying is a library without state and without database access, called by the process of the service.

Here: `notifier` keeps nothing between calls and reports its outcome to the caller.

### [alerts/0002 The alert row is the outbox of its notification](../../../docs/decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)
<!-- unifold:cites sha=f5351c6f -->

Says: an alert is stored as owing a notification. Delivery repeats for at most 24 hours. Whatever notifies makes a repeat harmless for the owner.

Here: `notify` is called more than once for the same alert. Making the repeat harmless is the duty of this unit, see [0001](../decisions/0001-once-means-repeatable-with-a-collapse-identifier.md). The time to live of a notification is the same 24 hours.

## From cloud

### [cloud: public API, alerts](../../../../../../docs/references/public-api/alert.md)
<!-- unifold:cites sha=d21ddf40 -->

Says, as the part of the contract that this unit implements: each alert leads to one notification to the owner, sent when the alert opens. It carries the alert `id` and the `plant_id`. `sent` means that the push service has taken it, `failed` that it refused for good. An alert has a `quantity` and a `bound`; light is judged by the highest value of a day.

Here: the data fields of a notification, the meaning of the outcomes, and the cases that the texts must cover.

### [cloud: glossary](../../../../../docs/references/glossary.md)
<!-- unifold:cites sha=2e1d860c -->

Says: a collapse identifier is a value sent with a notification. Two notifications with the same value show on a phone as one.

Here: the means by which a repeated call stays harmless.

## From plantwatch

### [plantwatch: push service, for a sender](../../../../../../docs/references/push-service.md)
<!-- unifold:cites sha=0e97e4ac -->

Says: a sender hands the service a notification for an owner, with an identifier under which a repeat replaces the earlier one. Delivery is not guaranteed.

Here: what stands behind the need `push`. `notifier` promises handing over, not delivery.

### [plantwatch: conventions, measured quantities](../../../../../../docs/references/conventions.md#measured-quantities)
<!-- unifold:cites sha=c9226f2c -->

Says: soil moisture in percent in steps of 0.1, light in lux in steps of 1, temperature in °C in steps of 0.1.

Here: the units and the number of decimals in the texts.

### [plantwatch: glossary](../../../../../../docs/references/glossary.md)
<!-- unifold:cites sha=082ae761 -->

Says: a notification is a message to the owner about an alert that has opened, one per alert. The owner is the user a plant belongs to.

Here: what `notify` produces and whom it addresses.
