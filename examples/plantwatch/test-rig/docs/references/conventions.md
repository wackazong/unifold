# Conventions of test-rig

How work on the rig is done. What must hold at every moment is in [invariants.md](../explanation/invariants.md).

- A test states a promise from the [catalogue](test-catalogue.md). Add its entry there before writing the test. A test without an entry tests an implementation detail.
- If the rig and something under test disagree, first check the definition; the rig can be the one that is wrong.
- A run against a real sensor stick confirms its readings, and the sensor stick then deletes them. Never run against a sensor stick that is in somebody's flower pot.
- A test that fails now and then is a failed test. Do not add a retry around a promise.
