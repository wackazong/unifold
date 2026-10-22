# Conventions of rules

How work in this unit is done. What must hold at every moment is in the
[invariants](../explanation/invariants.md).

- The need `thresholds` is of kind `library` on purpose. If judging needs
  something that lives behind a network, it is stated as a function in the
  words of this unit, and the fetching is left to whoever provides it.
- The state has a version field. A change of its form keeps reading the
  old form; otherwise the alerts that were open are forgotten at the next
  release.
- Every rule gets a row in the tables of the
  [evaluation reference](evaluation.md) and a test that is a sequence of
  readings. A rule that cannot be shown as such a sequence is not a rule of
  this unit.
- A margin is in the unit of its quantity and is never smaller than the
  resolution of the quantity.
