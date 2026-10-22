# Requirements of plantwatch

plantwatch must tell the owner of a house plant when the plant needs water,
more light or a warmer place, without the owner having to look. It is for
people who keep a few plants at home and carry a phone. It is not for
growers who need a system to act by itself, not for more than 50 plants per
owner, and not for plants that no phone ever comes near.

## Goals

1. **A dry plant leads to one notification.** When a reading crosses a
   threshold of its plant, the owner's phone shows one notification, and an
   alert that stays open produces no further one.
2. **A sensor stick runs for a year.** At the default sampling interval of
   15 minutes, one CR2032 cell lasts at least 12 months.
3. **Nothing is lost while the phone is away.** A sensor stick keeps at
   least 30 days of readings. A reading that reached the phone reaches the
   server, and every hop may deliver it twice without harm.
4. **The app works without a network.** It shows the last known state of
   each plant and 90 days of history from its own store.
5. **Thresholds are the owner's.** The owner sets them or picks a preset;
   no part guesses a species.

## Quality goals, in the order in which they win

| Rank | Quality | Observed as |
|---|---|---|
| 1 | No lost reading | A reading is deleted from a place only after the next place has confirmed it; the end-to-end tests deliver every reading of a scenario to the server |
| 2 | Battery life | 12 months on one cell at the default interval and 4 connections of 3 seconds a day |
| 3 | Freshness of an alert | Under 1 minute from the upload of a reading to the notification being handed to the push service |
| 4 | Works offline | Every screen of the app shows its last known state with the network off |
| 5 | Testable end to end | The whole path from a sensor value to an alert runs against the emulator on a developer machine or CI runner |
