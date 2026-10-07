# What the screens expect of `plant-data`

The interface ui requires of whoever provides `plant-data`, in ui's own
words. ui is built and tested against a stand-in that meets this file and
holds the prepared data at its end. The things named are those of the data
model cited in [context.md](../context.md).

## What ui asks for

Every answer can be observed: ui gets it again whenever it changes.

| ui asks for | It gets |
|---|---|
| All plants | Every plant with name, change state and, if refused, the reason; its newest reading or none; its open alerts; the age of its readings. Plants with an open alert come first, then by name. |
| One plant | The same for one plant, or "unknown" |
| The history of a plant for a span | For a day the single readings; for a week one entry per hour; for 90 days one entry per day. An entry holds minimum, mean and maximum per quantity and says whether a time in it is estimated. |
| The alerts of a plant | Open alerts and those closed within the last 90 days, newest first |
| The state of the app | Whether the phone acts for an owner, not yet, or has lost its access; the id of that owner once it exists; the time of the last successful exchange |

## What ui tells it to do

| ui says | Result |
|---|---|
| Start; join with a token; leave | Done, or a failure ui can show |
| Give a token for another phone | A token, or "network needed" |
| Create, change or remove a plant | The observed answers change; a failure names the field or the limit |
| Dismiss a refusal | The plant is `in step` |
| Ask for fresh data now | An answer when the attempt has ended |

## Limits ui relies on

- An answer comes from data on the phone within 100 milliseconds, with or
  without a network connection.
- After a change, the observed answer arrives within 1 second.
- When a command has returned, its effect survives a restart of the
  program. ui keeps no copy.
- No answer contains an alert that the server did not send.

## Prepared data

The stand-in holds these cases. Each is also a test of the screen named.

| Case | Data | The screen shows |
|---|---|---|
| First start | The phone acts for no owner | "Welcome" |
| No plant | An owner, no plant | "Plant list" in the state "empty" |
| No sensor stick | One plant without a sensor stick and without readings | The plant with "no value" and no age |
| Full list | 50 plants, 20 of them with an open alert | 50 rows without paging; the 20 first, each with its reason |
| Aged | One plant whose newest reading is 3 days old | "No readings since" with the time |
| Waiting and refused | One plant `waiting`, one `refused` with a reason | "Not yet sent"; "Not accepted" with the reason and "OK" |
| Estimated | A day of readings, half with estimated times | "about" before those times; that part of the chart dashed |
| Absent quantity | Readings without light | "no value" for light; soil moisture and temperature as usual |
| Low value, no alert | Soil moisture 12 % with a lower limit of 30 %, no alert | 12 % and no "needs water" |
| Access lost | The phone has lost its access | The bar "This phone can no longer reach your plants", all data visible |
