---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# A ring of blocks for readings and a separate journal for delivered marks

## Context and Problem Statement

`store` keeps a few thousand small readings in flash memory and has to know which of them are delivered. Flash can be written bit by bit only from 1 to 0, is erased in blocks of 4 kB, wears out after 10 000 erases of a block, and can lose power in the middle of any operation. Readings arrive steadily, marks arrive in bursts, up to several per hour. How are both laid out so that no block wears out and power loss costs at most the item being written?

## Decision Drivers

- No block is erased much more often than the others.
- Power loss at any moment leaves a log that recovery can read.
- The guaranteed capacity does not depend on how often marks arrive.
- The code is small enough to review and to test exhaustively.

## Considered Options

- A table with a fixed slot per reading and a "delivered" flag that is cleared in place
- A ring of blocks for readings, with the mark as a number in a fixed header block that is erased and rewritten
- A ring of blocks in which readings and marks are appended in one sequence
- A ring of blocks for readings, and marks appended to a journal of two blocks that take turns
- A flash file system or key-value library

## Decision Outcome

Chosen option: "a ring for readings and a journal of two blocks for marks", because it is the only option that meets all four drivers.

Appending in a ring spreads erases evenly by construction: every ring block is erased once per turn of the ring. No separate wear levelling exists. The journal takes the frequent small writes without an erase per write.

### Consequences

- Good: a ring block is erased about 10 times a year, a journal block about once per 1 000 marks. Both are far below 10 000 in the life of a sensor stick.
- Good: every write is an append to erased memory. Nothing is updated in place, so power loss cannot damage what was written before.
- Good: 2 880 readings fit whatever the pattern of marks.
- Bad: 2 of 20 blocks hold no readings.
- Bad: room is regained only block by block. Overflow discards up to 204 readings at once, not one.
- Bad: at start, `store` has to scan the newest ring block and both journal blocks to find its state.
- Bad: a mark is one number. `store` cannot mark single readings.

## Pros and Cons of the Options

### Fixed slots with a flag cleared in place

- Good: a reading is released individually.
- Bad: marking 2 880 readings is 2 880 writes, about 3 s with the board awake.
- Bad: reuse of a slot needs an erase of its block while neighbours are still stored; that needs copying.

### Mark in a fixed header block

- Good: simplest to read back.
- Bad: one erase per mark. At one mark per hour the header block is worn out in 14 months.

### Readings and marks in one ring

- Good: one structure.
- Bad: marks use slots of readings. A caller that marks often lowers the capacity.

### File system or key-value library

- Good: no layout to design.
- Bad: its erase pattern and its behaviour on power loss have to be trusted or studied. Its code is larger than the rest of `store`.

## More Information

The layout is in the [flash layout](../references/flash-layout.md).
