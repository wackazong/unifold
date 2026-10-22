# Contract of `pairing`

The operations, data and guarantees of the capability through which a sensor stick is found and bound to this phone. The description is independent of a programming language. The fields of a paired sensor stick are those cited in [context.md](../explanation/context.md).

## Operations

| Operation | Input | Output | Effect |
|---|---|---|---|
| Search | Nothing | The list of sensor sticks in range that can be paired, again whenever it changes | The client scans until the search is cancelled or 60 seconds have passed |
| Cancel search | Nothing | Nothing | The scan ends |
| Pair | Sensor id | `paired` or a failure | The sensor stick is bound to this phone and fetched from now on |
| List paired | Nothing | The paired sensor sticks, again whenever the list changes | None |
| Unpair | Sensor id | Nothing | The binding is removed on this phone; the client no longer fetches from the sensor stick |

## A found sensor stick

| Field | Content |
|---|---|
| Sensor id | The sensor stick |
| Signal strength | In dBm, averaged over the last second; larger means nearer |
| Protocol version | The version of the radio protocol the sensor stick states |

The list is ordered by signal strength, strongest first. A sensor stick that has not been heard for 5 seconds leaves the list.

## Guarantees

- **A search finds only what can be paired.** The list contains a sensor stick only while it advertises that it is open for pairing, and never one that is already paired with this phone.
- **Pairing is all or nothing.** After `paired`, the sensor stick appears in "list paired", the operating system wakes the program when the sensor stick is near, and a first fetch starts within 1 second. After a failure, nothing of this holds.
- **Pairing lasts.** A pairing survives restarts of the program and of the phone, and updates of the program.
- **Unpairing is local and always succeeds.** It works without the sensor stick in range. Readings that are still on the sensor stick stay there. The sensor stick is not told.
- **The limit holds.** At most 20 sensor sticks are paired at a time.

## Failures of "pair"

| Failure | Meaning |
|---|---|
| `not found` | The sensor stick did not answer within 10 seconds |
| `refused` | The sensor stick refuses to pair, normally because it is no longer open for pairing |
| `declined` | The owner declined a dialog of the operating system |
| `limit reached` | 20 sensor sticks are paired already |
| `unsupported version` | The sensor stick states a major protocol version other than 1 |
| `bluetooth off` | Bluetooth is switched off on the phone |
| `permission missing` | The program lacks a permission for Bluetooth |

"Search" reports `bluetooth off` and `permission missing` in the same way instead of delivering a list.

## Examples

| Case | Given | Expected |
|---|---|---|
| Search | Two unpaired sensor sticks in range, one open for pairing at -48 dBm, one not open | A list with the first only |
| Out of range | A listed sensor stick is not heard for 5 seconds | It leaves the list |
| Pair | "Pair" for a listed sensor stick; the owner accepts the system dialogs | `paired`; "list paired" contains it; a first fetch starts |
| Too late | "Pair" after the sensor stick has stopped being open for pairing | `refused`; "list paired" is unchanged |
| Limit | 20 sensor sticks are paired; "pair" for another | `limit reached`; the 20 stay paired |
| Unpair out of range | "Unpair" while the sensor stick is not in range | It leaves "list paired"; no later fetch from it |

## Limits

- A search runs only while the program is on the screen.
- During "pair" the operating system may show dialogs of its own. Their number and wording differ between iOS and Android and are not part of this contract.
- The capability does not know plants. Binding the sensor stick to a plant is up to the caller.
- The capability does not identify a sensor stick to the owner other than by signal strength. The nearest one is first in the list.
