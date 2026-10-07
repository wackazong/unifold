---
unit: sampling
summary: Takes a calibrated reading at every sampling interval
kind: library
status: planned
provides:
  readings:
    kind: library
    summary: Calibrated readings, one per sampling interval, delivered to subscribers
needs:
  sensor-io:
    kind: library
    summary: Raw sensor values on request
  timer:
    kind: library
    summary: Wakes the device at the next sampling time and counts ticks across sleep
---
# sampling

sampling is the place where a reading comes into being. At every sampling
interval it asks for raw sensor values, converts them into soil moisture,
light and temperature, gives the reading its sequence number and tick
count, and hands it to everyone who has subscribed.

## Provides

### `readings`

A subscriber registers once, at start. From then on it receives every
reading, once, in order, at the moment the reading is taken.

A reading consists of:

| Part | Form |
|---|---|
| Sequence number | Unsigned 32 bit, never 0 |
| Tick count | Boot counter and seconds since start at the moment of measuring |
| Soil moisture | 0.0 to 100.0 percent in steps of 0.1, or absent |
| Light | 0 to 100 000 lux in steps of 1, or absent |
| Temperature | −20.0 to 60.0 °C in steps of 0.1, or absent |

What a subscriber can rely on:

- **One reading per sampling interval.** The first is taken within 10 s
  after start, the following ones at whole multiples of the interval after
  the first. sampling never skips one. If no sensor answers, the reading
  has all three quantities absent.
- **The interval** is 900 s unless the firmware was built with another
  value between 300 s and 3600 s. It does not change while the firmware
  runs. sampling tells a caller the interval on request.
- **Sequence numbers rise strictly** over the whole life of a board, also
  across starts. They are consecutive between two starts and jump at a
  start.
- **Absent, not wrong.** A quantity is absent when its raw value is
  unavailable or implausible. No quantity is ever outside its range.
- **Order of delivery.** sampling calls the subscribers one after another,
  in the order in which they registered. All of them have returned before
  the next reading is taken.
- **A reading does not change** after it has been handed out.

Limits: up to 4 subscribers. A board gives readings for 16 383 starts and
for 262 143 readings per start; after that sampling takes no more. Soil
moisture is calibrated for the type of probe, not for the single board,
and is accurate to about 5 percentage points.

A reading as a subscriber sees it:

```text
sequence number   3 145 825        (start 12, 97th reading)
tick count        12 / 86 405 s
soil moisture     41.5 %
light             12 000 lx
temperature       21.4 °C
```

## Needs

### `sensor-io`

On request, one set of raw values: a soil value that falls as the soil
gets wetter, a light value that is proportional to the illuminance, and a
temperature value in fixed steps. Each of the three can be reported as
unavailable on its own. The answer comes within 250 ms. sampling asks once
per reading and expects the sensors to draw no current in between. The
scale that sampling assumes for each raw value is in the
[calibration](doc/references/calibration.md).

### `timer`

- A tick count: a boot counter that rises by one at every start and never
  repeats, and the seconds since start, which go on while the board sleeps
  and are wrong by at most 100 ppm.
- An alarm: sampling names a second, and is called not before that second
  and at most 1 s after it. The board may sleep until then.

## Out of scope

- Keeping readings. A reading that no subscriber keeps is gone.
- Sending readings anywhere.
- Changing the sampling interval while the firmware runs.
- Smoothing over several readings. Every reading stands for one moment.
- Judging whether a value is good or bad for a plant.

## More

- [AGENTS.md](AGENTS.md): why readings are made here and numbered this way
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- [Calibration](doc/references/calibration.md): from raw values to percent, lux and degrees
