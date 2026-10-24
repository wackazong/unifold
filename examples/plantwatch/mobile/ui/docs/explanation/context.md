# Context of ui

What this unit inherits from the units above. This is the only file of the unit that links upward. Each item is restated so that the unit can be understood when the link is not available.

## From mobile

### [mobile/0001 The local store is the only source for the screens](../../../docs/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)
<!-- unifold:cites sha=3670810d -->

Says: screens read only from a store on the phone and write the owner's changes to it. A notification names a plant; it is not a source of data.

Here: every screen is built on queries of `plant-data` and has no loading state for data on the phone. Registering for notifications is the only thing ui does outside the phone.

### [mobile/0004 One codebase for both platforms](../../../docs/decisions/0004-one-codebase-for-both-platforms.md)
<!-- unifold:cites sha=7c2b0ce8 -->

Says: the app is written once, in Flutter. Code per platform is allowed in the radio part only.

Here: the screens exist once. ui holds no code that is specific to iOS or Android.

### [plantwatch: what the owner can rely on](../../../../docs/references/app-ui.md)
<!-- unifold:cites sha=aa5d729a -->

Says, as far as the screens deliver it:

- The owner sees all plants, those with an open alert first with the reason; per plant the latest reading and 90 days of history; and the age of readings and of server data wherever either is shown.
- Adding, changing and removing a plant work offline; a change is marked until the server has it.
- The app needs no account. A second phone joins by scanning a code that the first one shows.
- A sensor stick is open for pairing only for a few minutes after its cell has been put in; the app tells the owner to do that.
- A tap on a notification opens the plant it is about. The app registers the phone for notifications once they are allowed and the owner exists, again when the phone's address changes, and ends this on leaving.
- Limits: 20 sensor sticks, 50 plants, one owner, English and German, portrait. Without Bluetooth, notification or camera permission the rest keeps working.
- No state by colour alone, a label on every control, system text size.

Here: the screens in [screens](../references/screens.md) deliver these promises. A new screen starts with a promise there.

### [mobile: data model](../../../docs/references/data-model.md)
<!-- unifold:cites sha=3bb1e1f6 -->

Says, as far as the screens show it:

- Reading: three quantities, each a value or absent; UTC time; a flag for an estimated time.
- Plant: name of 1 to 60 characters, a lower and an upper limit per quantity, at most one sensor stick, change state `in step`, `waiting` or `refused`. Version 1 lets the owner set the three lower limits.
- Reasons shown below a lower limit: "needs water", "needs more light", "needs a warmer place"; above an upper limit: "too wet", "too much light", "too warm".
- Alert: reason, limit and value, opened, closed. The phone learns of an alert only from the server.
- Two ages: of a plant's readings and of server data.

Here: the screens show these things under these names. The plant form edits the lower limits. No screen derives "needs water" from a reading.

### [mobile: platform limits](../../../docs/references/platform-limits.md)
<!-- unifold:cites sha=d3346c98 -->

Says: Bluetooth, notification and camera permissions are asked at run time. Pairing on Android shows a system dialog per sensor stick.

Here: the permission steps in [screens](../references/screens.md). The source marks its values as unverified design assumptions.

### [mobile: glossary](../../../docs/references/glossary.md)
<!-- unifold:cites sha=ec81296b -->

Says: a fetch takes the readings of a sensor stick onto the phone; an exchange is one round with the server.

Here: the words the screens use for "last fetch" and "last exchange". The unit's own terms are in its [glossary](../references/glossary.md).

## From plantwatch

### [plantwatch: conventions, measured quantities](../../../../docs/references/conventions.md#measured-quantities)
<!-- unifold:cites sha=c9226f2c -->

Says: soil moisture in percent, 0 to 100, resolution 0.1; light in lux, 0 to 100 000, resolution 1; temperature in °C, -20 to 60, resolution 0.1.

Here: number formats, axis ranges and the limits of the threshold controls.

### [plantwatch: glossary](../../../../docs/references/glossary.md)
<!-- unifold:cites sha=082ae761 -->

Says: an alert is the state "this plant needs attention for this reason". A notification is one message per alert.

Here: the words on the screens and in the documents of this unit, together with plant, owner, sensor stick, reading and threshold.
