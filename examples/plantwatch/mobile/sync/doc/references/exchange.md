# Exchange with the server

The steps, sizes and pauses of one exchange between the
[local store](local-store.md) and the server behind `cloud-api`. The
reasons are in the [decisions](../decisions/index.md).

## What starts an exchange

| Trigger | Remark |
|---|---|
| A batch of readings has been stored | Only steps 1 to 3 if the program runs in the background |
| A command has changed a plant | |
| The program comes onto the screen | |
| A network connection appears | |
| The operating system grants a slot of scheduled background work | |
| "Refresh" of [plant-data](plant-data.md) | Ignores a running pause |

One exchange runs at a time. A trigger during a running exchange causes one
more exchange directly after it.

## Steps of an exchange

| Step | sync | Ends the exchange on failure |
|---|---|---|
| 1 | Lets the server create the owner if it has not done so. Renews the token if it is valid for less than 30 days. | Yes |
| 2 | Sends the waiting changes of plants, oldest first, and takes each answer as the new state of the plant | Yes, on "try again later"; a refusal marks the plant and the exchange goes on |
| 3 | Uploads `fetched` readings in batches, oldest first, for every sensor stick the server knows as bound to a plant | Yes |
| 4 | Asks for the owner's plants and replaces every plant that has no waiting change | Yes |
| 5 | Asks for the alerts and replaces the alerts in the store | Yes |
| 6 | Asks for the history of each plant for the part of the last 90 days the store does not hold | No |

An exchange that completed step 5 counts as successful and sets the time
of the last exchange.

Step 6 runs only while the program is on the screen. It serves a phone that
has joined its owner later than the readings were taken.

## Sending a changed plant

| Waiting change | sync |
|---|---|
| New plant | Writes the whole plant under its id |
| Changed settings | Reads the server's version of the plant, lays the changed settings over it, and writes the result as a whole. Settings the phone does not show, such as upper limits, pass through untouched. |
| Changed settings, and the server has no such plant | Marks the plant `refused` with `removed elsewhere` and writes nothing |
| Removal | Removes the plant on the server |

## Upload batches

| Parameter | Value |
|---|---|
| Readings per batch | Up to 500, all of one sensor stick |
| Order within a sensor stick | Ascending sequence number |
| Order between sensor sticks | The one with the oldest `fetched` reading first |
| Requests at a time | 1 |
| Time limit per request | 20 seconds |

For every reading of a batch the server's answer is one of three: new,
known already, or refused. sync marks the first two as `confirmed` and the
third as `refused`. An answer that does not cover every reading of the
batch counts as "try again later".

## Answers of the server

| Answer | sync |
|---|---|
| Success | Goes on |
| No answer, time limit reached, or an error that says "try again later" | Ends the exchange, records `no network` or `server unavailable`, starts a pause. If the server names a waiting time, the pause is at least that long. |
| The token is not accepted | Ends the exchange, sets the session to `lost`, tries no further exchange until the phone has joined an owner again |
| The request is wrong, for a change of a plant | Marks the plant `refused` with the reason, takes the server's version of the plant |
| The request is wrong, for a batch of readings as a whole | Treats it as "try again later" and reports it |

## Pauses after a failure

| Parameter | Value |
|---|---|
| First pause | 30 seconds |
| Each further pause | Twice the one before, plus or minus up to 20 percent at random |
| Longest pause | 1 hour |
| A pause ends early when | The program comes onto the screen, a network connection appears, or "refresh" is called |
| The pause is reset to 30 seconds by | A successful exchange |

During a pause, triggers are remembered and no request is sent.

## In the background

In a background slot sync stores first and acknowledges the batch. It
starts an exchange only afterwards and gives up without a failure record
when the slot ends. The readings stay `fetched` and go with the next
exchange.
