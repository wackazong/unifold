# pairing

Contract of `ble-client.pairing`: the operations, data and guarantees of the capability through which a sensor stick is found and bound to this phone. The description is independent of a programming language. The fields of a paired sensor stick are those cited in [context.md](../explanation/context.md). The capability does not know plants; binding the sensor stick to a plant is up to the caller. It does not identify a sensor stick to the owner other than by signal strength: the nearest one is first in the list. Notation: wit.
Sources: the BLE profile of plantwatch, the product parameters, the platform limits of `mobile`.

## Parts

### search

Kind: query

```wit
search: func(observer: found-list-observer) -> result<_, pairing-failure>;
```

Pre: the program is on the screen.
Result: the observer receives the list of sensor sticks in range that can be paired, again whenever it changes; the client scans until the search is cancelled or 60 seconds have passed. The list contains a sensor stick only while it advertises that it is open for pairing, and never one that is already paired with this phone. It is ordered by signal strength, strongest first; a sensor stick that has not been heard for 5 seconds leaves the list.
Errors: `bluetooth off`, `permission missing`, reported instead of a list.
Examples:

| Case | Given | Expected |
|---|---|---|
| search | two unpaired sensor sticks in range, one open for pairing at -48 dBm, one not open | a list with the first only |
| out of range | a listed sensor stick is not heard for 5 seconds | it leaves the list |

### cancel-search

Kind: command

```wit
cancel-search: func();
```

Pre: none.
Result: the scan ends.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| cancel | a search runs | no further list is delivered |

### pair

Kind: command

```wit
pair: func(sensor-id: string) -> result<_, pairing-failure>;
```

Pre: the sensor stick is in the list of a search; fewer than 20 sensor sticks are paired. During the call the operating system may show dialogs of its own, whose number and wording differ between iOS and Android and are not part of this contract.
Result: `paired`, all or nothing: the sensor stick appears in `list-paired`, the operating system wakes the program when the sensor stick is near, and a first fetch starts within 1 second. The pairing survives restarts of the program and of the phone, and updates of the program. After a failure, nothing of this holds.
Errors: `not found` when the sensor stick did not answer within 10 seconds; `refused` when the sensor stick refuses to pair, normally because it is no longer open for pairing; `declined` when the owner declined a dialog of the operating system; `limit reached` when 20 sensor sticks are paired already; `unsupported version` when the sensor stick states a major protocol version other than 1; `bluetooth off`; `permission missing`.
Examples:

| Case | Given | Expected |
|---|---|---|
| pair | `pair` for a listed sensor stick; the owner accepts the system dialogs | `paired`; `list-paired` contains it; a first fetch starts |
| too late | `pair` after the sensor stick has stopped being open for pairing | `refused`; `list-paired` is unchanged |
| limit | 20 sensor sticks are paired; `pair` for another | `limit reached`; the 20 stay paired |

### list-paired

Kind: query

```wit
list-paired: func(observer: paired-list-observer);
```

Pre: none.
Result: the paired sensor sticks, again whenever the list changes. At most 20 sensor sticks are paired at a time.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| after pairing | one sensor stick was paired | a list with that sensor stick |

### unpair

Kind: command

```wit
unpair: func(sensor-id: string);
```

Pre: none; the sensor stick need not be in range.
Result: the binding is removed on this phone and the client no longer fetches from the sensor stick. Unpairing is local and always succeeds. Readings that are still on the sensor stick stay there; the sensor stick is not told.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| unpair out of range | `unpair` while the sensor stick is not in range | it leaves `list-paired`; no later fetch from it |

### found-sensor-stick

Kind: type

```wit
record found-sensor-stick { sensor-id: string, signal-strength-dbm: s8, protocol-version: string }
```

| Field | Content |
|---|---|
| sensor-id | the sensor stick |
| signal-strength-dbm | in dBm, averaged over the last second; larger means nearer |
| protocol-version | the version of the radio protocol the sensor stick states |

### pairing-failure

Kind: type

```wit
variant pairing-failure {
  not-found, refused, declined, limit-reached, unsupported-version, bluetooth-off, permission-missing
}
```

## Fake

Scripted: a test sets which sensor sticks are in range, which are open for pairing and how strong they are; `pair` answers as scripted and the lists follow. Faults it can inject: every failure of `pairing-failure`.
