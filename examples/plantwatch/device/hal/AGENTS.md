# AGENTS.md: hal

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show device/hal`
prints this unit with its neighbours.

## Why

`hal` exists so that exactly one place knows the board. It changes when the
board changes: a pin, a sensor part, the microcontroller, the radio stack
of its vendor. Nothing else is a reason to touch it.

Three forces lead there. Testing: logic that is reached only through a
soldered board is tested late and seldom; behind four narrow libraries a
substitute can stand in for the board. Energy: with one owner of the power
state, no two parts can each keep something awake. The radio stack: it
comes as a binary, owns the radio and dictates when memory may be written;
`hal` absorbs these constraints, so that its callers see plain calls.

The interface is four libraries and not one, so that a caller states only
what it uses. The level is chosen so that `hal` needs no knowledge of the
product: raw values instead of percent, GATT primitives instead of a
profile, blocks instead of records. What must stay true: nothing outside
this folder includes a vendor header, and nothing inside knows what a
reading is.

## Read next

1. [README.md](README.md): what the four libraries guarantee
2. [doc/context.md](doc/context.md): decisions and budgets from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): the sleep state and the boot counter
5. The contracts of the four ports:
   [sensor-io](doc/references/sensor-io.md),
   [radio](doc/references/radio.md),
   [flash](doc/references/flash.md),
   [timer](doc/references/timer.md)
6. [doc/references/board.md](doc/references/board.md): pins, peripherals, memory map

## Rules for work here

- `hal` has no product logic. It knows the tick count, because that is
  time. It knows no reading, no sequence number, no profile and no record.
- A change of a pin, a peripheral or the memory map changes
  [board.md](doc/references/board.md) in the same change.
- The regions of the memory map never move once boards are in use. Moving
  one destroys what is stored there.
- `hal` raises the boot counter before any caller can read the tick count.
- Every function of the four libraries must be replaceable by a
  substitute. A function that hands out a register, a vendor type or a
  pointer into the radio stack is not allowed.
- A change to a port starts with its contract: change the example case
  first, then the test, then the code.
- Numbers in [board.md](doc/references/board.md) are planned values until
  they are measured on a board. Replace them, do not add a second column.
