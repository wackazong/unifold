# Conventions of hal

How work in the hardware layer is done. What must hold at every moment is
in [invariants.md](../explanation/invariants.md).

- A change of a pin, a peripheral or the memory map changes
  [board.md](board.md) in the same change.
- A change to a capability starts with its contract: change the example case
  first, then the test, then the code.
- Numbers in [board.md](board.md) are planned values until they are
  measured on a board. Replace them, do not add a second column.
