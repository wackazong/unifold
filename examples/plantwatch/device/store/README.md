# store

`store` keeps readings on the sensor stick from the moment they are taken until someone has confirmed that they are safe elsewhere. It keeps them through power loss, hands them out oldest first, and when its memory is full it gives up the oldest readings in favour of new ones.

## Why

What this unit hides is the layout of readings in the flash blocks and the recovery after power loss ([0001](docs/decisions/0001-a-ring-of-blocks-for-readings-and-a-journal-for-marks.md)). Readings have to wait on the sensor stick, for weeks if need be, and the cell can be pulled at any moment. `store` exists so that the harsh rules of the memory that makes this possible stay in one unit: bits only fall from 1 to 0, erasing takes whole blocks, blocks wear out, and any write can be cut off. It changes when the kind or the size of that memory changes, or the number of readings to keep.

`store` provides a log with a "delivered" mark and not a general storage, because only one question is ever asked of it: which readings have not been delivered yet, in order. A log answers it without an index and without cleaning up in the background, and appending is the access pattern that flash memory tolerates best.

`store` never decides by itself that a reading is done. It is told, or it runs out of room. The trade-off of the log is coarse release: room comes back a block at a time.

What must stay true: a reading is written once and never touched again; whatever the moment of power loss, recovery finds a consistent log; and a mark that has been reported as done is never forgotten.

## Read next

1. [docs/references/flash-layout.md](docs/references/flash-layout.md): blocks, slots, recovery, test cases
2. [flash](../docs/references/flash.md): what `store` expects of the memory
3. [docs/explanation/context.md](docs/explanation/context.md): what `store` inherits from above
4. [Decisions](docs/decisions/index.md)
