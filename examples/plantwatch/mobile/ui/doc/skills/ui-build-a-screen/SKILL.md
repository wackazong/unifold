---
name: ui-build-a-screen
description: Add or change one screen of the user interface, from its description to the accessibility check. Use it when the data the screen needs is already available through plant-data or pairing and the work is inside the ui unit.
---
# Build a screen

A screen is finished when every state it can be in is described, built and
checked in both languages. The description comes first, because the states
nobody wrote down are the ones nobody builds.

## Steps

1. **Check the data.** List what the screen shows and what the owner can do
   on it. For each item, find the query or command under `plant-data` or
   `pairing` in [README.md](../../../README.md). If one is missing, stop:
   the change is larger than this unit. Tell the human; do not fetch the
   data in another way.
2. **Describe the screen.** Add or change its row in the table "Screens" of
   [app-ui.md](../../references/app-ui.md) and its arrows in the navigation
   diagram.
3. **Go through the states.** For each row of "States every screen has" in
   [app-ui.md](../../references/app-ui.md), decide what this screen shows.
   If the screen has a state of its own, add a table for it, as "Find
   sensor stick" has.
4. **Write the texts** in English and German. Use the words of the glossary
   cited in [context.md](../../context.md). Build ages, numbers and dates
   with the platform's formatting and the formats in
   [app-ui.md](../../references/app-ui.md).
5. **Build the screen on observed queries.** The screen draws the latest
   answer and keeps nothing. A command is sent and the screen waits for the
   observed query to change; it does not change its own picture first.
6. **Check the rules that cannot be seen in a review of the picture:**
   - no comparison of a reading with a threshold anywhere in the screen,
   - no loading state for data on the phone,
   - no state shown by colour alone.
7. **Test with prepared data:** an empty phone; one plant without a sensor
   stick; 50 plants of which 20 have an open alert; a plant whose newest
   reading is 3 days old; a plant in the state `waiting` and one in the
   state `refused`; readings with estimated times; a quantity that is
   absent.
8. **Test accessibility:** the largest text size of the system, the screen
   reader of each platform from the first to the last control, and a
   contrast check of every text.
9. **Record a decision** in [decisions](../../decisions/index.md) with
   status `proposed` if the screen changes the navigation.
10. **Finish.** Run the generator and the checker of the project and review
    the files you changed.

## Checks

- Every state of the screen is described in
  [app-ui.md](../../references/app-ui.md) and exists in the build.
- The screen looks the same in flight mode as with a network connection,
  apart from the ages it shows.
- Both languages fit at the largest text size without cut-off text.
- The navigation diagram shows every way into and out of the screen.

## Reference

- [app-ui.md](../../references/app-ui.md): screens, navigation, states,
  formats
- [presets.md](../../references/presets.md): threshold presets of the plant
  form
