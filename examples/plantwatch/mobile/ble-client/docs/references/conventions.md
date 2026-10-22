# Conventions of ble-client

How work on the client is done. What must hold at every moment is in
[invariants.md](../explanation/invariants.md).

- Take every UUID, field layout and timing from `link-profile`. Do not copy
  them into the documents of this unit; they would drift.
- Test on real phones against a real or simulated sensor stick. Simulators
  of the phone platforms have no usable BLE.
