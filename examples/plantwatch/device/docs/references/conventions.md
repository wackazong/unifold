# Conventions of device

How work in the firmware is done. What must hold at every moment is in
[invariants.md](../explanation/invariants.md).

- A part writes down what it expects of another as a need, with a contract where numbers matter. Whoever changes a wiring line in the manifest reads both ends and makes them agree.
- Every number in the [energy budget](energy-budget.md) is a planned value until it is measured. Replace it when a measurement exists.
- A feature that needs a setting to survive a start has no place to keep it today. That is a change of the decomposition, not a detail: propose it as a decision first.
