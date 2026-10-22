# Conventions of protocol

How the two definitions are written and changed.

- Every change to a contract changes its version number in the same change.
- When two implementations disagree, the question is what the text says.
  If the text allows both, the text is at fault. Correct the text first.
- Name roles, not implementations. The roles are "sensor stick" and
  "central". Do not name a platform, a library or a product part.
- Use the terms of the [glossary](glossary.md) unchanged. In particular,
  the BLE step is "bonding", never "pairing".
- Layouts are tables with offset and size. The byte examples in
  [README.md](../../README.md), in the
  [reading schema](reading-schema.md) and in the
  [procedures](ble-profile/procedures.md) are computed from the tables.
  Recompute them when a layout changes.
- The UUID base and the company identifier are placeholders. They must be
  replaced before a product ships with them.
