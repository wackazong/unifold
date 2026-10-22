# Ambient sensor

The contract of the need `ambient-sensor`: the light and temperature sensor of the sensor stick.

| Property | Value |
|---|---|
| Bus | One device on an I2C bus at 100 kHz |
| Light | 0 to at least 100 000 lux |
| Temperature | -20 °C to 60 °C |
| Supply | 2.0 V to 3.3 V |
| Answer | Both values within 150 ms after a request |
| Idle current | At most 1 µA |
| Placement | Where it sees the light the plant sees |

## Examples

| Case | Expected |
|---|---|
| A request in daylight at 7 500 lux and 21.8 °C | Both values within 150 ms |
| No request for an hour | At most 1 µA drawn |
