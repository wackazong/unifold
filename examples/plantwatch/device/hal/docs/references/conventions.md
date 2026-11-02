# Conventions of hal

How work in the hardware layer is done. What must hold at every moment is in [invariants.md](../explanation/invariants.md).

- A change of a pin, a peripheral or the memory map changes [board.md](board.md) in the same change.
- A change to a capability starts with its contract: change the example case first, then the test, then the code.
- A measurement on a board replaces an estimate in [board.md](board.md) in its row. Do not add a second column.
