# Readings

The contract of the connections `readings` and `live-readings`: every new reading at the moment it is taken, as the provider hands it to each subscriber.

## A reading

| Part | Form |
|---|---|
| Sequence number | Unsigned 32 bit, never 0 |
| Tick count | Boot counter and seconds since start at the moment of measuring |
| Soil moisture | 0.0 to 100.0 percent in steps of 0.1, or absent |
| Light | 0 to 100 000 lux in steps of 1, or absent |
| Temperature | -20.0 to 60.0 °C in steps of 0.1, or absent |

## Delivery

- A subscriber registers once, at start. Up to 4 subscribers.
- Every reading reaches every subscriber once, in ascending order of sequence number, at the moment it is taken. Subscribers are called one after another, in the order in which they registered; all have returned before the next reading is taken.
- A reading does not change after it has been handed out.
- Sequence numbers rise strictly over the life of a board: consecutive between two starts, with a jump at every start.
- On request, the sampling interval in seconds.

## Example

```text
sequence number   3 145 825        (start 12, 97th reading)
tick count        12 / 86 405 s
soil moisture     41.5 %
light             12 000 lx
temperature       21.4 °C
```
