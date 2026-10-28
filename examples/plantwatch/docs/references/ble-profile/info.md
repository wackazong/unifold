# info

Kind: query

```text
read Info (0002), 18 bytes:
  offset 0  size 1  major               major version of the profile: 1
  offset 1  size 1  minor               minor version of the profile: 0
  offset 2  size 8  sensor_id           the sensor id, byte 0 first
  offset 10 size 1  quantities          quantities this sensor stick can measure, bits as in `present` of the record
  offset 11 size 2  sampling_interval   sampling interval in seconds, 300 to 3600
  offset 13 size 2  capacity            number of readings the sensor stick can hold, at least 2880
  offset 15 size 3  build               version of the implementation: major, minor, patch; for display and diagnosis only
```

Pre: a connection; no encryption is required.
Result: facts that do not change while the sensor stick runs, in the layout above.
Errors: none; Info is readable by anyone in range.
Examples:

| Case | Expected |
|---|---|
| Sensor id `00a1b2c3d4e5f607`, all three quantities, interval 900 s, capacity 2 880, build 1.0.0 | `01 00 00 A1 B2 C3 D4 E5 F6 07 07 84 03 40 0B 01 00 00` |
