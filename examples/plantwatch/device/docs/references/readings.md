# readings

Contract of `sampling.readings`, which `store` names `readings` and `link` names `live-readings`: every new reading at the moment it is taken, as the provider hands it to each subscriber. Notation: wit.
Sources: the reading schema and decision 0005 of plantwatch, decision 0003 of `device`.

## Parts

### subscribe

Kind: command

```wit
subscribe: func(subscriber: subscriber) -> result<_, subscribe-error>;
```

Pre: called once per subscriber, at start; fewer than 4 subscribers are registered.
Result: every reading reaches this subscriber once, in ascending order of sequence number, at the moment it is taken. Subscribers are called one after another, in the order in which they registered, and all have returned before the next reading is taken.
Errors: `too-many` when 4 subscribers are registered already.
Examples:

| Case | Input | Expected |
|---|---|---|
| two subscribers | `store`, then `link` subscribe; a reading is taken | `store` receives it, then `link`; each once |
| a fifth | `subscribe` with 4 registered | `too-many` |

### new-reading

Kind: event

```wit
new-reading: func(reading: reading);
```

A reading does not change after it has been handed out.

### sampling-interval

Kind: query

```wit
sampling-interval: func() -> u16;
```

Pre: none.
Result: the sampling interval in seconds.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| default interval | `sampling-interval()` | 900 |

### reading

Kind: type

```wit
record reading {
  sequence-number: u32,
  ticks: tick-count,
  soil-moisture: option<u16>,
  light: option<u32>,
  temperature: option<s16>,
}
```

| Field | Form |
|---|---|
| sequence-number | unsigned 32 bit, never 0; rises strictly over the life of a board: consecutive between two starts, with a jump at every start |
| ticks | boot counter and seconds since start at the moment of measuring, the [tick count](timer.md#tick-count) |
| soil-moisture | 0.0 to 100.0 percent in steps of 0.1, carried as tenths, or absent |
| light | 0 to 100 000 lux in steps of 1, or absent |
| temperature | −20.0 to 60.0 °C in steps of 0.1, carried as tenths, or absent |

The 97th reading of start 12, for example: sequence number 3 145 825, tick count 12 / 86 405 s, soil moisture 41.5 %, light 12 000 lx, temperature 21.4 °C.

### subscribe-error

Kind: type

```wit
variant subscribe-error { too-many }
```

## Fake

A publisher that a test drives: `emit(reading)` hands one reading to every subscriber in the order of registration and returns when all have returned. `sampling-interval` answers the value the test set, 900 by default. Faults it can inject: none.
