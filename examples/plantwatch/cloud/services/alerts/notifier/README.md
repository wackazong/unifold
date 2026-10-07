# notifier

`notifier` is an adapter that tells an owner about an opened alert. Its
caller sees a plain function. Behind it, `notifier` words the message,
hands it to a push service addressed to the owner, and reports how that
went. It stores nothing. It is built so that a caller that is unsure
whether a notification went out can simply ask again.

## Provides

### `notification`

One function, `notify(alert)`. `alert` carries alert id, owner id, plant
id, plant name, quantity, bound, judged value, threshold and the time of
the reading that opened the alert. The function makes one attempt and
returns one of three outcomes:

| Outcome | Meaning | The caller |
|---|---|---|
| `sent` | The push service has taken the notification | never calls again for this alert |
| `retry` | The attempt failed in a way that may pass | calls again later |
| `failed` | The push service refuses this notification for good | does not call again |

A caller can rely on this:

- **Once for the owner.** Every call for the same alert produces the same
  notification with the same collapse identifier. If two of them reach a
  phone, the phone shows one.
- `sent` is returned only after the push service confirmed that it took
  the notification.
- The function returns within 6 seconds.
- The same alert always gives the same words. `notifier` uses no clock
  and keeps nothing between calls.
- An alert with a quantity or bound that `notifier` has no words for
  still produces a notification, with a general text.

Limits:

- "Once" depends on the collapse identifier. A repeat that arrives after
  the owner has dismissed the first notification is shown again. A caller
  keeps repeats rare by not calling again after `sent`.
- `sent` means taken by the push service, not shown on a phone.
- The text is English.
- A phone that is unreachable for more than 24 hours does not get the
  notification.

Example:

```text
notify({alert 7d2c..., plant "Monstera in the hall",
        soil_moisture/min, value 28.4, threshold 30.0})
  -> sent

title: Monstera in the hall
body:  Needs water. Soil moisture is 28.4 %, below 30.0 %.
```

Contract: [notification](doc/references/notification.md).

## Needs

### `push`

An HTTP service that takes one notification per request. `notifier`
expects that the service

- accepts an owner id as the addressee and delivers to every phone that
  has registered with it for that owner,
- accepts a collapse identifier and shows two notifications with the same
  identifier on a phone as one,
- accepts a time to live of 24 hours, after which it stops trying to
  deliver,
- accepts a title of up to 60 characters, a body of up to 120 characters
  and five data fields of up to 40 characters each,
- answers each request clearly: taken, refused for good, or failed for
  now.

`notifier` does not expect delivery to be certain or prompt.

## Out of scope

- Deciding whether or when to notify. `notifier` notifies when it is
  called.
- Repeating a failed attempt by itself.
- Remembering which alerts were notified.
- Registering phones or knowing which phones an owner has.
- Notifying about anything but an opened alert: no reminders, no "alert
  closed".
- Languages other than English.

## More

- [AGENTS.md](AGENTS.md): why notifying is a library of its own
- [doc/context.md](doc/context.md): what the unit inherits
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- References: [notification](doc/references/notification.md)
