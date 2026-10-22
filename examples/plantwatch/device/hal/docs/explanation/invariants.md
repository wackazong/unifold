# Invariants of hal

What is true of the hardware layer at every moment. These lines keep the board in one place and the rest of the firmware testable without it.

- `hal` has no product logic. It knows the tick count, because that is time. It knows no reading, no sequence number, no profile and no record.
- The regions of the memory map never move once boards are in use. Moving one destroys what is stored there.
- `hal` raises the boot counter before any caller can read the tick count.
- Every function of the four libraries can be replaced by a substitute. No function hands out a register, a vendor type or a pointer into the radio stack.
