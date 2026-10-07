---
name: ble-client-support-a-profile-version
description: Make the BLE client speak a new version of the link profile while it keeps working with sensor sticks of the older version. Use it when the definition behind the need link-profile has a new minor or major version.
---
# Support a new version of the link profile

The client meets sensor sticks of every version that is in people's flower
pots. The result of this procedure is a client that speaks the new version
and still fetches from the old one.

## Steps

1. **Read the difference.** Read the new version of the definition behind
   `link-profile` and list what changed: services, characteristics, fields
   of a reading, procedures, timings. Sort each change into "the client must
   act" or "the client may ignore".
2. **Check the expectations.** Compare the list with the expectations under
   `sensor-link` and `link-profile` in [README.md](../../../README.md). If
   an expectation no longer holds or a new one is needed, change the
   `README.md` first.
3. **Decide per change how an old sensor stick is handled.** The client
   learns the version of a sensor stick in the state "Preparing" of the
   [fetch session](../../references/fetch-session.md). Everything
   version-specific branches there and nowhere else.
4. **A new field of a reading.** If the provided ports shall carry it,
   that is a change to [sensor-readings](../../references/sensor-readings.md):
   the field is absent for sensor sticks that do not send it. If the ports
   shall not carry it, the client ignores it.
5. **A new major version.** The client refuses a major version it does not
   know with `unsupported version`. Supporting a second major version is a
   choice with alternatives: record a decision in
   [decisions](../../decisions/index.md) with status `proposed` before
   writing code.
6. **Update the facts.** Adjust the sizes and timeouts in
   [fetch-session.md](../../references/fetch-session.md) if a timing
   changed, and the failure tables of the two contracts if a failure was
   added.
7. **Implement on both platforms.** The platform code implements one common
   interface; change the interface first, then both implementations.
8. **Test against both versions.** Run a fetch of a full backlog, an
   interrupted fetch and a pairing against a sensor stick of the old version
   and one of the new version, real or simulated, on a real phone of each
   platform.
9. **Finish.** Run the generator and the checker of the project and review
   the files you changed.

## Checks

- A sensor stick of the previous version is still found, paired and fetched
  completely.
- No UUID, field layout or timing of the profile has been copied into a
  document of this unit.
- The contracts say for every new field what a consumer sees when the sensor
  stick does not send it.
- [doc/context.md](../../context.md) still restates the supported protocol
  version correctly.

## Reference

- [fetch-session.md](../../references/fetch-session.md)
- [sensor-readings.md](../../references/sensor-readings.md)
- [pairing.md](../../references/pairing.md)
