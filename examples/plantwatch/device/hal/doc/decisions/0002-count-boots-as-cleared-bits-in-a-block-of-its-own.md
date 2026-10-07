---
status: proposed
date: 2026-10-06
---
# Count boots as cleared bits in a memory block of its own

## Context and Problem Statement

`timer` promises a boot counter that rises at every start and never
repeats, also when the cell was out for a week. The counter must therefore
be in flash memory, and it is written at every start, possibly at a moment
when the cell is weak. Flash can only be erased in whole blocks, and an
erase that is interrupted leaves the block undefined. Where and how does
`hal` keep the counter?

## Considered Options

- A number at a fixed place, erased and rewritten at every start
- A number in one of the blocks that the `flash` library offers
- A block of its own in which every start clears one more bit

## Decision Outcome

Chosen option: "a block of its own in which every start clears one more
bit", because a start then never erases anything, and clearing a single
bit either happens or does not.

The block starts with a 4-byte base value. The remaining 4092 bytes are a
bit field. The boot counter is the base value plus the number of cleared
bits. The bit field lasts for 32 736 starts. When it is full, `hal` erases
the block once and writes the new base value.

### Consequences

- Good: no erase at a start. Power loss during the write cannot destroy
  the counter; at worst the counter rises by one start that never ran.
- Good: the block is erased at most twice in the life of a board.
- Good: the counter is independent of whatever the caller of `flash` does
  with its blocks.
- Bad: one block of 4 kB for one number.
- Bad: reading the counter means counting bits, up to 4 kB at every start.
- Bad: the single erase after 32 736 starts is not protected against power
  loss. `hal` carries it out only when the supply is above the power-fail
  level, and keeps the last value in the reserved block during the erase.

## More Information

The block is in the [memory map](../references/board.md).
