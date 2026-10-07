# Context of ui

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From mobile

| Source | What it says | What it means here |
|---|---|---|
| [mobile/0001 The local store is the only source for the screens](../../doc/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md) | Screens read only from a store on the phone and write the owner's changes to it. They never talk to the radio or the network. | Every screen is built on queries of `plant-data`. There is no loading state for data on the phone, and every screen shows the age of its data. |
| [mobile/0004 One codebase for both platforms](../../doc/decisions/0004-one-codebase-for-both-platforms.md) | The app is written once in a cross-platform toolkit, Flutter. Code per platform is allowed in the radio part only. | The screens exist once. ui contains no code that is specific to iOS or Android. |
| [mobile: what the owner can rely on](../../doc/references/app-ui.md) | Lists what the owner can do, what the app does not promise, the limits, the behaviour without permissions, and the accessibility rules. The app needs no account; a second phone joins through a code. A sensor stick is open for pairing only for a few minutes after its cell has been put in. | The screens in [app-ui.md](references/app-ui.md) deliver these promises, among them the code for a second phone and the instruction to put the cell in again. A new screen starts with a promise there. |
| [mobile: data model](../../doc/references/data-model.md) | Defines reading, plant, a lower and an upper limit per quantity with the reason shown for each, the change states `in step`, `waiting` and `refused`, alert, paired sensor stick, session, and the two ages of data. Version 1 sets the three lower limits only. The phone learns of an alert only from the server. | The screens show these things under these names. The plant form edits the lower limits. The screens never derive "needs water" from a reading. |
| [mobile: platform limits](../../doc/references/platform-limits.md) | Bluetooth, notification and camera permissions are asked at run time. Pairing on Android shows a system dialog per sensor stick. | The permission steps of the screens. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0005 Ticks and UTC](../../../doc/decisions/0005-the-sensor-counts-ticks-and-the-phone-assigns-time.md) | The time of a reading is computed by the phone. A time that cannot be computed is estimated and marked. | A reading with an estimated time is shown with "about". |
| [Conventions: measured quantities](../../../doc/references/conventions.md) | Soil moisture in percent, 0 to 100, resolution 0.1. Light in lux, 0 to 100 000, resolution 1. Temperature in °C, -20 to 60, resolution 0.1. An unmeasured quantity is absent, not zero. | Number formats, axis ranges and the limits of the threshold controls. An absent value is shown as "no value". |
| [Conventions: time](../../../doc/references/conventions.md) | Every time is UTC. | The screens convert to the phone's time zone for display. |
| [Product parameters](../../../doc/references/product-parameters.md) | Up to 50 plants per owner, 20 sensor sticks per phone, 90 days of history on the phone. | The list is built for 50 rows without paging. The chart reaches back 90 days. |
| [Glossary](../../../doc/references/glossary.md) | Plant, owner, sensor stick, reading, threshold, pairing. Alert: the state "this plant needs attention for this reason". Notification: one message per alert. | The words on the screens and in the documents of this unit. |
