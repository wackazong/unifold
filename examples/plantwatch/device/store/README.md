# store

`store` keeps readings on the sensor stick from the moment they are taken
until someone has confirmed that they are safe elsewhere. It keeps them
through power loss, hands them out oldest first, and when its memory is
full it gives up the oldest readings in favour of new ones.

## Provides

### `reading-log`

The log of stored readings. "Stored" means: received by `store`, and neither
marked as delivered nor discarded.

| Operation | Effect |
|---|---|
| Summary | Returns the number of stored readings, the sequence numbers of the oldest and the newest stored reading, the highest sequence number `store` has ever received, the capacity, and whether `store` has discarded stored readings since the last mark or since start. A number that does not exist is 0. |
| Read | Takes a sequence number and returns the stored reading with the lowest sequence number at or above it, or "none". Asked again with the number after the one returned, it yields the stored readings in ascending order. |
| Mark as delivered | Takes a sequence number. Every reading up to that number is no longer stored. |

What a caller can rely on:

- **Durable.** When `store` has accepted a reading, the reading survives
  power loss and restart. It comes back from Read bit for bit as it was
  received.
- **Capacity.** `store` holds at least 2 880 stored readings.
- **Full.** When there is no room for a new reading, `store` discards the
  oldest stored readings, up to 204 at once, and says so in the summary.
  It never refuses a reading for lack of room.
- **Reading changes nothing.** Only Mark as delivered and a full memory
  remove a reading.
- **A mark is durable** when the call returns. A mark with a number at or
  below an earlier mark succeeds and changes nothing. `store` refuses a
  mark above the highest sequence number it has received.
- **Power loss at any moment** costs at most the reading or the mark that
  was being written. Everything written before is intact.
- **After a start** the log is complete before `store` accepts the first new
  reading. Recovery takes less than 100 ms, or less than 200 ms when power
  was lost during an erase.
- **Refused memory.** When `flash` refuses a write or an erase, a mark
  fails and says so, and a reading handed over is not stored. The log is
  then as it was before.

Limits: Read returns within 2 ms. A mark takes up to 2 ms, and up to
110 ms once in 510 marks. Accepting a reading takes up to 5 ms, and up to
110 ms once in 204 readings. `store` draws no conclusion from gaps between
sequence numbers.

```text
summary             -> stored 96, oldest 3145729, newest 3145824, capacity 3468
read 0              -> 3145729
read 3145730        -> 3145730        ... and so on up to 3145824
read 3145825        -> none
mark up to 3145824  -> ok
summary             -> stored 0, oldest 0, newest 0, highest received 3145824
```

## Needs

### `flash`

At least 20 blocks of 4096 bytes that keep their content without power,
with the usual properties of flash memory: a write changes whole 4-byte
words and only turns bits from 1 to 0, an erase works on a whole block,
and a block endures at least 10 000 erases. What has returned survives
power loss, and power loss damages only what was being written or erased.
`store` erases each block at most once in 12 days. Contract:
[flash](doc/references/flash.md).

### `readings`

Every new reading, once, in ascending order of sequence number, at the
moment it has been taken. A reading has a sequence number, a tick count,
and soil moisture in steps of 0.1 %, light in lux and temperature in
steps of 0.1 °C, each present or absent. `store` expects that the provider
waits until `store` has accepted one reading before it hands over the next.
`store` ignores a reading whose sequence number is not higher than the
highest it has received.

## Out of scope

- Deciding that a reading has been delivered. `store` is told.
- Any index other than the sequence number: no search by time or value.
- Storing anything that is not a reading: no settings, no keys.
- Changing or correcting a stored reading.

## More

- [AGENTS.md](AGENTS.md): why readings are kept in a log of this shape
- [doc/context.md](doc/context.md): what `store` inherits from above
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- [Flash layout](doc/references/flash-layout.md): blocks, records and recovery
