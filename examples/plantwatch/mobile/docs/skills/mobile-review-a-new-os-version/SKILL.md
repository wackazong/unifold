---
name: mobile-review-a-new-os-version
description: Review what a new major version of iOS or Android changes for background fetching, permissions and notifications, and update the platform limits of the phone app. Use it when a new major version is announced, and again when it is released.
---

# Review a new version of iOS or Android

Background fetching rests on rules the operating systems change every year. The result of this procedure is a current [platform-limits.md](../../references/platform-limits.md) and a list of what the app has to change.

## Steps

1. **Read the vendor's notes.** Read the release notes and the behaviour changes the vendor publishes for the new version. Look for: Bluetooth, background execution, companion devices, state restoration, permissions, notifications, battery saving.
2. **Go through the tables.** For every row of [platform-limits.md](../../references/platform-limits.md), decide: unchanged, changed, or unknown. Do not answer from memory; find the sentence in the vendor's documentation.
3. **Measure what the notes do not say.** Install a release build on a real phone with the new version. With a paired sensor stick in range, measure:
   - the delay between the sensor stick appearing and the app being woken,
   - the run time the app gets after being woken,
   - whether the app is woken after a restart of the phone,
   - whether the app is woken after the owner has removed it from the app switcher. Repeat each measurement five times and note the worst value.
4. **Update the reference.** Change the rows that changed and raise "Designed for up to". If a value could not be determined, write that, with the date.
5. **Judge the design budget.** If the run time per wake-up fell below the design budget, or the wake-up mechanism is deprecated, [0002](../../decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md) no longer holds as written. Write a new decision with status `proposed` that supersedes it. Do not edit the old one beyond its status.
6. **Check the promises.** Read "What happens without the owner" in [app-ui.md](../../references/app-ui.md). Change every promise the new version breaks, and tell the human.
7. **Decide on the oldest supported version.** Propose dropping a version only together with a human; it removes the app from phones in use.
8. **Finish.** Run the generator and the checker of the project.

## Checks

- Every row of [platform-limits.md](../../references/platform-limits.md) has been confirmed or changed for the new version.
- The measurements of step 3 are in the report to the human.
- No promise in [app-ui.md](../../references/app-ui.md) contradicts the updated limits.

## Reference

- [platform-limits.md](../../references/platform-limits.md)
- [runtime.md](../../explanation/runtime.md): background fetching as a state diagram
