# store

`store` keeps readings on the sensor stick from the moment they are taken until someone has confirmed that they are safe elsewhere. It keeps them through power loss, hands them out oldest first, and when its memory is full it gives up the oldest readings in favour of new ones.

## Why

Readings have to wait on the sensor stick, for weeks if need be, and the cell can be pulled at any moment. `store` exists so that the harsh rules of the memory that makes this possible stay in one unit: bits only fall from 1 to 0, erasing takes whole blocks, blocks wear out, and any write can be cut off. It changes when the kind or the size of that memory changes, or the number of readings to keep.

`store` provides a log with a "delivered" mark and not a general storage, because only one question is ever asked of it: which readings have not been delivered yet, in order. A log answers it without an index and without cleaning up in the background, and appending is the access pattern that flash memory tolerates best.

`store` never decides by itself that a reading is done. It is told, or it runs out of room. The trade-off of the log is coarse release: room comes back a block at a time.

What must stay true: a reading is written once and never touched again; whatever the moment of power loss, recovery finds a consistent log; and a mark that has been reported as done is never forgotten.

## Capabilities

### `reading-log`

Beyond the contract:

- **Power loss at any moment** costs at most the reading or the mark that was being written. Everything written before is intact.
- **After a start** the log is complete before `store` accepts the first new reading. Recovery takes less than 100 ms, or less than 200 ms when power was lost during an erase.
- **Refused memory.** When `flash` refuses a write or an erase, a mark fails and says so, and a reading handed over is not stored. The log is then as it was before.

Limits: Read returns within 2 ms. A mark takes up to 2 ms, and up to 110 ms once in 510 marks. Accepting a reading takes up to 5 ms, and up to 110 ms once in 204 readings. `store` draws no conclusion from gaps between sequence numbers.

## Needs

### `flash`

`store` erases each block at most once in 12 days.

### `readings`

`store` ignores a reading whose sequence number is not higher than the highest it has received.

## Read next

1. [docs/references/flash-layout.md](docs/references/flash-layout.md): blocks, slots, recovery, test cases
2. [flash](../docs/references/flash.md): what `store` expects of the memory
3. [docs/explanation/context.md](docs/explanation/context.md): what `store` inherits from above
4. [Context diagram](docs/diagrams/context.md)
5. [Decisions](docs/decisions/index.md)
