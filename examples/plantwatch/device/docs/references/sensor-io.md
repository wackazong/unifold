# sensor-io

The contract of the capability `sensor-io`: what a caller gets when it asks for raw sensor values.

## Operation

| Operation | Behaviour |
|---|---|
| Measure | Powers the soil probe and the ambient sensor, measures each once, powers both off and returns three raw values. Returns within 300 ms. The provider refuses a request while a measurement runs. |

## Raw values

| Value | Range | Scale |
|---|---|---|
| Soil | 0 to 4095 | Output voltage of the probe divided by its supply voltage, times 4095. Higher means drier. |
| Light | 0 to 4 294 967 295 | One count is 0.01 lux at the sensor |
| Temperature | −32 768 to 32 767 | One count is 1/16 °C at the sensor |

- Each value is a number or "unavailable", independently of the other two. The provider never returns 0 or an earlier value in place of a missing one.
- The provider returns what the sensors deliver. It does not calibrate, average, clamp or judge.
- Between two measurements both sensors are without supply.

## Examples

| Case | Returned |
|---|---|
| Probe output 1.20 V at a supply of 3.00 V | Soil 1638 |
| The same soil with the cell at 2.40 V: probe output 0.96 V | Soil 1638 |
| 7 500 lux at the sensor | Light 750 000 |
| Darkness | Light 0, not "unavailable" |
| 21.8125 °C at the sensor | Temperature 349 |
| −19.5625 °C at the sensor | Temperature −313 |
| The ambient sensor does not answer within 150 ms | Soil as measured; light and temperature "unavailable"; still within 300 ms |
