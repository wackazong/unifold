# push-service

Contract of the need `push-service` of plantwatch: a service such as APNs or FCM that the phone app and the server side both use, each from its own side. Nothing in plantwatch implements it. Delivery may be delayed and is not guaranteed; the sender does not learn whether a phone showed the notification. Notation: the operations of the service as text.
Sources: the documentation of the push services of the two phone platforms, reduced to what plantwatch relies on.

## Parts

### register

Kind: command

```text
register(owner id) -> this phone receives the notifications of that owner
```

Pre: the owner has allowed notifications on the phone.
Result: the phone receives the notifications of that owner. The service tells the app when the phone's address at the service has changed, so that the app registers again.
Errors: none that plantwatch relies on.
Examples:

| Case | Input | Expected |
|---|---|---|
| register, then send | a phone registers; the sender sends one notification for its owner | the phone shows it with title, body and data |
| address changed | the service changes the phone's address | the app is told and registers again |

### end-registration

Kind: command

```text
end-registration(owner id) -> this phone receives nothing more for that owner
```

Pre: the phone is registered for the owner.
Result: the phone receives nothing more for that owner.
Errors: none that plantwatch relies on.
Examples:

| Case | Input | Expected |
|---|---|---|
| ended, then send | the phone ends its registration; the sender sends | taken; nothing reaches the phone |

### deliver

Kind: event

```text
deliver(notification) -> the phone receives title, body and data fields unchanged
```

A notification sent to the owner reaches the phone with its title, body and data fields unchanged. Two notifications with the same collapse identifier show as one.

### send

Kind: command

```text
send(notification) -> taken | refused for good | failed for now
```

Pre: the notification has an owner id as addressee, a title of up to 60 characters, a body of up to 120 characters, up to five data fields, a collapse identifier, and a time to live of up to 24 hours.
Result: `taken`: the service delivers to every phone registered for the owner, as long as the time to live lasts.
Errors: `refused for good` when the request is malformed, too large, or nobody is registered for the owner. `failed for now` on too many requests or an error of the service; the sender may try again.
Examples:

| Case | Input | Expected |
|---|---|---|
| one notification | a phone is registered; one notification for its owner | `taken`; the phone shows it with title, body and data |
| same collapse identifier twice | the same notification is sent twice with one collapse identifier | the phone shows one |
| nobody registered | a notification for an owner with no registered phone | `refused for good` |

### notification

Kind: type

```text
notification { owner id; title: <= 60 characters; body: <= 120 characters; data: <= 5 fields that reach the phone unchanged; collapse identifier; time to live: <= 24 hours }
```

## Fake

A push service in memory: it records registrations per owner, records every `send` and delivers to the registered phones of the test, collapsing by identifier. Faults it can inject: `refused for good`, `failed for now`, no answer, a changed phone address.
