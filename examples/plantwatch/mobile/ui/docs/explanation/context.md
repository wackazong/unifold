# Context of ui

What this unit takes over from the units above, and what each item means here.

## From mobile

### [mobile/0001 The local store is the only source for the screens](../../../docs/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)

Screens read only from a store on the phone and write the owner's changes to it. A notification names a plant; it is not a source of data.

Every screen is built on queries of `plant-data` and has no loading state for data on the phone. Registering for notifications is the only thing `ui` does outside the phone.

### [mobile/0004 One codebase for both platforms](../../../docs/decisions/0004-one-codebase-for-both-platforms.md)

The app is written once, in Flutter. Code per platform is allowed in the radio part only. The screens therefore exist once, and `ui` holds no code that is specific to iOS or Android.

### [plantwatch: what the owner can rely on](../../../../docs/references/app-ui.md)

The reference promises the following, as far as the screens deliver it:

- The owner sees all plants, with those that have an open alert first, together with the reason. Per plant, the owner sees the latest reading and 90 days of history, and the age of readings and of server data wherever either is shown.
- Adding, changing and removing a plant work offline; a change is marked until the server has it.
- The app needs no account. A second phone joins by scanning a code that the first one shows.
- A sensor stick is open for pairing only for a few minutes after its cell has been put in; the app tells the owner to do that.
- A tap on a notification opens the plant it is about. The app registers the phone for notifications once they are allowed and the owner exists, again when the phone's address changes, and ends this on leaving.
- The limits are 20 sensor sticks, 50 plants, one owner, English and German, and portrait. Without Bluetooth, notification or camera permission the rest keeps working.
- No state is shown by colour alone, every control has a label, and the app uses the system text size.

The screens in [screens](../references/screens.md) deliver these promises. A new screen starts with a promise there.

### [mobile: data model](../../../docs/references/data-model.md)

The data model defines the following, as far as the screens show it:

- A reading has three quantities, each a value or absent, a UTC time and a flag for an estimated time.
- A plant has a name of 1 to 60 characters, a lower and an upper limit per quantity, at most one sensor stick, and a change state `in step`, `waiting` or `refused`. The app lets the owner set the three lower limits.
- Below a lower limit the reasons shown are "needs water", "needs more light" and "needs a warmer place". Above an upper limit they are "too wet", "too much light" and "too warm".
- An alert has a reason, a limit and a value, and the times when it opened and when it closed. The phone learns of an alert only from the server.
- There are two ages: the age of a plant's readings and the age of server data.

The screens show these things under these names. The plant form edits the lower limits. No screen derives "needs water" from a reading.

### [mobile: platform limits](../../../docs/references/platform-limits.md)

Bluetooth, notification and camera permissions are asked at run time. Pairing on Android shows a system dialog per sensor stick.

The permission steps in [screens](../references/screens.md) follow from these limits. The source marks its values as unverified design assumptions.

### [mobile: glossary](../../../docs/references/glossary.md)

A fetch takes the readings of a sensor stick onto the phone, and an exchange is one round with the server.

These are the words the screens use for "last fetch" and "last exchange". The unit's own terms are in its [glossary](../references/glossary.md).

## From plantwatch

### [plantwatch: conventions, measured quantities](../../../../docs/references/conventions.md#measured-quantities)

Soil moisture is in percent, from 0 to 100, with a resolution of 0.1. Light is in lux, from 0 to 100 000, with a resolution of 1. Temperature is in °C, from -20 to 60, with a resolution of 0.1.

These values set the number formats, the axis ranges and the limits of the threshold controls.

### [plantwatch: glossary](../../../../docs/references/glossary.md)

An alert is the state "this plant needs attention for this reason". A notification is one message per alert.

The screens and the documents of this unit use these words, together with plant, owner, sensor stick, reading and threshold.
