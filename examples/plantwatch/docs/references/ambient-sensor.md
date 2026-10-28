# ambient-sensor

Contract of the need `ambient-sensor` of plantwatch: the light and temperature sensor of the sensor stick, one device on an I2C bus at 100 kHz, placed where it sees the light the plant sees. Notation: the bus transaction as text.
Sources: the data sheet of the sensor, reduced to what the firmware relies on.

## Parts

### read

Kind: query

```text
I2C request at 100 kHz -> light (lux) and temperature (°C), both within 150 ms
```

Pre: the supply is 2.0 V to 3.3 V.
Result: both values within 150 ms after a request: light from 0 to at least 100 000 lux, temperature from -20 °C to 60 °C. Without a request the sensor draws at most 1 µA.
Errors: no answer within 150 ms; the firmware treats both values as unavailable.
Examples:

| Case | Input | Expected |
|---|---|---|
| daylight | a request in daylight at 7 500 lux and 21.8 °C | both values within 150 ms |
| idle | no request for an hour | at most 1 µA drawn |
| silent | the sensor does not answer within 150 ms | no values; the requester treats both as unavailable |

### sensor

Kind: type

```text
sensor { bus: I2C, 100 kHz, one device; light: 0 to >= 100 000 lux; temperature: -20 °C to 60 °C; supply: 2.0 V to 3.3 V; answer: <= 150 ms; idle current: <= 1 µA }
```

| Property | Value |
|---|---|
| bus | one device on an I2C bus at 100 kHz |
| light | 0 to at least 100 000 lux |
| temperature | -20 °C to 60 °C |
| supply | 2.0 V to 3.3 V |
| answer | both values within 150 ms after a request |
| idle current | at most 1 µA |
| placement | where it sees the light the plant sees |

## Fake

A simulated I2C device that answers a request with the light and temperature a test has set. Faults it can inject: silence, so that no answer comes within 150 ms.
