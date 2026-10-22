# Push service

The contract of the need `push-service`: a service such as APNs or FCM that the phone app and the server side both use, each from its own side. Nothing in plantwatch implements it.

## For a phone

| Operation | Behaviour |
|---|---|
| Register | The phone registers for the notifications of one owner. The service tells the app when the phone's address at the service has changed, so that the app registers again. |
| End registration | The phone receives nothing more for that owner |
| Deliver | A notification sent to the owner reaches the phone with its title, body and data fields unchanged. Two notifications with the same collapse identifier show as one. |

## For a sender

A request carries an owner id as addressee, a title of up to 60 characters, a body of up to 120 characters, up to five data fields that reach the phone unchanged, a collapse identifier, and a time to live of up to 24 hours.

| Answer | Meaning |
|---|---|
| Taken | The service delivers to every phone registered for the owner, as long as the time to live lasts |
| Refused for good | The request is malformed, too large, or nobody is registered for the owner |
| Failed for now | Too many requests, or an error of the service; the sender may try again |

Delivery may be delayed and is not guaranteed. The sender does not learn whether a phone showed the notification.

## Examples

| Case | Expected |
|---|---|
| A phone registers, the sender sends one notification for its owner | The phone shows it with title, body and data |
| The same notification is sent twice with one collapse identifier | The phone shows one |
| The sender sends for an owner with no registered phone | Refused for good |
| The phone ends its registration, the sender sends | Taken; nothing reaches the phone |
