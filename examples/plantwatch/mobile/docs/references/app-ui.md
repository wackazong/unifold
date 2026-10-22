# What the owner can rely on: contract of `app-ui`

The promises the app makes to its owner, independent of how a screen looks. The screens and the way between them are defined by [ui](../../ui/README.md). The things named here are those of the [data model](data-model.md).

## What the owner can do

| The owner wants to | The app guarantees |
|---|---|
| See which plants need attention | A list of all plants. Plants with an open alert come first, with the reason. |
| See how a plant is doing | The latest reading and the history of the last 90 days for soil moisture, light and temperature |
| Know how far to trust what is shown | The age of the plant's readings and the age of server data, on every screen that shows either |
| Add a plant | Name, thresholds or a preset, and optionally a sensor stick; possible without a network connection |
| Put a sensor stick to a plant | Pairing with a sensor stick in range and binding it to one plant; needs Bluetooth, no network connection. A sensor stick is open for pairing only for a few minutes after its cell has been put in, as the BLE profile defines; the app tells the owner to do that. |
| Change or remove a plant | Possible without a network connection; the change is marked until the server has it |
| React to a notification | A tap opens the plant the notification is about |
| Start without an account | The app asks for no name and no password and works from the first start, also without a network connection. The server creates the owner at the first exchange. |
| Use the app on a second phone | The first phone shows a code, the second phone scans it; from then on it shows the same plants, history and alerts |

## What happens without the owner

| Situation | The app guarantees |
|---|---|
| The phone comes near a paired sensor stick, app not open | The app fetches the stored readings as far as the operating system lets it run ([platform limits](platform-limits.md)) |
| The owner opens the app near a paired sensor stick | A fetch starts within 5 seconds and runs to the end while the app stays open |
| Readings are on the phone, a network connection exists | The app uploads them without being asked |
| Readings are on the phone, no network connection | They stay on the phone and are visible in the history |
| The owner has allowed notifications and the server has created the owner | The app registers the phone through `push-service` for its owner, and again whenever the platform changes the phone's address |
| The phone leaves its owner | The app ends that registration |

## Examples

Each case starts from a phone with one plant, "Monstera", whose sensor stick is paired, lower limit for soil moisture 30 %.

| Case | Given | Expected |
|---|---|---|
| Offline view | Flight mode; newest reading 2 days old | The plant with that reading and "2 days ago"; no error, no loading state |
| Fetch on opening | Sensor stick in range holds 96 unconfirmed readings; no network | A fetch starts within 5 seconds; afterwards the history holds the 96 readings |
| Low value, no alert yet | A fetched reading of 23 %, not uploaded | 23 % in the history; the plant is not marked "needs water" |
| Alert arrives | After the upload the server reports an open alert | The plant is first in the list with "needs water" |
| Change offline | Flight mode; the owner sets the limit to 25 % | 25 % within 1 second, marked "not yet sent"; the mark goes after the next exchange |
| Tap on a notification | A notification about the alert of "Monstera" | The app opens the screen of "Monstera" |
| 21st sensor stick | 20 sensor sticks are paired | Pairing is refused with the reason; the 20 stay paired |
| No notifications | The owner has not allowed notifications | No registration; the alert shows in the app |

## What the app does not promise

- A time by which a reading reaches the phone or the server. It depends on the phone coming near the sensor stick.
- Background fetching after a force-quit, with Bluetooth off or without the permissions.
- An alert on the phone before the server has raised it. A reading below a threshold that is not uploaded yet shows up in the history, not as an alert.
- Exact times for readings flagged as estimated.
- A way back to the owner's data for a phone that has lost its token while no other phone of the owner is at hand.

## Limits

| Limit | Value |
|---|---|
| Sensor sticks paired with one phone | 20 |
| Plants of one owner | 50 |
| History on the phone | 90 days per plant |
| Owners per phone | 1 |
| Systems | See [platform limits](platform-limits.md) |
| Languages | English and German |
| Screen orientation | Portrait |

The first three values are inherited; see [context.md](../explanation/context.md).

## Permissions

| Permission | Without it |
|---|---|
| Bluetooth | No pairing and no fetching. Everything already on the phone stays visible. The app says what is missing and leads to the system settings. |
| Notifications | No notifications. Alerts are visible in the app. |
| Camera | No joining an owner by scanning a code. Everything else works. |

The app asks for a permission at the moment the owner first needs it and says why.

## Accessibility

- Every state that is shown by colour is also shown by text or a symbol.
- Every control has a label for screen readers.
- Text follows the text size set in the system.
