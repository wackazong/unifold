---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The central confirms with one cumulative sequence number

## Context and Problem Statement

A sensor stick keeps a reading until a central has it. Connections break at any moment, also in the middle of a transfer. The sensor stick must learn which readings it may delete, without ever deleting one that the central does not hold. How does the central tell it?

## Decision Drivers

- No reading is lost when the connection breaks at any point.
- A sensor stick keeps little state per reading and per central.
- Repeating a step after a failure is always safe.

## Considered Options

- Delete on send: the sensor stick deletes a reading when the radio link has acknowledged the packet
- Confirm implicitly: the next fetch names the first sequence number wanted, and everything below it counts as confirmed
- Confirm each reading by its sequence number
- Confirm explicitly with one number: "I hold everything up to n"

## Decision Outcome

Chosen option: "confirm explicitly with one number", because it separates reading from deleting, needs one stored number on the sensor stick, and can be repeated without harm.

`fetch` never changes the sensor stick. `confirm` is the only request that does, and writing the same or a lower number again has no effect.

### Consequences

- Good: a central that crashes between receiving and storing loses nothing; it fetches again.
- Good: the sensor stick stores one number, not one flag per reading.
- Good: a confirm is valid in a later connection, so a lost confirm costs no second transfer.
- Bad: a central cannot confirm reading 12 while it lacks reading 11. It has to fetch in order.
- Bad: a central can confirm readings it never fetched and so delete them unseen. The profile allows this; the encrypted connection limits who can do it.
- Bad: with two bonded centrals, a reading confirmed by one never reaches the other over the radio link.

## Pros and Cons of the Options

### Delete on send

- Good: no confirm step.
- Bad: an acknowledged packet says that the central's radio has the bytes, not that the central has stored the reading.

### Confirm implicitly with the next fetch

- Good: one request instead of two.
- Bad: reading and deleting are coupled. A central that only wants to look cannot.
- Bad: the last fetch of a session is never confirmed until the next session.

### Confirm each reading

- Good: readings can be confirmed out of order.
- Bad: one stored flag and one request per reading.

## More Information

The procedure is defined in
[procedures.md](../references/ble-profile/procedures.md).
