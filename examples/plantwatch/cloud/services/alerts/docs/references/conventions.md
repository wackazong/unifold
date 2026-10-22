# Conventions of alerts

How work in this unit is done. What must hold at every moment is in the [invariants](../explanation/invariants.md).

- After a change to a child's capability, both ends of its wiring lines are read again: the need of one child and the capability of the other must still say the same.
- A change to when an alert opens or closes changes what clients see. It is checked against the contract cited in [context](../explanation/context.md) before a rule changes.
