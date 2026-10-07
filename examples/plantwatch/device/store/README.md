---
unit: store
summary: Keeps readings on the device until they have been delivered
kind: library
status: planned
provides:
  reading-log:
    kind: library
    summary: Stored readings oldest first, with a way to mark them as delivered
needs:
  flash:
    kind: library
    summary: Block storage that survives power loss
  readings:
    kind: library
    summary: Every new reading as soon as it has been taken
---
# store

store keeps readings on the sensor stick from the moment they are taken
until someone has confirmed that they are safe elsewhere. It keeps them
through power loss, hands them out oldest first, and when its memory is
full it gives up the oldest readings in favour of new ones.

## Provides

### `reading-log`

The log of stored readings. "Stored" means: received by store and not yet
marked as delivered.

| Operation | Effect |
|---|---|
| Summary | Returns the number of stored readings, the sequence numbers of the oldest and the newest stored reading, the highest sequence number store has ever received, the capacity, and whether store has discarded stored readings since the last mark or since start |
| Read | Returns the stored readings in ascending order of sequence number, beginning at a sequence number the caller names, one reading per call |
| Mark as delivered | Takes a sequence number. Every reading up to that number is no longer stored. |

What a caller can rely on:

- **Durable.** When store has accepted a reading, the reading survives
  power loss and restart. It comes back from Read bit for bit as it was
  received.
- **Capacity.** store holds at least 2 880 stored readings.
- **Full.** When there is no room for a new reading, store discards the
  oldest stored readings, up to 204 at once, and says so in the summary.
  It never refuses a new reading.
- **Reading changes nothing.** Only Mark as delivered and a full memory
  remove a reading.
- **A mark is durable** when the call returns. A mark with a number at or
  below an earlier mark succeeds and changes nothing. store refuses a
  mark above the highest sequence number it has received.
- **Power loss at any moment** costs at most the reading or the mark that
  was being written. Everything written before is intact.
- **After a start** the log is complete before store accepts the first new
  reading. Recovery takes less than 100 ms.

Limits: Read takes up to 2 ms per reading. Accepting a reading takes up to
5 ms, and up to 110 ms once in 204 readings. store draws no conclusion from
gaps between sequence numbers.

```text
summary             -> stored 96, oldest 3145729, newest 3145824, capacity 3468
read from 0         -> 3145729, 3145730, ... 3145824
mark up to 3145824  -> ok
summary             -> stored 0
```

## Needs

### `flash`

At least 20 blocks of 4096 bytes that keep their content without power.
store expects:

- a write changes whole 4-byte words and can only turn bits from 1 to 0;
- an erase works on a whole block and sets every bit to 1;
- a block endures at least 10 000 erases;
- when a call returns, its effect survives power loss;
- power loss during a write damages only the words of that write, power
  loss during an erase only that block.

With 288 new readings a day, store erases each block about once in
12 days.

### `readings`

Every new reading, once, in ascending order of sequence number, at the
moment it has been taken. A reading has a sequence number, a tick count,
and soil moisture, light and temperature, each present or absent. store
expects that the provider waits until store has accepted one reading
before it hands over the next. store ignores a reading whose sequence
number is not higher than the highest it has received.

## Out of scope

- Deciding that a reading has been delivered. store is told.
- Any index other than the sequence number: no search by time or value.
- Storing anything that is not a reading: no settings, no keys.
- Changing or correcting a stored reading.

## More

- [AGENTS.md](AGENTS.md): why readings are kept in a log of this shape
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- [Flash layout](doc/references/flash-layout.md): blocks, records and recovery
