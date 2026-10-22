# Conventions of emulator

How work on the program is done. What must hold at every moment is in [invariants.md](../explanation/invariants.md).

- Build the radio face from the BLE profile and from nothing else. Do not read, copy or imitate another implementation.
- If the definition does not say what to do, do not guess. The gap is a finding: report it, and build only after the definition is corrected.
- A control request names a target state. Never add a request that means "one more step".
- A new request or scenario member starts as a row in the examples of its reference. The row is the first test.
