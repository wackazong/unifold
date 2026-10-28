# timer

Contract of `hal.timer`: the tick count and the alarms of the board. The provider does not start the board while the supply is below 2.1 V, so a start always has the energy to be counted. Notation: wit.
Sources: the board of the sensor stick as `hal` abstracts it; decision 0003 of `device` for the tick count.

## Parts

### ticks

Kind: query

```wit
ticks: func() -> tick-count;
```

Pre: none.
Result: the boot counter and the seconds since this start. The boot counter is 1 at the first start of a board and higher at every later start: by one, or by two when power was lost while the start before was being counted. It never repeats, also after the cell was out. The provider counts the start before any caller can ask for the tick count. The seconds are 0 at a start and rise by one per second, also while the board sleeps, with an error of at most 50 ppm. The boot counter ends at 65 535; the provider does not start the board after that.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| first start of a new board | `ticks()` | 1 / 0 |
| cell out after the third start, back a week later | `ticks()` after the start | 4 / 0; the seconds count from 0 |
| power lost while the fifth start was being counted | `ticks()` at the next start | boot counter 5 or 6, never 4 |
| cell put in at 2.0 V | the board does not start | the boot counter keeps its value |
| 30 days pass on a reference clock | the seconds | advance by 2 592 000 ± 130 |

### set-alarm

Kind: command

```wit
set-alarm: func(alarm: u8, at-second: u32);
```

Pre: `alarm` is one of the 4 alarms, 0 to 3.
Result: the provider raises `alarm` at that second of this start: not earlier, and at most 100 ms later. A value in the past is raised within 100 ms. Setting an alarm again replaces its time. An alarm may be set from inside an alarm call. The board sleeps until the next alarm or radio event.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| in the future | at second 5, `set-alarm(0, 900)` | the call comes between 900.0 s and 900.1 s |
| in the past | at second 250, `set-alarm(0, 100)` | the call comes within 100 ms |
| set again | `set-alarm(0, 900)`, then `set-alarm(0, 1800)` | one call, at second 1800 |

### cancel-alarm

Kind: command

```wit
cancel-alarm: func(alarm: u8);
```

Pre: `alarm` is 0 to 3.
Result: the alarm is not raised.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| cancelled | `set-alarm(0, 900)`, then `cancel-alarm(0)` | no call at second 900 |

### alarm

Kind: event

```wit
alarm: func(alarm: u8, now: tick-count);
```

### tick-count

Kind: type

```wit
record tick-count { boot-counter: u16, seconds-since-boot: u32 }
```

| Field | Meaning |
|---|---|
| boot-counter | counts the starts of the board, 1 at the first start |
| seconds-since-boot | seconds since this start |

## Fake

A timer in memory that stands still until a test moves it: `advance(seconds)` adds to the seconds and raises every alarm that falls due, in order; `restart()` raises the boot counter by one and sets the seconds to 0. Faults it can inject: a start that was lost while being counted, so that the boot counter rises by two.
