# Conventions of notifier

How work in this unit is done. What must hold at every moment is in the
[invariants](../explanation/invariants.md).

- When in doubt between `retry` and `failed`, `notify` returns `retry`. A wrong `failed` loses a notification; a wrong `retry` costs a call.
- Texts name the plant and the measured fact. They give no advice beyond the obvious and do not mention the product.
