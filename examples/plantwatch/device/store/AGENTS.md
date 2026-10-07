# AGENTS.md: store

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show device/store`
prints this unit with its neighbours.

## Why

Readings have to wait on the sensor stick, for weeks if need be, and the
cell can be pulled at any moment. `store` exists so that the harsh rules of
the memory that makes this possible stay in one unit: bits only fall from
1 to 0, erasing takes whole blocks, blocks wear out, and any write can be
cut off. It changes when the kind or the size of that memory changes, or
the number of readings to keep.

`store` offers a log with a "delivered" mark and not a general storage,
because only one question is ever asked of it: which readings have not
been delivered yet, in order. A log answers it without an index and
without cleaning up in the background, and appending is the access
pattern that flash memory tolerates best.

`store` never decides by itself that a reading is done. It is told, or it
runs out of room. The trade-off of the log is coarse release: room comes
back a block at a time.

What must stay true: a reading is written once and never touched again;
whatever the moment of power loss, recovery finds a consistent log; and a
mark that has been reported as done is never forgotten.

## Read next

1. [README.md](README.md): what the log guarantees
2. [doc/context.md](doc/context.md): rules from above on keeping and releasing readings
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): why a ring and a journal
5. [doc/references/flash-layout.md](doc/references/flash-layout.md): blocks, slots, recovery, test cases
6. [doc/references/flash.md](doc/references/flash.md): what `store` expects of the memory

## Rules for work here

- There are two erase paths: the oldest ring block when the ring needs
  room, and the idle journal block when the journal is full. Do not add a
  third.
- Write the journal entry first, then change the state in RAM, then
  return. Never the other way round.
- Compare sequence numbers only with "higher than". They are not
  consecutive.
- Test every write sequence with a `flash` substitute that cuts power
  after each single word. Recovery must succeed after every cut. The
  substitute has to pass the examples in
  [flash](doc/references/flash.md) itself.
- A change to the [flash layout](doc/references/flash-layout.md) gets a
  new layout version. Recovery either still reads the previous version or
  the change states plainly that stored readings are lost on update.
- The slot layout resembles other encodings of a reading by coincidence.
  It is private. Do not hand a slot out as bytes.
