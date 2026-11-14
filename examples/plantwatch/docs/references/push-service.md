# push-service

Contract of the need `push-service` of plantwatch: a service such as APNs or FCM that the phone app and the server side both use, each from its own side. Nothing in plantwatch implements it. Notation: the operations of the service as text.
Sources: the documentation of the push services of the two phone platforms, reduced to what plantwatch relies on.
Binding: http
Version: 1

## Use

A phone registers for its owner once the owner has allowed notifications. It registers again whenever the service reports a new address, and ends the registration when it leaves the owner. From its registration to its end, the phone receives the notifications of that owner. The server side sends a notification to an owner at any time. The service delivers it to every phone registered for that owner, as long as its time to live lasts. A send for an owner without a registered phone is refused for good.

## Qualities

| Aspect | Guarantee |
|---|---|
| delivery | may be delayed and is not guaranteed; the sender does not learn whether a phone showed the notification; two notifications with the same collapse identifier show as one |
| limits | a title of up to 60 characters, a body of up to 120 characters, up to five data fields, a time to live of up to 24 hours |
| fidelity | title, body and data fields reach the phone unchanged |

## Parts

### register

Kind: operation

```text
register(owner id) -> this phone receives the notifications of that owner
```

Pre: the owner has allowed notifications on the phone.
Result: the phone receives the notifications of that owner. The service tells the app when the phone's address at the service has changed, so that the app registers again.
Errors: none that plantwatch relies on.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| register, then send | | `register(owner)` | ok; a notification that the sender sends for the owner afterwards is shown on the phone with title, body and data |
| address changed | the service has changed the phone's address and told the app | `register(owner)` again | ok; the phone receives the notifications of the owner at the new address |

### end-registration

Kind: operation

```text
end-registration(owner id) -> this phone receives nothing more for that owner
```

Pre: the phone is registered for the owner.
Result: the phone receives nothing more for that owner.
Errors: none that plantwatch relies on.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| ended, then send | this phone and another phone are registered for the owner | `end-registration(owner)` | ok; a notification that the sender sends afterwards is `taken`, reaches the other phone, and nothing reaches this phone |

### deliver

Kind: event

```text
deliver(notification) -> the phone receives title, body and data fields unchanged
```

When: the server side has sent a notification for an owner for which the phone is registered, and the time to live has not passed.
Delivery: at most once per phone and notification, possibly delayed; two notifications with the same collapse identifier show as one; no order.

Examples:

| Case | Given | Action | Emitted |
|---|---|---|---|
| one notification | the phone is registered for the owner | the sender sends one notification for the owner | the phone shows it with title, body and data unchanged |
| collapsed | the phone is registered for the owner | the sender sends the same notification twice with one collapse identifier | the phone shows one |

### send

Kind: operation

```text
send(notification) -> taken | refused for good | failed for now
```

Pre: the notification has an owner id as addressee, a title of up to 60 characters, a body of up to 120 characters, up to five data fields, a collapse identifier, and a time to live of up to 24 hours.
Result: `taken`: the service delivers to every phone registered for the owner, as long as the time to live lasts.
Errors: `refused for good` when the request is malformed, too large, or nobody is registered for the owner. `failed for now` on too many requests or an error of the service; the sender may try again.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| one notification | a phone is registered for the owner | `send` of one notification for the owner | `taken`; the phone shows it with title, body and data |
| same collapse identifier twice | a phone is registered for the owner | `send` of the same notification twice with one collapse identifier | `taken` both times; the phone shows one |
| nobody registered | no phone is registered for the owner | `send` of a notification for the owner | `refused for good` |

### notification

Kind: type

```text
notification { owner id; title: <= 60 characters; body: <= 120 characters; data: <= 5 fields that reach the phone unchanged; collapse identifier; time to live: <= 24 hours }
```

## Fake

A push service in memory: it records registrations per owner, records every `send` and delivers to the registered phones of the test, collapsing by identifier. Faults it can inject: `refused for good`, `failed for now`, no answer, a changed phone address.
