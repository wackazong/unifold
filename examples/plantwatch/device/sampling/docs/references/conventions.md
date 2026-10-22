# Conventions of sampling

How work on measuring and calibration is done. What must hold at every moment is in [invariants.md](../explanation/invariants.md).

- The constants in [calibration.md](calibration.md) and in the code are the same numbers. Change both in one change, and the example tables first: they are the test cases.
- What `sampling` expects of raw values and of time is written in the contracts of its two needs, [sensor-io](../../../docs/references/sensor-io.md) and [timer](../../../docs/references/timer.md). A new expectation goes there before the code relies on it.
