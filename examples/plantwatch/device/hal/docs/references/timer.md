# timer

The contract of the capability `timer`: the tick count and the alarms of the
board.

## Operations

| Operation | Behaviour |
|---|---|
| Tick count | Returns the boot counter and the seconds since this start |
| Set alarm | Takes one of 4 alarms and a value of seconds since start. `hal` calls the caller at that second: not earlier, and at most 100 ms later. A value in the past is called within 100 ms. Setting an alarm again replaces its time. |
| Cancel alarm | The alarm is not called |

## Guarantees

- **Boot counter.** 1 at the first start of a board. Higher at every later
  start: by one, or by two when power was lost while the start before was
  being counted. It never repeats, also after the cell was out. `hal` counts
  the start before any caller can ask for the tick count.
- **Seconds.** 0 at a start. They rise by one per second, also while the
  board sleeps, with an error of at most 50 ppm.
- **Alarms** may be set from inside an alarm call. The board sleeps until
  the next alarm or radio event.
- **Weak cell.** `hal` does not start the board while the supply is below
  2.1 V, so a start always has the energy to be counted.
- **End.** The boot counter ends at 65 535. `hal` does not start the board
  after that.

## Examples

| Case | Expected |
|---|---|
| First start of a new board | Tick count 1 / 0 |
| The cell is taken out after the third start and put back a week later | Tick count 4 / 0; the seconds count from 0 |
| Power is lost while the fifth start is being counted | The next start reports 5 or 6, never 4 |
| The cell is put in at 2.0 V | The board does not start; the boot counter keeps its value |
| At second 5 an alarm is set for second 900 | The call comes between 900.0 s and 900.1 s |
| At second 250 an alarm is set for second 100 | The call comes within 100 ms |
| 30 days pass on a reference clock | The seconds advance by 2 592 000 ± 130 |
