# timer

Contract of `hal.timer`: the tick count and the alarms of the board. The provider does not start the board while the supply is below 2.1 V, so a start always has the energy to be counted. Notation: wit.
Sources: the board of the sensor stick as `hal` abstracts it.
Binding: in-process

## Use

The caller reads the tick count, sets an alarm for a second of this start, and receives `alarm` when that second has come. Setting an alarm again replaces its time, and an alarm may be set from inside an alarm call. No call depends on an earlier one: any part may be called at any time. The board sleeps until the next alarm or radio event.

## Qualities

| Aspect | Guarantee |
|---|---|
| accuracy | the seconds rise by one per second, also while the board sleeps, with an error of at most 50 ppm |
| latency | an alarm is raised not earlier than its second and at most 100 ms later; a value in the past is raised within 100 ms |
| limits | 4 alarms, 0 to 3; the boot counter ends at 65 535, and the provider does not start the board after that |
| concurrency | `hal` delivers the events and alarms of all four contracts one after another, never two at the same time; whenever no event is being handled, the board sleeps, keeps counting time and keeps the radio schedule, and draws the sleep current of the board reference |

## Parts

### ticks

Kind: operation

```wit
ticks: func() -> tick-count;
```

Pre: none.
Result: the boot counter and the seconds since this start. The boot counter is 1 at the first start of a board and higher at every later start: by one, or by two when power was lost while the start before was being counted. It never repeats, also after the cell was out. The provider counts the start before any caller can ask for the tick count. The seconds are 0 at a start.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| first start of a new board | a board that never started | `ticks()` | 1 / 0 |
| cell out after the third start, back a week later | the cell was out for a week after the third start | `ticks()` after the start | 4 / 0; the seconds count from 0 |
| power lost while the fifth start was being counted | power was lost while the fifth start was being counted | `ticks()` at the next start | boot counter 5 or 6, never 4 |
| cell put in at 2.0 V | the cell was put in at 2.0 V | `ticks()` | no answer: the board does not start, and the boot counter keeps its value |
| 30 days pass | 30 days passed on a reference clock since the start | `ticks()` | the seconds are 2 592 000 ± 130 |

### set-alarm

Kind: operation

```wit
set-alarm: func(alarm: u8, at-second: u32);
```

Pre: `alarm` is one of the 4 alarms, 0 to 3.
Result: the provider raises `alarm` at that second of this start. Setting an alarm again replaces its time. An alarm may be set from inside an alarm call.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| in the future | the seconds are at 5 | `set-alarm(0, 900)` | the call comes between 900.0 s and 900.1 s |
| in the past | the seconds are at 250 | `set-alarm(0, 100)` | the call comes within 100 ms |
| set again | `set-alarm(0, 900)` was called | `set-alarm(0, 1800)` | one call, at second 1800 |

### alarm

Kind: event

```wit
alarm: func(alarm: u8, now: tick-count);
```

When: the second for which the alarm was set has come, or the alarm was set to a second in the past.
Delivery: exactly once per `set-alarm` that is not replaced, in the order of the alarm times.

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
