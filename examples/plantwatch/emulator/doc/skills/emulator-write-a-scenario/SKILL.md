---
name: emulator-write-a-scenario
description: Write a scenario file for the emulator - a course of soil moisture, light and temperature over simulated time, with restarts if needed. Use it when a situation of a plant or of a sensor stick shall be reproduced without hardware.
---
# Write a scenario

The result is a file `<name>.scenario.json` that the emulator plays, and a
check that it produces the readings you meant. A scenario that is written
without the check often has a track that never reaches the value it was
written for.

## Steps

1. **Say what shall happen** in one sentence, in terms of readings: for
   example "soil moisture falls below 20 % on day three" or "the sensor
   stick restarts while 200 readings are stored". Put the sentence into
   `description`.
2. **Choose the length.** Count in sampling intervals: at the default of
   900 s, a day has 96 readings, and the memory overflows after 2 880
   readings, that is after 30 days.
3. **Write one track per quantity** as points with `at_s` and `value`.
   - A value that changes steadily: two points, the program draws the
     line.
   - A value that jumps: set `step` on the point before the jump.
   - A daily cycle: one day of points and `repeat_s` of 86 400.
   - A sensor that fails: a point with `null`, and a later point with a
     number when it recovers.
   - A quantity that stays constant still needs a track with one point.
     Without a track it is absent in every reading.
4. **Add events** if the sensor stick shall restart. Use
   `skip_sequence_numbers` when a gap in the sequence numbers shall
   appear.
5. **Leave out what the defaults cover.** Set `sensor_id` only when
   several scenarios run side by side or a fixed id matters.
6. **Save** the file in the folder `scenarios/` of this unit, named after
   `name`.
7. **Load it**: `PUT /scenario` with the file as body. A 422 response
   names the member that breaks a rule.
8. **Play it**: `PUT /time` with the `elapsed_s` of the moment that
   matters, then `GET /readings`.

## Checks

- The reading at the moment that matters has the value from step 1. Look
  at the reading itself, not at the track: sampling happens only at
  multiples of the sampling interval.
- In a scenario without restarts, `readings_taken` in the state equals
  the elapsed time divided by the sampling interval, rounded down, plus
  one.
- Loading the scenario a second time and playing it again gives the same
  answer from `GET /readings`.

## Reference

- [Scenario format](../../references/scenario-format.md): members, tracks,
  events, and the rules for rejection
- [scenario-control API](../../references/scenario-control-api.md): the
  requests used in steps 7 and 8
