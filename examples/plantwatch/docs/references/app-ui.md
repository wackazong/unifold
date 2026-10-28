# app-ui

Contract of `app-ui`, the promises the app makes to its owner, independent of how a screen looks. The screens and the way between them, and the data model behind them, are up to [mobile](../../mobile/README.md). Notation: what the owner does and sees, as text.
Sources: the requirements and the product parameters of plantwatch.

## What the app does not promise

- A time by which a reading reaches the phone or the server. It depends on the phone coming near the sensor stick.
- Background fetching after a force-quit, with Bluetooth off or without the permissions.
- An alert on the phone before the server has raised it. A reading below a threshold that is not uploaded yet shows up in the history, not as an alert.
- Exact times for readings flagged as estimated.
- A way back to the owner's data for a phone that has lost its token while no other phone of the owner is at hand.

## Limits, permissions and accessibility

| Limit | Value |
|---|---|
| sensor sticks paired with one phone | 20 |
| plants of one owner | 50 |
| history on the phone | 90 days per plant |
| owners per phone | 1 |
| systems | the iOS and Android versions that [mobile](../../mobile/README.md) names |
| languages | English and German |
| screen orientation | portrait |

The first three values are [product parameters](product-parameters.md). The app asks for a permission at the moment the owner first needs it and says why:

| Permission | Without it |
|---|---|
| Bluetooth | no pairing and no fetching; everything already on the phone stays visible; the app says what is missing and leads to the system settings |
| notifications | no notifications; alerts are visible in the app |
| camera | no joining an owner by scanning a code; everything else works |

Every state that is shown by colour is also shown by text or a symbol. Every control has a label for screen readers. Text follows the text size set in the system.

## Parts

Each example starts from a phone with one plant, "Monstera", whose sensor stick is paired, lower limit for soil moisture 30 %.

### plants

Kind: query

```text
the owner opens the app -> a list of all plants
```

Pre: none; works without a network connection.
Result: a list of all plants. Plants with an open alert come first, with the reason. The age of the plant's readings and the age of server data are shown on every screen that shows either.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| offline view | flight mode; newest reading 2 days old | the plant with that reading and "2 days ago"; no error, no loading state |
| alert arrives | after the upload the server reports an open alert | the plant is first in the list with "needs water" |

### plant

Kind: query

```text
the owner opens a plant -> the latest reading and the history of the last 90 days
```

Pre: none; works without a network connection.
Result: the latest reading and the history of the last 90 days for soil moisture, light and temperature, with the age of the readings.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| low value, no alert yet | a fetched reading of 23 %, not uploaded | 23 % in the history; the plant is not marked "needs water" |

### edit-plant

Kind: command

```text
add, change or remove a plant: name, thresholds or a preset, optionally a sensor stick
```

Pre: none; possible without a network connection.
Result: the plant is added, changed or removed; a change is marked until the server has it.
Errors: a refusal by the server, shown with its reason.
Examples:

| Case | Given | Expected |
|---|---|---|
| change offline | flight mode; the owner sets the limit to 25 % | 25 % within 1 second, marked "not yet sent"; the mark goes after the next exchange |

### pair

Kind: command

```text
put a sensor stick to a plant: pairing with a sensor stick in range, then binding it to one plant
```

Pre: Bluetooth is on; no network connection is needed. A sensor stick is open for pairing only for a few minutes after its cell has been put in, as the BLE profile defines; the app tells the owner to do that.
Result: the sensor stick is paired and bound to the plant.
Errors: refused with the reason when 20 sensor sticks are paired.
Examples:

| Case | Given | Expected |
|---|---|---|
| 21st sensor stick | 20 sensor sticks are paired | pairing is refused with the reason; the 20 stay paired |

### notification-tap

Kind: command

```text
the owner taps a notification -> the app opens the plant the notification is about
```

Pre: the notification is about an alert of a plant on this phone.
Result: the app opens the plant the notification is about.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| tap on a notification | a notification about the alert of "Monstera" | the app opens the screen of "Monstera" |

### owner

Kind: command

```text
start without an account; use the app on a second phone by scanning a code shown on the first
```

Pre: none.
Result: the app asks for no name and no password and works from the first start, also without a network connection; the server creates the owner at the first exchange. On a second phone the owner scans a code the first phone shows; from then on it shows the same plants, history and alerts.
Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| first start | a new phone in flight mode | the app works and asks for no name and no password |

### fetch

Kind: event

```text
the phone comes near a paired sensor stick -> the app fetches its stored readings
```

With the app not open, the app fetches the stored readings as far as the operating system lets it run. When the owner opens the app near a paired sensor stick, a fetch starts within 5 seconds and runs to the end while the app stays open.

| Case | Given | Expected |
|---|---|---|
| fetch on opening | sensor stick in range holds 96 unconfirmed readings; no network | a fetch starts within 5 seconds; afterwards the history holds the 96 readings |

### upload

Kind: event

```text
readings are on the phone and a network connection exists -> the app uploads them without being asked
```

Without a network connection the readings stay on the phone and are visible in the history.

### registration

Kind: event

```text
the owner has allowed notifications and the server has created the owner -> the app registers the phone through push-service for its owner
```

The app registers again whenever the platform changes the phone's address. When the phone leaves its owner, the app ends that registration.

| Case | Given | Expected |
|---|---|---|
| no notifications | the owner has not allowed notifications | no registration; the alert shows in the app |

## Fake

The real implementation: no fake stands in for the app. The tests of the owner's promises are the end-to-end tests of `test-rig`, which observe the public API, and the screen tests of `mobile` against prepared data.
