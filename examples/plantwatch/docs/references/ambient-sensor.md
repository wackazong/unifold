# ambient-sensor

Contract of the need `ambient-sensor` of plantwatch: the light and temperature sensor of the sensor stick, one device on an I2C bus at 100 kHz, placed where it sees the light the plant sees. Notation: the bus transaction as text.
Sources: the data sheet of the sensor, reduced to what the firmware relies on.
Binding: i2c
Version: 1

## Use

The firmware sends a request and waits up to 150 ms for both values. The sensor has no state that the firmware must respect. A request may be sent at any time while the supply is 2.0 V to 3.3 V.

## Qualities

| Aspect | Guarantee |
|---|---|
| latency | both values within 150 ms after a request |
| power | at most 1 µA without a request |
| supply | 2.0 V to 3.3 V |
| ranges | light from 0 to at least 100 000 lux; temperature from -20 °C to 60 °C |

## Parts

### read

Kind: query

```text
I2C request at 100 kHz -> light (lux) and temperature (°C), both within 150 ms
```

Pre: the supply is 2.0 V to 3.3 V.
Result: both values within 150 ms after a request: light from 0 to at least 100 000 lux, temperature from -20 °C to 60 °C.
Errors: no answer within 150 ms; the firmware treats both values as unavailable.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| daylight | 7 500 lux and 21.8 °C at the sensor | a request | both values within 150 ms |
| idle | no request for an hour | the current drawn is measured | at most 1 µA |
| silent | the sensor does not answer | a request | no values within 150 ms; the requester treats both as unavailable |

## Fake

A simulated I2C device that answers a request with the light and temperature a test has set. Faults it can inject: silence, so that no answer comes within 150 ms.
