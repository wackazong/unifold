# timer as sampling expects it

The contract of the need `timer`: the time `sampling` requires of whoever
provides it. `sampling` stamps every reading with the tick count and takes
its sampling times from the alarm.

## Tick count

| Part | What `sampling` expects |
|---|---|
| Boot counter | A whole number of 1 or more that is higher at every start than at any start before, also after the cell was out. It is ready before `sampling` asks for it. |
| Seconds since start | 0 at a start, then one more per second, also while the board sleeps. Wrong by at most 100 ppm. |

`sampling` uses boot counters up to 16 383 and reads the tick count once per
reading.

## Alarm

`sampling` needs one alarm. It names a value of seconds since start and is
called not before that second and at most 1 s after it. The board may
sleep until then. `sampling` sets the next alarm from inside the call.

## Examples

The cases a provider has to pass, a substitute included.

| Case | Expected |
|---|---|
| A start, and the start after it | The second boot counter is higher than the first |
| The cell is out for a week between two starts | The same |
| At second 5 `sampling` sets the alarm for second 905 | The call comes between 905.0 s and 906.0 s |
| Inside that call `sampling` sets the alarm for second 1805 | The call comes between 1805.0 s and 1806.0 s |
| 86 400 s pass on a reference clock while the board mostly sleeps | The seconds advance by 86 400 ± 9 |
