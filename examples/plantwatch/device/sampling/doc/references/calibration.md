# Calibration

How `sampling` converts raw sensor values into the quantities of a reading.
The constants are planned values. They are replaced by measured ones
before the first boards are used. The example tables are the first test
cases of the conversion.

## Raw values

The scales of the three raw values are part of what `sampling` expects of
`sensor-io`: [sensor-io](sensor-io.md). The constants below rest on them.

## Constants

| Constant | Value | Meaning | Source |
|---|---|---|---|
| `SOIL_DRY` | 3400 | Soil raw value with the probe in dry air | Planned, from the probe's data sheet |
| `SOIL_WET` | 1640 | Soil raw value with the probe in water up to the mark | Planned, from the probe's data sheet |
| `SOIL_MIN_PLAUSIBLE` | 800 | Below this the probe is shorted or missing | Planned |
| `SOIL_MAX_PLAUSIBLE` | 3900 | Above this the probe is disconnected | Planned |
| `LIGHT_LUX_PER_COUNT` | 0.01 | Scale of the light raw value | Definition of the raw value |
| `LIGHT_WINDOW_FACTOR` | 1.6 | Compensates the light the housing window absorbs | Planned, to be measured with the housing |
| `TEMP_C_PER_COUNT` | 0.0625 | Scale of the temperature raw value | Definition of the raw value |
| `TEMP_OFFSET_C` | −0.4 | Compensates the warmth of the board | Planned, to be measured |

## Soil moisture

```text
moisture = (SOIL_DRY − raw) × 100 / (SOIL_DRY − SOIL_WET)
```

| Condition | Result |
|---|---|
| Raw value unavailable | Absent |
| `raw` below `SOIL_MIN_PLAUSIBLE` or above `SOIL_MAX_PLAUSIBLE` | Absent |
| `moisture` below 0 | 0.0 |
| `moisture` above 100 | 100.0 |
| Otherwise | `moisture`, rounded to 0.1 |

"Percent of the calibrated range" means: 0 is the probe in dry air, 100 is
the probe in water. Garden soil at field capacity reads about 70 to 85.

| Raw | Soil moisture |
|---|---|
| 3950 | absent |
| 3500 | 0.0 |
| 3400 | 0.0 |
| 2670 | 41.5 |
| 1640 | 100.0 |
| 1500 | 100.0 |
| 700 | absent |

## Light

```text
light = raw × LIGHT_LUX_PER_COUNT × LIGHT_WINDOW_FACTOR
```

| Condition | Result |
|---|---|
| Raw value unavailable | Absent |
| `light` above 100 000 | 100 000 |
| Otherwise | `light`, rounded to a whole number |

| Raw | Light |
|---|---|
| unavailable | absent |
| 0 | 0 |
| 750 000 | 12 000 |
| 7 000 000 | 100 000 |

## Temperature

```text
temperature = raw × TEMP_C_PER_COUNT + TEMP_OFFSET_C
```

| Condition | Result |
|---|---|
| Raw value unavailable | Absent |
| Rounded `temperature` below −20.0 or above 60.0 | Absent |
| Otherwise | `temperature`, rounded to 0.1 |

A temperature outside the range is absent and not clamped: the board is
not specified there, and a clamped value would look like a measurement.

| Raw | Temperature |
|---|---|
| 349 | 21.4 |
| 966 | 60.0 |
| 968 | absent |
| −313 | −20.0 |
| −330 | absent |

## Rounding

`sampling` rounds half away from zero, once, as the last step. It computes
with integers scaled by 10; no floating point is needed.

## Expected accuracy

| Quantity | Error | Dominated by |
|---|---|---|
| Soil moisture | ±5 percentage points | Spread between probes of one type |
| Light | ±15 % | Angle of the light and the housing window |
| Temperature | ±0.5 °C | The sensor |
