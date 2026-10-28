# sensor-io

Contract of `hal.sensor-io`: what a caller gets when it asks for raw sensor values. The provider returns what the sensors deliver; it does not calibrate, average, clamp or judge. Between two measurements both sensors are without supply. Notation: wit.
Sources: the contracts of the needs `soil-probe` and `ambient-sensor` of plantwatch, and the board.

## Parts

### measure

Kind: query

```wit
measure: func() -> result<raw-values, sensor-error>;
```

Pre: no measurement runs.
Result: the provider powers the soil probe and the ambient sensor, measures each once, powers both off and returns three raw values within 300 ms. Each value is a number or `unavailable`, independently of the other two. The provider never returns 0 or an earlier value in place of a missing one.
Errors: `busy` while a measurement runs; the provider refuses the request.
Examples:

| Case | Input | Expected |
|---|---|---|
| probe at 1.20 V, supply 3.00 V | `measure()` | soil 1638 |
| the same soil with the cell at 2.40 V, probe at 0.96 V | `measure()` | soil 1638 |
| 7 500 lux at the sensor | `measure()` | light 750 000 |
| darkness | `measure()` | light 0, not `unavailable` |
| 21.8125 °C at the sensor | `measure()` | temperature 349 |
| −19.5625 °C at the sensor | `measure()` | temperature −313 |
| ambient sensor silent for 150 ms | `measure()` | soil as measured; light and temperature `unavailable`; still within 300 ms |
| during a measurement | `measure()` while one runs | `busy` |

### raw-values

Kind: type

```wit
record raw-values { soil: option<u16>, light: option<u32>, temperature: option<s16> }
```

| Field | Range | Scale |
|---|---|---|
| soil | 0 to 4095 | output voltage of the probe divided by its supply voltage, times 4095; higher means drier |
| light | 0 to 4 294 967 295 | one count is 0.01 lux at the sensor |
| temperature | −32 768 to 32 767 | one count is 1/16 °C at the sensor |

An absent value is `unavailable`.

### sensor-error

Kind: type

```wit
variant sensor-error { busy }
```

## Fake

Answers each call with the raw values a test has scripted, in order, and replays the examples by default. Faults it can inject: `unavailable` for any one of the three values, and `busy`.
