# sensor-io as sampling expects it

The contract of the need `sensor-io`: the interface `sampling` requires of
whoever provides raw sensor values. The
[calibration](calibration.md) rests on these scales. If a scale changes,
its constants change with it.

## Request and answer

`sampling` sends one request per reading. The answer comes within 300 ms and
holds three raw values:

| Raw value | Type | Scale |
|---|---|---|
| Soil | Integer, 0 to 4095 | Output voltage of the probe as a share of its supply voltage; 4095 is the full supply. Higher means drier. |
| Light | Unsigned integer of at least 24 bits | One count is 0.01 lux at the sensor |
| Temperature | Signed integer of at least 16 bits | One count is 1/16 °C at the sensor |

## What sampling relies on

- Each value is a number or "unavailable", on its own. A sensor that does
  not answer gives "unavailable": never 0, never an earlier value.
- The soil value does not move with the voltage of the cell.
- The values are as the sensors deliver them: not averaged, not clamped,
  not calibrated.
- The sensors draw no current between two requests. `sampling` does not
  switch them.

## Examples

The cases a provider has to pass, a substitute included.

| Case | Expected answer |
|---|---|
| The probe output is 40 % of its supply, at 3.0 V and at 2.4 V | Soil 1638 both times |
| 7 500 lux at the sensor | Light 750 000 |
| 21.8125 °C at the sensor | Temperature 349 |
| −19.5625 °C at the sensor | Temperature −313 |
| The light and temperature sensor is disconnected | Soil as measured; light and temperature "unavailable"; the answer still comes within 300 ms |
| Two requests 900 s apart | No sensor current flows between them |
