# Reasoning of device

The long form of the why in [README.md](../../README.md). Which parts exist
and how they are wired is shown in the
[component diagram](../diagrams/component.md).

**Energy decides the control flow.** The
[energy budget](../references/energy-budget.md) allows 19.4 µA on average,
and a running processor draws 200 times that. The firmware is therefore a
set of reactions to two sources of events, a timer and the radio. Between
events the board sleeps
([0001](../decisions/0001-sleep-between-events-and-advertise-all-the-time.md)).

**The hardware has one owner.** Everything that depends on the board is
in [hal](../../hal/README.md). The reason is less portability than testing:
the rest of the firmware is logic about readings, memory and a profile,
and it is tested on a development machine against substitutes
([0002](../decisions/0002-only-one-part-touches-the-hardware.md)).

**The other boundaries follow the reasons for change.** Measuring and
calibration change with the sensors, so they are in
[sampling](../../sampling/README.md). The way readings survive in memory
changes with the memory technology, so it is in
[store](../../store/README.md). Everything that knows the BLE profile
changes with the profile, so it is in [link](../../link/README.md). None of
the three knows how the others work, and each has one job that can be
stated in a sentence.

**A reading gets its identity where it is made.** If the part that keeps
readings numbered them, a reading would have no number until it is stored,
and a reading shown live could not be recognised when it is fetched later.
The number is therefore computed from the tick count at the moment of
measuring
([0003](../decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md)).

**There is no main program.** The start-up code creates the parts and
returns; after that only events run. This keeps the order of things in
one place, the start order in [runtime.md](runtime.md), and out of the
parts.

## Trade-offs

| Chosen | Given up | Decision |
|---|---|---|
| Being found at any time | Half of the energy budget goes into advertising | [0001](../decisions/0001-sleep-between-events-and-advertise-all-the-time.md) |
| Testing on a development machine | One layer of calls between logic and hardware | [0002](../decisions/0002-only-one-part-touches-the-hardware.md) |
| Identity without stored state | Consecutive sequence numbers; an upper limit of starts | [0003](../decisions/0003-sequence-numbers-are-derived-from-the-tick-count.md) |
