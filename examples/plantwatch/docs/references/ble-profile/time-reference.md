# time-reference

Kind: query

```text
taken_at(T, B, S, reading) ->
  reading.boot_counter == B:  T - (S - reading.seconds_since_boot), rounded to whole seconds; time_estimated false
  reference kept for reading.boot_counter: computed from that reference; time_estimated false
  otherwise: an estimate that keeps the order of the readings; time_estimated true
```

Pre: the central has read Status in the same connection, before the fetch, and noted its own UTC time `T` at the moment the response arrived; `B` is `boot_counter` and `S` is `seconds_since_boot` of that Status value. A sensor stick has no clock; a reading carries a tick count, and the central turns it into a UTC time.
Result: for a reading with `boot_counter` equal to `B`: `taken_at` = `T` − (`S` − `seconds_since_boot` of the reading), rounded to whole seconds, and `time_estimated` is `false`. For a reading with another `boot_counter`, the central uses a time reference it has kept for that boot counter and this sensor stick, if it has one; `time_estimated` is then `false`. Otherwise the central estimates `taken_at` and sets `time_estimated` to `true`; the estimate keeps the order of the readings and is not later than the start of the next boot that the central has a reference for. The central keeps the newest reference per sensor stick and boot counter.
Errors: none.
Examples:

| Case | Status read at `T` | Reading | Expected |
|---|---|---|---|
| Same boot | `T` 2026-10-06T07:30:05Z, `B` 12, `S` 87 305 | 12 / 86 400 | `taken_at` 2026-10-06T07:15:00Z, `time_estimated` `false` |
| Earlier boot, reference kept | as above | 11 / 500, reference for boot 11 exists | Computed from that reference, `false` |
| Earlier boot, no reference | as above | 11 / 500 | `time_estimated` `true`, `taken_at` not after 2026-10-05T07:15:00Z |
