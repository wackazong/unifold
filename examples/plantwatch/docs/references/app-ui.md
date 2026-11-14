# app-ui

Contract of `app-ui`, the promises the app makes to its owner, independent of how a screen looks. The screens and the way between them, and the data model behind them, are up to [mobile](../../mobile/README.md). Notation: what the owner does and sees, as text.
Sources: the requirements and the product parameters of plantwatch.
Binding: ui
Version: 1

## Use

The owner starts the app without an account, adds plants, and puts a sensor stick to each plant. From then on the owner sees the plants, their history and their alerts. The app has no state that limits what the owner may do: every part may be used at any time, also without a network connection, except showing the code for a second phone and leaving the owner, which need one (part `owner`). Pairing and fetching need Bluetooth.

What the app does without being asked:

- It fetches the stored readings when the phone comes near a paired sensor stick, as far as the operating system lets it run, and when the owner opens the app near one. A fetch that is cut off is taken up again at the next opportunity, and a reading that reaches the phone twice is kept once.
- It uploads the readings on the phone whenever a network connection exists. Without one they stay on the phone and are visible in the history. The server reports a reading it already has as a duplicate, so nothing is stored twice.
- It registers the phone through `push-service` once the owner has allowed notifications and the server has created the owner, and again whenever the platform changes the phone's address. When the phone leaves its owner, the app ends that registration.

The app does not promise:

- A time by which a reading reaches the phone or the server. It depends on the phone coming near the sensor stick.
- Background fetching after a force-quit, with Bluetooth off or without the permissions.
- An alert on the phone before the server has raised it. A reading below a threshold that is not uploaded yet shows up in the history, not as an alert.
- Exact times for readings flagged as estimated.
- A way back to the owner's data for a phone that has lost its token while no other phone of the owner is at hand.

The app does not depend on the delivery of notifications: every alert that a notification announces is on the screens after the next exchange with the server, also when notifications are not allowed. When the newest reading of a plant is older than 24 hours, the screen says "No readings since" with the time. A low value in the history is not marked as a problem by itself. Temperatures are shown in degrees Celsius only.

## Qualities

| Aspect | Guarantee |
|---|---|
| limits | 20 sensor sticks paired with one phone, 50 plants of one owner and 90 days of history per plant on the phone, which are [product parameters](product-parameters.md); 1 owner per phone; in the background the app fetches each sensor stick at most 4 times a day |
| systems | the iOS and Android versions that [mobile](../../mobile/README.md) names |
| languages | English and German |
| orientation | portrait |
| latency | a change to a plant shows within 1 second; when the owner opens the app near a paired sensor stick, a fetch starts within 5 seconds |
| permissions | the app asks for a permission at the moment the owner first needs it and says why; without Bluetooth there is no pairing and no fetching, everything already on the phone stays visible, and the app says what is missing and leads to the system settings; without notifications there are none, and alerts are visible in the app; without the camera there is no joining an owner by scanning a code, and everything else works |
| accessibility | every state that is shown by colour is also shown by text or a symbol; every control has a label for screen readers; text follows the text size set in the system |

## Parts

Each example starts from a phone with one plant, "Monstera", whose sensor stick is paired, lower limit for soil moisture 30 %.

### plants

Kind: operation

```text
the owner opens the app, or pulls the list down -> a list of all plants
```

Pre: none; works without a network connection.
Result: a list of all plants. Plants with an open alert come first, with the reason. The age of the plant's readings and the age of server data are shown on every screen that shows either. Pulling the list down asks for a fetch from the sensor sticks in range and an exchange with the server now.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| offline view | flight mode; newest reading 2 days old | the owner opens the app | the plant with that reading and "2 days ago"; no error, no loading state |
| alert arrives | after the upload the server reports an open alert | the owner opens the app | the plant is first in the list with "needs water" |
| no notifications | the owner has not allowed notifications; the server has raised an alert | the owner opens the app | the plant is first in the list with "needs water"; the phone is not registered |

### plant

Kind: operation

```text
the owner opens a plant -> the latest reading and the history of the last 90 days
```

Pre: none; works without a network connection.
Result: the latest reading and the history of the last 90 days for soil moisture, light and temperature, with the age of the readings.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| low value, no alert yet | a fetched reading of 23 %, not uploaded | the owner opens the plant | 23 % in the history; the plant is not marked "needs water" |
| fetch on opening | the sensor stick in range holds 96 unconfirmed readings; no network | the owner opens the app, then the plant | a fetch starts within 5 seconds; afterwards the history holds the 96 readings |

### edit-plant

Kind: operation

```text
add, change or remove a plant: name, thresholds or a preset, optionally a sensor stick
```

Pre: none; possible without a network connection.
Result: the plant is added, changed or removed; a change is marked until the server has it.
Errors: a refusal by the server, shown with its reason.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| change offline | flight mode | the owner sets the limit to 25 % | 25 % within 1 second, marked "not yet sent"; the mark goes after the next exchange |

### pair

Kind: operation

```text
put a sensor stick to a plant: pairing with a sensor stick in range, then binding it to one plant
```

Pre: Bluetooth is on; no network connection is needed. A sensor stick is open for pairing only for a few minutes after its cell has been put in, as the BLE profile defines; the app tells the owner to do that.
Result: the sensor stick is paired and bound to the plant.
Errors: refused with the reason when 20 sensor sticks are paired.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| 21st sensor stick | 20 sensor sticks are paired | the owner puts a further sensor stick to a plant | pairing is refused with the reason; the 20 stay paired |

### notification-tap

Kind: operation

```text
the owner taps a notification -> the app opens the plant the notification is about
```

Pre: the notification is about an alert of a plant on this phone.
Result: the app opens the plant the notification is about.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| tap on a notification | a notification about the alert of "Monstera" is shown | the owner taps it | the app opens the screen of "Monstera" |

### owner

Kind: operation

```text
start without an account; show a code that a second phone scans to join the owner; leave the owner
```

Pre: none; showing the code and leaving need a network connection.
Result: the app asks for no name and no password and works from the first start, also without a network connection; the server creates the owner at the first exchange. On a second phone the owner scans a code the first phone shows; from then on it shows the same plants, history and alerts. A phone that leaves its owner uploads what is waiting and then holds nothing of the owner.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| first start | a new phone in flight mode | the owner starts the app | the app works and asks for no name and no password |
| move to a new phone | a second phone has joined with the code of the first | the first phone leaves the owner | the first phone shows the welcome screen and holds no plant; the second shows the plants |

## Fake

The real implementation: no fake stands in for the app. The tests of the owner's promises are the end-to-end tests of `test-rig`, which observe the public API, and the screen tests of `mobile` against prepared data.
