# Data model of the app

The things the app handles, with their fields, their origin and who may
change them. Every part of the app uses these names. How the things are laid
out in the store on the phone is not defined here.

Terms, units, ranges and identifier forms are inherited; see
[context.md](../context.md).

## Overview

| Thing | Origin | Changed on the phone by | Kept on the phone |
|---|---|---|---|
| Reading | A sensor stick | Nobody | 90 days, and in any case until the server has confirmed it |
| Plant | The owner, on this phone or elsewhere | The owner | While it exists |
| Alert | The server | Nobody | While open, and 90 days after it has closed |
| Paired sensor stick | Pairing on this phone | Pairing and unpairing | While paired |
| Session | The first start, or joining an owner | Joining and leaving | Until the phone leaves the owner |

## Reading

| Field | Content |
|---|---|
| Sensor id | The sensor stick that took the reading |
| Sequence number | The number the sensor stick gave it |
| Tick count | Boot counter and seconds since that boot, as the sensor stick sent them |
| Soil moisture | Percent, or absent |
| Light | Lux, or absent |
| Temperature | Degrees Celsius, or absent |
| Time | UTC, whole seconds |
| Time estimated | Yes if the time could not be computed and was estimated |

Sensor id and sequence number together identify a reading. Two readings with
the same pair are the same reading; the one stored first stays.

The tick count is carried along because the `reading-format` contains it.
Only the part that fetches computes with it
([0003](../decisions/0003-a-reading-gets-its-time-before-it-is-stored.md)).

The field names in stored documents and uploads are those of the
`reading-format`. This table names what the app relies on.

## Plant

| Field | Content |
|---|---|
| Plant id | UUID, chosen on the phone when the owner creates the plant |
| Name | Text the owner gives, 1 to 60 characters |
| Thresholds | See below |
| Sensor id | The sensor stick in the pot, or none |
| Change state | `in step`, `waiting` or `refused`; see below |

A plant has at most one sensor stick, and a sensor stick belongs to at most
one plant.

### Thresholds

A plant has, per measured quantity, a lower limit, an upper limit, both or
none. A limit lies inside the range of its quantity. The app stores and
shows thresholds; it does not compare readings with them.

| Quantity | Reason shown when below the lower limit | Reason shown when above the upper limit |
|---|---|---|
| Soil moisture | Needs water | Too wet |
| Light | Needs more light | Too much light |
| Temperature | Needs a warmer place | Too warm |

Version 1 of the app lets the owner set the three lower limits. An upper
limit that was set elsewhere stays with the plant untouched, and an alert
about it is shown like any other.

### Change state

| State | Meaning |
|---|---|
| `in step` | The phone holds the plant as the server last sent it |
| `waiting` | The owner has changed the plant on this phone and the server has not confirmed it yet |
| `refused` | The server has refused the last change; the phone holds the server's version again and the reason |

## Alert

| Field | Content |
|---|---|
| Alert id | UUID, given by the server |
| Plant id | The plant that needs attention |
| Reason | The measured quantity, and whether the lower or the upper limit is crossed |
| Limit and value | The limit and the measured value at the moment the alert opened |
| Opened | UTC time |
| Closed | UTC time, absent while the alert is open |

The phone learns of an alert only from the server.

## Paired sensor stick

| Field | Content |
|---|---|
| Sensor id | The sensor stick |
| Paired | UTC time of the pairing |
| Last fetch | UTC time of the last fetch that ended with all readings confirmed, or none |
| Protocol version | The version of the radio protocol the sensor stick states |

## Session

| Field | Content |
|---|---|
| Owner id | UUID of the owner this phone acts for; absent until the server has created the owner |
| Token | What the server gave out for this owner; kept in the phone's protected storage |
| Token valid until | UTC time; the app renews the token well before |

A phone acts for one owner at a time. After the first start the app lets
the server create an owner at the first exchange. A further phone joins the
same owner with a token that the first phone obtains for it and shows as a
code. A phone that loses its token without another phone to join from can
no longer reach the owner's data.

Leaving an owner removes plants, readings and alerts from the phone and
keeps the paired sensor sticks. The app leaves only after the server has
confirmed every reading on the phone; without a network connection it
waits. While the phone acts for no owner the app fetches nothing, so
readings stay on their sensor sticks.

## Age of data

Two ages describe how current the data on the phone is. Screens show them.

| Age | Defined as |
|---|---|
| Age of a plant's readings | Time since the newest reading of the plant's sensor stick |
| Age of server data | Time since the last exchange with the server that succeeded |
