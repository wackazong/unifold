# Conventions of plants

How work in this unit is done. What must hold at every moment is in the
[invariants](../explanation/invariants.md).

- An aggregate is never added to. The hour is always recomputed from its
  raw readings, because adding counts a repeated event twice.
- A schema change is a migration that works while the previous version of
  the service still runs.
