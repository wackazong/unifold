# Invariants of device

What is true of the firmware at every moment. A change that breaks one of
these lines is a change of the decomposition and needs a decision.

- No file outside the folder of [hal](../../hal/README.md) includes a vendor
  header or touches a register.
- A reading is complete, numbered and unchangeable when it leaves the part
  that made it.
- A reading is in durable memory before the board sleeps after taking it.
- A stored reading is released only by a confirm of a central or by an
  overflow of the memory. No part releases one on its own judgement.
- Sampling is never late by more than 1 s because of the radio. A
  connected central does not stop the firmware from taking readings.
- No part keeps a wall-clock time. The only time is the tick count.
- The average current stays within the
  [energy budget](../references/energy-budget.md).
- Nothing waits in a loop. Code that needs to wait sets an alarm or
  reacts to a radio event, and returns.
- The start-up code in this folder only creates the parts in the order
  given in [runtime.md](runtime.md) and returns. It holds no logic. Logic
  belongs into a part.
- A part does not include a file of another part other than its public
  interface. If two parts need the same type, the part that provides the
  capability defines it.
